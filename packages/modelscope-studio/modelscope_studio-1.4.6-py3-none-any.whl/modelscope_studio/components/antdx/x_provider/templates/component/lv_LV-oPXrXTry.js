import { a as g } from "./XProvider-Cvj7sJYT.js";
import { i as r, o as k, c as j } from "./config-provider-rXQnJyjg.js";
function P(n, c) {
  for (var v = 0; v < c.length; v++) {
    const e = c[v];
    if (typeof e != "string" && !Array.isArray(e)) {
      for (const a in e)
        if (a !== "default" && !(a in n)) {
          const p = Object.getOwnPropertyDescriptor(e, a);
          p && Object.defineProperty(n, a, p.get ? p : {
            enumerable: !0,
            get: () => e[a]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(n, Symbol.toStringTag, {
    value: "Module"
  }));
}
var i = {}, o = {};
Object.defineProperty(o, "__esModule", {
  value: !0
});
o.default = void 0;
var b = {
  // Options
  items_per_page: "/ lappuse",
  jump_to: "iet uz",
  jump_to_confirm: "apstiprināt",
  page: "",
  // Pagination
  prev_page: "Iepriekšējā lapa",
  next_page: "Nākamā lapaspuse",
  prev_5: "Iepriekšējās 5 lapas",
  next_5: "Nākamās 5 lapas",
  prev_3: "Iepriekšējās 3 lapas",
  next_3: "Nākamās 3 lapas",
  page_size: "Page Size"
};
o.default = b;
var u = {}, t = {}, s = {}, y = r.default;
Object.defineProperty(s, "__esModule", {
  value: !0
});
s.default = void 0;
var f = y(k), L = j, O = (0, f.default)((0, f.default)({}, L.commonLocale), {}, {
  locale: "lv_LV",
  today: "Šodien",
  now: "Tagad",
  backToToday: "Atpakaļ pie šodienas",
  ok: "OK",
  clear: "Skaidrs",
  week: "Nedēļa",
  month: "Mēnesis",
  year: "Gads",
  timeSelect: "Izvēlieties laiku",
  dateSelect: "Izvēlieties datumu",
  monthSelect: "Izvēlieties mēnesi",
  yearSelect: "Izvēlieties gadu",
  decadeSelect: "Izvēlieties desmit gadus",
  dateFormat: "D.M.YYYY",
  dateTimeFormat: "D.M.YYYY HH:mm:ss",
  previousMonth: "Iepriekšējais mēnesis (PageUp)",
  nextMonth: "Nākammēnes (PageDown)",
  previousYear: "Pagājušais gads (Control + left)",
  nextYear: "Nākamgad (Control + right)",
  previousDecade: "Pēdējā desmitgadē",
  nextDecade: "Nākamā desmitgade",
  previousCentury: "Pagājušajā gadsimtā",
  nextCentury: "Nākamajā gadsimtā"
});
s.default = O;
var l = {};
Object.defineProperty(l, "__esModule", {
  value: !0
});
l.default = void 0;
const V = {
  placeholder: "Izvēlieties laiku"
};
l.default = V;
var _ = r.default;
Object.defineProperty(t, "__esModule", {
  value: !0
});
t.default = void 0;
var x = _(s), $ = _(l);
const z = {
  lang: Object.assign({
    placeholder: "Izvēlieties datumu",
    rangePlaceholder: ["Sākuma datums", "Beigu datums"]
  }, x.default),
  timePickerLocale: Object.assign({}, $.default)
};
t.default = z;
var T = r.default;
Object.defineProperty(u, "__esModule", {
  value: !0
});
u.default = void 0;
var M = T(t);
u.default = M.default;
var d = r.default;
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
var D = d(o), I = d(u), N = d(t), h = d(l);
const S = {
  locale: "lv",
  Pagination: D.default,
  DatePicker: N.default,
  TimePicker: h.default,
  Calendar: I.default,
  global: {
    close: "Aizvērt"
  },
  Table: {
    filterTitle: "Filtrēšanas izvēlne",
    filterConfirm: "OK",
    filterReset: "Atiestatīt",
    selectAll: "Atlasiet pašreizējo lapu",
    selectInvert: "Pārvērst pašreizējo lapu"
  },
  Tour: {
    Next: "Nākamais",
    Previous: "Iepriekšējais",
    Finish: "Pabeigt"
  },
  Modal: {
    okText: "OK",
    cancelText: "Atcelt",
    justOkText: "OK"
  },
  Popconfirm: {
    okText: "OK",
    cancelText: "Atcelt"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Meklēt šeit",
    itemUnit: "vienumu",
    itemsUnit: "vienumus"
  },
  Upload: {
    uploading: "Augšupielāde...",
    removeFile: "Noņemt failu",
    uploadError: "Augšupielādes kļūda",
    previewFile: "Priekšskatiet failu",
    downloadFile: "Lejupielādēt failu"
  },
  Empty: {
    description: "Nav datu"
  }
};
i.default = S;
var m = i;
const A = /* @__PURE__ */ g(m), C = /* @__PURE__ */ P({
  __proto__: null,
  default: A
}, [m]);
export {
  C as l
};
