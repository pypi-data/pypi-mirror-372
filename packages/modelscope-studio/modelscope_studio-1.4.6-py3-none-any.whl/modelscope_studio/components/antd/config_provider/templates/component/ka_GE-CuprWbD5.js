import { c as b } from "./Index-WXKJnuTW.js";
import { i as o, o as g, c as x } from "./config-provider-C0s-_bDn.js";
function k(s, f) {
  for (var m = 0; m < f.length; m++) {
    const a = f[m];
    if (typeof a != "string" && !Array.isArray(a)) {
      for (const l in a)
        if (l !== "default" && !(l in s)) {
          const p = Object.getOwnPropertyDescriptor(a, l);
          p && Object.defineProperty(s, l, p.get ? p : {
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
  items_per_page: "/ გვერდი.",
  jump_to: "გადასვლა",
  jump_to_confirm: "დადასტურება",
  page: "",
  // Pagination
  prev_page: "წინა გვერდი",
  next_page: "შემდეგი გვერდი",
  prev_5: "წინა 5 გვერდი",
  next_5: "შემდეგი 5 გვერდი",
  prev_3: "წინა 3 გვერდი",
  next_3: "შემდეგი 3 გვერდი",
  page_size: "Page Size"
};
i.default = y;
var c = {}, t = {}, d = {}, P = o.default;
Object.defineProperty(d, "__esModule", {
  value: !0
});
d.default = void 0;
var _ = P(g), h = x, E = (0, _.default)((0, _.default)({}, h.commonLocale), {}, {
  locale: "ka_GE",
  today: "დღეს",
  now: "ახლა",
  backToToday: "მიმდინარე თარიღი",
  ok: "OK",
  clear: "გასუფთავება",
  week: "კვირა",
  month: "თვე",
  year: "წელი",
  timeSelect: "დროის არჩევა",
  dateSelect: "თარიღის არჩევა",
  weekSelect: "კვირის არჩევა",
  monthSelect: "თვის არჩევა",
  yearSelect: "წლის არჩევა",
  decadeSelect: "ათწლეულის არჩევა",
  dateFormat: "M/D/YYYY",
  dateTimeFormat: "M/D/YYYY HH:mm:ss",
  previousMonth: "წინა თვე (PageUp)",
  nextMonth: "მომდევნო თვე (PageDown)",
  previousYear: "წინა წელი (Control + left)",
  nextYear: "მომდევნო წელი (Control + right)",
  previousDecade: "წინა ათწლეული",
  nextDecade: "მომდევნო ათწლეული",
  previousCentury: "გასული საუკუნე",
  nextCentury: "მომდევნო საუკუნე"
});
d.default = E;
var r = {};
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
const j = {
  placeholder: "აირჩიეთ დრო",
  rangePlaceholder: ["საწყისი თარიღი", "საბოლოო თარიღი"]
};
r.default = j;
var $ = o.default;
Object.defineProperty(t, "__esModule", {
  value: !0
});
t.default = void 0;
var T = $(d), G = $(r);
const O = {
  lang: Object.assign({
    placeholder: "აირჩიეთ თარიღი",
    yearPlaceholder: "აირჩიეთ წელი",
    quarterPlaceholder: "აირჩიეთ მეოთხედი",
    monthPlaceholder: "აირჩიეთ თვე",
    weekPlaceholder: "აირჩიეთ კვირა",
    rangePlaceholder: ["საწყისი თარიღი", "საბოლოო თარიღი"],
    rangeYearPlaceholder: ["საწყისი წელი", "საბოლოო წელი"],
    rangeMonthPlaceholder: ["საწყისი თვე", "საბოლოო თვე"],
    rangeWeekPlaceholder: ["საწყისი კვირა", "საბოლოო კვირა"]
  }, T.default),
  timePickerLocale: Object.assign({}, G.default)
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
var S = u(i), Y = u(c), w = u(t), C = u(r);
const e = "${label} არ არის სწორი ${type}", F = {
  locale: "ka",
  Pagination: S.default,
  DatePicker: w.default,
  TimePicker: C.default,
  Calendar: Y.default,
  global: {
    placeholder: "გთხოვთ აირჩიოთ",
    close: "დახურვა"
  },
  Table: {
    filterTitle: "ფილტრის მენიუ",
    filterConfirm: "კარგი",
    filterReset: "გასუფთავება",
    filterEmptyText: "ფილტრები არაა",
    emptyText: "ინფორმაცია არაა",
    selectAll: "აირჩიეთ მიმდინარე გვერდი",
    selectInvert: "შეაბრუნეთ მიმდინარე გვერდი",
    selectNone: "მონაცემების გასუფთავება",
    selectionAll: "ყველას მონიშვნა",
    sortTitle: "დალაგება",
    expand: "სტრიქონის გაშლა",
    collapse: "სტრიქონის შეკუმშვა",
    triggerDesc: "დაღმავალი დალაგება",
    triggerAsc: "აღმავალი დალაგება",
    cancelSort: "დალაგების გაუქმება"
  },
  Tour: {
    Next: "მომდევნო",
    Previous: "წინა",
    Finish: "დასრულება"
  },
  Modal: {
    okText: "კარგი",
    cancelText: "გაუქმება",
    justOkText: "ოკ"
  },
  Popconfirm: {
    okText: "კარგი",
    cancelText: "გაუქმება"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "მოძებნე აქ",
    itemUnit: "ერთეული",
    itemsUnit: "ერთეულები",
    remove: "ამოშლა",
    selectCurrent: "მიმდინარე გვერდის არჩევა",
    removeCurrent: "მიმდინარე გვერდის ამოშლა",
    selectAll: "ყველას მონიშვნა",
    removeAll: "ყველას წაშლა",
    selectInvert: "მიმდინარე გვერდის შებრუნება"
  },
  Upload: {
    uploading: "იტვირთება...",
    removeFile: "ფაილის ამოშლა",
    uploadError: "ატვირთვის შეცდომა",
    previewFile: "ფაილის გადახედვა",
    downloadFile: "ფაილის ჩამოტვირთვა"
  },
  Empty: {
    description: "ინფორმაცია არაა"
  },
  Icon: {
    icon: "ხატულა"
  },
  Text: {
    edit: "რედაქტირება",
    copy: "ასლი",
    copied: "ასლი აღებულია",
    expand: "გაშლა"
  },
  Form: {
    optional: "(არასავალდებულო)",
    defaultValidateMessages: {
      default: "ველის შემოწმების შეცდომა ${label}-ისთვის",
      required: "გთხოვთ შეიყვანეთ ${label}",
      enum: "${label} უნდა იყოს ერთ-ერთი [${enum}]-დან",
      whitespace: "${label} არ შეიძლება იყოს ცარიელი სიმბოლო",
      date: {
        format: "${label} თარიღის ფორმატი არასწორია",
        parse: "${label} თარიღში კონვერტირება არ არის შესაძლებელი",
        invalid: "${label} არასწორი თარიღია"
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
        len: "${label} უნდა იყოს ${len} სიმბოლო",
        min: "${label} უნდა იყოს სულ მცირე ${min} სიმბოლო",
        max: "${label} უნდა იყოს მაქსიმუმ ${max} სიმბოლო",
        range: "${label} უნდა იყოს ${min}-${max} სიმბოლოს შორის"
      },
      number: {
        len: "${label} უნდა იყოს ${len} ტოლი",
        min: "${label} უნდა იყოს მინუმიმ ${min}",
        max: "${label} უნდა იყოს მაქსიმუმ ${max}",
        range: "${label} უნდა იყოს ${min}-${max} შორის"
      },
      array: {
        len: "უნდა იყოს ${len} ${label}",
        min: "სულ მცირე ${min} ${label}",
        max: "არაუმეტეს ${max} ${label}",
        range: "${label}-ის რაოდენობა უნდა იყოს ${min}-${max} შორის"
      },
      pattern: {
        mismatch: "${label} არ ერგება შაბლონს ${pattern}"
      }
    }
  },
  Image: {
    preview: "გადახედვა"
  }
};
n.default = F;
var v = n;
const q = /* @__PURE__ */ b(v), I = /* @__PURE__ */ k({
  __proto__: null,
  default: q
}, [v]);
export {
  I as k
};
