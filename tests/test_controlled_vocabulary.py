import json

from isamples_api.controlled_vocabulary import ControlledVocabulary


def _test_controlled_vocabulary(path: str):
    with open(path) as json_file:
        controlled_vocabulary_json = json.load(json_file)
        controlled_vocabulary = ControlledVocabulary(controlled_vocabulary_json, "foo")
        root_term = controlled_vocabulary.root_term()
        assert root_term is not None


def test_material_type():
    _test_controlled_vocabulary("./test_data/vocabularies/material_type.json")


def test_material_sample_object_type():
    _test_controlled_vocabulary("./test_data/vocabularies/material_sample_object_type.json")


def test_sampled_feature_type():
    _test_controlled_vocabulary("./test_data/vocabularies/sampled_feature_type.json")
