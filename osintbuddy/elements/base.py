import typing


class BaseElement:
    """
    BaseElement is the fundamental class for all UI elements in osintbuddy.

    It provides shared attributes and the core serialization logic required
    by the osintbuddy UI for consistent rendering of input and display elements.

    Parameters
    ----------
    label : str, optional
        A human-readable label for the element (default is "").
    style : dict[str, Any], optional
        A dictionary of React-style properties to apply to the element
        (default is an empty dict).
    placeholder : str, optional
        A placeholder string used in input/display elements (default is "").

    Attributes
    ----------
    label : str
        The label associated with the element.
    style : dict[str, Any]
        CSS-like style definitions used in the frontend.
    placeholder : str
        A placeholder string for the UI.
    element_type : str
        Must be defined in subclasses to describe the element type.

    Methods
    -------
    _base_entity_element(**kwargs) -> dict[str, Any]
        Constructs the base dictionary required by the UI.
    """

    def __init__(
        self,
        label: str = "",
        style: typing.Optional[dict[str, typing.Any]] = None,
        placeholder: str = "",
    ) -> None:
        self.label: str = label
        self.style: dict[str, typing.Any] = style if style is not None else {}
        self.placeholder: str = placeholder

    def _base_entity_element(
        self, **kwargs: typing.Any
    ) -> dict[str, typing.Any]:
        """
        Constructs the dictionary representing the element for UI rendering.

        Parameters
        ----------
        **kwargs : Any
            Additional key-value pairs specific to subclasses.

        Returns
        -------
        dict[str, Any]
            A dictionary containing the common and custom UI attributes.

        Raises
        ------
        AttributeError
            If the subclass does not define the `element_type` attribute.

        Examples
        --------
        >>> class MyElement(BaseElement):
        ...     element_type = "custom"
        >>> e = MyElement(label="Name", style={"color": "blue"})
        >>> e._base_entity_element(foo="bar")
        {
            "type": "custom",
            "label": "Name",
            "style": {"color": "blue"},
            "foo": "bar"
        }
        """
        if not hasattr(self, "element_type"):
            raise AttributeError(
                "Subclasses must define an `element_type` attribute."
            )

        base: dict[str, typing.Any] = {
            "type": getattr(self, "element_type"),
            "label": self.label,
            "style": self.style,
        }

        if self.placeholder:
            base["placeholder"] = self.placeholder

        base.update(kwargs)
        return base


class BaseInput(BaseElement):
    """
    Base class for input-type elements in osintbuddy.

    Subclasses must override or use the `element_type` attribute to define
    the specific input element type used in rendering.
    """

    element_type: str = "input"


class BaseDisplay(BaseElement):
    """
    Base class for display-only elements in osintbuddy.

    Subclasses must override or use the `element_type` attribute to define
    the specific display element type used in rendering.
    """

    element_type: str = "display"
