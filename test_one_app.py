import sys, os, time, json, glob
from playwright.sync_api import sync_playwright
import ollama

MODEL_NAME = "qwen2.5:7b"

# Automatically find any PDF resume in current directory or fallback to named PDF
resume_files = glob.glob("*.pdf")
if resume_files:
    RESUME_PATH = os.path.abspath(resume_files[0])
else:
    RESUME_PATH = os.path.abspath("Soham Vishal Seth Resume (2).pdf")

# Possible Opera / Opera GX executable paths on macOS
POSSIBLE_OPERA_PATHS = [
    "/Applications/Opera GX.app/Contents/MacOS/Opera GX",
    "/Applications/Opera.app/Contents/MacOS/Opera",
    os.path.expanduser("~/Applications/Opera GX.app/Contents/MacOS/Opera GX"),
]

OPERA_GX_PATH = None
for path in POSSIBLE_OPERA_PATHS:
    if os.path.exists(path):
        OPERA_GX_PATH = path
        break

CANDIDATE_PROFILE = {
    "first_name": "Soham",
    "last_name": "Vishal Seth",
    "email": "soham.v.seth@gmail.com",
    "phone": "+447344124796",
    "linkedin": "https://www.linkedin.com/in/soham-vishal-seth/",
    "resume_path": RESUME_PATH
}

def generate_cover_letter(job_url):
    print("🤖 [Ollama]: Generating tailored legal cover letter for Soham...")
    prompt = f"""
    Write a 150-word tailored legal application cover letter for Soham Vishal Seth applying for a Vacation Scheme / Legal role at this link: {job_url}.
    Candidate Details:
    - Name: Soham Vishal Seth
    - Education: Law with Business LLB, Queen Mary University of London
    - Experience: Legal Intern at Martinez, Peña & Fernández (Dominican Republic) and Seth Law Office (Canada)
    - Skills: Legal Research, Case Analysis, Legal Writing, Evidence Review
    
    Highlight academic rigor at Queen Mary, international legal internship experience, and interest in commercial law.
    Do NOT use placeholders or bracketed text. Output plain text cover letter only.
    """
    try:
        response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}])
        return response.message.content.strip()
    except Exception as e:
        print(f"⚠️ Ollama warning ({e}), using default fallback cover letter.")
        return ("I am writing to express my strong interest in the Vacation Scheme / legal opportunity at your firm. "
                "As a Law with Business LLB student at Queen Mary University of London with international legal internship "
                "experience in Canada and the Dominican Republic, I bring strong legal research, case analysis, and commercial awareness skills to your firm.")

