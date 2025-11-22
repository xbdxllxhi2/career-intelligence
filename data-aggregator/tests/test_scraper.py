import unittest
import json
import os

import sys
import os

# Adding project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dags.scrapers.linkedin_scraper import compute_checksum, filter_new_jobs, save_jobs, load_existing_jobs


TEST_FILE = "./jobs.json"

class TestJobScraper(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

    def tearDown(self):
        if os.path.exists(TEST_FILE):
            os.remove(TEST_FILE)

    def test_compute_checksum(self):
        job = {"id": "1", "title": "Test Job"}
        checksum = compute_checksum(job)
        self.assertIsInstance(checksum, str)
        self.assertEqual(len(checksum), 64) 

    def test_filter_new_jobs(self):
        existing_job = {"id": "1", "title": "Existing"}
        existing_checksum = compute_checksum(existing_job)
        with open(TEST_FILE, "w", encoding="utf-8") as f:
            json.dump({existing_checksum: existing_job}, f)

        # this is to patch loader to use TEST_FILE
        def mock_load_existing_jobs(file_path=None):
            with open(TEST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

        # New jobs list
        jobs = [
            {"id": "1", "title": "Existing", "checksum": existing_checksum},  # should be filtered
            {"id": "2", "title": "New Job", "checksum": compute_checksum({"id": "2", "title": "New Job"})}
        ]

        filtered = {k: v for k, v in filter_new_jobs.__globals__.items() if k == 'load_existing_jobs'}
        # Temporarily patch
        filter_new_jobs.__globals__['load_existing_jobs'] = mock_load_existing_jobs
        result = filter_new_jobs(jobs)
        filter_new_jobs.__globals__['load_existing_jobs'] = filtered['load_existing_jobs']

        self.assertEqual(len(result), 1)
        self.assertIn(jobs[1]["checksum"], result)

    def test_save_jobs_merges(self):
        job1 = {"id": "1", "title": "Job1"}
        job2 = {"id": "2", "title": "Job2"}

        save_jobs({compute_checksum(job1): job1})
        save_jobs({compute_checksum(job2): job2})

        with open(TEST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(len(data), 2)
        self.assertIn(compute_checksum(job1), data)
        self.assertIn(compute_checksum(job2), data)


if __name__ == "__main__":
    unittest.main() 
