# daily_check.py
import sys
from strava_coach_common import (
    list_my_activities,
    get_activity,
    get_activity_streams,
    get_activity_laps,
    load_state,
    save_state,
    coach_prompt_for_single,
    call_openai_chat,
    save_output
)

def main():
    state = load_state()
    last_seen = state.get("last_seen_activity_id")

    # Fetch the most recent activity
    latest_list = list_my_activities(per_page=1, page=1)
    if not latest_list:
        print("No activities found.")
        return

    latest = latest_list[0]
    latest_id = latest["id"]

    if str(latest_id) == str(last_seen):
        print(f"No new activity. Last seen: {last_seen}")
        return

    # Fetch activity details
    details = get_activity(latest_id)
    streams, laps = {}, []

    if details.get("type") == "Run":
        try:
            streams = get_activity_streams(latest_id, ["time", "heartrate", "velocity_smooth", "cadence"])
        except Exception as e:
            print(f"Streams not available: {e}")
        try:
            laps = get_activity_laps(latest_id)
        except Exception as e:
            print(f"Laps not available: {e}")

    # Generate prompt dynamically from DAILY_PROMPT_FILE
    messages = coach_prompt_for_single(details, streams, laps)
    analysis = call_openai_chat(messages)

    # Save results
    slug = f"activity_{latest_id}"
    raw = {"activity": details, "streams": streams, "laps": laps, "analysis": analysis}
    save_output("daily", slug, analysis, raw)

    # Update state
    state["last_seen_activity_id"] = latest_id
    save_state(state)

    print(f"New activity {latest_id} analyzed and saved.")

if __name__ == "__main__":
    sys.exit(main())
