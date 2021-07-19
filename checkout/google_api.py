import json
import requests
from djangoProject.settings import GOOGLE_MAPS_API_KEY, CATERING_PLACE_ID


class GoogleApi:
    """Calculating distance between catering and order destination"""
    @staticmethod
    def get_place_id(address, address_info) -> str:
        parameters = {"input": address + " " + address_info, "key": GOOGLE_MAPS_API_KEY}
        localization_api_call = requests.get("https://maps.googleapis.com/maps/api/place/autocomplete/json",
                                             params=parameters).text
        json_object = json.loads(localization_api_call)
        place_id = json_object["predictions"][0]["place_id"]
        return place_id

    @staticmethod
    def calculate_distance_between_order_and_catering(place_id) -> float:
        parameters = {"origin": f"place_id:{CATERING_PLACE_ID}", "destination": f"place_id:{place_id}",
                      "key": f"{GOOGLE_MAPS_API_KEY}"}
        distance_api_call = requests.get("https://maps.googleapis.com/maps/api/directions/json?",
                                         params=parameters).text
        json_object = json.loads(distance_api_call)
        distance = json_object['routes'][0]['legs'][0]['distance']['value']
        distance = int(distance) / 1000

        return distance
