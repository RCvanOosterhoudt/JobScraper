import ipdb
from bs4 import BeautifulSoup
import os
import pandas as pd

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService

from webdriver_manager.chrome import ChromeDriverManager


def configure_webdriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    return driver


def search_jobs(driver, url: str):
    driver.get(url)
    global total_jobs
    try:
        job_count_element = driver.find_element(By.XPATH,
                                                '//div[starts-with(@class, "jobsearch-JobCountAndSortPane-jobCount")]')
        total_jobs = job_count_element.find_element(By.XPATH, './span').text
        print(f"{total_jobs} found")
    except NoSuchElementException:
        print("No job count found")
        total_jobs = "Unknown"

    driver.save_screenshot('screenshot.png')
    return url


def scrape_job_data(driver, country_url: str, url: str):
    df = pd.DataFrame(columns=['Link', 'Job Title', 'Company', 'Date Posted', 'Location'])

    total_job_count = 0
    while True:
        soup = BeautifulSoup(driver.page_source, 'lxml')
        boxes = soup.find_all('div', class_="job_seen_beacon")

        job_count = 0
        for i in boxes:
            # --- Get full link to page
            link = i.find('a').get('href')
            link_full = country_url + link

            # --- Get the job title
            job_title = i.find('a', class_='jcs-JobTitle css-jspxzf eu4oa1w0').text

            # --- Get the company
            company_tag = i.find('span', {'data-testid': 'company-name'})
            company = company_tag.text if company_tag else None

            # --- Get posted date
            try:
                date_posted = i.find('span', class_='date').text
            except AttributeError:
                try:
                    date_posted = i.find('span', {'data-testid': 'myJobsStateDate'}).text.strip()
                except:
                    date_posted = "UNKNOWN (Needs to be fixed)"

            # --- Get location
            location_element = i.find('div', {'data-testid': 'text-location'})
            location = ''
            if location_element:
                # Check if the element contains a span
                span_element = location_element.find('span')

                if span_element:
                    location = span_element.text
                else:
                    location = location_element.text

            new_data = pd.DataFrame({'Link': [link_full],
                                     'Job Title': [job_title],
                                     'Company': [company],
                                     'Date Posted': [date_posted],
                                     'Location': [location]})

            df = pd.concat([df, new_data], ignore_index=True)
            job_count += 1

        total_job_count += job_count

        try:
            next_page = soup.find('a', {'aria-label': 'Next Page'}).get('href')

            next_page = country_url + next_page
            driver.get(next_page)

        except:
            break

    driver.close()

    return df


def clean_data(df: pd.DataFrame):
    def posted(x):
        x = x.replace('PostedPosted', '').strip()
        x = x.replace('EmployerActive', '').strip()
        x = x.replace('PostedToday', '0').strip()
        x = x.replace('PostedJust posted', '0').strip()
        x = x.replace('today', '0').strip()

        return x

    def day(x):
        x = x.replace('days ago', '').strip()
        x = x.replace('day ago', '').strip()
        return x

    def plus(x):
        x = x.replace('+', '').strip()
        return x

    df['Date Posted'] = df['Date Posted'].apply(posted)
    df['Date Posted'] = df['Date Posted'].apply(day)
    df['Date Posted'] = df['Date Posted'].apply(plus)

    return df


def sort_data(df):
    def convert_to_integer(x):
        try:
            return int(x)
        except ValueError:
            return float('inf')

    df['Date_num'] = df['Date Posted'].apply(lambda x: x[:2].strip())
    df['Date_num2'] = df['Date_num'].apply(convert_to_integer)
    df.sort_values(by=['Date_num2'], inplace=True)

    df = df[['Job Title', 'Company', 'Date Posted', 'Location', 'Link']]
    return df


def save_csv_job(df: pd.DataFrame, job_position: str, job_location: str, date=None):
    def get_user_desktop_path():
        home_dir = os.path.expanduser("~")
        desktop_path = os.path.join(home_dir, "Desktop")
        return desktop_path

    if date is not None:
        file_path = os.path.join(get_user_desktop_path(), '{}_{}_{}'.format(date, job_position, job_location))
    else:
        file_path = os.path.join(get_user_desktop_path(), '{}_{}'.format(job_position, job_location))

    # csv_file = '{}.csv'.format(file_path)
    df.to_csv('{}.csv'.format(file_path), index=False)


def save_csv_site(df: pd.DataFrame, job_site: str, job_location: str, date=None):
    def get_user_desktop_path():
        home_dir = os.path.expanduser("~")
        desktop_path = os.path.join(home_dir, "Desktop")
        return desktop_path

    if date is not None:
        file_path = os.path.join(get_user_desktop_path(), '{}_{}_{}'.format(date, job_site, job_location))
    else:
        file_path = os.path.join(get_user_desktop_path(), '{}_{}'.format(job_site, job_location))

    # csv_file = '{}.csv'.format(file_path)
    df.to_csv('{}.csv'.format(file_path), index=False)
