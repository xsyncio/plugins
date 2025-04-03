import sys, os, importlib, inspect
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from osintbuddy import __version__
from osintbuddy.plugins import load_plugins
from osintbuddy.utils import to_snake_case
from osintbuddy import Registry

load_plugins()
app = FastAPI(title=f"OSINTBuddy Plugins v{__version__}")


class EntityCreate(BaseModel):
    id: int
    label: str = None
    author: str = "Unknown author"
    description: str = "No description found..."
    last_edit: str
    source: str | None


@app.get("/entities")
async def get_entities():
    entities = []
    for idx, plugin in enumerate(Registry.plugins):
        file = sys.modules[plugin.__module__].__file__ 
        file_entity = EntityCreate(
                label=plugin.label,
                author=plugin.author,
                description=plugin.description,
                last_edit=datetime.utcfromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S'),
                id=idx,
                source=""
        )
        entities.append(file_entity)
    return {"entities": entities}


@app.get("/entities/{hid}")
async def get_entity_source(hid: str):
    for idx, plugin in enumerate(Registry.plugins):
        if str(idx) == hid:
            file = sys.modules[plugin.__module__].__file__ 
            source = open(file).read()
            entity = EntityCreate(
                id=idx,
                label=plugin.label,
                author=plugin.author,
                description=plugin.description,
                last_edit=datetime.utcfromtimestamp(os.path.getmtime(file)).strftime('%Y-%m-%d %H:%M:%S'),
                source=source
            )
            return entity
    return []


@app.get("/refresh")
async def reload_entities():
    load_plugins()
    return Registry.ui_labels


@app.get("/blueprint")
async def get_entity_blueprint(label: str):
    plugin = await Registry.get_plugin(label)
    return plugin.blueprint() if plugin else None


@app.get("/entities/{label}")
async def get_entity_transforms(label):
    plugin = await Registry.get_plugin(label)
    if plugin := plugin():
        return plugin.transform_labels
    return []
