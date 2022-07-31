from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from csv import writer
from selenium.webdriver.chrome.options import Options
import logging, json, os, sys, time, random
from scrapy.selector import Selector
from seleniumwire import webdriver
import pandas as pd
from selenium.webdriver.chrome.service import Service
from urllib.parse import quote
import datetime
import pandas as pd
import requests, json

DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"
options = Options()
# options.add_argument("--headless")
# options.add_argument("--disable-gpu")
# options.add_argument("--disable-logging")
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option("useAutomationExtension", False)
# options.add_experimental_option("excludeSwitches", ["enable-logging"])


def click(element, driver):
    """Use javascript click if selenium click method fails"""
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)


def map_search(query):
    print(f">>> Searching Google Maps for {query}...")
    query_encoded = "+".join(query.split())

    driver.get(f"https://www.google.com/maps/search/{query_encoded}")
    search_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@id="searchbox-searchbutton"]'))
    )
    click(search_button, driver)


def get_api_urls(driver):
    # scroll till the end (no new response recieved in backend)
    time_limit = 3600  # in seconds
    time_counter = 0

    print("Scrolling...")
    while time_counter < time_limit:
        try:
            driver.execute_script(
                """
            b = document.querySelector("div[role='feed']")
            b.scrollBy(0,b.scrollHeight)
            """
            )
        except Exception as e:
            print(e)

        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(),'reached the end of the list.')]")
                )
            )
            break
        except:
            continue

    # filter backend responses
    api_urls = set()
    for backend_response in driver.requests:
        if "search?" in backend_response.url:
            backend_api_url = backend_response.url
            api_urls.add(backend_api_url)
    print(len(api_urls))
    return api_urls


def parse_apis(api_urls):
    write_headers = not os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, "a") as csvfile:

        csv_writer = writer(csvfile)
        if write_headers:
            csv_writer.writerow(
                (
                    "store_name",
                    "tag",
                    "location",
                    "website",
                    "num_reviews",
                    "average_reviews",
                    "features",
                    "region",
                    "phone_number",
                    "price_range",
                )
            )
        for i, url in enumerate(api_urls):
            print(f"Parsing page {i}")
            api_response = requests.get(url)

            # clean api_response
            try:
                response_text = api_response.text[:-6]
                response_dict = json.loads(response_text)
            except:
                response_text = api_response.text[:-6]
                response_dict = json.loads(response_text)

            search_response = response_dict.get("d", "" * 6)[5:]
            search_json = json.loads(search_response)

            cleaned_api = search_json[0][1]

            # extract data from cleaned api
            extracted_data = extract_data(cleaned_api)

            csv_writer.writerows(extracted_data)


def extract_data(cleaned_api):
    extracted_data = []

    for i, data in enumerate(cleaned_api):

        if i == 0:
            continue
        try:
            store_name = data[14][11]
            tags_list = data[14][32]
            location_list = data[14][2]
            location = ", ".join(location_list) if location_list else None

            website = data[14][7][1] if data[14][7] else None
            num_reviews = data[14][4][3][1] if data[14][4] else None
            average_reviews = data[14][4][7] if data[14][4] else None
            features_list = data[14][13]

            features = ", ".join(features_list) if features_list else None

            region = data[14][14]
            tags = []
            if tags_list:
                for tag in tags_list:
                    if tag[1]:
                        tags.append(tag[1])

                tag = ", ".join(tags)
            else:
                tag = None

            phone_number = data[14][178][0][0] if data[14][178] else None

            try:

                price_range = data[14][4][10]
            except:
                price_range = None
            extracted_data.append(
                (
                    store_name,
                    tag,
                    location,
                    website,
                    num_reviews,
                    average_reviews,
                    features,
                    region,
                    phone_number,
                    price_range,
                )
            )
        except Exception as e:
            print(e)
            continue
    return extracted_data


if __name__ == "__main__":
    argument = sys.argv

    # query = argument[1]
    # OUTPUT_FILE = argument[2]
    query = "restaurants in florida"
    OUTPUT_FILE = "file.csv"

    service = Service(DRIVER_EXECUTABLE_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    map_search(query)
    # get_api_urls(driver)
    api_urls = get_api_urls(driver)
    parse_apis(api_urls)
