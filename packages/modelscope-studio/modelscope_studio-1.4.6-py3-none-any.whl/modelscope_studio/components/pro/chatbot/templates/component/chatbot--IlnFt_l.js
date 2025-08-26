var Nn = (e) => {
  throw TypeError(e);
};
var Fn = (e, t, n) => t.has(e) || Nn("Cannot " + n);
var De = (e, t, n) => (Fn(e, t, "read from private field"), n ? n.call(e) : t.get(e)), On = (e, t, n) => t.has(e) ? Nn("Cannot add the same private member more than once") : t instanceof WeakSet ? t.add(e) : t.set(e, n), jn = (e, t, n, r) => (Fn(e, t, "write to private field"), r ? r.call(e, n) : t.set(e, n), n);
import { i as jo, a as ye, r as ko, b as Ao, Z as ft, g as zo, c as N, d as bn, e as mt, o as An } from "./Index-BhNTxK4Q.js";
const M = window.ms_globals.React, c = window.ms_globals.React, Mo = window.ms_globals.React.isValidElement, Lo = window.ms_globals.React.version, ne = window.ms_globals.React.useRef, No = window.ms_globals.React.useLayoutEffect, Ee = window.ms_globals.React.useEffect, Fo = window.ms_globals.React.useCallback, fe = window.ms_globals.React.useMemo, Oo = window.ms_globals.React.forwardRef, Ze = window.ms_globals.React.useState, kn = window.ms_globals.ReactDOM, yt = window.ms_globals.ReactDOM.createPortal, Nr = window.ms_globals.antdIcons.FileTextFilled, Do = window.ms_globals.antdIcons.CloseCircleFilled, Ho = window.ms_globals.antdIcons.FileExcelFilled, Bo = window.ms_globals.antdIcons.FileImageFilled, Wo = window.ms_globals.antdIcons.FileMarkdownFilled, Vo = window.ms_globals.antdIcons.FilePdfFilled, Xo = window.ms_globals.antdIcons.FilePptFilled, Uo = window.ms_globals.antdIcons.FileWordFilled, Go = window.ms_globals.antdIcons.FileZipFilled, qo = window.ms_globals.antdIcons.PlusOutlined, Ko = window.ms_globals.antdIcons.LeftOutlined, Yo = window.ms_globals.antdIcons.RightOutlined, Zo = window.ms_globals.antdIcons.CloseOutlined, Fr = window.ms_globals.antdIcons.CheckOutlined, Qo = window.ms_globals.antdIcons.DeleteOutlined, Jo = window.ms_globals.antdIcons.EditOutlined, es = window.ms_globals.antdIcons.SyncOutlined, ts = window.ms_globals.antdIcons.DislikeOutlined, ns = window.ms_globals.antdIcons.LikeOutlined, rs = window.ms_globals.antdIcons.CopyOutlined, os = window.ms_globals.antdIcons.EyeOutlined, ss = window.ms_globals.antdIcons.ArrowDownOutlined, is = window.ms_globals.antd.ConfigProvider, Qe = window.ms_globals.antd.theme, Or = window.ms_globals.antd.Upload, as = window.ms_globals.antd.Progress, ls = window.ms_globals.antd.Image, ae = window.ms_globals.antd.Button, Ce = window.ms_globals.antd.Flex, $e = window.ms_globals.antd.Typography, cs = window.ms_globals.antd.Avatar, us = window.ms_globals.antd.Popconfirm, ds = window.ms_globals.antd.Tooltip, fs = window.ms_globals.antd.Collapse, ms = window.ms_globals.antd.Input, jr = window.ms_globals.createItemsContext.createItemsContext, ps = window.ms_globals.internalContext.useContextPropsContext, zn = window.ms_globals.internalContext.ContextPropsProvider, Ve = window.ms_globals.antdCssinjs.unit, Vt = window.ms_globals.antdCssinjs.token2CSSVar, Dn = window.ms_globals.antdCssinjs.useStyleRegister, gs = window.ms_globals.antdCssinjs.useCSSVarRegister, hs = window.ms_globals.antdCssinjs.createTheme, ys = window.ms_globals.antdCssinjs.useCacheToken, kr = window.ms_globals.antdCssinjs.Keyframes, vt = window.ms_globals.components.Markdown;
var vs = /\s/;
function bs(e) {
  for (var t = e.length; t-- && vs.test(e.charAt(t)); )
    ;
  return t;
}
var xs = /^\s+/;
function Ss(e) {
  return e && e.slice(0, bs(e) + 1).replace(xs, "");
}
var Hn = NaN, ws = /^[-+]0x[0-9a-f]+$/i, _s = /^0b[01]+$/i, Es = /^0o[0-7]+$/i, Cs = parseInt;
function Bn(e) {
  if (typeof e == "number")
    return e;
  if (jo(e))
    return Hn;
  if (ye(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = ye(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Ss(e);
  var n = _s.test(e);
  return n || Es.test(e) ? Cs(e.slice(2), n ? 2 : 8) : ws.test(e) ? Hn : +e;
}
var Xt = function() {
  return ko.Date.now();
}, Ts = "Expected a function", $s = Math.max, Rs = Math.min;
function Is(e, t, n) {
  var r, o, s, i, a, l, u = 0, m = !1, f = !1, d = !0;
  if (typeof e != "function")
    throw new TypeError(Ts);
  t = Bn(t) || 0, ye(n) && (m = !!n.leading, f = "maxWait" in n, s = f ? $s(Bn(n.maxWait) || 0, t) : s, d = "trailing" in n ? !!n.trailing : d);
  function p(v) {
    var P = r, I = o;
    return r = o = void 0, u = v, i = e.apply(I, P), i;
  }
  function y(v) {
    return u = v, a = setTimeout(S, t), m ? p(v) : i;
  }
  function h(v) {
    var P = v - l, I = v - u, F = t - P;
    return f ? Rs(F, s - I) : F;
  }
  function g(v) {
    var P = v - l, I = v - u;
    return l === void 0 || P >= t || P < 0 || f && I >= s;
  }
  function S() {
    var v = Xt();
    if (g(v))
      return _(v);
    a = setTimeout(S, h(v));
  }
  function _(v) {
    return a = void 0, d && r ? p(v) : (r = o = void 0, i);
  }
  function w() {
    a !== void 0 && clearTimeout(a), u = 0, r = l = o = a = void 0;
  }
  function $() {
    return a === void 0 ? i : _(Xt());
  }
  function R() {
    var v = Xt(), P = g(v);
    if (r = arguments, o = this, l = v, P) {
      if (a === void 0)
        return y(l);
      if (f)
        return clearTimeout(a), a = setTimeout(S, t), p(l);
    }
    return a === void 0 && (a = setTimeout(S, t)), i;
  }
  return R.cancel = w, R.flush = $, R;
}
function Ps(e, t) {
  return Ao(e, t);
}
var Ar = {
  exports: {}
}, _t = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ms = c, Ls = Symbol.for("react.element"), Ns = Symbol.for("react.fragment"), Fs = Object.prototype.hasOwnProperty, Os = Ms.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, js = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function zr(e, t, n) {
  var r, o = {}, s = null, i = null;
  n !== void 0 && (s = "" + n), t.key !== void 0 && (s = "" + t.key), t.ref !== void 0 && (i = t.ref);
  for (r in t) Fs.call(t, r) && !js.hasOwnProperty(r) && (o[r] = t[r]);
  if (e && e.defaultProps) for (r in t = e.defaultProps, t) o[r] === void 0 && (o[r] = t[r]);
  return {
    $$typeof: Ls,
    type: e,
    key: s,
    ref: i,
    props: o,
    _owner: Os.current
  };
}
_t.Fragment = Ns;
_t.jsx = zr;
_t.jsxs = zr;
Ar.exports = _t;
var x = Ar.exports;
const {
  SvelteComponent: ks,
  assign: Wn,
  binding_callbacks: Vn,
  check_outros: As,
  children: Dr,
  claim_element: Hr,
  claim_space: zs,
  component_subscribe: Xn,
  compute_slots: Ds,
  create_slot: Hs,
  detach: He,
  element: Br,
  empty: Un,
  exclude_internal_props: Gn,
  get_all_dirty_from_scope: Bs,
  get_slot_changes: Ws,
  group_outros: Vs,
  init: Xs,
  insert_hydration: pt,
  safe_not_equal: Us,
  set_custom_element_data: Wr,
  space: Gs,
  transition_in: gt,
  transition_out: nn,
  update_slot_base: qs
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ks,
  getContext: Ys,
  onDestroy: Zs,
  setContext: Qs
} = window.__gradio__svelte__internal;
function qn(e) {
  let t, n;
  const r = (
    /*#slots*/
    e[7].default
  ), o = Hs(
    r,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = Br("svelte-slot"), o && o.c(), this.h();
    },
    l(s) {
      t = Hr(s, "SVELTE-SLOT", {
        class: !0
      });
      var i = Dr(t);
      o && o.l(i), i.forEach(He), this.h();
    },
    h() {
      Wr(t, "class", "svelte-1rt0kpf");
    },
    m(s, i) {
      pt(s, t, i), o && o.m(t, null), e[9](t), n = !0;
    },
    p(s, i) {
      o && o.p && (!n || i & /*$$scope*/
      64) && qs(
        o,
        r,
        s,
        /*$$scope*/
        s[6],
        n ? Ws(
          r,
          /*$$scope*/
          s[6],
          i,
          null
        ) : Bs(
          /*$$scope*/
          s[6]
        ),
        null
      );
    },
    i(s) {
      n || (gt(o, s), n = !0);
    },
    o(s) {
      nn(o, s), n = !1;
    },
    d(s) {
      s && He(t), o && o.d(s), e[9](null);
    }
  };
}
function Js(e) {
  let t, n, r, o, s = (
    /*$$slots*/
    e[4].default && qn(e)
  );
  return {
    c() {
      t = Br("react-portal-target"), n = Gs(), s && s.c(), r = Un(), this.h();
    },
    l(i) {
      t = Hr(i, "REACT-PORTAL-TARGET", {
        class: !0
      }), Dr(t).forEach(He), n = zs(i), s && s.l(i), r = Un(), this.h();
    },
    h() {
      Wr(t, "class", "svelte-1rt0kpf");
    },
    m(i, a) {
      pt(i, t, a), e[8](t), pt(i, n, a), s && s.m(i, a), pt(i, r, a), o = !0;
    },
    p(i, [a]) {
      /*$$slots*/
      i[4].default ? s ? (s.p(i, a), a & /*$$slots*/
      16 && gt(s, 1)) : (s = qn(i), s.c(), gt(s, 1), s.m(r.parentNode, r)) : s && (Vs(), nn(s, 1, 1, () => {
        s = null;
      }), As());
    },
    i(i) {
      o || (gt(s), o = !0);
    },
    o(i) {
      nn(s), o = !1;
    },
    d(i) {
      i && (He(t), He(n), He(r)), e[8](null), s && s.d(i);
    }
  };
}
function Kn(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function ei(e, t, n) {
  let r, o, {
    $$slots: s = {},
    $$scope: i
  } = t;
  const a = Ds(s);
  let {
    svelteInit: l
  } = t;
  const u = ft(Kn(t)), m = ft();
  Xn(e, m, ($) => n(0, r = $));
  const f = ft();
  Xn(e, f, ($) => n(1, o = $));
  const d = [], p = Ys("$$ms-gr-react-wrapper"), {
    slotKey: y,
    slotIndex: h,
    subSlotIndex: g
  } = zo() || {}, S = l({
    parent: p,
    props: u,
    target: m,
    slot: f,
    slotKey: y,
    slotIndex: h,
    subSlotIndex: g,
    onDestroy($) {
      d.push($);
    }
  });
  Qs("$$ms-gr-react-wrapper", S), Ks(() => {
    u.set(Kn(t));
  }), Zs(() => {
    d.forEach(($) => $());
  });
  function _($) {
    Vn[$ ? "unshift" : "push"](() => {
      r = $, m.set(r);
    });
  }
  function w($) {
    Vn[$ ? "unshift" : "push"](() => {
      o = $, f.set(o);
    });
  }
  return e.$$set = ($) => {
    n(17, t = Wn(Wn({}, t), Gn($))), "svelteInit" in $ && n(5, l = $.svelteInit), "$$scope" in $ && n(6, i = $.$$scope);
  }, t = Gn(t), [r, o, m, f, a, l, i, s, _, w];
}
class ti extends ks {
  constructor(t) {
    super(), Xs(this, t, ei, Js, Us, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: sc
} = window.__gradio__svelte__internal, Yn = window.ms_globals.rerender, Ut = window.ms_globals.tree;
function ni(e, t = {}) {
  function n(r) {
    const o = ft(), s = new ti({
      ...r,
      props: {
        svelteInit(i) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: e,
            props: i.props,
            slot: i.slot,
            target: i.target,
            slotIndex: i.slotIndex,
            subSlotIndex: i.subSlotIndex,
            ignore: t.ignore,
            slotKey: i.slotKey,
            nodes: []
          }, l = i.parent ?? Ut;
          return l.nodes = [...l.nodes, a], Yn({
            createPortal: yt,
            node: Ut
          }), i.onDestroy(() => {
            l.nodes = l.nodes.filter((u) => u.svelteInstance !== o), Yn({
              createPortal: yt,
              node: Ut
            });
          }), a;
        },
        ...r.props
      }
    });
    return o.set(s), s;
  }
  return new Promise((r) => {
    window.ms_globals.initializePromise.then(() => {
      r(n);
    });
  });
}
const ri = "1.6.0";
function ve() {
  return ve = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var n = arguments[t];
      for (var r in n) ({}).hasOwnProperty.call(n, r) && (e[r] = n[r]);
    }
    return e;
  }, ve.apply(null, arguments);
}
function re(e) {
  "@babel/helpers - typeof";
  return re = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, re(e);
}
function oi(e, t) {
  if (re(e) != "object" || !e) return e;
  var n = e[Symbol.toPrimitive];
  if (n !== void 0) {
    var r = n.call(e, t);
    if (re(r) != "object") return r;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function Vr(e) {
  var t = oi(e, "string");
  return re(t) == "symbol" ? t : t + "";
}
function A(e, t, n) {
  return (t = Vr(t)) in e ? Object.defineProperty(e, t, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = n, e;
}
function Zn(e, t) {
  var n = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var r = Object.getOwnPropertySymbols(e);
    t && (r = r.filter(function(o) {
      return Object.getOwnPropertyDescriptor(e, o).enumerable;
    })), n.push.apply(n, r);
  }
  return n;
}
function j(e) {
  for (var t = 1; t < arguments.length; t++) {
    var n = arguments[t] != null ? arguments[t] : {};
    t % 2 ? Zn(Object(n), !0).forEach(function(r) {
      A(e, r, n[r]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Zn(Object(n)).forEach(function(r) {
      Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(n, r));
    });
  }
  return e;
}
var si = `accept acceptCharset accessKey action allowFullScreen allowTransparency
    alt async autoComplete autoFocus autoPlay capture cellPadding cellSpacing challenge
    charSet checked classID className colSpan cols content contentEditable contextMenu
    controls coords crossOrigin data dateTime default defer dir disabled download draggable
    encType form formAction formEncType formMethod formNoValidate formTarget frameBorder
    headers height hidden high href hrefLang htmlFor httpEquiv icon id inputMode integrity
    is keyParams keyType kind label lang list loop low manifest marginHeight marginWidth max maxLength media
    mediaGroup method min minLength multiple muted name noValidate nonce open
    optimum pattern placeholder poster preload radioGroup readOnly rel required
    reversed role rowSpan rows sandbox scope scoped scrolling seamless selected
    shape size sizes span spellCheck src srcDoc srcLang srcSet start step style
    summary tabIndex target title type useMap value width wmode wrap`, ii = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, ai = "".concat(si, " ").concat(ii).split(/[\s\n]+/), li = "aria-", ci = "data-";
function Qn(e, t) {
  return e.indexOf(t) === 0;
}
function ui(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, n;
  t === !1 ? n = {
    aria: !0,
    data: !0,
    attr: !0
  } : t === !0 ? n = {
    aria: !0
  } : n = j({}, t);
  var r = {};
  return Object.keys(e).forEach(function(o) {
    // Aria
    (n.aria && (o === "role" || Qn(o, li)) || // Data
    n.data && Qn(o, ci) || // Attr
    n.attr && ai.includes(o)) && (r[o] = e[o]);
  }), r;
}
const di = /* @__PURE__ */ c.createContext({}), fi = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, Et = (e) => {
  const t = c.useContext(di);
  return c.useMemo(() => ({
    ...fi,
    ...t[e]
  }), [t[e]]);
};
function Re() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: r,
    theme: o
  } = c.useContext(is.ConfigContext);
  return {
    theme: o,
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: r
  };
}
function mi(e) {
  if (Array.isArray(e)) return e;
}
function pi(e, t) {
  var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (n != null) {
    var r, o, s, i, a = [], l = !0, u = !1;
    try {
      if (s = (n = n.call(e)).next, t === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (r = s.call(n)).done) && (a.push(r.value), a.length !== t); l = !0) ;
    } catch (m) {
      u = !0, o = m;
    } finally {
      try {
        if (!l && n.return != null && (i = n.return(), Object(i) !== i)) return;
      } finally {
        if (u) throw o;
      }
    }
    return a;
  }
}
function Jn(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
  return r;
}
function gi(e, t) {
  if (e) {
    if (typeof e == "string") return Jn(e, t);
    var n = {}.toString.call(e).slice(8, -1);
    return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? Jn(e, t) : void 0;
  }
}
function hi() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function oe(e, t) {
  return mi(e) || pi(e, t) || gi(e, t) || hi();
}
function Ge(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function er(e, t) {
  for (var n = 0; n < t.length; n++) {
    var r = t[n];
    r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, Vr(r.key), r);
  }
}
function qe(e, t, n) {
  return t && er(e.prototype, t), n && er(e, n), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function Le(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function rn(e, t) {
  return rn = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, r) {
    return n.__proto__ = r, n;
  }, rn(e, t);
}
function Ct(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && rn(e, t);
}
function bt(e) {
  return bt = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, bt(e);
}
function Xr() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Xr = function() {
    return !!e;
  })();
}
function yi(e, t) {
  if (t && (re(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return Le(e);
}
function Tt(e) {
  var t = Xr();
  return function() {
    var n, r = bt(e);
    if (t) {
      var o = bt(this).constructor;
      n = Reflect.construct(r, arguments, o);
    } else n = r.apply(this, arguments);
    return yi(this, n);
  };
}
var Ur = /* @__PURE__ */ qe(function e() {
  Ge(this, e);
}), Gr = "CALC_UNIT", vi = new RegExp(Gr, "g");
function Gt(e) {
  return typeof e == "number" ? "".concat(e).concat(Gr) : e;
}
var bi = /* @__PURE__ */ function(e) {
  Ct(n, e);
  var t = Tt(n);
  function n(r, o) {
    var s;
    Ge(this, n), s = t.call(this), A(Le(s), "result", ""), A(Le(s), "unitlessCssVar", void 0), A(Le(s), "lowPriority", void 0);
    var i = re(r);
    return s.unitlessCssVar = o, r instanceof n ? s.result = "(".concat(r.result, ")") : i === "number" ? s.result = Gt(r) : i === "string" && (s.result = r), s;
  }
  return qe(n, [{
    key: "add",
    value: function(o) {
      return o instanceof n ? this.result = "".concat(this.result, " + ").concat(o.getResult()) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " + ").concat(Gt(o))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(o) {
      return o instanceof n ? this.result = "".concat(this.result, " - ").concat(o.getResult()) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " - ").concat(Gt(o))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(o) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), o instanceof n ? this.result = "".concat(this.result, " * ").concat(o.getResult(!0)) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " * ").concat(o)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(o) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), o instanceof n ? this.result = "".concat(this.result, " / ").concat(o.getResult(!0)) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " / ").concat(o)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(o) {
      return this.lowPriority || o ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(o) {
      var s = this, i = o || {}, a = i.unit, l = !0;
      return typeof a == "boolean" ? l = a : Array.from(this.unitlessCssVar).some(function(u) {
        return s.result.includes(u);
      }) && (l = !1), this.result = this.result.replace(vi, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(Ur), xi = /* @__PURE__ */ function(e) {
  Ct(n, e);
  var t = Tt(n);
  function n(r) {
    var o;
    return Ge(this, n), o = t.call(this), A(Le(o), "result", 0), r instanceof n ? o.result = r.result : typeof r == "number" && (o.result = r), o;
  }
  return qe(n, [{
    key: "add",
    value: function(o) {
      return o instanceof n ? this.result += o.result : typeof o == "number" && (this.result += o), this;
    }
  }, {
    key: "sub",
    value: function(o) {
      return o instanceof n ? this.result -= o.result : typeof o == "number" && (this.result -= o), this;
    }
  }, {
    key: "mul",
    value: function(o) {
      return o instanceof n ? this.result *= o.result : typeof o == "number" && (this.result *= o), this;
    }
  }, {
    key: "div",
    value: function(o) {
      return o instanceof n ? this.result /= o.result : typeof o == "number" && (this.result /= o), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), n;
}(Ur), Si = function(t, n) {
  var r = t === "css" ? bi : xi;
  return function(o) {
    return new r(o, n);
  };
}, tr = function(t, n) {
  return "".concat([n, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function Ne(e) {
  var t = M.useRef();
  t.current = e;
  var n = M.useCallback(function() {
    for (var r, o = arguments.length, s = new Array(o), i = 0; i < o; i++)
      s[i] = arguments[i];
    return (r = t.current) === null || r === void 0 ? void 0 : r.call.apply(r, [t].concat(s));
  }, []);
  return n;
}
function $t() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var nr = $t() ? M.useLayoutEffect : M.useEffect, qr = function(t, n) {
  var r = M.useRef(!0);
  nr(function() {
    return t(r.current);
  }, n), nr(function() {
    return r.current = !1, function() {
      r.current = !0;
    };
  }, []);
}, rr = function(t, n) {
  qr(function(r) {
    if (!r)
      return t();
  }, n);
};
function Je(e) {
  var t = M.useRef(!1), n = M.useState(e), r = oe(n, 2), o = r[0], s = r[1];
  M.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function i(a, l) {
    l && t.current || s(a);
  }
  return [o, i];
}
function qt(e) {
  return e !== void 0;
}
function wi(e, t) {
  var n = t || {}, r = n.defaultValue, o = n.value, s = n.onChange, i = n.postState, a = Je(function() {
    return qt(o) ? o : qt(r) ? typeof r == "function" ? r() : r : typeof e == "function" ? e() : e;
  }), l = oe(a, 2), u = l[0], m = l[1], f = o !== void 0 ? o : u, d = i ? i(f) : f, p = Ne(s), y = Je([f]), h = oe(y, 2), g = h[0], S = h[1];
  rr(function() {
    var w = g[0];
    u !== w && p(u, w);
  }, [g]), rr(function() {
    qt(o) || m(o);
  }, [o]);
  var _ = Ne(function(w, $) {
    m(w, $), S([f], $);
  });
  return [d, _];
}
var Kr = {
  exports: {}
}, H = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var xn = Symbol.for("react.element"), Sn = Symbol.for("react.portal"), Rt = Symbol.for("react.fragment"), It = Symbol.for("react.strict_mode"), Pt = Symbol.for("react.profiler"), Mt = Symbol.for("react.provider"), Lt = Symbol.for("react.context"), _i = Symbol.for("react.server_context"), Nt = Symbol.for("react.forward_ref"), Ft = Symbol.for("react.suspense"), Ot = Symbol.for("react.suspense_list"), jt = Symbol.for("react.memo"), kt = Symbol.for("react.lazy"), Ei = Symbol.for("react.offscreen"), Yr;
Yr = Symbol.for("react.module.reference");
function me(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case xn:
        switch (e = e.type, e) {
          case Rt:
          case Pt:
          case It:
          case Ft:
          case Ot:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case _i:
              case Lt:
              case Nt:
              case kt:
              case jt:
              case Mt:
                return e;
              default:
                return t;
            }
        }
      case Sn:
        return t;
    }
  }
}
H.ContextConsumer = Lt;
H.ContextProvider = Mt;
H.Element = xn;
H.ForwardRef = Nt;
H.Fragment = Rt;
H.Lazy = kt;
H.Memo = jt;
H.Portal = Sn;
H.Profiler = Pt;
H.StrictMode = It;
H.Suspense = Ft;
H.SuspenseList = Ot;
H.isAsyncMode = function() {
  return !1;
};
H.isConcurrentMode = function() {
  return !1;
};
H.isContextConsumer = function(e) {
  return me(e) === Lt;
};
H.isContextProvider = function(e) {
  return me(e) === Mt;
};
H.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === xn;
};
H.isForwardRef = function(e) {
  return me(e) === Nt;
};
H.isFragment = function(e) {
  return me(e) === Rt;
};
H.isLazy = function(e) {
  return me(e) === kt;
};
H.isMemo = function(e) {
  return me(e) === jt;
};
H.isPortal = function(e) {
  return me(e) === Sn;
};
H.isProfiler = function(e) {
  return me(e) === Pt;
};
H.isStrictMode = function(e) {
  return me(e) === It;
};
H.isSuspense = function(e) {
  return me(e) === Ft;
};
H.isSuspenseList = function(e) {
  return me(e) === Ot;
};
H.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === Rt || e === Pt || e === It || e === Ft || e === Ot || e === Ei || typeof e == "object" && e !== null && (e.$$typeof === kt || e.$$typeof === jt || e.$$typeof === Mt || e.$$typeof === Lt || e.$$typeof === Nt || e.$$typeof === Yr || e.getModuleId !== void 0);
};
H.typeOf = me;
Kr.exports = H;
var Kt = Kr.exports, Ci = Symbol.for("react.element"), Ti = Symbol.for("react.transitional.element"), $i = Symbol.for("react.fragment");
function Ri(e) {
  return (
    // Base object type
    e && re(e) === "object" && // React Element type
    (e.$$typeof === Ci || e.$$typeof === Ti) && // React Fragment type
    e.type === $i
  );
}
var Ii = Number(Lo.split(".")[0]), Pi = function(t, n) {
  typeof t == "function" ? t(n) : re(t) === "object" && t && "current" in t && (t.current = n);
}, Mi = function(t) {
  var n, r;
  if (!t)
    return !1;
  if (Zr(t) && Ii >= 19)
    return !0;
  var o = Kt.isMemo(t) ? t.type.type : t.type;
  return !(typeof o == "function" && !((n = o.prototype) !== null && n !== void 0 && n.render) && o.$$typeof !== Kt.ForwardRef || typeof t == "function" && !((r = t.prototype) !== null && r !== void 0 && r.render) && t.$$typeof !== Kt.ForwardRef);
};
function Zr(e) {
  return /* @__PURE__ */ Mo(e) && !Ri(e);
}
var Li = function(t) {
  if (t && Zr(t)) {
    var n = t;
    return n.props.propertyIsEnumerable("ref") ? n.props.ref : n.ref;
  }
  return null;
};
function or(e, t, n, r) {
  var o = j({}, t[e]);
  if (r != null && r.deprecatedTokens) {
    var s = r.deprecatedTokens;
    s.forEach(function(a) {
      var l = oe(a, 2), u = l[0], m = l[1];
      if (o != null && o[u] || o != null && o[m]) {
        var f;
        (f = o[m]) !== null && f !== void 0 || (o[m] = o == null ? void 0 : o[u]);
      }
    });
  }
  var i = j(j({}, n), o);
  return Object.keys(i).forEach(function(a) {
    i[a] === t[a] && delete i[a];
  }), i;
}
var Qr = typeof CSSINJS_STATISTIC < "u", on = !0;
function Ke() {
  for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++)
    t[n] = arguments[n];
  if (!Qr)
    return Object.assign.apply(Object, [{}].concat(t));
  on = !1;
  var r = {};
  return t.forEach(function(o) {
    if (re(o) === "object") {
      var s = Object.keys(o);
      s.forEach(function(i) {
        Object.defineProperty(r, i, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return o[i];
          }
        });
      });
    }
  }), on = !0, r;
}
var sr = {};
function Ni() {
}
var Fi = function(t) {
  var n, r = t, o = Ni;
  return Qr && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), r = new Proxy(t, {
    get: function(i, a) {
      if (on) {
        var l;
        (l = n) === null || l === void 0 || l.add(a);
      }
      return i[a];
    }
  }), o = function(i, a) {
    var l;
    sr[i] = {
      global: Array.from(n),
      component: j(j({}, (l = sr[i]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: r,
    keys: n,
    flush: o
  };
};
function ir(e, t, n) {
  if (typeof n == "function") {
    var r;
    return n(Ke(t, (r = t[e]) !== null && r !== void 0 ? r : {}));
  }
  return n ?? {};
}
function Oi(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, r = new Array(n), o = 0; o < n; o++)
        r[o] = arguments[o];
      return "max(".concat(r.map(function(s) {
        return Ve(s);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, r = new Array(n), o = 0; o < n; o++)
        r[o] = arguments[o];
      return "min(".concat(r.map(function(s) {
        return Ve(s);
      }).join(","), ")");
    }
  };
}
var ji = 1e3 * 60 * 10, ki = /* @__PURE__ */ function() {
  function e() {
    Ge(this, e), A(this, "map", /* @__PURE__ */ new Map()), A(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), A(this, "nextID", 0), A(this, "lastAccessBeat", /* @__PURE__ */ new Map()), A(this, "accessBeat", 0);
  }
  return qe(e, [{
    key: "set",
    value: function(n, r) {
      this.clear();
      var o = this.getCompositeKey(n);
      this.map.set(o, r), this.lastAccessBeat.set(o, Date.now());
    }
  }, {
    key: "get",
    value: function(n) {
      var r = this.getCompositeKey(n), o = this.map.get(r);
      return this.lastAccessBeat.set(r, Date.now()), this.accessBeat += 1, o;
    }
  }, {
    key: "getCompositeKey",
    value: function(n) {
      var r = this, o = n.map(function(s) {
        return s && re(s) === "object" ? "obj_".concat(r.getObjectID(s)) : "".concat(re(s), "_").concat(s);
      });
      return o.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(n) {
      if (this.objectIDMap.has(n))
        return this.objectIDMap.get(n);
      var r = this.nextID;
      return this.objectIDMap.set(n, r), this.nextID += 1, r;
    }
  }, {
    key: "clear",
    value: function() {
      var n = this;
      if (this.accessBeat > 1e4) {
        var r = Date.now();
        this.lastAccessBeat.forEach(function(o, s) {
          r - o > ji && (n.map.delete(s), n.lastAccessBeat.delete(s));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), ar = new ki();
function Ai(e, t) {
  return c.useMemo(function() {
    var n = ar.get(t);
    if (n)
      return n;
    var r = e();
    return ar.set(t, r), r;
  }, t);
}
var zi = function() {
  return {};
};
function Di(e) {
  var t = e.useCSP, n = t === void 0 ? zi : t, r = e.useToken, o = e.usePrefix, s = e.getResetStyles, i = e.getCommonStyle, a = e.getCompUnitless;
  function l(d, p, y, h) {
    var g = Array.isArray(d) ? d[0] : d;
    function S(I) {
      return "".concat(String(g)).concat(I.slice(0, 1).toUpperCase()).concat(I.slice(1));
    }
    var _ = (h == null ? void 0 : h.unitless) || {}, w = typeof a == "function" ? a(d) : {}, $ = j(j({}, w), {}, A({}, S("zIndexPopup"), !0));
    Object.keys(_).forEach(function(I) {
      $[S(I)] = _[I];
    });
    var R = j(j({}, h), {}, {
      unitless: $,
      prefixToken: S
    }), v = m(d, p, y, R), P = u(g, y, R);
    return function(I) {
      var F = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : I, T = v(I, F), L = oe(T, 2), O = L[1], b = P(F), E = oe(b, 2), k = E[0], D = E[1];
      return [k, O, D];
    };
  }
  function u(d, p, y) {
    var h = y.unitless, g = y.injectStyle, S = g === void 0 ? !0 : g, _ = y.prefixToken, w = y.ignore, $ = function(P) {
      var I = P.rootCls, F = P.cssVar, T = F === void 0 ? {} : F, L = r(), O = L.realToken;
      return gs({
        path: [d],
        prefix: T.prefix,
        key: T.key,
        unitless: h,
        ignore: w,
        token: O,
        scope: I
      }, function() {
        var b = ir(d, O, p), E = or(d, O, b, {
          deprecatedTokens: y == null ? void 0 : y.deprecatedTokens
        });
        return Object.keys(b).forEach(function(k) {
          E[_(k)] = E[k], delete E[k];
        }), E;
      }), null;
    }, R = function(P) {
      var I = r(), F = I.cssVar;
      return [function(T) {
        return S && F ? /* @__PURE__ */ c.createElement(c.Fragment, null, /* @__PURE__ */ c.createElement($, {
          rootCls: P,
          cssVar: F,
          component: d
        }), T) : T;
      }, F == null ? void 0 : F.key];
    };
    return R;
  }
  function m(d, p, y) {
    var h = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = Array.isArray(d) ? d : [d, d], S = oe(g, 1), _ = S[0], w = g.join("-"), $ = e.layer || {
      name: "antd"
    };
    return function(R) {
      var v = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : R, P = r(), I = P.theme, F = P.realToken, T = P.hashId, L = P.token, O = P.cssVar, b = o(), E = b.rootPrefixCls, k = b.iconPrefixCls, D = n(), B = O ? "css" : "js", z = Ai(function() {
        var V = /* @__PURE__ */ new Set();
        return O && Object.keys(h.unitless || {}).forEach(function(K) {
          V.add(Vt(K, O.prefix)), V.add(Vt(K, tr(_, O.prefix)));
        }), Si(B, V);
      }, [B, _, O == null ? void 0 : O.prefix]), W = Oi(B), ie = W.max, G = W.min, J = {
        theme: I,
        token: L,
        hashId: T,
        nonce: function() {
          return D.nonce;
        },
        clientOnly: h.clientOnly,
        layer: $,
        // antd is always at top of styles
        order: h.order || -999
      };
      typeof s == "function" && Dn(j(j({}, J), {}, {
        clientOnly: !1,
        path: ["Shared", E]
      }), function() {
        return s(L, {
          prefix: {
            rootPrefixCls: E,
            iconPrefixCls: k
          },
          csp: D
        });
      });
      var U = Dn(j(j({}, J), {}, {
        path: [w, R, k]
      }), function() {
        if (h.injectStyle === !1)
          return [];
        var V = Fi(L), K = V.token, ee = V.flush, Z = ir(_, F, y), Se = ".".concat(R), je = or(_, F, Z, {
          deprecatedTokens: h.deprecatedTokens
        });
        O && Z && re(Z) === "object" && Object.keys(Z).forEach(function(ze) {
          Z[ze] = "var(".concat(Vt(ze, tr(_, O.prefix)), ")");
        });
        var ke = Ke(K, {
          componentCls: Se,
          prefixCls: R,
          iconCls: ".".concat(k),
          antCls: ".".concat(E),
          calc: z,
          // @ts-ignore
          max: ie,
          // @ts-ignore
          min: G
        }, O ? Z : je), Ae = p(ke, {
          hashId: T,
          prefixCls: R,
          rootPrefixCls: E,
          iconPrefixCls: k
        });
        ee(_, je);
        var we = typeof i == "function" ? i(ke, R, v, h.resetFont) : null;
        return [h.resetStyle === !1 ? null : we, Ae];
      });
      return [U, T];
    };
  }
  function f(d, p, y) {
    var h = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = m(d, p, y, j({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, h)), S = function(w) {
      var $ = w.prefixCls, R = w.rootCls, v = R === void 0 ? $ : R;
      return g($, v), null;
    };
    return S;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: f,
    genComponentStyleHook: m
  };
}
const Hi = {
  blue: "#1677FF",
  purple: "#722ED1",
  cyan: "#13C2C2",
  green: "#52C41A",
  magenta: "#EB2F96",
  /**
   * @deprecated Use magenta instead
   */
  pink: "#EB2F96",
  red: "#F5222D",
  orange: "#FA8C16",
  yellow: "#FADB14",
  volcano: "#FA541C",
  geekblue: "#2F54EB",
  gold: "#FAAD14",
  lime: "#A0D911"
}, Bi = Object.assign(Object.assign({}, Hi), {
  // Color
  colorPrimary: "#1677ff",
  colorSuccess: "#52c41a",
  colorWarning: "#faad14",
  colorError: "#ff4d4f",
  colorInfo: "#1677ff",
  colorLink: "",
  colorTextBase: "",
  colorBgBase: "",
  // Font
  fontFamily: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
'Noto Color Emoji'`,
  fontFamilyCode: "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace",
  fontSize: 14,
  // Line
  lineWidth: 1,
  lineType: "solid",
  // Motion
  motionUnit: 0.1,
  motionBase: 0,
  motionEaseOutCirc: "cubic-bezier(0.08, 0.82, 0.17, 1)",
  motionEaseInOutCirc: "cubic-bezier(0.78, 0.14, 0.15, 0.86)",
  motionEaseOut: "cubic-bezier(0.215, 0.61, 0.355, 1)",
  motionEaseInOut: "cubic-bezier(0.645, 0.045, 0.355, 1)",
  motionEaseOutBack: "cubic-bezier(0.12, 0.4, 0.29, 1.46)",
  motionEaseInBack: "cubic-bezier(0.71, -0.46, 0.88, 0.6)",
  motionEaseInQuint: "cubic-bezier(0.755, 0.05, 0.855, 0.06)",
  motionEaseOutQuint: "cubic-bezier(0.23, 1, 0.32, 1)",
  // Radius
  borderRadius: 6,
  // Size
  sizeUnit: 4,
  sizeStep: 4,
  sizePopupArrow: 16,
  // Control Base
  controlHeight: 32,
  // zIndex
  zIndexBase: 0,
  zIndexPopupBase: 1e3,
  // Image
  opacityImage: 1,
  // Wireframe
  wireframe: !1,
  // Motion
  motion: !0
}), Q = Math.round;
function Yt(e, t) {
  const n = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], r = n.map((o) => parseFloat(o));
  for (let o = 0; o < 3; o += 1)
    r[o] = t(r[o] || 0, n[o] || "", o);
  return n[3] ? r[3] = n[3].includes("%") ? r[3] / 100 : r[3] : r[3] = 1, r;
}
const lr = (e, t, n) => n === 0 ? e : e / 100;
function Ye(e, t) {
  const n = t || 255;
  return e > n ? n : e < 0 ? 0 : e;
}
class xe {
  constructor(t) {
    A(this, "isValid", !0), A(this, "r", 0), A(this, "g", 0), A(this, "b", 0), A(this, "a", 1), A(this, "_h", void 0), A(this, "_s", void 0), A(this, "_l", void 0), A(this, "_v", void 0), A(this, "_max", void 0), A(this, "_min", void 0), A(this, "_brightness", void 0);
    function n(r) {
      return r[0] in t && r[1] in t && r[2] in t;
    }
    if (t) if (typeof t == "string") {
      let o = function(s) {
        return r.startsWith(s);
      };
      const r = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(r) ? this.fromHexString(r) : o("rgb") ? this.fromRgbString(r) : o("hsl") ? this.fromHslString(r) : (o("hsv") || o("hsb")) && this.fromHsvString(r);
    } else if (t instanceof xe)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (n("rgb"))
      this.r = Ye(t.r), this.g = Ye(t.g), this.b = Ye(t.b), this.a = typeof t.a == "number" ? Ye(t.a, 1) : 1;
    else if (n("hsl"))
      this.fromHsl(t);
    else if (n("hsv"))
      this.fromHsv(t);
    else
      throw new Error("@ant-design/fast-color: unsupported input " + JSON.stringify(t));
  }
  // ======================= Setter =======================
  setR(t) {
    return this._sc("r", t);
  }
  setG(t) {
    return this._sc("g", t);
  }
  setB(t) {
    return this._sc("b", t);
  }
  setA(t) {
    return this._sc("a", t, 1);
  }
  setHue(t) {
    const n = this.toHsv();
    return n.h = t, this._c(n);
  }
  // ======================= Getter =======================
  /**
   * Returns the perceived luminance of a color, from 0-1.
   * @see http://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
   */
  getLuminance() {
    function t(s) {
      const i = s / 255;
      return i <= 0.03928 ? i / 12.92 : Math.pow((i + 0.055) / 1.055, 2.4);
    }
    const n = t(this.r), r = t(this.g), o = t(this.b);
    return 0.2126 * n + 0.7152 * r + 0.0722 * o;
  }
  getHue() {
    if (typeof this._h > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._h = 0 : this._h = Q(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
    }
    return this._h;
  }
  getSaturation() {
    if (typeof this._s > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._s = 0 : this._s = t / this.getMax();
    }
    return this._s;
  }
  getLightness() {
    return typeof this._l > "u" && (this._l = (this.getMax() + this.getMin()) / 510), this._l;
  }
  getValue() {
    return typeof this._v > "u" && (this._v = this.getMax() / 255), this._v;
  }
  /**
   * Returns the perceived brightness of the color, from 0-255.
   * Note: this is not the b of HSB
   * @see http://www.w3.org/TR/AERT#color-contrast
   */
  getBrightness() {
    return typeof this._brightness > "u" && (this._brightness = (this.r * 299 + this.g * 587 + this.b * 114) / 1e3), this._brightness;
  }
  // ======================== Func ========================
  darken(t = 10) {
    const n = this.getHue(), r = this.getSaturation();
    let o = this.getLightness() - t / 100;
    return o < 0 && (o = 0), this._c({
      h: n,
      s: r,
      l: o,
      a: this.a
    });
  }
  lighten(t = 10) {
    const n = this.getHue(), r = this.getSaturation();
    let o = this.getLightness() + t / 100;
    return o > 1 && (o = 1), this._c({
      h: n,
      s: r,
      l: o,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(t, n = 50) {
    const r = this._c(t), o = n / 100, s = (a) => (r[a] - this[a]) * o + this[a], i = {
      r: Q(s("r")),
      g: Q(s("g")),
      b: Q(s("b")),
      a: Q(s("a") * 100) / 100
    };
    return this._c(i);
  }
  /**
   * Mix the color with pure white, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return white.
   */
  tint(t = 10) {
    return this.mix({
      r: 255,
      g: 255,
      b: 255,
      a: 1
    }, t);
  }
  /**
   * Mix the color with pure black, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return black.
   */
  shade(t = 10) {
    return this.mix({
      r: 0,
      g: 0,
      b: 0,
      a: 1
    }, t);
  }
  onBackground(t) {
    const n = this._c(t), r = this.a + n.a * (1 - this.a), o = (s) => Q((this[s] * this.a + n[s] * n.a * (1 - this.a)) / r);
    return this._c({
      r: o("r"),
      g: o("g"),
      b: o("b"),
      a: r
    });
  }
  // ======================= Status =======================
  isDark() {
    return this.getBrightness() < 128;
  }
  isLight() {
    return this.getBrightness() >= 128;
  }
  // ======================== MISC ========================
  equals(t) {
    return this.r === t.r && this.g === t.g && this.b === t.b && this.a === t.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let t = "#";
    const n = (this.r || 0).toString(16);
    t += n.length === 2 ? n : "0" + n;
    const r = (this.g || 0).toString(16);
    t += r.length === 2 ? r : "0" + r;
    const o = (this.b || 0).toString(16);
    if (t += o.length === 2 ? o : "0" + o, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const s = Q(this.a * 255).toString(16);
      t += s.length === 2 ? s : "0" + s;
    }
    return t;
  }
  /** CSS support color pattern */
  toHsl() {
    return {
      h: this.getHue(),
      s: this.getSaturation(),
      l: this.getLightness(),
      a: this.a
    };
  }
  /** CSS support color pattern */
  toHslString() {
    const t = this.getHue(), n = Q(this.getSaturation() * 100), r = Q(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${t},${n}%,${r}%,${this.a})` : `hsl(${t},${n}%,${r}%)`;
  }
  /** Same as toHsb */
  toHsv() {
    return {
      h: this.getHue(),
      s: this.getSaturation(),
      v: this.getValue(),
      a: this.a
    };
  }
  toRgb() {
    return {
      r: this.r,
      g: this.g,
      b: this.b,
      a: this.a
    };
  }
  toRgbString() {
    return this.a !== 1 ? `rgba(${this.r},${this.g},${this.b},${this.a})` : `rgb(${this.r},${this.g},${this.b})`;
  }
  toString() {
    return this.toRgbString();
  }
  // ====================== Privates ======================
  /** Return a new FastColor object with one channel changed */
  _sc(t, n, r) {
    const o = this.clone();
    return o[t] = Ye(n, r), o;
  }
  _c(t) {
    return new this.constructor(t);
  }
  getMax() {
    return typeof this._max > "u" && (this._max = Math.max(this.r, this.g, this.b)), this._max;
  }
  getMin() {
    return typeof this._min > "u" && (this._min = Math.min(this.r, this.g, this.b)), this._min;
  }
  fromHexString(t) {
    const n = t.replace("#", "");
    function r(o, s) {
      return parseInt(n[o] + n[s || o], 16);
    }
    n.length < 6 ? (this.r = r(0), this.g = r(1), this.b = r(2), this.a = n[3] ? r(3) / 255 : 1) : (this.r = r(0, 1), this.g = r(2, 3), this.b = r(4, 5), this.a = n[6] ? r(6, 7) / 255 : 1);
  }
  fromHsl({
    h: t,
    s: n,
    l: r,
    a: o
  }) {
    if (this._h = t % 360, this._s = n, this._l = r, this.a = typeof o == "number" ? o : 1, n <= 0) {
      const d = Q(r * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let s = 0, i = 0, a = 0;
    const l = t / 60, u = (1 - Math.abs(2 * r - 1)) * n, m = u * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (s = u, i = m) : l >= 1 && l < 2 ? (s = m, i = u) : l >= 2 && l < 3 ? (i = u, a = m) : l >= 3 && l < 4 ? (i = m, a = u) : l >= 4 && l < 5 ? (s = m, a = u) : l >= 5 && l < 6 && (s = u, a = m);
    const f = r - u / 2;
    this.r = Q((s + f) * 255), this.g = Q((i + f) * 255), this.b = Q((a + f) * 255);
  }
  fromHsv({
    h: t,
    s: n,
    v: r,
    a: o
  }) {
    this._h = t % 360, this._s = n, this._v = r, this.a = typeof o == "number" ? o : 1;
    const s = Q(r * 255);
    if (this.r = s, this.g = s, this.b = s, n <= 0)
      return;
    const i = t / 60, a = Math.floor(i), l = i - a, u = Q(r * (1 - n) * 255), m = Q(r * (1 - n * l) * 255), f = Q(r * (1 - n * (1 - l)) * 255);
    switch (a) {
      case 0:
        this.g = f, this.b = u;
        break;
      case 1:
        this.r = m, this.b = u;
        break;
      case 2:
        this.r = u, this.b = f;
        break;
      case 3:
        this.r = u, this.g = m;
        break;
      case 4:
        this.r = f, this.g = u;
        break;
      case 5:
      default:
        this.g = u, this.b = m;
        break;
    }
  }
  fromHsvString(t) {
    const n = Yt(t, lr);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(t) {
    const n = Yt(t, lr);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(t) {
    const n = Yt(t, (r, o) => (
      // Convert percentage to number. e.g. 50% -> 128
      o.includes("%") ? Q(r / 100 * 255) : r
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function Zt(e) {
  return e >= 0 && e <= 255;
}
function st(e, t) {
  const {
    r: n,
    g: r,
    b: o,
    a: s
  } = new xe(e).toRgb();
  if (s < 1)
    return e;
  const {
    r: i,
    g: a,
    b: l
  } = new xe(t).toRgb();
  for (let u = 0.01; u <= 1; u += 0.01) {
    const m = Math.round((n - i * (1 - u)) / u), f = Math.round((r - a * (1 - u)) / u), d = Math.round((o - l * (1 - u)) / u);
    if (Zt(m) && Zt(f) && Zt(d))
      return new xe({
        r: m,
        g: f,
        b: d,
        a: Math.round(u * 100) / 100
      }).toRgbString();
  }
  return new xe({
    r: n,
    g: r,
    b: o,
    a: 1
  }).toRgbString();
}
var Wi = function(e, t) {
  var n = {};
  for (var r in e) Object.prototype.hasOwnProperty.call(e, r) && t.indexOf(r) < 0 && (n[r] = e[r]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var o = 0, r = Object.getOwnPropertySymbols(e); o < r.length; o++)
    t.indexOf(r[o]) < 0 && Object.prototype.propertyIsEnumerable.call(e, r[o]) && (n[r[o]] = e[r[o]]);
  return n;
};
function Vi(e) {
  const {
    override: t
  } = e, n = Wi(e, ["override"]), r = Object.assign({}, t);
  Object.keys(Bi).forEach((d) => {
    delete r[d];
  });
  const o = Object.assign(Object.assign({}, n), r), s = 480, i = 576, a = 768, l = 992, u = 1200, m = 1600;
  if (o.motion === !1) {
    const d = "0s";
    o.motionDurationFast = d, o.motionDurationMid = d, o.motionDurationSlow = d;
  }
  return Object.assign(Object.assign(Object.assign({}, o), {
    // ============== Background ============== //
    colorFillContent: o.colorFillSecondary,
    colorFillContentHover: o.colorFill,
    colorFillAlter: o.colorFillQuaternary,
    colorBgContainerDisabled: o.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: o.colorBgContainer,
    colorSplit: st(o.colorBorderSecondary, o.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: o.colorTextQuaternary,
    colorTextDisabled: o.colorTextQuaternary,
    colorTextHeading: o.colorText,
    colorTextLabel: o.colorTextSecondary,
    colorTextDescription: o.colorTextTertiary,
    colorTextLightSolid: o.colorWhite,
    colorHighlight: o.colorError,
    colorBgTextHover: o.colorFillSecondary,
    colorBgTextActive: o.colorFill,
    colorIcon: o.colorTextTertiary,
    colorIconHover: o.colorText,
    colorErrorOutline: st(o.colorErrorBg, o.colorBgContainer),
    colorWarningOutline: st(o.colorWarningBg, o.colorBgContainer),
    // Font
    fontSizeIcon: o.fontSizeSM,
    // Line
    lineWidthFocus: o.lineWidth * 3,
    // Control
    lineWidth: o.lineWidth,
    controlOutlineWidth: o.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: o.controlHeight / 2,
    controlItemBgHover: o.colorFillTertiary,
    controlItemBgActive: o.colorPrimaryBg,
    controlItemBgActiveHover: o.colorPrimaryBgHover,
    controlItemBgActiveDisabled: o.colorFill,
    controlTmpOutline: o.colorFillQuaternary,
    controlOutline: st(o.colorPrimaryBg, o.colorBgContainer),
    lineType: o.lineType,
    borderRadius: o.borderRadius,
    borderRadiusXS: o.borderRadiusXS,
    borderRadiusSM: o.borderRadiusSM,
    borderRadiusLG: o.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: o.sizeXXS,
    paddingXS: o.sizeXS,
    paddingSM: o.sizeSM,
    padding: o.size,
    paddingMD: o.sizeMD,
    paddingLG: o.sizeLG,
    paddingXL: o.sizeXL,
    paddingContentHorizontalLG: o.sizeLG,
    paddingContentVerticalLG: o.sizeMS,
    paddingContentHorizontal: o.sizeMS,
    paddingContentVertical: o.sizeSM,
    paddingContentHorizontalSM: o.size,
    paddingContentVerticalSM: o.sizeXS,
    marginXXS: o.sizeXXS,
    marginXS: o.sizeXS,
    marginSM: o.sizeSM,
    margin: o.size,
    marginMD: o.sizeMD,
    marginLG: o.sizeLG,
    marginXL: o.sizeXL,
    marginXXL: o.sizeXXL,
    boxShadow: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowSecondary: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowTertiary: `
      0 1px 2px 0 rgba(0, 0, 0, 0.03),
      0 1px 6px -1px rgba(0, 0, 0, 0.02),
      0 2px 4px 0 rgba(0, 0, 0, 0.02)
    `,
    screenXS: s,
    screenXSMin: s,
    screenXSMax: i - 1,
    screenSM: i,
    screenSMMin: i,
    screenSMMax: a - 1,
    screenMD: a,
    screenMDMin: a,
    screenMDMax: l - 1,
    screenLG: l,
    screenLGMin: l,
    screenLGMax: u - 1,
    screenXL: u,
    screenXLMin: u,
    screenXLMax: m - 1,
    screenXXL: m,
    screenXXLMin: m,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new xe("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new xe("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new xe("rgba(0, 0, 0, 0.09)").toRgbString()}
    `,
    boxShadowDrawerRight: `
      -6px 0 16px 0 rgba(0, 0, 0, 0.08),
      -3px 0 6px -4px rgba(0, 0, 0, 0.12),
      -9px 0 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerLeft: `
      6px 0 16px 0 rgba(0, 0, 0, 0.08),
      3px 0 6px -4px rgba(0, 0, 0, 0.12),
      9px 0 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerUp: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerDown: `
      0 -6px 16px 0 rgba(0, 0, 0, 0.08),
      0 -3px 6px -4px rgba(0, 0, 0, 0.12),
      0 -9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowTabsOverflowLeft: "inset 10px 0 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowRight: "inset -10px 0 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowTop: "inset 0 10px 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowBottom: "inset 0 -10px 8px -8px rgba(0, 0, 0, 0.08)"
  }), r);
}
const Xi = {
  lineHeight: !0,
  lineHeightSM: !0,
  lineHeightLG: !0,
  lineHeightHeading1: !0,
  lineHeightHeading2: !0,
  lineHeightHeading3: !0,
  lineHeightHeading4: !0,
  lineHeightHeading5: !0,
  opacityLoading: !0,
  fontWeightStrong: !0,
  zIndexPopupBase: !0,
  zIndexBase: !0,
  opacityImage: !0
}, Ui = {
  motionBase: !0,
  motionUnit: !0
}, Gi = hs(Qe.defaultAlgorithm), qi = {
  screenXS: !0,
  screenXSMin: !0,
  screenXSMax: !0,
  screenSM: !0,
  screenSMMin: !0,
  screenSMMax: !0,
  screenMD: !0,
  screenMDMin: !0,
  screenMDMax: !0,
  screenLG: !0,
  screenLGMin: !0,
  screenLGMax: !0,
  screenXL: !0,
  screenXLMin: !0,
  screenXLMax: !0,
  screenXXL: !0,
  screenXXLMin: !0
}, Jr = (e, t, n) => {
  const r = n.getDerivativeToken(e), {
    override: o,
    ...s
  } = t;
  let i = {
    ...r,
    override: o
  };
  return i = Vi(i), s && Object.entries(s).forEach(([a, l]) => {
    const {
      theme: u,
      ...m
    } = l;
    let f = m;
    u && (f = Jr({
      ...i,
      ...m
    }, {
      override: m
    }, u)), i[a] = f;
  }), i;
};
function Ki() {
  const {
    token: e,
    hashed: t,
    theme: n = Gi,
    override: r,
    cssVar: o
  } = c.useContext(Qe._internalContext), [s, i, a] = ys(n, [Qe.defaultSeed, e], {
    salt: `${ri}-${t || ""}`,
    override: r,
    getComputedToken: Jr,
    cssVar: o && {
      prefix: o.prefix,
      key: o.key,
      unitless: Xi,
      ignore: Ui,
      preserve: qi
    }
  });
  return [n, a, t ? i : "", s, o];
}
const {
  genStyleHooks: At
} = Di({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = Re();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, n, r, o] = Ki();
    return {
      theme: e,
      realToken: t,
      hashId: n,
      token: r,
      cssVar: o
    };
  },
  useCSP: () => {
    const {
      csp: e
    } = Re();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), rt = /* @__PURE__ */ c.createContext(null);
function cr(e) {
  const {
    getDropContainer: t,
    className: n,
    prefixCls: r,
    children: o
  } = e, {
    disabled: s
  } = c.useContext(rt), [i, a] = c.useState(), [l, u] = c.useState(null);
  if (c.useEffect(() => {
    const d = t == null ? void 0 : t();
    i !== d && a(d);
  }, [t]), c.useEffect(() => {
    if (i) {
      const d = () => {
        u(!0);
      }, p = (g) => {
        g.preventDefault();
      }, y = (g) => {
        g.relatedTarget || u(!1);
      }, h = (g) => {
        u(!1), g.preventDefault();
      };
      return document.addEventListener("dragenter", d), document.addEventListener("dragover", p), document.addEventListener("dragleave", y), document.addEventListener("drop", h), () => {
        document.removeEventListener("dragenter", d), document.removeEventListener("dragover", p), document.removeEventListener("dragleave", y), document.removeEventListener("drop", h);
      };
    }
  }, [!!i]), !(t && i && !s))
    return null;
  const f = `${r}-drop-area`;
  return /* @__PURE__ */ yt(/* @__PURE__ */ c.createElement("div", {
    className: N(f, n, {
      [`${f}-on-body`]: i.tagName === "BODY"
    }),
    style: {
      display: l ? "block" : "none"
    }
  }, o), i);
}
function ur(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function Yi(e) {
  return e && re(e) === "object" && ur(e.nativeElement) ? e.nativeElement : ur(e) ? e : null;
}
function Zi(e) {
  var t = Yi(e);
  if (t)
    return t;
  if (e instanceof c.Component) {
    var n;
    return (n = kn.findDOMNode) === null || n === void 0 ? void 0 : n.call(kn, e);
  }
  return null;
}
function Qi(e, t) {
  if (e == null) return {};
  var n = {};
  for (var r in e) if ({}.hasOwnProperty.call(e, r)) {
    if (t.indexOf(r) !== -1) continue;
    n[r] = e[r];
  }
  return n;
}
function dr(e, t) {
  if (e == null) return {};
  var n, r, o = Qi(e, t);
  if (Object.getOwnPropertySymbols) {
    var s = Object.getOwnPropertySymbols(e);
    for (r = 0; r < s.length; r++) n = s[r], t.indexOf(n) === -1 && {}.propertyIsEnumerable.call(e, n) && (o[n] = e[n]);
  }
  return o;
}
var Ji = /* @__PURE__ */ M.createContext({}), ea = /* @__PURE__ */ function(e) {
  Ct(n, e);
  var t = Tt(n);
  function n() {
    return Ge(this, n), t.apply(this, arguments);
  }
  return qe(n, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), n;
}(M.Component);
function ta(e) {
  var t = M.useReducer(function(a) {
    return a + 1;
  }, 0), n = oe(t, 2), r = n[1], o = M.useRef(e), s = Ne(function() {
    return o.current;
  }), i = Ne(function(a) {
    o.current = typeof a == "function" ? a(o.current) : a, r();
  });
  return [s, i];
}
var Te = "none", it = "appear", at = "enter", lt = "leave", fr = "none", ge = "prepare", Be = "start", We = "active", wn = "end", eo = "prepared";
function mr(e, t) {
  var n = {};
  return n[e.toLowerCase()] = t.toLowerCase(), n["Webkit".concat(e)] = "webkit".concat(t), n["Moz".concat(e)] = "moz".concat(t), n["ms".concat(e)] = "MS".concat(t), n["O".concat(e)] = "o".concat(t.toLowerCase()), n;
}
function na(e, t) {
  var n = {
    animationend: mr("Animation", "AnimationEnd"),
    transitionend: mr("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete n.animationend.animation, "TransitionEvent" in t || delete n.transitionend.transition), n;
}
var ra = na($t(), typeof window < "u" ? window : {}), to = {};
if ($t()) {
  var oa = document.createElement("div");
  to = oa.style;
}
var ct = {};
function no(e) {
  if (ct[e])
    return ct[e];
  var t = ra[e];
  if (t)
    for (var n = Object.keys(t), r = n.length, o = 0; o < r; o += 1) {
      var s = n[o];
      if (Object.prototype.hasOwnProperty.call(t, s) && s in to)
        return ct[e] = t[s], ct[e];
    }
  return "";
}
var ro = no("animationend"), oo = no("transitionend"), so = !!(ro && oo), pr = ro || "animationend", gr = oo || "transitionend";
function hr(e, t) {
  if (!e) return null;
  if (re(e) === "object") {
    var n = t.replace(/-\w/g, function(r) {
      return r[1].toUpperCase();
    });
    return e[n];
  }
  return "".concat(e, "-").concat(t);
}
const sa = function(e) {
  var t = ne();
  function n(o) {
    o && (o.removeEventListener(gr, e), o.removeEventListener(pr, e));
  }
  function r(o) {
    t.current && t.current !== o && n(t.current), o && o !== t.current && (o.addEventListener(gr, e), o.addEventListener(pr, e), t.current = o);
  }
  return M.useEffect(function() {
    return function() {
      n(t.current);
    };
  }, []), [r, n];
};
var io = $t() ? No : Ee, ao = function(t) {
  return +setTimeout(t, 16);
}, lo = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (ao = function(t) {
  return window.requestAnimationFrame(t);
}, lo = function(t) {
  return window.cancelAnimationFrame(t);
});
var yr = 0, _n = /* @__PURE__ */ new Map();
function co(e) {
  _n.delete(e);
}
var sn = function(t) {
  var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  yr += 1;
  var r = yr;
  function o(s) {
    if (s === 0)
      co(r), t();
    else {
      var i = ao(function() {
        o(s - 1);
      });
      _n.set(r, i);
    }
  }
  return o(n), r;
};
sn.cancel = function(e) {
  var t = _n.get(e);
  return co(e), lo(t);
};
const ia = function() {
  var e = M.useRef(null);
  function t() {
    sn.cancel(e.current);
  }
  function n(r) {
    var o = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var s = sn(function() {
      o <= 1 ? r({
        isCanceled: function() {
          return s !== e.current;
        }
      }) : n(r, o - 1);
    });
    e.current = s;
  }
  return M.useEffect(function() {
    return function() {
      t();
    };
  }, []), [n, t];
};
var aa = [ge, Be, We, wn], la = [ge, eo], uo = !1, ca = !0;
function fo(e) {
  return e === We || e === wn;
}
const ua = function(e, t, n) {
  var r = Je(fr), o = oe(r, 2), s = o[0], i = o[1], a = ia(), l = oe(a, 2), u = l[0], m = l[1];
  function f() {
    i(ge, !0);
  }
  var d = t ? la : aa;
  return io(function() {
    if (s !== fr && s !== wn) {
      var p = d.indexOf(s), y = d[p + 1], h = n(s);
      h === uo ? i(y, !0) : y && u(function(g) {
        function S() {
          g.isCanceled() || i(y, !0);
        }
        h === !0 ? S() : Promise.resolve(h).then(S);
      });
    }
  }, [e, s]), M.useEffect(function() {
    return function() {
      m();
    };
  }, []), [f, s];
};
function da(e, t, n, r) {
  var o = r.motionEnter, s = o === void 0 ? !0 : o, i = r.motionAppear, a = i === void 0 ? !0 : i, l = r.motionLeave, u = l === void 0 ? !0 : l, m = r.motionDeadline, f = r.motionLeaveImmediately, d = r.onAppearPrepare, p = r.onEnterPrepare, y = r.onLeavePrepare, h = r.onAppearStart, g = r.onEnterStart, S = r.onLeaveStart, _ = r.onAppearActive, w = r.onEnterActive, $ = r.onLeaveActive, R = r.onAppearEnd, v = r.onEnterEnd, P = r.onLeaveEnd, I = r.onVisibleChanged, F = Je(), T = oe(F, 2), L = T[0], O = T[1], b = ta(Te), E = oe(b, 2), k = E[0], D = E[1], B = Je(null), z = oe(B, 2), W = z[0], ie = z[1], G = k(), J = ne(!1), U = ne(null);
  function V() {
    return n();
  }
  var K = ne(!1);
  function ee() {
    D(Te), ie(null, !0);
  }
  var Z = Ne(function(te) {
    var Y = k();
    if (Y !== Te) {
      var le = V();
      if (!(te && !te.deadline && te.target !== le)) {
        var Ie = K.current, Pe;
        Y === it && Ie ? Pe = R == null ? void 0 : R(le, te) : Y === at && Ie ? Pe = v == null ? void 0 : v(le, te) : Y === lt && Ie && (Pe = P == null ? void 0 : P(le, te)), Ie && Pe !== !1 && ee();
      }
    }
  }), Se = sa(Z), je = oe(Se, 1), ke = je[0], Ae = function(Y) {
    switch (Y) {
      case it:
        return A(A(A({}, ge, d), Be, h), We, _);
      case at:
        return A(A(A({}, ge, p), Be, g), We, w);
      case lt:
        return A(A(A({}, ge, y), Be, S), We, $);
      default:
        return {};
    }
  }, we = M.useMemo(function() {
    return Ae(G);
  }, [G]), ze = ua(G, !e, function(te) {
    if (te === ge) {
      var Y = we[ge];
      return Y ? Y(V()) : uo;
    }
    if (C in we) {
      var le;
      ie(((le = we[C]) === null || le === void 0 ? void 0 : le.call(we, V(), null)) || null);
    }
    return C === We && G !== Te && (ke(V()), m > 0 && (clearTimeout(U.current), U.current = setTimeout(function() {
      Z({
        deadline: !0
      });
    }, m))), C === eo && ee(), ca;
  }), ot = oe(ze, 2), Wt = ot[0], C = ot[1], q = fo(C);
  K.current = q;
  var X = ne(null);
  io(function() {
    if (!(J.current && X.current === t)) {
      O(t);
      var te = J.current;
      J.current = !0;
      var Y;
      !te && t && a && (Y = it), te && t && s && (Y = at), (te && !t && u || !te && f && !t && u) && (Y = lt);
      var le = Ae(Y);
      Y && (e || le[ge]) ? (D(Y), Wt()) : D(Te), X.current = t;
    }
  }, [t]), Ee(function() {
    // Cancel appear
    (G === it && !a || // Cancel enter
    G === at && !s || // Cancel leave
    G === lt && !u) && D(Te);
  }, [a, s, u]), Ee(function() {
    return function() {
      J.current = !1, clearTimeout(U.current);
    };
  }, []);
  var pe = M.useRef(!1);
  Ee(function() {
    L && (pe.current = !0), L !== void 0 && G === Te && ((pe.current || L) && (I == null || I(L)), pe.current = !0);
  }, [L, G]);
  var de = W;
  return we[ge] && C === Be && (de = j({
    transition: "none"
  }, de)), [G, C, de, L ?? t];
}
function fa(e) {
  var t = e;
  re(e) === "object" && (t = e.transitionSupport);
  function n(o, s) {
    return !!(o.motionName && t && s !== !1);
  }
  var r = /* @__PURE__ */ M.forwardRef(function(o, s) {
    var i = o.visible, a = i === void 0 ? !0 : i, l = o.removeOnLeave, u = l === void 0 ? !0 : l, m = o.forceRender, f = o.children, d = o.motionName, p = o.leavedClassName, y = o.eventProps, h = M.useContext(Ji), g = h.motion, S = n(o, g), _ = ne(), w = ne();
    function $() {
      try {
        return _.current instanceof HTMLElement ? _.current : Zi(w.current);
      } catch {
        return null;
      }
    }
    var R = da(S, a, $, o), v = oe(R, 4), P = v[0], I = v[1], F = v[2], T = v[3], L = M.useRef(T);
    T && (L.current = !0);
    var O = M.useCallback(function(z) {
      _.current = z, Pi(s, z);
    }, [s]), b, E = j(j({}, y), {}, {
      visible: a
    });
    if (!f)
      b = null;
    else if (P === Te)
      T ? b = f(j({}, E), O) : !u && L.current && p ? b = f(j(j({}, E), {}, {
        className: p
      }), O) : m || !u && !p ? b = f(j(j({}, E), {}, {
        style: {
          display: "none"
        }
      }), O) : b = null;
    else {
      var k;
      I === ge ? k = "prepare" : fo(I) ? k = "active" : I === Be && (k = "start");
      var D = hr(d, "".concat(P, "-").concat(k));
      b = f(j(j({}, E), {}, {
        className: N(hr(d, P), A(A({}, D, D && k), d, typeof d == "string")),
        style: F
      }), O);
    }
    if (/* @__PURE__ */ M.isValidElement(b) && Mi(b)) {
      var B = Li(b);
      B || (b = /* @__PURE__ */ M.cloneElement(b, {
        ref: O
      }));
    }
    return /* @__PURE__ */ M.createElement(ea, {
      ref: w
    }, b);
  });
  return r.displayName = "CSSMotion", r;
}
const ma = fa(so);
var an = "add", ln = "keep", cn = "remove", Qt = "removed";
function pa(e) {
  var t;
  return e && re(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, j(j({}, t), {}, {
    key: String(t.key)
  });
}
function un() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(pa);
}
function ga() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], n = [], r = 0, o = t.length, s = un(e), i = un(t);
  s.forEach(function(u) {
    for (var m = !1, f = r; f < o; f += 1) {
      var d = i[f];
      if (d.key === u.key) {
        r < f && (n = n.concat(i.slice(r, f).map(function(p) {
          return j(j({}, p), {}, {
            status: an
          });
        })), r = f), n.push(j(j({}, d), {}, {
          status: ln
        })), r += 1, m = !0;
        break;
      }
    }
    m || n.push(j(j({}, u), {}, {
      status: cn
    }));
  }), r < o && (n = n.concat(i.slice(r).map(function(u) {
    return j(j({}, u), {}, {
      status: an
    });
  })));
  var a = {};
  n.forEach(function(u) {
    var m = u.key;
    a[m] = (a[m] || 0) + 1;
  });
  var l = Object.keys(a).filter(function(u) {
    return a[u] > 1;
  });
  return l.forEach(function(u) {
    n = n.filter(function(m) {
      var f = m.key, d = m.status;
      return f !== u || d !== cn;
    }), n.forEach(function(m) {
      m.key === u && (m.status = ln);
    });
  }), n;
}
var ha = ["component", "children", "onVisibleChanged", "onAllRemoved"], ya = ["status"], va = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function ba(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : ma, n = /* @__PURE__ */ function(r) {
    Ct(s, r);
    var o = Tt(s);
    function s() {
      var i;
      Ge(this, s);
      for (var a = arguments.length, l = new Array(a), u = 0; u < a; u++)
        l[u] = arguments[u];
      return i = o.call.apply(o, [this].concat(l)), A(Le(i), "state", {
        keyEntities: []
      }), A(Le(i), "removeKey", function(m) {
        i.setState(function(f) {
          var d = f.keyEntities.map(function(p) {
            return p.key !== m ? p : j(j({}, p), {}, {
              status: Qt
            });
          });
          return {
            keyEntities: d
          };
        }, function() {
          var f = i.state.keyEntities, d = f.filter(function(p) {
            var y = p.status;
            return y !== Qt;
          }).length;
          d === 0 && i.props.onAllRemoved && i.props.onAllRemoved();
        });
      }), i;
    }
    return qe(s, [{
      key: "render",
      value: function() {
        var a = this, l = this.state.keyEntities, u = this.props, m = u.component, f = u.children, d = u.onVisibleChanged;
        u.onAllRemoved;
        var p = dr(u, ha), y = m || M.Fragment, h = {};
        return va.forEach(function(g) {
          h[g] = p[g], delete p[g];
        }), delete p.keys, /* @__PURE__ */ M.createElement(y, p, l.map(function(g, S) {
          var _ = g.status, w = dr(g, ya), $ = _ === an || _ === ln;
          return /* @__PURE__ */ M.createElement(t, ve({}, h, {
            key: w.key,
            visible: $,
            eventProps: w,
            onVisibleChanged: function(v) {
              d == null || d(v, {
                key: w.key
              }), v || a.removeKey(w.key);
            }
          }), function(R, v) {
            return f(j(j({}, R), {}, {
              index: S
            }), v);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, l) {
        var u = a.keys, m = l.keyEntities, f = un(u), d = ga(m, f);
        return {
          keyEntities: d.filter(function(p) {
            var y = m.find(function(h) {
              var g = h.key;
              return p.key === g;
            });
            return !(y && y.status === Qt && p.status === cn);
          })
        };
      }
    }]), s;
  }(M.Component);
  return A(n, "defaultProps", {
    component: "div"
  }), n;
}
const xa = ba(so);
function Sa(e, t) {
  const {
    children: n,
    upload: r,
    rootClassName: o
  } = e, s = c.useRef(null);
  return c.useImperativeHandle(t, () => s.current), /* @__PURE__ */ c.createElement(Or, ve({}, r, {
    showUploadList: !1,
    rootClassName: o,
    ref: s
  }), n);
}
const mo = /* @__PURE__ */ c.forwardRef(Sa), wa = (e) => {
  const {
    componentCls: t,
    antCls: n,
    calc: r
  } = e, o = `${t}-list-card`, s = r(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [o]: {
      borderRadius: e.borderRadius,
      position: "relative",
      background: e.colorFillContent,
      borderWidth: e.lineWidth,
      borderStyle: "solid",
      borderColor: "transparent",
      flex: "none",
      // =============================== Desc ================================
      [`${o}-name,${o}-desc`]: {
        display: "flex",
        flexWrap: "nowrap",
        maxWidth: "100%"
      },
      [`${o}-ellipsis-prefix`]: {
        flex: "0 1 auto",
        minWidth: 0,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap"
      },
      [`${o}-ellipsis-suffix`]: {
        flex: "none"
      },
      // ============================= Overview ==============================
      "&-type-overview": {
        padding: r(e.paddingSM).sub(e.lineWidth).equal(),
        paddingInlineStart: r(e.padding).add(e.lineWidth).equal(),
        display: "flex",
        flexWrap: "nowrap",
        gap: e.paddingXS,
        alignItems: "flex-start",
        width: 236,
        // Icon
        [`${o}-icon`]: {
          fontSize: r(e.fontSizeLG).mul(2).equal(),
          lineHeight: 1,
          paddingTop: r(e.paddingXXS).mul(1.5).equal(),
          flex: "none"
        },
        // Content
        [`${o}-content`]: {
          flex: "auto",
          minWidth: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch"
        },
        [`${o}-desc`]: {
          color: e.colorTextTertiary
        }
      },
      // ============================== Preview ==============================
      "&-type-preview": {
        width: s,
        height: s,
        lineHeight: 1,
        display: "flex",
        alignItems: "center",
        [`&:not(${o}-status-error)`]: {
          border: 0
        },
        // Img
        [`${n}-image`]: {
          width: "100%",
          height: "100%",
          borderRadius: "inherit",
          position: "relative",
          overflow: "hidden",
          img: {
            height: "100%",
            objectFit: "cover",
            borderRadius: "inherit"
          }
        },
        // Mask
        [`${o}-img-mask`]: {
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          borderRadius: "inherit",
          background: `rgba(0, 0, 0, ${e.opacityLoading})`
        },
        // Error
        [`&${o}-status-error`]: {
          borderRadius: "inherit",
          [`img, ${o}-img-mask`]: {
            borderRadius: r(e.borderRadius).sub(e.lineWidth).equal()
          },
          [`${o}-desc`]: {
            paddingInline: e.paddingXXS
          }
        },
        // Progress
        [`${o}-progress`]: {}
      },
      // ============================ Remove Icon ============================
      [`${o}-remove`]: {
        position: "absolute",
        top: 0,
        insetInlineEnd: 0,
        border: 0,
        padding: e.paddingXXS,
        background: "transparent",
        lineHeight: 1,
        transform: "translate(50%, -50%)",
        fontSize: e.fontSize,
        cursor: "pointer",
        opacity: e.opacityLoading,
        display: "none",
        "&:dir(rtl)": {
          transform: "translate(-50%, -50%)"
        },
        "&:hover": {
          opacity: 1
        },
        "&:active": {
          opacity: e.opacityLoading
        }
      },
      [`&:hover ${o}-remove`]: {
        display: "block"
      },
      // ============================== Status ===============================
      "&-status-error": {
        borderColor: e.colorError,
        [`${o}-desc`]: {
          color: e.colorError
        }
      },
      // ============================== Motion ===============================
      "&-motion": {
        transition: ["opacity", "width", "margin", "padding"].map((i) => `${i} ${e.motionDurationSlow}`).join(","),
        "&-appear-start": {
          width: 0,
          transition: "none"
        },
        "&-leave-active": {
          opacity: 0,
          width: 0,
          paddingInline: 0,
          borderInlineWidth: 0,
          marginInlineEnd: r(e.paddingSM).mul(-1).equal()
        }
      }
    }
  };
}, dn = {
  "&, *": {
    boxSizing: "border-box"
  }
}, _a = (e) => {
  const {
    componentCls: t,
    calc: n,
    antCls: r
  } = e, o = `${t}-drop-area`, s = `${t}-placeholder`;
  return {
    // ============================== Full Screen ==============================
    [o]: {
      position: "absolute",
      inset: 0,
      zIndex: e.zIndexPopupBase,
      ...dn,
      "&-on-body": {
        position: "fixed",
        inset: 0
      },
      "&-hide-placement": {
        [`${s}-inner`]: {
          display: "none"
        }
      },
      [s]: {
        padding: 0
      }
    },
    "&": {
      // ============================= Placeholder =============================
      [s]: {
        height: "100%",
        borderRadius: e.borderRadius,
        borderWidth: e.lineWidthBold,
        borderStyle: "dashed",
        borderColor: "transparent",
        padding: e.padding,
        position: "relative",
        backdropFilter: "blur(10px)",
        background: e.colorBgPlaceholderHover,
        ...dn,
        [`${r}-upload-wrapper ${r}-upload${r}-upload-btn`]: {
          padding: 0
        },
        [`&${s}-drag-in`]: {
          borderColor: e.colorPrimaryHover
        },
        [`&${s}-disabled`]: {
          opacity: 0.25,
          pointerEvents: "none"
        },
        [`${s}-inner`]: {
          gap: n(e.paddingXXS).div(2).equal()
        },
        [`${s}-icon`]: {
          fontSize: e.fontSizeHeading2,
          lineHeight: 1
        },
        [`${s}-title${s}-title`]: {
          margin: 0,
          fontSize: e.fontSize,
          lineHeight: e.lineHeight
        },
        [`${s}-description`]: {}
      }
    }
  };
}, Ea = (e) => {
  const {
    componentCls: t,
    calc: n
  } = e, r = `${t}-list`, o = n(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [t]: {
      position: "relative",
      width: "100%",
      ...dn,
      // =============================== File List ===============================
      [r]: {
        display: "flex",
        flexWrap: "wrap",
        gap: e.paddingSM,
        fontSize: e.fontSize,
        lineHeight: e.lineHeight,
        color: e.colorText,
        paddingBlock: e.paddingSM,
        paddingInline: e.padding,
        width: "100%",
        background: e.colorBgContainer,
        // Hide scrollbar
        scrollbarWidth: "none",
        "-ms-overflow-style": "none",
        "&::-webkit-scrollbar": {
          display: "none"
        },
        // Scroll
        "&-overflow-scrollX, &-overflow-scrollY": {
          "&:before, &:after": {
            content: '""',
            position: "absolute",
            opacity: 0,
            transition: `opacity ${e.motionDurationSlow}`,
            zIndex: 1
          }
        },
        "&-overflow-ping-start:before": {
          opacity: 1
        },
        "&-overflow-ping-end:after": {
          opacity: 1
        },
        "&-overflow-scrollX": {
          overflowX: "auto",
          overflowY: "hidden",
          flexWrap: "nowrap",
          "&:before, &:after": {
            insetBlock: 0,
            width: 8
          },
          "&:before": {
            insetInlineStart: 0,
            background: "linear-gradient(to right, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          },
          "&:after": {
            insetInlineEnd: 0,
            background: "linear-gradient(to left, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          },
          "&:dir(rtl)": {
            "&:before": {
              background: "linear-gradient(to left, rgba(0,0,0,0.06), rgba(0,0,0,0));"
            },
            "&:after": {
              background: "linear-gradient(to right, rgba(0,0,0,0.06), rgba(0,0,0,0));"
            }
          }
        },
        "&-overflow-scrollY": {
          overflowX: "hidden",
          overflowY: "auto",
          maxHeight: n(o).mul(3).equal(),
          "&:before, &:after": {
            insetInline: 0,
            height: 8
          },
          "&:before": {
            insetBlockStart: 0,
            background: "linear-gradient(to bottom, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          },
          "&:after": {
            insetBlockEnd: 0,
            background: "linear-gradient(to top, rgba(0,0,0,0.06), rgba(0,0,0,0));"
          }
        },
        // ======================================================================
        // ==                              Upload                              ==
        // ======================================================================
        "&-upload-btn": {
          width: o,
          height: o,
          fontSize: e.fontSizeHeading2,
          color: "#999"
        },
        // ======================================================================
        // ==                             PrevNext                             ==
        // ======================================================================
        "&-prev-btn, &-next-btn": {
          position: "absolute",
          top: "50%",
          transform: "translateY(-50%)",
          boxShadow: e.boxShadowTertiary,
          opacity: 0,
          pointerEvents: "none"
        },
        "&-prev-btn": {
          left: {
            _skip_check_: !0,
            value: e.padding
          }
        },
        "&-next-btn": {
          right: {
            _skip_check_: !0,
            value: e.padding
          }
        },
        "&:dir(ltr)": {
          [`&${r}-overflow-ping-start ${r}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${r}-overflow-ping-end ${r}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        },
        "&:dir(rtl)": {
          [`&${r}-overflow-ping-end ${r}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${r}-overflow-ping-start ${r}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        }
      }
    }
  };
}, Ca = (e) => {
  const {
    colorBgContainer: t
  } = e;
  return {
    colorBgPlaceholderHover: new xe(t).setA(0.85).toRgbString()
  };
}, po = At("Attachments", (e) => {
  const t = Ke(e, {});
  return [_a(t), Ea(t), wa(t)];
}, Ca), Ta = (e) => e.indexOf("image/") === 0, ut = 200;
function $a(e) {
  return new Promise((t) => {
    if (!e || !e.type || !Ta(e.type)) {
      t("");
      return;
    }
    const n = new Image();
    if (n.onload = () => {
      const {
        width: r,
        height: o
      } = n, s = r / o, i = s > 1 ? ut : ut * s, a = s > 1 ? ut / s : ut, l = document.createElement("canvas");
      l.width = i, l.height = a, l.style.cssText = `position: fixed; left: 0; top: 0; width: ${i}px; height: ${a}px; z-index: 9999; display: none;`, document.body.appendChild(l), l.getContext("2d").drawImage(n, 0, 0, i, a);
      const m = l.toDataURL();
      document.body.removeChild(l), window.URL.revokeObjectURL(n.src), t(m);
    }, n.crossOrigin = "anonymous", e.type.startsWith("image/svg+xml")) {
      const r = new FileReader();
      r.onload = () => {
        r.result && typeof r.result == "string" && (n.src = r.result);
      }, r.readAsDataURL(e);
    } else if (e.type.startsWith("image/gif")) {
      const r = new FileReader();
      r.onload = () => {
        r.result && t(r.result);
      }, r.readAsDataURL(e);
    } else
      n.src = window.URL.createObjectURL(e);
  });
}
function Ra() {
  return /* @__PURE__ */ c.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    //xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ c.createElement("title", null, "audio"), /* @__PURE__ */ c.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ c.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M10.7315824,7.11216117 C10.7428131,7.15148751 10.7485063,7.19218979 10.7485063,7.23309113 L10.7485063,8.07742614 C10.7484199,8.27364959 10.6183424,8.44607275 10.4296853,8.50003683 L8.32984514,9.09986306 L8.32984514,11.7071803 C8.32986605,12.5367078 7.67249692,13.217028 6.84345686,13.2454634 L6.79068592,13.2463395 C6.12766108,13.2463395 5.53916361,12.8217001 5.33010655,12.1924966 C5.1210495,11.563293 5.33842118,10.8709227 5.86959669,10.4741173 C6.40077221,10.0773119 7.12636292,10.0652587 7.67042486,10.4442027 L7.67020842,7.74937024 L7.68449368,7.74937024 C7.72405122,7.59919041 7.83988806,7.48101083 7.98924584,7.4384546 L10.1880418,6.81004755 C10.42156,6.74340323 10.6648954,6.87865515 10.7315824,7.11216117 Z M9.60714286,1.31785714 L12.9678571,4.67857143 L9.60714286,4.67857143 L9.60714286,1.31785714 Z",
    fill: "currentColor"
  })));
}
function Ia(e) {
  const {
    percent: t
  } = e, {
    token: n
  } = Qe.useToken();
  return /* @__PURE__ */ c.createElement(as, {
    type: "circle",
    percent: t,
    size: n.fontSizeHeading2 * 2,
    strokeColor: "#FFF",
    trailColor: "rgba(255, 255, 255, 0.3)",
    format: (r) => /* @__PURE__ */ c.createElement("span", {
      style: {
        color: "#FFF"
      }
    }, (r || 0).toFixed(0), "%")
  });
}
function Pa() {
  return /* @__PURE__ */ c.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    // xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ c.createElement("title", null, "video"), /* @__PURE__ */ c.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ c.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M12.9678571,4.67857143 L9.60714286,1.31785714 L9.60714286,4.67857143 L12.9678571,4.67857143 Z M10.5379461,10.3101106 L6.68957555,13.0059749 C6.59910784,13.0693494 6.47439406,13.0473861 6.41101953,12.9569184 C6.3874624,12.9232903 6.37482581,12.8832269 6.37482581,12.8421686 L6.37482581,7.45043999 C6.37482581,7.33998304 6.46436886,7.25043999 6.57482581,7.25043999 C6.61588409,7.25043999 6.65594753,7.26307658 6.68957555,7.28663371 L10.5379461,9.98249803 C10.6284138,10.0458726 10.6503772,10.1705863 10.5870027,10.2610541 C10.5736331,10.2801392 10.5570312,10.2967411 10.5379461,10.3101106 Z",
    fill: "currentColor"
  })));
}
const Jt = " ", ht = "#8c8c8c", go = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"], vr = [{
  key: "default",
  icon: /* @__PURE__ */ c.createElement(Nr, null),
  color: ht,
  ext: []
}, {
  key: "excel",
  icon: /* @__PURE__ */ c.createElement(Ho, null),
  color: "#22b35e",
  ext: ["xlsx", "xls"]
}, {
  key: "image",
  icon: /* @__PURE__ */ c.createElement(Bo, null),
  color: ht,
  ext: go
}, {
  key: "markdown",
  icon: /* @__PURE__ */ c.createElement(Wo, null),
  color: ht,
  ext: ["md", "mdx"]
}, {
  key: "pdf",
  icon: /* @__PURE__ */ c.createElement(Vo, null),
  color: "#ff4d4f",
  ext: ["pdf"]
}, {
  key: "ppt",
  icon: /* @__PURE__ */ c.createElement(Xo, null),
  color: "#ff6e31",
  ext: ["ppt", "pptx"]
}, {
  key: "word",
  icon: /* @__PURE__ */ c.createElement(Uo, null),
  color: "#1677ff",
  ext: ["doc", "docx"]
}, {
  key: "zip",
  icon: /* @__PURE__ */ c.createElement(Go, null),
  color: "#fab714",
  ext: ["zip", "rar", "7z", "tar", "gz"]
}, {
  key: "video",
  icon: /* @__PURE__ */ c.createElement(Pa, null),
  color: "#ff4d4f",
  ext: ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
}, {
  key: "audio",
  icon: /* @__PURE__ */ c.createElement(Ra, null),
  color: "#8c8c8c",
  ext: ["mp3", "wav", "flac", "ape", "aac", "ogg"]
}];
function br(e, t) {
  return t.some((n) => e.toLowerCase() === `.${n}`);
}
function Ma(e) {
  let t = e;
  const n = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
  let r = 0;
  for (; t >= 1024 && r < n.length - 1; )
    t /= 1024, r++;
  return `${t.toFixed(0)} ${n[r]}`;
}
function La(e, t) {
  const {
    prefixCls: n,
    item: r,
    onRemove: o,
    className: s,
    style: i,
    imageProps: a,
    type: l,
    icon: u
  } = e, m = c.useContext(rt), {
    disabled: f
  } = m || {}, {
    name: d,
    size: p,
    percent: y,
    status: h = "done",
    description: g
  } = r, {
    getPrefixCls: S
  } = Re(), _ = S("attachment", n), w = `${_}-list-card`, [$, R, v] = po(_), [P, I] = c.useMemo(() => {
    const z = d || "", W = z.match(/^(.*)\.[^.]+$/);
    return W ? [W[1], z.slice(W[1].length)] : [z, ""];
  }, [d]), F = c.useMemo(() => br(I, go), [I]), T = c.useMemo(() => g || (h === "uploading" ? `${y || 0}%` : h === "error" ? r.response || Jt : p ? Ma(p) : Jt), [h, y]), [L, O] = c.useMemo(() => {
    if (u)
      if (typeof u == "string") {
        const z = vr.find((W) => W.key === u);
        if (z)
          return [z.icon, z.color];
      } else
        return [u, void 0];
    for (const {
      ext: z,
      icon: W,
      color: ie
    } of vr)
      if (br(I, z))
        return [W, ie];
    return [/* @__PURE__ */ c.createElement(Nr, {
      key: "defaultIcon"
    }), ht];
  }, [I, u]), [b, E] = c.useState();
  c.useEffect(() => {
    if (r.originFileObj) {
      let z = !0;
      return $a(r.originFileObj).then((W) => {
        z && E(W);
      }), () => {
        z = !1;
      };
    }
    E(void 0);
  }, [r.originFileObj]);
  let k = null;
  const D = r.thumbUrl || r.url || b, B = l === "image" || l !== "file" && F && (r.originFileObj || D);
  return B ? k = /* @__PURE__ */ c.createElement(c.Fragment, null, D && /* @__PURE__ */ c.createElement(ls, ve({
    alt: "preview",
    src: D
  }, a)), h !== "done" && /* @__PURE__ */ c.createElement("div", {
    className: `${w}-img-mask`
  }, h === "uploading" && y !== void 0 && /* @__PURE__ */ c.createElement(Ia, {
    percent: y,
    prefixCls: w
  }), h === "error" && /* @__PURE__ */ c.createElement("div", {
    className: `${w}-desc`
  }, /* @__PURE__ */ c.createElement("div", {
    className: `${w}-ellipsis-prefix`
  }, T)))) : k = /* @__PURE__ */ c.createElement(c.Fragment, null, /* @__PURE__ */ c.createElement("div", {
    className: `${w}-icon`,
    style: O ? {
      color: O
    } : void 0
  }, L), /* @__PURE__ */ c.createElement("div", {
    className: `${w}-content`
  }, /* @__PURE__ */ c.createElement("div", {
    className: `${w}-name`
  }, /* @__PURE__ */ c.createElement("div", {
    className: `${w}-ellipsis-prefix`
  }, P ?? Jt), /* @__PURE__ */ c.createElement("div", {
    className: `${w}-ellipsis-suffix`
  }, I)), /* @__PURE__ */ c.createElement("div", {
    className: `${w}-desc`
  }, /* @__PURE__ */ c.createElement("div", {
    className: `${w}-ellipsis-prefix`
  }, T)))), $(/* @__PURE__ */ c.createElement("div", {
    className: N(w, {
      [`${w}-status-${h}`]: h,
      [`${w}-type-preview`]: B,
      [`${w}-type-overview`]: !B
    }, s, R, v),
    style: i,
    ref: t
  }, k, !f && o && /* @__PURE__ */ c.createElement("button", {
    type: "button",
    className: `${w}-remove`,
    onClick: () => {
      o(r);
    }
  }, /* @__PURE__ */ c.createElement(Do, null))));
}
const ho = /* @__PURE__ */ c.forwardRef(La), xr = 1;
function Na(e) {
  const {
    prefixCls: t,
    items: n,
    onRemove: r,
    overflow: o,
    upload: s,
    listClassName: i,
    listStyle: a,
    itemClassName: l,
    uploadClassName: u,
    uploadStyle: m,
    itemStyle: f,
    imageProps: d
  } = e, p = `${t}-list`, y = c.useRef(null), [h, g] = c.useState(!1), {
    disabled: S
  } = c.useContext(rt);
  c.useEffect(() => (g(!0), () => {
    g(!1);
  }), []);
  const [_, w] = c.useState(!1), [$, R] = c.useState(!1), v = () => {
    const T = y.current;
    T && (o === "scrollX" ? (w(Math.abs(T.scrollLeft) >= xr), R(T.scrollWidth - T.clientWidth - Math.abs(T.scrollLeft) >= xr)) : o === "scrollY" && (w(T.scrollTop !== 0), R(T.scrollHeight - T.clientHeight !== T.scrollTop)));
  };
  c.useEffect(() => {
    v();
  }, [o, n.length]);
  const P = (T) => {
    const L = y.current;
    L && L.scrollTo({
      left: L.scrollLeft + T * L.clientWidth,
      behavior: "smooth"
    });
  }, I = () => {
    P(-1);
  }, F = () => {
    P(1);
  };
  return /* @__PURE__ */ c.createElement("div", {
    className: N(p, {
      [`${p}-overflow-${e.overflow}`]: o,
      [`${p}-overflow-ping-start`]: _,
      [`${p}-overflow-ping-end`]: $
    }, i),
    ref: y,
    onScroll: v,
    style: a
  }, /* @__PURE__ */ c.createElement(xa, {
    keys: n.map((T) => ({
      key: T.uid,
      item: T
    })),
    motionName: `${p}-card-motion`,
    component: !1,
    motionAppear: h,
    motionLeave: !0,
    motionEnter: !0
  }, ({
    key: T,
    item: L,
    className: O,
    style: b
  }) => /* @__PURE__ */ c.createElement(ho, {
    key: T,
    prefixCls: t,
    item: L,
    onRemove: r,
    className: N(O, l),
    imageProps: d,
    style: {
      ...b,
      ...f
    }
  })), !S && /* @__PURE__ */ c.createElement(mo, {
    upload: s
  }, /* @__PURE__ */ c.createElement(ae, {
    className: N(u, `${p}-upload-btn`),
    style: m,
    type: "dashed"
  }, /* @__PURE__ */ c.createElement(qo, {
    className: `${p}-upload-btn-icon`
  }))), o === "scrollX" && /* @__PURE__ */ c.createElement(c.Fragment, null, /* @__PURE__ */ c.createElement(ae, {
    size: "small",
    shape: "circle",
    className: `${p}-prev-btn`,
    icon: /* @__PURE__ */ c.createElement(Ko, null),
    onClick: I
  }), /* @__PURE__ */ c.createElement(ae, {
    size: "small",
    shape: "circle",
    className: `${p}-next-btn`,
    icon: /* @__PURE__ */ c.createElement(Yo, null),
    onClick: F
  })));
}
function Fa(e, t) {
  const {
    prefixCls: n,
    placeholder: r = {},
    upload: o,
    className: s,
    style: i
  } = e, a = `${n}-placeholder`, l = r || {}, {
    disabled: u
  } = c.useContext(rt), [m, f] = c.useState(!1), d = () => {
    f(!0);
  }, p = (g) => {
    g.currentTarget.contains(g.relatedTarget) || f(!1);
  }, y = () => {
    f(!1);
  }, h = /* @__PURE__ */ c.isValidElement(r) ? r : /* @__PURE__ */ c.createElement(Ce, {
    align: "center",
    justify: "center",
    vertical: !0,
    className: `${a}-inner`
  }, /* @__PURE__ */ c.createElement($e.Text, {
    className: `${a}-icon`
  }, l.icon), /* @__PURE__ */ c.createElement($e.Title, {
    className: `${a}-title`,
    level: 5
  }, l.title), /* @__PURE__ */ c.createElement($e.Text, {
    className: `${a}-description`,
    type: "secondary"
  }, l.description));
  return /* @__PURE__ */ c.createElement("div", {
    className: N(a, {
      [`${a}-drag-in`]: m,
      [`${a}-disabled`]: u
    }, s),
    onDragEnter: d,
    onDragLeave: p,
    onDrop: y,
    "aria-hidden": u,
    style: i
  }, /* @__PURE__ */ c.createElement(Or.Dragger, ve({
    showUploadList: !1
  }, o, {
    ref: t,
    style: {
      padding: 0,
      border: 0,
      background: "transparent"
    }
  }), h));
}
const Oa = /* @__PURE__ */ c.forwardRef(Fa);
function ja(e, t) {
  const {
    prefixCls: n,
    rootClassName: r,
    rootStyle: o,
    className: s,
    style: i,
    items: a,
    children: l,
    getDropContainer: u,
    placeholder: m,
    onChange: f,
    onRemove: d,
    overflow: p,
    imageProps: y,
    disabled: h,
    maxCount: g,
    classNames: S = {},
    styles: _ = {},
    ...w
  } = e, {
    getPrefixCls: $,
    direction: R
  } = Re(), v = $("attachment", n), P = Et("attachments"), {
    classNames: I,
    styles: F
  } = P, T = c.useRef(null), L = c.useRef(null);
  c.useImperativeHandle(t, () => ({
    nativeElement: T.current,
    upload: (U) => {
      var K, ee;
      const V = (ee = (K = L.current) == null ? void 0 : K.nativeElement) == null ? void 0 : ee.querySelector('input[type="file"]');
      if (V) {
        const Z = new DataTransfer();
        Z.items.add(U), V.files = Z.files, V.dispatchEvent(new Event("change", {
          bubbles: !0
        }));
      }
    }
  }));
  const [O, b, E] = po(v), k = N(b, E), [D, B] = wi([], {
    value: a
  }), z = Ne((U) => {
    B(U.fileList), f == null || f(U);
  }), W = {
    ...w,
    fileList: D,
    maxCount: g,
    onChange: z
  }, ie = (U) => Promise.resolve(typeof d == "function" ? d(U) : d).then((V) => {
    if (V === !1)
      return;
    const K = D.filter((ee) => ee.uid !== U.uid);
    z({
      file: {
        ...U,
        status: "removed"
      },
      fileList: K
    });
  });
  let G;
  const J = (U, V, K) => {
    const ee = typeof m == "function" ? m(U) : m;
    return /* @__PURE__ */ c.createElement(Oa, {
      placeholder: ee,
      upload: W,
      prefixCls: v,
      className: N(I.placeholder, S.placeholder),
      style: {
        ...F.placeholder,
        ..._.placeholder,
        ...V == null ? void 0 : V.style
      },
      ref: K
    });
  };
  if (l)
    G = /* @__PURE__ */ c.createElement(c.Fragment, null, /* @__PURE__ */ c.createElement(mo, {
      upload: W,
      rootClassName: r,
      ref: L
    }, l), /* @__PURE__ */ c.createElement(cr, {
      getDropContainer: u,
      prefixCls: v,
      className: N(k, r)
    }, J("drop")));
  else {
    const U = D.length > 0;
    G = /* @__PURE__ */ c.createElement("div", {
      className: N(v, k, {
        [`${v}-rtl`]: R === "rtl"
      }, s, r),
      style: {
        ...o,
        ...i
      },
      dir: R || "ltr",
      ref: T
    }, /* @__PURE__ */ c.createElement(Na, {
      prefixCls: v,
      items: D,
      onRemove: ie,
      overflow: p,
      upload: W,
      listClassName: N(I.list, S.list),
      listStyle: {
        ...F.list,
        ..._.list,
        ...!U && {
          display: "none"
        }
      },
      uploadClassName: N(I.upload, S.upload),
      uploadStyle: {
        ...F.upload,
        ..._.upload
      },
      itemClassName: N(I.item, S.item),
      itemStyle: {
        ...F.item,
        ..._.item
      },
      imageProps: y
    }), J("inline", U ? {
      style: {
        display: "none"
      }
    } : {}, L), /* @__PURE__ */ c.createElement(cr, {
      getDropContainer: u || (() => T.current),
      prefixCls: v,
      className: k
    }, J("drop")));
  }
  return O(/* @__PURE__ */ c.createElement(rt.Provider, {
    value: {
      disabled: h
    }
  }, G));
}
const yo = /* @__PURE__ */ c.forwardRef(ja);
yo.FileCard = ho;
function dt(e) {
  return typeof e == "string";
}
const ka = (e, t, n, r) => {
  const o = M.useRef(""), [s, i] = M.useState(1), a = t && dt(e);
  return qr(() => {
    !a && dt(e) ? i(e.length) : dt(e) && dt(o.current) && e.indexOf(o.current) !== 0 && i(1), o.current = e;
  }, [e]), M.useEffect(() => {
    if (a && s < e.length) {
      const u = setTimeout(() => {
        i((m) => m + n);
      }, r);
      return () => {
        clearTimeout(u);
      };
    }
  }, [s, t, e]), [a ? e.slice(0, s) : e, a && s < e.length];
};
function Aa(e) {
  return M.useMemo(() => {
    if (!e)
      return [!1, 0, 0, null];
    let t = {
      step: 1,
      interval: 50,
      // set default suffix is empty
      suffix: null
    };
    return typeof e == "object" && (t = {
      ...t,
      ...e
    }), [!0, t.step, t.interval, t.suffix];
  }, [e]);
}
const za = ({
  prefixCls: e
}) => /* @__PURE__ */ c.createElement("span", {
  className: `${e}-dot`
}, /* @__PURE__ */ c.createElement("i", {
  className: `${e}-dot-item`,
  key: "item-1"
}), /* @__PURE__ */ c.createElement("i", {
  className: `${e}-dot-item`,
  key: "item-2"
}), /* @__PURE__ */ c.createElement("i", {
  className: `${e}-dot-item`,
  key: "item-3"
})), Da = (e) => {
  const {
    componentCls: t,
    paddingSM: n,
    padding: r
  } = e;
  return {
    [t]: {
      [`${t}-content`]: {
        // Shared: filled, outlined, shadow
        "&-filled,&-outlined,&-shadow": {
          padding: `${Ve(n)} ${Ve(r)}`,
          borderRadius: e.borderRadiusLG
        },
        // Filled:
        "&-filled": {
          backgroundColor: e.colorFillContent
        },
        // Outlined:
        "&-outlined": {
          border: `1px solid ${e.colorBorderSecondary}`
        },
        // Shadow:
        "&-shadow": {
          boxShadow: e.boxShadowTertiary
        }
      }
    }
  };
}, Ha = (e) => {
  const {
    componentCls: t,
    fontSize: n,
    lineHeight: r,
    paddingSM: o,
    padding: s,
    calc: i
  } = e, a = i(n).mul(r).div(2).add(o).equal(), l = `${t}-content`;
  return {
    [t]: {
      [l]: {
        // round:
        "&-round": {
          borderRadius: {
            _skip_check_: !0,
            value: a
          },
          paddingInline: i(s).mul(1.25).equal()
        }
      },
      // corner:
      [`&-start ${l}-corner`]: {
        borderStartStartRadius: e.borderRadiusXS
      },
      [`&-end ${l}-corner`]: {
        borderStartEndRadius: e.borderRadiusXS
      }
    }
  };
}, Ba = (e) => {
  const {
    componentCls: t,
    padding: n
  } = e;
  return {
    [`${t}-list`]: {
      display: "flex",
      flexDirection: "column",
      gap: n,
      overflowY: "auto",
      "&::-webkit-scrollbar": {
        width: 8,
        backgroundColor: "transparent"
      },
      "&::-webkit-scrollbar-thumb": {
        backgroundColor: e.colorTextTertiary,
        borderRadius: e.borderRadiusSM
      },
      // For Firefox
      "&": {
        scrollbarWidth: "thin",
        scrollbarColor: `${e.colorTextTertiary} transparent`
      }
    }
  };
}, Wa = new kr("loadingMove", {
  "0%": {
    transform: "translateY(0)"
  },
  "10%": {
    transform: "translateY(4px)"
  },
  "20%": {
    transform: "translateY(0)"
  },
  "30%": {
    transform: "translateY(-4px)"
  },
  "40%": {
    transform: "translateY(0)"
  }
}), Va = new kr("cursorBlink", {
  "0%": {
    opacity: 1
  },
  "50%": {
    opacity: 0
  },
  "100%": {
    opacity: 1
  }
}), Xa = (e) => {
  const {
    componentCls: t,
    fontSize: n,
    lineHeight: r,
    paddingSM: o,
    colorText: s,
    calc: i
  } = e;
  return {
    [t]: {
      display: "flex",
      columnGap: o,
      [`&${t}-end`]: {
        justifyContent: "end",
        flexDirection: "row-reverse",
        [`& ${t}-content-wrapper`]: {
          alignItems: "flex-end"
        }
      },
      [`&${t}-rtl`]: {
        direction: "rtl"
      },
      [`&${t}-typing ${t}-content:last-child::after`]: {
        content: '"|"',
        fontWeight: 900,
        userSelect: "none",
        opacity: 1,
        marginInlineStart: "0.1em",
        animationName: Va,
        animationDuration: "0.8s",
        animationIterationCount: "infinite",
        animationTimingFunction: "linear"
      },
      // ============================ Avatar =============================
      [`& ${t}-avatar`]: {
        display: "inline-flex",
        justifyContent: "center",
        alignSelf: "flex-start"
      },
      // ======================== Header & Footer ========================
      [`& ${t}-header, & ${t}-footer`]: {
        fontSize: n,
        lineHeight: r,
        color: e.colorText
      },
      [`& ${t}-header`]: {
        marginBottom: e.paddingXXS
      },
      [`& ${t}-footer`]: {
        marginTop: o
      },
      // =========================== Content =============================
      [`& ${t}-content-wrapper`]: {
        flex: "auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        minWidth: 0,
        maxWidth: "100%"
      },
      [`& ${t}-content`]: {
        position: "relative",
        boxSizing: "border-box",
        minWidth: 0,
        maxWidth: "100%",
        color: s,
        fontSize: e.fontSize,
        lineHeight: e.lineHeight,
        minHeight: i(o).mul(2).add(i(r).mul(n)).equal(),
        wordBreak: "break-word",
        [`& ${t}-dot`]: {
          position: "relative",
          height: "100%",
          display: "flex",
          alignItems: "center",
          columnGap: e.marginXS,
          padding: `0 ${Ve(e.paddingXXS)}`,
          "&-item": {
            backgroundColor: e.colorPrimary,
            borderRadius: "100%",
            width: 4,
            height: 4,
            animationName: Wa,
            animationDuration: "2s",
            animationIterationCount: "infinite",
            animationTimingFunction: "linear",
            "&:nth-child(1)": {
              animationDelay: "0s"
            },
            "&:nth-child(2)": {
              animationDelay: "0.2s"
            },
            "&:nth-child(3)": {
              animationDelay: "0.4s"
            }
          }
        }
      }
    }
  };
}, Ua = () => ({}), vo = At("Bubble", (e) => {
  const t = Ke(e, {});
  return [Xa(t), Ba(t), Da(t), Ha(t)];
}, Ua), bo = /* @__PURE__ */ c.createContext({}), Ga = (e, t) => {
  const {
    prefixCls: n,
    className: r,
    rootClassName: o,
    style: s,
    classNames: i = {},
    styles: a = {},
    avatar: l,
    placement: u = "start",
    loading: m = !1,
    loadingRender: f,
    typing: d,
    content: p = "",
    messageRender: y,
    variant: h = "filled",
    shape: g,
    onTypingComplete: S,
    header: _,
    footer: w,
    _key: $,
    ...R
  } = e, {
    onUpdate: v
  } = c.useContext(bo), P = c.useRef(null);
  c.useImperativeHandle(t, () => ({
    nativeElement: P.current
  }));
  const {
    direction: I,
    getPrefixCls: F
  } = Re(), T = F("bubble", n), L = Et("bubble"), [O, b, E, k] = Aa(d), [D, B] = ka(p, O, b, E);
  c.useEffect(() => {
    v == null || v();
  }, [D]);
  const z = c.useRef(!1);
  c.useEffect(() => {
    !B && !m ? z.current || (z.current = !0, S == null || S()) : z.current = !1;
  }, [B, m]);
  const [W, ie, G] = vo(T), J = N(T, o, L.className, r, ie, G, `${T}-${u}`, {
    [`${T}-rtl`]: I === "rtl",
    [`${T}-typing`]: B && !m && !y && !k
  }), U = c.useMemo(() => /* @__PURE__ */ c.isValidElement(l) ? l : /* @__PURE__ */ c.createElement(cs, l), [l]), V = c.useMemo(() => y ? y(D) : D, [D, y]), K = (Se) => typeof Se == "function" ? Se(D, {
    key: $
  }) : Se;
  let ee;
  m ? ee = f ? f() : /* @__PURE__ */ c.createElement(za, {
    prefixCls: T
  }) : ee = /* @__PURE__ */ c.createElement(c.Fragment, null, V, B && k);
  let Z = /* @__PURE__ */ c.createElement("div", {
    style: {
      ...L.styles.content,
      ...a.content
    },
    className: N(`${T}-content`, `${T}-content-${h}`, g && `${T}-content-${g}`, L.classNames.content, i.content)
  }, ee);
  return (_ || w) && (Z = /* @__PURE__ */ c.createElement("div", {
    className: `${T}-content-wrapper`
  }, _ && /* @__PURE__ */ c.createElement("div", {
    className: N(`${T}-header`, L.classNames.header, i.header),
    style: {
      ...L.styles.header,
      ...a.header
    }
  }, K(_)), Z, w && /* @__PURE__ */ c.createElement("div", {
    className: N(`${T}-footer`, L.classNames.footer, i.footer),
    style: {
      ...L.styles.footer,
      ...a.footer
    }
  }, K(w)))), W(/* @__PURE__ */ c.createElement("div", ve({
    style: {
      ...L.style,
      ...s
    },
    className: J
  }, R, {
    ref: P
  }), l && /* @__PURE__ */ c.createElement("div", {
    style: {
      ...L.styles.avatar,
      ...a.avatar
    },
    className: N(`${T}-avatar`, L.classNames.avatar, i.avatar)
  }, U), Z));
}, En = /* @__PURE__ */ c.forwardRef(Ga);
function qa(e, t) {
  const n = M.useCallback((r, o) => typeof t == "function" ? t(r, o) : t ? t[r.role] || {} : {}, [t]);
  return M.useMemo(() => (e || []).map((r, o) => {
    const s = r.key ?? `preset_${o}`;
    return {
      ...n(r, o),
      ...r,
      key: s
    };
  }), [e, n]);
}
const Ka = ({
  _key: e,
  ...t
}, n) => /* @__PURE__ */ M.createElement(En, ve({}, t, {
  _key: e,
  ref: (r) => {
    var o;
    r ? n.current[e] = r : (o = n.current) == null || delete o[e];
  }
})), Ya = /* @__PURE__ */ M.memo(/* @__PURE__ */ M.forwardRef(Ka)), Za = 1, Qa = (e, t) => {
  const {
    prefixCls: n,
    rootClassName: r,
    className: o,
    items: s,
    autoScroll: i = !0,
    roles: a,
    onScroll: l,
    ...u
  } = e, m = ui(u, {
    attr: !0,
    aria: !0
  }), f = M.useRef(null), d = M.useRef({}), {
    getPrefixCls: p
  } = Re(), y = p("bubble", n), h = `${y}-list`, [g, S, _] = vo(y), [w, $] = M.useState(!1);
  M.useEffect(() => ($(!0), () => {
    $(!1);
  }), []);
  const R = qa(s, a), [v, P] = M.useState(!0), [I, F] = M.useState(0), T = (b) => {
    const E = b.target;
    P(E.scrollHeight - Math.abs(E.scrollTop) - E.clientHeight <= Za), l == null || l(b);
  };
  M.useEffect(() => {
    i && f.current && v && f.current.scrollTo({
      top: f.current.scrollHeight
    });
  }, [I]), M.useEffect(() => {
    var b;
    if (i) {
      const E = (b = R[R.length - 2]) == null ? void 0 : b.key, k = d.current[E];
      if (k) {
        const {
          nativeElement: D
        } = k, {
          top: B,
          bottom: z
        } = D.getBoundingClientRect(), {
          top: W,
          bottom: ie
        } = f.current.getBoundingClientRect();
        B < ie && z > W && (F((J) => J + 1), P(!0));
      }
    }
  }, [R.length]), M.useImperativeHandle(t, () => ({
    nativeElement: f.current,
    scrollTo: ({
      key: b,
      offset: E,
      behavior: k = "smooth",
      block: D
    }) => {
      if (typeof E == "number")
        f.current.scrollTo({
          top: E,
          behavior: k
        });
      else if (b !== void 0) {
        const B = d.current[b];
        if (B) {
          const z = R.findIndex((W) => W.key === b);
          P(z === R.length - 1), B.nativeElement.scrollIntoView({
            behavior: k,
            block: D
          });
        }
      }
    }
  }));
  const L = Ne(() => {
    i && F((b) => b + 1);
  }), O = M.useMemo(() => ({
    onUpdate: L
  }), []);
  return g(/* @__PURE__ */ M.createElement(bo.Provider, {
    value: O
  }, /* @__PURE__ */ M.createElement("div", ve({}, m, {
    className: N(h, r, o, S, _, {
      [`${h}-reach-end`]: v
    }),
    ref: f,
    onScroll: T
  }), R.map(({
    key: b,
    ...E
  }) => /* @__PURE__ */ M.createElement(Ya, ve({}, E, {
    key: b,
    _key: b,
    ref: d,
    typing: w ? E.typing : !1
  }))))));
}, Ja = /* @__PURE__ */ M.forwardRef(Qa);
En.List = Ja;
const el = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      // ======================== Prompt ========================
      "&, & *": {
        boxSizing: "border-box"
      },
      maxWidth: "100%",
      [`&${t}-rtl`]: {
        direction: "rtl"
      },
      [`& ${t}-title`]: {
        marginBlockStart: 0,
        fontWeight: "normal",
        color: e.colorTextTertiary
      },
      [`& ${t}-list`]: {
        display: "flex",
        gap: e.paddingSM,
        overflowX: "auto",
        // Hide scrollbar
        scrollbarWidth: "none",
        "-ms-overflow-style": "none",
        "&::-webkit-scrollbar": {
          display: "none"
        },
        listStyle: "none",
        paddingInlineStart: 0,
        marginBlock: 0,
        alignItems: "stretch",
        "&-wrap": {
          flexWrap: "wrap"
        },
        "&-vertical": {
          flexDirection: "column",
          alignItems: "flex-start"
        }
      },
      // ========================= Item =========================
      [`${t}-item`]: {
        flex: "none",
        display: "flex",
        gap: e.paddingXS,
        height: "auto",
        paddingBlock: e.paddingSM,
        paddingInline: e.padding,
        alignItems: "flex-start",
        justifyContent: "flex-start",
        background: e.colorBgContainer,
        borderRadius: e.borderRadiusLG,
        transition: ["border", "background"].map((n) => `${n} ${e.motionDurationSlow}`).join(","),
        border: `${Ve(e.lineWidth)} ${e.lineType} ${e.colorBorderSecondary}`,
        [`&:not(${t}-item-has-nest)`]: {
          "&:hover": {
            cursor: "pointer",
            background: e.colorFillTertiary
          },
          "&:active": {
            background: e.colorFill
          }
        },
        [`${t}-content`]: {
          flex: "auto",
          minWidth: 0,
          display: "flex",
          gap: e.paddingXXS,
          flexDirection: "column",
          alignItems: "flex-start"
        },
        [`${t}-icon, ${t}-label, ${t}-desc`]: {
          margin: 0,
          padding: 0,
          fontSize: e.fontSize,
          lineHeight: e.lineHeight,
          textAlign: "start",
          whiteSpace: "normal"
        },
        [`${t}-label`]: {
          color: e.colorTextHeading,
          fontWeight: 500
        },
        [`${t}-label + ${t}-desc`]: {
          color: e.colorTextTertiary
        },
        // Disabled
        [`&${t}-item-disabled`]: {
          pointerEvents: "none",
          background: e.colorBgContainerDisabled,
          [`${t}-label, ${t}-desc`]: {
            color: e.colorTextTertiary
          }
        }
      }
    }
  };
}, tl = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      // ========================= Parent =========================
      [`${t}-item-has-nest`]: {
        [`> ${t}-content`]: {
          // gap: token.paddingSM,
          [`> ${t}-label`]: {
            fontSize: e.fontSizeLG,
            lineHeight: e.lineHeightLG
          }
        }
      },
      // ========================= Nested =========================
      [`&${t}-nested`]: {
        marginTop: e.paddingXS,
        // ======================== Prompt ========================
        alignSelf: "stretch",
        [`${t}-list`]: {
          alignItems: "stretch"
        },
        // ========================= Item =========================
        [`${t}-item`]: {
          border: 0,
          background: e.colorFillQuaternary
        }
      }
    }
  };
}, nl = () => ({}), rl = At("Prompts", (e) => {
  const t = Ke(e, {});
  return [el(t), tl(t)];
}, nl), Cn = (e) => {
  const {
    prefixCls: t,
    title: n,
    className: r,
    items: o,
    onItemClick: s,
    vertical: i,
    wrap: a,
    rootClassName: l,
    styles: u = {},
    classNames: m = {},
    style: f,
    ...d
  } = e, {
    getPrefixCls: p,
    direction: y
  } = Re(), h = p("prompts", t), g = Et("prompts"), [S, _, w] = rl(h), $ = N(h, g.className, r, l, _, w, {
    [`${h}-rtl`]: y === "rtl"
  }), R = N(`${h}-list`, g.classNames.list, m.list, {
    [`${h}-list-wrap`]: a
  }, {
    [`${h}-list-vertical`]: i
  });
  return S(/* @__PURE__ */ c.createElement("div", ve({}, d, {
    className: $,
    style: {
      ...f,
      ...g.style
    }
  }), n && /* @__PURE__ */ c.createElement($e.Title, {
    level: 5,
    className: N(`${h}-title`, g.classNames.title, m.title),
    style: {
      ...g.styles.title,
      ...u.title
    }
  }, n), /* @__PURE__ */ c.createElement("div", {
    className: R,
    style: {
      ...g.styles.list,
      ...u.list
    }
  }, o == null ? void 0 : o.map((v, P) => {
    const I = v.children && v.children.length > 0;
    return /* @__PURE__ */ c.createElement("div", {
      key: v.key || `key_${P}`,
      style: {
        ...g.styles.item,
        ...u.item
      },
      className: N(`${h}-item`, g.classNames.item, m.item, {
        [`${h}-item-disabled`]: v.disabled,
        [`${h}-item-has-nest`]: I
      }),
      onClick: () => {
        !I && s && s({
          data: v
        });
      }
    }, v.icon && /* @__PURE__ */ c.createElement("div", {
      className: `${h}-icon`
    }, v.icon), /* @__PURE__ */ c.createElement("div", {
      className: N(`${h}-content`, g.classNames.itemContent, m.itemContent),
      style: {
        ...g.styles.itemContent,
        ...u.itemContent
      }
    }, v.label && /* @__PURE__ */ c.createElement("h6", {
      className: `${h}-label`
    }, v.label), v.description && /* @__PURE__ */ c.createElement("p", {
      className: `${h}-desc`
    }, v.description), I && /* @__PURE__ */ c.createElement(Cn, {
      className: `${h}-nested`,
      items: v.children,
      vertical: !0,
      onItemClick: s,
      classNames: {
        list: m.subList,
        item: m.subItem
      },
      styles: {
        list: u.subList,
        item: u.subItem
      }
    })));
  }))));
}, ol = (e) => {
  const {
    componentCls: t,
    calc: n
  } = e, r = n(e.fontSizeHeading3).mul(e.lineHeightHeading3).equal(), o = n(e.fontSize).mul(e.lineHeight).equal();
  return {
    [t]: {
      gap: e.padding,
      // ======================== Icon ========================
      [`${t}-icon`]: {
        height: n(r).add(o).add(e.paddingXXS).equal(),
        display: "flex",
        img: {
          height: "100%"
        }
      },
      // ==================== Content Wrap ====================
      [`${t}-content-wrapper`]: {
        gap: e.paddingXS,
        flex: "auto",
        minWidth: 0,
        [`${t}-title-wrapper`]: {
          gap: e.paddingXS
        },
        [`${t}-title`]: {
          margin: 0
        },
        [`${t}-extra`]: {
          marginInlineStart: "auto"
        }
      }
    }
  };
}, sl = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      // ======================== Filled ========================
      "&-filled": {
        paddingInline: e.padding,
        paddingBlock: e.paddingSM,
        background: e.colorFillContent,
        borderRadius: e.borderRadiusLG
      },
      // ====================== Borderless ======================
      "&-borderless": {
        [`${t}-title`]: {
          fontSize: e.fontSizeHeading3,
          lineHeight: e.lineHeightHeading3
        }
      }
    }
  };
}, il = () => ({}), al = At("Welcome", (e) => {
  const t = Ke(e, {});
  return [ol(t), sl(t)];
}, il);
function ll(e, t) {
  const {
    prefixCls: n,
    rootClassName: r,
    className: o,
    style: s,
    variant: i = "filled",
    // Semantic
    classNames: a = {},
    styles: l = {},
    // Layout
    icon: u,
    title: m,
    description: f,
    extra: d
  } = e, {
    direction: p,
    getPrefixCls: y
  } = Re(), h = y("welcome", n), g = Et("welcome"), [S, _, w] = al(h), $ = c.useMemo(() => {
    if (!u)
      return null;
    let P = u;
    return typeof u == "string" && u.startsWith("http") && (P = /* @__PURE__ */ c.createElement("img", {
      src: u,
      alt: "icon"
    })), /* @__PURE__ */ c.createElement("div", {
      className: N(`${h}-icon`, g.classNames.icon, a.icon),
      style: l.icon
    }, P);
  }, [u]), R = c.useMemo(() => m ? /* @__PURE__ */ c.createElement($e.Title, {
    level: 4,
    className: N(`${h}-title`, g.classNames.title, a.title),
    style: l.title
  }, m) : null, [m]), v = c.useMemo(() => d ? /* @__PURE__ */ c.createElement("div", {
    className: N(`${h}-extra`, g.classNames.extra, a.extra),
    style: l.extra
  }, d) : null, [d]);
  return S(/* @__PURE__ */ c.createElement(Ce, {
    ref: t,
    className: N(h, g.className, o, r, _, w, `${h}-${i}`, {
      [`${h}-rtl`]: p === "rtl"
    }),
    style: s
  }, $, /* @__PURE__ */ c.createElement(Ce, {
    vertical: !0,
    className: `${h}-content-wrapper`
  }, d ? /* @__PURE__ */ c.createElement(Ce, {
    align: "flex-start",
    className: `${h}-title-wrapper`
  }, R, v) : R, f && /* @__PURE__ */ c.createElement($e.Text, {
    className: N(`${h}-description`, g.classNames.description, a.description),
    style: l.description
  }, f))));
}
const cl = /* @__PURE__ */ c.forwardRef(ll);
function se(e) {
  const t = ne(e);
  return t.current = e, Fo((...n) => {
    var r;
    return (r = t.current) == null ? void 0 : r.call(t, ...n);
  }, []);
}
function be(e, t) {
  return Object.keys(e).reduce((n, r) => (e[r] !== void 0 && (!(t != null && t.omitNull) || e[r] !== null) && (n[r] = e[r]), n), {});
}
var xo = Symbol.for("immer-nothing"), Sr = Symbol.for("immer-draftable"), ce = Symbol.for("immer-state");
function he(e, ...t) {
  throw new Error(`[Immer] minified error nr: ${e}. Full error at: https://bit.ly/3cXEKWf`);
}
var Xe = Object.getPrototypeOf;
function Ue(e) {
  return !!e && !!e[ce];
}
function Fe(e) {
  var t;
  return e ? So(e) || Array.isArray(e) || !!e[Sr] || !!((t = e.constructor) != null && t[Sr]) || Dt(e) || Ht(e) : !1;
}
var ul = Object.prototype.constructor.toString();
function So(e) {
  if (!e || typeof e != "object") return !1;
  const t = Xe(e);
  if (t === null)
    return !0;
  const n = Object.hasOwnProperty.call(t, "constructor") && t.constructor;
  return n === Object ? !0 : typeof n == "function" && Function.toString.call(n) === ul;
}
function xt(e, t) {
  zt(e) === 0 ? Reflect.ownKeys(e).forEach((n) => {
    t(n, e[n], e);
  }) : e.forEach((n, r) => t(r, n, e));
}
function zt(e) {
  const t = e[ce];
  return t ? t.type_ : Array.isArray(e) ? 1 : Dt(e) ? 2 : Ht(e) ? 3 : 0;
}
function fn(e, t) {
  return zt(e) === 2 ? e.has(t) : Object.prototype.hasOwnProperty.call(e, t);
}
function wo(e, t, n) {
  const r = zt(e);
  r === 2 ? e.set(t, n) : r === 3 ? e.add(n) : e[t] = n;
}
function dl(e, t) {
  return e === t ? e !== 0 || 1 / e === 1 / t : e !== e && t !== t;
}
function Dt(e) {
  return e instanceof Map;
}
function Ht(e) {
  return e instanceof Set;
}
function Me(e) {
  return e.copy_ || e.base_;
}
function mn(e, t) {
  if (Dt(e))
    return new Map(e);
  if (Ht(e))
    return new Set(e);
  if (Array.isArray(e)) return Array.prototype.slice.call(e);
  const n = So(e);
  if (t === !0 || t === "class_only" && !n) {
    const r = Object.getOwnPropertyDescriptors(e);
    delete r[ce];
    let o = Reflect.ownKeys(r);
    for (let s = 0; s < o.length; s++) {
      const i = o[s], a = r[i];
      a.writable === !1 && (a.writable = !0, a.configurable = !0), (a.get || a.set) && (r[i] = {
        configurable: !0,
        writable: !0,
        // could live with !!desc.set as well here...
        enumerable: a.enumerable,
        value: e[i]
      });
    }
    return Object.create(Xe(e), r);
  } else {
    const r = Xe(e);
    if (r !== null && n)
      return {
        ...e
      };
    const o = Object.create(r);
    return Object.assign(o, e);
  }
}
function Tn(e, t = !1) {
  return Bt(e) || Ue(e) || !Fe(e) || (zt(e) > 1 && (e.set = e.add = e.clear = e.delete = fl), Object.freeze(e), t && Object.entries(e).forEach(([n, r]) => Tn(r, !0))), e;
}
function fl() {
  he(2);
}
function Bt(e) {
  return Object.isFrozen(e);
}
var ml = {};
function Oe(e) {
  const t = ml[e];
  return t || he(0, e), t;
}
var et;
function _o() {
  return et;
}
function pl(e, t) {
  return {
    drafts_: [],
    parent_: e,
    immer_: t,
    // Whenever the modified draft contains a draft from another scope, we
    // need to prevent auto-freezing so the unowned draft can be finalized.
    canAutoFreeze_: !0,
    unfinalizedDrafts_: 0
  };
}
function wr(e, t) {
  t && (Oe("Patches"), e.patches_ = [], e.inversePatches_ = [], e.patchListener_ = t);
}
function pn(e) {
  gn(e), e.drafts_.forEach(gl), e.drafts_ = null;
}
function gn(e) {
  e === et && (et = e.parent_);
}
function _r(e) {
  return et = pl(et, e);
}
function gl(e) {
  const t = e[ce];
  t.type_ === 0 || t.type_ === 1 ? t.revoke_() : t.revoked_ = !0;
}
function Er(e, t) {
  t.unfinalizedDrafts_ = t.drafts_.length;
  const n = t.drafts_[0];
  return e !== void 0 && e !== n ? (n[ce].modified_ && (pn(t), he(4)), Fe(e) && (e = St(t, e), t.parent_ || wt(t, e)), t.patches_ && Oe("Patches").generateReplacementPatches_(n[ce].base_, e, t.patches_, t.inversePatches_)) : e = St(t, n, []), pn(t), t.patches_ && t.patchListener_(t.patches_, t.inversePatches_), e !== xo ? e : void 0;
}
function St(e, t, n) {
  if (Bt(t)) return t;
  const r = t[ce];
  if (!r)
    return xt(t, (o, s) => Cr(e, r, t, o, s, n)), t;
  if (r.scope_ !== e) return t;
  if (!r.modified_)
    return wt(e, r.base_, !0), r.base_;
  if (!r.finalized_) {
    r.finalized_ = !0, r.scope_.unfinalizedDrafts_--;
    const o = r.copy_;
    let s = o, i = !1;
    r.type_ === 3 && (s = new Set(o), o.clear(), i = !0), xt(s, (a, l) => Cr(e, r, o, a, l, n, i)), wt(e, o, !1), n && e.patches_ && Oe("Patches").generatePatches_(r, n, e.patches_, e.inversePatches_);
  }
  return r.copy_;
}
function Cr(e, t, n, r, o, s, i) {
  if (Ue(o)) {
    const a = s && t && t.type_ !== 3 && // Set objects are atomic since they have no keys.
    !fn(t.assigned_, r) ? s.concat(r) : void 0, l = St(e, o, a);
    if (wo(n, r, l), Ue(l))
      e.canAutoFreeze_ = !1;
    else return;
  } else i && n.add(o);
  if (Fe(o) && !Bt(o)) {
    if (!e.immer_.autoFreeze_ && e.unfinalizedDrafts_ < 1)
      return;
    St(e, o), (!t || !t.scope_.parent_) && typeof r != "symbol" && Object.prototype.propertyIsEnumerable.call(n, r) && wt(e, o);
  }
}
function wt(e, t, n = !1) {
  !e.parent_ && e.immer_.autoFreeze_ && e.canAutoFreeze_ && Tn(t, n);
}
function hl(e, t) {
  const n = Array.isArray(e), r = {
    type_: n ? 1 : 0,
    // Track which produce call this is associated with.
    scope_: t ? t.scope_ : _o(),
    // True for both shallow and deep changes.
    modified_: !1,
    // Used during finalization.
    finalized_: !1,
    // Track which properties have been assigned (true) or deleted (false).
    assigned_: {},
    // The parent draft state.
    parent_: t,
    // The base state.
    base_: e,
    // The base proxy.
    draft_: null,
    // set below
    // The base copy with any updated values.
    copy_: null,
    // Called by the `produce` function.
    revoke_: null,
    isManual_: !1
  };
  let o = r, s = $n;
  n && (o = [r], s = tt);
  const {
    revoke: i,
    proxy: a
  } = Proxy.revocable(o, s);
  return r.draft_ = a, r.revoke_ = i, a;
}
var $n = {
  get(e, t) {
    if (t === ce) return e;
    const n = Me(e);
    if (!fn(n, t))
      return yl(e, n, t);
    const r = n[t];
    return e.finalized_ || !Fe(r) ? r : r === en(e.base_, t) ? (tn(e), e.copy_[t] = yn(r, e)) : r;
  },
  has(e, t) {
    return t in Me(e);
  },
  ownKeys(e) {
    return Reflect.ownKeys(Me(e));
  },
  set(e, t, n) {
    const r = Eo(Me(e), t);
    if (r != null && r.set)
      return r.set.call(e.draft_, n), !0;
    if (!e.modified_) {
      const o = en(Me(e), t), s = o == null ? void 0 : o[ce];
      if (s && s.base_ === n)
        return e.copy_[t] = n, e.assigned_[t] = !1, !0;
      if (dl(n, o) && (n !== void 0 || fn(e.base_, t))) return !0;
      tn(e), hn(e);
    }
    return e.copy_[t] === n && // special case: handle new props with value 'undefined'
    (n !== void 0 || t in e.copy_) || // special case: NaN
    Number.isNaN(n) && Number.isNaN(e.copy_[t]) || (e.copy_[t] = n, e.assigned_[t] = !0), !0;
  },
  deleteProperty(e, t) {
    return en(e.base_, t) !== void 0 || t in e.base_ ? (e.assigned_[t] = !1, tn(e), hn(e)) : delete e.assigned_[t], e.copy_ && delete e.copy_[t], !0;
  },
  // Note: We never coerce `desc.value` into an Immer draft, because we can't make
  // the same guarantee in ES5 mode.
  getOwnPropertyDescriptor(e, t) {
    const n = Me(e), r = Reflect.getOwnPropertyDescriptor(n, t);
    return r && {
      writable: !0,
      configurable: e.type_ !== 1 || t !== "length",
      enumerable: r.enumerable,
      value: n[t]
    };
  },
  defineProperty() {
    he(11);
  },
  getPrototypeOf(e) {
    return Xe(e.base_);
  },
  setPrototypeOf() {
    he(12);
  }
}, tt = {};
xt($n, (e, t) => {
  tt[e] = function() {
    return arguments[0] = arguments[0][0], t.apply(this, arguments);
  };
});
tt.deleteProperty = function(e, t) {
  return tt.set.call(this, e, t, void 0);
};
tt.set = function(e, t, n) {
  return $n.set.call(this, e[0], t, n, e[0]);
};
function en(e, t) {
  const n = e[ce];
  return (n ? Me(n) : e)[t];
}
function yl(e, t, n) {
  var o;
  const r = Eo(t, n);
  return r ? "value" in r ? r.value : (
    // This is a very special case, if the prop is a getter defined by the
    // prototype, we should invoke it with the draft as context!
    (o = r.get) == null ? void 0 : o.call(e.draft_)
  ) : void 0;
}
function Eo(e, t) {
  if (!(t in e)) return;
  let n = Xe(e);
  for (; n; ) {
    const r = Object.getOwnPropertyDescriptor(n, t);
    if (r) return r;
    n = Xe(n);
  }
}
function hn(e) {
  e.modified_ || (e.modified_ = !0, e.parent_ && hn(e.parent_));
}
function tn(e) {
  e.copy_ || (e.copy_ = mn(e.base_, e.scope_.immer_.useStrictShallowCopy_));
}
var vl = class {
  constructor(e) {
    this.autoFreeze_ = !0, this.useStrictShallowCopy_ = !1, this.produce = (t, n, r) => {
      if (typeof t == "function" && typeof n != "function") {
        const s = n;
        n = t;
        const i = this;
        return function(l = s, ...u) {
          return i.produce(l, (m) => n.call(this, m, ...u));
        };
      }
      typeof n != "function" && he(6), r !== void 0 && typeof r != "function" && he(7);
      let o;
      if (Fe(t)) {
        const s = _r(this), i = yn(t, void 0);
        let a = !0;
        try {
          o = n(i), a = !1;
        } finally {
          a ? pn(s) : gn(s);
        }
        return wr(s, r), Er(o, s);
      } else if (!t || typeof t != "object") {
        if (o = n(t), o === void 0 && (o = t), o === xo && (o = void 0), this.autoFreeze_ && Tn(o, !0), r) {
          const s = [], i = [];
          Oe("Patches").generateReplacementPatches_(t, o, s, i), r(s, i);
        }
        return o;
      } else he(1, t);
    }, this.produceWithPatches = (t, n) => {
      if (typeof t == "function")
        return (i, ...a) => this.produceWithPatches(i, (l) => t(l, ...a));
      let r, o;
      return [this.produce(t, n, (i, a) => {
        r = i, o = a;
      }), r, o];
    }, typeof (e == null ? void 0 : e.autoFreeze) == "boolean" && this.setAutoFreeze(e.autoFreeze), typeof (e == null ? void 0 : e.useStrictShallowCopy) == "boolean" && this.setUseStrictShallowCopy(e.useStrictShallowCopy);
  }
  createDraft(e) {
    Fe(e) || he(8), Ue(e) && (e = bl(e));
    const t = _r(this), n = yn(e, void 0);
    return n[ce].isManual_ = !0, gn(t), n;
  }
  finishDraft(e, t) {
    const n = e && e[ce];
    (!n || !n.isManual_) && he(9);
    const {
      scope_: r
    } = n;
    return wr(r, t), Er(void 0, r);
  }
  /**
   * Pass true to automatically freeze all copies created by Immer.
   *
   * By default, auto-freezing is enabled.
   */
  setAutoFreeze(e) {
    this.autoFreeze_ = e;
  }
  /**
   * Pass true to enable strict shallow copy.
   *
   * By default, immer does not copy the object descriptors such as getter, setter and non-enumrable properties.
   */
  setUseStrictShallowCopy(e) {
    this.useStrictShallowCopy_ = e;
  }
  applyPatches(e, t) {
    let n;
    for (n = t.length - 1; n >= 0; n--) {
      const o = t[n];
      if (o.path.length === 0 && o.op === "replace") {
        e = o.value;
        break;
      }
    }
    n > -1 && (t = t.slice(n + 1));
    const r = Oe("Patches").applyPatches_;
    return Ue(e) ? r(e, t) : this.produce(e, (o) => r(o, t));
  }
};
function yn(e, t) {
  const n = Dt(e) ? Oe("MapSet").proxyMap_(e, t) : Ht(e) ? Oe("MapSet").proxySet_(e, t) : hl(e, t);
  return (t ? t.scope_ : _o()).drafts_.push(n), n;
}
function bl(e) {
  return Ue(e) || he(10, e), Co(e);
}
function Co(e) {
  if (!Fe(e) || Bt(e)) return e;
  const t = e[ce];
  let n;
  if (t) {
    if (!t.modified_) return t.base_;
    t.finalized_ = !0, n = mn(e, t.scope_.immer_.useStrictShallowCopy_);
  } else
    n = mn(e, !0);
  return xt(n, (r, o) => {
    wo(n, r, Co(o));
  }), t && (t.finalized_ = !1), n;
}
var ue = new vl(), Tr = ue.produce;
ue.produceWithPatches.bind(ue);
ue.setAutoFreeze.bind(ue);
ue.setUseStrictShallowCopy.bind(ue);
ue.applyPatches.bind(ue);
ue.createDraft.bind(ue);
ue.finishDraft.bind(ue);
const {
  useItems: ic,
  withItemsContextProvider: ac,
  ItemHandler: lc
} = jr("antdx-bubble.list-items"), {
  useItems: xl,
  withItemsContextProvider: Sl,
  ItemHandler: cc
} = jr("antdx-bubble.list-roles");
function wl(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function _l(e, t = !1) {
  try {
    if (bn(e))
      return e;
    if (t && !wl(e))
      return;
    if (typeof e == "string") {
      let n = e.trim();
      return n.startsWith(";") && (n = n.slice(1)), n.endsWith(";") && (n = n.slice(0, -1)), new Function(`return (...args) => (${n})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function El(e, t) {
  return fe(() => _l(e, t), [e, t]);
}
function Cl(e, t) {
  return t((r, o) => bn(r) ? o ? (...s) => ye(o) && o.unshift ? r(...e, ...s) : r(...s, ...e) : r(...e) : r);
}
const Tl = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function $l(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const r = e[n];
    return t[n] = Rl(n, r), t;
  }, {}) : {};
}
function Rl(e, t) {
  return typeof t == "number" && !Tl.includes(e) ? t + "px" : t;
}
function vn(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const o = c.Children.toArray(e._reactElement.props.children).map((s) => {
      if (c.isValidElement(s) && s.props.__slot__) {
        const {
          portals: i,
          clonedElement: a
        } = vn(s.props.el);
        return c.cloneElement(s, {
          ...s.props,
          el: a,
          children: [...c.Children.toArray(s.props.children), ...i]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(yt(c.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: i,
      type: a,
      useCapture: l
    }) => {
      n.addEventListener(a, i, l);
    });
  });
  const r = Array.from(e.childNodes);
  for (let o = 0; o < r.length; o++) {
    const s = r[o];
    if (s.nodeType === 1) {
      const {
        clonedElement: i,
        portals: a
      } = vn(s);
      t.push(...a), n.appendChild(i);
    } else s.nodeType === 3 && n.appendChild(s.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function Il(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const $r = Oo(({
  slot: e,
  clone: t,
  className: n,
  style: r,
  observeAttributes: o
}, s) => {
  const i = ne(), [a, l] = Ze([]), {
    forceClone: u
  } = ps(), m = u ? !0 : t;
  return Ee(() => {
    var h;
    if (!i.current || !e)
      return;
    let f = e;
    function d() {
      let g = f;
      if (f.tagName.toLowerCase() === "svelte-slot" && f.children.length === 1 && f.children[0] && (g = f.children[0], g.tagName.toLowerCase() === "react-portal-target" && g.children[0] && (g = g.children[0])), Il(s, g), n && g.classList.add(...n.split(" ")), r) {
        const S = $l(r);
        Object.keys(S).forEach((_) => {
          g.style[_] = S[_];
        });
      }
    }
    let p = null, y = null;
    if (m && window.MutationObserver) {
      let g = function() {
        var $, R, v;
        ($ = i.current) != null && $.contains(f) && ((R = i.current) == null || R.removeChild(f));
        const {
          portals: _,
          clonedElement: w
        } = vn(e);
        f = w, l(_), f.style.display = "contents", y && clearTimeout(y), y = setTimeout(() => {
          d();
        }, 50), (v = i.current) == null || v.appendChild(f);
      };
      g();
      const S = Is(() => {
        g(), p == null || p.disconnect(), p == null || p.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      p = new window.MutationObserver(S), p.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      f.style.display = "contents", d(), (h = i.current) == null || h.appendChild(f);
    return () => {
      var g, S;
      f.style.display = "", (g = i.current) != null && g.contains(f) && ((S = i.current) == null || S.removeChild(f)), p == null || p.disconnect();
    };
  }, [e, m, n, r, s, o, u]), c.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...a);
}), Pl = ({
  children: e,
  ...t
}) => /* @__PURE__ */ x.jsx(x.Fragment, {
  children: e(t)
});
function Ml(e) {
  return c.createElement(Pl, {
    children: e
  });
}
function To(e, t, n) {
  const r = e.filter(Boolean);
  if (r.length !== 0)
    return r.map((o, s) => {
      var u, m;
      if (typeof o != "object")
        return t != null && t.fallback ? t.fallback(o) : o;
      const i = t != null && t.itemPropsTransformer ? t == null ? void 0 : t.itemPropsTransformer({
        ...o.props,
        key: ((u = o.props) == null ? void 0 : u.key) ?? (n ? `${n}-${s}` : `${s}`)
      }) : {
        ...o.props,
        key: ((m = o.props) == null ? void 0 : m.key) ?? (n ? `${n}-${s}` : `${s}`)
      };
      let a = i;
      Object.keys(o.slots).forEach((f) => {
        if (!o.slots[f] || !(o.slots[f] instanceof Element) && !o.slots[f].el)
          return;
        const d = f.split(".");
        d.forEach((_, w) => {
          a[_] || (a[_] = {}), w !== d.length - 1 && (a = i[_]);
        });
        const p = o.slots[f];
        let y, h, g = (t == null ? void 0 : t.clone) ?? !1, S = t == null ? void 0 : t.forceClone;
        p instanceof Element ? y = p : (y = p.el, h = p.callback, g = p.clone ?? g, S = p.forceClone ?? S), S = S ?? !!h, a[d[d.length - 1]] = y ? h ? (..._) => (h(d[d.length - 1], _), /* @__PURE__ */ x.jsx(zn, {
          ...o.ctx,
          params: _,
          forceClone: S,
          children: /* @__PURE__ */ x.jsx($r, {
            slot: y,
            clone: g
          })
        })) : Ml((_) => /* @__PURE__ */ x.jsx(zn, {
          ...o.ctx,
          forceClone: S,
          children: /* @__PURE__ */ x.jsx($r, {
            ..._,
            slot: y,
            clone: g
          })
        })) : a[d[d.length - 1]], a = i;
      });
      const l = (t == null ? void 0 : t.children) || "children";
      return o[l] ? i[l] = To(o[l], t, `${s}`) : t != null && t.children && (i[l] = void 0, Reflect.deleteProperty(i, l)), i;
    });
}
const $o = Symbol();
function Ll(e, t) {
  return Cl(t, (n) => {
    var r, o;
    return {
      ...e,
      avatar: bn(e.avatar) ? n(e.avatar) : ye(e.avatar) ? {
        ...e.avatar,
        icon: n((r = e.avatar) == null ? void 0 : r.icon),
        src: n((o = e.avatar) == null ? void 0 : o.src)
      } : e.avatar,
      footer: n(e.footer, {
        unshift: !0
      }),
      header: n(e.header, {
        unshift: !0
      }),
      loadingRender: n(e.loadingRender, !0),
      messageRender: n(e.messageRender, !0)
    };
  });
}
function Nl({
  roles: e,
  preProcess: t,
  postProcess: n
}, r = []) {
  const o = El(e), s = se(t), i = se(n), {
    items: {
      roles: a
    }
  } = xl(), l = fe(() => {
    var m;
    return e || ((m = To(a, {
      clone: !0,
      forceClone: !0
    })) == null ? void 0 : m.reduce((f, d) => (d.role !== void 0 && (f[d.role] = d), f), {}));
  }, [a, e]), u = fe(() => (m, f) => {
    const d = f ?? m[$o], p = s(m, d) || m;
    if (p.role && (l || {})[p.role])
      return Ll((l || {})[p.role], [p, d]);
    let y;
    return y = i(p, d), y || {
      messageRender(h) {
        return /* @__PURE__ */ x.jsx(x.Fragment, {
          children: ye(h) ? JSON.stringify(h) : h
        });
      }
    };
  }, [l, i, s, ...r]);
  return o || u;
}
function Fl(e) {
  const [t, n] = Ze(!1), r = ne(0), o = ne(!0), s = ne(!0), {
    autoScroll: i,
    scrollButtonOffset: a,
    ref: l,
    value: u
  } = e, m = se((d = "instant") => {
    l.current && (s.current = !0, requestAnimationFrame(() => {
      var p;
      (p = l.current) == null || p.scrollTo({
        offset: l.current.nativeElement.scrollHeight,
        behavior: d
      });
    }), n(!1));
  }), f = se((d = 100) => {
    if (!l.current)
      return !1;
    const p = l.current.nativeElement, y = p.scrollHeight, {
      scrollTop: h,
      clientHeight: g
    } = p;
    return y - (h + g) < d;
  });
  return Ee(() => {
    l.current && i && (u.length !== r.current && (o.current = !0), o.current && requestAnimationFrame(() => {
      m();
    }), r.current = u.length);
  }, [u, l, i, m, f]), Ee(() => {
    if (l.current && i) {
      const d = l.current.nativeElement;
      let p = 0, y = 0;
      const h = (g) => {
        const S = g.target;
        s.current ? s.current = !1 : S.scrollTop < p && S.scrollHeight >= y ? o.current = !1 : f() && (o.current = !0), p = S.scrollTop, y = S.scrollHeight, n(!f(a));
      };
      return d.addEventListener("scroll", h), () => {
        d.removeEventListener("scroll", h);
      };
    }
  }, [i, f, a]), {
    showScrollButton: t,
    scrollToBottom: m
  };
}
new Intl.Collator(0, {
  numeric: 1
}).compare;
typeof process < "u" && process.versions && process.versions.node;
var _e;
class uc extends TransformStream {
  /** Constructs a new instance. */
  constructor(n = {
    allowCR: !1
  }) {
    super({
      transform: (r, o) => {
        for (r = De(this, _e) + r; ; ) {
          const s = r.indexOf(`
`), i = n.allowCR ? r.indexOf("\r") : -1;
          if (i !== -1 && i !== r.length - 1 && (s === -1 || s - 1 > i)) {
            o.enqueue(r.slice(0, i)), r = r.slice(i + 1);
            continue;
          }
          if (s === -1) break;
          const a = r[s - 1] === "\r" ? s - 1 : s;
          o.enqueue(r.slice(0, a)), r = r.slice(s + 1);
        }
        jn(this, _e, r);
      },
      flush: (r) => {
        if (De(this, _e) === "") return;
        const o = n.allowCR && De(this, _e).endsWith("\r") ? De(this, _e).slice(0, -1) : De(this, _e);
        r.enqueue(o);
      }
    });
    On(this, _e, "");
  }
}
_e = new WeakMap();
function Ol(e) {
  try {
    const t = new URL(e);
    return t.protocol === "http:" || t.protocol === "https:";
  } catch {
    return !1;
  }
}
function jl() {
  const e = document.querySelector(".gradio-container");
  if (!e)
    return "";
  const t = e.className.match(/gradio-container-(.+)/);
  return t ? t[1] : "";
}
const kl = +jl()[0];
function nt(e, t, n) {
  const r = kl >= 5 ? "gradio_api/" : "";
  return e == null ? n ? `/proxy=${n}${r}file=` : `${t}${r}file=` : Ol(e) ? e : n ? `/proxy=${n}${r}file=${e}` : `${t}/${r}file=${e}`;
}
const Al = (e) => !!e.url;
function Ro(e, t, n) {
  if (e)
    return Al(e) ? e.url : typeof e == "string" ? e.startsWith("http") ? e : nt(e, t, n) : e;
}
const zl = ({
  options: e,
  urlProxyUrl: t,
  urlRoot: n,
  onWelcomePromptSelect: r
}) => {
  var a;
  const {
    prompts: o,
    ...s
  } = e, i = fe(() => be(o || {}, {
    omitNull: !0
  }), [o]);
  return /* @__PURE__ */ x.jsxs(Ce, {
    vertical: !0,
    gap: "middle",
    children: [/* @__PURE__ */ x.jsx(cl, {
      ...s,
      icon: Ro(s.icon, n, t),
      styles: {
        ...s == null ? void 0 : s.styles,
        icon: {
          flexShrink: 0,
          ...(a = s == null ? void 0 : s.styles) == null ? void 0 : a.icon
        }
      },
      classNames: s.class_names,
      className: N(s.elem_classes),
      style: s.elem_style
    }), /* @__PURE__ */ x.jsx(Cn, {
      ...i,
      classNames: i == null ? void 0 : i.class_names,
      className: N(i == null ? void 0 : i.elem_classes),
      style: i == null ? void 0 : i.elem_style,
      onItemClick: ({
        data: l
      }) => {
        r({
          value: l
        });
      }
    })]
  });
}, Rr = Symbol(), Ir = Symbol(), Pr = Symbol(), Mr = Symbol(), Dl = (e) => e ? typeof e == "string" ? {
  src: e
} : ((n) => !!n.url)(e) ? {
  src: e.url
} : e.src ? {
  ...e,
  src: typeof e.src == "string" ? e.src : e.src.url
} : e : void 0, Hl = (e) => typeof e == "string" ? [{
  type: "text",
  content: e
}] : Array.isArray(e) ? e.map((t) => typeof t == "string" ? {
  type: "text",
  content: t
} : t) : ye(e) ? [e] : [], Bl = (e, t) => {
  if (typeof e == "string")
    return t[0];
  if (Array.isArray(e)) {
    const n = [...e];
    return Object.keys(t).forEach((r) => {
      const o = n[r];
      typeof o == "string" ? n[r] = t[r] : n[r] = {
        ...o,
        content: t[r]
      };
    }), n;
  }
  return ye(e) ? {
    ...e,
    content: t[0]
  } : e;
}, Io = (e, t, n) => typeof e == "string" ? e : Array.isArray(e) ? e.map((r) => Io(r, t, n)).filter(Boolean).join(`
`) : ye(e) ? e.copyable ?? !0 ? typeof e.content == "string" ? e.content : e.type === "file" ? JSON.stringify(e.content.map((r) => Ro(r, t, n))) : JSON.stringify(e.content) : "" : JSON.stringify(e), Po = (e, t) => (e || []).map((n) => ({
  ...t(n),
  children: Array.isArray(n.children) ? Po(n.children, t) : void 0
})), Wl = ({
  content: e,
  className: t,
  style: n,
  disabled: r,
  urlRoot: o,
  urlProxyUrl: s,
  onCopy: i
}) => {
  const a = fe(() => Io(e, o, s), [e, s, o]), l = ne(null);
  return /* @__PURE__ */ x.jsx($e.Text, {
    copyable: {
      tooltips: !1,
      onCopy() {
        i == null || i(a);
      },
      text: a,
      icon: [/* @__PURE__ */ x.jsx(ae, {
        ref: l,
        variant: "text",
        color: "default",
        disabled: r,
        size: "small",
        className: t,
        style: n,
        icon: /* @__PURE__ */ x.jsx(rs, {})
      }, "copy"), /* @__PURE__ */ x.jsx(ae, {
        variant: "text",
        color: "default",
        size: "small",
        disabled: r,
        className: t,
        style: n,
        icon: /* @__PURE__ */ x.jsx(Fr, {})
      }, "copied")]
    }
  });
}, Vl = ({
  action: e,
  disabledActions: t,
  message: n,
  onCopy: r,
  onDelete: o,
  onEdit: s,
  onLike: i,
  onRetry: a,
  urlRoot: l,
  urlProxyUrl: u
}) => {
  var S;
  const m = ne(), f = () => ye(e) ? {
    action: e.action,
    disabled: (t == null ? void 0 : t.includes(e.action)) || !!e.disabled,
    disableHandler: !!e.popconfirm
  } : {
    action: e,
    disabled: (t == null ? void 0 : t.includes(e)) || !1,
    disableHandler: !1
  }, {
    action: d,
    disabled: p,
    disableHandler: y
  } = f(), g = (() => {
    var _, w;
    switch (d) {
      case "copy":
        return /* @__PURE__ */ x.jsx(Wl, {
          disabled: p,
          content: n.content,
          onCopy: r,
          urlRoot: l,
          urlProxyUrl: u
        });
      case "like":
        return m.current = () => i(!0), /* @__PURE__ */ x.jsx(ae, {
          variant: "text",
          color: ((_ = n.meta) == null ? void 0 : _.feedback) === "like" ? "primary" : "default",
          disabled: p,
          size: "small",
          icon: /* @__PURE__ */ x.jsx(ns, {}),
          onClick: () => {
            !y && i(!0);
          }
        });
      case "dislike":
        return m.current = () => i(!1), /* @__PURE__ */ x.jsx(ae, {
          variant: "text",
          color: ((w = n.meta) == null ? void 0 : w.feedback) === "dislike" ? "primary" : "default",
          size: "small",
          icon: /* @__PURE__ */ x.jsx(ts, {}),
          disabled: p,
          onClick: () => !y && i(!1)
        });
      case "retry":
        return m.current = a, /* @__PURE__ */ x.jsx(ae, {
          variant: "text",
          color: "default",
          size: "small",
          disabled: p,
          icon: /* @__PURE__ */ x.jsx(es, {}),
          onClick: () => !y && a()
        });
      case "edit":
        return m.current = s, /* @__PURE__ */ x.jsx(ae, {
          variant: "text",
          color: "default",
          size: "small",
          disabled: p,
          icon: /* @__PURE__ */ x.jsx(Jo, {}),
          onClick: () => !y && s()
        });
      case "delete":
        return m.current = o, /* @__PURE__ */ x.jsx(ae, {
          variant: "text",
          color: "default",
          size: "small",
          disabled: p,
          icon: /* @__PURE__ */ x.jsx(Qo, {}),
          onClick: () => !y && o()
        });
      default:
        return null;
    }
  })();
  if (ye(e)) {
    const _ = {
      ...typeof e.popconfirm == "string" ? {
        title: e.popconfirm
      } : {
        ...e.popconfirm,
        title: (S = e.popconfirm) == null ? void 0 : S.title
      },
      disabled: p,
      onConfirm() {
        var w;
        (w = m.current) == null || w.call(m);
      }
    };
    return c.createElement(e.popconfirm ? us : c.Fragment, e.popconfirm ? _ : void 0, c.createElement(e.tooltip ? ds : c.Fragment, e.tooltip ? typeof e.tooltip == "string" ? {
      title: e.tooltip
    } : e.tooltip : void 0, g));
  }
  return g;
}, Xl = ({
  isEditing: e,
  onEditCancel: t,
  onEditConfirm: n,
  onCopy: r,
  onEdit: o,
  onLike: s,
  onDelete: i,
  onRetry: a,
  editValues: l,
  message: u,
  extra: m,
  index: f,
  actions: d,
  disabledActions: p,
  urlRoot: y,
  urlProxyUrl: h
}) => e ? /* @__PURE__ */ x.jsxs(Ce, {
  justify: "end",
  children: [/* @__PURE__ */ x.jsx(ae, {
    variant: "text",
    color: "default",
    size: "small",
    icon: /* @__PURE__ */ x.jsx(Zo, {}),
    onClick: () => {
      t == null || t();
    }
  }), /* @__PURE__ */ x.jsx(ae, {
    variant: "text",
    color: "default",
    size: "small",
    icon: /* @__PURE__ */ x.jsx(Fr, {}),
    onClick: () => {
      const g = Bl(u.content, l);
      n == null || n({
        index: f,
        value: g,
        previous_value: u.content
      });
    }
  })]
}) : /* @__PURE__ */ x.jsx(Ce, {
  justify: "space-between",
  align: "center",
  gap: m && (d != null && d.length) ? "small" : void 0,
  children: (u.role === "user" ? ["extra", "actions"] : ["actions", "extra"]).map((g) => {
    switch (g) {
      case "extra":
        return /* @__PURE__ */ x.jsx($e.Text, {
          type: "secondary",
          children: m
        }, "extra");
      case "actions":
        return /* @__PURE__ */ x.jsx("div", {
          children: (d || []).map((S, _) => /* @__PURE__ */ x.jsx(Vl, {
            urlRoot: y,
            urlProxyUrl: h,
            action: S,
            disabledActions: p,
            message: u,
            onCopy: (w) => r({
              value: w,
              index: f
            }),
            onDelete: () => i({
              index: f,
              value: u.content
            }),
            onEdit: () => o(f),
            onLike: (w) => s == null ? void 0 : s({
              value: u.content,
              liked: w,
              index: f
            }),
            onRetry: () => a == null ? void 0 : a({
              index: f,
              value: u.content
            })
          }, `${S}-${_}`))
        }, "actions");
    }
  })
}), Ul = ({
  markdownConfig: e,
  title: t
}) => t ? e.renderMarkdown ? /* @__PURE__ */ x.jsx(vt, {
  ...e,
  value: t
}) : /* @__PURE__ */ x.jsx(x.Fragment, {
  children: t
}) : null, Gl = ({
  item: e,
  urlRoot: t,
  urlProxyUrl: n,
  ...r
}) => {
  const o = fe(() => e ? typeof e == "string" ? {
    url: e.startsWith("http") ? e : nt(e, t, n),
    uid: e,
    name: e.split("/").pop()
  } : {
    ...e,
    uid: e.uid || e.path || e.url,
    name: e.name || e.orig_name || (e.url || e.path).split("/").pop(),
    url: e.url || nt(e.path, t, n)
  } : {}, [e, n, t]);
  return /* @__PURE__ */ x.jsx(yo.FileCard, {
    ...r,
    imageProps: {
      ...r.imageProps
      // fixed in @ant-design/x@1.2.0
      // wrapperStyle: {
      //   width: '100%',
      //   height: '100%',
      //   ...props.imageProps?.wrapperStyle,
      // },
      // style: {
      //   width: '100%',
      //   height: '100%',
      //   objectFit: 'contain',
      //   borderRadius: token.borderRadius,
      //   ...props.imageProps?.style,
      // },
    },
    item: o
  });
}, ql = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"];
function Kl(e, t) {
  return t.some((n) => e.toLowerCase() === `.${n}`);
}
const Yl = (e, t, n) => e ? typeof e == "string" ? {
  url: e.startsWith("http") ? e : nt(e, t, n),
  uid: e,
  name: e.split("/").pop()
} : {
  ...e,
  uid: e.uid || e.path || e.url,
  name: e.name || e.orig_name || (e.url || e.path).split("/").pop(),
  url: e.url || nt(e.path, t, n)
} : {}, Zl = ({
  children: e,
  item: t
}) => {
  const {
    token: n
  } = Qe.useToken(), r = fe(() => {
    const o = t.name || "", s = o.match(/^(.*)\.[^.]+$/), i = s ? o.slice(s[1].length) : "";
    return Kl(i, ql);
  }, [t.name]);
  return /* @__PURE__ */ x.jsx("div", {
    className: "ms-gr-pro-chatbot-message-file-message-container",
    style: {
      borderRadius: n.borderRadius
    },
    children: r ? /* @__PURE__ */ x.jsxs(x.Fragment, {
      children: [" ", e]
    }) : /* @__PURE__ */ x.jsxs(x.Fragment, {
      children: [e, /* @__PURE__ */ x.jsx("div", {
        className: "ms-gr-pro-chatbot-message-file-message-toolbar",
        style: {
          backgroundColor: n.colorBgMask,
          zIndex: n.zIndexPopupBase,
          borderRadius: n.borderRadius
        },
        children: /* @__PURE__ */ x.jsx(ae, {
          icon: /* @__PURE__ */ x.jsx(os, {
            style: {
              color: n.colorWhite
            }
          }),
          variant: "link",
          color: "default",
          size: "small",
          href: t.url,
          target: "_blank",
          rel: "noopener noreferrer"
        })
      })]
    })
  });
}, Ql = ({
  value: e,
  urlProxyUrl: t,
  urlRoot: n,
  options: r
}) => {
  const {
    imageProps: o
  } = r;
  return /* @__PURE__ */ x.jsx(Ce, {
    gap: "small",
    wrap: !0,
    ...r,
    className: "ms-gr-pro-chatbot-message-file-message",
    children: e == null ? void 0 : e.map((s, i) => {
      const a = Yl(s, n, t);
      return /* @__PURE__ */ x.jsx(Zl, {
        item: a,
        children: /* @__PURE__ */ x.jsx(Gl, {
          item: a,
          urlRoot: n,
          urlProxyUrl: t,
          imageProps: o
        })
      }, `${a.uid}-${i}`);
    })
  });
}, Jl = ({
  value: e,
  options: t,
  onItemClick: n
}) => {
  const {
    elem_style: r,
    elem_classes: o,
    class_names: s,
    styles: i,
    ...a
  } = t;
  return /* @__PURE__ */ x.jsx(Cn, {
    ...a,
    classNames: s,
    className: N(o),
    style: r,
    styles: i,
    items: e,
    onItemClick: ({
      data: l
    }) => {
      n(l);
    }
  });
}, Lr = ({
  value: e,
  options: t
}) => {
  const {
    renderMarkdown: n,
    ...r
  } = t;
  return /* @__PURE__ */ x.jsx(x.Fragment, {
    children: n ? /* @__PURE__ */ x.jsx(vt, {
      ...r,
      value: e
    }) : e
  });
}, ec = ({
  value: e,
  options: t
}) => {
  const {
    renderMarkdown: n,
    status: r,
    title: o,
    ...s
  } = t, [i, a] = Ze(() => r !== "done");
  return Ee(() => {
    a(r !== "done");
  }, [r]), /* @__PURE__ */ x.jsx(x.Fragment, {
    children: /* @__PURE__ */ x.jsx(fs, {
      activeKey: i ? ["tool"] : [],
      onChange: () => {
        a(!i);
      },
      items: [{
        key: "tool",
        label: n ? /* @__PURE__ */ x.jsx(vt, {
          ...s,
          value: o
        }) : o,
        children: n ? /* @__PURE__ */ x.jsx(vt, {
          ...s,
          value: e
        }) : e
      }]
    })
  });
}, tc = ["text", "tool"], nc = ({
  isEditing: e,
  index: t,
  message: n,
  isLastMessage: r,
  markdownConfig: o,
  onEdit: s,
  onSuggestionSelect: i,
  urlProxyUrl: a,
  urlRoot: l
}) => {
  const u = ne(null), m = () => Hl(n.content).map((d, p) => {
    const y = () => {
      var h;
      if (e && (d.editable ?? !0) && tc.includes(d.type)) {
        const g = d.content, S = (h = u.current) == null ? void 0 : h.getBoundingClientRect().width;
        return /* @__PURE__ */ x.jsx("div", {
          style: {
            width: S,
            minWidth: 200,
            maxWidth: "100%"
          },
          children: /* @__PURE__ */ x.jsx(ms.TextArea, {
            autoSize: {
              minRows: 1,
              maxRows: 10
            },
            defaultValue: g,
            onChange: (_) => {
              s(p, _.target.value);
            }
          })
        });
      }
      switch (d.type) {
        case "text":
          return /* @__PURE__ */ x.jsx(Lr, {
            value: d.content,
            options: be({
              ...o,
              ...mt(d.options)
            }, {
              omitNull: !0
            })
          });
        case "tool":
          return /* @__PURE__ */ x.jsx(ec, {
            value: d.content,
            options: be({
              ...o,
              ...mt(d.options)
            }, {
              omitNull: !0
            })
          });
        case "file":
          return /* @__PURE__ */ x.jsx(Ql, {
            value: d.content,
            urlRoot: l,
            urlProxyUrl: a,
            options: be(d.options || {}, {
              omitNull: !0
            })
          });
        case "suggestion":
          return /* @__PURE__ */ x.jsx(Jl, {
            value: r ? d.content : Po(d.content, (g) => ({
              ...g,
              disabled: g.disabled ?? !0
            })),
            options: be(d.options || {}, {
              omitNull: !0
            }),
            onItemClick: (g) => {
              i({
                index: t,
                value: g
              });
            }
          });
        default:
          return typeof d.content != "string" ? null : /* @__PURE__ */ x.jsx(Lr, {
            value: d.content,
            options: be({
              ...o,
              ...mt(d.options)
            }, {
              omitNull: !0
            })
          });
      }
    };
    return /* @__PURE__ */ x.jsx(c.Fragment, {
      children: y()
    }, p);
  });
  return /* @__PURE__ */ x.jsx("div", {
    ref: u,
    children: /* @__PURE__ */ x.jsx(Ce, {
      vertical: !0,
      gap: "small",
      children: m()
    })
  });
}, dc = ni(Sl(["roles"], ({
  id: e,
  className: t,
  style: n,
  height: r,
  minHeight: o,
  maxHeight: s,
  value: i,
  roles: a,
  urlRoot: l,
  urlProxyUrl: u,
  themeMode: m,
  autoScroll: f = !0,
  showScrollToBottomButton: d = !0,
  scrollToBottomButtonOffset: p = 200,
  markdownConfig: y,
  welcomeConfig: h,
  userConfig: g,
  botConfig: S,
  onValueChange: _,
  onCopy: w,
  onChange: $,
  onEdit: R,
  onRetry: v,
  onDelete: P,
  onLike: I,
  onSuggestionSelect: F,
  onWelcomePromptSelect: T
}) => {
  const L = fe(() => ({
    variant: "borderless",
    ...h ? be(h, {
      omitNull: !0
    }) : {}
  }), [h]), O = fe(() => ({
    lineBreaks: !0,
    renderMarkdown: !0,
    ...mt(y),
    urlRoot: l,
    themeMode: m
  }), [y, m, l]), b = fe(() => g ? be(g, {
    omitNull: !0
  }) : {}, [g]), E = fe(() => S ? be(S, {
    omitNull: !0
  }) : {}, [S]), k = fe(() => {
    const C = (i || []).map((q, X) => {
      const pe = X === i.length - 1, de = be(q, {
        omitNull: !0
      });
      return {
        ...An(de, ["header", "footer", "avatar"]),
        [$o]: X,
        [Rr]: de.header,
        [Ir]: de.footer,
        [Pr]: de.avatar,
        [Mr]: pe,
        key: de.key ?? `${X}`
      };
    }).filter((q) => q.role !== "system");
    return C.length > 0 ? C : [{
      role: "chatbot-internal-welcome"
    }];
  }, [i]), D = ne(null), [B, z] = Ze(-1), [W, ie] = Ze({}), G = ne(), J = se((C, q) => {
    ie((X) => ({
      ...X,
      [C]: q
    }));
  }), U = se($);
  Ee(() => {
    Ps(G.current, i) || (U(), G.current = i);
  }, [i, U]);
  const V = se((C) => {
    F == null || F(C);
  }), K = se((C) => {
    T == null || T(C);
  }), ee = se((C) => {
    v == null || v(C);
  }), Z = se((C) => {
    z(C);
  }), Se = se(() => {
    z(-1);
  }), je = se((C) => {
    z(-1), _([...i.slice(0, C.index), {
      ...i[C.index],
      content: C.value
    }, ...i.slice(C.index + 1)]), R == null || R(C);
  }), ke = se((C) => {
    w == null || w(C);
  }), Ae = se((C) => {
    I == null || I(C), _(Tr(i, (q) => {
      const X = q[C.index].meta || {}, pe = C.liked ? "like" : "dislike";
      q[C.index] = {
        ...q[C.index],
        meta: {
          ...X,
          feedback: X.feedback === pe ? null : pe
        }
      };
    }));
  }), we = se((C) => {
    _(Tr(i, (q) => {
      q.splice(C.index, 1);
    })), P == null || P(C);
  }), ze = Nl({
    roles: a,
    preProcess(C, q) {
      var pe, de, te, Y, le, Ie, Pe, Rn, In, Pn, Mn, Ln;
      const X = C.role === "user";
      return {
        ...C,
        style: C.elem_style,
        className: N(C.elem_classes, "ms-gr-pro-chatbot-message"),
        classNames: {
          ...C.class_names,
          avatar: N(X ? (pe = b == null ? void 0 : b.class_names) == null ? void 0 : pe.avatar : (de = E == null ? void 0 : E.class_names) == null ? void 0 : de.avatar, (te = C.class_names) == null ? void 0 : te.avatar, "ms-gr-pro-chatbot-message-avatar"),
          header: N(X ? (Y = b == null ? void 0 : b.class_names) == null ? void 0 : Y.header : (le = E == null ? void 0 : E.class_names) == null ? void 0 : le.header, (Ie = C.class_names) == null ? void 0 : Ie.header, "ms-gr-pro-chatbot-message-header"),
          footer: N(X ? (Pe = b == null ? void 0 : b.class_names) == null ? void 0 : Pe.footer : (Rn = E == null ? void 0 : E.class_names) == null ? void 0 : Rn.footer, (In = C.class_names) == null ? void 0 : In.footer, "ms-gr-pro-chatbot-message-footer", q === B ? "ms-gr-pro-chatbot-message-footer-editing" : void 0),
          content: N(X ? (Pn = b == null ? void 0 : b.class_names) == null ? void 0 : Pn.content : (Mn = E == null ? void 0 : E.class_names) == null ? void 0 : Mn.content, (Ln = C.class_names) == null ? void 0 : Ln.content, "ms-gr-pro-chatbot-message-content")
        }
      };
    },
    postProcess(C, q) {
      const X = C.role === "user";
      switch (C.role) {
        case "chatbot-internal-welcome":
          return {
            variant: "borderless",
            styles: {
              content: {
                width: "100%"
              }
            },
            messageRender() {
              return /* @__PURE__ */ x.jsx(zl, {
                urlRoot: l,
                urlProxyUrl: u,
                options: L || {},
                onWelcomePromptSelect: K
              });
            }
          };
        case "user":
        case "assistant":
          return {
            ...An(X ? b : E, ["actions", "avatar", "header"]),
            ...C,
            style: {
              ...X ? b == null ? void 0 : b.style : E == null ? void 0 : E.style,
              ...C.style
            },
            className: N(C.className, X ? b == null ? void 0 : b.elem_classes : E == null ? void 0 : E.elem_classes),
            header: /* @__PURE__ */ x.jsx(Ul, {
              title: C[Rr] ?? (X ? b == null ? void 0 : b.header : E == null ? void 0 : E.header),
              markdownConfig: O
            }),
            avatar: Dl(C[Pr] ?? (X ? b == null ? void 0 : b.avatar : E == null ? void 0 : E.avatar)),
            footer: (
              // bubbleProps[lastMessageSymbol] &&
              C.loading || C.status === "pending" ? null : /* @__PURE__ */ x.jsx(Xl, {
                isEditing: B === q,
                message: C,
                extra: C[Ir] ?? (X ? b == null ? void 0 : b.footer : E == null ? void 0 : E.footer),
                urlRoot: l,
                urlProxyUrl: u,
                editValues: W,
                index: q,
                actions: C.actions ?? (X ? (b == null ? void 0 : b.actions) || [] : (E == null ? void 0 : E.actions) || []),
                disabledActions: C.disabled_actions ?? (X ? (b == null ? void 0 : b.disabled_actions) || [] : (E == null ? void 0 : E.disabled_actions) || []),
                onEditCancel: Se,
                onEditConfirm: je,
                onCopy: ke,
                onEdit: Z,
                onDelete: we,
                onRetry: ee,
                onLike: Ae
              })
            ),
            messageRender() {
              return /* @__PURE__ */ x.jsx(nc, {
                index: q,
                urlProxyUrl: u,
                urlRoot: l,
                isEditing: B === q,
                message: C,
                isLastMessage: C[Mr] || !1,
                markdownConfig: O,
                onEdit: J,
                onSuggestionSelect: V
              });
            }
          };
        default:
          return;
      }
    }
  }, [B, b, L, E, O, W]), {
    scrollToBottom: ot,
    showScrollButton: Wt
  } = Fl({
    ref: D,
    value: i,
    autoScroll: f,
    scrollButtonOffset: p
  });
  return /* @__PURE__ */ x.jsxs("div", {
    id: e,
    className: N(t, "ms-gr-pro-chatbot"),
    style: {
      height: r,
      minHeight: o,
      maxHeight: s,
      ...n
    },
    children: [/* @__PURE__ */ x.jsx(En.List, {
      ref: D,
      className: "ms-gr-pro-chatbot-messages",
      autoScroll: !1,
      roles: ze,
      items: k
    }), d && Wt && /* @__PURE__ */ x.jsx("div", {
      className: "ms-gr-pro-chatbot-scroll-to-bottom-button",
      children: /* @__PURE__ */ x.jsx(ae, {
        icon: /* @__PURE__ */ x.jsx(ss, {}),
        shape: "circle",
        variant: "outlined",
        color: "primary",
        onClick: () => ot("smooth")
      })
    })]
  });
}));
export {
  dc as Chatbot,
  dc as default
};
