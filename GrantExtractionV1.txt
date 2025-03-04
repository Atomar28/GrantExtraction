import asyncio
from playwright.async_api import async_playwright

def select_dropdown_option(page, selector, value):
    """Helper function to select a value from a dropdown."""
    return page.select_option(selector, value)

async def extract_grant_details():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Navigating to the form...")
        await page.goto("https://npc.collegeboard.org/app/northeastern")
        
        # Check for iframe (if needed, we find and switch)
        frames = page.frames
        if len(frames) > 1:
            frame = frames[1]  # Assuming the target iframe is the second one
            print("Switched to correct frame.")
        else:
            frame = page  # Stay on the main page if no iframe is found

        # Getting Started Page
        print("Filling 'Getting Started' page...")
        await page.fill("input[aria-label='The student’s first name (optional)']", "John")
        await select_dropdown_option(page, "select[aria-label='The Student’s state of legal residence']", "Massachusetts")
        await select_dropdown_option(page, "select[aria-label='Who will be answering the questions?']", "The Student")
        await page.click("text=Continue")
        
        # Dependency Status Page
        print("Filling 'Dependency Status' page...")
        await select_dropdown_option(page, "select[aria-label='Your year of birth']", "2002")
        await select_dropdown_option(page, "select[aria-label='Your marital status']", "Never married")
        await page.click("text=No", nth=0)  # Dependent children? No
        await page.click("text=No", nth=1)  # Orphan or ward? No
        await page.click("text=Next")
        
        # Parent Household Page
        print("Filling 'Parent Household' page...")
        await select_dropdown_option(page, "select[aria-label='Your parents' marital status']", "Married")
        await select_dropdown_option(page, "select[aria-label='Your older parent's year of birth']", "1975")
        await select_dropdown_option(page, "select[aria-label='Your parents' state of legal residence']", "Massachusetts")
        await select_dropdown_option(page, "select[aria-label='Number of siblings in your parents' household']", "2")
        await page.click("text=Next")
        
        # Parent Income Page
        print("Filling 'Parent Income' page...")
        await select_dropdown_option(page, "select[aria-label='Type of Federal income tax form your parents filed']", "1040")
        await page.fill("input[aria-label='Your parents' combined adjusted gross income (AGI)']", "80000")
        await page.fill("input[aria-label='Your parents' federal tax payment']", "5000")
        await page.fill("input[aria-label='Work income from one parent']", "40000")
        await page.click("text=Next")
        
        # Parent Assets Page
        print("Filling 'Parent Assets' page...")
        await page.fill("input[aria-label='Current amount in cash, savings, and checking accounts']", "20000")
        await page.click("text=No", nth=0)  # Own a home? No
        await page.fill("input[aria-label='Current value of your parents' investments']", "15000")
        await page.click("text=No", nth=1)  # Own a business? No
        await page.click("text=Next")
        
        # Student Finances Page
        print("Filling 'Student Finances' page...")
        await page.fill("input[aria-label='Combined wages, salaries, and tips from your work']", "5000")
        await page.fill("input[aria-label='Your adjusted gross income (AGI)']", "4500")
        await page.click("text=Next")
        
        # Northeastern Questions Page
        print("Filling 'Northeastern University Questions' page...")
        await select_dropdown_option(page, "select[aria-label='Your housing status in college']", "On campus")
        
        # Calculate
        await page.click("text=Calculate")
        
        print("Waiting for results...")
        await page.wait_for_load_state("networkidle")
        
        # Extract Results (if necessary)
        result_text = await page.text_content(".results-selector")  # Adjust selector if needed
        print("Results:", result_text)
        
        await browser.close()

asyncio.run(extract_grant_details())
