import { c as k } from "./Index-WXKJnuTW.js";
import { i as o, o as b, c as g } from "./config-provider-C0s-_bDn.js";
function x(s, f) {
  for (var p = 0; p < f.length; p++) {
    const a = f[p];
    if (typeof a != "string" && !Array.isArray(a)) {
      for (const l in a)
        if (l !== "default" && !(l in s)) {
          const m = Object.getOwnPropertyDescriptor(a, l);
          m && Object.defineProperty(s, l, m.get ? m : {
            enumerable: !0,
            get: () => a[l]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(s, Symbol.toStringTag, {
    value: "Module"
  }));
}
var n = {}, i = {};
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
var y = {
  // Options
  items_per_page: "/ бет",
  jump_to: "Секіру",
  jump_to_confirm: "Растау",
  page: "",
  // Pagination
  prev_page: "Артқа",
  next_page: "Алға",
  prev_5: "Алдыңғы 5",
  next_5: "Келесі 5",
  prev_3: "Алдыңғы 3",
  next_3: "Келесі 3",
  page_size: "Page Size"
};
i.default = y;
var c = {}, t = {}, d = {}, P = o.default;
Object.defineProperty(d, "__esModule", {
  value: !0
});
d.default = void 0;
var _ = P(b), h = g, j = (0, _.default)((0, _.default)({}, h.commonLocale), {}, {
  locale: "kk_KZ",
  today: "Бүгін",
  now: "Қазір",
  backToToday: "Ағымдағы күн",
  ok: "Таңдау",
  clear: "Таза",
  week: "Апта",
  month: "Ай",
  year: "Жыл",
  timeSelect: "Уақытты таңдау",
  dateSelect: "Күнді таңдау",
  monthSelect: "Айды таңдаңыз",
  yearSelect: "Жылды таңдаңыз",
  decadeSelect: "Онжылды таңдаңыз",
  dateFormat: "D-M-YYYY",
  dateTimeFormat: "D-M-YYYY HH:mm:ss",
  previousMonth: "Алдыңғы ай (PageUp)",
  nextMonth: "Келесі ай (PageDown)",
  previousYear: "Алдыңғы жыл (Control + left)",
  nextYear: "Келесі жыл (Control + right)",
  previousDecade: "Алдыңғы онжылдық",
  nextDecade: "Келесі онжылдық",
  previousCentury: "Алдыңғы ғасыр",
  nextCentury: "Келесі ғасыр"
});
d.default = j;
var r = {};
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
const T = {
  placeholder: "Уақытты таңдаңыз",
  rangePlaceholder: ["Бастау уақыты", "Аяқталу уақыты"]
};
r.default = T;
var $ = o.default;
Object.defineProperty(t, "__esModule", {
  value: !0
});
t.default = void 0;
var K = $(d), Z = $(r);
const O = {
  lang: Object.assign({
    placeholder: "Күнді таңдаңыз",
    yearPlaceholder: "Жылды таңдаңыз",
    quarterPlaceholder: "Тоқсанды таңдаңыз",
    monthPlaceholder: "Айды таңдаңыз",
    weekPlaceholder: "Аптаны таңдаңыз",
    rangePlaceholder: ["Бастау күні", "Аяқталу күні"],
    rangeYearPlaceholder: ["Бастау жылы", "Аяқталу жылы"],
    rangeMonthPlaceholder: ["Бастау айы", "Аяқталу айы"],
    rangeWeekPlaceholder: ["Бастау апта", "Аяқталу апта"]
  }, K.default),
  timePickerLocale: Object.assign({}, Z.default)
};
t.default = O;
var D = o.default;
Object.defineProperty(c, "__esModule", {
  value: !0
});
c.default = void 0;
var M = D(t);
c.default = M.default;
var u = o.default;
Object.defineProperty(n, "__esModule", {
  value: !0
});
n.default = void 0;
var S = u(i), Y = u(c), C = u(t), w = u(r);
const e = "${label} ${type} типі емес", F = {
  locale: "kk",
  Pagination: S.default,
  DatePicker: C.default,
  TimePicker: w.default,
  Calendar: Y.default,
  global: {
    placeholder: "Таңдаңыз",
    close: "Жабу"
  },
  Table: {
    filterTitle: "Фильтр",
    filterConfirm: "OK",
    filterReset: "Тазарту",
    filterEmptyText: "Фильтр жоқ",
    emptyText: "Деректер жоқ",
    selectAll: "Барлығын таңдау",
    selectInvert: "Таңдауды төңкеру",
    selectionAll: "Барлық деректерді таңдаңыз",
    sortTitle: "Сұрыптау",
    expand: "Жолды жазу",
    collapse: "Жолды бүктеу",
    triggerDesc: "Төмендеуді сұрыптау үшін басыңыз",
    triggerAsc: "Өсу ретімен сұрыптау үшін басыңыз",
    cancelSort: "Сұрыптаудан бас тарту үшін басыңыз"
  },
  Tour: {
    Next: "Келесі",
    Previous: "Алдыңғы",
    Finish: "Аяқтау"
  },
  Modal: {
    okText: "Жарайды",
    cancelText: "Болдырмау",
    justOkText: "Жарайды"
  },
  Popconfirm: {
    okText: "Жарайды",
    cancelText: "Болдырмау"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Іздеу",
    itemUnit: "элемент.",
    itemsUnit: "элемент.",
    remove: "Жою",
    selectAll: "Барлық деректерді таңдау",
    selectCurrent: "Ағымдағы бетті таңдау",
    selectInvert: "Кері тәртіпте көрсету",
    removeAll: "Барлық деректерді жою",
    removeCurrent: "Ағымдағы парақты өшіру"
  },
  Upload: {
    uploading: "Жүктеу...",
    removeFile: "Файлды жою",
    uploadError: "Жүктеу кезінде қате пайда болды",
    previewFile: "Файлды алдын ала қарау",
    downloadFile: "Файлды жүктеу"
  },
  Empty: {
    description: "Деректер жоқ"
  },
  Icon: {
    icon: "белгішесі"
  },
  Text: {
    edit: "Өңдеу",
    copy: "Көшіру",
    copied: "Көшірілді",
    expand: "Жазу"
  },
  Form: {
    defaultValidateMessages: {
      default: "${label} өрісін тексеру қателігі",
      required: "${label} енгізіңіз",
      enum: "${label} [${enum}] қатарынан болуы керек",
      whitespace: "${label} бос болмауы керек",
      date: {
        format: "${label} жарамды күн форматы емес",
        parse: "${label} күнге түрлендірілмейді",
        invalid: "${label} жарамды күн емес"
      },
      types: {
        string: e,
        method: e,
        array: e,
        object: e,
        number: e,
        date: e,
        boolean: e,
        integer: e,
        float: e,
        regexp: e,
        email: e,
        url: e,
        hex: e
      },
      string: {
        len: "${label} ${len} таңбадан тұруы керек",
        min: "${label} ${min} таңбадан үлкен немесе оған тең болуы керек",
        max: "${label} ${max} таңбадан кем немесе оған тең болуы керек",
        range: "${label} ұзындығы ${min}-${max} таңба аралығында болуы керек"
      },
      number: {
        len: "${label} ${len} тең болуы керек",
        min: "${label} ${min} мәнінен үлкен немесе оған тең болуы керек",
        max: "${label} ${max} мәнінен аз немесе оған тең болуы керек"
      },
      array: {
        len: "${label} элементтерінің саны ${len} тең болуы керек",
        min: "${label} элементтерінің саны ${min} көп немесе оған тең болуы керек",
        max: "${label} элементтерінің саны ${max} аз немесе оған тең болуы керек",
        range: "${label} элементтерінің саны ${min} - ${max} аралығында болуы керек"
      },
      pattern: {
        mismatch: "${label} ${pattern} мен сәйкес келмейді"
      }
    }
  }
};
n.default = F;
var v = n;
const q = /* @__PURE__ */ k(v), R = /* @__PURE__ */ x({
  __proto__: null,
  default: q
}, [v]);
export {
  R as k
};
