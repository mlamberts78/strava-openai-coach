[![Buy me a coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/mlamberts7I)
[![PayPal](https://img.shields.io/badge/Donate-PayPal-blue?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=HZUUW64FRM2J2)
# Strava AI Coach

AI-powered Strava training analyzer that fetches your latest activities (including laps and descriptions) via the Strava API and generates personalized insights, race predictions, and training suggestions using OpenAI.  

The project supports:
- **Daily analysis** → Analyze your most recent activity every day
- **Weekly analysis** → Summarize and analyze your last 7 running sessions
- **Lap analysis** → Detect and evaluate intervals or structured workouts
- **Custom prompts** → Define separate prompts for daily and weekly analyses
- **File-based output** → Store AI feedback in Markdown files for easy review

---

## 🚀 Features

- Fetch activities automatically from Strava API  
- Include activity metadata, description, and laps in the analysis  
- Generate insights with OpenAI, as if written by a professional running coach  
- Store results in `daily/` and `weekly/` folders  
- Customizable prompts via `prompts/` directory  
- Secure environment variables via `.env`  

---

## ⚙️ Setup

### 1. Clone repository
```bash
git clone https://github.com/mlamberts78/strava-openai-coach.git
cd strava-openai-coach
```
### 2. Install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### 3. Configure .env

Create a .env file in the root directory with:

```bash
cp -rp .env.sample .env
```
Edit .env
### Strava API
STRAVA_CLIENT_ID=your_client_id

STRAVA_CLIENT_SECRET=your_client_secret

### OpenAI API
OPENAI_API_KEY=your_openai_key

🔑 create your OpenAI API key here: https://platform.openai.com/api-keys

### 4. Get Strava refresh token

Use the get_strava_tokens.py helper, run it while your venv is active; it will open the URL for you and store data/strava_tokens.json automatically.

```bash
. .venv/bin/activate
python get_strava_tokens.py
```

### 4. Customizing Prompts

daily_prompt.txt → used for daily activity analysis

weekly_prompt.txt → used for weekly summary analysis

Edit these files to adjust how openai analyzes your runs (e.g., focus on pacing, intervals, recovery, or race prediction).

Samples can be used:
```bash
cp -rp daily_prompt.txt.sample daily_prompt.txt
cp -rp weekly_prompt.txt.sample weekly_prompt.txt
```

**TIP:** Create the prompt in your own language, and the report will be generated in that same language.

## 🏃 Usage

### Daily analysis

Fetch the most recent activity and run the daily prompt:
```bash
. .venv/bin/activate
python daily_check.py
```

Output → daily/YYYYMMDD-HHMMSS_activity_{id}.md

### Weekly analysis

Fetch last 7 runs and generate a summary:
```bash
. .venv/bin/activate
python weekly_analysis.py
```

Output → weekly/YYYYMMDD-HHMMSS_last7_runs.md

## 📅 Automation

To run automatically on a Linux server, set up cron jobs:

### Daily analysis at 06:00
0 6 * * * /path/to/venv/bin/python /path/to/daily_analysis.py >> /var/log/strava_daily.log 2>&1

### Weekly analysis every Monday at 07:00
0 7 * * MON /path/to/venv/bin/python /path/to/weekly_analysis.py >> /var/log/strava_weekly.log 2>&1

## 📊 Example output

Daily analysis file (20250827-105308_activity_15601264415.md):

Here’s your session review.

### 1) Summary
- Session: Morning Interval Run — 4 x 6 min @ ~4:45/km (2 min easy jog recoveries)
- Distance: 9.41 km
- Time: 50:17
- Overall pace: 5:20/km
- Elevation gain: 7 m (flat)
- Heart rate: avg 151 bpm, max 165 bpm
- Cadence: easy 88–92 spm; work reps 95–98 spm (consistent increase at faster pace)

### 2) Intervals/blocks (from laps)
Warm-up (L1–2): 1.70 km in 9:59 @ ~5:52/km, avg HR ~133 bpm

Rep 1 (L3+4 = 6:00): 1.266 km @ 4:44/km, avg HR ~153 bpm, cadence ~95–96
Recovery 1 (L5 = 2:00): 0.286 km @ 6:56/km, avg HR 143 bpm (≈10 bpm drop)

Rep 2 (L6+7 = 6:00): 1.267 km @ 4:43/km, avg HR ~156 bpm, cadence ~96
Recovery 2 (L8 = 2:00): 0.283 km @ 7:00/km, avg HR 147 bpm (≈9 bpm drop)

Rep 3 (L9+10 = 6:00): 1.269 km @ 4:43/km, avg HR ~159 bpm, cadence ~97
Recovery 3 (L11 = 2:00): 0.287 km @ 6:54/km, avg HR 152 bpm (≈7 bpm drop)

Rep 4 (L12+13 = 6:00): 1.274 km @ 4:42/km, avg HR ~160 bpm, cadence ~98

Cool-down (L14–16): 1.78 km in 10:16 @ ~5:46/km, avg HR ~155 bpm

### Notes:
- Pacing on reps was very tight: 4:44, 4:43, 4:43, 4:42 — you hit the brief perfectly and finished slightly faster.
- HR rose progressively across reps (≈153 → 156 → 159 → 160), a normal, controlled drift for threshold-type work.
- Recovery HR drops diminished slightly (10 → 9 → 7 bpm), showing accumulating fatigue but still well-managed.
- Cadence appropriately increased on work reps and was consistent rep-to-rep.

### 3) Strengths and areas for improvement
Strengths
- Excellent execution vs target pace with minimal variability and a slight negative split.
- Controlled, modest HR drift across reps; max HR only 165, indicating you stayed in the threshold/upper-tempo range.
- Cadence consistent and appropriately higher in work segments.
- Flat route minimized confounders; you managed recoveries at genuinely easy paces.

### Areas for improvement
- Warm-up was on the short side for threshold work; first rep HR was notably lower than later reps, suggesting you weren’t fully primed.
- Recovery HR didn’t drop as much by rep 3, hinting at rising fatigue; not problematic, but watch that trend in hotter days or tougher weeks.
- Cool-down HR stayed relatively high (~155 bpm). Consider extending or easing the first few minutes to bring HR down more gradually.

### 4) Concrete training advice for next time
- Warm-up: 12–15 min easy + 3–4 x 20 s strides with 40 s easy between. This will raise HR/neuromuscular activation so rep 1 matches later reps.
- Pacing cue: Keep reps at 4:44–4:46/km for the first 3–4 minutes, then allow a gentle squeeze to 4:42–4:44 in the final 2 minutes (as you did on the last rep).
- Recovery: Keep the 2:00 jog very easy (≈6:50–7:10/km) and aim for ≥10–12 bpm drop in the first minute. If heat/fatigue limits HR drop, slow the jog further rather than standing.
- Progression options (choose one, not multiple, on a given week):
  - Add a 5th x 6 min at same pace,
  - Or shorten recoveries to 90 s at same pace,
  - Or keep 4 x 6 min and nudge pace to 4:42–4:43/km.
- Cool-down: 10–15 min easy. If HR remains >150 after 5 min, back off pace a touch until it settles.
- Form cues: Maintain relaxed shoulders, slight forward lean, quick but relaxed cadence (as recorded). Avoid overstriding as you fatigue.
- Week structure: Follow this with an easy day or two. Complement with 1 short hill/strength session (e.g., 8–10 x 10–15 s hills) later in the week and light mobility for calves/hips post-run.

## Excellent, disciplined session — you matched the plan precisely and finished strong.

==================

## In case of issues with the STRAVA refresh token:

You need a refresh token so the script can obtain a (short-lived) access token.

#### Option A — helper script (get_strava_tokens.py) 

Use the **get_strava_tokens.py** helper, run it while your venv is active; it will open the URL for you and store data/strava_tokens.json automatically.

#### Option B — Browser + curl (manual)

Open this URL in your browser (replace CLIENT_ID and REDIRECT_URI accordingly — redirect_uri can be any valid redirect you set in your Strava app):

https://www.strava.com/oauth/authorize?client_id=CLIENT_ID&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read,activity:read_all

After authorizing you get a code in the redirect URL: ?code=XXXX.

Exchange the code for tokens:

curl -X POST https://www.strava.com/oauth/token \
  -F client_id=CLIENT_ID \
  -F client_secret=CLIENT_SECRET \
  -F code=XXXX \
  -F grant_type=authorization_code

Save refresh_token from the response into .env as STRAVA_REFRESH_TOKEN (or place it into data/strava_tokens.json as described below).
