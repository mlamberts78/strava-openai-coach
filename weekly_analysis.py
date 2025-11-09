# weekly_analysis.py
from strava_coach_common import (
    list_my_activities,
    get_activity,
    get_activity_laps,
    get_activity_streams,
    coach_prompt_for_week,
    call_openai_chat,
    save_output
)

def main():
    # Fetch enough pages to ensure at least 7 recent runs
    all_recent = []
    for page in range(1, 5):
        page_data = list_my_activities(per_page=50, page=page)
        if not page_data:
            break
        all_recent.extend(page_data)
        if len(all_recent) >= 200:  # safety limit
            break

    # Filter for Runs and take the last 7
    runs = [a for a in all_recent if a.get("type") in ("Run", "VirtualRun")]
    runs_sorted = sorted(runs, key=lambda a: a.get("start_date_local", ""), reverse=True)
    last7 = runs_sorted[:7]

    if not last7:
        print("No recent runs found.")
        return

    enriched_runs = []
    for run in last7:
        details = get_activity(run["id"])
        try:
            laps = get_activity_laps(run["id"])
        except Exception:
            laps = []
        try:
            streams = get_activity_streams(run["id"], ["time", "heartrate", "velocity_smooth", "cadence"])
        except Exception:
            streams = {}
        enriched_runs.append({"details": details, "laps": laps, "streams": streams})

    # Generate prompt dynamically from WEEKLY_PROMPT_FILE
    messages = coach_prompt_for_week(enriched_runs)
    analysis = call_openai_chat(messages)

    raw = {"input_runs": enriched_runs, "analysis": analysis}
    save_output("weekly", "last7_runs", analysis, raw)

    print("Weekly analysis saved.")

if __name__ == "__main__":
    main()
