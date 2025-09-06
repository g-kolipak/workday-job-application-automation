from playwright.sync_api import Playwright, sync_playwright, expect
import time
import re
import os

# Define a list of jobs with their names and IDs
jobs = [
    {"name": "Office Aide", "id": "JR112396"},
    # Add more jobs as needed
]

# File paths
COVER_LETTER_DIR = "/path/to/cover/letters"
RESUME_PATH = "/path/to/resume.pdf"

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.myworkday.com/asu/d/task/1422$3898.htmld")

    # Login process
    page.locator("#username").click()
    page.locator("#username").fill("")
    page.locator("#username").press("Tab")
    page.locator("#password").press("CapsLock")
    page.locator("#password").fill("")
    page.get_by_role("button", name="Sign In").click()
    time.sleep(5)
    page.get_by_role("button", name="Yes, this is my device").click()

    # Track successful applications
    successful_applications = 0
    total_jobs = len(jobs)

    # Apply for each job
    for job in jobs:
        job_name = job["name"]
        job_id = job["id"]
        print(f"Applying for job: {job_name} ({job_id})")
        try:
            # Navigation process
            page.get_by_role("button", name="MENU").click()
            page.get_by_role("link", name="Jobs Hub").click()
            page.get_by_role("link", name="Find Student Jobs").click()

            page.evaluate("window.scrollBy({ top: 500, behavior: 'smooth' })")
            page.wait_for_timeout(1000)  # wait for scroll to complete

            time.sleep(3)

            # Select job
            page.get_by_role("link", name=job_name).nth(0).click()
            time.sleep(5)
            # Application process
            page.get_by_role(
                "button", name="Apply Student Internal Career").click()

            # Upload resume
            file_input = page.locator('input[type="file"]')
            if not os.path.exists(RESUME_PATH):
                print(f"Resume not found at {RESUME_PATH}")
                continue
            file_input.set_input_files(RESUME_PATH)

            time.sleep(5)
            page.get_by_role("button", name="Next", exact=True).click()
            page.wait_for_load_state("load")

            # Fill job history
            page.locator(
                "[data-automation-id='textInput'][data-metadata-id='textInput.jobHistoryCompany'] input[data-automation-id='textInputBox']").nth(0).fill("N/A")
            page.locator("[data-automation-id='textInput'][data-metadata-id='textInput.jobHistoryCompany'] input[data-automation-id='textInputBox']").nth(
                1).fill("")
            page.locator(
                "[data-automation-id='panelSetRowDeleteButton']").nth(3).click()

            time.sleep(3)
            # Upload cover letter
            cover_letter_path = os.path.join(
                COVER_LETTER_DIR, f"{job_id} cover letter.pdf")
            if not os.path.exists(cover_letter_path):
                print(
                    f"Cover letter not found for {job_id}: {cover_letter_path}")
                continue
            file_input = page.locator('input[type="file"]')
            file_input.set_input_files(cover_letter_path)

            time.sleep(6)

            # Proceed to next steps
            page.get_by_role("button", name="Next", exact=True).click()

            # Answer eligibility questions
            page.wait_for_load_state("load")
            page.get_by_label("Are you currently eligible to").click()
            page.get_by_role("option", name="Yes").locator(
                "div").nth(1).click()
            page.get_by_label("Are you or will you be").click()
            page.get_by_role("option", name="Yes").locator(
                "div").nth(1).click()
            page.get_by_label("Are you eligible for Federal").click()
            page.get_by_role("option", name="Yes").locator(
                "div").nth(1).click()
            page.get_by_label("Are you 18 years or older?").click()
            page.get_by_role("option", name="Yes").locator(
                "div").nth(1).click()
            page.get_by_role("button", name="Next", exact=True).click()

            page.wait_for_load_state("load")

            # Select demographics
            page.get_by_text("No", exact=True).click()
            page.locator("div").filter(has_text=re.compile(
                r"^Asian \(United States of America\)$")).locator("div").click()
            page.get_by_label("Please select your gender.").click()
            page.get_by_role("option", name="Male", exact=True).locator(
                "div").nth(1).click()
            page.get_by_label("Please select your Veteran").click()
            page.get_by_role("option", name="Not a Veteran").locator(
                "div").nth(1).click()
            page.locator("[data-automation-id='checkboxPanel']").nth(6).click()
            page.get_by_role("button", name="Next", exact=True).click()

            page.wait_for_load_state("load")

            # Fill out personal information
            page.get_by_label("Name").click()
            page.get_by_label("Name").fill("Your Name")
            time.sleep(2)
            page.get_by_label("Calendar").click()
            time.sleep(1)
            page.get_by_label("Selected Today Thu 4 Sep").click()
            time.sleep(1)
            page.locator(".WMWF").first.click()
            time.sleep(4)

            page.get_by_label("Please check one of the boxes").locator("div").filter(
                has_text="I do not want to answer").locator("div").first.click()

            page.get_by_role("button", name="Next", exact=True).click()
            page.get_by_role("button", name="Submit").click()
            time.sleep(5)
            page.get_by_role("button", name="Done").click()

            print(f"Successfully submitted application for {job_name}")
            successful_applications += 1
            time.sleep(5)  # Wait before starting next application

        except Exception as e:
            print(f"Failed to apply for {job_name} ({job_id}): {str(e)}")
            continue  # Continue to the next job

    # Summary
    print(
        f"Completed: {successful_applications}/{total_jobs} applications submitted successfully")

    # Close the browser
    time.sleep(20)
    browser.close()

# Run the script
with sync_playwright() as playwright:
    run(playwright)