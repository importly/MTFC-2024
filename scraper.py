from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
import math
import pandas as pd

def get_text(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    #https://storage.googleapis.com/chrome-for-testing-public/122.0.6261.94/win64/chromedriver-win64.zip go here for windows version
    chrome_service = ChromeService(executable_path='/Users/m296082/Downloads/chromedriver-mac-arm64/chromedriver')
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )

    full_text = driver.find_element(By.TAG_NAME, 'body').text
    driver.quit()
    return full_text

api_key = "AIzaSyCSHrAFKl82mhUCGXC9dQBkBSarJ9hUxyc"
console_id = "15a4ea5e446f84812"
queries = ["Is Climate Change Real?"]

end_year = 2024
start_year = 1954

year_range = end_year - start_year
incr = year_range // 10
#incr = 1 # when we have final prompt
searchpoint = end_year - incr

for query in queries:
    dataset = {
        "title": [],
        "link": [],
        "date": [],
        "date_range": [],
        "content": [],
        "snippet": []
    }
    while (searchpoint > start_year - incr):
        for i in range(1, 100, 10):
            print(i)
            res = requests.get(f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={console_id}&q={query}&start={i}&num=10&sort=date:r:{searchpoint}0000:{searchpoint+incr}0000").json()
            if "items" in res:
                for i, result in enumerate(res["items"]):
                    print(result["link"])
                    content = get_text(result["link"])
                    date = "NA"
                    try:
                        res = requests.head(result["link"])
                        date_data = res.headers.get("Last-Modified")
                        if date_data:
                            date = date_data
                        else:
                            meta = result["pagemap"]["metatags"][0]
                            res = [val for key, val in meta.items() if "date" in key]
                            if res:
                                date = res[0]
                    except:
                        pass
                    dataset["title"].append(result["title"])
                    dataset["link"].append(result["link"])
                    dataset["date"].append(date)
                    dataset["date_range"].append(f"{searchpoint}-{searchpoint+incr}")
                    dataset["content"].append(content)
                    dataset["snippet"].append(result["snippet"])

                datasetFile = pd.DataFrame(dataset)
                datasetFile.to_csv(f"{query}.csv")
        searchpoint -= incr

                                                  