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
from multiprocessing import Pool
import requests, json


RUN_ERROR = False
POOL_SIZE = 8
TIME_LIMIT = 30  # maximum scroll time in seconds
OUTPUT_FILE = "google_maps.csv"
ERROR_FILE = "googlemaps_error.csv"

DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"
service = Service(DRIVER_EXECUTABLE_PATH)

# headless mode setting
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--disable-logging")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-logging"])


def click(element, driver):
    """Use javascript click if selenium click method fails"""
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)


def clean(string):
    if string == None:
        return string
    string = str(string)
    string = string.replace("\r", "").replace("\\r", "")
    string = string.replace("\n", "").replace("\\n", "")
    string = string.replace("*", "")
    string = string.replace("?", "")
    string = string.replace("#", "")
    string = string.encode("ascii", "ignore").decode("ascii")
    return string


def map_search(query, driver):
    print(f">>> Searching Google Maps for {query}...")
    query_encoded = "+".join(query.split())

    driver.get(f"https://www.google.com/maps/search/{query_encoded}")
    search_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@id="searchbox-searchbutton"]'))
    )
    del driver.requests
    click(search_button, driver)
    time.sleep(5)


def get_api_urls(driver):
    # scroll till the end (no new response recieved in backend)
    time_counter = 0

    api_urls = set()

    print("Scrolling...")
    while time_counter < TIME_LIMIT:
        try:
            driver.execute_script(
                """
            b = document.querySelector("div[role='feed']")
            b.scrollBy(0,b.scrollHeight)
            """
            )
        except Exception as e:
            break

        try:
            WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(),'reached the end of the list.')]")
                )
            )
            # making sure the api is caught
            for backend_response in driver.requests:
                if "search?" in backend_response.url:
                    backend_api_url = backend_response.url
                    api_urls.add(backend_api_url)

            if api_urls:
                break
            else:
                driver.refresh()
                time_counter += 2
                continue

        except:
            time_counter += 2
            continue

    # get all and necessary backend responses
    for backend_response in driver.requests:
        if "search?" in backend_response.url:
            backend_api_url = backend_response.url
            api_urls.add(backend_api_url)

    return api_urls


def parse_apis(api_urls, search_query):
    write_headers = not os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, "a") as csvfile:

        csv_writer = writer(csvfile)
        if write_headers:
            csv_writer.writerow(
                (
                    "store_name",
                    "tag",
                    "postal_code",
                    "country",
                    "location",
                    "website",
                    "num_reviews",
                    "average_reviews",
                    "features",
                    "region",
                    "phone_number",
                    "price_range",
                    "Search Query",
                    "API URL",
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
            extracted_data = extract_data(cleaned_api, url, search_query)

            csv_writer.writerows(extracted_data)


def extract_data(cleaned_api, api_url, search_query):
    extracted_data = []

    for i, data in enumerate(cleaned_api):
        try:
            store_name = clean(data[14][11])
            tags_list = data[14][32]
            location_list = data[14][2]
            postal_list = location_list[-2].split()

            country = location_list[-1]
            if country and country.lower().strip() != "united kingdom":
                postal_code = postal_list[-1]
            elif len(postal_list) > 1:
                postal_code = " ".join(postal_list[-2:])
            else:
                postal_code = None

            location = clean(", ".join(location_list) if location_list else None)

            website = clean(data[14][7][0] if data[14][7] else None)
            if website:
                website = website.replace("/urlq=", "").strip()
            num_reviews = clean(data[14][4][3][1] if data[14][4] else None)
            average_reviews = clean(data[14][4][7] if data[14][4] else None)
            features_list = data[14][13]

            features = clean(", ".join(features_list) if features_list else None)

            region = clean(data[14][14])
            tags = []
            if tags_list:
                for tag in tags_list:
                    if tag[1]:
                        tags.append(tag[1])

                tag = clean(", ".join(tags))
            else:
                tag = None

            phone_number = clean(data[14][178][0][0] if data[14][178] else None)

            try:

                price_range = data[14][4][10]
            except:
                price_range = None
            extracted_data.append(
                (
                    store_name,
                    tag,
                    postal_code,
                    country,
                    location,
                    website,
                    num_reviews,
                    average_reviews,
                    features,
                    region,
                    phone_number,
                    price_range,
                    search_query,
                    api_url,
                )
            )
        except:
            continue
    return extracted_data


def scrape_googlemaps(query):
    try:

        driver = webdriver.Chrome(service=service, options=options)
        map_search(query, driver)
        api_urls = get_api_urls(driver)
        parse_apis(api_urls, query)
        driver.quit()
    except:
        with open(ERROR_FILE, "a") as error_file:
            error_file.write(query)
            error_file.write("\n")


if __name__ == "__main__":
    argument = sys.argv

    if len(argument) > 1:
        query = argument[1]
        OUTPUT_FILE = argument[2]
        scrape_googlemaps(query)
    else:
        if RUN_ERROR and os.path.exists(ERROR_FILE):
            with open(ERROR_FILE, "r") as query_file:
                queries = list(set(query_file.read().split("\n")))
        else:
            # getting queries
            queries_df = pd.read_csv("query.csv")
            queries = list(queries_df["query"].unique())

        # creating concurrent pool batches
        scraping_batches = list()
        for i in range(0, len(queries), POOL_SIZE):
            scraping_batches.append(queries[i : i + POOL_SIZE])

        # looping over batches of urls to add them to multiprocessing pools
        for batch_num, batch in enumerate(scraping_batches):
            print(
                f"<<<<< Running Concurrent Batch {batch_num}/{len(scraping_batches)} >>>>>"
            )
            p = Pool(len(batch))
            try:
                p.map(scrape_googlemaps, batch)
            except Exception as e:
                print(f"ERROR: {e}")
                p.map(scrape_googlemaps, batch)
            p.terminate()
            p.join()
