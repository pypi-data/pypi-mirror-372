import { c as M } from "./Index-WXKJnuTW.js";
import { i as o, o as k, c as g } from "./config-provider-C0s-_bDn.js";
function y(c, p) {
  for (var f = 0; f < p.length; f++) {
    const e = p[f];
    if (typeof e != "string" && !Array.isArray(e)) {
      for (const t in e)
        if (t !== "default" && !(t in c)) {
          const _ = Object.getOwnPropertyDescriptor(e, t);
          _ && Object.defineProperty(c, t, _.get ? _ : {
            enumerable: !0,
            get: () => e[t]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(c, Symbol.toStringTag, {
    value: "Module"
  }));
}
var l = {}, i = {};
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
var P = {
  // Options
  items_per_page: "/ стр",
  jump_to: "Оди на",
  jump_to_confirm: "потврди",
  page: "",
  // Pagination
  prev_page: "Претходна страница",
  next_page: "Наредна страница",
  prev_5: "Претходни 5 страници",
  next_5: "Наредни 5 страници",
  prev_3: "Претходни 3 страници",
  next_3: "Наредни 3 страници",
  page_size: "Page Size"
};
i.default = P;
var u = {}, a = {}, d = {}, b = o.default;
Object.defineProperty(d, "__esModule", {
  value: !0
});
d.default = void 0;
var m = b(k), x = g, j = (0, m.default)((0, m.default)({}, x.commonLocale), {}, {
  locale: "mk_MK",
  today: "Денес",
  now: "Сега",
  backToToday: "Назад до денес",
  ok: "ОК",
  clear: "Избриши",
  week: "Недела",
  month: "Месец",
  year: "Година",
  timeSelect: "Избери време",
  dateSelect: "Избери датум",
  monthSelect: "Избери месец",
  yearSelect: "Избери година",
  decadeSelect: "Избери деценија",
  dateFormat: "D.M.YYYY",
  dateTimeFormat: "D.M.YYYY HH:mm:ss",
  previousMonth: "Претходен месец (PageUp)",
  nextMonth: "Нареден месец (PageDown)",
  previousYear: "Претходна година (Control + left)",
  nextYear: "Наредна година (Control + right)",
  previousDecade: "Претходна деценија",
  nextDecade: "Наредна деценија",
  previousCentury: "Претходен век",
  nextCentury: "Нареден век"
});
d.default = j;
var r = {};
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
const K = {
  placeholder: "Избери време"
};
r.default = K;
var s = o.default;
Object.defineProperty(a, "__esModule", {
  value: !0
});
a.default = void 0;
var $ = s(d), T = s(r);
const O = {
  lang: Object.assign({
    placeholder: "Избери датум",
    rangePlaceholder: ["Од датум", "До датум"]
  }, $.default),
  timePickerLocale: Object.assign({}, T.default)
};
a.default = O;
var h = o.default;
Object.defineProperty(u, "__esModule", {
  value: !0
});
u.default = void 0;
var D = h(a);
u.default = D.default;
var n = o.default;
Object.defineProperty(l, "__esModule", {
  value: !0
});
l.default = void 0;
var S = n(i), Y = n(u), C = n(a), F = n(r);
const w = {
  locale: "mk",
  Pagination: S.default,
  DatePicker: C.default,
  TimePicker: F.default,
  Calendar: Y.default,
  global: {
    placeholder: "Ве молиме означете",
    close: "Затвори"
  },
  Table: {
    filterTitle: "Мени за филтрирање",
    filterConfirm: "ОК",
    filterReset: "Избриши",
    selectAll: "Одбери страница",
    selectInvert: "Инвертирај страница"
  },
  Tour: {
    Next: "Следно",
    Previous: "Претходно",
    Finish: "Заврши"
  },
  Modal: {
    okText: "ОК",
    cancelText: "Откажи",
    justOkText: "ОК"
  },
  Popconfirm: {
    okText: "ОК",
    cancelText: "Откажи"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Пребарај тука",
    itemUnit: "предмет",
    itemsUnit: "предмети"
  },
  Upload: {
    uploading: "Се прикачува...",
    removeFile: "Избриши фајл",
    uploadError: "Грешка при прикачување",
    previewFile: "Прикажи фајл",
    downloadFile: "Преземи фајл"
  },
  Empty: {
    description: "Нема податоци"
  },
  Icon: {
    icon: "Икона"
  },
  Text: {
    edit: "Уреди",
    copy: "Копирај",
    copied: "Копирано",
    expand: "Зголеми"
  }
};
l.default = w;
var v = l;
const R = /* @__PURE__ */ M(v), U = /* @__PURE__ */ y({
  __proto__: null,
  default: R
}, [v]);
export {
  U as m
};
