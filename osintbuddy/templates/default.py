"""
Plugin source code generator for OsintBuddy.

This utility returns a string of Python code that serves as a template
for a new OsintBuddy plugin class, with fields pre-filled from parameters.
"""

import re


def plugin_source_template(label: str, description: str, author: str) -> str:
    """
    Generate a source template for a new OsintBuddy plugin.

    Parameters
    ----------
    label : str
        The human-readable label of the plugin.
    description : str
        A short description of what the plugin does.
    author : str
        The author's name or handle.

    Returns
    -------
    str
        A string containing the complete plugin source code.
    """
    class_name = re.sub(r"\W|^(?=\d)", "", label.title().replace(" ", ""))
    return f"""import osintbuddy as ob
from osintbuddy.elements import TextInput

class {class_name}(ob.Plugin):
    label = "{label}"
    icon = "atom-2"   # Customize with a Tabler icon (https://tabler-icons.io/)
    color = "#FFD166"

    author = "{author}"
    description = "{description}"

    entity = [
        TextInput(label="Example", icon="radioactive")
    ]

    @ob.transform(label="To example", icon="atom-2")
    async def transform_example(self, node, use):
        WebsitePlugin = await ob.Registry.get_plugin("website")
        website_plugin = WebsitePlugin()
        return website_plugin.create(domain=node.example)
"""
