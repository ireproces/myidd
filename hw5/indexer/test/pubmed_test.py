from selenium import webdriver
from selenium.webdriver.common.by import By
url = "http://pmc.ncbi.nlm.nih.gov/articles/PMC5322482"


driver = webdriver.Chrome()  # Make sure you have the appropriate WebDriver installed
driver.implicitly_wait(5)  # Wait for the page to load
driver.get(url)
driver.find_element(By.TAG_NAME, "figure")  # Click on the figure with id "fig1"
print(driver.title)
print(driver.page_source[:50000])  # print the first 500 characters of the page source