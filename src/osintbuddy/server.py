import sys, os
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from osintbuddy import __version__, Use, Registry
from osintbuddy.plugins import load_plugins
from osintbuddy.utils.deps import get_driver

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
    Registry.labels = []
    Registry.plugins = []
    Registry.ui_labels = []
    load_plugins()
    return Registry.ui_labels


@app.get("/blueprint")
async def get_entity_blueprint(label: str):
    plugin = await Registry.get_plugin(label)
    return plugin.create() if plugin else []


@app.get("/transforms")
async def get_entity_transforms(label: str):
    plugin = await Registry.get_plugin(label)
    if plugin := plugin():
        return plugin.transform_labels
    return []


@app.post("/transforms")
async def run_entity_transform(context: dict):
    plugin = await Registry.get_plugin(context['data'].get("label"))
    if entity := plugin():
        transform_result = await entity.run_transform(
            transform_type=context.get("transform"),
            entity=context,
            use=Use(get_driver=get_driver)
        )
        return transform_result
    return []
