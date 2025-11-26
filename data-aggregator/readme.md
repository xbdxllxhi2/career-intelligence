# Internship Helper - Job Scraper

This project is a Python-based tool to fetch and manage internship and job postings from LinkedIn via the RapidAPI LinkedIn Job Search API. It computes checksums to avoid duplicates and stores the data locally in JSON format.  

## Features

- Fetch job postings with filters (title, location, description type).
- Avoid duplicate entries using SHA256 checksums.
- Merge new job postings into existing local JSON storage.
- Handle API rate limits with exponential backoff.
- Unit tests to validate scraping and data-saving logic.