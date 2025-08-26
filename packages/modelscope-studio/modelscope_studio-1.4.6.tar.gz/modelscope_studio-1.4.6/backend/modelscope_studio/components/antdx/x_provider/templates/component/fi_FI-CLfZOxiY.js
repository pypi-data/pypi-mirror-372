import { a as k } from "./XProvider-Cvj7sJYT.js";
import { i as l, o as y, c as g } from "./config-provider-rXQnJyjg.js";
function P(d, c) {
  for (var v = 0; v < c.length; v++) {
    const e = c[v];
    if (typeof e != "string" && !Array.isArray(e)) {
      for (const t in e)
        if (t !== "default" && !(t in d)) {
          const f = Object.getOwnPropertyDescriptor(e, t);
          f && Object.defineProperty(d, t, f.get ? f : {
            enumerable: !0,
            get: () => e[t]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(d, Symbol.toStringTag, {
    value: "Module"
  }));
}
var o = {}, r = {};
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
var j = {
  // Options
  items_per_page: "/ sivu",
  jump_to: "Mene",
  jump_to_confirm: "Potvrdite",
  page: "Sivu",
  // Pagination
  prev_page: "Edellinen sivu",
  next_page: "Seuraava sivu",
  prev_5: "Edelliset 5 sivua",
  next_5: "Seuraavat 5 sivua",
  prev_3: "Edelliset 3 sivua",
  next_3: "Seuraavat 3 sivua",
  page_size: "Page Size"
};
r.default = j;
var u = {}, a = {}, s = {}, F = l.default;
Object.defineProperty(s, "__esModule", {
  value: !0
});
s.default = void 0;
var p = F(y), S = g, h = (0, p.default)((0, p.default)({}, S.commonLocale), {}, {
  locale: "fi_FI",
  today: "Tänään",
  now: "Nyt",
  backToToday: "Tämä päivä",
  ok: "OK",
  clear: "Tyhjennä",
  week: "Viikko",
  month: "Kuukausi",
  year: "Vuosi",
  timeSelect: "Valise aika",
  dateSelect: "Valitse päivä",
  monthSelect: "Valitse kuukausi",
  yearSelect: "Valitse vuosi",
  decadeSelect: "Valitse vuosikymmen",
  dateFormat: "D.M.YYYY",
  dateTimeFormat: "D.M.YYYY HH:mm:ss",
  previousMonth: "Edellinen kuukausi (PageUp)",
  nextMonth: "Seuraava kuukausi (PageDown)",
  previousYear: "Edellinen vuosi (Control + left)",
  nextYear: "Seuraava vuosi (Control + right)",
  previousDecade: "Edellinen vuosikymmen",
  nextDecade: "Seuraava vuosikymmen",
  previousCentury: "Edellinen vuosisata",
  nextCentury: "Seuraava vuosisata"
});
s.default = h;
var i = {};
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
const T = {
  placeholder: "Valitse aika"
};
i.default = T;
var _ = l.default;
Object.defineProperty(a, "__esModule", {
  value: !0
});
a.default = void 0;
var b = _(s), x = _(i);
const O = {
  lang: Object.assign({
    placeholder: "Valitse päivä",
    rangePlaceholder: ["Alkamispäivä", "Päättymispäivä"]
  }, b.default),
  timePickerLocale: Object.assign({}, x.default)
};
a.default = O;
var I = l.default;
Object.defineProperty(u, "__esModule", {
  value: !0
});
u.default = void 0;
var $ = I(a);
u.default = $.default;
var n = l.default;
Object.defineProperty(o, "__esModule", {
  value: !0
});
o.default = void 0;
var E = n(r), D = n(u), M = n(a), V = n(i);
const Y = {
  locale: "fi",
  Pagination: E.default,
  DatePicker: M.default,
  TimePicker: V.default,
  Calendar: D.default,
  global: {
    close: "Sulje"
  },
  Table: {
    filterTitle: "Suodatus valikko",
    filterConfirm: "OK",
    filterReset: "Tyhjennä",
    selectAll: "Valitse kaikki",
    selectInvert: "Valitse päinvastoin",
    sortTitle: "Lajittele",
    triggerDesc: "Lajittele laskevasti",
    triggerAsc: "Lajittele nousevasti",
    cancelSort: "Peruuta lajittelu"
  },
  Tour: {
    Next: "Seuraava",
    Previous: "Edellinen",
    Finish: "Valmis"
  },
  Modal: {
    okText: "OK",
    cancelText: "Peruuta",
    justOkText: "OK"
  },
  Popconfirm: {
    okText: "OK",
    cancelText: "Peruuta"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Etsi täältä",
    itemUnit: "kohde",
    itemsUnit: "kohdetta"
  },
  Upload: {
    uploading: "Lähetetään...",
    removeFile: "Poista tiedosto",
    uploadError: "Virhe lähetyksessä",
    previewFile: "Esikatsele tiedostoa",
    downloadFile: "Lataa tiedosto"
  },
  Empty: {
    description: "Ei kohteita"
  },
  Text: {
    edit: "Muokkaa",
    copy: "Kopioi",
    copied: "Kopioitu",
    expand: "Näytä lisää"
  }
};
o.default = Y;
var m = o;
const K = /* @__PURE__ */ k(m), w = /* @__PURE__ */ P({
  __proto__: null,
  default: K
}, [m]);
export {
  w as f
};
