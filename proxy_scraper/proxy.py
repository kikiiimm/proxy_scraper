from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://geonode.com/free-proxy-list?fbclid=IwAR2GLARwzPDmGU_sJVcLHEpFAu7O6ocBrt0RLDhqK8V_7e7n5gspFtHlhSE')

accept_cookies_button = WebDriverWait(driver, 50).until(
    EC.element_to_be_clickable((By.XPATH, '//button[@data-cookiefirst-action="accept"]'))
)
accept_cookies_button.click()

# driver.implicitly_wait(50)

# fast_button = WebDriverWait(driver, 150).until(
#     EC.element_to_be_clickable((By.XPATH, '//button[contains(@type, "button")]/span[@data-state="checked"]'))
# )
# fast_button.click()

ip_address = []
port  = []
country = []
anonymity = []
speed = []

max_retries = 60
retry_count = 0

while retry_count < max_retries:

    try:
        rows = driver.find_elements(By.XPATH, "//tbody//tr")
        prev_state = (len(ip_address), len(port), len(country), len(anonymity), len(speed))


        for row in rows:
            ip_address.append(row.find_element(By.XPATH, ".//td[1]").text)
            port.append(row.find_element(By.XPATH, ".//td[2]").text)
            country.append(row.find_element(By.XPATH, ".//td[3]").text)
            anonymity.append(row.find_element(By.XPATH, ".//td[5]").text)
            speed.append(row.find_element(By.XPATH, ".//td[7]").text)

        next_page_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, '/html/body/main/div/div/div[2]/div[3]/div[2]/nav/div[2]/button[2]'))
        )

        ActionChains(driver).move_to_element(next_page_button).perform()

        driver.execute_script("arguments[0].click();", next_page_button)

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//tbody//tr"))
        )

        new_state = (len(ip_address), len(port), len(country), len(anonymity), len(speed))
        if new_state == prev_state:
            print("No new data loaded. Exiting loop.")
            break

        retry_count += 1

        time.sleep(1)
       
    except StaleElementReferenceException:
        print("Stale element encountered. Retrying for the current page...")
        retry_count += 1

    except NoSuchElementException:
        print("No more pages left.")
        break  

    except Exception as e:
        print("An error occurred:", e)
        break   

max_length = max(len(ip_address), len(port), len(country), len(anonymity), len(speed))

ip_address += [''] * (max_length - len(ip_address))
port += [''] * (max_length - len(port))
country += [''] * (max_length - len(country))
anonymity += [''] * (max_length - len(anonymity))
speed += [''] * (max_length - len(speed))

df = pd.DataFrame({'IP Address': ip_address, 
                   'Port': port, 
                   'Country': country, 
                   'Anonymity': anonymity, 
                   'Speed': speed})

df.to_csv('data.csv', index=False)

driver.quit()
