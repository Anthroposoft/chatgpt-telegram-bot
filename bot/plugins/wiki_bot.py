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
                    },
                    "required": ["topic"],
                },
            },
            {
                "name": "get_article_from_wikipedia",
                "description": f"""This function must be called when the user want to receive a summary about 
                                   a Wikipedia article, or if he wants that you analyse the whole wikipedia article 
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

Questions: Summarize Biodiversity from Wikipedia.
title: Biodiversity
       
Questions: Give me the wikipedia article about Python (programming language).
title: Python (programming language)
          
Questions: What is the wikipedia entry about Liverpool?. Please summarize.
title: Liverpool

Questions: Show me the most important concept in Physics based on Wikipedia.
title: Physics
               
Questions: Tell me everything about Michael Jackson the singer from Wikipedia.
title: Michael Jackson (singer)
""",
                        },
                        "type": {
                            "type": "string",
                            "description": f"""
The processing type of the wikipedia article the user want: either the 'summary' from wikipedia directly,
or the whole 'article' so that you can analyse it by user request. 
Extract this type from the user question.
Examples:

Questions: Summarize Biodiversity from Wikipedia.
type: summary

Questions: Give me the wikipedia article about Python (programming language).
type: article

Questions: Give me the wikipedia article about Python (programming language) and summarize it yourself.
type: article

Questions: What is the wikipedia entry about Liverpool?. Please summarize.
type: summary

Questions: Show me the most important concept in Physics based on Wikipedia.
type: article

Questions: Tell me everything about Michael Jackson the singer from Wikipedia.
type: article
""",
                        },
                    },
                    "required": ["title", "type"],
                },
            },
        ]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        logging.info(function_name, kwargs)
        wikipedia.set_lang(self.language_code)

        if function_name == "search_wikipedia":
            topic = kwargs['topic']
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
            the_type = kwargs['type']

            try:
                page = wikipedia.page(title)
                if "article" in the_type.lower():
                    result = {"text": page.content, "url": page.url, "images_urls": page.images,
                              "references": page.references}
                else:
                    result = {"summary": page.summary, "url":  page.url}
                logging.info(result)
                return result

            except wikipedia.exceptions.DisambiguationError as e:
                print(e.options)
                return (f"The title {title} is ambgious. Wikipedia has several entries for this title: "
                        f"{str(e.options)}. Please chose one of these titles.")
