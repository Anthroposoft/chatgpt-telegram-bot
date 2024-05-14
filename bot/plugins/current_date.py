from datetime import datetime, timezone
from typing import Dict
from .plugin import Plugin
import holidays

import holidays

# Liste der Bundesländer-Codes
bundeslaender = [
    'BW',  # Baden-Württemberg
    'BY',  # Bayern
    'BE',  # Berlin
    'BB',  # Brandenburg
    'HB',  # Bremen
    'HH',  # Hamburg
    'HE',  # Hessen
    'MV',  # Mecklenburg-Vorpommern
    'NI',  # Niedersachsen
    'NW',  # Nordrhein-Westfalen
    'RP',  # Rheinland-Pfalz
    'SL',  # Saarland
    'SN',  # Sachsen
    'ST',  # Sachsen-Anhalt
    'SH',  # Schleswig-Holstein
    'TH'  # Thüringen
]

feiertage_alle_bundeslaender = {}
for bundesland in bundeslaender:
    feiertage_alle_bundeslaender[bundesland] = holidays.Germany(state=bundesland)


class CurrentDatePlugin(Plugin):
    """
    A plugin to get the current time and date
    """

    def get_source_name(self) -> str:
        return "CurrentDate"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "get_current_date",
            "description": "Get the current date and/or time for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "country_code": {"type": "string",
                                     "description": """Extract the country code from the user's input language to
                                 determine which holidays should be extracted. If no language is specified, use
                                 DE as default language. Possible values: DE, US, RU, FR, ES, IT, NL, CZ, PL, BR. '.
                                  
                                  Examples:
                                  
                                  Question: Wie spät ist es?
                                  type: DE
                                  
                                  Question: What date is today?
                                  type: US
                                  
                                  Question: Который час?
                                  type: RU
                                                                    
                                  """},
                },
                "required": ["country_code"],
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        try:
            country_code = kwargs['country_code']

            date = datetime.today().date().isoformat()
            dt = datetime.now(timezone.utc).astimezone()
            tz_info = dt.tzinfo
            holdates = holidays.country_holidays(country_code, years=[int(date.split("-")[0])])
            holiday_list = []
            for d, s in holdates.items():
                print(d.isoformat(), s)
                holiday_list.append(f"Date: {d.isoformat()}, Name: {s}")
            return {"current_time": dt,
                    "current_date": date,
                    "time_zone": tz_info,
                    "holidays": holiday_list}
        except Exception as e:
            return {'error': 'An unexpected error occurred: ' + str(e)}
