import { c as _ } from "./Index-WXKJnuTW.js";
import { i as c } from "./config-provider-C0s-_bDn.js";
function j(s, f) {
  for (var d = 0; d < f.length; d++) {
    const e = f[d];
    if (typeof e != "string" && !Array.isArray(e)) {
      for (const t in e)
        if (t !== "default" && !(t in s)) {
          const u = Object.getOwnPropertyDescriptor(e, t);
          u && Object.defineProperty(s, t, u.get ? u : {
            enumerable: !0,
            get: () => e[t]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(s, Symbol.toStringTag, {
    value: "Module"
  }));
}
var l = {}, o = {};
Object.defineProperty(o, "__esModule", {
  value: !0
});
o.default = void 0;
var v = {
  // Options
  items_per_page: "/ strani",
  jump_to: "Pojdi na",
  jump_to_confirm: "potrdi",
  page: "",
  // Pagination
  prev_page: "Prejšnja stran",
  next_page: "Naslednja stran",
  prev_5: "Prejšnjih 5 strani",
  next_5: "Naslednjih 5 strani",
  prev_3: "Prejšnje 3 strani",
  next_3: "Naslednje 3 strani",
  page_size: "Page Size"
};
o.default = v;
var i = {}, r = {}, a = {};
Object.defineProperty(a, "__esModule", {
  value: !0
});
a.default = void 0;
const m = {
  placeholder: "Izberite čas"
};
a.default = m;
var P = c.default;
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
var b = P(a);
const g = {
  lang: {
    locale: "sl",
    placeholder: "Izberite datum",
    rangePlaceholder: ["Začetni datum", "Končni datum"],
    today: "Danes",
    now: "Trenutno",
    backToToday: "Nazaj na trenutni datum",
    ok: "OK",
    clear: "Počisti",
    week: "Teden",
    month: "Mesec",
    year: "Leto",
    timeSelect: "Izberi čas",
    dateSelect: "Izberi datum",
    monthSelect: "Izberite mesec",
    yearSelect: "Izberite leto",
    decadeSelect: "Izberite desetletje",
    yearFormat: "YYYY",
    monthFormat: "MMMM",
    monthBeforeYear: !0,
    previousMonth: "Prejšnji mesec (PageUp)",
    nextMonth: "Naslednji mesec (PageDown)",
    previousYear: "Lansko leto (Control + left)",
    nextYear: "Naslednje leto (Control + right)",
    previousDecade: "Prejšnje desetletje",
    nextDecade: "Naslednje desetletje",
    previousCentury: "Zadnje stoletje",
    nextCentury: "Naslednje stoletje"
  },
  timePickerLocale: Object.assign({}, b.default)
};
r.default = g;
var I = c.default;
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
var S = I(r);
i.default = S.default;
var n = c.default;
Object.defineProperty(l, "__esModule", {
  value: !0
});
l.default = void 0;
var k = n(o), y = n(i), O = n(r), h = n(a);
const x = {
  locale: "sl",
  Pagination: k.default,
  DatePicker: O.default,
  TimePicker: h.default,
  Calendar: y.default,
  global: {
    close: "Zapri"
  },
  Table: {
    filterTitle: "Filter",
    filterConfirm: "Filtriraj",
    filterReset: "Pobriši filter",
    selectAll: "Izberi vse na trenutni strani",
    selectInvert: "Obrni izbor na trenutni strani"
  },
  Tour: {
    Next: "Naprej",
    Previous: "Prejšnje",
    Finish: "Končaj"
  },
  Modal: {
    okText: "V redu",
    cancelText: "Prekliči",
    justOkText: "V redu"
  },
  Popconfirm: {
    okText: "v redu",
    cancelText: "Prekliči"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Išči tukaj",
    itemUnit: "Objekt",
    itemsUnit: "Objektov"
  },
  Upload: {
    uploading: "Nalaganje...",
    removeFile: "Odstrani datoteko",
    uploadError: "Napaka pri nalaganju",
    previewFile: "Predogled datoteke",
    downloadFile: "Prenos datoteke"
  },
  Empty: {
    description: "Ni podatkov"
  }
};
l.default = x;
var p = l;
const T = /* @__PURE__ */ _(p), z = /* @__PURE__ */ j({
  __proto__: null,
  default: T
}, [p]);
export {
  z as s
};
