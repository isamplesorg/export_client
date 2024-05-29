/**
 * Bundled by jsDelivr using Rollup v2.79.1 and Terser v5.19.2.
 * Original file: /npm/leaflet-spin@1.1.2/leaflet.spin.js
 *
 * Do NOT use SRI with dynamically generated files! More information: https://www.jsdelivr.com/using-sri-with-dynamic-files
 */
import n from"../leaflet@1.9.4/_esm.js";import i from"../spin.js@2.3.2/_esm.js";var t={exports:{}},s=t.exports=function(t,s){return void 0===t&&(t=n),void 0===s&&(s=i),function(n,i){var t={spin:function(n,t){n?(this._spinner||(this._spinner=new i(t).spin(this._container),this._spinning=0),this._spinning++):(this._spinning--,this._spinning<=0&&this._spinner&&(this._spinner.stop(),this._spinner=null))}},s=function(){this.on("layeradd",(function(n){n.layer.loading&&this.spin(!0),"function"==typeof n.layer.on&&(n.layer.on("data:loading",(function(){this.spin(!0)}),this),n.layer.on("data:loaded",(function(){this.spin(!1)}),this))}),this),this.on("layerremove",(function(n){n.layer.loading&&this.spin(!1),"function"==typeof n.layer.on&&(n.layer.off("data:loaded"),n.layer.off("data:loading"))}),this)};n.Map.include(t),n.Map.addInitHook(s)}(t,s),t};export{s as default};
