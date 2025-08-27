# weekly_analysis.py
import itertools
from strava_coach_common import (
    list_my_activities, coach_prompt_for_week, call_openai_chat, save_output
)

def main():
    # Fetch enough pages to ensure at least 7 recent runs
    all_recent = []
    for page in range(1, 5):
        page_data = list_my_activities(per_page=50, page=page)
        if not page_data:
            break
        all_recent.extend(page_data)
        if len(all_recent) >= 100:
            break

    # Filter for Runs and take the last 7
    runs = [a for a in all_recent if a.get("type") == "Run"]
    runs_sorted = sorted(runs, key=lambda a: a.get("start_date_local", ""), reverse=True)
    last7 = runs_sorted[:7]
    if not last7:
        print("No recent runs found.")
        return

    messages = coach_prompt_for_week(last7)
    analysis = call_openai_chat(messages)

    raw = {"input_runs": last7, "analysis": analysis}
    save_output("weekly", "last7_runs", analysis, raw)
    print("Weekly analysis saved.")

if __name__ == "__main__":
    main()
