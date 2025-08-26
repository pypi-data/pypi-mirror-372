import { c as g } from "./Index-WXKJnuTW.js";
import { i as o, o as v, c as x } from "./config-provider-C0s-_bDn.js";
function y(b, s) {
  for (var f = 0; f < s.length; f++) {
    const a = s[f];
    if (typeof a != "string" && !Array.isArray(a)) {
      for (const t in a)
        if (t !== "default" && !(t in b)) {
          const m = Object.getOwnPropertyDescriptor(a, t);
          m && Object.defineProperty(b, t, m.get ? m : {
            enumerable: !0,
            get: () => a[t]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(b, Symbol.toStringTag, {
    value: "Module"
  }));
}
var n = {}, i = {};
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
var P = {
  // Options
  items_per_page: "/ страница",
  jump_to: "Към",
  jump_to_confirm: "потвърждавам",
  page: "",
  // Pagination
  prev_page: "Предишна страница",
  next_page: "Следваща страница",
  prev_5: "Предишни 5 страници",
  next_5: "Следващи 5 страници",
  prev_3: "Предишни 3 страници",
  next_3: "Следващи 3 страници",
  page_size: "Page Size"
};
i.default = P;
var u = {}, l = {}, d = {}, j = o.default;
Object.defineProperty(d, "__esModule", {
  value: !0
});
d.default = void 0;
var p = j(v), B = x, G = (0, p.default)((0, p.default)({}, B.commonLocale), {}, {
  locale: "bg_BG",
  today: "Днес",
  now: "Сега",
  backToToday: "Към днес",
  ok: "Добре",
  clear: "Изчистване",
  week: "Седмица",
  month: "Месец",
  year: "Година",
  timeSelect: "Избор на час",
  dateSelect: "Избор на дата",
  monthSelect: "Избор на месец",
  yearSelect: "Избор на година",
  decadeSelect: "Десетилетие",
  dateFormat: "D M YYYY",
  dateTimeFormat: "D M YYYY HH:mm:ss",
  previousMonth: "Предишен месец (PageUp)",
  nextMonth: "Следващ месец (PageDown)",
  previousYear: "Последна година (Control + left)",
  nextYear: "Следваща година (Control + right)",
  previousDecade: "Предишно десетилетие",
  nextDecade: "Следващо десетилетие",
  previousCentury: "Последен век",
  nextCentury: "Следващ век"
});
d.default = G;
var r = {};
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
const h = {
  placeholder: "Избор на час"
};
r.default = h;
var _ = o.default;
Object.defineProperty(l, "__esModule", {
  value: !0
});
l.default = void 0;
var T = _(d), O = _(r);
const D = {
  lang: Object.assign({
    placeholder: "Избор на дата",
    rangePlaceholder: ["Начална", "Крайна"]
  }, T.default),
  timePickerLocale: Object.assign({}, O.default)
};
l.default = D;
var M = o.default;
Object.defineProperty(u, "__esModule", {
  value: !0
});
u.default = void 0;
var k = M(l);
u.default = k.default;
var c = o.default;
Object.defineProperty(n, "__esModule", {
  value: !0
});
n.default = void 0;
var S = c(i), Y = c(u), F = c(l), w = c(r);
const e = "${label} не е валиден ${type}", C = {
  locale: "bg",
  Pagination: S.default,
  DatePicker: F.default,
  TimePicker: w.default,
  Calendar: Y.default,
  global: {
    close: "Затвори"
  },
  Table: {
    filterTitle: "Филтриране",
    filterConfirm: "Добре",
    filterReset: "Нулриане",
    selectAll: "Избор на текуща страница",
    selectInvert: "Обръщане"
  },
  Tour: {
    Next: "Следващ",
    Previous: "Предишен",
    Finish: "Завърши"
  },
  Modal: {
    okText: "Добре",
    cancelText: "Отказ",
    justOkText: "Добре"
  },
  Popconfirm: {
    okText: "Добре",
    cancelText: "Отказ"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Търсене",
    itemUnit: "избор",
    itemsUnit: "избори"
  },
  Upload: {
    uploading: "Качване...",
    removeFile: "Премахване",
    uploadError: "Грешка при качването",
    previewFile: "Преглед",
    downloadFile: "Свали файл"
  },
  Empty: {
    description: "Няма данни"
  },
  Form: {
    optional: "（по желание）",
    defaultValidateMessages: {
      default: "грешка при проверка на полето ${label}",
      required: "Моля, въведете ${label}",
      enum: "${label} трябва да е един от [${enum}]",
      whitespace: "${label} Не може да бъде нулев знак",
      date: {
        format: "${label} невалиден формат на датата",
        parse: "${label} не може да се преобразува в дата",
        invalid: "${label} е невалидна дата"
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
        len: "${label} ще бъде ${len} знака",
        min: "${label} най-малко ${min} герои",
        max: "${label} повечето ${max} герои",
        range: "${label} Трябва да е вътре ${min}-${max} между знаци"
      },
      number: {
        len: "${label} трябва да е равно на ${len}",
        min: "${label} Минималната стойност е ${min}",
        max: "${label} Максималната стойност е ${max}",
        range: "${label} Трябва да е вътре ${min}-${max} между"
      },
      array: {
        len: "ще бъде ${len} индивидуален ${label}",
        min: "най-малко ${min} индивидуален ${label}",
        max: "повечето ${max} индивидуален ${label}",
        range: "${label} Количеството трябва да е вътре ${min}-${max} между"
      },
      pattern: {
        mismatch: "${label} не отговаря на модела ${pattern}"
      }
    }
  }
};
n.default = C;
var $ = n;
const q = /* @__PURE__ */ g($), U = /* @__PURE__ */ y({
  __proto__: null,
  default: q
}, [$]);
export {
  U as b
};
