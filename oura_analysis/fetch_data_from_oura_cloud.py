from pydantic_settings import BaseSettings
import requests
from pathlib import Path
import json


class OuraApiSettings(BaseSettings):
    oura_api_host: str = "api.ouraring.com"
    oura_api_personal_access_token: str = ""


api_settings = OuraApiSettings()


def get_nightly_HRV_and_HR_data(start_date: str, end_date: str):
    # Fetch data from oura cloud
    url = f"https://{api_settings.oura_api_host}/v2/usercollection/sleep"
    headers = {"Authorization": f"Bearer {api_settings.oura_api_personal_access_token}"}
    params = {
        "start_date": start_date,
        "end_date": end_date,
    }
    response = requests.request("GET", url, params=params, headers=headers)
    print(response)

    full_response = json.loads(response.content)

    # extract HRV and HR
    result_data = []
    for entry in full_response["data"]:
        result_data.append(
            {
                "date": entry["day"],
                "heart_rate": entry["heart_rate"],
                "hrv": entry["hrv"],
            }
        )

    result = {"query_params": params, "data": result_data}
    return result


def save_nightly_HRV_and_HR_data(sleep_data, save_folder: Path):
    # save to json
    start_date = sleep_data["query_params"]["start_date"]
    end_date = sleep_data["query_params"]["end_date"]

    save_filename = f"sleep_HRV_HR_{start_date}_{end_date}.json"
    save_path = save_folder / save_filename
    with save_path.open("w") as f:
        json.dump(sleep_data, f)
    print(f"Saved data to: {save_path.absolute()}")
    return None


def main():
    start_date = "2023-11-01"
    end_date = "2024-01-01"
    sleep_data = get_nightly_HRV_and_HR_data(start_date, end_date)

    save_folder = Path(__file__).parent.parent / "data"
    save_nightly_HRV_and_HR_data(sleep_data, save_folder)


if __name__ == "__main__":
    main()
