<p align="center">
  <h1 align="center">osintbuddy‑plugins</h1>
  <p align="center"><strong>Alpha:</strong> Expect breaking changes 🚧</p>
</p>

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [How It Works](#how-it-works)
4. [Plugin Example](#plugin-example)
5. [CLI Commands](#cli-commands)
6. [Roadmap & TODO](#roadmap--todo)

---

## Overview

`osintbuddy-plugins` is the plugin framework powering the [osintbuddy](https://github.com/osintbuddy/osintbuddy) application. It provides:

* A **`Registry`** for discovering and registering `Plugin` classes
* A simple decorator (`@transform`) to expose data‑transformation methods
* Automatic mapping of returned “blueprints” into an Apache AGE / PostgreSQL graph

> **Alpha Warning:** The API is still settling—breaking changes may occur.

---

## Installation

```bash
# In development mode, with auto‑reload
pip install -e .
ob start
```

---

## How It Works

1. **Registry**
   A central `Registry` holds all `Plugin` subclasses.

2. **Discovery**
   On `ob start`, the `osintbuddy` plugins service loads the registry and exposes:

   * **Entities**: types you can add to your project graph
   * **Transforms**: context‑menu actions on each node

3. **Execution**
   Each `@transform` method returns one or more “blueprints”—plain dicts containing data.
   These are then persisted to the AGE/PostgreSQL graph, with node labels derived from your plugin’s `node` schema.

---

## Plugin Example

```python
import osintbuddy
from pydantic import BaseModel
from osintbuddy import Plugin, transform
from osintbuddy.elements import TextInput, DropdownInput, Title, CopyText
from osintbuddy.errors import OBPluginError

class CSESearchResults(Plugin):
    label        = "CSE Result"
    name         = "CSE result"
    is_available = False
    color        = "#058F63"
    node         = [
        Title(label="Result"),
        CopyText(label="URL"),
        CopyText(label="Cache URL"),
    ]

class CSESearchPlugin(Plugin):
    label = "CSE Search"
    name  = "CSE search"
    color = "#2C7237"
    node  = [
        [
            TextInput(label="Query", icon="search"),
            TextInput(label="Pages", icon="123", default="1"),
        ],
        DropdownInput(label="CSE Categories", options=cse_link_options),
    ]

    @transform(label="To CSE Results", icon="search")
    async def transform_to_cse_results(
        self,
        node: BaseModel,      # auto‑generated model for inputs
        use: BaseModel,       # provides selenium & graph context
    ):
        """
        Fetches search results from a CSE and returns them as blueprints.

        Parameters
        ----------
        node : BaseModel
            Contains `query`, `pages`, and `cse_categories` fields.
        use : BaseModel
            Context model giving access to Selenium and graph APIs.

        Returns
        -------
        List[dict]
            A list of blueprints for CSESearchResults nodes.
        """
        if not node.query:
            raise OBPluginError(
                "Please provide a search query."
            )

        # ... perform your HTTP or Selenium calls here ...

        results = []
        for item in resp["results"]:
            blueprint = CSESearchResults.create(
                result={
                    "title": item["titleNoFormatting"],
                    "subtitle": item["breadcrumbUrl"]["host"] + item["breadcrumbUrl"]["crumbs"],
                    "text": item["contentNoFormatting"],
                },
                url=item["unescapedUrl"],
                cache_url=item["cacheUrl"],
            )
            results.append(blueprint)

        return results
```

---

## CLI Commands

| Command    | Description                      |
| ---------- | -------------------------------- |
| `ob start` | Launch plugin service            |
| `ob init`  | Initialize a new plugin template |

---

## Roadmap & TODO

* [ ] Document full CLI usage
* [ ] Add Git‑based plugin loading
* [ ] Support multiple Selenium drivers
* [ ] Provide a Playwright plugin example

---

<sub>Built with ♥ for the OSINT community.</sub>
