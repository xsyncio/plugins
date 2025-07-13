import os, importlib, inspect, sys, glob
import importlib.util
from typing import List, Any, Callable, Optional, Dict
from collections import defaultdict
from packaging import version
from pydantic import BaseModel, ConfigDict
from osintbuddy.elements.base import BaseElement
from osintbuddy.errors import OBPluginError
from osintbuddy.utils import to_snake_case


OBNodeConfig = ConfigDict(extra="allow", frozen=False, populate_by_name=True, arbitrary_types_allowed=True)

class OBNode(BaseModel):
    model_config = OBNodeConfig


class OBVersion:
    """Version handling for OSINTBuddy plugins."""
    
    def __init__(self, version_string: str):
        self.version_string = version_string
        self._parsed_version = version.parse(version_string)
    
    def __str__(self) -> str:
        return self.version_string
    
    def __repr__(self) -> str:
        return f"OBVersion('{self.version_string}')"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self._parsed_version == version.parse(other)
        elif isinstance(other, OBVersion):
            return self._parsed_version == other._parsed_version
        return False
    
    def __lt__(self, other) -> bool:
        if isinstance(other, str):
            return self._parsed_version < version.parse(other)
        elif isinstance(other, OBVersion):
            return self._parsed_version < other._parsed_version
        return NotImplemented
    
    def __le__(self, other) -> bool:
        return self == other or self < other
    
    def __gt__(self, other) -> bool:
        if isinstance(other, str):
            return self._parsed_version > version.parse(other)
        elif isinstance(other, OBVersion):
            return self._parsed_version > other._parsed_version
        return NotImplemented
    
    def __ge__(self, other) -> bool:
        return self == other or self > other
    
    def is_compatible_with(self, min_version: str, max_version: Optional[str] = None) -> bool:
        """Check if this version is compatible with the given version constraints."""
        min_ver = version.parse(min_version)
        if self._parsed_version < min_ver:
            return False
        
        if max_version is not None:
            max_ver = version.parse(max_version)
            if self._parsed_version > max_ver:
                return False
        
        return True
    
    @property
    def major(self) -> int:
        return self._parsed_version.major
    
    @property
    def minor(self) -> int:
        return self._parsed_version.minor
    
    @property
    def micro(self) -> int:
        return self._parsed_version.micro
    
    @property
    def is_prerelease(self) -> bool:
        return self._parsed_version.is_prerelease
    
    @property
    def is_dev(self) -> bool:
        return self._parsed_version.is_devrelease


class OBVersionManager:
    """Manages version compatibility for OSINTBuddy plugins."""
    
    # Current framework version - should be updated when breaking changes are made
    FRAMEWORK_VERSION = "0.1.0"
    
    @classmethod
    def get_framework_version(cls) -> OBVersion:
        """Get the current framework version."""
        return OBVersion(cls.FRAMEWORK_VERSION)
    
    @classmethod
    def validate_plugin_version(cls, plugin_version: str, min_framework_version: str = "0.1.0", 
                              max_framework_version: Optional[str] = None) -> bool:
        """Validate that a plugin version is compatible with the framework."""
        try:
            plugin_ver = OBVersion(plugin_version)
            framework_ver = cls.get_framework_version()
            
            # Check if plugin version is compatible with framework version constraints
            return framework_ver.is_compatible_with(min_framework_version, max_framework_version)
        except Exception as e:
            raise OBPluginError(f"Invalid plugin version format: {plugin_version}. Error: {e}")
    
    @classmethod
    def check_compatibility(cls, plugin_version: str, required_framework_version: str) -> bool:
        """Check if plugin version is compatible with required framework version."""
        try:
            plugin_ver = OBVersion(plugin_version)
            required_ver = OBVersion(required_framework_version)
            
            # For now, we use simple major.minor compatibility
            # Plugins are compatible if they have the same major version
            # and plugin minor version >= required minor version
            return (plugin_ver.major == required_ver.major and 
                   plugin_ver.minor >= required_ver.minor)
        except Exception as e:
            raise OBPluginError(f"Version compatibility check failed: {e}")
    
    @classmethod
    def get_version_info(cls, plugin_version: str) -> Dict[str, Any]:
        """Get detailed version information for a plugin."""
        try:
            plugin_ver = OBVersion(plugin_version)
            framework_ver = cls.get_framework_version()
            
            return {
                "plugin_version": str(plugin_ver),
                "framework_version": str(framework_ver),
                "is_compatible": cls.check_compatibility(plugin_version, cls.FRAMEWORK_VERSION),
                "version_details": {
                    "major": plugin_ver.major,
                    "minor": plugin_ver.minor,
                    "micro": plugin_ver.micro,
                    "is_prerelease": plugin_ver.is_prerelease,
                    "is_dev": plugin_ver.is_dev
                }
            }
        except Exception as e:
            raise OBPluginError(f"Failed to get version info: {e}")


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
    settings: dict


