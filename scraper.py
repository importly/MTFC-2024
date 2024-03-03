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
import os

from dotenv import load_dotenv
load_dotenv()

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_service = ChromeService(executable_path='/home/prithish/MTFC/MTFC-2024/chromedriver')
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

def get_text(url):
    try:
        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        full_text = driver.find_element(By.TAG_NAME, 'body').text
    except:
        full_text = ""
    return full_text

api_key = os.getenv("API_KEY")
console_id = os.getenv("CONSOLE_ID")

queries = [ 
    #"How should the United States treat Russia?",
    #"How effective was the War on Drugs?",
    #"How should border security be enforced?",
    #"Support for healthcare reform.",
    #"Is climate change important?",
    #"Should the United States keep funding NASA?",
    #"Should there be more free trade agreements?",
    "US foreign policy in the Middle East",
    "racial equality government policies",
    "gender equality governemnt policies",
    "Is nuclear power safe?",
    "What are the views on Hydroelectric Power?",
    "What are the views on social media, interconnectivity, and globalization?"
]

incr = 3
max_year = 2024
min_year = 1974
init_month = 2
month_incr = incr % 12
year_incr = incr // 12

#print("hello")
for query in queries:
    upper_month = init_month
    upper_year = max_year
    lower_year = upper_year - year_incr
    noData = 0
    directory = os.fsencode("/home/prithish/MTFC/MTFC-2024")
    files = os.listdir(directory)
    #if any(query in file.replace(" ", "_") for file in files)
    #    continue
    for file in files:
        filename = os.fsdecode(file)
        print(filename)
        if filename.endswith(".py") or filename.endswith(".csv") or filename == ".git" or filename == ".env" or filename == ".gitignore" or filename == "chromedriver": 
            continue
        else:
            print(f"/home/prithish/MTFC/MTFC-2024/{filename}")
            os.remove(f"/home/prithish/MTFC/MTFC-2024/{filename}")
    
    dataset = {
        "title": [],
        "link": [],
        #"determined_date": [],
        "date_range": [],
        "content": [],
        "snippet": []
    }
    while (upper_year >= min_year):
        if noData > 10:
            break
        lower_month = upper_month - month_incr
        if lower_month < 0:
            lower_month += 12
            lower_year -= 1
        print(f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={console_id}&q={query}&start={1}&num=10&sort=date:r:{lower_year}{'{:02d}'.format(lower_month)}00:{upper_year}{'{:02d}'.format(upper_month)}00")
        res = requests.get(f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={console_id}&q={query}&start={1}&num=10&sort=date:r:{lower_year}{'{:02d}'.format(lower_month)}00:{upper_year}{'{:02d}'.format(upper_month)}00").json()
        upper_year = lower_year
        lower_year -= year_incr
        upper_month = lower_month
        if "items" in res:
            noData = 0
            print(len(res["items"]))
            for i, result in enumerate(res["items"]):
                print(result["link"])
                content = get_text(result["link"])
                if content == "":
                    continue
                #date = "NA"
                #try:
                #    res = requests.head(result["link"])
                #    date_data = res.headers.get("Last-Modified")
                #    if date_data:
                #        date = date_data
                #    else:
                #        meta = result["pagemap"]["metatags"][0]
                #        res = [val for key, val in meta.items() if "date" in key]
                #        if res:
                #            date = res[0]
                #except:
                    #pass
                dataset["title"].append(result["title"])
                dataset["link"].append(result["link"])
                #dataset["determined_date"].append(date)
                dataset["date_range"].append(f"{lower_year}{lower_month}-{upper_year}{upper_month}")
                dataset["content"].append(content)
                dataset["snippet"].append(result["snippet"])
        else:
            noData += 1

        datasetFile = pd.DataFrame(dataset)
        datasetFile.to_csv(f"{query.replace(' ', '_')}{min_year}-{max_year}by{incr}months.csv")                                  
