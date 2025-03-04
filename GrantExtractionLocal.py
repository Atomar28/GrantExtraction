import asyncio
import csv
from playwright.async_api import async_playwright

# Constants
FORM_URL = "file:///Users/anshumantomar/Desktop/test_form.html"  # Local HTML file path
OUTPUT_CSV = "/Users/anshumantomar/Desktop/output_grant_details.csv"
INPUT_CSV = "/Users/anshumantomar/Desktop/income_values.csv"

async def extract_grant_details():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)  # Keep browser visible for testing by slowing it down
        page = await browser.new_page()
        
        # Reads income values from CSV
        with open(INPUT_CSV, newline='') as csvfile:
            reader = csv.reader(csvfile)
            income_values = [row[0] for row in reader if row]
        
        output_data = []
        
        for income in income_values:
            await page.goto(FORM_URL)
            
            # Fills form fields
            await page.fill("input[name='name']", "John Doe")  # Static value
            await page.fill("input[name='age']", "30")  # Static value
            await page.evaluate("(value) => document.querySelector(\"input[name='income']\").value = value", str(income))  # Dynamic income
            
            # Submits form
            await page.click("button[type='submit']")
            
            # Waits for result to appear
            await page.wait_for_selector("#grant-details", timeout=5000)
            
            # Extracts grant details
            grant_details = await page.inner_text("#result")
            output_data.append([income, grant_details])
        
        await browser.close()
        
        # Writes extracted details to the CSV file
        with open(OUTPUT_CSV, "w", newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Income", "Grant Details"])
            writer.writerows(output_data)

# Run the script
asyncio.run(extract_grant_details())
