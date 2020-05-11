from prometheus_client import Gauge, start_http_server
import requests
import json
import time

class Data:
    gauges = {
        "confirmed": Gauge("covid_tracker_confirmed_total", "confirmed cases", ["country", "province", "source"]),
        "deaths": Gauge("covid_tracker_deaths_total", "total deaths", ["country", "province", "source"]),
        "recovered": Gauge("covid_tracker_recovered_total", "total recovered", ["country", "province", "source"])
    }
    def pull(self):
        return requests.get(self.url)

class WorldometerWorldData (Data):
    def __init__(self, **kwargs):
        super(WorldometerWorldData, self).__init__(**kwargs)
        self.url = "https://disease.sh/v2/countries"

    def process(self):
        json = self.pull().json()
        for unit in json:
            self.gauges["deaths"].labels(country=unit["country"], province="all", source="worldometer").set(unit["deaths"])
            self.gauges["confirmed"].labels(country=unit["country"], province="all", source="worldometer").set(unit["cases"])
            self.gauges["recovered"].labels(country=unit["country"], province="all", source="worldometer").set(unit["recovered"])

class WorldometerUSData (Data):
    def __init__(self, **kwargs):
        super(WorldometerUSData, self).__init__(**kwargs)
        self.url = "https://disease.sh/v2/states"

    def process(self):
        json = self.pull().json()
        for unit in json:
            self.gauges["deaths"].labels(country="USA", province=unit["state"], source="worldometer").set(unit["deaths"])
            self.gauges["confirmed"].labels(country="USA", province=unit["state"], source="worldometer").set(unit["cases"])

class JHU (Data):
    def __init__(self, **kwargs):
        super(JHU,self).__init__(**kwargs)
        self.url = "https://disease.sh/v2/jhucsse"

    def process(self):
        json = self.pull().json()
        for unit in json:
            self.gauges["deaths"].labels(country=unit["country"], province=unit["province"], source="JHU").set(unit["stats"]["deaths"], )
            self.gauges["confirmed"].labels(source="JHU", country=unit["country"], province=unit["province"]).set(unit["stats"]["confirmed"])
            self.gauges["recovered"].labels(source="JHU", country=unit["country"], province=unit["province"]).set(unit["stats"]["recovered"])

def main():
    
    start_http_server(9002)
    jhu = JHU()
    w = WorldometerWorldData()
    gatherers = [JHU(), WorldometerWorldData(), WorldometerUSData()]
    while True:
        for g in gatherers:
            g.process()
        print("processed chunk")
        # this data only updates every 10 minutes, no point in spamming the API
        time.sleep(600)        

main()
