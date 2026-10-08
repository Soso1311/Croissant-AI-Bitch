import sys, os, time, json
from playwright.sync_api import sync_playwright

def fill_greenhouse(page, data):
    print("📋 [JARVIS]: Filling Greenhouse form for Soham...")
    if page.locator("#first_name").is_visible(): page.fill("#first_name", data.get("first_name", ""))
    if page.locator("#last_name").is_visible(): page.fill("#last_name", data.get("last_name", ""))
    if page.locator("#email").is_visible(): page.fill("#email", data.get("email", ""))
    if page.locator("#phone").is_visible(): page.fill("#phone", data.get("phone", ""))

    # Social Links
    if page.locator("input[placeholder*="LinkedIn"], input[id*="linkedin"]").is_visible():
        page.locator("input[placeholder*="LinkedIn"], input[id*="linkedin"]").first.fill(data.get("linkedin", ""))

    # Cover Letter
    cl_area = page.locator("#cover_letter_text, textarea[name*="cover_letter"], textarea[id*="cover_letter"]")
    if cl_area.count() > 0 and cl_area.first.is_visible():
        cl_area.first.fill(data.get("cover_letter", ""))
        print("✍️ [JARVIS]: Custom legal cover letter inserted.")

    # Resume Upload
    resume_input = page.locator("input[type="file"][id*="resume"], input[type="file"][name*="resume"]")
    if resume_input.count() > 0 and os.path.exists(data.get("resume_path", "")):
        resume_input.first.set_input_files(data["resume_path"])
        print("📎 [JARVIS]: Resume attached.")

def fill_lever(page, data):
    print("📋 [JARVIS]: Filling Lever form for Soham...")
    page.fill("input[name="name"]", f"{data.get("first_name", "")} {data.get("last_name", "")}")
    page.fill("input[name="email"]", data.get("email", ""))
    page.fill("input[name="phone"]", data.get("phone", ""))

    # Social Links
    if page.locator("input[name*="urls[LinkedIn]"]").is_visible():
        page.fill("input[name*="urls[LinkedIn]"]", data.get("linkedin", ""))

    # Cover Letter / Comments
    cl_area = page.locator("textarea[name*="comments"], textarea[name*="cover"]")
    if cl_area.count() > 0 and cl_area.first.is_visible():
        cl_area.first.fill(data.get("cover_letter", ""))
        print("✍️ [JARVIS]: Custom legal cover letter inserted.")

    # Resume Upload
    resume_input = page.locator("input[type="file"]")
    if resume_input.count() > 0 and os.path.exists(data.get("resume_path", "")):
        resume_input.first.set_input_files(data["resume_path"])
        print("📎 [JARVIS]: Resume attached.")

def apply_to_job(job_url: str, candidate_data: dict):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()
        print(f"🌐 [JARVIS]: Navigating to {job_url}...")
        try:
            page.goto(job_url, wait_until="domcontentloaded")
            time.sleep(2)
            url = page.url.lower()
            if "greenhouse.io" in url or page.locator("#application_form").is_visible():
                fill_greenhouse(page, candidate_data)
            elif "lever.co" in url or page.locator("form#application-form").is_visible():
                fill_lever(page, candidate_data)
            
            print("
" + "="*50)
            print("⏸️ [JARVIS PAUSED FOR HUMAN REVIEW]")
            print("• Form filled with profile details & custom cover letter.")
            print("• Resume uploaded.")
            print("👉 Check the open browser window, verify details, click SUBMIT when ready.")
            print("="*50 + "
")
            
            input("Press ENTER in this terminal once you have submitted (or to skip to next job)... ")
            
        except Exception as e:
            print(f"❌ Error during form filling: {e}")
        browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        url = sys.argv[1]
        data = json.loads(sys.argv[2])
        apply_to_job(url, data)
