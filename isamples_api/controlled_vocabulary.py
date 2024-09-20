import logging
from typing import Optional, Any

import requests

from isamples_api.metadata_constants import METADATA_LABEL, METADATA_IDENTIFIER


# Inherit from dict in order to make this class JSON serializable
class VocabularyTerm(dict):
    def __init__(self, key: Optional[str], label: str, uri: Optional[str]):
        self.key = key
        self.label = label
        self.uri = uri
        super().__init__(self.metadata_dict())

    def metadata_dict(self) -> dict[str, str]:
        metadata_dict = {
            METADATA_LABEL: self.label
        }
        if self.uri is not None:
            metadata_dict[METADATA_IDENTIFIER] = self.uri
        return metadata_dict


class ControlledVocabulary:
    def __init__(self, uijson_dict: dict[str, Any], key_prefix: str):
        self.vocabulary_terms_by_key: dict[str, VocabularyTerm] = {}
        self.vocabulary_terms_by_label: dict[str, VocabularyTerm] = {}
        self.vocabulary_terms_by_uri: dict[str, VocabularyTerm] = {}
        self._uijson_dict = uijson_dict
        self._key_prefix = key_prefix
        self._is_first = True
        self._process_uijson_dict(uijson_dict)

    def _term_key_for_label(self, label: str):
        return f"{self._key_prefix}:{label}"

    def _process_uijson_dict(self, uijson_dict: dict[str, Any]):
        for dict_key, value in uijson_dict.items():
            # structure looks like this:
            """
                "https://w3id.org/isample/vocabulary/material/1.0/material":
                {
                    "label":
                    {
                        "en": "Material"
                    },
                    "children":
                    [
            """
            uri = dict_key
            label = value.get("label").get("en")
            last_piece_of_uri = dict_key.rsplit("/", 1)[-1]
            term_key = self._term_key_for_label(last_piece_of_uri)
            term = VocabularyTerm(term_key, label, uri)
            # There's a mix of callers that use both namespaced and non-namespaced keys to look terms up.
            # We should support both, e.g. "biogenicnonorganicmaterial" and "spec:biogenicnonorganicmaterial"
            self.vocabulary_terms_by_key[term_key.lower()] = term
            self.vocabulary_terms_by_key[last_piece_of_uri] = term
            self.vocabulary_terms_by_label[label.lower()] = term
            self.vocabulary_terms_by_uri[uri] = term
            if self._is_first:
                self._root_term = term
                self._is_first = False
            for child in value.get("children"):
                self._process_uijson_dict(child)

    def root_term(self) -> VocabularyTerm:
        return self._root_term

    def term_for_key(self, key: str) -> VocabularyTerm:
        term = self.vocabulary_terms_by_key.get(key.lower())
        if term is None:
            term = self.vocabulary_terms_by_label.get(self._term_key_for_label(key.lower()))
        if term is None:
            logging.warning(f"Unable to look up vocabulary term for key {key}, returning root term instead.")
            term = self.root_term()
        return term

    def term_for_label(self, label: str) -> VocabularyTerm:
        term = self.vocabulary_terms_by_label.get(label.lower())
        if term is None:
            # There are cases where we may already have the uri, allow those through
            term = self.vocabulary_terms_by_uri.get(label.lower())
        if term is None:
            term = self.vocabulary_terms_by_key.get(label.lower())
        if term is None:
            logging.warning(f"Unable to look up vocabulary term for label {label}, returning root term instead.")
            term = self.root_term()
        return term

    @staticmethod
    def _fetch_uijson_from_uri(uri: str) -> dict:
        response = requests.get(uri)
        return response.json()

    MATERIAL_SAMPLE_OBJECT_TYPE = None
    MATERIAL_TYPE = None
    SAMPLED_FEATURE_TYPE = None

    @staticmethod
    def material_sample_object_type() -> "ControlledVocabulary":
        if ControlledVocabulary.MATERIAL_SAMPLE_OBJECT_TYPE is None:
            uijson = ControlledVocabulary._fetch_uijson_from_uri("https://central.isample.xyz/isamples_central/vocabulary/material_sample_type")
            assert uijson is not None
            ControlledVocabulary.MATERIAL_SAMPLE_OBJECT_TYPE = ControlledVocabulary(uijson, "spec")
        return ControlledVocabulary.MATERIAL_SAMPLE_OBJECT_TYPE

    @staticmethod
    def material_type() -> "ControlledVocabulary":
        if ControlledVocabulary.MATERIAL_TYPE is None:
            uijson = ControlledVocabulary._fetch_uijson_from_uri("https://central.isample.xyz/isamples_central/vocabulary/material_type")
            assert uijson is not None
            ControlledVocabulary.MATERIAL_TYPE = ControlledVocabulary(uijson, "mat")
        return ControlledVocabulary.MATERIAL_TYPE

    @staticmethod
    def sampled_feature_type() -> "ControlledVocabulary":
        if ControlledVocabulary.SAMPLED_FEATURE_TYPE is None:
            uijson = ControlledVocabulary._fetch_uijson_from_uri("https://central.isample.xyz/isamples_central/vocabulary/sampled_feature_type")
            assert uijson is not None
            ControlledVocabulary.SAMPLED_FEATURE_TYPE = ControlledVocabulary(uijson, "sf")
        return ControlledVocabulary.SAMPLED_FEATURE_TYPE
