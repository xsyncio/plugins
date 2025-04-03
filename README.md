# OSINTBuddy plugins and extensions

The plugins library for [osintbuddy/osintbuddy](https://github.com/osintbuddy/osintbuddy).

## Install

```bash
pip install -e .
ob start
```

## Plugin Example

To make this a bit more clear please see the below example...

```py
from pydantic import BaseModel
import osintbuddy import transform, Plugin
from osintbuddy.elements import TextInput, DropdownInput, Title, CopyText
from osintbuddy.errors import OBPluginError


class CSESearchResults(Plugin):
    label = "CSE Result"
    name = "CSE result"
    show_label = False  # do not show this on the entities dialog 
    # the user sees on the left of the project graph screen
    color = "#058F63"
    node = [
        Title(label="Result"),
        CopyText(label="URL"),
        CopyText(label="Cache URL"),
    ]


class CSESearchPlugin(Plugin):
    label = "CSE Search"
    name = "CSE search"
    color = "#2C7237"
    node = [
        [
            TextInput(label="Query", icon="search"),
            TextInput(label="Pages", icon="123", default="1"),
        ],
        DropdownInput(label="CSE Categories", options=cse_link_options)
    ]

    @transform(label="To cse results", icon="search")
    async def transform_to_cse_results(
      self,
      node: BaseModel,  # dynamically generated pydantic model 
      # that is mapped from the above labels contained within `node`
      use  # a pydantic model allowing you to access a selenium instance
      # (and eventually a gremlin graph and settings api) 
    ):
        results = []

        if not node.query:
          raise OBPluginError((
            'You can send error messages to the user here'
            'if they forget to submit data or if some other error occurs'
          ))

        # notice how you can access data returned from the context menu
        # of this node; using the label name in snake case
        print(node.cse_categories, node.query, node.pages) 

        ... # (removed code for clarity)

        if resp:
            for result in resp["results"]:
                url = result.get("breadcrumbUrl", {})
                # some elements you can store more than just a string,
                # (these elements storing dicts are mapped 
                # to janusgraph as properties with the names
                # result_title, result_subtitle, and result_text)
                blueprint = CSESearchResults.blueprint(
                    result={
                        "title": result.get("titleNoFormatting"),
                        "subtitle": url.get("host") + url.get("crumbs"),
                        "text": result.get("contentNoFormatting"),
                    },
                    url=result.get("unescapedUrl"),
                    cache_url=result.get("cacheUrl"),
                )
                results.append(blueprint)
        # here we return a list of blueprints (blueprints are dicts)
        # but you can also return a single blueprint without a list
        return results

```


