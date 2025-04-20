import os, importlib, inspect, sys, glob
import importlib.util
from typing import List, Any, Callable
from collections import defaultdict
from pydantic import BaseModel, ConfigDict
from osintbuddy.elements.base import BaseElement
from osintbuddy.errors import OBPluginError
from osintbuddy.utils import to_snake_case


OBNodeConfig = ConfigDict(extra="allow", frozen=False, populate_by_name=True, arbitrary_types_allowed=True)

class OBNode(BaseModel):
    model_config = OBNodeConfig


def plugin_results_middleman(f):
    def return_result(r):
        return r
    def yield_result(r):
        for i in r:
            yield i
    def decorator(*a, **kwa):
        if inspect.isgeneratorfunction(f):
            return yield_result(f(*a, **kwa))
        else:
            return return_result(f(*a, **kwa))
    return decorator


class OBUse(BaseModel):
    get_driver: Callable[[], None]


class OBRegistry(type):
    plugins = []
    labels = []
    ui_labels = []

    def __init__(cls, name, bases, attrs):
        """
        Initializes the OBRegistry metaclass by adding the plugin class
        and its label if it is a valid plugin.
        """
        if name != 'OBPlugin' and name != 'Plugin' and issubclass(cls, OBPlugin):
            label = cls.label.strip()
            if cls.is_available is True:
                if isinstance(cls.author, list):
                    cls.author = ', '.join(cls.author)
                OBRegistry.ui_labels.append({
                    'label': label,
                    'description': cls.description if cls.description != None else "Description not available.",
                    'author': cls.author if cls.author != None else "Author not provided.",
                })
            OBRegistry.labels.append(label)
            OBRegistry.plugins.append(cls)

    @classmethod
    async def get_plugin(cls, plugin_label: str):
        """
        Returns the corresponding plugin class for a given plugin_label or
        'None' if not found.

        :param plugin_label: The label of the plugin to be returned.
        :return: The plugin class or None if not found.
        """
        for idx, label in enumerate(cls.labels):
            if label == plugin_label or to_snake_case(label) == to_snake_case(plugin_label):
                return cls.plugins[idx]
        return None

    @classmethod
    def get_plug(cls, plugin_label: str):
        """
        Returns the corresponding plugin class for a given plugin_label or
        'None' if not found.

        :param plugin_label: The label of the plugin to be returned.
        :return: The plugin class or None if not found.
        """
        for idx, label in enumerate(cls.labels):
            if to_snake_case(label) == to_snake_case(plugin_label):
                return cls.plugins[idx]
        return None

    def __getitem__(self, i: str):
        return self.get_plug[i]

# https://stackoverflow.com/a/7548190
def load_plugin(
    mod_name: str,
    plugin_code: str,
):
    """
    Load plugins from a string of code

    :param module_name: The desired module name of the plugin.
    :param plugin_code: The code of the plugin.
    :return:
    """
    # spec = importlib.util.spec_from_file_location('my_module', '/paht/to/my_module')
    # module = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(module)
    new_mod = importlib.create_module(mod_name)
    exec(plugin_code, new_mod.__dict__)
    return OBRegistry.plugins


