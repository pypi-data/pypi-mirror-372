const { AssetstoreType: U } = girder.constants;
U.DICOMWEB = "dicomweb";
const J = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null
}, Symbol.toStringTag, { value: "Module" }));
function D(r, e, s, o) {
  if (!(r instanceof Error)) throw r;
  if (!(typeof window > "u" && e || o)) throw r.message += " on line " + s, r;
  var u, t, i, F;
  try {
    o = o || require("fs").readFileSync(e, { encoding: "utf8" }), u = 3, t = o.split(`
`), i = Math.max(s - u, 0), F = Math.min(t.length, s + u);
  } catch (c) {
    return r.message += " - could not read from " + e + " (" + c.message + ")", void D(r, null, s);
  }
  u = t.slice(i, F).map(function(c, d) {
    var p = d + i + 1;
    return (p == s ? "  > " : "    ") + p + "| " + c;
  }).join(`
`), r.path = e;
  try {
    r.message = (e || "Pug") + ":" + s + `
` + u + `

` + r.message;
  } catch {
  }
  throw r;
}
function z(r) {
  var e = "", s, o;
  try {
    o = 1, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<div class="g-body-title">', o = 1, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "Import references to DICOM objects on a DICOMweb Server</div>", o = 3, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<div class="g-import-instructions">', o = 4, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "Use this page to import references to DICOM objects on a DICOMweb server", o = 5, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + `
`, o = 5, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "into the girder assetstore system. An existing folder must be used as the", o = 6, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + `
`, o = 6, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "destination for the DICOM references.", o = 7, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + `
`, o = 7, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "</div>", o = 8, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<form class="g-dwas-import-form">', o = 9, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<div class="form-group">', o = 10, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<label for="g-dwas-import-dest-type">', o = 10, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "Destination type</label>", o = 11, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<select class="form-control" id="g-dwas-import-dest-type">', o = 12, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<option value="folder" selected="selected">', o = 12, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "Folder</option>", o = 13, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<option value="user">', o = 13, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "User</option>", o = 14, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<option value="collection">', o = 14, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "Collection</option></select></div>", o = 15, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<div class="form-group">', o = 16, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<label for="g-dwas-import-dest-id">', o = 16, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "Destination ID</label>", o = 17, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<div class="input-group input-group-sm">', o = 18, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<input class="form-control input-sm" id="g-dwas-import-dest-id" type="text" placeholder="Existing folder, user, or collection ID to use as the destination"/>', o = 21, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<div class="input-group-btn">', o = 22, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<button class="g-open-browser btn btn-default" type="button">', o = 23, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<i class="icon-folder-open"></i></button></div></div>', o = 24, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<label for="g-dwas-import-limit">', o = 24, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "Limit (Studies)</label>", o = 25, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<input class="form-control" id="g-dwas-import-limit" type="number" step="1" min="1" value="10"/>', o = 27, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<label for="g-dwas-import-filters">', o = 27, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "Filters (Studies)</label>", o = 28, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<textarea class="form-control" id="g-dwas-import-filters" rows="10">', o = 29, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "{", o = 30, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + `
`, o = 30, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '    "ModalitiesInStudy": "SM"', o = 31, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + `
`, o = 31, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + "}</textarea></div>", o = 32, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<div class="g-validation-failed-message"></div>', o = 33, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<button class="g-submit-assetstore-import btn btn-success" type="submit">', o = 34, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + '<i class="icon-link-ext"></i>', o = 35, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/assetstoreImport.pug", e = e + " Begin import</button></form>";
  } catch (u) {
    D(u, s, o);
  }
  return e;
}
const O = girder.$, L = girder.views.widgets.BrowserWidget, R = girder.router, { View: Q } = girder.views, { restRequest: G } = girder.rest, { assetstoreImportViewMap: k } = girder.views.body, { AssetstoreType: H } = girder.constants, S = Q.extend({
  events: {
    "submit .g-dwas-import-form": function(r) {
      r.preventDefault(), this.$(".g-validation-failed-message").empty();
      const e = this.$("#g-dwas-import-dest-type").val(), s = this.$("#g-dwas-import-dest-id").val().trim().split(/\s/)[0], o = this.$("#g-dwas-import-filters").val().trim(), u = this.$("#g-dwas-import-limit").val().trim();
      if (!s) {
        this.$(".g-validation-failed-message").html("Invalid Destination ID");
        return;
      }
      this.$(".g-submit-dwas-import").addClass("disabled"), this.assetstore.off().on("g:imported", function() {
        R.navigate(e + "/" + s, { trigger: !0 });
      }, this).on("g:error", function(t) {
        this.$(".g-submit-dwas-import").removeClass("disabled"), this.$(".g-validation-failed-message").html(t.responseJSON.message);
      }, this).import({
        destinationId: s,
        destinationType: e,
        limit: u,
        filters: o,
        progress: !0
      });
    },
    "click .g-open-browser": "_openBrowser"
  },
  initialize: function(r) {
    this._browserWidgetView = new L({
      parentView: this,
      titleText: "Destination",
      helpText: "Browse to a location to select it as the destination.",
      submitText: "Select Destination",
      validate: function(e) {
        const s = O.Deferred();
        return e ? s.resolve() : s.reject("Please select a valid root."), s.promise();
      }
    }), this.listenTo(this._browserWidgetView, "g:saved", function(e) {
      this.$("#g-dwas-import-dest-id").val(e.id);
      const o = this._browserWidgetView._hierarchyView.parentModel.get("_modelType");
      this.$("#g-dwas-import-dest-type").val(o), G({
        url: `resource/${e.id}/path`,
        method: "GET",
        data: { type: o }
      }).done((u) => {
        this.$("#g-dwas-import-dest-id").val() === e.id && this.$("#g-dwas-import-dest-id").val(`${e.id} (${u})`);
      });
    }), this.assetstore = r.assetstore, this.render();
  },
  render: function() {
    return this.$el.html(z({
      assetstore: this.assetstore
    })), this;
  },
  _openBrowser: function() {
    this._browserWidgetView.setElement(O("#g-dialog-container")).render();
  }
});
k && (k[H.DICOMWEB] = S);
function K(r, e, s, o) {
  if (e === !1 || e == null || !e && r === "style") return "";
  if (e === !0) return " " + (r + '="' + r + '"');
  var u = typeof e;
  return u !== "object" && u !== "function" || typeof e.toJSON != "function" || (e = e.toJSON()), typeof e == "string" || (e = JSON.stringify(e), s) ? (e = X(e), " " + r + '="' + e + '"') : " " + r + "='" + e.replace(/'/g, "&#39;") + "'";
}
function X(r) {
  var e = "" + r, s = Y.exec(e);
  if (!s) return r;
  var o, u, t, i = "";
  for (o = s.index, u = 0; o < e.length; o++) {
    switch (e.charCodeAt(o)) {
      case 34:
        t = "&quot;";
        break;
      case 38:
        t = "&amp;";
        break;
      case 60:
        t = "&lt;";
        break;
      case 62:
        t = "&gt;";
        break;
      default:
        continue;
    }
    u !== o && (i += e.substring(u, o)), u = o + 1, i += t;
  }
  return u !== o ? i + e.substring(u, o) : i;
}
var Y = /["&<>]/;
function T(r, e, s, o) {
  if (!(r instanceof Error)) throw r;
  if (!(typeof window > "u" && e || o)) throw r.message += " on line " + s, r;
  var u, t, i, F;
  try {
    o = o || require("fs").readFileSync(e, { encoding: "utf8" }), u = 3, t = o.split(`
`), i = Math.max(s - u, 0), F = Math.min(t.length, s + u);
  } catch (c) {
    return r.message += " - could not read from " + e + " (" + c.message + ")", void T(r, null, s);
  }
  u = t.slice(i, F).map(function(c, d) {
    var p = d + i + 1;
    return (p == s ? "  > " : "    ") + p + "| " + c;
  }).join(`
`), r.path = e;
  try {
    r.message = (e || "Pug") + ":" + s + `
` + u + `

` + r.message;
  } catch {
  }
  throw r;
}
function Z(r) {
  var e = "", s, o;
  try {
    var u = r || {};
    (function(t) {
      o = 1, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreImportButton.pug", e = e + '<div class="g-assetstore-import-button-container">', o = 2, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreImportButton.pug", e = e + "<a" + (' class="g-dwas-import-button btn btn-sm btn-success"' + K("href", `#assetstore/${t.get("_id")}/import`, !0, !1) + ' title="Import references to DICOM objects from a DICOMweb server"') + ">", o = 5, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreImportButton.pug", e = e + '<i class="icon-link-ext"></i>', o = 6, s = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreImportButton.pug", e = e + " Import data</a></div>";
    }).call(this, "assetstore" in u ? u.assetstore : typeof assetstore < "u" ? assetstore : void 0);
  } catch (t) {
    T(t, s, o);
  }
  return e;
}
const e0 = girder._, u0 = girder.views.body.AssetstoresView, { AssetstoreType: t0 } = girder.constants, { wrap: o0 } = girder.utilities.PluginUtils;
o0(u0, "render", function(r) {
  r.call(this);
  const e = '.g-assetstore-info-section[assetstore-type="' + t0.DICOMWEB + '"]';
  return e0.each(this.$(e), function(s) {
    const o = this.$(s), u = this.collection.get(o.attr("cid"));
    o.parent().find(".g-assetstore-buttons").append(
      Z({
        assetstore: u
      })
    );
  }, this), this.$(".g-dwas-import-button").tooltip({
    delay: 100
  }), this;
});
const s0 = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null
}, Symbol.toStringTag, { value: "Module" }));
function a(r, e, s, o) {
  if (e === !1 || e == null || !e && (r === "class" || r === "style")) return "";
  if (e === !0) return " " + (r + '="' + r + '"');
  var u = typeof e;
  return u !== "object" && u !== "function" || typeof e.toJSON != "function" || (e = e.toJSON()), typeof e == "string" || (e = JSON.stringify(e), s) ? (e = h(e), " " + r + '="' + e + '"') : " " + r + "='" + e.replace(/'/g, "&#39;") + "'";
}
function h(r) {
  var e = "" + r, s = i0.exec(e);
  if (!s) return r;
  var o, u, t, i = "";
  for (o = s.index, u = 0; o < e.length; o++) {
    switch (e.charCodeAt(o)) {
      case 34:
        t = "&quot;";
        break;
      case 38:
        t = "&amp;";
        break;
      case 60:
        t = "&lt;";
        break;
      case 62:
        t = "&gt;";
        break;
      default:
        continue;
    }
    u !== o && (i += e.substring(u, o)), u = o + 1, i += t;
  }
  return u !== o ? i + e.substring(u, o) : i;
}
var r0 = Object.prototype.hasOwnProperty, i0 = /["&<>]/;
function W(r, e, s, o) {
  if (!(r instanceof Error)) throw r;
  if (!(typeof window > "u" && e || o)) throw r.message += " on line " + s, r;
  var u, t, i, F;
  try {
    o = o || require("fs").readFileSync(e, { encoding: "utf8" }), u = 3, t = o.split(`
`), i = Math.max(s - u, 0), F = Math.min(t.length, s + u);
  } catch (c) {
    return r.message += " - could not read from " + e + " (" + c.message + ")", void W(r, null, s);
  }
  u = t.slice(i, F).map(function(c, d) {
    var p = d + i + 1;
    return (p == s ? "  > " : "    ") + p + "| " + c;
  }).join(`
`), r.path = e;
  try {
    r.message = (e || "Pug") + ":" + s + `
` + u + `

` + r.message;
  } catch {
  }
  throw r;
}
function c0(r) {
  if (!r) return "";
  if (typeof r == "object") {
    var e = "";
    for (var s in r) r0.call(r, s) && (e = e + s + ":" + r[s] + ";");
    return e;
  }
  return r + "";
}
function F0(r) {
  var e = "", s = {}, o, u, t;
  try {
    var i = r || {};
    (function(F, c) {
      t = 1, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", s["g-dwas-parameters"] = o = function(d) {
        var p = this && this.block, V = this && this.attributes || {};
        t = 2, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const m = d;
        t = 7, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const C = `g-${m}-dwas-url`;
        t = 8, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const v = `g-${m}-dwas-qido-prefix`;
        t = 9, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const A = `g-${m}-dwas-wado-prefix`;
        t = 10, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const b = `g-${m}-dwas-auth-type`;
        t = 11, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const M = `g-${m}-dwas-auth-type-container`;
        t = 12, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const x = `g-${m}-dwas-auth-token`;
        t = 13, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const E = `g-${m}-dwas-auth-token-container`;
        t = 15, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + '<div class="form-group">', t = 16, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<label" + (' class="control-label"' + a("for", C, !0, !1)) + ">", t = 16, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "DICOMweb server URL</label>", t = 17, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<input" + (' class="input-sm form-control"' + a("id", C, !0, !1) + ' type="text" placeholder="URL"') + "/>", t = 21, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<label" + (' class="control-label"' + a("for", v, !0, !1)) + ">", t = 21, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "DICOMweb QIDO prefix (optional)</label>", t = 22, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<input" + (' class="input-sm form-control"' + a("id", v, !0, !1) + ' type="text" placeholder="QIDO prefix"') + "/>", t = 26, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<label" + (' class="control-label"' + a("for", A, !0, !1)) + ">", t = 26, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "DICOMweb WADO prefix (optional)</label>", t = 27, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<input" + (' class="input-sm form-control"' + a("id", A, !0, !1) + ' type="text" placeholder="WADO prefix"') + "/>", t = 31, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<label" + (' class="control-label"' + a("for", b, !0, !1)) + ">", t = 31, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "DICOMweb authentication type (optional)</label>", t = 32, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const w = F && F.attributes.dicomweb_meta.auth_type || null;
        t = 33, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const y = `${m}UpdateVisibilities`;
        t = 34, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<script>", t = 35, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "var ", t = 35, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + h((o = y) == null ? "" : o), t = 35, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + " = function () {", t = 36, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + `
`, t = 36, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "   const isToken = document.getElementById('", t = 36, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + h((o = b) == null ? "" : o), t = 36, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "').value === 'token';", t = 37, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + `
`, t = 37, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "   const display = isToken ? 'block' : 'none';", t = 38, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + `
`, t = 38, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "   document.getElementById('", t = 38, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + h((o = E) == null ? "" : o), t = 38, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "').style.display = display;", t = 39, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + `
`, t = 39, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "};<\/script>", t = 40, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<div" + a("id", M, !0, !1) + ">", t = 41, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<select" + (' class="form-control"' + a("id", b, !0, !1) + a("onchange", y + "()", !0, !1)) + ">", t = 44, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", (function() {
          var _ = c;
          if (typeof _.length == "number")
            for (var g = 0, f = _.length; g < f; g++) {
              var n = _[g];
              t = 45, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<option" + (a("value", n.value, !0, !1) + a("selected", w === n.value, !0, !1)) + ">", t = 45, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + h((o = n.label) == null ? "" : o) + "</option>";
            }
          else {
            var f = 0;
            for (var g in _) {
              f++;
              var n = _[g];
              t = 45, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<option" + (a("value", n.value, !0, !1) + a("selected", w === n.value, !0, !1)) + ">", t = 45, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + h((o = n.label) == null ? "" : o) + "</option>";
            }
          }
        }).call(this), e = e + "</select></div>", t = 46, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const I = w === "token" ? "block" : "none";
        t = 47, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<div" + (a("id", E, !0, !1) + a("style", c0("display: " + I + ";"), !0, !1)) + ">", t = 48, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<label" + (' class="control-label"' + a("for", x, !0, !1)) + ">", t = 48, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "DICOMweb authentication token</label>", t = 49, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<input" + (' class="input-sm form-control"' + a("id", x, !0, !1) + ' type="text" placeholder="Token"') + "/></div></div>";
      }, t = 3, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreEditFields.pug", s["g-dwas-parameters"]("edit");
    }).call(this, "assetstore" in i ? i.assetstore : typeof assetstore < "u" ? assetstore : void 0, "authOptions" in i ? i.authOptions : typeof authOptions < "u" ? authOptions : void 0);
  } catch (F) {
    W(F, u, t);
  }
  return e;
}
const $ = [
  {
    // HTML can't accept null, but it can accept an empty string
    value: "",
    label: "None"
  },
  {
    value: "token",
    label: "Token"
  }
], B = girder.views.widgets.EditAssetstoreWidget, { AssetstoreType: N } = girder.constants, { wrap: a0 } = girder.utilities.PluginUtils;
a0(B, "render", function(r) {
  return r.call(this), this.model.get("type") === N.DICOMWEB && this.$(".g-assetstore-form-fields").append(
    F0({
      assetstore: this.model,
      authOptions: $
    })
  ), this;
});
B.prototype.fieldsMap[N.DICOMWEB] = {
  get: function() {
    return {
      url: this.$("#g-edit-dwas-url").val(),
      qido_prefix: this.$("#g-edit-dwas-qido-prefix").val(),
      wado_prefix: this.$("#g-edit-dwas-wado-prefix").val(),
      auth_type: this.$("#g-edit-dwas-auth-type").val(),
      auth_token: this.$("#g-edit-dwas-auth-token").val()
    };
  },
  set: function() {
    const r = this.model.get("dicomweb_meta");
    this.$("#g-edit-dwas-url").val(r.url), this.$("#g-edit-dwas-qido-prefix").val(r.qido_prefix), this.$("#g-edit-dwas-wado-prefix").val(r.wado_prefix), this.$("#g-edit-dwas-auth-type").val(r.auth_type || ""), this.$("#g-edit-dwas-auth-token").val(r.auth_token);
  }
};
const l0 = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null
}, Symbol.toStringTag, { value: "Module" }));
function l(r, e, s, o) {
  if (e === !1 || e == null || !e && (r === "class" || r === "style")) return "";
  if (e === !0) return " " + (r + '="' + r + '"');
  var u = typeof e;
  return u !== "object" && u !== "function" || typeof e.toJSON != "function" || (e = e.toJSON()), typeof e == "string" || (e = JSON.stringify(e), s) ? (e = j(e), " " + r + '="' + e + '"') : " " + r + "='" + e.replace(/'/g, "&#39;") + "'";
}
function j(r) {
  var e = "" + r, s = n0.exec(e);
  if (!s) return r;
  var o, u, t, i = "";
  for (o = s.index, u = 0; o < e.length; o++) {
    switch (e.charCodeAt(o)) {
      case 34:
        t = "&quot;";
        break;
      case 38:
        t = "&amp;";
        break;
      case 60:
        t = "&lt;";
        break;
      case 62:
        t = "&gt;";
        break;
      default:
        continue;
    }
    u !== o && (i += e.substring(u, o)), u = o + 1, i += t;
  }
  return u !== o ? i + e.substring(u, o) : i;
}
var m0 = Object.prototype.hasOwnProperty, n0 = /["&<>]/;
function q(r, e, s, o) {
  if (!(r instanceof Error)) throw r;
  if (!(typeof window > "u" && e || o)) throw r.message += " on line " + s, r;
  var u, t, i, F;
  try {
    o = o || require("fs").readFileSync(e, { encoding: "utf8" }), u = 3, t = o.split(`
`), i = Math.max(s - u, 0), F = Math.min(t.length, s + u);
  } catch (c) {
    return r.message += " - could not read from " + e + " (" + c.message + ")", void q(r, null, s);
  }
  u = t.slice(i, F).map(function(c, d) {
    var p = d + i + 1;
    return (p == s ? "  > " : "    ") + p + "| " + c;
  }).join(`
`), r.path = e;
  try {
    r.message = (e || "Pug") + ":" + s + `
` + u + `

` + r.message;
  } catch {
  }
  throw r;
}
function p0(r) {
  if (!r) return "";
  if (typeof r == "object") {
    var e = "";
    for (var s in r) m0.call(r, s) && (e = e + s + ":" + r[s] + ";");
    return e;
  }
  return r + "";
}
function d0(r) {
  var e = "", s = {}, o, u, t;
  try {
    var i = r || {};
    (function(F, c) {
      t = 1, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", s["g-dwas-parameters"] = o = function(d) {
        var p = this && this.block, V = this && this.attributes || {};
        t = 2, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const m = d;
        t = 7, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const C = `g-${m}-dwas-url`;
        t = 8, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const v = `g-${m}-dwas-qido-prefix`;
        t = 9, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const A = `g-${m}-dwas-wado-prefix`;
        t = 10, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const b = `g-${m}-dwas-auth-type`;
        t = 11, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const M = `g-${m}-dwas-auth-type-container`;
        t = 12, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const x = `g-${m}-dwas-auth-token`;
        t = 13, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const E = `g-${m}-dwas-auth-token-container`;
        t = 15, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + '<div class="form-group">', t = 16, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<label" + (' class="control-label"' + l("for", C, !0, !1)) + ">", t = 16, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "DICOMweb server URL</label>", t = 17, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<input" + (' class="input-sm form-control"' + l("id", C, !0, !1) + ' type="text" placeholder="URL"') + "/>", t = 21, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<label" + (' class="control-label"' + l("for", v, !0, !1)) + ">", t = 21, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "DICOMweb QIDO prefix (optional)</label>", t = 22, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<input" + (' class="input-sm form-control"' + l("id", v, !0, !1) + ' type="text" placeholder="QIDO prefix"') + "/>", t = 26, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<label" + (' class="control-label"' + l("for", A, !0, !1)) + ">", t = 26, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "DICOMweb WADO prefix (optional)</label>", t = 27, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<input" + (' class="input-sm form-control"' + l("id", A, !0, !1) + ' type="text" placeholder="WADO prefix"') + "/>", t = 31, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<label" + (' class="control-label"' + l("for", b, !0, !1)) + ">", t = 31, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "DICOMweb authentication type (optional)</label>", t = 32, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const w = F && F.attributes.dicomweb_meta.auth_type || null;
        t = 33, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const y = `${m}UpdateVisibilities`;
        t = 34, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<script>", t = 35, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "var ", t = 35, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + j((o = y) == null ? "" : o), t = 35, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + " = function () {", t = 36, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + `
`, t = 36, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "   const isToken = document.getElementById('", t = 36, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + j((o = b) == null ? "" : o), t = 36, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "').value === 'token';", t = 37, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + `
`, t = 37, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "   const display = isToken ? 'block' : 'none';", t = 38, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + `
`, t = 38, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "   document.getElementById('", t = 38, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + j((o = E) == null ? "" : o), t = 38, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "').style.display = display;", t = 39, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + `
`, t = 39, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "};<\/script>", t = 40, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<div" + l("id", M, !0, !1) + ">", t = 41, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<select" + (' class="form-control"' + l("id", b, !0, !1) + l("onchange", y + "()", !0, !1)) + ">", t = 44, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", (function() {
          var _ = c;
          if (typeof _.length == "number")
            for (var g = 0, f = _.length; g < f; g++) {
              var n = _[g];
              t = 45, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<option" + (l("value", n.value, !0, !1) + l("selected", w === n.value, !0, !1)) + ">", t = 45, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + j((o = n.label) == null ? "" : o) + "</option>";
            }
          else {
            var f = 0;
            for (var g in _) {
              f++;
              var n = _[g];
              t = 45, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<option" + (l("value", n.value, !0, !1) + l("selected", w === n.value, !0, !1)) + ">", t = 45, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + j((o = n.label) == null ? "" : o) + "</option>";
            }
          }
        }).call(this), e = e + "</select></div>", t = 46, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug";
        const I = w === "token" ? "block" : "none";
        t = 47, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<div" + (l("id", E, !0, !1) + l("style", p0("display: " + I + ";"), !0, !1)) + ">", t = 48, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<label" + (' class="control-label"' + l("for", x, !0, !1)) + ">", t = 48, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "DICOMweb authentication token</label>", t = 49, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreMixins.pug", e = e + "<input" + (' class="input-sm form-control"' + l("id", x, !0, !1) + ' type="text" placeholder="Token"') + "/></div></div>";
      }, t = 3, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + '<div class="panel panel-default">', t = 4, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + '<div class="panel-heading" data-toggle="collapse" data-parent="#g-assetstore-accordion" data-target="#g-create-dwas-tab">', t = 8, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + '<div class="panel-title">', t = 9, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + "<a>", t = 10, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + '<i class="icon-server"></i>', t = 11, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + "<span>", t = 11, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + "Create new ", t = 11, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + "<b>", t = 11, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + "DICOMweb</b>", t = 11, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + " assetstore</span></a></div></div>", t = 12, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + '<div class="panel-collapse collapse" id="g-create-dwas-tab">', t = 13, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + '<div class="panel-body">', t = 14, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + "<p>", t = 15, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + "The DICOMweb assetstore can be used to search for and view WSI DICOM", t = 16, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + `
`, t = 16, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + "files on a DICOMweb server. Each DICOMweb assetstore should point to a", t = 17, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + `
`, t = 17, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + "particular DICOMweb server.</p>", t = 18, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + '<form id="g-new-dwas-form" role="form">', t = 19, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + '<label class="control-label" for="g-new-dwas-name">', t = 19, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + "Assetstore name</label>", t = 20, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + '<input class="input-sm form-control" id="g-new-dwas-name" type="text" placeholder="Name"/>', t = 23, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", s["g-dwas-parameters"]("new"), t = 24, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + '<p class="g-validation-failed-message" id="g-new-dwas-error"></p>', t = 25, u = "/root/project/sources/dicom/large_image_source_dicom/web_client/templates/dicomwebAssetstoreCreate.pug", e = e + '<input class="g-new-assetstore-submit btn btn-sm btn-primary" type="submit" value="Create"/></form></div></div></div>';
    }).call(this, "assetstore" in i ? i.assetstore : typeof assetstore < "u" ? assetstore : void 0, "authOptions" in i ? i.authOptions : typeof authOptions < "u" ? authOptions : void 0);
  } catch (F) {
    q(F, u, t);
  }
  return e;
}
const P = girder.views.widgets.NewAssetstoreWidget, { AssetstoreType: _0 } = girder.constants, { wrap: g0 } = girder.utilities.PluginUtils;
g0(P, "render", function(r) {
  return r.call(this), this.$("#g-assetstore-accordion").append(d0({
    authOptions: $
  })), this;
});
P.prototype.events["submit #g-new-dwas-form"] = function(r) {
  this.createAssetstore(r, this.$("#g-new-dwas-error"), {
    type: _0.DICOMWEB,
    name: this.$("#g-new-dwas-name").val(),
    url: this.$("#g-new-dwas-url").val(),
    qido_prefix: this.$("#g-new-dwas-qido-prefix").val(),
    wado_prefix: this.$("#g-new-dwas-wado-prefix").val(),
    auth_type: this.$("#g-new-dwas-auth-type").val(),
    auth_token: this.$("#g-new-dwas-auth-token").val()
  });
};
const b0 = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null
}, Symbol.toStringTag, { value: "Module" })), w0 = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  AssetstoresView: s0,
  AuthOptions: $,
  DICOMwebImportView: S,
  EditAssetstoreWidget: l0,
  NewAssetstoreWidget: b0
}, Symbol.toStringTag, { value: "Module" })), f0 = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  constants: J,
  views: w0
}, Symbol.toStringTag, { value: "Module" })), { registerPluginNamespace: h0 } = girder.pluginUtils;
h0("dicomweb", f0);
//# sourceMappingURL=girder-plugin-dicomweb.mjs.map
