#!/usr/bin/env python
# coding: utf-8

# In[16]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time


# In[20]:


driver = webdriver.Chrome()
driver.get("https://ttc.lacounty.gov/request-duplicate-bill/")

# Setup wait for later
wait = WebDriverWait(driver, 10)

# Check we don't have other windows open already
assert len(driver.window_handles) == 1;

# Insert AIN and get results
elem = driver.find_element(By.ID, "ain")
elem.clear()
elem.send_keys("4327027001")

driver.save_screenshot("screenshot1.png")

elem.send_keys(Keys.RETURN)


# switch to new tab with results
wait.until(EC.number_of_windows_to_be(2));
driver.switch_to.window(driver.window_handles[1])
    
driver.save_screenshot("screenshot2.png") 

# click on pdf tax bill
driver.find_element(By.PARTIAL_LINK_TEXT, '(Click').click()

# switch to tab with tax bill open
wait.until(EC.number_of_windows_to_be(3));
driver.switch_to.window(driver.window_handles[2])

time.sleep(5)
driver.save_screenshot("screenshot3.png")