def run_test_application(job_url):
    cover_letter = generate_cover_letter(job_url)
    
    with sync_playwright() as p:
        print("🌐 [JARVIS]: Launching Opera GX browser...")
        
        launch_kwargs = {"headless": False, "slow_mo": 100}
        if OPERA_GX_PATH:
            print(f"✓ Found Opera GX at: {OPERA_GX_PATH}")
            launch_kwargs["executable_path"] = OPERA_GX_PATH
        else:
            print("⚠️ Opera GX path not found in default locations. Launching Playwright Chromium...")

        browser = p.chromium.launch(**launch_kwargs)
        page = browser.new_page()
        
        print(f"🔗 [JARVIS]: Opening {job_url}...")
        page.goto(job_url, wait_until="domcontentloaded")
        time.sleep(3)

        # Handle cookie banners if present
        try:
            cookie_btn = page.locator("button:has-text('Accept'), button:has-text('Allow'), #onetrust-accept-btn-handler")
            if cookie_btn.count() > 0 and cookie_btn.first.is_visible():
                cookie_btn.first.click()
                time.sleep(1)
        except Exception:
            pass

        url_lower = page.url.lower()

        # Greenhouse ATS
        if "greenhouse.io" in url_lower or page.locator("#application_form").is_visible():
            print("📋 [JARVIS]: Greenhouse form detected.")
            if page.locator("#first_name").is_visible(): page.fill("#first_name", CANDIDATE_PROFILE["first_name"])
            if page.locator("#last_name").is_visible(): page.fill("#last_name", CANDIDATE_PROFILE["last_name"])
            if page.locator("#email").is_visible(): page.fill("#email", CANDIDATE_PROFILE["email"])
            if page.locator("#phone").is_visible(): page.fill("#phone", CANDIDATE_PROFILE["phone"])

            if page.locator("input[placeholder*='LinkedIn'], input[id*='linkedin']").is_visible():
                page.locator("input[placeholder*='LinkedIn'], input[id*='linkedin']").first.fill(CANDIDATE_PROFILE["linkedin"])

            cl_area = page.locator("#cover_letter_text, textarea[name*='cover_letter'], textarea[id*='cover_letter']")
            if cl_area.count() > 0 and cl_area.first.is_visible():
                cl_area.first.fill(cover_letter)
                print("✍️ [JARVIS]: Cover letter inserted.")

            resume_input = page.locator("input[type='file'][id*='resume'], input[type='file'][name*='resume']")
            if resume_input.count() > 0 and os.path.exists(RESUME_PATH):
                resume_input.first.set_input_files(RESUME_PATH)
                print(f"📎 [JARVIS]: Resume attached ({os.path.basename(RESUME_PATH)}).")

        # Lever ATS
        elif "lever.co" in url_lower or page.locator("form#application-form").is_visible():
            print("📋 [JARVIS]: Lever form detected.")
            page.fill("input[name='name']", f"{CANDIDATE_PROFILE['first_name']} {CANDIDATE_PROFILE['last_name']}")
            page.fill("input[name='email']", CANDIDATE_PROFILE["email"])
            page.fill("input[name='phone']", CANDIDATE_PROFILE["phone"])

            if page.locator("input[name*='urls[LinkedIn]']").is_visible():
                page.fill("input[name*='urls[LinkedIn]']", CANDIDATE_PROFILE["linkedin"])

            cl_area = page.locator("textarea[name*='comments'], textarea[name*='cover']")
            if cl_area.count() > 0 and cl_area.first.is_visible():
                cl_area.first.fill(cover_letter)
                print("✍️ [JARVIS]: Cover letter inserted.")

            resume_input = page.locator("input[type='file']")
            if resume_input.count() > 0 and os.path.exists(RESUME_PATH):
                resume_input.first.set_input_files(RESUME_PATH)
                print(f"📎 [JARVIS]: Resume attached ({os.path.basename(RESUME_PATH)}).")

        else:
            print("📋 [JARVIS]: Custom portal/landing page detected.")
            if page.locator("input[name*='first_name'], input[id*='first_name']").is_visible():
                page.locator("input[name*='first_name'], input[id*='first_name']").first.fill(CANDIDATE_PROFILE["first_name"])
            if page.locator("input[name*='last_name'], input[id*='last_name']").is_visible():
                page.locator("input[name*='last_name'], input[id*='last_name']").first.fill(CANDIDATE_PROFILE["last_name"])
            if page.locator("input[type='email']").is_visible():
                page.locator("input[type='email']").first.fill(CANDIDATE_PROFILE["email"])

        print("\n" + "="*50)
        print("✍️ [TAILORED COVER LETTER GENERATED]:")
        print("-" * 50)
        print(cover_letter)
        print("-" * 50)
        print("\n🎯 [OPERA GX BROWSER OPEN]")
        print("• Review the opened page in Opera GX.")
        print("• For A&O Shearman, click 'Apply Now' on the page to open their portal.")
        print("• You can copy/paste the cover letter printed above if required.")
        print("="*50 + "\n")
        
        input("Press ENTER in terminal when finished to close the browser... ")
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = "https://careers.aoshearman.com/en/london-vacation-schemes"
    
    run_test_application(target_url)
