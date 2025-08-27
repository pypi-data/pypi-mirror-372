# --------------- Imports ---------------

import unittest
import subprocess
import os
import sys
import time
import pickle

from src.macho.main import Cache
from src.macho.dashboard import JSON_DATA_PATH

# --------------- Test Streamlit Dashboard ---------------

class TestDashboard(unittest.TestCase):

    def setUp(self):
        self.test_cache = Cache(
            max_cache_size=50,
            ttl=100.0,
            shard_count=2,
            strategy="lru",
            bloom=False
        )

        with open(JSON_DATA_PATH, "wb") as f:
            pickle.dump(self.test_cache, f)

    def test_dashboard_launch(self):
        abs_path = os.path.abspath(__file__)
        script_dir = os.path.dirname(abs_path)
        dashboard_main_path = os.path.join(script_dir, "..", "src", "cache", "dashboard", "dashboard.py")

        assert os.path.exists(dashboard_main_path), f"Dashboard path does not exist {dashboard_main_path}"

        launch_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", dashboard_main_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            time.sleep(5)
            self.assertIsNone(launch_process.poll(), "Streamlit Dashboard terminated early")
        finally:
            launch_process.terminate()
            launch_process.wait()

    def tearDown(self):
        if os.path.exists(JSON_DATA_PATH):
            os.remove(JSON_DATA_PATH)
