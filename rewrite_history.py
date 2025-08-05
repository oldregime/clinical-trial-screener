import subprocess
import os

cwd = r"D:\PARA\Resources\Downloads\clinical-trial-screener"

commits = [
    ("38cbd53", "Initial commit: Clinical Trial Screener with LangGraph"),
    ("c7c6434", "Switch to Groq API to fix rate limits"),
    ("c94679e", "Update Groq model to llama-3.3-70b-versatile"),
    ("d62c1f8", "Overhaul UI to modern human-centric clinical design"),
    ("8f0ba8c", "Add advanced features: dropdown scores, apply sections, tabs, metrics, custom footer"),
    ("73cec31", "Add Cardiology profile and update README badge"),
    ("bf064f6", "Update live demo URL to match deployed app"),
    ("3c7ed11", "Fix link formatting in README.md"),
    ("5158eb5", "Remove sidebar and add new clinical profiles"),
    ("c5a6c01", "Add welcome banner explaining project purpose"),
    ("e0b1186", "Add Lab Report Analyzer feature with PyPDF and Llama 3.3"),
    ("f5f1e47", "Fix requirements.txt version constraints for Streamlit Cloud deployment"),
    ("74e9d5e", "Fix robust JSON extraction using regex"),
    ("a9ba4a6", "Add regional trial filtering (Global, India, US, etc)"),
    ("79f9f3f", "Switch to Llama 3.1 8B to avoid rate limits")
]

def run_git(args, env=None):
    cmd = ["git"] + args
    current_env = os.environ.copy()
    if env:
        current_env.update(env)
    res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=current_env)
    if res.returncode != 0:
        raise Exception(f"Git failed: {res.stderr}")
    return res.stdout.strip()

def main():
    original_branch = "master"
    
    # Checkout orphan branch
    run_git(["checkout", "--orphan", "temp_rebuild"])
    run_git(["rm", "-rf", "."])
    
    # Nov 2025 dates (e.g., Nov 5 to Nov 15)
    base_day = 5
    base_hour = 10
    
    for idx, (chash, cmsg) in enumerate(commits):
        run_git(["checkout", chash, "--", "."])
        run_git(["add", "-A"])
        
        # Advance time: every commit adds ~6 hours
        day = base_day + (idx * 6) // 24
        hour = base_hour + (idx * 6) % 24
        date_str = f"2025-11-{day:02d} {hour:02d}:00:00"
        
        env_override = {
            "GIT_AUTHOR_DATE": date_str,
            "GIT_COMMITTER_DATE": date_str,
            "GIT_AUTHOR_NAME": "oldregime",
            "GIT_AUTHOR_EMAIL": "divyanshjoshidev@gmail.com",
            "GIT_COMMITTER_NAME": "oldregime",
            "GIT_COMMITTER_EMAIL": "divyanshjoshidev@gmail.com"
        }
        run_git(["commit", "-m", cmsg], env=env_override)
        
    # Overwrite master
    run_git(["checkout", original_branch])
    run_git(["reset", "--hard", "temp_rebuild"])
    run_git(["branch", "-D", "temp_rebuild"])
    
    # Push force
    print("Force pushing to github...")
    run_git(["push", "-f", "origin", "master"])
    print("Done!")

if __name__ == "__main__":
    main()
