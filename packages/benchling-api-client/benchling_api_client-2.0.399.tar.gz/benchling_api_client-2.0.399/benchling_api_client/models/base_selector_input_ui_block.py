from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="BaseSelectorInputUIBlock")


@attr.s(auto_attribs=True, repr=False)
class BaseSelectorInputUIBlock:
    """  """

    _options: List[str]
    _placeholder: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("options={}".format(repr(self._options)))
        fields.append("placeholder={}".format(repr(self._placeholder)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BaseSelectorInputUIBlock({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        options = self._options

        placeholder = self._placeholder

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        # Allow the model to serialize even if it was created outside of the constructor, circumventing validation
        if options is not UNSET:
            field_dict["options"] = options
        if placeholder is not UNSET:
            field_dict["placeholder"] = placeholder

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any], strict: bool = False) -> T:
        d = src_dict.copy()

        def get_options() -> List[str]:
            options = cast(List[str], d.pop("options"))

            return options

        try:
            options = get_options()
        except KeyError:
            if strict:
                raise
            options = cast(List[str], UNSET)

        def get_placeholder() -> Union[Unset, None, str]:
            placeholder = d.pop("placeholder")
            return placeholder

        try:
            placeholder = get_placeholder()
        except KeyError:
            if strict:
                raise
            placeholder = cast(Union[Unset, None, str], UNSET)

        base_selector_input_ui_block = cls(
            options=options,
            placeholder=placeholder,
        )

        base_selector_input_ui_block.additional_properties = d
        return base_selector_input_ui_block

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def options(self) -> List[str]:
        if isinstance(self._options, Unset):
            raise NotPresentError(self, "options")
        return self._options

    @options.setter
    def options(self, value: List[str]) -> None:
        self._options = value

    @property
    def placeholder(self) -> Optional[str]:
        if isinstance(self._placeholder, Unset):
            raise NotPresentError(self, "placeholder")
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value: Optional[str]) -> None:
        self._placeholder = value

    @placeholder.deleter
    def placeholder(self) -> None:
        self._placeholder = UNSET
