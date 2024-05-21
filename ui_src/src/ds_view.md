# View Dataset

```js
/* 
This part is a bit hacky and will likely change. 
Basically, we want to use page_url#data_location to identify the data source for the page
The DuckDB client wants an absolute url, but for convenience we just want to include the path to the file
 */
const data_root = `${document.location.protocol}//${document.location.host}`;
const page_data_source = document.location.hash;
let source_url = `http://localhost:8080/example/test/isamples_export_geo.parquet`;

if (document.location.hash) {
    let _source_url = document.location.hash.substring(1);
    if (!_source_url.startsWith("http")) {
        if (!_source_url.startsWith("/")) {
            _source_url = `/${_source_url}`;
        }
        source_url = `${data_root}${_source_url}`;
    } else {
        source_url = _source_url;
    }
}
```

```js
/*
Setup the data source, which is an instance of the Sample class defined in ./sample.js
 */
import {Samples} from './sample.js';
const db = await DuckDBClient.of();
const samples = new Samples(db)
await samples.init(source_url);
```

This resource is loaded from:

${source_url} 

and contains ${samples.totalRecords} records.


```js
import * as L from "npm:leaflet";
import * as glify from "npm:leaflet.glify";
import * as spin from "npm:leaflet-spin";

```
```js

const div = display(document.createElement("div"));
div.style = "height: 600px;";

const map = L.map(div)
  .setView([0, 0], 2);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
})
  .addTo(map);

////

const sourcemap = {
  "GEOME":0,
  "SMITHSONIAN":1,
  "OPENCONTEXT":2,
  "SESAR":3
}

const colormap = {
  0: {r:1,g:1,b:0,a:0.1},
  1: {r:0,g:1,b:0,a:0.1},
  2: {r:1.0,g:0.5,b:0,a:0.1},
  3: {r:0.5,g:0,b:1,a:0.1},
}

let records_table = Inputs.table([{}]);

const clicked_point = Inputs.text({
    label:"Clicked PID",
    placeholder:"",
    value:"",
  });

let data_points = [];

let glify_points = glify.glify.points({
    map:map,
        size: (i) => {
            return 10;
        },
        color: (i) => {
          return colormap[data_points[i][2]];
        },
    data: data_points,
    click: (e, p, xy) => {
      console.log(p);
      clicked_point.value = p[3];
      samples.getRecordsById(p[3]).then((rows) => {
          records_table = Inputs.table(rows);
          const rdiv = document.getElementById("selected_records");
          rdiv.replaceChildren(records_table);
      }).catch((e) => {
          console.log("Unable to load points:");
          console.log(e);
      });
      clicked_point.dispatchEvent(new Event("input", {bubbles: true}));
    }
  });


async function renderNewBounds() {
    const maxx = map.getBounds().getEast();
    const minx = map.getBounds().getWest();
    const miny = map.getBounds().getSouth();
    const maxy = map.getBounds().getNorth();
    let bb = [minx, miny, maxx, maxy];
    const zoom = map.getZoom();
    //glify_points.remove();
    data_points.length = 0;
    samples.getRecordsByBB(bb).then((pts) => {
        for (const p of pts) {
            data_points.push([p.y, p.x, sourcemap[p.source], p.pid]);
        }
        glify_points.render();
    });
}

renderNewBounds();
```

${clicked_point}

Selected:

<div id="selected_records">
${records_table}
</div>

