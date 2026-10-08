import os, sys, json, subprocess
from ddgs import DDGS
import ollama

MODEL_NAME = "qwen2.5:7b"
RESUME_PATH = os.path.abspath("Soham Vishal Seth Resume (2).pdf")

# Pre-loaded with Soham Vishal Seth profile data
CANDIDATE_PROFILE = {
    "first_name": "Soham",
    "last_name": "Vishal Seth",
    "email": "soham.v.seth@gmail.com",
    "phone": "+447344124796",
    "location": "London, England",
    "linkedin": "https://www.linkedin.com/in/soham-vishal-seth/",
    "education": "Law with Business LLB, Queen Mary University of London",
    "resume_path": RESUME_PATH
}

SOHAM_RESUME_TEXT = """
SOHAM VISHAL SETH
Location: London, England | Phone: +44 07344124796 | Email: soham.v.seth@gmail.com
LinkedIn: https://www.linkedin.com/in/soham-vishal-seth/

SUMMARY:
Law with Business LLB student at Queen Mary University of London with experience in office and client-facing roles. Skilled in legal research, case analysis, legal writing, evidence review, and handling confidential information.

EDUCATION:
- Bachelor of Laws (LLB), Law with Business | Queen Mary University of London (Sep 2025 - Present)
- International Baccalaureate (IB Diploma) | The English School, Bogota (Sep 2023 - Aug 2025)

EXPERIENCE:
- Legal Intern | Martínez, Peña & Fernández (Santo Domingo, Dominican Republic) [Dec 2025 - Jan 2026]
  Organized 20+ legal documents weekly, maintained client confidentiality, supported legal professionals.
- Legal Intern | Seth Law Office (Mississauga, Canada) [Mar 2025 - Oct 2025]
  Assisted attorneys across 10+ active cases, researched legal precedents, reviewed case files, analyzed witness statements and evidence.
- Simulations: Clifford Chance (Business & Human Rights), Latham & Watkins (White Collar Defence), Fidelity Investments.

SKILLS:
Legal Research, Case Analysis, Legal Writing, Evidence Review, Research & Analysis, Critical Thinking, Client Interaction.
"""

def search_law_jobs():
    print("🔍 [JARVIS]: Searching for active legal opportunities in London...")
    queries = [
        "site:boards.greenhouse.io legal associate london",
        "site:boards.greenhouse.io paralegal london",
        "site:jobs.lever.co legal assistant london",
        "site:jobs.lever.co compliance analyst london"
    ]
    links = []
    ddgs = DDGS()
    for q in queries:
        try:
            results = list(ddgs.text(q, max_results=3))
            for r in results:
                url = r.get("href")
                if url and url not in links:
                    links.append(url)
        except Exception as e:
            print(f"Search warning: {e}")
    return links

def generate_cover_letter(job_url):
    print("🤖 [Ollama]: Tailoring cover letter for Soham Vishal Seth...")
    prompt = f"""
    You are writing a tailored job application cover letter on behalf of candidate Soham Vishal Seth.

    Candidate Details:
    {SOHAM_RESUME_TEXT}

    Target Application URL: {job_url}

    Write a concise, professional cover letter (under 180 words) highlighting Soham Queen Mary Law LLB background, legal intern experience in Canada and Dominican Republic, and legal research skills.
    Do NOT use brackets or placeholders. Return strictly the cover letter text.
    """
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.message.content.strip()
    except Exception as e:
        return ("I am writing to express my interest in this legal role. "
                "As a Law with Business LLB student at Queen Mary University of London with hands-on "
                "legal internship experience, I bring strong legal research, "
                "case analysis, and client management skills to your team.")

def run_bulk_pipeline():
    job_links = search_law_jobs()
    print(f"📍 Found {len(job_links)} law postings.")

    for idx, url in enumerate(job_links, 1):
        print(f"\n==========================================")
        print(f"[{idx}/{len(job_links)}] Preparing Application: {url}")
        print(f"==========================================")

        cover_letter = generate_cover_letter(url)

        profile = CANDIDATE_PROFILE.copy()
        profile["cover_letter"] = cover_letter

        # Launch applier (it will pause for your manual review)
        subprocess.run(["python3", "job_applier.py", url, json.dumps(profile)])

if __name__ == "__main__":
    run_bulk_pipeline()
