from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import pandas as pd
import os

# preload the csvs in the server for faster resolution
lang_data = pd.read_csv(os.path.join("data", "lang_data.csv"))
featuremap = pd.read_csv(os.path.join("data", "featuremap.csv"))
feature_def = pd.read_csv(os.path.join("data", "feature_definitions.csv"), sep=",,, ")

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
            print("Looking up", query_lang)
            
            result= lang_data[lang_data["lang_name"] == query_lang]

            if len(result) > 0:
                lang = result.iloc[0]
                out_text = "'%s' se habla en los países: %s\nWALS Latitud, Longitud: (%s, %s)\nCódigo ISO '%s'\n" % (
                    query_lang,
                    ", ".join(result.iloc[:, -2].values),
                    lang["lat"],
                    lang["long"],
                    lang["iso_code"]
                )
                dispatcher.utter_message(text = out_text)
            else:
                dispatcher.utter_message(text = "¡Lo siento señor! No tenemos registros para el idioma %s\n" % query_lang)

        return []

class FeatureOfLanguageSearch(Action):

    def name(self) -> Text:
        return "action_feature_of_lang_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = list(tracker.get_latest_entity_values("language"))
        feat = list(tracker.get_latest_entity_values("feature"))

        if len(entities) > 0 and len(feat)>0:
            query_feature = feat.pop()

            query_lang = entities.pop()
            query_lang = query_lang.lower().capitalize()
            print("Looking up", query_feature, "for", query_lang)
            
            result= featuremap[
                (featuremap["Language_name"] == query_lang)
                & (featuremap["Parameter_name"] == query_feature)
            ]

            if len(result) > 0:
                out_text = "El valor de característica de '%s' para '%s' es '%s'\n" % (
                    query_feature,
                    query_lang,
                    result.iloc[0, -3]
                )
                dispatcher.utter_message(text = out_text)
            else:
                dispatcher.utter_message(text = "¡Lo siento señor! No tenemos registros de la función %s para el idioma %s\n" % (query_feature, query_lang))

        return []

class RandomTypeSearch(Action):

    def name(self) -> Text:
        return "action_random_type_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        val = list(tracker.get_latest_entity_values("val"))
        feat = list(tracker.get_latest_entity_values("feature"))

        if len(val) > 0 and len(feat)>0:
            query_feature = feat.pop()

            query_val = val.pop()

            print("Looking up languages with", query_val, "for", query_feature)
            
            result= featuremap[
                (featuremap["Value"] == query_val)
                & (featuremap["Parameter_name"] == query_feature)
            ]
            max_num = len(result.iloc[:, 3].values)
            n_samples = 5
            if max_num < n_samples:
                n_samples =  max_num
            if len(result) > 0:
                out_text = "Otros idiomas con la característica %s como '%s' son: %s\n" % (
                    query_feature,
                    query_val,
                    ", ".join(result.iloc[:, 3].sample(n=n_samples).values)
                )
                dispatcher.utter_message(text = out_text)
            else:
                dispatcher.utter_message(text = "¡Lo siento señor! No tenemos registros de la característica %s con valor %s\n" % (query_feature, query_val))

        return []

class FeatureCatSearch(Action):

    def name(self) -> Text:
        return "action_feature_cat_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        feat = list(tracker.get_latest_entity_values("feature"))

        if len(feat)>0:
            query_feature = feat.pop()

            print("Looking up types of", query_feature)
            
            result= featuremap[featuremap["Parameter_name"] == query_feature]["Value"].unique()
            if len(result) > 0:
                out_text = "Los diferentes tipos de característica '%s' son: %s\n" % (
                    query_feature,
                    ", ".join(result)
                )
                dispatcher.utter_message(text = out_text)
            else:
                dispatcher.utter_message(text = "¡Lo siento señor! No tenemos registros de la característica %s\n" % query_feature)

        return []

class GetDescription(Action):

    def name(self) -> Text:
        return "action_get_description"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        feat = list(tracker.get_latest_entity_values("feature"))

        if len(feat)>0:
            query_feature = feat.pop()

            print("Looking up the definition of", query_feature)
            
            result= feature_def[feature_def["Feature_Name"] == query_feature]["Feature_Definition"].values
            print(result)
            if len(result) > 0:
                out_text = "Esto es lo que encontré: '%s'\n" % (
                    result[0]
                )
                dispatcher.utter_message(text = out_text)
            else:
                dispatcher.utter_message(text = "¡Lo siento señor! No tenemos registros de la característica %s\n" % query_feature)

        return []