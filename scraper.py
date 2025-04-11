import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome WebDriver
options = Options()
options.add_argument("--headless")  # Headless mode
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 40)

# Set up SQLite
conn = sqlite3.connect('eudamed_data.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS device_data (
    udi_di TEXT,
    version TEXT,
    last_update_date TEXT,
    actor_name TEXT,
    actor_id TEXT,
    address TEXT,
    country TEXT,
    telephone TEXT,
    email TEXT,
    version_2 TEXT,
    last_update_date_2 TEXT,
    applicable_legislation TEXT,
    basic_udi TEXT,
    kit TEXT,
    system_procedure TEXT,
    authorised_rep TEXT,
    special_device_type TEXT,
    risk_class TEXT,
    implantable TEXT,
    suture_device TEXT,
    measuring_function TEXT,
    reusable_instrument TEXT,
    active_device TEXT,
    admin_device TEXT,
    companion_diagnostic TEXT,
    near_patient_testing TEXT,
    patient_self_testing TEXT,
    professional_testing TEXT,
    reagent TEXT,
    instrument TEXT,
    device_model TEXT,
    device_name TEXT,
    human_tissues TEXT,
    animal_tissues TEXT,
    microbial_origin TEXT,
    medicinal_product TEXT,
    blood_product TEXT,
    version_3 TEXT,
    last_update_date_3 TEXT,
    udi_di_code TEXT,
    status TEXT,
    secondary_udi TEXT,
    nomenclature_code TEXT,
    trade_name TEXT,
    catalogue_number TEXT,
    direct_marking TEXT,
    unit_of_use TEXT,
    quantity TEXT,
    udi_pi TEXT,
    product_description TEXT,
    info_url TEXT,
    clinical_sizes TEXT,
    single_use TEXT,
    max_reuses TEXT,
    sterilisation TEXT,
    sterile TEXT,
    latex TEXT,
    handling_conditions TEXT,
    warnings TEXT,
    reprocessed TEXT,
    intended_purpose TEXT,
    market_member_state TEXT,
    med_product_2 TEXT,
    version_4 TEXT,
    last_update_date_4 TEXT,
    available_member_state TEXT,
    sscp_ref TEXT,
    sscp_rev TEXT,
    issue_date TEXT,
    certificate_numbers TEXT
)
''')
conn.commit()

# Navigate to site
driver.get("https://ec.europa.eu/tools/eudamed/#/screen/search-device?submitted=true")

# Set items per page
dropdown = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "p-dropdown")))
driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
dropdown.click()

option_50 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[aria-label='50']")))
option_50.click()

# Wait for data to load
time.sleep(5)
# Determine the total number of pages
try:
    pagination_buttons = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//button[contains(@aria-label, 'Page number')]")))
    total_pages = int(pagination_buttons[-1].text)
except Exception:
    total_pages = 20000

print(f"Total pages found: {total_pages}")

# Example: Visit a few pages for demonstration
pages_to_visit = list(range(1, total_pages + 1))
for page in pages_to_visit:
    try:
        print(f"Visiting page {page}")
        page_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//button[contains(@aria-label, 'Page number {page} ')]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", page_button)
        page_button.click()
        time.sleep(3)

        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        for i, row in enumerate(rows):
            try:
                view_button = row.find_element(By.XPATH, ".//button[@title='View detail']")
                driver.execute_script("arguments[0].scrollIntoView(true);", view_button)
                view_button.click()

                # Example scraping
                def safe_get(xpath):
                    try:
                        return wait.until(EC.presence_of_element_located((By.XPATH, xpath))).text.strip()
                    except:
                        return ""
                    
                udi_di = safe_get("//dt[text()='UDI-DI code / Issuing entity']/following-sibling::dd/div")
                version = safe_get("(//ul[@id='versionStatus']/li/strong)[1]")
                last_update = safe_get("(//ul[@id='versionStatus']/li[contains(text(), 'Last update date:')])[1]").replace("Last update date: ", "")
                actor_name = safe_get("(//dt[text()='Actor/Organisation name']/following-sibling::dd/div)[1]")
                actor_id = safe_get("//dt[text()='Actor ID/SRN']/following-sibling::dd/div")
                address = safe_get("//dt[text()='Address']/following-sibling::dd/div")
                country = safe_get("//dt[text()='Country']/following-sibling::dd/div")
                telephone = safe_get("//dt[text()='Telephone number']/following-sibling::dd/div")
                email = safe_get("//dt[text()='Email']/following-sibling::dd/div")
                version_2 = safe_get("(//ul[@id='versionStatus']/li/strong)[2]")
                last_update_2 = safe_get("(//ul[@id='versionStatus']/li[contains(text(), 'Last update date:')])[2]").replace("Last update date: ", "")
                applicable_legislation = safe_get("//dt[contains(text(), 'Applicable legislation')]/following-sibling::dd/div")
                basic_udi = safe_get("//dt[contains(text(), 'UDI-DI/EUDAMED')]/following-sibling::dd/div")
                kit = safe_get("//dt[contains(text(), 'Kit')]/following-sibling::dd/div")
                system_procedure = safe_get("//dt[contains(text(), 'System')]/following-sibling::dd/div")
                authorised_rep = safe_get("//dt[contains(text(), 'Authorised representative')]/following-sibling::dd/div")
                special_device_type = safe_get("//dt[contains(text(), 'Special device Type')]/following-sibling::dd/div")
                risk_class = safe_get("//dt[contains(text(), 'Risk class')]/following-sibling::dd/div")
                implantable = safe_get("//dt[contains(text(), 'Implantable')]/following-sibling::dd/div")
                suture_device = safe_get("//dt[contains(text(), 'Is the device a suture, ')]/following-sibling::dd/div")
                measuring_function = safe_get("//dt[contains(text(), 'Measuring function')]/following-sibling::dd/div")
                reusable_instrument = safe_get("//dt[contains(text(), 'Reusable surgical instrument')]/following-sibling::dd/div")
                active_device = safe_get("//dt[contains(text(), 'Active device')]/following-sibling::dd/div")
                admin_device = safe_get("//dt[contains(text(), 'Device intended to administer and / or remove medicinal product')]/following-sibling::dd/div")
                companion_diagnostic = safe_get("//dt[contains(text(), 'Companion diagnostic')]/following-sibling::dd/div")
                near_patient_testing = safe_get("//dt[contains(text(), 'Near patient testing')]/following-sibling::dd/div")
                patient_self_testing = safe_get("//dt[contains(text(), 'Patient self testing')]/following-sibling::dd/div")
                professional_testing = safe_get("//dt[contains(text(), 'Professional testing')]/following-sibling::dd/div")
                reagent = safe_get("//dt[contains(text(), 'Reagent')]/following-sibling::dd/div")
                instrument = safe_get("//dt[contains(text(), 'Instrument')]/following-sibling::dd/div")
                device_model = safe_get("//dt[contains(text(), 'Device model')]/following-sibling::dd/div")
                device_name = safe_get("//dt[contains(text(), 'Device name')]/following-sibling::dd/div")

                presence_of_human_tissues = safe_get("//dt[text()='Presence of human tissues and cells or their derivatives']/following-sibling::dd/div")
                presence_of_animal_tissues = safe_get("//dt[text()='Presence of animal tissues and cells or their derivatives']/following-sibling::dd/div")
                presence_of_microbial_origin = safe_get("//dt[contains(text(), 'Presence of cells or substances of microbial origin')]/following-sibling::dd/div")
                presence_of_medicinal_product = safe_get("//dt[text()='Presence of a substance which, if used separately, may be considered to be a medicinal product']/following-sibling::dd/div")
                presence_of_blood_product = safe_get("//dt[text()='Presence of a substance which, if used separately, may be considered to be a medicinal product derived from human blood or human plasma']/following-sibling::dd/div")

                version_3 = safe_get("(//ul[@id='versionStatus']/li/strong)[3]")
                last_update_3 = safe_get("(//ul[@id='versionStatus']/li[contains(text(), 'Last update date:')])[3]").replace("Last update date: ", "")
                status = safe_get("//dt[text()='Status']/following-sibling::dd/div")
                secondary_udi = safe_get("//dt[text()='UDI-DI from another entity (secondary)']/following-sibling::dd/div")
                nomenclature_code = safe_get("//dt[text()='Nomenclature code(s)']/following-sibling::dd/div")
                trade_name = safe_get("//dt[text()='Name/Trade name(s)']/following-sibling::dd/div")
                catalogue_number = safe_get("//dt[text()='Reference / Catalogue number']/following-sibling::dd/div")
                direct_marking = safe_get("//dt[text()='Direct marking DI']/following-sibling::dd/div")
                unit_of_use = safe_get("//dt[contains(text(), 'Unit of use')]/following-sibling::dd/div")
                quantity = safe_get("//dt[text()='Quantity of device']/following-sibling::dd/div")
                udi_pi = safe_get("//dt[text()='Type of UDI-PI']/following-sibling::dd/div")
                product_description = safe_get("//dt[text()='Additional Product description']/following-sibling::dd/div")
                info_url = safe_get("//dt[text()='Additional information url']/following-sibling::dd/div")
                clinical_sizes = safe_get("//dt[text()='Clinical sizes']/following-sibling::dd/div")
                single_use = safe_get("//dt[text()='Labelled as single use']/following-sibling::dd/div")
                max_reuses = safe_get("//dt[text()='Maximum number of reuses']/following-sibling::dd/div")
                sterilisation = safe_get("//dt[text()='Need for sterilisation before use']/following-sibling::dd/div")
                sterile = safe_get("//dt[text()='Device labelled as sterile']/following-sibling::dd/div")
                latex = safe_get("//dt[text()='Containing Latex']/following-sibling::dd/div")
                handling_conditions = safe_get("//dt[text()='Storage and handling conditions']/following-sibling::dd/div")
                warnings = safe_get("//dt[text()='Critical warnings or contra-indications']/following-sibling::dd/div")
                do_not_reuse = safe_get("//dt[text()='Critical warnings or contra-indications']/following-sibling::dd//li[text()='Do not re-use']")
                reprocessed = safe_get("//dt[contains(text(), 'Reprocessesed single use device')]/following-sibling::dd/div")
                intended_purpose = safe_get("//dt[contains(text(), 'Intended purpose other than medical')]/following-sibling::dd/div")
                market_member_state = safe_get("//dt[text()='Member state of the placing on the EU market of the device']/following-sibling::dd/div")
                med_product_2 = safe_get("//dt[text()='Presence of a substance which, if used separately, may be considered to be a medicinal product']/following-sibling::dd/div")
                version_4 = safe_get("(//ul[@id='versionStatus']/li/strong)[4]")
                last_update_4 = safe_get("(//ul[@id='versionStatus']/li[contains(text(), 'Last update date:')])[4]").replace("Last update date: ", "")
                available_member_state = safe_get("//dt[text()='Member State where the device is or is to be made available']/following-sibling::dd//ul")
                sscp_ref = safe_get("//dt[text()='SS(C)P Reference number']/following-sibling::dd/div")
                sscp_rev = safe_get("//dt[text()='SS(C)P revision number']/following-sibling::dd/div")
                issue_date = safe_get("//dt[text()='Issue date']/following-sibling::dd/div")

                # Certificate Numbers
                certificate_no_elements_1 = driver.find_elements(By.XPATH, "//h2[text()='Certificates']/following-sibling::div[1]//mat-expansion-panel-header")
                certificate_no_elements_2 = driver.find_elements(By.XPATH, "//h2[text()='Certificates']/following-sibling::div[1]//mat-expansion-panel/div/div/div")
                certificate_numbers = "  %  ".join([e.text for e in certificate_no_elements_1 + certificate_no_elements_2 if e.text]).strip()

                # Save to SQLite
                
                cursor.execute('''
                    INSERT INTO device_data (
                        udi_di, version, last_update_date, actor_name, actor_id, address,
                        country, telephone, email, version_2, last_update_date_2, legislation,
                        basic_udi, kit, system_procedure, authorised_rep, special_device_type,
                        risk_class, implantable, suture_device, measuring_function, reusable_instrument,
                        active_device, admin_device, companion_diagnostic, near_patient_testing,
                        patient_self_testing, professional_testing, reagent, instrument, device_model,
                        device_name, human_tissues, animal_tissues, microbial_origin, medicinal_product,
                        blood_product, version_3, last_update_date_3, udi_di_code, status, secondary_udi,
                        nomenclature_code, trade_name, catalogue_number, direct_marking, unit_of_use,
                        quantity, udi_pi, product_description, info_url, clinical_sizes, single_use,
                        max_reuses, sterilisation, sterile, latex, handling_conditions, warnings,
                        reprocessed, intended_purpose, market_member_state, med_product_2, version_4,
                        last_update_date_4, available_member_state, sscp_ref, sscp_rev, issue_date,
                        certificate_numbers
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    udi_di, version, last_update, actor_name, actor_id, address,
country, telephone, email, version_2, last_update_2, applicable_legislation,
basic_udi, kit, system_procedure, authorised_rep, special_device_type,
risk_class, implantable, suture_device, measuring_function, reusable_instrument,
active_device, admin_device, companion_diagnostic, near_patient_testing,
patient_self_testing, professional_testing, reagent, instrument, device_model,
device_name, presence_of_human_tissues, presence_of_animal_tissues, presence_of_microbial_origin,
presence_of_medicinal_product, presence_of_blood_product, version_3, last_update_3,
udi_di, status, secondary_udi, nomenclature_code, trade_name, catalogue_number,
direct_marking, unit_of_use, quantity, udi_pi, product_description, info_url,
clinical_sizes, single_use, max_reuses, sterilisation, sterile, latex,
handling_conditions, warnings, do_not_reuse, reprocessed, intended_purpose,
market_member_state, med_product_2, version_4, last_update_4,
available_member_state, sscp_ref, sscp_rev, issue_date, certificate_numbers

                ))

                conn.commit()
                

                print(f"Saved device: {udi_di}")

                driver.back()
                time.sleep(5)

            except Exception as e:
                print(f"Error on row {i + 1}: {e}")
                driver.back()
                time.sleep(5)

    except Exception as e:
        print(f"Error on page {page}: {e}")

driver.quit()
conn.close()
