import logging
from typing import Dict
import os
import wikipedia

from .plugin import Plugin


class WikipediaPlugin(Plugin):

    def __init__(self):
        self.language_code = os.getenv('WIKIPEDIA_LANGUAGE_CODE', default="en")

    def get_source_name(self) -> str:
        return "WikipediaSearchInterface"

    def get_spec(self) -> [Dict]:
        return [
            {
                "name": "search_wikipedia",
                "description": f"""This function must be called when the user want to search Wikipedia 
                                   for a specific topic and want to see a list of titles that where found.
                                   The user must explicitly mention Wikipedia and search terms for a specific
                                   topic.
                                  .""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": f"""
The topic the user want to search for. Extract this topic 
from the user question, if he wants to search the wikipedia entries/titles for 
a specific topic. Examples:

Questions: Look for Biodiversity in Wikipedia.
topic: Biodiversity
       
Questions: Query for programming languages in Wikipedia.
topic: programming languages
          
Questions: Search for Liverpool in Wikipedia.
topic: Liverpool
               
Questions: Search for Politicians from London in Wikipedia.
topic: Politicians from London""",
                        },
                        "num_titles": {
                            "type": "integer",
                            "description": """
The numbers of entries/titles to search for. Extract this number from the question of the user,
if he explicitly mention it. Default is 5.

Questions: Look for Biodiversity in Wikipedia. Reduce the number of titles to 10.
num_titles: 10

Questions: Find the top 3 results about Python in Wikipedia.
num_titles: 3"""
                        },
                        "language": {
                            "type": "string",
                            "description": """
Detect the language that the user would like to search for. Extract this from the question of the user, or
use the language of the question if the user did not mention it.

Questions: Look for Biodiversity in Wikipedia. Reduce the number of titles to 10.
language: en

Questions: Finde die Einträge über Python in Wikipedia.
language: de

Questions: Search the russian wikipedia for Siberian Tiger.
language: ru
"""
                        },
                    },
                    "required": ["topic", "language"],
                },
            },
            {
                "name": "get_article_from_wikipedia",
                "description": f"""This function must be called when the user want to receive a full  
                                   Wikipedia article, or if he wants that you analyse the whole wikipedia article 
                                   for a specific title. The user must explicitly mention Wikipedia and 
                                   summary or page terms for a specific title in wikipedia.
                                  .""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": f"""
The title of the wikipedia article the user want to summarize or to analyse by you. 
Extract this title from the user question.
Examples:

Questions: Summarize Biodiversity article from Wikipedia.
title: Biodiversity
       
Questions: Give me the wikipedia article about Python (programming language).
title: Python (programming language)
          
Questions: What is the wikipedia entry about Liverpool?. Please summarize.
title: Liverpool

Questions: Show me the most important concept in Physics based on Wikipedia.
title: Physics
               
Question: Tell me everything about Michael Jackson the singer from Wikipedia.
title: Michael Jackson (singer)

Question: Load the wikipedia article about Michael Jackson the singer from Wikipedia.
title: Michael Jackson (singer)
""",
                        },
                        "language": {
                            "type": "string",
                            "description": """
Detect the language that the user would like to search for. Extract this from the question of the user, or
use the language of the question if the user did not mention it.

Questions: Tell me everything about Michael Jackson the singer from Wikipedia.
language: en

Question: Lade den Artikel über Python aus Wikipedia.
language: de

Questions: Show me the russian wikipedia about the Siberian Tiger.
language: ru
"""
                        },
                    },
                    "required": ["title", "language"],
                },
            },
        ]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        logging.info(function_name, kwargs)

        if function_name == "search_wikipedia":
            topic = kwargs['topic']
            language = kwargs['language']
            wikipedia.set_lang(language)
            print("Wiki search", topic, language)
            num_titles = 5
            if "num_titles" in kwargs:
                num_titles = kwargs['num_titles']

            r = wikipedia.search(topic, results=num_titles)
            search_result = (f"The following titles about the topic {topic} where found in wikipedia: {str(r)}.\n"
                             f"You can use these titles to ask for a summary or the complete wikipedia "
                             f"entry page for this title.")
            return {"topic": topic, "search_result": search_result}

        elif function_name == "get_article_from_wikipedia":
            title = kwargs['title']
            language = kwargs['language']
            wikipedia.set_lang(language)
            print("Wiki article", title, language)

            try:
                page = wikipedia.page(title)
                result = {"text": page.content, "url": page.url, "images_urls": page.images,
                          "references": page.references}
                logging.info(result)
                return result

            except wikipedia.exceptions.DisambiguationError as e:
                return (f"The title {title} is ambgious. Wikipedia has several entries for this title: "
                        f"{str(e.options)}. Please chose one of these titles.")
