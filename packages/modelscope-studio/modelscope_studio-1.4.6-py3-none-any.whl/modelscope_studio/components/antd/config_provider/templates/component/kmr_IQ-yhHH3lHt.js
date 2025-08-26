import { c as s } from "./Index-WXKJnuTW.js";
import { i as u } from "./config-provider-C0s-_bDn.js";
import { k as f, a as c, b as k, c as d } from "./kmr_IQ-Dk85WxeC.js";
function p(l, n) {
  for (var i = 0; i < n.length; i++) {
    const e = n[i];
    if (typeof e != "string" && !Array.isArray(e)) {
      for (const r in e)
        if (r !== "default" && !(r in l)) {
          const o = Object.getOwnPropertyDescriptor(e, r);
          o && Object.defineProperty(l, r, o.get ? o : {
            enumerable: !0,
            get: () => e[r]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(l, Symbol.toStringTag, {
    value: "Module"
  }));
}
var t = {}, a = u.default;
Object.defineProperty(t, "__esModule", {
  value: !0
});
t.default = void 0;
var _ = a(f), b = a(c), T = a(k), v = a(d);
const g = {
  locale: "ku",
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
t.default = g;
var m = t;
const I = /* @__PURE__ */ s(m), x = /* @__PURE__ */ p({
  __proto__: null,
  default: I
}, [m]);
export {
  x as k
};
