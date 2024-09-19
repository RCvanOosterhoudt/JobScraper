from utils import configure_webdriver, search_jobs, scrape_job_data, clean_data, sort_data, save_csv_job


class Indeed:
    def __init__(self, country: str, position: str, location: str, distance: int, days: int):
        self._url = f'https://{country}.indeed.com/jobs?q={position}&l={location}&radius={distance}&fromage={days}'

        self._position = position
        self._location = location

        self._country_url = f'https://{country}.indeed.com'

        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                          'Version/17.6 Safari/605.1.15'}

        self._driver = configure_webdriver()

    def run(self):
        print(f"Search on Indeed for: {self._position}")

        full_url = search_jobs(driver=self._driver, url=self._url)
        df = scrape_job_data(driver=self._driver, country_url=self._country_url, url=self._url)

        cleaned_df = clean_data(df)
        sorted_df = sort_data(cleaned_df)
        # save_csv_job(sorted_df, job_position=self._position, job_location=self._location)

        return sorted_df
