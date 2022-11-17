from typing import Any, Dict, List, Union

from labelbox.data.annotation_types.annotation import (
    ClassificationAnnotation, ObjectAnnotation, VideoClassificationAnnotation,
    VideoObjectAnnotation)
from labelbox.data.annotation_types.classification.classification import (
    Checklist, ClassificationAnswer, Dropdown, Radio, Text)
from labelbox.data.annotation_types.label import Label
from labelbox.data.annotation_types.metrics.confusion_matrix import \
    ConfusionMatrixMetric
from labelbox.data.annotation_types.metrics.scalar import ScalarMetric
from labelbox.data.serialization.ndjson.converter import NDJsonConverter


class LabelsConfidencePresenceChecker:
    """
    Checks if a given list of labels contains at least one confidence score
    """

    @classmethod
    def check(cls, raw_labels: List[Dict[str, Any]]):
        label_list = NDJsonConverter.deserialize(raw_labels).as_list()
        return any([cls._check_label(x) for x in label_list])

    @classmethod
    def _check_label(cls, label: Label):
        return any([cls._check_annotation(x) for x in label.annotations])

    @classmethod
    def _check_annotation(cls, annotation: Union[ClassificationAnnotation,
                                                 ObjectAnnotation,
                                                 VideoObjectAnnotation,
                                                 VideoClassificationAnnotation,
                                                 ScalarMetric,
                                                 ConfusionMatrixMetric]):

        confidence: Union[float, None] = getattr(annotation, 'confidence')
        if confidence is not None:
            return True

        classifications: Union[List[ClassificationAnnotation],
                               None] = getattr(annotation, 'classifications')
        if classifications:
            return any([cls._check_classification(x) for x in classifications])
        return False

    @classmethod
    def _check_classification(cls,
                              classification: ClassificationAnnotation) -> bool:
        if isinstance(classification.value, (Checklist, Dropdown)):
            return any(
                cls._check_classification_answer(x)
                for x in classification.value.answer)
        if isinstance(classification.value, Radio):
            return cls._check_classification_answer(classification.value.answer)
        if isinstance(classification.value, Text):
            return False
        raise Exception(
            f"Unexpected classification value type {type(classification.value)}"
        )

    @classmethod
    def _check_classification_answer(cls, answer: ClassificationAnswer) -> bool:
        return answer.confidence is not None
