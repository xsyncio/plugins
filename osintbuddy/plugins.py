import glob
import importlib
import importlib.util
import inspect
import sys
import typing
from collections.abc import Mapping

import pydantic

import osintbuddy.elements.base as elements_base
import osintbuddy.errors as errors
import osintbuddy.utils as utils

OBNodeConfig: pydantic.ConfigDict = pydantic.ConfigDict(
    extra="allow",
    frozen=False,
    populate_by_name=True,
    arbitrary_types_allowed=True,
)


class OBNode(pydantic.BaseModel):
    """
    Generic model to encapsulate OSINTBuddy transform input.

    Notes
    -----
    Allows arbitrary field keys and types.
    """

    model_config = OBNodeConfig


def plugin_results_middleman(
    func: typing.Callable[..., typing.Any],
) -> typing.Callable[..., typing.Any]:
    """
    Wraps plugin methods to support both generator and non-generator returns.

    Parameters
    ----------
    func : Callable
        The plugin function to wrap.

    Returns
    -------
    Callable
        Wrapped function that returns or yields results.
    """

    def _return_result(result: typing.Any) -> typing.Any:
        return typing.cast("typing.List[dict[str, typing.Any]]", result)

    def _yield_result(
        result: typing.Generator[typing.Any, None, None],
    ) -> typing.Generator[typing.Any, None, None]:
        for item in result:
            yield item

    def _decorator(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        if inspect.isgeneratorfunction(func):
            return _yield_result(func(*args, **kwargs))
        return _return_result(func(*args, **kwargs))

    return _decorator


class OBUse(pydantic.BaseModel):
    """
    Context for plugin execution.

    Attributes
    ----------
    get_driver : Callable
        Function returning browser/HTTP driver.
    settings : dict
        Plugin-specific settings.
    """

    get_driver: typing.Callable[[], None]
    settings: dict[str, typing.Any]


class OBRegistry(type):
    """
    Metaclass-based registry for OSINTBuddy plugins.

    Attributes
    ----------
    plugins : list[type]
        List of registered plugin classes.
    labels : list[str]
        Labels of registered plugins.
    ui_labels : list[dict]
        UI-visible metadata per plugin.
    """

    plugins: typing.List[type] = []
    labels: typing.List[str] = []
    ui_labels: typing.List[dict[str, str]] = []

    def __init__(
        cls, name: str, bases: tuple[type, ...], attrs: dict[str, typing.Any]
    ) -> None:
        if name not in ("OBPlugin", "Plugin") and issubclass(cls, OBPlugin):
            label = cls.label.strip()
            if cls.is_available:
                author = (
                    cls.author
                    if isinstance(cls.author, str)
                    else ", ".join(cls.author)
                )
                OBRegistry.ui_labels.append(
                    {
                        "label": label,
                        "description": cls.description
                        or "Description not available.",
                        "author": author or "Author not provided.",
                    }
                )
            OBRegistry.labels.append(label)
            OBRegistry.plugins.append(cls)
        super().__init__(name, bases, attrs)

    @classmethod
    async def get_plugin(cls, plugin_label: str) -> typing.Optional[type]:
        """
        Retrieve plugin class by label (snake_case-safe).

        Parameters
        ----------
        plugin_label : str
            Label of the plugin.

        Returns
        -------
        type or None
            Matching plugin class or None.
        """
        for i, label in enumerate(cls.labels):
            if utils.to_snake_case(label) == utils.to_snake_case(plugin_label):
                return cls.plugins[i]
        return None

    @classmethod
    def get_plug(cls, plugin_label: str) -> typing.Optional[type]:
        """
        Retrieve plugin class synchronously.

        Parameters
        ----------
        plugin_label : str
            Plugin identifier.

        Returns
        -------
        type or None
            Plugin class or None.
        """
        for i, label in enumerate(cls.labels):
            if utils.to_snake_case(label) == utils.to_snake_case(plugin_label):
                return cls.plugins[i]
        return None

    def __getitem__(cls, key: str) -> typing.Optional[type]:
        return cls.get_plug(key)


def load_plugin(mod_name: str, plugin_code: str) -> typing.List[type]:
    """
    Dynamically load a plugin from Python source code.

    Parameters
    ----------
    mod_name : str
        Desired module name.
    plugin_code : str
        Code string.

    Returns
    -------
    list[type]
        Registered plugin classes.
    """
    import types

    module = types.ModuleType(mod_name)
    exec(plugin_code, module.__dict__)
    return OBRegistry.plugins


def load_plugins(plugins_path: str = "plugins") -> typing.List[type]:
    """
    Load plugin Python modules from filesystem.

    Parameters
    ----------
    plugins_path : str
        Directory path.

    Returns
    -------
    list[type]
        Loaded plugin classes.
    """
    files = glob.glob(f"{plugins_path}/*.py")
    for path in files:
        name = path.replace(".py", "").replace("plugins/", "")
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is not None and spec.loader is not None:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
    return OBRegistry.plugins


def transform(
    label: str, icon: str = "list", edge_label: str = "transformed_to"
) -> typing.Callable[..., typing.Any]:
    """
    Decorator for plugin transform functions.

    Parameters
    ----------
    label : str
        Display label for transform.
    icon : str, optional
        Icon identifier (default: 'list').
    edge_label : str, optional
        Graph edge label (default: 'transformed_to').

    Returns
    -------
    Callable
        Decorator.
    """
    import functools

    def decorator_transform(
        func: typing.Callable[..., typing.Any],
    ) -> typing.Callable[..., typing.Any]:
        @functools.wraps(func)
        async def wrapper(
            self: typing.Any, node: OBNode, **kwargs: typing.Any
        ) -> typing.Any:
            return await func(self=self, node=node, **kwargs)

        setattr(wrapper, "label", label)
        setattr(wrapper, "icon", icon)
        setattr(wrapper, "edge_label", edge_label)
        return wrapper

    return decorator_transform


class OBPlugin(object, metaclass=OBRegistry):
    """Base class for OSINTBuddy plugin implementations."""

    entity: typing.List[elements_base.BaseElement]
    label: str = ""
    icon: str = "atom-2"
    color: str = "#145070"
    is_available: bool = True
    author: typing.Union[str, typing.List[str]] = ""
    description: str = ""

    transform_labels: typing.List[dict[str, str]]

    def __init__(self) -> None:
        transforms = self.__class__.__dict__.values()
        self.transforms = {
            utils.to_snake_case(func.label): func
            for func in transforms
            if hasattr(func, "label")
        }
        self.transform_labels = [
            {
                "label": str(func.label),
                "icon": str(getattr(func, "icon", "atom-2")),
            }
            for func in transforms
            if hasattr(func, "label")
        ]

    def __call__(self) -> dict[str, typing.Any]:
        return self.create()

    @staticmethod
    def _map_entity_labels(
        element: dict[str, typing.Any], **kwargs: typing.Any
    ) -> dict[str, typing.Any]:
        """
        Maps entity labels to values from kwargs.

        Parameters
        ----------
        element : dict
            The element dictionary (from BaseElement.to_dict()).
        kwargs : dict
            Additional values to map.

        Returns
        -------
        dict
            Updated element dictionary.
        """
        label = utils.to_snake_case(element.get("label", ""))
        if label in kwargs:
            value = kwargs[label]
            if isinstance(value, str):
                element["value"] = value
            elif isinstance(value, dict):
                value_typed = typing.cast("dict[str, typing.Any]", value)
                element.update(value_typed)
        return element

    @classmethod
    def create(cls, **kwargs: typing.Any) -> dict[str, typing.Any]:
        """Construct a new EntityCreate or OsintBuddyPlugin instance as a dictionary."""
        ui: dict[str, typing.Any] = {
            "label": cls.label,
            "color": cls.color,
            "icon": cls.icon,
            "data": {
                "elements": [],
            },
        }
        for element in cls.entity or []:
            if isinstance(element, list):
                for e in element:  # type: ignore
                    row = cls._map_entity_labels(
                        e.to_dict()
                        if hasattr(e, "to_dict") and callable(e.to_dict)  # type: ignore
                        else dict(e)  # type: ignore
                        if isinstance(e, Mapping)
                        else {},
                        **kwargs,
                    )
                    ui["data"]["elements"].append(row)
            else:
                row = cls._map_entity_labels(
                    element.to_dict()  # type: ignore
                    if hasattr(element, "to_dict")
                    and callable(element.to_dict)  # type: ignore
                    else dict(element)
                    if isinstance(element, Mapping)
                    else {},  # type: ignore
                    **kwargs,
                )
                ui["data"]["elements"].append(row)
        return ui

    async def run_transform(
        self, transform_type: str, entity: dict[str, typing.Any], use: OBUse
    ) -> typing.Optional[typing.List[dict[str, typing.Any]]]:
        """
        Execute a registered transform.

        Parameters
        ----------
        transform_type : str
            Method name.
        entity : dict
            Input entity.
        use : OBUse
            Execution context.

        Returns
        -------
        list[dict] or None
            Transformed output or None.
        """
        name = utils.to_snake_case(transform_type)
        if self.transforms and name in self.transforms:
            try:
                func = self.transforms[name]
                result: (
                    typing.List[dict[str, typing.Any]] | typing.Any
                ) = await func(
                    self=self,
                    node=self._map_to_transform_data(entity),
                    use=use,
                )
                edge = func.edge_label
                if isinstance(result, list):
                    for node in result:  # type: ignore
                        node["edge_label"] = edge
                    return result  # type: ignore
                result["edge_label"] = edge
                return [result]
            except (Exception, errors.OBPluginError) as exc:
                raise exc
        return None

    @classmethod
    def _map_to_transform_data(cls, node: dict[str, typing.Any]) -> OBNode:
        transform_map: dict[str, typing.Any] = {}
        elements = node.get("data", {}).get("elements", [])
        for item in elements:
            if isinstance(item, list):
                for sub in item:  # type: ignore
                    cls._map_element(transform_map, sub)  # type: ignore
            else:
                cls._map_element(transform_map, item)
        return OBNode(**transform_map)

    @staticmethod
    def _map_element(
        transform_map: dict[str, typing.Any], element: dict[str, typing.Any]
    ) -> None:
        label = utils.to_snake_case(element.pop("label", ""))
        transform_map[label] = {}
        element.pop("icon", None)
        element_type = element.pop("type", "")
        element.pop("placeholder", None)
        element.pop("style", None)
        element.pop("options", None)

        for k, v in element.items():
            if (
                isinstance(v, str)
                and len(element) == 1
                or element_type == "dropdown"
            ):
                transform_map[label] = v
            else:
                transform_map[label][k] = v
