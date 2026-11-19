"""One-shot: commit control-panel changes, push to fork, enable GitHub Pages."""
import os
import subprocess
import sys

import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN = open(r"C:\Users\DEVMACHINE\AppData\Local\Temp\opencode\gh_token.txt", encoding="utf-8").read().strip()
FORK = "https://github.com/Mahvieper/flipkart-minutes-deals.git"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "opencode-deploy",
}


def run(args):
    env = os.environ.copy()
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "http.extraHeader"
    env["GIT_CONFIG_VALUE_0"] = f"AUTHORIZATION: bearer {TOKEN}"
    r = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True)
    if r.returncode:
        print("CMD FAILED:", " ".join(args))
        print("stdout:", r.stdout[-1500:])
        print("stderr:", r.stderr[-1500:])
        sys.exit(1)
    return r.stdout.strip()


print("[1/5] Repointing remotes...")
out = run(["git", "remote"])
if "upstream" not in out.split():
    run(["git", "remote", "rename", "origin", "upstream"])
    print("  renamed origin -> upstream")
if "origin" in run(["git", "remote"]).split():
    run(["git", "remote", "set-url", "origin", FORK])
else:
    run(["git", "remote", "add", "origin", FORK])
print("  origin ->", FORK)

print("[2/5] Staging and committing...")
run(["git", "add", "-A"])
try:
    out = run(["git", "commit", "-m", "Add web control panel for all bot settings"])
    print("  ", out.splitlines()[0])
except SystemExit:
    # Nothing to commit is fine.
    print("  nothing to commit (already up to date)")

print("[3/5] Pushing to fork...")
out = run(["git", "push", "-u", "origin", "main"])
print("  ", out.splitlines()[-1] if out else "ok")

print("[4/5] Enabling GitHub Pages from /docs ...")
r = requests.get("https://api.github.com/repos/Mahvieper/flipkart-minutes-deals/pages",
                 headers=HEADERS, timeout=30)
if r.status_code == 200:
    print("  Pages already configured; ensuring source is /docs")
    r = requests.put("https://api.github.com/repos/Mahvieper/flipkart-minutes-deals/pages",
                     headers=HEADERS, json={"source": {"branch": "main", "path": "/docs"}}, timeout=30)
else:
    r = requests.post("https://api.github.com/repos/Mahvieper/flipkart-minutes-deals/pages",
                      headers=HEADERS, json={"source": {"branch": "main", "path": "/docs"}}, timeout=30)
if r.status_code >= 400:
    print("  Pages API error:", r.status_code, r.text[:300])
else:
    print("  Pages configured:", r.json().get("html_url"))

print("[5/5] Verifying files on fork...")
for path in ("config/settings.json", "docs/index.html", "bot/config.py"):
    rr = requests.get(f"https://api.github.com/repos/Mahvieper/flipkart-minutes-deals/contents/{path}",
                      headers=HEADERS, timeout=30)
    print(f"  {path}: HTTP {rr.status_code}")

print("\nDONE")
