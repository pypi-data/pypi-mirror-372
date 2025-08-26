import { i as Bt, a as Te, r as zt, Z as Q, g as $t, c as Z } from "./Index-BuPMJ6y0.js";
const _ = window.ms_globals.React, jt = window.ms_globals.React.version, Rt = window.ms_globals.React.forwardRef, Lt = window.ms_globals.React.useRef, At = window.ms_globals.React.useState, Dt = window.ms_globals.React.useEffect, Ht = window.ms_globals.React.useMemo, we = window.ms_globals.ReactDOM.createPortal, Xt = window.ms_globals.internalContext.useContextPropsContext, ze = window.ms_globals.internalContext.ContextPropsProvider, Ft = window.ms_globals.createItemsContext.createItemsContext, Vt = window.ms_globals.antd.ConfigProvider, Nt = window.ms_globals.antd.Dropdown, Oe = window.ms_globals.antd.theme, Ut = window.ms_globals.antd.Tooltip, Wt = window.ms_globals.antdIcons.EllipsisOutlined, $e = window.ms_globals.antdCssinjs.unit, ye = window.ms_globals.antdCssinjs.token2CSSVar, Xe = window.ms_globals.antdCssinjs.useStyleRegister, Gt = window.ms_globals.antdCssinjs.useCSSVarRegister, Kt = window.ms_globals.antdCssinjs.createTheme, qt = window.ms_globals.antdCssinjs.useCacheToken;
var Qt = /\s/;
function Zt(t) {
  for (var e = t.length; e-- && Qt.test(t.charAt(e)); )
    ;
  return e;
}
var Jt = /^\s+/;
function Yt(t) {
  return t && t.slice(0, Zt(t) + 1).replace(Jt, "");
}
var Fe = NaN, er = /^[-+]0x[0-9a-f]+$/i, tr = /^0b[01]+$/i, rr = /^0o[0-7]+$/i, nr = parseInt;
function Ve(t) {
  if (typeof t == "number")
    return t;
  if (Bt(t))
    return Fe;
  if (Te(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = Te(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Yt(t);
  var n = tr.test(t);
  return n || rr.test(t) ? nr(t.slice(2), n ? 2 : 8) : er.test(t) ? Fe : +t;
}
var ve = function() {
  return zt.Date.now();
}, or = "Expected a function", ir = Math.max, sr = Math.min;
function ar(t, e, n) {
  var o, r, i, s, a, l, c = 0, d = !1, f = !1, u = !0;
  if (typeof t != "function")
    throw new TypeError(or);
  e = Ve(e) || 0, Te(n) && (d = !!n.leading, f = "maxWait" in n, i = f ? ir(Ve(n.maxWait) || 0, e) : i, u = "trailing" in n ? !!n.trailing : u);
  function g(h) {
    var x = o, w = r;
    return o = r = void 0, c = h, s = t.apply(w, x), s;
  }
  function b(h) {
    return c = h, a = setTimeout(y, e), d ? g(h) : s;
  }
  function S(h) {
    var x = h - l, w = h - c, M = e - x;
    return f ? sr(M, i - w) : M;
  }
  function p(h) {
    var x = h - l, w = h - c;
    return l === void 0 || x >= e || x < 0 || f && w >= i;
  }
  function y() {
    var h = ve();
    if (p(h))
      return v(h);
    a = setTimeout(y, S(h));
  }
  function v(h) {
    return a = void 0, u && o ? g(h) : (o = r = void 0, s);
  }
  function P() {
    a !== void 0 && clearTimeout(a), c = 0, o = l = r = a = void 0;
  }
  function m() {
    return a === void 0 ? s : v(ve());
  }
  function T() {
    var h = ve(), x = p(h);
    if (o = arguments, r = this, l = h, x) {
      if (a === void 0)
        return b(l);
      if (f)
        return clearTimeout(a), a = setTimeout(y, e), g(l);
    }
    return a === void 0 && (a = setTimeout(y, e)), s;
  }
  return T.cancel = P, T.flush = m, T;
}
var lt = {
  exports: {}
}, oe = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var lr = _, cr = Symbol.for("react.element"), ur = Symbol.for("react.fragment"), fr = Object.prototype.hasOwnProperty, dr = lr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, hr = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ct(t, e, n) {
  var o, r = {}, i = null, s = null;
  n !== void 0 && (i = "" + n), e.key !== void 0 && (i = "" + e.key), e.ref !== void 0 && (s = e.ref);
  for (o in e) fr.call(e, o) && !hr.hasOwnProperty(o) && (r[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) r[o] === void 0 && (r[o] = e[o]);
  return {
    $$typeof: cr,
    type: t,
    key: i,
    ref: s,
    props: r,
    _owner: dr.current
  };
}
oe.Fragment = ur;
oe.jsx = ct;
oe.jsxs = ct;
lt.exports = oe;
var H = lt.exports;
const {
  SvelteComponent: gr,
  assign: Ne,
  binding_callbacks: Ue,
  check_outros: pr,
  children: ut,
  claim_element: ft,
  claim_space: mr,
  component_subscribe: We,
  compute_slots: br,
  create_slot: yr,
  detach: V,
  element: dt,
  empty: Ge,
  exclude_internal_props: Ke,
  get_all_dirty_from_scope: vr,
  get_slot_changes: xr,
  group_outros: Sr,
  init: Cr,
  insert_hydration: J,
  safe_not_equal: _r,
  set_custom_element_data: ht,
  space: wr,
  transition_in: Y,
  transition_out: Me,
  update_slot_base: Tr
} = window.__gradio__svelte__internal, {
  beforeUpdate: Or,
  getContext: Mr,
  onDestroy: Pr,
  setContext: Er
} = window.__gradio__svelte__internal;
function qe(t) {
  let e, n;
  const o = (
    /*#slots*/
    t[7].default
  ), r = yr(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = dt("svelte-slot"), r && r.c(), this.h();
    },
    l(i) {
      e = ft(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = ut(e);
      r && r.l(s), s.forEach(V), this.h();
    },
    h() {
      ht(e, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      J(i, e, s), r && r.m(e, null), t[9](e), n = !0;
    },
    p(i, s) {
      r && r.p && (!n || s & /*$$scope*/
      64) && Tr(
        r,
        o,
        i,
        /*$$scope*/
        i[6],
        n ? xr(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : vr(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      n || (Y(r, i), n = !0);
    },
    o(i) {
      Me(r, i), n = !1;
    },
    d(i) {
      i && V(e), r && r.d(i), t[9](null);
    }
  };
}
function Ir(t) {
  let e, n, o, r, i = (
    /*$$slots*/
    t[4].default && qe(t)
  );
  return {
    c() {
      e = dt("react-portal-target"), n = wr(), i && i.c(), o = Ge(), this.h();
    },
    l(s) {
      e = ft(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), ut(e).forEach(V), n = mr(s), i && i.l(s), o = Ge(), this.h();
    },
    h() {
      ht(e, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      J(s, e, a), t[8](e), J(s, n, a), i && i.m(s, a), J(s, o, a), r = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && Y(i, 1)) : (i = qe(s), i.c(), Y(i, 1), i.m(o.parentNode, o)) : i && (Sr(), Me(i, 1, 1, () => {
        i = null;
      }), pr());
    },
    i(s) {
      r || (Y(i), r = !0);
    },
    o(s) {
      Me(i), r = !1;
    },
    d(s) {
      s && (V(e), V(n), V(o)), t[8](null), i && i.d(s);
    }
  };
}
function Qe(t) {
  const {
    svelteInit: e,
    ...n
  } = t;
  return n;
}
function kr(t, e, n) {
  let o, r, {
    $$slots: i = {},
    $$scope: s
  } = e;
  const a = br(i);
  let {
    svelteInit: l
  } = e;
  const c = Q(Qe(e)), d = Q();
  We(t, d, (m) => n(0, o = m));
  const f = Q();
  We(t, f, (m) => n(1, r = m));
  const u = [], g = Mr("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: S,
    subSlotIndex: p
  } = $t() || {}, y = l({
    parent: g,
    props: c,
    target: d,
    slot: f,
    slotKey: b,
    slotIndex: S,
    subSlotIndex: p,
    onDestroy(m) {
      u.push(m);
    }
  });
  Er("$$ms-gr-react-wrapper", y), Or(() => {
    c.set(Qe(e));
  }), Pr(() => {
    u.forEach((m) => m());
  });
  function v(m) {
    Ue[m ? "unshift" : "push"](() => {
      o = m, d.set(o);
    });
  }
  function P(m) {
    Ue[m ? "unshift" : "push"](() => {
      r = m, f.set(r);
    });
  }
  return t.$$set = (m) => {
    n(17, e = Ne(Ne({}, e), Ke(m))), "svelteInit" in m && n(5, l = m.svelteInit), "$$scope" in m && n(6, s = m.$$scope);
  }, e = Ke(e), [o, r, d, f, a, l, s, i, v, P];
}
class jr extends gr {
  constructor(e) {
    super(), Cr(this, e, kr, Ir, _r, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Dn
} = window.__gradio__svelte__internal, Ze = window.ms_globals.rerender, xe = window.ms_globals.tree;
function Rr(t, e = {}) {
  function n(o) {
    const r = Q(), i = new jr({
      ...o,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: t,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: e.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, l = s.parent ?? xe;
          return l.nodes = [...l.nodes, a], Ze({
            createPortal: we,
            node: xe
          }), s.onDestroy(() => {
            l.nodes = l.nodes.filter((c) => c.svelteInstance !== r), Ze({
              createPortal: we,
              node: xe
            });
          }), a;
        },
        ...o.props
      }
    });
    return r.set(i), i;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise.then(() => {
      o(n);
    });
  });
}
const Lr = "1.6.0";
function te() {
  return te = Object.assign ? Object.assign.bind() : function(t) {
    for (var e = 1; e < arguments.length; e++) {
      var n = arguments[e];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (t[o] = n[o]);
    }
    return t;
  }, te.apply(null, arguments);
}
function A(t) {
  "@babel/helpers - typeof";
  return A = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, A(t);
}
function Ar(t, e) {
  if (A(t) != "object" || !t) return t;
  var n = t[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(t, e);
    if (A(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function gt(t) {
  var e = Ar(t, "string");
  return A(e) == "symbol" ? e : e + "";
}
function O(t, e, n) {
  return (e = gt(e)) in t ? Object.defineProperty(t, e, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : t[e] = n, t;
}
function Je(t, e) {
  var n = Object.keys(t);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(t);
    e && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(t, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function k(t) {
  for (var e = 1; e < arguments.length; e++) {
    var n = arguments[e] != null ? arguments[e] : {};
    e % 2 ? Je(Object(n), !0).forEach(function(o) {
      O(t, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(n)) : Je(Object(n)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return t;
}
var Dr = `accept acceptCharset accessKey action allowFullScreen allowTransparency
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
    summary tabIndex target title type useMap value width wmode wrap`, Hr = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, Br = "".concat(Dr, " ").concat(Hr).split(/[\s\n]+/), zr = "aria-", $r = "data-";
function Ye(t, e) {
  return t.indexOf(e) === 0;
}
function Xr(t) {
  var e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, n;
  e === !1 ? n = {
    aria: !0,
    data: !0,
    attr: !0
  } : e === !0 ? n = {
    aria: !0
  } : n = k({}, e);
  var o = {};
  return Object.keys(t).forEach(function(r) {
    // Aria
    (n.aria && (r === "role" || Ye(r, zr)) || // Data
    n.data && Ye(r, $r) || // Attr
    n.attr && Br.includes(r)) && (o[r] = t[r]);
  }), o;
}
const Fr = /* @__PURE__ */ _.createContext({}), Vr = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, Nr = (t) => {
  const e = _.useContext(Fr);
  return _.useMemo(() => ({
    ...Vr,
    ...e[t]
  }), [e[t]]);
};
function re() {
  const {
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = _.useContext(Vt.ConfigContext);
  return {
    theme: r,
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o
  };
}
const U = (t, e) => {
  const n = t[0];
  for (const o of e)
    if (o.key === n) {
      if (t.length === 1) return o;
      if ("children" in o)
        return U(t.slice(1), o.children);
    }
  return null;
}, Ur = (t) => {
  const {
    onClick: e,
    item: n
  } = t, {
    children: o = [],
    triggerSubMenuAction: r = "hover"
  } = n, {
    getPrefixCls: i
  } = re(), s = i("actions", t.prefixCls), a = (n == null ? void 0 : n.icon) ?? /* @__PURE__ */ _.createElement(Wt, null), l = {
    items: o,
    onClick: ({
      key: c,
      keyPath: d,
      domEvent: f
    }) => {
      var u, g, b;
      if ((u = U(d, o)) != null && u.onItemClick) {
        (b = (g = U(d, o)) == null ? void 0 : g.onItemClick) == null || b.call(g, U(d, o));
        return;
      }
      e == null || e({
        key: c,
        keyPath: [...d, n.key],
        domEvent: f,
        item: U(d, o)
      });
    }
  };
  return /* @__PURE__ */ _.createElement(Nt, {
    menu: l,
    overlayClassName: `${s}-sub-item`,
    arrow: !0,
    trigger: [r]
  }, /* @__PURE__ */ _.createElement("div", {
    className: `${s}-list-item`
  }, /* @__PURE__ */ _.createElement("div", {
    className: `${s}-list-item-icon`
  }, a)));
};
function Wr(t) {
  if (Array.isArray(t)) return t;
}
function Gr(t, e) {
  var n = t == null ? null : typeof Symbol < "u" && t[Symbol.iterator] || t["@@iterator"];
  if (n != null) {
    var o, r, i, s, a = [], l = !0, c = !1;
    try {
      if (i = (n = n.call(t)).next, e === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (o = i.call(n)).done) && (a.push(o.value), a.length !== e); l = !0) ;
    } catch (d) {
      c = !0, r = d;
    } finally {
      try {
        if (!l && n.return != null && (s = n.return(), Object(s) !== s)) return;
      } finally {
        if (c) throw r;
      }
    }
    return a;
  }
}
function et(t, e) {
  (e == null || e > t.length) && (e = t.length);
  for (var n = 0, o = Array(e); n < e; n++) o[n] = t[n];
  return o;
}
function Kr(t, e) {
  if (t) {
    if (typeof t == "string") return et(t, e);
    var n = {}.toString.call(t).slice(8, -1);
    return n === "Object" && t.constructor && (n = t.constructor.name), n === "Map" || n === "Set" ? Array.from(t) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? et(t, e) : void 0;
  }
}
function qr() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function ee(t, e) {
  return Wr(t) || Gr(t, e) || Kr(t, e) || qr();
}
function ie(t, e) {
  if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function");
}
function Qr(t, e) {
  for (var n = 0; n < e.length; n++) {
    var o = e[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, gt(o.key), o);
  }
}
function se(t, e, n) {
  return e && Qr(t.prototype, e), Object.defineProperty(t, "prototype", {
    writable: !1
  }), t;
}
function W(t) {
  if (t === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return t;
}
function Pe(t, e) {
  return Pe = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, Pe(t, e);
}
function pt(t, e) {
  if (typeof e != "function" && e !== null) throw new TypeError("Super expression must either be null or a function");
  t.prototype = Object.create(e && e.prototype, {
    constructor: {
      value: t,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(t, "prototype", {
    writable: !1
  }), e && Pe(t, e);
}
function ne(t) {
  return ne = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
    return e.__proto__ || Object.getPrototypeOf(e);
  }, ne(t);
}
function mt() {
  try {
    var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (mt = function() {
    return !!t;
  })();
}
function Zr(t, e) {
  if (e && (A(e) == "object" || typeof e == "function")) return e;
  if (e !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return W(t);
}
function bt(t) {
  var e = mt();
  return function() {
    var n, o = ne(t);
    if (e) {
      var r = ne(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return Zr(this, n);
  };
}
var yt = /* @__PURE__ */ se(function t() {
  ie(this, t);
}), vt = "CALC_UNIT", Jr = new RegExp(vt, "g");
function Se(t) {
  return typeof t == "number" ? "".concat(t).concat(vt) : t;
}
var Yr = /* @__PURE__ */ function(t) {
  pt(n, t);
  var e = bt(n);
  function n(o, r) {
    var i;
    ie(this, n), i = e.call(this), O(W(i), "result", ""), O(W(i), "unitlessCssVar", void 0), O(W(i), "lowPriority", void 0);
    var s = A(o);
    return i.unitlessCssVar = r, o instanceof n ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = Se(o) : s === "string" && (i.result = o), i;
  }
  return se(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(Se(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(Se(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(r) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), r instanceof n ? this.result = "".concat(this.result, " * ").concat(r.getResult(!0)) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " * ").concat(r)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(r) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), r instanceof n ? this.result = "".concat(this.result, " / ").concat(r.getResult(!0)) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " / ").concat(r)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(r) {
      return this.lowPriority || r ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(r) {
      var i = this, s = r || {}, a = s.unit, l = !0;
      return typeof a == "boolean" ? l = a : Array.from(this.unitlessCssVar).some(function(c) {
        return i.result.includes(c);
      }) && (l = !1), this.result = this.result.replace(Jr, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(yt), en = /* @__PURE__ */ function(t) {
  pt(n, t);
  var e = bt(n);
  function n(o) {
    var r;
    return ie(this, n), r = e.call(this), O(W(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return se(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result += r.result : typeof r == "number" && (this.result += r), this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result -= r.result : typeof r == "number" && (this.result -= r), this;
    }
  }, {
    key: "mul",
    value: function(r) {
      return r instanceof n ? this.result *= r.result : typeof r == "number" && (this.result *= r), this;
    }
  }, {
    key: "div",
    value: function(r) {
      return r instanceof n ? this.result /= r.result : typeof r == "number" && (this.result /= r), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), n;
}(yt), tn = function(e, n) {
  var o = e === "css" ? Yr : en;
  return function(r) {
    return new o(r, n);
  };
}, tt = function(e, n) {
  return "".concat([n, e.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
}, C = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var ke = Symbol.for("react.element"), je = Symbol.for("react.portal"), ae = Symbol.for("react.fragment"), le = Symbol.for("react.strict_mode"), ce = Symbol.for("react.profiler"), ue = Symbol.for("react.provider"), fe = Symbol.for("react.context"), rn = Symbol.for("react.server_context"), de = Symbol.for("react.forward_ref"), he = Symbol.for("react.suspense"), ge = Symbol.for("react.suspense_list"), pe = Symbol.for("react.memo"), me = Symbol.for("react.lazy"), nn = Symbol.for("react.offscreen"), xt;
xt = Symbol.for("react.module.reference");
function L(t) {
  if (typeof t == "object" && t !== null) {
    var e = t.$$typeof;
    switch (e) {
      case ke:
        switch (t = t.type, t) {
          case ae:
          case ce:
          case le:
          case he:
          case ge:
            return t;
          default:
            switch (t = t && t.$$typeof, t) {
              case rn:
              case fe:
              case de:
              case me:
              case pe:
              case ue:
                return t;
              default:
                return e;
            }
        }
      case je:
        return e;
    }
  }
}
C.ContextConsumer = fe;
C.ContextProvider = ue;
C.Element = ke;
C.ForwardRef = de;
C.Fragment = ae;
C.Lazy = me;
C.Memo = pe;
C.Portal = je;
C.Profiler = ce;
C.StrictMode = le;
C.Suspense = he;
C.SuspenseList = ge;
C.isAsyncMode = function() {
  return !1;
};
C.isConcurrentMode = function() {
  return !1;
};
C.isContextConsumer = function(t) {
  return L(t) === fe;
};
C.isContextProvider = function(t) {
  return L(t) === ue;
};
C.isElement = function(t) {
  return typeof t == "object" && t !== null && t.$$typeof === ke;
};
C.isForwardRef = function(t) {
  return L(t) === de;
};
C.isFragment = function(t) {
  return L(t) === ae;
};
C.isLazy = function(t) {
  return L(t) === me;
};
C.isMemo = function(t) {
  return L(t) === pe;
};
C.isPortal = function(t) {
  return L(t) === je;
};
C.isProfiler = function(t) {
  return L(t) === ce;
};
C.isStrictMode = function(t) {
  return L(t) === le;
};
C.isSuspense = function(t) {
  return L(t) === he;
};
C.isSuspenseList = function(t) {
  return L(t) === ge;
};
C.isValidElementType = function(t) {
  return typeof t == "string" || typeof t == "function" || t === ae || t === ce || t === le || t === he || t === ge || t === nn || typeof t == "object" && t !== null && (t.$$typeof === me || t.$$typeof === pe || t.$$typeof === ue || t.$$typeof === fe || t.$$typeof === de || t.$$typeof === xt || t.getModuleId !== void 0);
};
C.typeOf = L;
Number(jt.split(".")[0]);
function rt(t, e, n, o) {
  var r = k({}, e[t]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var l = ee(a, 2), c = l[0], d = l[1];
      if (r != null && r[c] || r != null && r[d]) {
        var f;
        (f = r[d]) !== null && f !== void 0 || (r[d] = r == null ? void 0 : r[c]);
      }
    });
  }
  var s = k(k({}, n), r);
  return Object.keys(s).forEach(function(a) {
    s[a] === e[a] && delete s[a];
  }), s;
}
var St = typeof CSSINJS_STATISTIC < "u", Ee = !0;
function Re() {
  for (var t = arguments.length, e = new Array(t), n = 0; n < t; n++)
    e[n] = arguments[n];
  if (!St)
    return Object.assign.apply(Object, [{}].concat(e));
  Ee = !1;
  var o = {};
  return e.forEach(function(r) {
    if (A(r) === "object") {
      var i = Object.keys(r);
      i.forEach(function(s) {
        Object.defineProperty(o, s, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return r[s];
          }
        });
      });
    }
  }), Ee = !0, o;
}
var nt = {};
function on() {
}
var sn = function(e) {
  var n, o = e, r = on;
  return St && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(e, {
    get: function(s, a) {
      if (Ee) {
        var l;
        (l = n) === null || l === void 0 || l.add(a);
      }
      return s[a];
    }
  }), r = function(s, a) {
    var l;
    nt[s] = {
      global: Array.from(n),
      component: k(k({}, (l = nt[s]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function ot(t, e, n) {
  if (typeof n == "function") {
    var o;
    return n(Re(e, (o = e[t]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function an(t) {
  return t === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(i) {
        return $e(i);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(i) {
        return $e(i);
      }).join(","), ")");
    }
  };
}
var ln = 1e3 * 60 * 10, cn = /* @__PURE__ */ function() {
  function t() {
    ie(this, t), O(this, "map", /* @__PURE__ */ new Map()), O(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), O(this, "nextID", 0), O(this, "lastAccessBeat", /* @__PURE__ */ new Map()), O(this, "accessBeat", 0);
  }
  return se(t, [{
    key: "set",
    value: function(n, o) {
      this.clear();
      var r = this.getCompositeKey(n);
      this.map.set(r, o), this.lastAccessBeat.set(r, Date.now());
    }
  }, {
    key: "get",
    value: function(n) {
      var o = this.getCompositeKey(n), r = this.map.get(o);
      return this.lastAccessBeat.set(o, Date.now()), this.accessBeat += 1, r;
    }
  }, {
    key: "getCompositeKey",
    value: function(n) {
      var o = this, r = n.map(function(i) {
        return i && A(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(A(i), "_").concat(i);
      });
      return r.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(n) {
      if (this.objectIDMap.has(n))
        return this.objectIDMap.get(n);
      var o = this.nextID;
      return this.objectIDMap.set(n, o), this.nextID += 1, o;
    }
  }, {
    key: "clear",
    value: function() {
      var n = this;
      if (this.accessBeat > 1e4) {
        var o = Date.now();
        this.lastAccessBeat.forEach(function(r, i) {
          o - r > ln && (n.map.delete(i), n.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), t;
}(), it = new cn();
function un(t, e) {
  return _.useMemo(function() {
    var n = it.get(e);
    if (n)
      return n;
    var o = t();
    return it.set(e, o), o;
  }, e);
}
var fn = function() {
  return {};
};
function dn(t) {
  var e = t.useCSP, n = e === void 0 ? fn : e, o = t.useToken, r = t.usePrefix, i = t.getResetStyles, s = t.getCommonStyle, a = t.getCompUnitless;
  function l(u, g, b, S) {
    var p = Array.isArray(u) ? u[0] : u;
    function y(w) {
      return "".concat(String(p)).concat(w.slice(0, 1).toUpperCase()).concat(w.slice(1));
    }
    var v = (S == null ? void 0 : S.unitless) || {}, P = typeof a == "function" ? a(u) : {}, m = k(k({}, P), {}, O({}, y("zIndexPopup"), !0));
    Object.keys(v).forEach(function(w) {
      m[y(w)] = v[w];
    });
    var T = k(k({}, S), {}, {
      unitless: m,
      prefixToken: y
    }), h = d(u, g, b, T), x = c(p, b, T);
    return function(w) {
      var M = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : w, j = h(w, M), z = ee(j, 2), I = z[1], $ = x(M), R = ee($, 2), D = R[0], G = R[1];
      return [D, I, G];
    };
  }
  function c(u, g, b) {
    var S = b.unitless, p = b.injectStyle, y = p === void 0 ? !0 : p, v = b.prefixToken, P = b.ignore, m = function(x) {
      var w = x.rootCls, M = x.cssVar, j = M === void 0 ? {} : M, z = o(), I = z.realToken;
      return Gt({
        path: [u],
        prefix: j.prefix,
        key: j.key,
        unitless: S,
        ignore: P,
        token: I,
        scope: w
      }, function() {
        var $ = ot(u, I, g), R = rt(u, I, $, {
          deprecatedTokens: b == null ? void 0 : b.deprecatedTokens
        });
        return Object.keys($).forEach(function(D) {
          R[v(D)] = R[D], delete R[D];
        }), R;
      }), null;
    }, T = function(x) {
      var w = o(), M = w.cssVar;
      return [function(j) {
        return y && M ? /* @__PURE__ */ _.createElement(_.Fragment, null, /* @__PURE__ */ _.createElement(m, {
          rootCls: x,
          cssVar: M,
          component: u
        }), j) : j;
      }, M == null ? void 0 : M.key];
    };
    return T;
  }
  function d(u, g, b) {
    var S = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = Array.isArray(u) ? u : [u, u], y = ee(p, 1), v = y[0], P = p.join("-"), m = t.layer || {
      name: "antd"
    };
    return function(T) {
      var h = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : T, x = o(), w = x.theme, M = x.realToken, j = x.hashId, z = x.token, I = x.cssVar, $ = r(), R = $.rootPrefixCls, D = $.iconPrefixCls, G = n(), be = I ? "css" : "js", wt = un(function() {
        var X = /* @__PURE__ */ new Set();
        return I && Object.keys(S.unitless || {}).forEach(function(K) {
          X.add(ye(K, I.prefix)), X.add(ye(K, tt(v, I.prefix)));
        }), tn(be, X);
      }, [be, v, I == null ? void 0 : I.prefix]), Le = an(be), Tt = Le.max, Ot = Le.min, Ae = {
        theme: w,
        token: z,
        hashId: j,
        nonce: function() {
          return G.nonce;
        },
        clientOnly: S.clientOnly,
        layer: m,
        // antd is always at top of styles
        order: S.order || -999
      };
      typeof i == "function" && Xe(k(k({}, Ae), {}, {
        clientOnly: !1,
        path: ["Shared", R]
      }), function() {
        return i(z, {
          prefix: {
            rootPrefixCls: R,
            iconPrefixCls: D
          },
          csp: G
        });
      });
      var Mt = Xe(k(k({}, Ae), {}, {
        path: [P, T, D]
      }), function() {
        if (S.injectStyle === !1)
          return [];
        var X = sn(z), K = X.token, Pt = X.flush, F = ot(v, M, b), Et = ".".concat(T), De = rt(v, M, F, {
          deprecatedTokens: S.deprecatedTokens
        });
        I && F && A(F) === "object" && Object.keys(F).forEach(function(Be) {
          F[Be] = "var(".concat(ye(Be, tt(v, I.prefix)), ")");
        });
        var He = Re(K, {
          componentCls: Et,
          prefixCls: T,
          iconCls: ".".concat(D),
          antCls: ".".concat(R),
          calc: wt,
          // @ts-ignore
          max: Tt,
          // @ts-ignore
          min: Ot
        }, I ? F : De), It = g(He, {
          hashId: j,
          prefixCls: T,
          rootPrefixCls: R,
          iconPrefixCls: D
        });
        Pt(v, De);
        var kt = typeof s == "function" ? s(He, T, h, S.resetFont) : null;
        return [S.resetStyle === !1 ? null : kt, It];
      });
      return [Mt, j];
    };
  }
  function f(u, g, b) {
    var S = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = d(u, g, b, k({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, S)), y = function(P) {
      var m = P.prefixCls, T = P.rootCls, h = T === void 0 ? m : T;
      return p(m, h), null;
    };
    return y;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: f,
    genComponentStyleHook: d
  };
}
const hn = {
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
}, gn = Object.assign(Object.assign({}, hn), {
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
}), E = Math.round;
function Ce(t, e) {
  const n = t.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = e(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const st = (t, e, n) => n === 0 ? t : t / 100;
function N(t, e) {
  const n = e || 255;
  return t > n ? n : t < 0 ? 0 : t;
}
class B {
  constructor(e) {
    O(this, "isValid", !0), O(this, "r", 0), O(this, "g", 0), O(this, "b", 0), O(this, "a", 1), O(this, "_h", void 0), O(this, "_s", void 0), O(this, "_l", void 0), O(this, "_v", void 0), O(this, "_max", void 0), O(this, "_min", void 0), O(this, "_brightness", void 0);
    function n(o) {
      return o[0] in e && o[1] in e && o[2] in e;
    }
    if (e) if (typeof e == "string") {
      let r = function(i) {
        return o.startsWith(i);
      };
      const o = e.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (e instanceof B)
      this.r = e.r, this.g = e.g, this.b = e.b, this.a = e.a, this._h = e._h, this._s = e._s, this._l = e._l, this._v = e._v;
    else if (n("rgb"))
      this.r = N(e.r), this.g = N(e.g), this.b = N(e.b), this.a = typeof e.a == "number" ? N(e.a, 1) : 1;
    else if (n("hsl"))
      this.fromHsl(e);
    else if (n("hsv"))
      this.fromHsv(e);
    else
      throw new Error("@ant-design/fast-color: unsupported input " + JSON.stringify(e));
  }
  // ======================= Setter =======================
  setR(e) {
    return this._sc("r", e);
  }
  setG(e) {
    return this._sc("g", e);
  }
  setB(e) {
    return this._sc("b", e);
  }
  setA(e) {
    return this._sc("a", e, 1);
  }
  setHue(e) {
    const n = this.toHsv();
    return n.h = e, this._c(n);
  }
  // ======================= Getter =======================
  /**
   * Returns the perceived luminance of a color, from 0-1.
   * @see http://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
   */
  getLuminance() {
    function e(i) {
      const s = i / 255;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    }
    const n = e(this.r), o = e(this.g), r = e(this.b);
    return 0.2126 * n + 0.7152 * o + 0.0722 * r;
  }
  getHue() {
    if (typeof this._h > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._h = 0 : this._h = E(60 * (this.r === this.getMax() ? (this.g - this.b) / e + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / e + 2 : (this.r - this.g) / e + 4));
    }
    return this._h;
  }
  getSaturation() {
    if (typeof this._s > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._s = 0 : this._s = e / this.getMax();
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
  darken(e = 10) {
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() - e / 100;
    return r < 0 && (r = 0), this._c({
      h: n,
      s: o,
      l: r,
      a: this.a
    });
  }
  lighten(e = 10) {
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() + e / 100;
    return r > 1 && (r = 1), this._c({
      h: n,
      s: o,
      l: r,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(e, n = 50) {
    const o = this._c(e), r = n / 100, i = (a) => (o[a] - this[a]) * r + this[a], s = {
      r: E(i("r")),
      g: E(i("g")),
      b: E(i("b")),
      a: E(i("a") * 100) / 100
    };
    return this._c(s);
  }
  /**
   * Mix the color with pure white, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return white.
   */
  tint(e = 10) {
    return this.mix({
      r: 255,
      g: 255,
      b: 255,
      a: 1
    }, e);
  }
  /**
   * Mix the color with pure black, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return black.
   */
  shade(e = 10) {
    return this.mix({
      r: 0,
      g: 0,
      b: 0,
      a: 1
    }, e);
  }
  onBackground(e) {
    const n = this._c(e), o = this.a + n.a * (1 - this.a), r = (i) => E((this[i] * this.a + n[i] * n.a * (1 - this.a)) / o);
    return this._c({
      r: r("r"),
      g: r("g"),
      b: r("b"),
      a: o
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
  equals(e) {
    return this.r === e.r && this.g === e.g && this.b === e.b && this.a === e.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let e = "#";
    const n = (this.r || 0).toString(16);
    e += n.length === 2 ? n : "0" + n;
    const o = (this.g || 0).toString(16);
    e += o.length === 2 ? o : "0" + o;
    const r = (this.b || 0).toString(16);
    if (e += r.length === 2 ? r : "0" + r, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const i = E(this.a * 255).toString(16);
      e += i.length === 2 ? i : "0" + i;
    }
    return e;
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
    const e = this.getHue(), n = E(this.getSaturation() * 100), o = E(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${e},${n}%,${o}%,${this.a})` : `hsl(${e},${n}%,${o}%)`;
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
  _sc(e, n, o) {
    const r = this.clone();
    return r[e] = N(n, o), r;
  }
  _c(e) {
    return new this.constructor(e);
  }
  getMax() {
    return typeof this._max > "u" && (this._max = Math.max(this.r, this.g, this.b)), this._max;
  }
  getMin() {
    return typeof this._min > "u" && (this._min = Math.min(this.r, this.g, this.b)), this._min;
  }
  fromHexString(e) {
    const n = e.replace("#", "");
    function o(r, i) {
      return parseInt(n[r] + n[i || r], 16);
    }
    n.length < 6 ? (this.r = o(0), this.g = o(1), this.b = o(2), this.a = n[3] ? o(3) / 255 : 1) : (this.r = o(0, 1), this.g = o(2, 3), this.b = o(4, 5), this.a = n[6] ? o(6, 7) / 255 : 1);
  }
  fromHsl({
    h: e,
    s: n,
    l: o,
    a: r
  }) {
    if (this._h = e % 360, this._s = n, this._l = o, this.a = typeof r == "number" ? r : 1, n <= 0) {
      const u = E(o * 255);
      this.r = u, this.g = u, this.b = u;
    }
    let i = 0, s = 0, a = 0;
    const l = e / 60, c = (1 - Math.abs(2 * o - 1)) * n, d = c * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (i = c, s = d) : l >= 1 && l < 2 ? (i = d, s = c) : l >= 2 && l < 3 ? (s = c, a = d) : l >= 3 && l < 4 ? (s = d, a = c) : l >= 4 && l < 5 ? (i = d, a = c) : l >= 5 && l < 6 && (i = c, a = d);
    const f = o - c / 2;
    this.r = E((i + f) * 255), this.g = E((s + f) * 255), this.b = E((a + f) * 255);
  }
  fromHsv({
    h: e,
    s: n,
    v: o,
    a: r
  }) {
    this._h = e % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const i = E(o * 255);
    if (this.r = i, this.g = i, this.b = i, n <= 0)
      return;
    const s = e / 60, a = Math.floor(s), l = s - a, c = E(o * (1 - n) * 255), d = E(o * (1 - n * l) * 255), f = E(o * (1 - n * (1 - l)) * 255);
    switch (a) {
      case 0:
        this.g = f, this.b = c;
        break;
      case 1:
        this.r = d, this.b = c;
        break;
      case 2:
        this.r = c, this.b = f;
        break;
      case 3:
        this.r = c, this.g = d;
        break;
      case 4:
        this.r = f, this.g = c;
        break;
      case 5:
      default:
        this.g = c, this.b = d;
        break;
    }
  }
  fromHsvString(e) {
    const n = Ce(e, st);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(e) {
    const n = Ce(e, st);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(e) {
    const n = Ce(e, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? E(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function _e(t) {
  return t >= 0 && t <= 255;
}
function q(t, e) {
  const {
    r: n,
    g: o,
    b: r,
    a: i
  } = new B(t).toRgb();
  if (i < 1)
    return t;
  const {
    r: s,
    g: a,
    b: l
  } = new B(e).toRgb();
  for (let c = 0.01; c <= 1; c += 0.01) {
    const d = Math.round((n - s * (1 - c)) / c), f = Math.round((o - a * (1 - c)) / c), u = Math.round((r - l * (1 - c)) / c);
    if (_e(d) && _e(f) && _e(u))
      return new B({
        r: d,
        g: f,
        b: u,
        a: Math.round(c * 100) / 100
      }).toRgbString();
  }
  return new B({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var pn = function(t, e) {
  var n = {};
  for (var o in t) Object.prototype.hasOwnProperty.call(t, o) && e.indexOf(o) < 0 && (n[o] = t[o]);
  if (t != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(t); r < o.length; r++)
    e.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(t, o[r]) && (n[o[r]] = t[o[r]]);
  return n;
};
function mn(t) {
  const {
    override: e
  } = t, n = pn(t, ["override"]), o = Object.assign({}, e);
  Object.keys(gn).forEach((u) => {
    delete o[u];
  });
  const r = Object.assign(Object.assign({}, n), o), i = 480, s = 576, a = 768, l = 992, c = 1200, d = 1600;
  if (r.motion === !1) {
    const u = "0s";
    r.motionDurationFast = u, r.motionDurationMid = u, r.motionDurationSlow = u;
  }
  return Object.assign(Object.assign(Object.assign({}, r), {
    // ============== Background ============== //
    colorFillContent: r.colorFillSecondary,
    colorFillContentHover: r.colorFill,
    colorFillAlter: r.colorFillQuaternary,
    colorBgContainerDisabled: r.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: r.colorBgContainer,
    colorSplit: q(r.colorBorderSecondary, r.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: r.colorTextQuaternary,
    colorTextDisabled: r.colorTextQuaternary,
    colorTextHeading: r.colorText,
    colorTextLabel: r.colorTextSecondary,
    colorTextDescription: r.colorTextTertiary,
    colorTextLightSolid: r.colorWhite,
    colorHighlight: r.colorError,
    colorBgTextHover: r.colorFillSecondary,
    colorBgTextActive: r.colorFill,
    colorIcon: r.colorTextTertiary,
    colorIconHover: r.colorText,
    colorErrorOutline: q(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: q(r.colorWarningBg, r.colorBgContainer),
    // Font
    fontSizeIcon: r.fontSizeSM,
    // Line
    lineWidthFocus: r.lineWidth * 3,
    // Control
    lineWidth: r.lineWidth,
    controlOutlineWidth: r.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: r.controlHeight / 2,
    controlItemBgHover: r.colorFillTertiary,
    controlItemBgActive: r.colorPrimaryBg,
    controlItemBgActiveHover: r.colorPrimaryBgHover,
    controlItemBgActiveDisabled: r.colorFill,
    controlTmpOutline: r.colorFillQuaternary,
    controlOutline: q(r.colorPrimaryBg, r.colorBgContainer),
    lineType: r.lineType,
    borderRadius: r.borderRadius,
    borderRadiusXS: r.borderRadiusXS,
    borderRadiusSM: r.borderRadiusSM,
    borderRadiusLG: r.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: r.sizeXXS,
    paddingXS: r.sizeXS,
    paddingSM: r.sizeSM,
    padding: r.size,
    paddingMD: r.sizeMD,
    paddingLG: r.sizeLG,
    paddingXL: r.sizeXL,
    paddingContentHorizontalLG: r.sizeLG,
    paddingContentVerticalLG: r.sizeMS,
    paddingContentHorizontal: r.sizeMS,
    paddingContentVertical: r.sizeSM,
    paddingContentHorizontalSM: r.size,
    paddingContentVerticalSM: r.sizeXS,
    marginXXS: r.sizeXXS,
    marginXS: r.sizeXS,
    marginSM: r.sizeSM,
    margin: r.size,
    marginMD: r.sizeMD,
    marginLG: r.sizeLG,
    marginXL: r.sizeXL,
    marginXXL: r.sizeXXL,
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
    screenXS: i,
    screenXSMin: i,
    screenXSMax: s - 1,
    screenSM: s,
    screenSMMin: s,
    screenSMMax: a - 1,
    screenMD: a,
    screenMDMin: a,
    screenMDMax: l - 1,
    screenLG: l,
    screenLGMin: l,
    screenLGMax: c - 1,
    screenXL: c,
    screenXLMin: c,
    screenXLMax: d - 1,
    screenXXL: d,
    screenXXLMin: d,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new B("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new B("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new B("rgba(0, 0, 0, 0.09)").toRgbString()}
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
  }), o);
}
const bn = {
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
}, yn = {
  motionBase: !0,
  motionUnit: !0
}, vn = Kt(Oe.defaultAlgorithm), xn = {
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
}, Ct = (t, e, n) => {
  const o = n.getDerivativeToken(t), {
    override: r,
    ...i
  } = e;
  let s = {
    ...o,
    override: r
  };
  return s = mn(s), i && Object.entries(i).forEach(([a, l]) => {
    const {
      theme: c,
      ...d
    } = l;
    let f = d;
    c && (f = Ct({
      ...s,
      ...d
    }, {
      override: d
    }, c)), s[a] = f;
  }), s;
};
function Sn() {
  const {
    token: t,
    hashed: e,
    theme: n = vn,
    override: o,
    cssVar: r
  } = _.useContext(Oe._internalContext), [i, s, a] = qt(n, [Oe.defaultSeed, t], {
    salt: `${Lr}-${e || ""}`,
    override: o,
    getComputedToken: Ct,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: bn,
      ignore: yn,
      preserve: xn
    }
  });
  return [n, a, e ? s : "", i, r];
}
const {
  genStyleHooks: Cn
} = dn({
  usePrefix: () => {
    const {
      getPrefixCls: t,
      iconPrefixCls: e
    } = re();
    return {
      iconPrefixCls: e,
      rootPrefixCls: t()
    };
  },
  useToken: () => {
    const [t, e, n, o, r] = Sn();
    return {
      theme: t,
      realToken: e,
      hashId: n,
      token: o,
      cssVar: r
    };
  },
  useCSP: () => {
    const {
      csp: t
    } = re();
    return t ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), _n = (t) => {
  const {
    componentCls: e,
    calc: n
  } = t;
  return {
    [e]: {
      [`&${e}-rtl`]: {
        direction: "rtl"
      },
      [`${e}-list`]: {
        display: "inline-flex",
        flexDirection: "row",
        gap: t.paddingXS,
        color: t.colorTextDescription,
        "&-item, &-sub-item": {
          cursor: "pointer",
          padding: t.paddingXXS,
          borderRadius: t.borderRadius,
          height: t.controlHeightSM,
          width: t.controlHeightSM,
          boxSizing: "border-box",
          display: "inline-flex",
          alignItems: "center",
          justifyContent: "center",
          "&-icon": {
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: t.fontSize,
            width: "100%",
            height: "100%"
          },
          "&:hover": {
            background: t.colorBgTextHover
          }
        }
      },
      "& .border": {
        padding: `${t.paddingXS} ${t.paddingSM}`,
        gap: t.paddingSM,
        borderRadius: n(t.borderRadiusLG).mul(1.5).equal(),
        backgroundColor: t.colorBorderSecondary,
        color: t.colorTextSecondary,
        [`${e}-list-item, ${e}-list-sub-item`]: {
          padding: 0,
          lineHeight: t.lineHeight,
          "&-icon": {
            fontSize: t.fontSizeLG
          },
          "&:hover": {
            opacity: 0.8
          }
        }
      },
      "& .block": {
        display: "flex"
      }
    }
  };
}, wn = () => ({}), Tn = Cn("Actions", (t) => {
  const e = Re(t, {});
  return [_n(e)];
}, wn), On = (t) => {
  const {
    prefixCls: e,
    rootClassName: n = {},
    style: o = {},
    variant: r = "borderless",
    block: i = !1,
    onClick: s,
    items: a = [],
    ...l
  } = t, c = Xr(l, {
    attr: !0,
    aria: !0,
    data: !0
  }), {
    getPrefixCls: d,
    direction: f
  } = re(), u = d("actions", e), g = Nr("actions"), [b, S, p] = Tn(u), y = Z(u, g.className, n, p, S, {
    [`${u}-rtl`]: f === "rtl"
  }), v = {
    ...g.style,
    ...o
  }, P = (h, x, w) => x ? /* @__PURE__ */ _.createElement(Ut, te({}, w, {
    title: x
  }), h) : h, m = (h, x, w) => {
    if (x.onItemClick) {
      x.onItemClick(x);
      return;
    }
    s == null || s({
      key: h,
      item: x,
      keyPath: [h],
      domEvent: w
    });
  }, T = (h) => {
    const {
      icon: x,
      label: w,
      key: M
    } = h;
    return /* @__PURE__ */ _.createElement("div", {
      className: Z(`${u}-list-item`),
      onClick: (j) => m(M, h, j),
      key: M
    }, P(/* @__PURE__ */ _.createElement("div", {
      className: `${u}-list-item-icon`
    }, x), w));
  };
  return b(/* @__PURE__ */ _.createElement("div", te({
    className: y
  }, c, {
    style: v
  }), /* @__PURE__ */ _.createElement("div", {
    className: Z(`${u}-list`, r, i)
  }, a.map((h) => "children" in h ? /* @__PURE__ */ _.createElement(Ur, {
    key: h.key,
    item: h,
    prefixCls: u,
    onClick: s
  }) : T(h)))));
}, Mn = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Pn(t) {
  return t ? Object.keys(t).reduce((e, n) => {
    const o = t[n];
    return e[n] = En(n, o), e;
  }, {}) : {};
}
function En(t, e) {
  return typeof e == "number" && !Mn.includes(t) ? e + "px" : e;
}
function Ie(t) {
  const e = [], n = t.cloneNode(!1);
  if (t._reactElement) {
    const r = _.Children.toArray(t._reactElement.props.children).map((i) => {
      if (_.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = Ie(i.props.el);
        return _.cloneElement(i, {
          ...i.props,
          el: a,
          children: [..._.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(we(_.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: r
    }), n)), {
      clonedElement: n,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((r) => {
    t.getEventListeners(r).forEach(({
      listener: s,
      type: a,
      useCapture: l
    }) => {
      n.addEventListener(a, s, l);
    });
  });
  const o = Array.from(t.childNodes);
  for (let r = 0; r < o.length; r++) {
    const i = o[r];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = Ie(i);
      e.push(...a), n.appendChild(s);
    } else i.nodeType === 3 && n.appendChild(i.cloneNode());
  }
  return {
    clonedElement: n,
    portals: e
  };
}
function In(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const at = Rt(({
  slot: t,
  clone: e,
  className: n,
  style: o,
  observeAttributes: r
}, i) => {
  const s = Lt(), [a, l] = At([]), {
    forceClone: c
  } = Xt(), d = c ? !0 : e;
  return Dt(() => {
    var S;
    if (!s.current || !t)
      return;
    let f = t;
    function u() {
      let p = f;
      if (f.tagName.toLowerCase() === "svelte-slot" && f.children.length === 1 && f.children[0] && (p = f.children[0], p.tagName.toLowerCase() === "react-portal-target" && p.children[0] && (p = p.children[0])), In(i, p), n && p.classList.add(...n.split(" ")), o) {
        const y = Pn(o);
        Object.keys(y).forEach((v) => {
          p.style[v] = y[v];
        });
      }
    }
    let g = null, b = null;
    if (d && window.MutationObserver) {
      let p = function() {
        var m, T, h;
        (m = s.current) != null && m.contains(f) && ((T = s.current) == null || T.removeChild(f));
        const {
          portals: v,
          clonedElement: P
        } = Ie(t);
        f = P, l(v), f.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          u();
        }, 50), (h = s.current) == null || h.appendChild(f);
      };
      p();
      const y = ar(() => {
        p(), g == null || g.disconnect(), g == null || g.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      g = new window.MutationObserver(y), g.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      f.style.display = "contents", u(), (S = s.current) == null || S.appendChild(f);
    return () => {
      var p, y;
      f.style.display = "", (p = s.current) != null && p.contains(f) && ((y = s.current) == null || y.removeChild(f)), g == null || g.disconnect();
    };
  }, [t, d, n, o, i, r, c]), _.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), kn = ({
  children: t,
  ...e
}) => /* @__PURE__ */ H.jsx(H.Fragment, {
  children: t(e)
});
function jn(t) {
  return _.createElement(kn, {
    children: t
  });
}
function _t(t, e, n) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((r, i) => {
      var c, d;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const s = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((c = r.props) == null ? void 0 : c.key) ?? (n ? `${n}-${i}` : `${i}`)
      }) : {
        ...r.props,
        key: ((d = r.props) == null ? void 0 : d.key) ?? (n ? `${n}-${i}` : `${i}`)
      };
      let a = s;
      Object.keys(r.slots).forEach((f) => {
        if (!r.slots[f] || !(r.slots[f] instanceof Element) && !r.slots[f].el)
          return;
        const u = f.split(".");
        u.forEach((v, P) => {
          a[v] || (a[v] = {}), P !== u.length - 1 && (a = s[v]);
        });
        const g = r.slots[f];
        let b, S, p = (e == null ? void 0 : e.clone) ?? !1, y = e == null ? void 0 : e.forceClone;
        g instanceof Element ? b = g : (b = g.el, S = g.callback, p = g.clone ?? p, y = g.forceClone ?? y), y = y ?? !!S, a[u[u.length - 1]] = b ? S ? (...v) => (S(u[u.length - 1], v), /* @__PURE__ */ H.jsx(ze, {
          ...r.ctx,
          params: v,
          forceClone: y,
          children: /* @__PURE__ */ H.jsx(at, {
            slot: b,
            clone: p
          })
        })) : jn((v) => /* @__PURE__ */ H.jsx(ze, {
          ...r.ctx,
          forceClone: y,
          children: /* @__PURE__ */ H.jsx(at, {
            ...v,
            slot: b,
            clone: p
          })
        })) : a[u[u.length - 1]], a = s;
      });
      const l = (e == null ? void 0 : e.children) || "children";
      return r[l] ? s[l] = _t(r[l], e, `${i}`) : e != null && e.children && (s[l] = void 0, Reflect.deleteProperty(s, l)), s;
    });
}
const {
  useItems: Rn,
  withItemsContextProvider: Ln,
  ItemHandler: Hn
} = Ft("antdx-actions-items"), Bn = Rr(Ln(["default", "items"], ({
  children: t,
  items: e,
  className: n,
  ...o
}) => {
  const {
    items: r
  } = Rn(), i = r.items.length > 0 ? r.items : r.default;
  return /* @__PURE__ */ H.jsxs(H.Fragment, {
    children: [/* @__PURE__ */ H.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ H.jsx(On, {
      ...o,
      rootClassName: Z(n, o.rootClassName),
      items: Ht(() => e || _t(i, {
        clone: !0
      }) || [], [e, i])
    })]
  });
}));
export {
  Bn as Actions,
  Bn as default
};
