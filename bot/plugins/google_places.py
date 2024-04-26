import logging
import types
from datetime import datetime
from typing import Dict
import os
import requests

from .plugin import Plugin


class GooglePlacesTextSearchPlugin(Plugin):
    """
    A plugin to get the current weather and 7-day daily forecast for a location
    """

    def __init__(self):
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
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
                               "specifc place or location or nearby his specific location."
                               "\n"
                               "For example:\n"
                               "I am at Berlin Alexanderplatz, what are the 5 best restaurants around?\n"
                               "Restaurants near Bakerstreet London?\n"
                               "Nearest hospital to Baker street ind London?\n"
                               "I need a shoemaker. I am at Bakerstreet London?\n",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": f"""
                                The question about a location of the user. 
                                If the user question does not contain his location, ask for the
                                location and use this location to formulate the correct question for
                                the Google Places Text Search API.
                                """,
                        }
                    },
                    "required": ["question"],
                },
            }
        ]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        logging.info(kwargs["question"])

        url = 'https://places.googleapis.com/v1/places:searchText'
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.priceLevel'
        }
        data = {
            'textQuery': kwargs["question"]
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print(response.json())
            return response.json()
        else:
            print('Fehler:', response.status_code, response.text)
            return f"Google Places API Error: {response.status_code}, {response.text}"