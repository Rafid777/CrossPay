import urllib.request
import json
import sys

runs_url = "https://api.github.com/repos/shahfahim/CrossPay/actions/runs"
req = urllib.request.Request(runs_url, headers={"User-Agent": "Mozilla/5.0"})

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
except Exception as e:
    print(f"Error querying runs: {e}")
    sys.exit(1)

for r in data.get("workflow_runs", [])[:4]:
    print("=" * 60)
    print(f"Workflow: {r['name']}")
    print(f"Run ID:   {r['id']}")
    print(f"Status:   {r['status']}")
    print(f"Outcome:  {r['conclusion']}")
    print(f"URL:      {r['html_url']}")
    
    # Query individual jobs
    jreq = urllib.request.Request(r["jobs_url"], headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(jreq) as jresp:
            jdata = json.loads(jresp.read().decode("utf-8"))
            for j in jdata.get("jobs", []):
                print(f"  - Job: {j['name']} | Status: {j['status']} | Conclusion: {j['conclusion']}")
    except Exception as je:
        print(f"  (Could not fetch jobs: {je})")
