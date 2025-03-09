import asyncio
import csv
from playwright.async_api import async_playwright

async def select_dropdown_option(page, selector, value):
    """Helper function to select a value from a dropdown."""
    await page.select_option(selector, value)

async def extract_grant_details():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)  # Show browser with delay
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Navigating to the form...")
        await page.goto("https://npc.collegeboard.org/app/northeastern/start")
        await page.wait_for_load_state("networkidle")  # Ensure page fully loads
        
        # Debugging: Print all available form fields
        elements = await page.query_selector_all("input, select, button")
        for e in elements:
            print(await e.get_attribute("name"), await e.get_attribute("aria-label"))
        
        agi_values = [str(i) for i in range(50000, 210000, 10000)]  # AGI values from 50k to 200k
        results = []
        
        for agi in agi_values:
            print(f"Processing AGI value: {agi}")
            
            # Getting Started Page
            print("Filling 'Getting Started' page...")
            await page.get_by_label("First Name").fill("John")
            await select_dropdown_option(page, "select[aria-label='The Student’s state of legal residence']", "Massachusetts")
            await select_dropdown_option(page, "select[aria-label='Who will be answering the questions?']", "The Student")
            await page.wait_for_timeout(1000)  # Small delay before clicking
            await page.click("text=Continue")
            
            # Dependency Status Page
            print("Filling 'Dependency Status' page...")
            await select_dropdown_option(page, "select[aria-label='Your year of birth']", "2002")
            await select_dropdown_option(page, "select[aria-label='Your marital status']", "Never married")
            await page.locator("text=No").nth(0).click()  # Dependent children? No
            await page.locator("text=No").nth(1).click()  # Orphan or ward? No
            await page.wait_for_timeout(1000)
            await page.click("text=Next")
            
            # Parent Household Page
            print("Filling 'Parent Household' page...")
            await select_dropdown_option(page, "select[aria-label='Your parents' marital status']", "Married")
            await select_dropdown_option(page, "select[aria-label='Your older parent's year of birth']", "1975")
            await select_dropdown_option(page, "select[aria-label='Your parents' state of legal residence']", "Massachusetts")
            await select_dropdown_option(page, "select[aria-label='Number of siblings in your parents' household']", "2")
            await page.wait_for_timeout(1000)
            await page.click("text=Next")
            
            # Parent Income Page
            print("Filling 'Parent Income' page...")
            await select_dropdown_option(page, "select[aria-label='Type of Federal income tax form your parents filed']", "1040")
            await page.get_by_label("Your parents' combined adjusted gross income (AGI)").fill(agi)
            await page.get_by_label("Your parents' federal tax payment").fill("5000")
            await page.get_by_label("Work income from one parent").fill("40000")
            await page.wait_for_timeout(1000)
            await page.click("text=Next")
            
            # Parent Assets Page
            print("Filling 'Parent Assets' page...")
            await page.get_by_label("Current amount in cash, savings, and checking accounts").fill("20000")
            await page.locator("text=No").nth(0).click()  # Own a home? No
            await page.get_by_label("Current value of your parents' investments").fill("15000")
            await page.locator("text=No").nth(1).click()  # Own a business? No
            await page.wait_for_timeout(1000)
            await page.click("text=Next")
            
            # Student Finances Page
            print("Filling 'Student Finances' page...")
            await page.get_by_label("Combined wages, salaries, and tips from your work").fill("5000")
            await page.get_by_label("Your adjusted gross income (AGI)").fill("4500")
            await page.wait_for_timeout(1000)
            await page.click("text=Next")
            
            # Northeastern Questions Page
            print("Filling 'Northeastern University Questions' page...")
            await select_dropdown_option(page, "select[aria-label='Your housing status in college']", "On campus")
            await page.wait_for_timeout(1000)
            
            # Calculate
            await page.click("text=Calculate")
            
            print("Waiting for results...")
            await page.wait_for_selector(".results-selector", timeout=10000)  # Ensure result loads
            
            # Extract Results
            tuition = await page.text_content(".tuition-selector")
            pell_grant = await page.text_content(".pell-grant-selector")
            institutional_grant = await page.text_content(".institutional-grant-selector")
            
            results.append([agi, tuition, pell_grant, institutional_grant])
            
            print(f"AGI: {agi}, Tuition: {tuition}, Pell Grant: {pell_grant}, Institutional Grant: {institutional_grant}")
        
        # Save to CSV
        with open("grant_results.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["AGI", "Tuition", "Pell Grant", "Institutional Grant"])
            writer.writerows(results)
        
        print("Results saved to grant_results.csv")
        await browser.close()

asyncio.run(extract_grant_details())