class OBRegistry(type):
    plugins = []
    labels = []
    ui_labels = []
    plugin_versions = {}  # Track plugin versions

    def __init__(cls, name, bases, attrs):
        """
        Initializes the OBRegistry metaclass by adding the plugin class
        and its label if it is a valid plugin.
        """
        if name != 'OBPlugin' and name != 'Plugin' and issubclass(cls, OBPlugin):
            label = cls.label.strip()
            
            # Validate plugin version if provided
            plugin_version = getattr(cls, 'version', '0.1.0')
            if not cls._validate_plugin_version(plugin_version):
                raise OBPluginError(f"Plugin '{label}' has invalid or incompatible version: {plugin_version}")
            
            # Store version information
            OBRegistry.plugin_versions[label] = {
                'version': plugin_version,
                'version_info': OBVersionManager.get_version_info(plugin_version),
                'class': cls
            }
            
            if cls.is_available is True:
                if isinstance(cls.author, list):
                    cls.author = ', '.join(cls.author)
                OBRegistry.ui_labels.append({
                    'label': label,
                    'description': cls.description if cls.description != None else "Description not available.",
                    'author': cls.author if cls.author != None else "Author not provided.",
                    'version': plugin_version,
                    'version_info': OBVersionManager.get_version_info(plugin_version)
                })
            OBRegistry.labels.append(label)
            OBRegistry.plugins.append(cls)
    
    @classmethod
    def _validate_plugin_version(cls, plugin_version: str) -> bool:
        """Validate plugin version format and compatibility."""
        try:
            return OBVersionManager.validate_plugin_version(plugin_version)
        except Exception:
            return False

    @classmethod
    async def get_plugin(cls, plugin_label: str, version_constraint: Optional[str] = None):
        """
        Returns the corresponding plugin class for a given plugin_label or
        'None' if not found.

        :param plugin_label: The label of the plugin to be returned.
        :param version_constraint: Optional version constraint (e.g., '>=0.1.0')
        :return: The plugin class or None if not found.
        """
        for idx, label in enumerate(cls.labels):
            if label == plugin_label or to_snake_case(label) == to_snake_case(plugin_label):
                plugin_class = cls.plugins[idx]
                
                # Check version constraint if provided
                if version_constraint is not None:
                    plugin_version = getattr(plugin_class, 'version', '0.1.0')
                    if not cls._check_version_constraint(plugin_version, version_constraint):
                        continue
                
                return plugin_class
        return None

    @classmethod
    def get_plug(cls, plugin_label: str, version_constraint: Optional[str] = None):
        """
        Returns the corresponding plugin class for a given plugin_label or
        'None' if not found.

        :param plugin_label: The label of the plugin to be returned.
        :param version_constraint: Optional version constraint (e.g., '>=0.1.0')
        :return: The plugin class or None if not found.
        """
        for idx, label in enumerate(cls.labels):
            if to_snake_case(label) == to_snake_case(plugin_label):
                plugin_class = cls.plugins[idx]
                
                # Check version constraint if provided
                if version_constraint is not None:
                    plugin_version = getattr(plugin_class, 'version', '0.1.0')
                    if not cls._check_version_constraint(plugin_version, version_constraint):
                        continue
                
                return plugin_class
        return None
    
    @classmethod
    def _check_version_constraint(cls, plugin_version: str, constraint: str) -> bool:
        """Check if plugin version satisfies the given constraint."""
        try:
            plugin_ver = OBVersion(plugin_version)
            
            # Simple constraint parsing - can be extended for more complex constraints
            if constraint.startswith('>='):
                min_version = constraint[2:].strip()
                return plugin_ver >= min_version
            elif constraint.startswith('>'):
                min_version = constraint[1:].strip()
                return plugin_ver > min_version
            elif constraint.startswith('<='):
                max_version = constraint[2:].strip()
                return plugin_ver <= max_version
            elif constraint.startswith('<'):
                max_version = constraint[1:].strip()
                return plugin_ver < max_version
            elif constraint.startswith('=='):
                exact_version = constraint[2:].strip()
                return plugin_ver == exact_version
            else:
                # Default to exact match
                return plugin_ver == constraint
        except Exception:
            return False
    
    @classmethod
    def get_plugin_version_info(cls, plugin_label: str) -> Optional[Dict[str, Any]]:
        """Get version information for a specific plugin."""
        return cls.plugin_versions.get(plugin_label)
    
    @classmethod
    def get_all_plugin_versions(cls) -> Dict[str, Dict[str, Any]]:
        """Get version information for all registered plugins."""
        return cls.plugin_versions.copy()
    
    @classmethod
    def get_plugins_by_version(cls, version_constraint: str) -> List[type]:
        """Get all plugins that satisfy the given version constraint."""
        compatible_plugins = []
        for plugin_class in cls.plugins:
            plugin_version = getattr(plugin_class, 'version', '0.1.0')
            if cls._check_version_constraint(plugin_version, version_constraint):
                compatible_plugins.append(plugin_class)
        return compatible_plugins

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


