import os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT=os.path.dirname(os.path.abspath(__file__))
T=open(r"C:\Users\DEVMACHINE\AppData\Local\Temp\opencode\gh_token.txt",encoding="utf-8").read().strip()
U=f"https://x-access-token:{T}@github.com/Mahvieper/flipkart-minutes-deals.git"
env=os.environ.copy(); env["GIT_TERMINAL_PROMPT"]="0"; env["GIT_CONFIG_COUNT"]="2"
env["GIT_CONFIG_KEY_0"]="credential.helper"; env["GIT_CONFIG_VALUE_0"]=""
env["GIT_CONFIG_KEY_1"]="http.extraHeader"; env["GIT_CONFIG_VALUE_1"]=""
def run(a):
    r=subprocess.run(a,cwd=ROOT,env=env,capture_output=True,text=True)
    if r.returncode: print("FAIL",a[:2],r.stdout[-600:],r.stderr[-600:]); sys.exit(1)
    return r
run(["git","add","-A"])
run(["git","commit","-m","Remove one-shot deploy helper from repository"])
r=run(["git","push",U,"main"])
print((r.stdout+r.stderr).strip().splitlines()[-1])
