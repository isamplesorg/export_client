# iSamples Export View

```js
import { Collection } from 'npm:stac-js';
import markdownit from "npm:markdown-it";
```
```js
const Markdown = new markdownit({html: true});

function md(strings) {
  let string = strings[0];
  for (let i = 1; i < arguments.length; ++i) {
    string += String(arguments[i]);
    string += strings[i];
  }
  const template = document.createElement("template");
  template.innerHTML = Markdown.render(string);
  return template.content.cloneNode(true);
}

async function loadCatalog(url) {
    const data = await fetch(url).then((response) => response.json());
    return new Collection(data, url);
}

function listDatasets(source) {
    const datasets = [];
    for (const item of source.links) {
        if (item.rel === "child") {
            datasets.push({
                "Title":item.title,
                "Link": item.href
            })
        }
    }
    return datasets;
}

const collection = await loadCatalog("http://localhost:8000/data/stac.json");



```
${collection.title}

${collection.type} ${collection.stac_version}

${md`${collection.description}`}

Datasets:

${Inputs.table(listDatasets(collection))}

---

<pre>
${JSON.stringify(collection, null, 2)}
</pre>