def load_plugins(plugins_path: str = "plugins"):
    """
    Loads plugins from the filesystem ./plugins/*.py directory

    :return: list of plugins sourced from the filesystem
    """
    entities = glob.glob(f'{plugins_path}/*.py')
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
    version: str = '0.1.0'  # Default version for plugins
    min_framework_version: str = '0.1.0'  # Minimum required framework version
    max_framework_version: Optional[str] = None  # Maximum supported framework version

    def __init__(self):
        # Validate plugin version compatibility on initialization
        self._validate_version_compatibility()
        
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
    
    def _validate_version_compatibility(self):
        """Validate that this plugin is compatible with the current framework."""
        try:
            framework_version = OBVersionManager.get_framework_version()
            plugin_version = OBVersion(self.version)
            
            # Check minimum framework version requirement
            if not framework_version.is_compatible_with(self.min_framework_version, self.max_framework_version):
                raise OBPluginError(
                    f"Plugin '{self.label}' (v{self.version}) requires framework version "
                    f">={self.min_framework_version}" + 
                    (f" and <={self.max_framework_version}" if self.max_framework_version else "") +
                    f", but current framework version is {framework_version}"
                )
        except Exception as e:
            raise OBPluginError(f"Version compatibility validation failed for plugin '{self.label}': {e}")
    
    def get_version_info(self) -> Dict[str, Any]:
        """Get version information for this plugin instance."""
        return {
            'plugin_version': self.version,
            'plugin_label': self.label,
            'min_framework_version': self.min_framework_version,
            'max_framework_version': self.max_framework_version,
            'framework_version': str(OBVersionManager.get_framework_version()),
            'is_compatible': OBVersionManager.check_compatibility(self.version, OBVersionManager.FRAMEWORK_VERSION)
        }

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
        Includes label, name, color, icon, version information, and a list of all elements
        for the entity/plugin.
        """
        ui_entity = defaultdict(None)
        ui_entity['data'] = {
            'label': cls.label,
            'color': cls.color if cls.color else '#145070',
            'icon': cls.icon,
            'version': cls.version,
            'version_info': OBVersionManager.get_version_info(cls.version),
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
