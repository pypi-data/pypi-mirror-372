import { c as u } from "./Index-WXKJnuTW.js";
import { i as s } from "./config-provider-C0s-_bDn.js";
import { k as f, a as c, b as k, c as d } from "./kmr_IQ-Dk85WxeC.js";
function p(l, n) {
  for (var i = 0; i < n.length; i++) {
    const e = n[i];
    if (typeof e != "string" && !Array.isArray(e)) {
      for (const t in e)
        if (t !== "default" && !(t in l)) {
          const o = Object.getOwnPropertyDescriptor(e, t);
          o && Object.defineProperty(l, t, o.get ? o : {
            enumerable: !0,
            get: () => e[t]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(l, Symbol.toStringTag, {
    value: "Module"
  }));
}
var r = {}, a = s.default;
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
var _ = a(f), b = a(c), T = a(k), v = a(d);
const g = {
  locale: "ku-iq",
  Pagination: _.default,
  DatePicker: T.default,
  TimePicker: v.default,
  Calendar: b.default,
  global: {
    close: "Betal ke"
  },
  Table: {
    filterTitle: "Menuê peldanka",
    filterConfirm: "Temam",
    filterReset: "Jê bibe",
    selectAll: "Hemî hilbijêre",
    selectInvert: "Hilbijartinan veguhere"
  },
  Tour: {
    Next: "Temam",
    Previous: "Betal ke",
    Finish: "Temam"
  },
  Modal: {
    okText: "Temam",
    cancelText: "Betal ke",
    justOkText: "Temam"
  },
  Popconfirm: {
    okText: "Temam",
    cancelText: "Betal ke"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Lêgerîn",
    itemUnit: "tişt",
    itemsUnit: "tişt"
  },
  Upload: {
    uploading: "Bardike...",
    removeFile: "Pelê rabike",
    uploadError: "Xeta barkirine",
    previewFile: "Pelê pêşbibîne",
    downloadFile: "Pelê dakêşin"
  },
  Empty: {
    description: "Agahî tune"
  }
};
r.default = g;
var m = r;
const I = /* @__PURE__ */ u(m), x = /* @__PURE__ */ p({
  __proto__: null,
  default: I
}, [m]);
export {
  x as k
};
