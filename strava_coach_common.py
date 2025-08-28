# strava_coach_common.py
import os
import json
import time
import pathlib
import datetime as dt
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv
import openai

load_dotenv()

DATA_DIR = pathlib.Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

TOKENS_PATH = DATA_DIR / "strava_tokens.json"
STATE_PATH = DATA_DIR / "state.json"

STRAVA_CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
STRAVA_CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")  # choose your model slot

DAILY_PROMPT_FILE = os.getenv("DAILY_PROMPT_FILE", "daily_prompt.txt")
WEEKLY_PROMPT_FILE = os.getenv("WEEKLY_PROMPT_FILE", "weekly_prompt.txt")

# --- OpenAI client (Chat Completions) ---
openai.api_key = OPENAI_API_KEY

STRAVA_API = "https://www.strava.com/api/v3"


# --- Utility functions ---
def now_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _save_json(path: pathlib.Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _load_json(path: pathlib.Path, default: Any):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def _refresh_access_token() -> Dict[str, Any]:
    payload = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": _load_json(TOKENS_PATH, {}).get("refresh_token", STRAVA_REFRESH_TOKEN),
    }
    r = requests.post("https://www.strava.com/oauth/token", data=payload, timeout=30)
    r.raise_for_status()
    tokens = r.json()
    _save_json(TOKENS_PATH, {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_at": tokens["expires_at"],
        "obtained_at": int(time.time())
    })
    return tokens


def _get_access_token() -> str:
    tokens = _load_json(TOKENS_PATH, {})
    if not tokens or int(tokens.get("expires_at", 0)) <= int(time.time()) + 60:
        tokens = _refresh_access_token()
    return tokens["access_token"]


def strava_get(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    access_token = _get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(f"{STRAVA_API}{path}", headers=headers, params=params or {}, timeout=60)
    if r.status_code == 401:
        _refresh_access_token()
        access_token = _get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        r = requests.get(f"{STRAVA_API}{path}", headers=headers, params=params or {}, timeout=60)
    r.raise_for_status()
    return r.json()


def list_my_activities(per_page: int = 30, page: int = 1) -> List[Dict[str, Any]]:
    return strava_get("/athlete/activities", {"per_page": per_page, "page": page})


def get_activity(activity_id: int) -> Dict[str, Any]:
    return strava_get(f"/activities/{activity_id}")


def get_activity_laps(activity_id: int):
    return strava_get(f"/activities/{activity_id}/laps")


def get_activity_streams(activity_id: int, keys: List[str]) -> Dict[str, Any]:
    params = {"keys": ",".join(keys), "key_by_type": "true"}
    return strava_get(f"/activities/{activity_id}/streams", params)


def load_state() -> Dict[str, Any]:
    return _load_json(STATE_PATH, {"last_seen_activity_id": None})


def save_state(state: Dict[str, Any]):
    _save_json(STATE_PATH, state)


def save_output(kind: str, filename_slug: str, content_md: str, raw: Dict[str, Any]):
    out_dir = pathlib.Path(__file__).resolve().parent / kind
    out_dir.mkdir(exist_ok=True, parents=True)
    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    md_path = out_dir / f"{ts}_{filename_slug}.md"
    json_path = out_dir / f"{ts}_{filename_slug}.json"
    _save_json(json_path, raw)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content_md)


# --- Prompt loader ---
def load_prompt(file_path: str) -> str:
    path = pathlib.Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {file_path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def coach_prompt_for_single(activity: Dict[str, Any], streams=None, laps=None):
    prompt_text = load_prompt(DAILY_PROMPT_FILE)
    core = {
        "id": activity.get("id"),
        "name": activity.get("name"),
        "description": activity.get("description"),
        "type": activity.get("type"),
        "start_date_local": activity.get("start_date_local"),
        "distance_m": activity.get("distance"),
        "moving_time_s": activity.get("moving_time"),
        "elapsed_time_s": activity.get("elapsed_time"),
        "average_speed_mps": activity.get("average_speed"),
        "max_speed_mps": activity.get("max_speed"),
        "average_heartrate": activity.get("average_heartrate"),
        "max_heartrate": activity.get("max_heartrate"),
        "elev_gain_m": activity.get("total_elevation_gain"),
        "pace_min_per_km": None if not activity.get("average_speed")
            else 1000.0 / (activity["average_speed"] * 60.0),
    }

    s_compact = {}
    if streams:
        for k in ("time", "heartrate", "velocity_smooth", "cadence"):
            if k in streams and "data" in streams[k]:
                s_compact[k] = streams[k]["data"][:600]

    laps_slim = []
    if laps:
        for l in laps:
            laps_slim.append({
                "lap": l.get("lap_index"),
                "split": l.get("split"),
                "distance_m": l.get("distance"),
                "elapsed_time_s": l.get("elapsed_time"),
                "moving_time_s": l.get("moving_time"),
                "avg_speed_mps": l.get("average_speed"),
                "avg_hr": l.get("average_heartrate"),
                "max_hr": l.get("max_heartrate"),
                "cadence": l.get("average_cadence"),
            })

    system = prompt_text
    user = (
        f"Core data including description:\n{json.dumps(core, ensure_ascii=False)}\n\n"
        f"Laps:\n{json.dumps(laps_slim, ensure_ascii=False)}\n\n"
        f"Streams (shortened):\n{json.dumps(s_compact, ensure_ascii=False)}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]


def coach_prompt_for_week(activities: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    prompt_text = load_prompt(WEEKLY_PROMPT_FILE)
    slim = []
    for a in activities:
        details = a["details"]
        laps = a.get("laps", [])
        streams = a.get("streams", {})

        laps_slim = []
        for l in laps:
            laps_slim.append({
                "lap": l.get("lap_index"),
                "split": l.get("split"),
                "distance_m": l.get("distance"),
                "elapsed_time_s": l.get("elapsed_time"),
                "moving_time_s": l.get("moving_time"),
                "avg_speed_mps": l.get("average_speed"),
                "avg_hr": l.get("average_heartrate"),
                "max_hr": l.get("max_heartrate"),
                "cadence": l.get("average_cadence"),
            })

        s_compact = {}
        if streams:
            for k in ("time", "heartrate", "velocity_smooth", "cadence"):
                if k in streams and "data" in streams[k]:
                    s_compact[k] = streams[k]["data"][:300]  # minder data per run

        slim.append({
            "id": details.get("id"),
            "name": details.get("name"),
            "description": details.get("description"),
            "start_date_local": details.get("start_date_local"),
            "distance_m": details.get("distance"),
            "moving_time_s": details.get("moving_time"),
            "avg_speed_mps": details.get("average_speed"),
            "avg_hr": details.get("average_heartrate"),
            "elev_gain_m": details.get("total_elevation_gain"),
            "type": details.get("type"),
            "laps": laps_slim,
            "streams": s_compact,
        })

    system = prompt_text
    user = (
        "Here are the last 7 running sessions (with description, laps, and shortened streams in JSON). "
        "Create a weekly summary with key metrics, evaluation, and suggested plan for next week.\n\n"
        f"{json.dumps(slim, ensure_ascii=False)}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]


def call_openai_chat(messages: List[Dict[str, str]]) -> str:
    resp = openai.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=1,
    )
    return resp.choices[0].message.content.strip()
