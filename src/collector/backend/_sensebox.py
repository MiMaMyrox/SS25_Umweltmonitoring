import requests
import pandas as pd
from datetime import datetime, timedelta, date
from urllib.error import HTTPError

from backend._format_df import format_df

class SenseBox:
    def __init__(self, box_id: str):
        self.id = box_id
        self.archive_url = "https://archive.opensensemap.org"
        self.api_url = "https://api.opensensemap.org/boxes"
        
        self._load_box_info()

    def _load_box_info(self):
        url = f"{self.api_url}/{self.id}"
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Box {self.id} not found or API error.")
        
        data = response.json()

        self.name = data.get("name", "Unnamed_Box").replace(" ", "_")
        self.creation_date = self._parse_date(data.get("createdAt"))
        self.last_measurement = self._parse_date(data.get("lastMeasurementAt"))

        self.sensors = {
            sensor["title"]: sensor["_id"]
            for sensor in data.get("sensors", [])
        }

    def _parse_date(self, iso_string: str) -> datetime.date:
        if iso_string:
            return datetime.fromisoformat(iso_string[:10]).date()
        return None

    def __repr__(self):
        return f"<SenseBox {self.name} ({self.id}) – {len(self.sensors)} Sensoren>"


    def fetch_archive(self, from_date=None, to_date=None) -> pd.DataFrame:

        if from_date is None:
            from_date= self.creation_date

        if to_date is None:
            to_date = self.last_measurement

        if isinstance(from_date, str):
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()

        if isinstance(to_date, str):
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()

        # Create range (inclusive of end date)
        date_range = [(from_date + timedelta(days=i)).isoformat()
                    for i in range((to_date - from_date).days + 1)]
        
        data = pd.DataFrame()
        count = 1
        for request_date in date_range:
            url = ""
            try:
                day_data = None
                for metric, sensor_id in self.sensors.items():
                    url = f"{self.archive_url}/{request_date}/{self.id}-{self.name}/{sensor_id}-{request_date}.csv"
                    sensor_data = pd.read_csv(url).rename(columns={"value":metric})
                    if day_data is None:
                        day_data = sensor_data
                    else:
                        day_data = day_data.merge(sensor_data, on="createdAt", how="outer")
                data = pd.concat([data,day_data])
                # if len(data) >= 10_000 * count:
                #     print(f"{request_date} - Current Length: {len(data)}")
                #     count += 1
                # print(f"{request_date} - Current Length: {len(data)}")

            except HTTPError as e:
                if e.code == 404:
                    # print(f"Failed at {request_date} with {e}, link: {url}")
                    pass
                else:
                    print(e)
                    break


        if data.empty:
            print("Empty DataFrame")
            raise ValueError("DataFrame is empty")
        # Convert index to datetime if needed
        return format_df(data)

    def fetch_buffer(self):
        data = None
        for metric, sensor_id in self.sensors.items():
            url = f"{self.api_url}/{self.id}/data/{sensor_id}"

            response = requests.get(url).json()
            sensor_data = pd.DataFrame(response).drop(columns=["location"]).rename(columns={"value":metric})

            if data is None:
                data = sensor_data
            else:
                data = data.merge(sensor_data, on="createdAt", how="outer")

        return format_df(data)

    def fetch_last_measurement(self):
        response = requests.get(f"https://api.opensensemap.org/boxes/{self.id}/sensors").json()

        new_entry = {"createdAt":pd.to_datetime(response["sensors"][0]["lastMeasurement"]["createdAt"])}

        for entry in response["sensors"]:
            new_entry[entry["title"]] = entry["lastMeasurement"]["value"]
        data = pd.DataFrame([new_entry])
        return format_df(data)