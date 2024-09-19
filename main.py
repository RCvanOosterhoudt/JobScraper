import datetime
from indeed import Indeed
import pandas as pd
from utils import save_csv_site


class JobScraper:
    def __init__(self, country: str, position: str, location: str, distance: int, days: int):
        self.js = Indeed(country=country, position=position, location=location, distance=distance, days=days)

    def __call__(self):
        return self.js.run()


df = pd.DataFrame({'Job Title': [''], 'Company': [''], 'Date Posted': [''], 'Location': [''], 'Link': ['']})
for index, job_title in pd.read_csv('interesting_job_titles.csv', header=None).iterrows():
    js = JobScraper("NL", job_title.item(), "Rotterdam", 50, 7)
    df_position = js()

    if df_position.shape[0] != 0:
        df = pd.concat([df, df_position])

current_date = datetime.datetime.now().strftime("%Y_%m_%d")

# df = df.drop_duplicates(subset=['Job Title'])
df = df.drop_duplicates(subset=['Job Title', 'Company'])
save_csv_site(df, "Indeed", "Rotterdam", current_date)
