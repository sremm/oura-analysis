import json
import os

from loguru import logger

from oura_analysis.oura_api import OuraApi
from oura_analysis.settings import DATA_FOLDER

# If python-dotenv is installed, prefer loading a local .env file automatically.
# This is optional and non-fatal: if dotenv isn't installed the loader is skipped.
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # dotenv not installed or failed to load; proceed using environment as-is
    pass

# Your OAuth2 application credentials
CLIENT_ID = os.getenv("OURA_CLIENT_ID", "YOUR_CLIENT_ID")
CLIENT_SECRET = os.getenv("OURA_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
REDIRECT_URI = os.getenv("OURA_REDIRECT_URI", "YOUR_REDIRECT_URI")


def main():
    # Step 3: Use the access token to make API calls
    logger.info("Starting Oura API authentication flow")
    scope = "daily heartrate personal sleep activity tag User"
    oura_api = OuraApi(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope)
    oura_api.start_auth_flow()

    start_date = "2020-05-01"  # first known coffee tag 2020-05-02
    end_date = "2026-01-01"
    logger.info("Getting sleep data")
    sleep_data = oura_api.get_sleep_data(start_date, end_date)
    with open(DATA_FOLDER / f"sleep_data_{start_date}_{end_date}.json", "w") as f:
        json.dump(sleep_data["data"], f, indent=2)

    # Get sleep score data
    sleep_score_data = oura_api.get_sleep_score_data(start_date, end_date)
    with open(DATA_FOLDER / f"sleep_score_data_{start_date}_{end_date}.json", "w") as f:
        json.dump(sleep_score_data["data"], f, indent=2)

    logger.info("Getting tags data")
    tags_data = oura_api.get_tags_data(start_date, end_date)
    with open(DATA_FOLDER / f"tags_data_{start_date}_{end_date}.json", "w") as f:
        json.dump(tags_data["data"], f, indent=2)


if __name__ == "__main__":
    main()
