import csv
from pathlib import Path
import datetime 
from collections import Counter, defaultdict

# resolve telemetry.csv in the same folder as this file
BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "telemetry.csv"
HISTORY_CSV   = BASE_DIR / "login_history.csv"
VIEW_HISTORY_CSV = BASE_DIR / "view_history.csv"

def update_telemetry():
    # if it doesn’t exist yet, initialize it
    if not CSV_PATH.exists():
        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([0, 0])

    # now safely read, bump, and write back
    with open(CSV_PATH, "r", newline="") as f:
        reader = csv.reader(f)
        values = next(reader)

    values[0] = str(int(values[0]) + 1)

    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(values)

    
def log_login_history(username: str):
    # ensure header row
    if not HISTORY_CSV.exists():
        with open(HISTORY_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "username"])
    # append timestamp + username
    with open(HISTORY_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.utcnow().isoformat(), username])

def log_view_history(username: str, report_id: str):
    # initialize with header if missing
    if not VIEW_HISTORY_CSV.exists():
        with open(VIEW_HISTORY_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "username", "report_id"])
    # append a new row
    with open(VIEW_HISTORY_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.utcnow().isoformat(), username, report_id])


def get_view_stats():
    total_views = 0
    viewers     = set()
    daily_views = Counter()
    daily_unique = defaultdict(set)
    per_user    = Counter()

    if not VIEW_HISTORY_CSV.exists():
        return {
            "totalViews": 0,
            "totalViewers": 0,
            "dailyViews": [],
            "dailyUniqueViewers": [],
            "viewsByUser": {}
        }

    with open(VIEW_HISTORY_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_views += 1
            u = row["username"]
            per_user[u] += 1
            viewers.add(u)

            date = row["timestamp"][:10]
            daily_views[date] += 1
            daily_unique[date].add(u)

    # build arrays sorted by date
    dv  = [{"date": d, "count": daily_views[d]} for d in sorted(daily_views)]
    duv = [{"date": d, "count": len(daily_unique[d])} for d in sorted(daily_unique)]

    return {
        "totalViews": total_views,
        "totalViewers": len(viewers),
        "dailyViews": dv,
        "dailyUniqueViewers": duv,
        "viewsByUser": dict(per_user)
    }

