from abc import ABC, abstractmethod
from typing import Optional, SupportsFloat

from isamples_api.controlled_vocabulary import VocabularyTerm
from isamples_api.metadata_constants import METADATA_AT_ID, METADATA_LABEL, METADATA_SAMPLE_IDENTIFIER, \
    METADATA_DESCRIPTION, METADATA_HAS_CONTEXT_CATEGORY, METADATA_HAS_MATERIAL_CATEGORY, \
    METADATA_HAS_SAMPLE_OBJECT_TYPE, METADATA_INFORMAL_CLASSIFICATION, METADATA_KEYWORDS, METADATA_PRODUCED_BY, \
    METADATA_HAS_FEATURE_OF_INTEREST, METADATA_RESPONSIBILITY, METADATA_RESULT_TIME, METADATA_SAMPLING_SITE, \
    METADATA_SAMPLE_LOCATION, METADATA_ELEVATION, METADATA_LATITUDE, METADATA_LONGITUDE, METADATA_PLACE_NAME, \
    METADATA_REGISTRANT, METADATA_SAMPLING_PURPOSE, METADATA_CURATION, METADATA_ACCESS_CONSTRAINTS, \
    METADATA_CURATION_LOCATION, METADATA_RELATED_RESOURCE, METADATA_AUTHORIZED_BY, METADATA_COMPLIES_WITH


class AbstractTransformer(ABC):

    def transform(self) -> dict:
        """Do the actual work of transforming a source record into an iSamples record.

        Arguments:
            sample -- The Sesar record to be transformed
        Return value:
            The record transformed into an iSamples record
        """
        context_categories = self.has_context_categories()
        material_categories = self.has_material_categories()
        material_sample_object_type_categories = self.has_material_sample_object_type_categories()
        transformed_record = {
            "$schema": "iSamplesSchemaCore1.0.json",
            METADATA_AT_ID: self.id_string(),
            METADATA_LABEL: self.sample_label(),
            METADATA_SAMPLE_IDENTIFIER: self.sample_identifier_string(),
            METADATA_DESCRIPTION: self.sample_description(),
            METADATA_HAS_CONTEXT_CATEGORY: context_categories,
            # "hasContextCategoryConfidence": self.has_context_category_confidences(context_categories),
            METADATA_HAS_MATERIAL_CATEGORY: material_categories,
            # "hasMaterialCategoryConfidence": self.has_material_category_confidences(material_categories),
            METADATA_HAS_SAMPLE_OBJECT_TYPE: material_sample_object_type_categories,
            # "hasSpecimenCategoryConfidence": self.has_specimen_category_confidences(specimen_categories),
            METADATA_INFORMAL_CLASSIFICATION: self.informal_classification(),
            METADATA_KEYWORDS: self.keywords(),
            METADATA_PRODUCED_BY: {
                METADATA_AT_ID: self.produced_by_id_string(),
                METADATA_LABEL: self.produced_by_label(),
                METADATA_DESCRIPTION: self.produced_by_description(),
                METADATA_HAS_FEATURE_OF_INTEREST: self.produced_by_feature_of_interest(),
                METADATA_RESPONSIBILITY: self.produced_by_responsibilities(),
                METADATA_RESULT_TIME: self.produced_by_result_time(),
                METADATA_SAMPLING_SITE: {
                    METADATA_DESCRIPTION: self.sampling_site_description(),
                    METADATA_LABEL: self.sampling_site_label(),
                    METADATA_SAMPLE_LOCATION: {
                        METADATA_ELEVATION: self.sampling_site_elevation(),
                        METADATA_LATITUDE: self.sampling_site_latitude(),
                        METADATA_LONGITUDE: self.sampling_site_longitude(),
                    },
                    METADATA_PLACE_NAME: self.sampling_site_place_names(),
                },
            },
            METADATA_REGISTRANT: self.sample_registrant(),
            METADATA_SAMPLING_PURPOSE: self.sample_sampling_purpose(),
            METADATA_CURATION: {
                METADATA_LABEL: self.curation_label(),
                METADATA_DESCRIPTION: self.curation_description(),
                METADATA_ACCESS_CONSTRAINTS: self.curation_access_constraints(),
                METADATA_CURATION_LOCATION: self.curation_location(),
                METADATA_RESPONSIBILITY: self.curation_responsibility(),
            },
            METADATA_RELATED_RESOURCE: self.related_resources(),
            METADATA_AUTHORIZED_BY: self.authorized_by(),
            METADATA_COMPLIES_WITH: self.complies_with(),
        }
        return transformed_record

    @abstractmethod
    def has_context_categories(self) -> list[VocabularyTerm]:
        pass

    @abstractmethod
    def has_material_categories(self) -> list[VocabularyTerm]:
        pass

    @abstractmethod
    def has_material_sample_object_type_categories(self) -> list[VocabularyTerm]:
        pass

    @abstractmethod
    def id_string(self) -> str:
        pass

    @abstractmethod
    def sample_label(self) -> str:
        pass

    @abstractmethod
    def sample_identifier_string(self) -> str:
        pass

    @abstractmethod
    def sample_description(self) -> str:
        pass

    @abstractmethod
    def informal_classification(self) -> list[str]:
        pass

    @abstractmethod
    def keywords(self) -> list[dict[str, str]]:
        pass

    @abstractmethod
    def produced_by_id_string(self) -> str:
        pass

    @abstractmethod
    def produced_by_label(self) -> str:
        pass

    @abstractmethod
    def produced_by_description(self) -> str:
        pass

    @abstractmethod
    def produced_by_feature_of_interest(self) -> str:
        pass

    @abstractmethod
    def produced_by_responsibilities(self) -> list[dict[str, str]]:
        pass

    @abstractmethod
    def produced_by_result_time(self) -> str:
        pass

    @abstractmethod
    def sampling_site_description(self) -> str:
        pass

    @abstractmethod
    def sampling_site_label(self) -> str:
        pass

    @abstractmethod
    def sampling_site_elevation(self) -> str:
        pass

    @abstractmethod
    def sampling_site_latitude(self) -> Optional[SupportsFloat]:
        pass

    @abstractmethod
    def sampling_site_longitude(self) -> Optional[SupportsFloat]:
        pass

    @abstractmethod
    def sampling_site_place_names(self) -> list[str]:
        pass

    @abstractmethod
    def sample_registrant(self) -> str:
        pass

    @abstractmethod
    def sample_sampling_purpose(self) -> str:
        pass

    @abstractmethod
    def curation_label(self) -> str:
        pass

    @abstractmethod
    def curation_description(self) -> str:
        pass

    @abstractmethod
    def curation_access_constraints(self) -> list[str]:
        pass

    @abstractmethod
    def curation_location(self) -> str:
        pass

    @abstractmethod
    def curation_responsibility(self) -> list[dict[str, str]]:
        pass

    @abstractmethod
    def related_resources(self) -> list[dict]:
        pass

    @abstractmethod
    def authorized_by(self) -> list[str]:
        pass

    @abstractmethod
    def complies_with(self) -> list[str]:
        pass
