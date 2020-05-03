from prometheus_client import Gauge, start_http_server
import requests
import json
import time

keys = {
    "covid_tracker_confirmed": "confirmed",
    "covid_tracker_deaths": "deaths",
    "covid_tracker_recovered": "recovered"
}

class Data:
    def pull(self):
        return requests.get(self.url)

class JHU (Data):
    def __init__(self, **kwargs):
        self.url = "https://disease.sh/v2/jhucsse"
        self.gauges = {
            "confirmed": Gauge("covid_tracker_confirmed_total", "confirmed cases", ["country", "province", "source"]),
            "deaths": Gauge("covid_tracker_deaths_total", "total deaths", ["country", "province", "source"]),
            "recovered": Gauge("covid_tracker_recovered_total", "total recovered", ["country", "province", "source"])
        }

    def process(self):
        json = self.pull().json()
        for unit in json:
            print(unit)
            self.gauges["deaths"].labels(country=unit["country"], province=unit["province"], source="JHU").set(unit["stats"]["deaths"], )
            self.gauges["confirmed"].labels(source="JHU", country=unit["country"], province=unit["province"]).set(unit["stats"]["confirmed"])
            self.gauges["recovered"].labels(source="JHU", country=unit["country"], province=unit["province"]).set(unit["stats"]["recovered"])

def main():
    
    start_http_server(8000)
    jhu = JHU()
    while True:
        jhu.process()
        print("processed chunk")
        # this data only updates every 10 minutes, no point in spamming the API
        time.sleep(600)        

main()
