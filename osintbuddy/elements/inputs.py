import typing

import osintbuddy.elements.base as _base


class UploadFileInput(_base.BaseInput):
    """
    Upload file input node for the OsintBuddy plugin system.

    Parameters
    ----------
    value : str, optional
        Initial file value (default is "").
    supported_files : list[str], optional
        List of allowed file extensions (default is empty list).
    icon : str, optional
        Icon for the node (default is "IconFileUpload").
    label, style, placeholder : see BaseInput

    Usage Example
    -------------
    class Plugin(OBPlugin):
        node = [UploadFileInput(supported_files=['.pdf', '.docx'])]
    """

    element_type: str = "upload"

    def __init__(
        self,
        value: str = "",
        supported_files: list[str] | None = None,
        icon: str = "IconFileUpload",
        label: str = "",
        style: dict[str, typing.Any] | None = None,
        placeholder: str = "",
    ) -> None:
        super().__init__(
            label=label, style=style or {}, placeholder=placeholder
        )
        self.value = value
        self.icon = icon
        self.supported_files = supported_files or []

    def to_dict(self) -> dict[str, typing.Any]:
        return self._base_entity_element(
            value=self.value,
            icon=self.icon,
            supported_files=self.supported_files,
        )


class TextInput(_base.BaseInput):
    """
    Text input node for the OsintBuddy plugin system.

    Parameters
    ----------
    value : str, optional
        Text input value (default is "").
    icon : str, optional
        Icon to display (default is "IconAlphabetLatin").
    default : str, optional
        Ignored, reserved for future use.

    Usage Example
    -------------
    class Plugin(OBPlugin):
        node = [TextInput(label='Email search', placeholder='Enter email')]
    """

    element_type: str = "text"

    def __init__(
        self,
        value: str = "",
        default: str = "",
        icon: str = "IconAlphabetLatin",
        label: str = "",
        style: dict[str, typing.Any] | None = None,
        placeholder: str = "",
    ) -> None:
        super().__init__(
            label=label, style=style or {}, placeholder=placeholder
        )
        self.value = value
        self.icon = icon

    def to_dict(self) -> dict[str, typing.Any]:
        return self._base_entity_element(value=self.value, icon=self.icon)


class TextAreaInput(_base.BaseInput):
    """
    Text area input node (multi-line text input).

    Parameters
    ----------
    value : str, optional
        Text area value (default is "").
    icon : str, optional
        Optional icon (default is "IconAlphabetLatin").
    """

    element_type: str = "textarea"

    def __init__(
        self,
        value: str = "",
        default: str = "",
        icon: str = "IconAlphabetLatin",
        label: str = "",
        style: dict[str, typing.Any] | None = None,
        placeholder: str = "",
    ) -> None:
        super().__init__(
            label=label, style=style or {}, placeholder=placeholder
        )
        self.value = value
        self.icon = icon

    def to_dict(self) -> dict[str, typing.Any]:
        return self._base_entity_element(value=self.value, icon=self.icon)


class DropdownInput(_base.BaseInput):
    """
    Dropdown select input for the OsintBuddy plugin system.

    Parameters
    ----------
    options : list[dict[str, typing.Any]]
        Dropdown options, each must contain 'label', optionally 'tooltip' and 'value'.
    value : dict[str, str], optional
        Initially selected item.

    Usage Example
    -------------
    class Plugin(OBPlugin):
        node = [
            DropdownInput(
                options=[{'label': 'Option 1', 'tooltip': 'Hello on hover!'}],
                value={'label': 'Option 1', 'tooltip': '', 'value': ''}
            )
        ]
    """

    element_type: str = "dropdown"

    def __init__(
        self,
        options: list[dict[str, typing.Any]] | None = None,
        value: dict[str, str] | None = None,
        label: str = "",
        style: dict[str, typing.Any] | None = None,
        placeholder: str = "",
    ) -> None:
        super().__init__(
            label=label, style=style or {}, placeholder=placeholder
        )
        self.options = options or []
        self.value = value or {"label": "", "tooltip": "", "value": ""}

    def to_dict(self) -> dict[str, typing.Any]:
        return self._base_entity_element(
            options=self.options, value=self.value
        )


class NumberInput(_base.BaseInput):
    """
    Whole number input field.

    Parameters
    ----------
    value : int, optional
        Integer value to store (default is 1).
    icon : str, optional
        Icon to display (default is "123").
    """

    element_type: str = "number"

    def __init__(
        self,
        value: int = 1,
        icon: str = "123",
        label: str = "",
        style: dict[str, typing.Any] | None = None,
        placeholder: str = "",
    ) -> None:
        super().__init__(
            label=label, style=style or {}, placeholder=placeholder
        )
        self.value = value
        self.icon = icon

    def to_dict(self) -> dict[str, typing.Any]:
        return self._base_entity_element(value=self.value, icon=self.icon)


class DecimalInput(_base.BaseInput):
    """
    Decimal number input field.

    Parameters
    ----------
    value : float, optional
        Float value to store (default is 3.14).
    icon : str, optional
        Icon to display (default is "123").
    """

    element_type: str = "decimal"

    def __init__(
        self,
        value: float = 3.14,
        icon: str = "123",
        label: str = "",
        style: dict[str, typing.Any] | None = None,
        placeholder: str = "",
    ) -> None:
        super().__init__(
            label=label, style=style or {}, placeholder=placeholder
        )
        self.value = value
        self.icon = icon

    def to_dict(self) -> dict[str, typing.Any]:
        return self._base_entity_element(value=self.value, icon=self.icon)
