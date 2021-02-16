# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import pandas as pd
import os

# preload the csvs in the server for faster resolution
lang_path = os.path.join("data", "cldf-datasets-wals-014143f", "raw", "language.csv")
lang_data = pd.read_csv(lang_path)

country_path = os.path.join("data", "cldf-datasets-wals-014143f", "raw", "country.csv")
country_data = pd.read_csv(country_path)

cl_path = os.path.join("data", "cldf-datasets-wals-014143f", "raw", "countrylanguage.csv")
cl_data = pd.read_csv(cl_path)

class ActionLanguageSearch(Action):

    def name(self) -> Text:
        return "action_lang_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = list(tracker.get_latest_entity_values("language"))

        if len(entities) > 0:
            query_lang = entities.pop()
            query_lang = query_lang.lower().capitalize()
            print(query_lang)
            
            out_lang = lang_data[lang_data["name"] == query_lang].to_dict("records")

            if len(out_lang) > 0:
                out_lang = out_lang[0]
                
                # use the private keys to find the corresponding country
                matched_country = cl_data[cl_data["language_pk"] == out_lang["pk"]].to_dict("records")
                country_name = country_data[country_data["pk"] == matched_country[0]["country_pk"]].to_dict("records")
                if len(country_name) > 0:
                    country_name = country_name[0]["name"]
                else:
                    country_name = "<Not found>"
                out_text = "'%s' pertenece al país '%s'\nLatitud, Longitud: (%s, %s)\nCódigo ISO '%s'\n" % (out_lang["name"], country_name, out_lang["latitude"], out_lang["longitude"], out_lang["id"])
                dispatcher.utter_message(text = out_text)
            else:
                dispatcher.utter_message(text = "¡Lo siento! No tenemos registros para el idioma %s\n" % query_lang)

        return []
