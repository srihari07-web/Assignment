import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from langdetect import detect
import pandas as pd
import csv

driver = webdriver.Firefox(executable_path=r'C:\\Users\\S SRIHARI\\firefox\\geckodriver.exe')
driver.get('https://www.poshantracker.in/')
time.sleep(5)


parent_elements_1 = driver.find_elements(By.CSS_SELECTOR, ".selected-lang")
parent_elements = driver.find_elements(By.CSS_SELECTOR, ".language-dropdown")

buttons = parent_elements[0].find_elements(By.XPATH, ".//*")

dictionaries = {}

for button in buttons:
    parent_elements_1[0].click()
    button.click()
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    interactive_sect_desc = soup.find_all("div", class_="interactive_sect_right_desc")
    for desc in interactive_sect_desc:
        desc.decompose()

    div_to_ignore = soup.find("div", class_="language-dropdown")
    new_in_poshan_tracker = soup.find("div", class_="inter_sect_content")
    if new_in_poshan_tracker:
        new_in_poshan_tracker.extract()
    if div_to_ignore:
        div_to_ignore.extract()

    def is_script_or_style(tag):
        return tag.name == "script" or tag.name == "style"

    texts = [re.sub(r'\s+', ' ', element.get_text(strip=True)) for element in soup.find_all(string=True, recursive=True) if not is_script_or_style(element.parent)]

    dictionaries[button.get_attribute("innerHTML")] = texts

driver.quit()


common_words = set(dictionaries[list(dictionaries.keys())[0]])
for dictionary in dictionaries.values():
    common_words = common_words.intersection(set(dictionary))


filtered_data = {}
for language, words in dictionaries.items():
    filtered_words = list(set(words) - common_words)
    filtered_data[language] = [word for word in filtered_words if not any(string in word for string in ["copyright@2023 Poshan Tracker.","ABHA",
                                                                                                      "All rights reserved",
                                                                                                      "https://play.google.com/store/apps/details?id=com.poshantracker"])]



file_name = 'filtered.csv'
with open(file_name, 'w', encoding='utf-8', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Language', 'Filtered Words'])  
    for language, words in filtered_data.items():
        writer.writerow([language, ', '.join(words)])  



for language, words in filtered_data.items():
    file_name = f'{language}_filtered_data.csv'  
    with open(file_name, 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Language', 'Filtered Words'])  
        writer.writerow([language, ', '.join(words)])  


