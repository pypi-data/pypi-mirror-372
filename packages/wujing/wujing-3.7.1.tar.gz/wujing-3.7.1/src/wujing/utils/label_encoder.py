import numpy as np
from pydantic import validate_call
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer


class ConsistentLabelEncoder:
    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def __init__(self, labels: list[str]) -> None:
        unique_labels = sorted(list(set(labels)))
        self.le = LabelEncoder()
        self.le.fit(unique_labels)
        self.labels = unique_labels

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def transform(self, label: str) -> int:
        return int(self.le.transform([label])[0])

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def inverse_transform(self, index: int) -> str:
        return self.le.inverse_transform([index])[0]

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def get_mapping(self, reverse: bool = False) -> dict[str, int] | dict[int, str]:
        if reverse:
            return {self.transform(label): label for label in self.labels}
        else:
            return {label: self.transform(label) for label in self.labels}


class ConsistentMultiLabelBinarizer:
    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def __init__(self, labels: list[list[str]]) -> None:
        all_labels = set()
        for label_list in labels:
            all_labels.update(label_list)
        sorted_labels = sorted(list(all_labels))

        self.mlb = MultiLabelBinarizer(classes=sorted_labels)
        self.mlb.fit(labels)

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def transform(self, label_list: list[str]) -> list[int]:
        return self.mlb.transform([label_list])[0].tolist()

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def inverse_transform(self, binary_array: list[int]) -> list[str]:
        result = self.mlb.inverse_transform(np.array([binary_array]))[0]
        return list(result)

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def get_mapping(self, reverse: bool = False) -> dict[str, int] | dict[int, str]:
        if reverse:
            return {idx: label for idx, label in enumerate(self.mlb.classes_)}
        else:
            return {label: idx for idx, label in enumerate(self.mlb.classes_)}
