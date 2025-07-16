import typing

import osintbuddy.elements.base as _base


class Title(_base.BaseDisplay):
    """
    A title element for osintbuddy UI.

    Parameters
    ----------
    value : str, optional
        The text content of the title (default is "").
    label : str, optional
        An optional label for the UI node (default is "").
    style : dict[str, typing.Any], optional
        React-style properties (default is {}).
    placeholder : str, optional
        Placeholder text (default is "").
    """

    element_type: str = "title"

    def __init__(
        self,
        value: str = "",
        label: str = "",
        style: typing.Optional[dict[str, typing.Any]] = None,
        placeholder: str = "",
    ) -> None:
        super().__init__(
            label=label, style=style or {}, placeholder=placeholder
        )
        self.value: str = value

    def to_dict(self) -> dict[str, typing.Any]:
        """Render the element as a dict."""
        return self._base_entity_element(value=self.value)


class Text(_base.BaseDisplay):
    """
    A paragraph or section of text with optional icon.

    Parameters
    ----------
    value : str, optional
        The text content (default is "").
    icon : str, optional
        An icon identifier (default is "").
    label : str, optional
        Optional UI label.
    style : dict[str, typing.Any], optional
        React-style styling dictionary.
    placeholder : str, optional
        Optional placeholder string.
    """

    element_type: str = "section"

    def __init__(
        self,
        value: str = "",
        icon: str = "",
        label: str = "",
        style: typing.Optional[dict[str, typing.Any]] = None,
        placeholder: str = "",
    ) -> None:
        super().__init__(
            label=label, style=style or {}, placeholder=placeholder
        )
        self.value: str = value
        self.icon: str = icon

    def to_dict(self) -> dict[str, typing.Any]:
        """Render the element with text and icon."""
        return self._base_entity_element(value=self.value, icon=self.icon)


class Empty(_base.BaseDisplay):
    """A placeholder or spacer element."""

    element_type: str = "empty"

    def to_dict(self) -> dict[str, typing.Any]:
        """Render an empty element."""
        return self._base_entity_element()


class CopyText(_base.BaseDisplay):
    """A copyable text element."""

    element_type: str = "copy-text"

    def __init__(
        self,
        value: str = "",
        label: str = "",
        style: typing.Optional[dict[str, typing.Any]] = None,
        placeholder: str = "",
    ) -> None:
        super().__init__(
            label=label, style=style or {}, placeholder=placeholder
        )
        self.value: str = value

    def to_dict(self) -> dict[str, typing.Any]:
        """Render text with copy-to-clipboard capability."""
        return self._base_entity_element(value=self.value)


class CopyCode(_base.BaseDisplay):
    """A copyable code block element."""

    element_type: str = "copy-code"

    def __init__(
        self,
        value: str = "",
        label: str = "",
        style: typing.Optional[dict[str, typing.Any]] = None,
        placeholder: str = "",
    ) -> None:
        super().__init__(
            label=label, style=style or {}, placeholder=placeholder
        )
        self.value: str = value

    def to_dict(self) -> dict[str, typing.Any]:
        """Render code block with copy capability."""
        return self._base_entity_element(value=self.value)


class Json(_base.BaseDisplay):
    """Display JSON content."""

    element_type: str = "json"

    def to_dict(self) -> dict[str, typing.Any]:
        return self._base_entity_element()


class Image(_base.BaseDisplay):
    """Display an image."""

    element_type: str = "image"

    def to_dict(self) -> dict[str, typing.Any]:
        return self._base_entity_element()


class Pdf(_base.BaseDisplay):
    """Display a PDF file."""

    element_type: str = "pdf"

    def to_dict(self) -> dict[str, typing.Any]:
        return self._base_entity_element()


class Video(_base.BaseDisplay):
    """Display a video."""

    element_type: str = "video"

    def to_dict(self) -> dict[str, typing.Any]:
        return self._base_entity_element()


class List(_base.BaseDisplay):
    """Display a list."""

    element_type: str = "list"

    def to_dict(self) -> dict[str, typing.Any]:
        return self._base_entity_element()


class Table(_base.BaseDisplay):
    """Display a table."""

    element_type: str = "table"

    def to_dict(self) -> dict[str, typing.Any]:
        return self._base_entity_element()
