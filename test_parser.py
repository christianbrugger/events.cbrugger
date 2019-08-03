from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

options = Options()
options.add_argument("--disable-notifications");
options.add_argument("--headless")  
options.add_argument("--disable-gpu");
options.add_argument('--no-sandbox')
options.add_experimental_option('prefs', {
    'credentials_enable_service': False,
    'profile': {
        'password_manager_enabled': False
    }
})

driver = webdriver.Chrome(options=options)

driver.get("http://www.facebook.org")

print("RESULT")
print(driver.find_element_by_class_name("_58mv").text)

driver.close()
print("DONE")