def load_plugins():
    """
    Loads plugins from the filesystem ./plugins/*.py directory

    :return: list of plugins sourced from the filesystem
    """
    entities = glob.glob('plugins/*.py')
    for entity in entities:
        mod_name = entity.replace('.py', '').replace('plugins/', '')
        spec = importlib.util.spec_from_file_location(mod_name, f"{entity}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)
    return OBRegistry.plugins


def transform(label, icon='list', edge_label='transformed_to'):
    """
    A decorator add transforms to an osintbuddy plugin.

    Usage:
    @transform(label=<label_text>, icon=<tabler_react_icon_name>)
    def transform_to_ip(self, node, **kwargs):
        # Method implementation

    :param label: str, A string representing the label for the transform
        method, which can be utilized for displaying in the context menu.
    :param icon: str, Optional icon name, representing the icon associated
        displayed by the transform label. Default is "list".
    :return: A decorator for the plugin transform method.
    """
    def decorator_transform(func, edge_label=edge_label):
        async def wrapper(self, node, **kwargs):
            return await func(self=self, node=node, **kwargs)
        wrapper.label = label
        wrapper.icon = icon
        wrapper.edge_label = edge_label
        return wrapper
    return decorator_transform


class OBPlugin(object, metaclass=OBRegistry):
    """
    OBPlugin is the base class for all plugin classes in this application.
    It provides the required structure and methods for a plugin.
    """
    entity: List[BaseElement]
    color: str = '#145070'
    label: str = ''
    icon: str = 'atom-2'
    is_available = True

    author = ''
    description = ''

    def __init__(self):
        transforms = self.__class__.__dict__.values()
        self.transforms = {
            to_snake_case(func.label): func for func in transforms if hasattr(func, 'label')
        }
        self.transform_labels = [
            {
                'label': func.label,
                'icon': func.icon if hasattr(func, 'icon') else 'atom-2',
            } for func in transforms
            if hasattr(func, 'label')
        ]

    def __call__(self):
        return self.create()

    @staticmethod
    def _map_entity_labels(element, **kwargs):
        label = to_snake_case(element['label'])
        for element_key in kwargs.keys():
            if element_key == label:
                if isinstance(kwargs[label], str):
                    element['value'] = kwargs[label]
                elif isinstance(kwargs[label], dict):
                    for t in kwargs[label]:
                        element[t] = kwargs[label][t]
        return element

    @classmethod
    def create(cls, **kwargs):
        """
        Generate and return a dictionary representing the plugins ui entity.
        Includes label, name, color, icon, and a list of all elements
        for the entity/plugin.
        """
        ui_entity = defaultdict(None)
        ui_entity['data'] = {
            'label': cls.label,
            'color': cls.color if cls.color else '#145070',
            'icon': cls.icon,
            'elements': []
        }
        if cls.entity:
            for element in cls.entity:
                # if an entity element is a nested list, 
                # elements will be positioned next to each other horizontally
                if isinstance(element, list):
                    ui_entity['data']['elements'].append([
                        cls._map_entity_labels(elm.to_dict(), **kwargs)
                        for elm in element
                    ])
                # otherwise position the entity elements vertically on the actual UI entity
                else:
                    element_row = cls._map_entity_labels(element.to_dict(), **kwargs)
                    ui_entity['data']['elements'].append(element_row)
            return ui_entity


    async def run_transform(self, transform_type: str, entity, use: OBUse) -> Any:
        """ Return output from a function accepting node data.
            The function will be called with a single argument, the node data
            from when a node context menu action is taken - and should return
            a list of Nodes.
            None if the plugin doesn't provide a transform
            for the transform_type.
        """
        transform_type = to_snake_case(transform_type)
        if self.transforms and self.transforms[transform_type]:
            try:
                transform = await self.transforms[transform_type](
                    self=self,
                    node=self._map_to_transform_data(entity),
                    use=use
                )
                edge_label = self.transforms[transform_type].edge_label
                if not isinstance(transform, list):
                    transform['edge_label'] = edge_label
                    return [transform]
                [
                    n.__setitem__('edge_label', edge_label)
                    for n in transform
                ]
                return transform
            except (Exception, OBPluginError) as e:
                raise e
                # exc_type, exc_obj, exc_tb = sys.exc_info()
                # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                # raise OBPluginError(f"Unhandled plugin error! {exc_type}\nPlease see {fname} on line no. {exc_tb.tb_lineno}\n{e}")
        return None

    @staticmethod
    def _map_element(transform_map: dict, element: dict):
        label = to_snake_case(element.pop('label', None))
        transform_map[label] = {}
        element_type = element.pop('type', None)
        element.pop('icon', None)
        element.pop('placeholder', None)
        element.pop('style', None)
        element.pop('options', None)
        for k, v in element.items():
            if (isinstance(v, str) and len(element.values()) == 1) or element_type == 'dropdown':
                transform_map[label] = v
            else:
                transform_map[label][k] = v

    @classmethod
    def _map_to_transform_data(cls, node: dict) -> OBNode:
        transform_map: dict = {}
        data: dict = node.get('data', {})
        elements: list[dict] = data.get('elements', [])
        for element in elements:
            if isinstance(element, list):
                [cls._map_element(transform_map, elm) for elm in element]
            else:
                cls._map_element(transform_map, element)
        return OBNode(**transform_map)
