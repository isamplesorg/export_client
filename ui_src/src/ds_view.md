<link rel="stylesheet" href="styles.css">
<link rel="stylesheet" href="npm:leaflet/dist/leaflet.css">
# View Dataset

```js
import * as duckdb from "npm:@duckdb/duckdb-wasm";
let default_data_source = "http://localhost:8000/data/test/isamples_export_geo.parquet";
if (location.hash) {
    default_data_source = new URL(document.location.hash.substring(1), location).href;
}
const source_url = view(Inputs.textarea({value:default_data_source, submit:true}));
```

```js
/*
Setup the data source, which is an instance of the Sample class defined in ./sample.js
 */
const sourceErrorMessage = (msg) => {
    const ele = document.getElementById("error_notice");
    if (ele) {
        if (msg) {
            ele.innerText = msg;
        } else {
            ele.remove();
        }
    } else {
        if (msg) {
            display(html`<div id="error_notice" class="caution" label="Error">${msg}</div>`);
        }
    }
    
}

import {Samples} from './sample.js';
const db = await DuckDBClient.of();
const samples = new Samples(db)
try {
    sourceErrorMessage("");
    await samples.init(source_url);
} catch (e) {
    sourceErrorMessage(html`Unable to load resource from: ${source_url}<br /><code>${e}</code>`);
    console.log(e);
}
```

The dataset resource contains ${samples.totalRecords} records.

Material type:

${Inputs.table(samples.vocabularyTermCounts())}

```js
import * as L from "npm:leaflet";
import * as glify from "npm:leaflet.glify";
```

```js

const div = display(document.createElement("div"));
div.style = "height: 600px;";

const map = L.map(div)
  .setView([0, 0], 2);
L.DomUtil.addClass(map._container,'crosshair-cursor-enabled');
const osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
});
osm.addTo(map); 

const mapLink = '<a href="http://www.esri.com/">Esri</a>';
const wholink = 'i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community';
const esri = L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
    {
        attribution: '&copy; '+mapLink+', '+wholink,
        maxZoom: 18,
    });
const baseMaps = {
    "OpenStreetMap": osm,
    "ESRI Satellite": esri 
}
const layerControl = L.control.layers(baseMaps).addTo(map);
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

const tableOptions = {
    format:{
        "sample_identifier": (v) => {
            return html`<a href="https://n2t.net/${v}">${v}</a>`;
        }
    }
}

let records_table = Inputs.table([{}]);

const clicked_point = Inputs.text({
    label:"Clicked PID",
    placeholder:"",
    value:"",
  });

let data_points = [];
let tooltip = new L.Tooltip();

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
          records_table = Inputs.table(rows, tableOptions);
          const rdiv = document.getElementById("selected_records");
          rdiv.replaceChildren(records_table);
      }).catch((e) => {
          console.log("Unable to load points:");
          console.log(e);
      });
      clicked_point.dispatchEvent(new Event("input", {bubbles: true}));
    },
    hover: (e, feature) => {
        console.log(feature);
        tooltip
            .setLatLng(e.latlng)
            .setContent(feature[3])
            .addTo(map);
    }
  });


async function renderNewBounds() {
    const maxx = map.getBounds().getEast();
    const minx = map.getBounds().getWest();
    const miny = map.getBounds().getSouth();
    const maxy = map.getBounds().getNorth();
    let bb = [minx, miny, maxx, maxy];
    //Override and get all points for now
    //TODO: This should be dynamically loading points based on the view extents.
    bb = [-180, -90, 180, 90];
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

