from scrapers.linkedin_scraper import fetch_and_save

def scrape_and_save_jobs(title_filter='"Stage Data Engineer"'):
    return fetch_and_save(title_filter=title_filter)
