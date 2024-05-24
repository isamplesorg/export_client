/**
 * Bundled by jsDelivr using Rollup v2.79.1 and Terser v5.19.2.
 * Original file: /npm/@radiantearth/stac-migrate@1.6.0/migrate.js
 *
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
import e from"../../compare-versions@3.6.0/_esm.js";var t=e;const s="1.0.0",i={classification:"https://stac-extensions.github.io/classification/v1.1.0/schema.json",datacube:"https://stac-extensions.github.io/datacube/v2.1.0/schema.json",eo:"https://stac-extensions.github.io/eo/v1.0.0/schema.json",file:"https://stac-extensions.github.io/file/v1.0.0/schema.json","item-assets":"https://stac-extensions.github.io/item-assets/v1.0.0/schema.json",label:"https://stac-extensions.github.io/label/v1.0.1/schema.json",pointcloud:"https://stac-extensions.github.io/pointcloud/v1.0.0/schema.json",processing:"https://stac-extensions.github.io/processing/v1.1.0/schema.json",projection:"https://stac-extensions.github.io/projection/v1.0.0/schema.json",raster:"https://stac-extensions.github.io/raster/v1.1.0/schema.json",sar:"https://stac-extensions.github.io/sar/v1.0.0/schema.json",sat:"https://stac-extensions.github.io/sat/v1.0.0/schema.json",scientific:"https://stac-extensions.github.io/scientific/v1.0.0/schema.json",table:"https://stac-extensions.github.io/table/v1.2.0/schema.json",timestamps:"https://stac-extensions.github.io/timestamps/v1.0.0/schema.json",version:"https://stac-extensions.github.io/version/v1.0.0/schema.json",view:"https://stac-extensions.github.io/view/v1.0.0/schema.json"},r={itemAndCollection:{"cube:":i.datacube,"eo:":i.eo,"file:":i.file,"label:":i.label,"pc:":i.pointcloud,"processing:":i.processing,"proj:":i.projection,"raster:":i.raster,"sar:":i.sar,"sat:":i.sat,"sci:":i.scientific,"view:":i.view,version:i.version,deprecated:i.version,published:i.timestamps,expires:i.timestamps,unpublished:i.timestamps},catalog:{},collection:{item_assets:i["item-assets"]},item:{}};r.collection=Object.assign(r.collection,r.itemAndCollection),r.item=Object.assign(r.item,r.itemAndCollection);var a={parseUrl(e){let t=e.match(/^https?:\/\/stac-extensions.github.io\/([^\/]+)\/v([^\/]+)\/[^.]+.json$/i);if(t)return{id:t[1],version:t[2]}}},n={version:s,extensions:{},set(e){if("string"!=typeof e.stac_version?n.version="0.6.0":n.version=e.stac_version,Array.isArray(e.stac_extensions))for(let t of e.stac_extensions){let e=a.parseUrl(t);e&&(n.extensions[e.id]=e.version)}},before(e,s=null){let i=s?n.extensions[s]:n.version;return void 0!==i&&t.compare(i,e,"<")}},o={type(e){let t=typeof e;if("object"===t){if(null===e)return"null";if(Array.isArray(e))return"array"}return t},is:(e,t)=>o.type(e)===t,isDefined:e=>void 0!==e,isObject:e=>"object"==typeof e&&e===Object(e)&&!Array.isArray(e),rename:(e,t,s)=>void 0!==e[t]&&void 0===e[s]&&(e[s]=e[t],delete e[t],!0),forAll(e,t,s){if(e[t]&&"object"==typeof e[t])for(let i in e[t])s(e[t][i])},toArray:(e,t)=>void 0!==e[t]&&!Array.isArray(e[t])&&(e[t]=[e[t]],!0),flattenArray(e,t,s,i=!1){if(Array.isArray(e[t])){for(let r in e[t])if("string"==typeof s[r]){let a=e[t][r];e[s[r]]=i?[a]:a}return delete e[t],!0}return!1},flattenOneElementArray:(e,t,s=!1)=>!(!s&&Array.isArray(e[t]))||1===e[t].length&&(e[t]=e[t][0],!0),removeFromArray(e,t,s){if(Array.isArray(e[t])){let i=e[t].indexOf(s);return i>-1&&e[t].splice(i,1),!0}return!1},ensure:(e,t,s)=>(o.type(s)!==o.type(e[t])&&(e[t]=s),!0),upgradeExtension(e,s){let{id:i,version:r}=a.parseUrl(s),n=e.stac_extensions.findIndex((e=>{let s=a.parseUrl(e);return s&&s.id===i&&t.compare(s.version,r,"<")}));return-1!==n&&(e.stac_extensions[n]=s,!0)},addExtension(e,s){let{id:i,version:r}=a.parseUrl(s),n=e.stac_extensions.findIndex((e=>{if(e===s)return!0;let n=a.parseUrl(e);return!(!n||n.id!==i||!t.compare(n.version,r,"<"))}));return-1===n?e.stac_extensions.push(s):e.stac_extensions[n]=s,e.stac_extensions.sort(),!0},removeExtension:(e,t)=>o.removeFromArray(e,"stac_extensions",t),migrateExtensionShortnames(e){let t=Object.keys(i),s=Object.values(i);return o.mapValues(e,"stac_extensions",t,s)},populateExtensions(e,t){let s=[];"catalog"!=t&&"collection"!=t||s.push(e),"item"!=t&&"collection"!=t||!o.isObject(e.assets)||(s=s.concat(Object.values(e.assets))),"collection"==t&&o.isObject(e.item_assets)&&(s=s.concat(Object.values(e.item_assets))),"collection"==t&&o.isObject(e.summaries)&&s.push(e.summaries),"item"==t&&o.isObject(e.properties)&&s.push(e.properties);for(let i of s)Object.keys(i).forEach((s=>{let i=s.match(/^(\w+:|[^:]+$)/i);if(Array.isArray(i)){let s=r[t][i[0]];o.is(s,"string")&&o.addExtension(e,s)}}))},mapValues(e,t,s,i){let r=e=>{let t=s.indexOf(e);return t>=0?i[t]:e};return Array.isArray(e[t])?e[t]=e[t].map(r):void 0!==e[t]&&(e[t]=r(e[t])),!0},mapObject(e,t){for(let s in e)e[s]=t(e[s],s)},moveTo(e,t,s,i=!1,r=!1){let a;return a=i?r?e=>Array.isArray(e):e=>Array.isArray(e)&&1===e.length:o.isDefined,!!a(e[t])&&(s[t]=i&&!r?e[t][0]:e[t],delete e[t],!0)},runAll(e,t,s,i){for(let r in e)r.startsWith("migrate")||e[r](t,s,i)},toUTC(e,t){if("string"==typeof e[t])try{return e[t]=this.toISOString(e[t]),!0}catch(e){}return delete e[t],!1},toISOString:e=>(e instanceof Date||(e=new Date(e)),e.toISOString().replace(".000",""))},l={multihash:null,hexToUint8(e){if(0===e.length||e.length%2!=0)throw new Error(`The string "${e}" is not valid hex.`);return new Uint8Array(e.match(/.{1,2}/g).map((e=>parseInt(e,16))))},uint8ToHex:e=>e.reduce(((e,t)=>e+t.toString(16).padStart(2,"0")),""),toMultihash(e,t,s){if(!l.multihash||!o.is(e[t],"string"))return!1;try{const i=l.multihash.encode(l.hexToUint8(e[t]),s);return e[t]=l.uint8ToHex(i),!0}catch(e){return console.warn(e),!1}}},c={migrate:(e,t=!0)=>(n.set(e),t&&(e.stac_version=s),e.type="Catalog",o.ensure(e,"stac_extensions",[]),n.before("1.0.0-rc.1")&&o.migrateExtensionShortnames(e),o.ensure(e,"id",""),o.ensure(e,"description",""),o.ensure(e,"links",[]),o.runAll(c,e,e),n.before("0.8.0")&&o.populateExtensions(e,"catalog"),e)},m={migrate:(e,t=!0)=>(c.migrate(e,t),e.type="Collection",n.before("1.0.0-rc.1")&&o.migrateExtensionShortnames(e),o.ensure(e,"license","proprietary"),o.ensure(e,"extent",{spatial:{bbox:[]},temporal:{interval:[]}}),o.runAll(m,e,e),o.isObject(e.properties)&&(o.removeFromArray(e,"stac_extensions","commons"),delete e.properties),n.before("0.8.0")&&o.populateExtensions(e,"collection"),n.before("1.0.0-beta.1")&&o.mapValues(e,"stac_extensions",["assets"],["item-assets"]),e),extent(e){if(o.ensure(e,"extent",{}),n.before("0.8.0")&&(Array.isArray(e.extent.spatial)&&(e.extent.spatial={bbox:[e.extent.spatial]}),Array.isArray(e.extent.temporal)&&(e.extent.temporal={interval:[e.extent.temporal]})),o.ensure(e.extent,"spatial",{}),o.ensure(e.extent.spatial,"bbox",[]),o.ensure(e.extent,"temporal",{}),o.ensure(e.extent.temporal,"interval",[]),n.before("1.0.0-rc.3")){if(e.extent.temporal.interval.length>1){let t,s;for(let i of e.extent.temporal.interval){if(null===i[0])t=null;else if("string"==typeof i[0]&&null!==t)try{let e=new Date(i[0]);(void 0===t||e<t)&&(t=e)}catch(e){}if(null===i[1])s=null;else if("string"==typeof i[1]&&null!==s)try{let e=new Date(i[1]);(void 0===s||e>s)&&(s=e)}catch(e){}}e.extent.temporal.interval.unshift([t?o.toISOString(t):null,s?o.toISOString(s):null])}if(e.extent.spatial.bbox.length>1){let t=e.extent.spatial.bbox.reduce(((e,t)=>Array.isArray(t)?Math.max(t.length,e):e),4);if(t>=4){let s=new Array(t).fill(null),i=t/2;for(let t of e.extent.spatial.bbox){if(!Array.isArray(t)||t.length<4)break;for(let e in t){let r=t[e];null===s[e]?s[e]=r:s[e]=e<i?Math.min(r,s[e]):Math.max(r,s[e])}}-1===s.findIndex((e=>null===e))&&e.extent.spatial.bbox.unshift(s)}}}},collectionAssets(e){n.before("1.0.0-rc.1")&&o.removeExtension(e,"collection-assets"),d.migrateAll(e)},itemAsset(e){n.before("1.0.0-beta.2")&&o.rename(e,"item_assets","assets"),d.migrateAll(e,"item_assets")},summaries(e){if(o.ensure(e,"summaries",{}),n.before("0.8.0")&&o.isObject(e.other_properties)){for(let t in e.other_properties){let s=e.other_properties[t];Array.isArray(s.extent)&&2===s.extent.length?e.summaries[t]={minimum:s.extent[0],maximum:s.extent[1]}:Array.isArray(s.values)&&(s.values.filter((e=>Array.isArray(e))).length===s.values.length?e.summaries[t]=s.values.reduce(((e,t)=>e.concat(t)),[]):e.summaries[t]=s.values)}delete e.other_properties}if(n.before("1.0.0-beta.1")&&o.isObject(e.properties)&&!e.links.find((e=>["child","item"].includes(e.rel))))for(let t in e.properties){let s=e.properties[t];Array.isArray(s)||(s=[s]),e.summaries[t]=s}n.before("1.0.0-rc.1")&&o.mapObject(e.summaries,(e=>(o.rename(e,"min","minimum"),o.rename(e,"max","maximum"),e))),f.migrate(e.summaries,e,!0),o.moveTo(e.summaries,"sci:doi",e,!0)&&o.addExtension(e,i.scientific),o.moveTo(e.summaries,"sci:publications",e,!0,!0)&&o.addExtension(e,i.scientific),o.moveTo(e.summaries,"sci:citation",e,!0)&&o.addExtension(e,i.scientific),o.moveTo(e.summaries,"cube:dimensions",e,!0)&&o.addExtension(e,i.datacube),0===Object.keys(e.summaries).length&&delete e.summaries}},u={migrate(e,t=null,i=!0){n.set(e),i&&(e.stac_version=s),o.ensure(e,"stac_extensions",[]),n.before("1.0.0-rc.1")&&o.migrateExtensionShortnames(e),o.ensure(e,"id",""),o.ensure(e,"type","Feature"),o.isObject(e.geometry)||(e.geometry=null),null!==e.geometry&&o.ensure(e,"bbox",[]),o.ensure(e,"properties",{}),o.ensure(e,"links",[]),o.ensure(e,"assets",{});let r=!1;return o.isObject(t)&&o.isObject(t.properties)&&(o.removeFromArray(e,"stac_extensions","commons"),e.properties=Object.assign({},t.properties,e.properties),r=!0),o.runAll(u,e,e),f.migrate(e.properties,e),d.migrateAll(e),(n.before("0.8.0")||r)&&o.populateExtensions(e,"item"),e}},p={migrate:(e,t=!0)=>(o.ensure(e,"collections",[]),o.ensure(e,"links",[]),o.runAll(p,e,e),e.collections=e.collections.map((e=>m.migrate(e,t))),e)},h={migrate:(e,t=!0)=>(o.ensure(e,"type","FeatureCollection"),o.ensure(e,"features",[]),o.ensure(e,"links",[]),o.runAll(h,e,e),e.features=e.features.map((e=>u.migrate(e,null,t))),e)},d={migrateAll(e,t="assets"){for(let s in e[t])d.migrate(e[t][s],e)},migrate:(e,t)=>(o.runAll(d,e,t),f.migrate(e,t),e),mediaTypes(e){o.is(e.type,"string")&&o.mapValues(e,"type",["image/vnd.stac.geotiff","image/vnd.stac.geotiff; cloud-optimized=true"],["image/tiff; application=geotiff","image/tiff; application=geotiff; profile=cloud-optimized"])},eo(e,t){let s=o.isObject(t.properties)&&Array.isArray(t.properties["eo:bands"])?t.properties["eo:bands"]:[];if(Array.isArray(e["eo:bands"]))for(let t in e["eo:bands"]){let i=e["eo:bands"][t];o.is(i,"number")&&o.isObject(s[i])?i=s[i]:o.isObject(i)||(i={}),e["eo:bands"][t]=i}}},f={migrate:(e,t,s=!1)=>(o.runAll(f,e,t,s),e),_commonMetadata(e){n.before("1.0.0-rc.3")&&(o.toUTC(e,"created"),o.toUTC(e,"updated"))},_timestamps(e,t){o.toUTC(e,"published"),o.toUTC(e,"expires"),o.toUTC(e,"unpublished"),o.upgradeExtension(t,i.timestamps)},_versioningIndicator(e,t){o.upgradeExtension(t,i.version)},checksum(e,t){n.before("0.9.0")&&l.multihash&&(o.rename(e,"checksum:md5","checksum:multihash")&&l.toMultihash(e,"checksum:multihash","md5"),o.rename(e,"checksum:sha1","checksum:multihash")&&l.toMultihash(e,"checksum:multihash","sha1"),o.rename(e,"checksum:sha2","checksum:multihash")&&l.toMultihash(e,"checksum:multihash","sha2-256"),o.rename(e,"checksum:sha3","checksum:multihash")&&l.toMultihash(e,"checksum:multihash","sha3-256")),n.before("1.0.0-rc.1")&&o.rename(e,"checksum:multihash","file:checksum")&&o.addExtension(t,i.file),o.removeExtension(t,"checksum")},classification(e,t){n.before("1.1.0","classification")&&o.forAll(e,"classification:classes",(e=>o.rename(e,"color-hint","color_hint"))),o.upgradeExtension(t,i.classification)},cube(e,t){o.upgradeExtension(t,i.datacube)},dtr(e,t){n.before("0.9.0")&&(o.rename(e,"dtr:start_datetime","start_datetime"),o.rename(e,"dtr:end_datetime","end_datetime"),o.removeExtension(t,"datetime-range"))},eo(e,t){n.before("0.9.0")&&(o.rename(e,"eo:epsg","proj:epsg")&&o.addExtension(t,i.projection),o.rename(e,"eo:platform","platform"),o.rename(e,"eo:instrument","instruments")&&o.toArray(e,"instruments"),o.rename(e,"eo:constellation","constellation"),o.rename(e,"eo:off_nadir","view:off_nadir")&&o.addExtension(t,i.view),o.rename(e,"eo:azimuth","view:azimuth")&&o.addExtension(t,i.view),o.rename(e,"eo:incidence_angle","view:incidence_angle")&&o.addExtension(t,i.view),o.rename(e,"eo:sun_azimuth","view:sun_azimuth")&&o.addExtension(t,i.view),o.rename(e,"eo:sun_elevation","view:sun_elevation")&&o.addExtension(t,i.view)),n.before("1.0.0-beta.1")&&o.rename(e,"eo:gsd","gsd"),o.upgradeExtension(t,i.eo)},file(e,t){o.upgradeExtension(t,i.file)},label(e,t){n.before("0.8.0")&&(o.rename(e,"label:property","label:properties"),o.rename(e,"label:task","label:tasks"),o.rename(e,"label:overview","label:overviews")&&o.toArray(e,"label:overviews"),o.rename(e,"label:method","label:methods"),o.toArray(e,"label:classes")),o.upgradeExtension(t,i.label)},pc(e,t){n.before("0.8.0")&&o.rename(e,"pc:schema","pc:schemas"),o.upgradeExtension(t,i.pointcloud)},processing(e,t){o.upgradeExtension(t,i.processing)},proj(e,t){o.upgradeExtension(t,i.projection)},raster(e,t){o.upgradeExtension(t,i.raster)},sar(e,t,s){o.rename(e,"sar:incidence_angle","view:incidence_angle")&&o.addExtension(t,i.view),o.rename(e,"sar:pass_direction","sat:orbit_state")&&o.mapValues(e,"sat:orbit_state",[null],["geostationary"])&&o.addExtension(t,i.sat),n.before("0.7.0")&&(o.flattenArray(e,"sar:resolution",["sar:resolution_range","sar:resolution_azimuth"],s),o.flattenArray(e,"sar:pixel_spacing",["sar:pixel_spacing_range","sar:pixel_spacing_azimuth"],s),o.flattenArray(e,"sar:looks",["sar:looks_range","sar:looks_azimuth","sar:looks_equivalent_number"],s),o.rename(e,"sar:off_nadir","view:off_nadir")&&o.addExtension(t,i.view)),n.before("0.9.0")&&(o.rename(e,"sar:platform","platform"),o.rename(e,"sar:instrument","instruments")&&o.toArray(e,"instruments"),o.rename(e,"sar:constellation","constellation"),o.rename(e,"sar:type","sar:product_type"),o.rename(e,"sar:polarization","sar:polarizations"),o.flattenOneElementArray(e,"sar:absolute_orbit",s)&&o.rename(e,"sar:absolute_orbit","sat:absolute_orbit")&&o.addExtension(t,i.sat),o.flattenOneElementArray(e,"sar:relative_orbit",s)&&o.rename(e,"sar:relative_orbit","sat:relative_orbit")&&o.addExtension(t,i.sat)),o.upgradeExtension(t,i.sar)},sat(e,t){n.before("0.9.0")&&(o.rename(e,"sat:off_nadir_angle","sat:off_nadir"),o.rename(e,"sat:azimuth_angle","sat:azimuth"),o.rename(e,"sat:sun_azimuth_angle","sat:sun_azimuth"),o.rename(e,"sat:sun_elevation_angle","sat:sun_elevation")),o.upgradeExtension(t,i.sat)},sci(e,t){o.upgradeExtension(t,i.scientific)},item(e){n.before("0.8.0")&&(o.rename(e,"item:license","license"),o.rename(e,"item:providers","providers"))},table(e,t){o.upgradeExtension(t,i.table)},view(e,t){o.upgradeExtension(t,i.view)}},b={item:(e,t=null,s=!0)=>u.migrate(e,t,s),catalog:(e,t=!0)=>c.migrate(e,t),collection:(e,t=!0)=>m.migrate(e,t),collectionCollection:(e,t=!0)=>p.migrate(e,t),itemCollection:(e,t=!0)=>h.migrate(e,t),stac:(e,t=!0)=>"Feature"===e.type?b.item(e,null,t):"FeatureCollection"===e.type?b.itemCollection(e,t):"Collection"===e.type||!e.type&&o.isDefined(e.extent)&&o.isDefined(e.license)?b.collection(e,t):!e.type&&Array.isArray(e.collections)?b.collectionCollection(e,t):b.catalog(e,t),enableMultihash(e){l.multihash=e}},g=b,x=g.catalog,v=g.collection,y=g.collectionCollection,A=g.enableMultihash,_=g.item,j=g.itemCollection,E=g.stac;export{x as catalog,v as collection,y as collectionCollection,g as default,A as enableMultihash,_ as item,j as itemCollection,E as stac};