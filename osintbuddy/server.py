"""OSINTBuddy Plugin Microservice (FastAPI Server).

Provides HTTP endpoints to manage OSINTBuddy plugins and transforms.
"""

import datetime
import os
import sys
import types
import typing

import fastapi
import pydantic

import osintbuddy
import osintbuddy.plugins
import osintbuddy.utils
import osintbuddy.utils.deps

osintbuddy.plugins.load_plugins()

app: fastapi.FastAPI = fastapi.FastAPI(
    title=f"OSINTBuddy Plugins v{osintbuddy.__version__}"
)


class EntityCreate(pydantic.BaseModel):
    """
    Model representing metadata and source code for a plugin entity.

    Attributes
    ----------
    id : int
        Unique identifier for the plugin.
    label : str
        The label of the plugin.
    author : str
        Author(s) of the plugin.
    description : str
        Description of what the plugin does.
    last_edit : str
        UTC timestamp of the last modification.
    source : str or None
        Source code of the plugin.
    """

    id: int
    label: str | None = None
    author: str = "Unknown author"
    description: str = "No description found..."
    last_edit: str
    source: str | None


@app.get("/entities")
async def get_entities() -> list[EntityCreate]:
    """
    Return all loaded plugin entities with metadata and source code.

    Returns
    -------
    list[EntityCreate]
        Plugin metadata with source code.
    """
    entities: list[EntityCreate] = []
    for idx, plugin in enumerate(osintbuddy.Registry.plugins):
        module_file = sys.modules[plugin.__module__].__file__

        # Handle potential None value for module_file
        if module_file is None:
            continue

        entity = EntityCreate(
            id=idx,
            label=getattr(plugin, "label", None),
            author=getattr(plugin, "author", "Unknown author"),
            description=getattr(
                plugin, "description", "No description found..."
            ),
            last_edit=datetime.datetime.fromtimestamp(
                os.path.getmtime(module_file), tz=datetime.timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            source=open(module_file, "r", encoding="utf-8").read(),
        )
        entities.append(entity)
    return entities


@app.get("/entities/{hid}")
async def get_entity_source(hid: str) -> EntityCreate | list[typing.Any]:
    """
    Return a single plugin entity's metadata and source code by ID.

    Parameters
    ----------
    hid : str
        The plugin index ID.

    Returns
    -------
    EntityCreate | list[typing.Any]
        The plugin entity or empty list if not found.
    """
    for idx, plugin in enumerate(osintbuddy.Registry.plugins):
        if str(idx) == hid:
            module_file: str | None = sys.modules[plugin.__module__].__file__

            # Handle potential None value for module_file
            if module_file is None:
                continue

            entity = EntityCreate(
                id=idx,
                label=getattr(plugin, "label", None),
                author=getattr(plugin, "author", "Unknown author"),
                description=getattr(
                    plugin, "description", "No description found..."
                ),
                last_edit=datetime.datetime.fromtimestamp(
                    os.path.getmtime(module_file), tz=datetime.timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S"),
                source=open(module_file, "r", encoding="utf-8").read(),
            )
            return entity
    return []


@app.get("/refresh")
async def reload_entities(blueprints: bool = False) -> list[dict[str, str]]:
    """
    Reload all registered plugins and return their UI labels.

    Parameters
    ----------
    blueprints : bool, optional
        Whether to refresh blueprints (unused).

    Returns
    -------
    list[dict[str, str]]
        All UI labels.
    """
    osintbuddy.Registry.labels.clear()
    osintbuddy.Registry.plugins.clear()
    osintbuddy.Registry.ui_labels.clear()
    osintbuddy.plugins.load_plugins()
    return osintbuddy.Registry.ui_labels


@app.get("/blueprint")
async def get_entity_blueprint(
    label: str,
) -> list[dict[str, typing.Any]] | dict[str, typing.Any]:
    """
    Return the blueprint of a plugin entity or all if '_osib_all'.

    Parameters
    ----------
    label : str
        Plugin label or '_osib_all' to get all.

    Returns
    -------
    list[dict[str, Any]] | dict[str, Any]
        Blueprint(s) for the plugin(s).
    """
    if label == "_osib_all":
        plugins = [
            await osintbuddy.Registry.get_plugin(
                osintbuddy.utils.to_snake_case(lbl)
            )
            for lbl in osintbuddy.Registry.labels
        ]
        return [p.create() for p in plugins if p is not None]  # type: ignore
    plugin = await osintbuddy.Registry.get_plugin(label)
    return plugin.create() if plugin is not None else []  # type: ignore


@app.get("/transforms")
async def get_entity_transforms(label: str) -> list[dict[str, str]]:
    """
    Get available transforms for a plugin entity.

    Parameters
    ----------
    label : str
        Plugin label.

    Returns
    -------
    list[dict[str, str]]
        Transform definitions (label + icon).
    """
    plugin = await osintbuddy.Registry.get_plugin(label)
    if not isinstance(plugin, types.NoneType):
        return plugin().transform_labels
    return []


@app.post("/transforms")
async def run_entity_transform(
    context: dict[str, typing.Any],
) -> list[dict[str, typing.Any]]:
    """
    Execute a plugin transform based on provided context.

    Parameters
    ----------
    context : dict[str, Any]
        Transform execution context including `label`, `transform`, and `data`.

    Returns
    -------
    list[dict[str, Any]]
        The transform output as node(s).
    """
    data: dict[str, typing.Any] = context.get("data", {})

    plugin_label = data.get("label")  # type: ignore
    if plugin_label is None:
        return []

    plugin = await osintbuddy.Registry.get_plugin(plugin_label)  # type: ignore
    if not isinstance(plugin, types.NoneType):
        result = await plugin().run_transform(
            transform_type=context.get("transform"),
            entity=context,
            use=osintbuddy.Use(
                get_driver=osintbuddy.utils.deps.get_driver, settings={}
            ),
        )
        return result
    return []
