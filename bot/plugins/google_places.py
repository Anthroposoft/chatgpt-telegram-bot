import logging
import pprint
from typing import Dict
import os
import requests

from .plugin import Plugin


class GooglePlacesTextSearchPlugin(Plugin):
    """

    GooglePlacesTextSearchPlugin

    This class is a plugin for querying detailed information about places and locations
    using the Google Places Text Search API.

    Attributes:
        api_key (str): The API key for accessing the Google Places API.

    Methods:
        __init__(): Initializes the GooglePlacesTextSearchPlugin instance.
        get_source_name(): Returns the name of the data source as a string.
        get_spec(): Returns the specification for the plugin in the form of a list of dictionaries.
        execute(function_name, helper, **kwargs): Executes the plugin function based on the provided parameters.

    """

    def __init__(self):
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.region_code = os.getenv('GOOGLE_MAPS_API_REGION_CODE', default="us")
        if not api_key:
            raise ValueError(
                'GOOGLE_MAPS_API_KEY environment variable must be set to use GooglePlacesTextSearch Plugin')
        self.api_key = api_key

    def get_source_name(self) -> str:
        return "GooglePlacesTextSearch"

    def get_spec(self) -> [Dict]:
        return [
            {
                "name": "get_google_places_via_text_search",
                "description": "Get detailed information about places and locations that are searched using "
                               "the Google Places Text Search API. The user may ask about restaurants, "
                               "shops, shopping malls, healthcare services, local companies,"
                               "medical care center, sight seeing, administration center, etc. at a "
                               "specific place or location or nearby his specific location."
                               "\n"
                               "For example:\n"
                               "I am at Berlin Alexanderplatz, what are the 5 best restaurants around?\n"
                               "Restaurants near Bakerstreet London?\n"
                               "Nearest hospital to Baker street ind London?\n"
                               "I need a shoemaker. I am at Bakerstreet London?\n"
                               "What are the opening times of restaurant Beekeeper in London?\n",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": f"""
                                The question about a location of the user. 
                                If the user question does not contain his location, ask for the
                                location and use this location to formulate the correct question for
                                the Google Places Text Search API. Or use the context of previous 
                                message to determine the location of the user.
                                """,
                        },
                        "result_count": {
                            "type": "integer",
                            "description": "The number of results that should be returned from the Google Places Text Search API."
                                           " By default this should be set to 5. If the user says 'give me the 3 best restaurants',"
                                           "then the this umber should be 3. If the user says give me the best restaurant or hotel, "
                                           "then this number should be 1."
                        },
                    },
                    "required": ["question"],
                },
            }
        ]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        logging.info(kwargs)

        result_count = 5
        if "result_count" in kwargs:
            result_count = kwargs["result_count"]

        field_mask = ('places.displayName,places.formattedAddress,places.priceLevel,places.rating,'
                      'places.googleMapsUri,places.websiteUri,places.regularOpeningHours')

        url = 'https://places.googleapis.com/v1/places:searchText'
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': field_mask
        }
        data = {
            'textQuery': kwargs["question"],
            'maxResultCount': result_count,
            'regionCode': self.region_code,
        }
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            logging.info(pprint.pformat(response.json()))
            return response.json()
        else:
            logging.error('Fehler:', response.status_code, response.text)
            return f"Google Places API Error: {response.status_code}, {response.text}"
