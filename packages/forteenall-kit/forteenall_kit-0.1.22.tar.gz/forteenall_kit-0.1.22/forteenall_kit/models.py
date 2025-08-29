from __future__ import annotations
from abc import ABC

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from forteenall_kit.invoke import Invoker
    from forteenall_kit.models import FeatureData


class FieldBase(ABC):
    def __init__(self, desc: str, required=False):
        self.desc = desc
        self.value = (None,)
        self.required = required

    @property
    def shema(self):
        return {
            "type": None,
            "description": self.desc,
        }

    def __str__(self):
        return f"<{super().__str__()}: {str(self.value)}>"

    def setValue(self, value):
        self.value = value


class CharField(FieldBase):
    @property
    def shema(self):
        return {
            **super().shema,
            "type": "string",
        }


class BoolField(FieldBase):
    @property
    def shema(self):
        return {
            **super().shema,
            "type": "boolean",
        }


class TextField(FieldBase):
    @property
    def shema(self):
        return {
            **super().shema,
            "type": "string",
        }


class IntegerField(FieldBase):
    @property
    def shema(self):
        return {
            **super().shema,
            "type": "number",
        }


class ChoiceField(FieldBase):
    def __init__(self, desc, choices: list[str], required=False):
        super().__init__(desc, required)
        self.choices = choices

    @property
    def shema(self):
        return {
            **super().shema,
            "type": "string",
        }


class ListModel(FieldBase):
    def __init__(self, desc, to: FeatureData, required=False):
        super().__init__(desc, required)
        self.feature = to

    @property
    def shema(self):
        return {
            **super().shema,
            "type": "array",
            "items": self.feature.shema,
        }


class FeatureData(ABC):
    def __init__(self, options):
        super().__init__()

        # this options set from JSON
        self.options = options
        self.fields: dict[str, FieldBase] = {}

    def _addField(self, name: str, field: FieldBase):
        self.__setattr__(name, field)
        self.fields[name] = field

    @property
    def shema(self):
        """
        create standard shema for this model.
        verify model and use in LLM prompt
        """

        properties = {}
        required_fields = []

        for name, field in self.fields.items():
            # check for shema and add to property
            properties[name] = field.shema

            # check each fields is required or not
            if field.required:
                required_fields.append(name)

        return {
            "title": "InvokerConfig",
            "type": "object",
            "properties": properties,
            "required": required_fields,
        }
