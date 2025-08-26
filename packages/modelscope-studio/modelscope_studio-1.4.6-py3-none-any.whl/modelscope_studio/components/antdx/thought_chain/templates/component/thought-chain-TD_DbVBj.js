import { i as tr, a as ht, r as nr, Z as Ae, g as rr, c as U } from "./Index-5vB-UqN7.js";
const M = window.ms_globals.React, x = window.ms_globals.React, qn = window.ms_globals.React.isValidElement, Qn = window.ms_globals.React.version, ee = window.ms_globals.React.useRef, Yn = window.ms_globals.React.useLayoutEffect, pe = window.ms_globals.React.useEffect, Zn = window.ms_globals.React.forwardRef, Jn = window.ms_globals.React.useState, er = window.ms_globals.React.useMemo, It = window.ms_globals.ReactDOM, mt = window.ms_globals.ReactDOM.createPortal, or = window.ms_globals.internalContext.useContextPropsContext, $t = window.ms_globals.internalContext.ContextPropsProvider, ir = window.ms_globals.createItemsContext.createItemsContext, sr = window.ms_globals.antd.ConfigProvider, pt = window.ms_globals.antd.theme, ar = window.ms_globals.antd.Avatar, jt = window.ms_globals.antd.Typography, je = window.ms_globals.antdCssinjs.unit, et = window.ms_globals.antdCssinjs.token2CSSVar, Dt = window.ms_globals.antdCssinjs.useStyleRegister, cr = window.ms_globals.antdCssinjs.useCSSVarRegister, lr = window.ms_globals.antdCssinjs.createTheme, ur = window.ms_globals.antdCssinjs.useCacheToken, fr = window.ms_globals.antdIcons.LeftOutlined, dr = window.ms_globals.antdIcons.RightOutlined;
var mr = /\s/;
function hr(e) {
  for (var t = e.length; t-- && mr.test(e.charAt(t)); )
    ;
  return t;
}
var pr = /^\s+/;
function gr(e) {
  return e && e.slice(0, hr(e) + 1).replace(pr, "");
}
var zt = NaN, vr = /^[-+]0x[0-9a-f]+$/i, yr = /^0b[01]+$/i, br = /^0o[0-7]+$/i, Sr = parseInt;
function kt(e) {
  if (typeof e == "number")
    return e;
  if (tr(e))
    return zt;
  if (ht(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = ht(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = gr(e);
  var r = yr.test(e);
  return r || br.test(e) ? Sr(e.slice(2), r ? 2 : 8) : vr.test(e) ? zt : +e;
}
var tt = function() {
  return nr.Date.now();
}, xr = "Expected a function", Cr = Math.max, Er = Math.min;
function _r(e, t, r) {
  var o, n, i, s, a, c, l = 0, d = !1, u = !1, f = !0;
  if (typeof e != "function")
    throw new TypeError(xr);
  t = kt(t) || 0, ht(r) && (d = !!r.leading, u = "maxWait" in r, i = u ? Cr(kt(r.maxWait) || 0, t) : i, f = "trailing" in r ? !!r.trailing : f);
  function m(p) {
    var P = o, T = n;
    return o = n = void 0, l = p, s = e.apply(T, P), s;
  }
  function v(p) {
    return l = p, a = setTimeout(S, t), d ? m(p) : s;
  }
  function g(p) {
    var P = p - c, T = p - l, R = t - P;
    return u ? Er(R, i - T) : R;
  }
  function h(p) {
    var P = p - c, T = p - l;
    return c === void 0 || P >= t || P < 0 || u && T >= i;
  }
  function S() {
    var p = tt();
    if (h(p))
      return y(p);
    a = setTimeout(S, g(p));
  }
  function y(p) {
    return a = void 0, f && o ? m(p) : (o = n = void 0, s);
  }
  function _() {
    a !== void 0 && clearTimeout(a), l = 0, o = c = n = a = void 0;
  }
  function b() {
    return a === void 0 ? s : y(tt());
  }
  function w() {
    var p = tt(), P = h(p);
    if (o = arguments, n = this, c = p, P) {
      if (a === void 0)
        return v(c);
      if (u)
        return clearTimeout(a), a = setTimeout(S, t), m(c);
    }
    return a === void 0 && (a = setTimeout(S, t)), s;
  }
  return w.cancel = _, w.flush = b, w;
}
var gn = {
  exports: {}
}, ze = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var wr = x, Tr = Symbol.for("react.element"), Pr = Symbol.for("react.fragment"), Mr = Object.prototype.hasOwnProperty, Or = wr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Rr = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function vn(e, t, r) {
  var o, n = {}, i = null, s = null;
  r !== void 0 && (i = "" + r), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (o in t) Mr.call(t, o) && !Rr.hasOwnProperty(o) && (n[o] = t[o]);
  if (e && e.defaultProps) for (o in t = e.defaultProps, t) n[o] === void 0 && (n[o] = t[o]);
  return {
    $$typeof: Tr,
    type: e,
    key: i,
    ref: s,
    props: n,
    _owner: Or.current
  };
}
ze.Fragment = Pr;
ze.jsx = vn;
ze.jsxs = vn;
gn.exports = ze;
var q = gn.exports;
const {
  SvelteComponent: Lr,
  assign: Ft,
  binding_callbacks: Nt,
  check_outros: Ar,
  children: yn,
  claim_element: bn,
  claim_space: Ir,
  component_subscribe: Ht,
  compute_slots: $r,
  create_slot: jr,
  detach: ae,
  element: Sn,
  empty: Vt,
  exclude_internal_props: Bt,
  get_all_dirty_from_scope: Dr,
  get_slot_changes: zr,
  group_outros: kr,
  init: Fr,
  insert_hydration: Ie,
  safe_not_equal: Nr,
  set_custom_element_data: xn,
  space: Hr,
  transition_in: $e,
  transition_out: gt,
  update_slot_base: Vr
} = window.__gradio__svelte__internal, {
  beforeUpdate: Br,
  getContext: Gr,
  onDestroy: Ur,
  setContext: Xr
} = window.__gradio__svelte__internal;
function Gt(e) {
  let t, r;
  const o = (
    /*#slots*/
    e[7].default
  ), n = jr(
    o,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = Sn("svelte-slot"), n && n.c(), this.h();
    },
    l(i) {
      t = bn(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = yn(t);
      n && n.l(s), s.forEach(ae), this.h();
    },
    h() {
      xn(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      Ie(i, t, s), n && n.m(t, null), e[9](t), r = !0;
    },
    p(i, s) {
      n && n.p && (!r || s & /*$$scope*/
      64) && Vr(
        n,
        o,
        i,
        /*$$scope*/
        i[6],
        r ? zr(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : Dr(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      r || ($e(n, i), r = !0);
    },
    o(i) {
      gt(n, i), r = !1;
    },
    d(i) {
      i && ae(t), n && n.d(i), e[9](null);
    }
  };
}
function Wr(e) {
  let t, r, o, n, i = (
    /*$$slots*/
    e[4].default && Gt(e)
  );
  return {
    c() {
      t = Sn("react-portal-target"), r = Hr(), i && i.c(), o = Vt(), this.h();
    },
    l(s) {
      t = bn(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), yn(t).forEach(ae), r = Ir(s), i && i.l(s), o = Vt(), this.h();
    },
    h() {
      xn(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      Ie(s, t, a), e[8](t), Ie(s, r, a), i && i.m(s, a), Ie(s, o, a), n = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && $e(i, 1)) : (i = Gt(s), i.c(), $e(i, 1), i.m(o.parentNode, o)) : i && (kr(), gt(i, 1, 1, () => {
        i = null;
      }), Ar());
    },
    i(s) {
      n || ($e(i), n = !0);
    },
    o(s) {
      gt(i), n = !1;
    },
    d(s) {
      s && (ae(t), ae(r), ae(o)), e[8](null), i && i.d(s);
    }
  };
}
function Ut(e) {
  const {
    svelteInit: t,
    ...r
  } = e;
  return r;
}
function Kr(e, t, r) {
  let o, n, {
    $$slots: i = {},
    $$scope: s
  } = t;
  const a = $r(i);
  let {
    svelteInit: c
  } = t;
  const l = Ae(Ut(t)), d = Ae();
  Ht(e, d, (b) => r(0, o = b));
  const u = Ae();
  Ht(e, u, (b) => r(1, n = b));
  const f = [], m = Gr("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: g,
    subSlotIndex: h
  } = rr() || {}, S = c({
    parent: m,
    props: l,
    target: d,
    slot: u,
    slotKey: v,
    slotIndex: g,
    subSlotIndex: h,
    onDestroy(b) {
      f.push(b);
    }
  });
  Xr("$$ms-gr-react-wrapper", S), Br(() => {
    l.set(Ut(t));
  }), Ur(() => {
    f.forEach((b) => b());
  });
  function y(b) {
    Nt[b ? "unshift" : "push"](() => {
      o = b, d.set(o);
    });
  }
  function _(b) {
    Nt[b ? "unshift" : "push"](() => {
      n = b, u.set(n);
    });
  }
  return e.$$set = (b) => {
    r(17, t = Ft(Ft({}, t), Bt(b))), "svelteInit" in b && r(5, c = b.svelteInit), "$$scope" in b && r(6, s = b.$$scope);
  }, t = Bt(t), [o, n, d, u, a, c, s, i, y, _];
}
class qr extends Lr {
  constructor(t) {
    super(), Fr(this, t, Kr, Wr, Nr, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: zi
} = window.__gradio__svelte__internal, Xt = window.ms_globals.rerender, nt = window.ms_globals.tree;
function Qr(e, t = {}) {
  function r(o) {
    const n = Ae(), i = new qr({
      ...o,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: n,
            reactComponent: e,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, c = s.parent ?? nt;
          return c.nodes = [...c.nodes, a], Xt({
            createPortal: mt,
            node: nt
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((l) => l.svelteInstance !== n), Xt({
              createPortal: mt,
              node: nt
            });
          }), a;
        },
        ...o.props
      }
    });
    return n.set(i), i;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise.then(() => {
      o(r);
    });
  });
}
const Yr = "1.6.0";
function ue() {
  return ue = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var r = arguments[t];
      for (var o in r) ({}).hasOwnProperty.call(r, o) && (e[o] = r[o]);
    }
    return e;
  }, ue.apply(null, arguments);
}
function k(e) {
  "@babel/helpers - typeof";
  return k = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, k(e);
}
function Zr(e, t) {
  if (k(e) != "object" || !e) return e;
  var r = e[Symbol.toPrimitive];
  if (r !== void 0) {
    var o = r.call(e, t);
    if (k(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function Cn(e) {
  var t = Zr(e, "string");
  return k(t) == "symbol" ? t : t + "";
}
function E(e, t, r) {
  return (t = Cn(t)) in e ? Object.defineProperty(e, t, {
    value: r,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = r, e;
}
function Wt(e, t) {
  var r = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(e);
    t && (o = o.filter(function(n) {
      return Object.getOwnPropertyDescriptor(e, n).enumerable;
    })), r.push.apply(r, o);
  }
  return r;
}
function C(e) {
  for (var t = 1; t < arguments.length; t++) {
    var r = arguments[t] != null ? arguments[t] : {};
    t % 2 ? Wt(Object(r), !0).forEach(function(o) {
      E(e, o, r[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(r)) : Wt(Object(r)).forEach(function(o) {
      Object.defineProperty(e, o, Object.getOwnPropertyDescriptor(r, o));
    });
  }
  return e;
}
var Jr = `accept acceptCharset accessKey action allowFullScreen allowTransparency
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
    summary tabIndex target title type useMap value width wmode wrap`, eo = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, to = "".concat(Jr, " ").concat(eo).split(/[\s\n]+/), no = "aria-", ro = "data-";
function Kt(e, t) {
  return e.indexOf(t) === 0;
}
function En(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, r;
  t === !1 ? r = {
    aria: !0,
    data: !0,
    attr: !0
  } : t === !0 ? r = {
    aria: !0
  } : r = C({}, t);
  var o = {};
  return Object.keys(e).forEach(function(n) {
    // Aria
    (r.aria && (n === "role" || Kt(n, no)) || // Data
    r.data && Kt(n, ro) || // Attr
    r.attr && to.includes(n)) && (o[n] = e[n]);
  }), o;
}
const oo = /* @__PURE__ */ x.createContext({}), io = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, so = (e) => {
  const t = x.useContext(oo);
  return x.useMemo(() => ({
    ...io,
    ...t[e]
  }), [t[e]]);
}, ao = "ant";
function vt() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: r,
    iconPrefixCls: o,
    theme: n
  } = x.useContext(sr.ConfigContext);
  return {
    theme: n,
    getPrefixCls: e,
    direction: t,
    csp: r,
    iconPrefixCls: o
  };
}
function co(e) {
  if (Array.isArray(e)) return e;
}
function lo(e, t) {
  var r = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (r != null) {
    var o, n, i, s, a = [], c = !0, l = !1;
    try {
      if (i = (r = r.call(e)).next, t === 0) {
        if (Object(r) !== r) return;
        c = !1;
      } else for (; !(c = (o = i.call(r)).done) && (a.push(o.value), a.length !== t); c = !0) ;
    } catch (d) {
      l = !0, n = d;
    } finally {
      try {
        if (!c && r.return != null && (s = r.return(), Object(s) !== s)) return;
      } finally {
        if (l) throw n;
      }
    }
    return a;
  }
}
function qt(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var r = 0, o = Array(t); r < t; r++) o[r] = e[r];
  return o;
}
function uo(e, t) {
  if (e) {
    if (typeof e == "string") return qt(e, t);
    var r = {}.toString.call(e).slice(8, -1);
    return r === "Object" && e.constructor && (r = e.constructor.name), r === "Map" || r === "Set" ? Array.from(e) : r === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r) ? qt(e, t) : void 0;
  }
}
function fo() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function N(e, t) {
  return co(e) || lo(e, t) || uo(e, t) || fo();
}
function fe(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function Qt(e, t) {
  for (var r = 0; r < t.length; r++) {
    var o = t[r];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, Cn(o.key), o);
  }
}
function de(e, t, r) {
  return t && Qt(e.prototype, t), r && Qt(e, r), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function se(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function yt(e, t) {
  return yt = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(r, o) {
    return r.__proto__ = o, r;
  }, yt(e, t);
}
function ke(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && yt(e, t);
}
function De(e) {
  return De = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, De(e);
}
function _n() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (_n = function() {
    return !!e;
  })();
}
function mo(e, t) {
  if (t && (k(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return se(e);
}
function Fe(e) {
  var t = _n();
  return function() {
    var r, o = De(e);
    if (t) {
      var n = De(this).constructor;
      r = Reflect.construct(o, arguments, n);
    } else r = o.apply(this, arguments);
    return mo(this, r);
  };
}
var wn = /* @__PURE__ */ de(function e() {
  fe(this, e);
}), Tn = "CALC_UNIT", ho = new RegExp(Tn, "g");
function rt(e) {
  return typeof e == "number" ? "".concat(e).concat(Tn) : e;
}
var po = /* @__PURE__ */ function(e) {
  ke(r, e);
  var t = Fe(r);
  function r(o, n) {
    var i;
    fe(this, r), i = t.call(this), E(se(i), "result", ""), E(se(i), "unitlessCssVar", void 0), E(se(i), "lowPriority", void 0);
    var s = k(o);
    return i.unitlessCssVar = n, o instanceof r ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = rt(o) : s === "string" && (i.result = o), i;
  }
  return de(r, [{
    key: "add",
    value: function(n) {
      return n instanceof r ? this.result = "".concat(this.result, " + ").concat(n.getResult()) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " + ").concat(rt(n))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(n) {
      return n instanceof r ? this.result = "".concat(this.result, " - ").concat(n.getResult()) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " - ").concat(rt(n))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(n) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), n instanceof r ? this.result = "".concat(this.result, " * ").concat(n.getResult(!0)) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " * ").concat(n)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(n) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), n instanceof r ? this.result = "".concat(this.result, " / ").concat(n.getResult(!0)) : (typeof n == "number" || typeof n == "string") && (this.result = "".concat(this.result, " / ").concat(n)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(n) {
      return this.lowPriority || n ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(n) {
      var i = this, s = n || {}, a = s.unit, c = !0;
      return typeof a == "boolean" ? c = a : Array.from(this.unitlessCssVar).some(function(l) {
        return i.result.includes(l);
      }) && (c = !1), this.result = this.result.replace(ho, c ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), r;
}(wn), go = /* @__PURE__ */ function(e) {
  ke(r, e);
  var t = Fe(r);
  function r(o) {
    var n;
    return fe(this, r), n = t.call(this), E(se(n), "result", 0), o instanceof r ? n.result = o.result : typeof o == "number" && (n.result = o), n;
  }
  return de(r, [{
    key: "add",
    value: function(n) {
      return n instanceof r ? this.result += n.result : typeof n == "number" && (this.result += n), this;
    }
  }, {
    key: "sub",
    value: function(n) {
      return n instanceof r ? this.result -= n.result : typeof n == "number" && (this.result -= n), this;
    }
  }, {
    key: "mul",
    value: function(n) {
      return n instanceof r ? this.result *= n.result : typeof n == "number" && (this.result *= n), this;
    }
  }, {
    key: "div",
    value: function(n) {
      return n instanceof r ? this.result /= n.result : typeof n == "number" && (this.result /= n), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), r;
}(wn), vo = function(t, r) {
  var o = t === "css" ? po : go;
  return function(n) {
    return new o(n, r);
  };
}, Yt = function(t, r) {
  return "".concat([r, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function ge(e) {
  var t = M.useRef();
  t.current = e;
  var r = M.useCallback(function() {
    for (var o, n = arguments.length, i = new Array(n), s = 0; s < n; s++)
      i[s] = arguments[s];
    return (o = t.current) === null || o === void 0 ? void 0 : o.call.apply(o, [t].concat(i));
  }, []);
  return r;
}
function Ne() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var Zt = Ne() ? M.useLayoutEffect : M.useEffect, yo = function(t, r) {
  var o = M.useRef(!0);
  Zt(function() {
    return t(o.current);
  }, r), Zt(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, Jt = function(t, r) {
  yo(function(o) {
    if (!o)
      return t();
  }, r);
};
function ve(e) {
  var t = M.useRef(!1), r = M.useState(e), o = N(r, 2), n = o[0], i = o[1];
  M.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function s(a, c) {
    c && t.current || i(a);
  }
  return [n, s];
}
function ot(e) {
  return e !== void 0;
}
function bo(e, t) {
  var r = t || {}, o = r.defaultValue, n = r.value, i = r.onChange, s = r.postState, a = ve(function() {
    return ot(n) ? n : ot(o) ? typeof o == "function" ? o() : o : typeof e == "function" ? e() : e;
  }), c = N(a, 2), l = c[0], d = c[1], u = n !== void 0 ? n : l, f = s ? s(u) : u, m = ge(i), v = ve([u]), g = N(v, 2), h = g[0], S = g[1];
  Jt(function() {
    var _ = h[0];
    l !== _ && m(l, _);
  }, [h]), Jt(function() {
    ot(n) || d(n);
  }, [n]);
  var y = ge(function(_, b) {
    d(_, b), S([u], b);
  });
  return [f, y];
}
var Pn = {
  exports: {}
}, O = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Tt = Symbol.for("react.element"), Pt = Symbol.for("react.portal"), He = Symbol.for("react.fragment"), Ve = Symbol.for("react.strict_mode"), Be = Symbol.for("react.profiler"), Ge = Symbol.for("react.provider"), Ue = Symbol.for("react.context"), So = Symbol.for("react.server_context"), Xe = Symbol.for("react.forward_ref"), We = Symbol.for("react.suspense"), Ke = Symbol.for("react.suspense_list"), qe = Symbol.for("react.memo"), Qe = Symbol.for("react.lazy"), xo = Symbol.for("react.offscreen"), Mn;
Mn = Symbol.for("react.module.reference");
function X(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case Tt:
        switch (e = e.type, e) {
          case He:
          case Be:
          case Ve:
          case We:
          case Ke:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case So:
              case Ue:
              case Xe:
              case Qe:
              case qe:
              case Ge:
                return e;
              default:
                return t;
            }
        }
      case Pt:
        return t;
    }
  }
}
O.ContextConsumer = Ue;
O.ContextProvider = Ge;
O.Element = Tt;
O.ForwardRef = Xe;
O.Fragment = He;
O.Lazy = Qe;
O.Memo = qe;
O.Portal = Pt;
O.Profiler = Be;
O.StrictMode = Ve;
O.Suspense = We;
O.SuspenseList = Ke;
O.isAsyncMode = function() {
  return !1;
};
O.isConcurrentMode = function() {
  return !1;
};
O.isContextConsumer = function(e) {
  return X(e) === Ue;
};
O.isContextProvider = function(e) {
  return X(e) === Ge;
};
O.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === Tt;
};
O.isForwardRef = function(e) {
  return X(e) === Xe;
};
O.isFragment = function(e) {
  return X(e) === He;
};
O.isLazy = function(e) {
  return X(e) === Qe;
};
O.isMemo = function(e) {
  return X(e) === qe;
};
O.isPortal = function(e) {
  return X(e) === Pt;
};
O.isProfiler = function(e) {
  return X(e) === Be;
};
O.isStrictMode = function(e) {
  return X(e) === Ve;
};
O.isSuspense = function(e) {
  return X(e) === We;
};
O.isSuspenseList = function(e) {
  return X(e) === Ke;
};
O.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === He || e === Be || e === Ve || e === We || e === Ke || e === xo || typeof e == "object" && e !== null && (e.$$typeof === Qe || e.$$typeof === qe || e.$$typeof === Ge || e.$$typeof === Ue || e.$$typeof === Xe || e.$$typeof === Mn || e.getModuleId !== void 0);
};
O.typeOf = X;
Pn.exports = O;
var it = Pn.exports, Co = Symbol.for("react.element"), Eo = Symbol.for("react.transitional.element"), _o = Symbol.for("react.fragment");
function wo(e) {
  return (
    // Base object type
    e && k(e) === "object" && // React Element type
    (e.$$typeof === Co || e.$$typeof === Eo) && // React Fragment type
    e.type === _o
  );
}
var To = Number(Qn.split(".")[0]), Po = function(t, r) {
  typeof t == "function" ? t(r) : k(t) === "object" && t && "current" in t && (t.current = r);
}, Mo = function(t) {
  var r, o;
  if (!t)
    return !1;
  if (On(t) && To >= 19)
    return !0;
  var n = it.isMemo(t) ? t.type.type : t.type;
  return !(typeof n == "function" && !((r = n.prototype) !== null && r !== void 0 && r.render) && n.$$typeof !== it.ForwardRef || typeof t == "function" && !((o = t.prototype) !== null && o !== void 0 && o.render) && t.$$typeof !== it.ForwardRef);
};
function On(e) {
  return /* @__PURE__ */ qn(e) && !wo(e);
}
var Oo = function(t) {
  if (t && On(t)) {
    var r = t;
    return r.props.propertyIsEnumerable("ref") ? r.props.ref : r.ref;
  }
  return null;
};
function en(e, t, r, o) {
  var n = C({}, t[e]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var c = N(a, 2), l = c[0], d = c[1];
      if (n != null && n[l] || n != null && n[d]) {
        var u;
        (u = n[d]) !== null && u !== void 0 || (n[d] = n == null ? void 0 : n[l]);
      }
    });
  }
  var s = C(C({}, r), n);
  return Object.keys(s).forEach(function(a) {
    s[a] === t[a] && delete s[a];
  }), s;
}
var Rn = typeof CSSINJS_STATISTIC < "u", bt = !0;
function Mt() {
  for (var e = arguments.length, t = new Array(e), r = 0; r < e; r++)
    t[r] = arguments[r];
  if (!Rn)
    return Object.assign.apply(Object, [{}].concat(t));
  bt = !1;
  var o = {};
  return t.forEach(function(n) {
    if (k(n) === "object") {
      var i = Object.keys(n);
      i.forEach(function(s) {
        Object.defineProperty(o, s, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return n[s];
          }
        });
      });
    }
  }), bt = !0, o;
}
var tn = {};
function Ro() {
}
var Lo = function(t) {
  var r, o = t, n = Ro;
  return Rn && typeof Proxy < "u" && (r = /* @__PURE__ */ new Set(), o = new Proxy(t, {
    get: function(s, a) {
      if (bt) {
        var c;
        (c = r) === null || c === void 0 || c.add(a);
      }
      return s[a];
    }
  }), n = function(s, a) {
    var c;
    tn[s] = {
      global: Array.from(r),
      component: C(C({}, (c = tn[s]) === null || c === void 0 ? void 0 : c.component), a)
    };
  }), {
    token: o,
    keys: r,
    flush: n
  };
};
function nn(e, t, r) {
  if (typeof r == "function") {
    var o;
    return r(Mt(t, (o = t[e]) !== null && o !== void 0 ? o : {}));
  }
  return r ?? {};
}
function Ao(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var r = arguments.length, o = new Array(r), n = 0; n < r; n++)
        o[n] = arguments[n];
      return "max(".concat(o.map(function(i) {
        return je(i);
      }).join(","), ")");
    },
    min: function() {
      for (var r = arguments.length, o = new Array(r), n = 0; n < r; n++)
        o[n] = arguments[n];
      return "min(".concat(o.map(function(i) {
        return je(i);
      }).join(","), ")");
    }
  };
}
var Io = 1e3 * 60 * 10, $o = /* @__PURE__ */ function() {
  function e() {
    fe(this, e), E(this, "map", /* @__PURE__ */ new Map()), E(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), E(this, "nextID", 0), E(this, "lastAccessBeat", /* @__PURE__ */ new Map()), E(this, "accessBeat", 0);
  }
  return de(e, [{
    key: "set",
    value: function(r, o) {
      this.clear();
      var n = this.getCompositeKey(r);
      this.map.set(n, o), this.lastAccessBeat.set(n, Date.now());
    }
  }, {
    key: "get",
    value: function(r) {
      var o = this.getCompositeKey(r), n = this.map.get(o);
      return this.lastAccessBeat.set(o, Date.now()), this.accessBeat += 1, n;
    }
  }, {
    key: "getCompositeKey",
    value: function(r) {
      var o = this, n = r.map(function(i) {
        return i && k(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(k(i), "_").concat(i);
      });
      return n.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(r) {
      if (this.objectIDMap.has(r))
        return this.objectIDMap.get(r);
      var o = this.nextID;
      return this.objectIDMap.set(r, o), this.nextID += 1, o;
    }
  }, {
    key: "clear",
    value: function() {
      var r = this;
      if (this.accessBeat > 1e4) {
        var o = Date.now();
        this.lastAccessBeat.forEach(function(n, i) {
          o - n > Io && (r.map.delete(i), r.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), rn = new $o();
function jo(e, t) {
  return x.useMemo(function() {
    var r = rn.get(t);
    if (r)
      return r;
    var o = e();
    return rn.set(t, o), o;
  }, t);
}
var Do = function() {
  return {};
};
function zo(e) {
  var t = e.useCSP, r = t === void 0 ? Do : t, o = e.useToken, n = e.usePrefix, i = e.getResetStyles, s = e.getCommonStyle, a = e.getCompUnitless;
  function c(f, m, v, g) {
    var h = Array.isArray(f) ? f[0] : f;
    function S(T) {
      return "".concat(String(h)).concat(T.slice(0, 1).toUpperCase()).concat(T.slice(1));
    }
    var y = (g == null ? void 0 : g.unitless) || {}, _ = typeof a == "function" ? a(f) : {}, b = C(C({}, _), {}, E({}, S("zIndexPopup"), !0));
    Object.keys(y).forEach(function(T) {
      b[S(T)] = y[T];
    });
    var w = C(C({}, g), {}, {
      unitless: b,
      prefixToken: S
    }), p = d(f, m, v, w), P = l(h, v, w);
    return function(T) {
      var R = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : T, L = p(T, R), A = N(L, 2), I = A[1], $ = P(R), j = N($, 2), D = j[0], V = j[1];
      return [D, I, V];
    };
  }
  function l(f, m, v) {
    var g = v.unitless, h = v.injectStyle, S = h === void 0 ? !0 : h, y = v.prefixToken, _ = v.ignore, b = function(P) {
      var T = P.rootCls, R = P.cssVar, L = R === void 0 ? {} : R, A = o(), I = A.realToken;
      return cr({
        path: [f],
        prefix: L.prefix,
        key: L.key,
        unitless: g,
        ignore: _,
        token: I,
        scope: T
      }, function() {
        var $ = nn(f, I, m), j = en(f, I, $, {
          deprecatedTokens: v == null ? void 0 : v.deprecatedTokens
        });
        return Object.keys($).forEach(function(D) {
          j[y(D)] = j[D], delete j[D];
        }), j;
      }), null;
    }, w = function(P) {
      var T = o(), R = T.cssVar;
      return [function(L) {
        return S && R ? /* @__PURE__ */ x.createElement(x.Fragment, null, /* @__PURE__ */ x.createElement(b, {
          rootCls: P,
          cssVar: R,
          component: f
        }), L) : L;
      }, R == null ? void 0 : R.key];
    };
    return w;
  }
  function d(f, m, v) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = Array.isArray(f) ? f : [f, f], S = N(h, 1), y = S[0], _ = h.join("-"), b = e.layer || {
      name: "antd"
    };
    return function(w) {
      var p = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : w, P = o(), T = P.theme, R = P.realToken, L = P.hashId, A = P.token, I = P.cssVar, $ = n(), j = $.rootPrefixCls, D = $.iconPrefixCls, V = r(), te = I ? "css" : "js", Z = jo(function() {
        var G = /* @__PURE__ */ new Set();
        return I && Object.keys(g.unitless || {}).forEach(function(re) {
          G.add(et(re, I.prefix)), G.add(et(re, Yt(y, I.prefix)));
        }), vo(te, G);
      }, [te, y, I == null ? void 0 : I.prefix]), ye = Ao(te), be = ye.max, B = ye.min, ne = {
        theme: T,
        token: A,
        hashId: L,
        nonce: function() {
          return V.nonce;
        },
        clientOnly: g.clientOnly,
        layer: b,
        // antd is always at top of styles
        order: g.order || -999
      };
      typeof i == "function" && Dt(C(C({}, ne), {}, {
        clientOnly: !1,
        path: ["Shared", j]
      }), function() {
        return i(A, {
          prefix: {
            rootPrefixCls: j,
            iconPrefixCls: D
          },
          csp: V
        });
      });
      var me = Dt(C(C({}, ne), {}, {
        path: [_, w, D]
      }), function() {
        if (g.injectStyle === !1)
          return [];
        var G = Lo(A), re = G.token, Se = G.flush, Q = nn(y, R, v), Ye = ".".concat(w), xe = en(y, R, Q, {
          deprecatedTokens: g.deprecatedTokens
        });
        I && Q && k(Q) === "object" && Object.keys(Q).forEach(function(_e) {
          Q[_e] = "var(".concat(et(_e, Yt(y, I.prefix)), ")");
        });
        var Ce = Mt(re, {
          componentCls: Ye,
          prefixCls: w,
          iconCls: ".".concat(D),
          antCls: ".".concat(j),
          calc: Z,
          // @ts-ignore
          max: be,
          // @ts-ignore
          min: B
        }, I ? Q : xe), Ee = m(Ce, {
          hashId: L,
          prefixCls: w,
          rootPrefixCls: j,
          iconPrefixCls: D
        });
        Se(y, xe);
        var oe = typeof s == "function" ? s(Ce, w, p, g.resetFont) : null;
        return [g.resetStyle === !1 ? null : oe, Ee];
      });
      return [me, L];
    };
  }
  function u(f, m, v) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = d(f, m, v, C({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, g)), S = function(_) {
      var b = _.prefixCls, w = _.rootCls, p = w === void 0 ? b : w;
      return h(b, p), null;
    };
    return S;
  }
  return {
    genStyleHooks: c,
    genSubStyleComponent: u,
    genComponentStyleHook: d
  };
}
const ko = {
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
}, Fo = Object.assign(Object.assign({}, ko), {
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
}), z = Math.round;
function st(e, t) {
  const r = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = r.map((n) => parseFloat(n));
  for (let n = 0; n < 3; n += 1)
    o[n] = t(o[n] || 0, r[n] || "", n);
  return r[3] ? o[3] = r[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const on = (e, t, r) => r === 0 ? e : e / 100;
function he(e, t) {
  const r = t || 255;
  return e > r ? r : e < 0 ? 0 : e;
}
class Y {
  constructor(t) {
    E(this, "isValid", !0), E(this, "r", 0), E(this, "g", 0), E(this, "b", 0), E(this, "a", 1), E(this, "_h", void 0), E(this, "_s", void 0), E(this, "_l", void 0), E(this, "_v", void 0), E(this, "_max", void 0), E(this, "_min", void 0), E(this, "_brightness", void 0);
    function r(o) {
      return o[0] in t && o[1] in t && o[2] in t;
    }
    if (t) if (typeof t == "string") {
      let n = function(i) {
        return o.startsWith(i);
      };
      const o = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : n("rgb") ? this.fromRgbString(o) : n("hsl") ? this.fromHslString(o) : (n("hsv") || n("hsb")) && this.fromHsvString(o);
    } else if (t instanceof Y)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (r("rgb"))
      this.r = he(t.r), this.g = he(t.g), this.b = he(t.b), this.a = typeof t.a == "number" ? he(t.a, 1) : 1;
    else if (r("hsl"))
      this.fromHsl(t);
    else if (r("hsv"))
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
    const r = this.toHsv();
    return r.h = t, this._c(r);
  }
  // ======================= Getter =======================
  /**
   * Returns the perceived luminance of a color, from 0-1.
   * @see http://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
   */
  getLuminance() {
    function t(i) {
      const s = i / 255;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    }
    const r = t(this.r), o = t(this.g), n = t(this.b);
    return 0.2126 * r + 0.7152 * o + 0.0722 * n;
  }
  getHue() {
    if (typeof this._h > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._h = 0 : this._h = z(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
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
    const r = this.getHue(), o = this.getSaturation();
    let n = this.getLightness() - t / 100;
    return n < 0 && (n = 0), this._c({
      h: r,
      s: o,
      l: n,
      a: this.a
    });
  }
  lighten(t = 10) {
    const r = this.getHue(), o = this.getSaturation();
    let n = this.getLightness() + t / 100;
    return n > 1 && (n = 1), this._c({
      h: r,
      s: o,
      l: n,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(t, r = 50) {
    const o = this._c(t), n = r / 100, i = (a) => (o[a] - this[a]) * n + this[a], s = {
      r: z(i("r")),
      g: z(i("g")),
      b: z(i("b")),
      a: z(i("a") * 100) / 100
    };
    return this._c(s);
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
    const r = this._c(t), o = this.a + r.a * (1 - this.a), n = (i) => z((this[i] * this.a + r[i] * r.a * (1 - this.a)) / o);
    return this._c({
      r: n("r"),
      g: n("g"),
      b: n("b"),
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
  equals(t) {
    return this.r === t.r && this.g === t.g && this.b === t.b && this.a === t.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let t = "#";
    const r = (this.r || 0).toString(16);
    t += r.length === 2 ? r : "0" + r;
    const o = (this.g || 0).toString(16);
    t += o.length === 2 ? o : "0" + o;
    const n = (this.b || 0).toString(16);
    if (t += n.length === 2 ? n : "0" + n, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const i = z(this.a * 255).toString(16);
      t += i.length === 2 ? i : "0" + i;
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
    const t = this.getHue(), r = z(this.getSaturation() * 100), o = z(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${t},${r}%,${o}%,${this.a})` : `hsl(${t},${r}%,${o}%)`;
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
  _sc(t, r, o) {
    const n = this.clone();
    return n[t] = he(r, o), n;
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
    const r = t.replace("#", "");
    function o(n, i) {
      return parseInt(r[n] + r[i || n], 16);
    }
    r.length < 6 ? (this.r = o(0), this.g = o(1), this.b = o(2), this.a = r[3] ? o(3) / 255 : 1) : (this.r = o(0, 1), this.g = o(2, 3), this.b = o(4, 5), this.a = r[6] ? o(6, 7) / 255 : 1);
  }
  fromHsl({
    h: t,
    s: r,
    l: o,
    a: n
  }) {
    if (this._h = t % 360, this._s = r, this._l = o, this.a = typeof n == "number" ? n : 1, r <= 0) {
      const f = z(o * 255);
      this.r = f, this.g = f, this.b = f;
    }
    let i = 0, s = 0, a = 0;
    const c = t / 60, l = (1 - Math.abs(2 * o - 1)) * r, d = l * (1 - Math.abs(c % 2 - 1));
    c >= 0 && c < 1 ? (i = l, s = d) : c >= 1 && c < 2 ? (i = d, s = l) : c >= 2 && c < 3 ? (s = l, a = d) : c >= 3 && c < 4 ? (s = d, a = l) : c >= 4 && c < 5 ? (i = d, a = l) : c >= 5 && c < 6 && (i = l, a = d);
    const u = o - l / 2;
    this.r = z((i + u) * 255), this.g = z((s + u) * 255), this.b = z((a + u) * 255);
  }
  fromHsv({
    h: t,
    s: r,
    v: o,
    a: n
  }) {
    this._h = t % 360, this._s = r, this._v = o, this.a = typeof n == "number" ? n : 1;
    const i = z(o * 255);
    if (this.r = i, this.g = i, this.b = i, r <= 0)
      return;
    const s = t / 60, a = Math.floor(s), c = s - a, l = z(o * (1 - r) * 255), d = z(o * (1 - r * c) * 255), u = z(o * (1 - r * (1 - c)) * 255);
    switch (a) {
      case 0:
        this.g = u, this.b = l;
        break;
      case 1:
        this.r = d, this.b = l;
        break;
      case 2:
        this.r = l, this.b = u;
        break;
      case 3:
        this.r = l, this.g = d;
        break;
      case 4:
        this.r = u, this.g = l;
        break;
      case 5:
      default:
        this.g = l, this.b = d;
        break;
    }
  }
  fromHsvString(t) {
    const r = st(t, on);
    this.fromHsv({
      h: r[0],
      s: r[1],
      v: r[2],
      a: r[3]
    });
  }
  fromHslString(t) {
    const r = st(t, on);
    this.fromHsl({
      h: r[0],
      s: r[1],
      l: r[2],
      a: r[3]
    });
  }
  fromRgbString(t) {
    const r = st(t, (o, n) => (
      // Convert percentage to number. e.g. 50% -> 128
      n.includes("%") ? z(o / 100 * 255) : o
    ));
    this.r = r[0], this.g = r[1], this.b = r[2], this.a = r[3];
  }
}
function at(e) {
  return e >= 0 && e <= 255;
}
function Pe(e, t) {
  const {
    r,
    g: o,
    b: n,
    a: i
  } = new Y(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: s,
    g: a,
    b: c
  } = new Y(t).toRgb();
  for (let l = 0.01; l <= 1; l += 0.01) {
    const d = Math.round((r - s * (1 - l)) / l), u = Math.round((o - a * (1 - l)) / l), f = Math.round((n - c * (1 - l)) / l);
    if (at(d) && at(u) && at(f))
      return new Y({
        r: d,
        g: u,
        b: f,
        a: Math.round(l * 100) / 100
      }).toRgbString();
  }
  return new Y({
    r,
    g: o,
    b: n,
    a: 1
  }).toRgbString();
}
var No = function(e, t) {
  var r = {};
  for (var o in e) Object.prototype.hasOwnProperty.call(e, o) && t.indexOf(o) < 0 && (r[o] = e[o]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var n = 0, o = Object.getOwnPropertySymbols(e); n < o.length; n++)
    t.indexOf(o[n]) < 0 && Object.prototype.propertyIsEnumerable.call(e, o[n]) && (r[o[n]] = e[o[n]]);
  return r;
};
function Ho(e) {
  const {
    override: t
  } = e, r = No(e, ["override"]), o = Object.assign({}, t);
  Object.keys(Fo).forEach((f) => {
    delete o[f];
  });
  const n = Object.assign(Object.assign({}, r), o), i = 480, s = 576, a = 768, c = 992, l = 1200, d = 1600;
  if (n.motion === !1) {
    const f = "0s";
    n.motionDurationFast = f, n.motionDurationMid = f, n.motionDurationSlow = f;
  }
  return Object.assign(Object.assign(Object.assign({}, n), {
    // ============== Background ============== //
    colorFillContent: n.colorFillSecondary,
    colorFillContentHover: n.colorFill,
    colorFillAlter: n.colorFillQuaternary,
    colorBgContainerDisabled: n.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: n.colorBgContainer,
    colorSplit: Pe(n.colorBorderSecondary, n.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: n.colorTextQuaternary,
    colorTextDisabled: n.colorTextQuaternary,
    colorTextHeading: n.colorText,
    colorTextLabel: n.colorTextSecondary,
    colorTextDescription: n.colorTextTertiary,
    colorTextLightSolid: n.colorWhite,
    colorHighlight: n.colorError,
    colorBgTextHover: n.colorFillSecondary,
    colorBgTextActive: n.colorFill,
    colorIcon: n.colorTextTertiary,
    colorIconHover: n.colorText,
    colorErrorOutline: Pe(n.colorErrorBg, n.colorBgContainer),
    colorWarningOutline: Pe(n.colorWarningBg, n.colorBgContainer),
    // Font
    fontSizeIcon: n.fontSizeSM,
    // Line
    lineWidthFocus: n.lineWidth * 3,
    // Control
    lineWidth: n.lineWidth,
    controlOutlineWidth: n.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: n.controlHeight / 2,
    controlItemBgHover: n.colorFillTertiary,
    controlItemBgActive: n.colorPrimaryBg,
    controlItemBgActiveHover: n.colorPrimaryBgHover,
    controlItemBgActiveDisabled: n.colorFill,
    controlTmpOutline: n.colorFillQuaternary,
    controlOutline: Pe(n.colorPrimaryBg, n.colorBgContainer),
    lineType: n.lineType,
    borderRadius: n.borderRadius,
    borderRadiusXS: n.borderRadiusXS,
    borderRadiusSM: n.borderRadiusSM,
    borderRadiusLG: n.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: n.sizeXXS,
    paddingXS: n.sizeXS,
    paddingSM: n.sizeSM,
    padding: n.size,
    paddingMD: n.sizeMD,
    paddingLG: n.sizeLG,
    paddingXL: n.sizeXL,
    paddingContentHorizontalLG: n.sizeLG,
    paddingContentVerticalLG: n.sizeMS,
    paddingContentHorizontal: n.sizeMS,
    paddingContentVertical: n.sizeSM,
    paddingContentHorizontalSM: n.size,
    paddingContentVerticalSM: n.sizeXS,
    marginXXS: n.sizeXXS,
    marginXS: n.sizeXS,
    marginSM: n.sizeSM,
    margin: n.size,
    marginMD: n.sizeMD,
    marginLG: n.sizeLG,
    marginXL: n.sizeXL,
    marginXXL: n.sizeXXL,
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
    screenMDMax: c - 1,
    screenLG: c,
    screenLGMin: c,
    screenLGMax: l - 1,
    screenXL: l,
    screenXLMin: l,
    screenXLMax: d - 1,
    screenXXL: d,
    screenXXLMin: d,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new Y("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new Y("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new Y("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const Vo = {
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
}, Bo = {
  motionBase: !0,
  motionUnit: !0
}, Go = lr(pt.defaultAlgorithm), Uo = {
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
}, Ln = (e, t, r) => {
  const o = r.getDerivativeToken(e), {
    override: n,
    ...i
  } = t;
  let s = {
    ...o,
    override: n
  };
  return s = Ho(s), i && Object.entries(i).forEach(([a, c]) => {
    const {
      theme: l,
      ...d
    } = c;
    let u = d;
    l && (u = Ln({
      ...s,
      ...d
    }, {
      override: d
    }, l)), s[a] = u;
  }), s;
};
function Xo() {
  const {
    token: e,
    hashed: t,
    theme: r = Go,
    override: o,
    cssVar: n
  } = x.useContext(pt._internalContext), [i, s, a] = ur(r, [pt.defaultSeed, e], {
    salt: `${Yr}-${t || ""}`,
    override: o,
    getComputedToken: Ln,
    cssVar: n && {
      prefix: n.prefix,
      key: n.key,
      unitless: Vo,
      ignore: Bo,
      preserve: Uo
    }
  });
  return [r, a, t ? s : "", i, n];
}
const {
  genStyleHooks: Wo
} = zo({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = vt();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, r, o, n] = Xo();
    return {
      theme: e,
      realToken: t,
      hashId: r,
      token: o,
      cssVar: n
    };
  },
  useCSP: () => {
    const {
      csp: e
    } = vt();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
});
function sn(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function Ko(e) {
  return e && k(e) === "object" && sn(e.nativeElement) ? e.nativeElement : sn(e) ? e : null;
}
function qo(e) {
  var t = Ko(e);
  if (t)
    return t;
  if (e instanceof x.Component) {
    var r;
    return (r = It.findDOMNode) === null || r === void 0 ? void 0 : r.call(It, e);
  }
  return null;
}
function Qo(e, t) {
  if (e == null) return {};
  var r = {};
  for (var o in e) if ({}.hasOwnProperty.call(e, o)) {
    if (t.indexOf(o) !== -1) continue;
    r[o] = e[o];
  }
  return r;
}
function an(e, t) {
  if (e == null) return {};
  var r, o, n = Qo(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (o = 0; o < i.length; o++) r = i[o], t.indexOf(r) === -1 && {}.propertyIsEnumerable.call(e, r) && (n[r] = e[r]);
  }
  return n;
}
var Yo = /* @__PURE__ */ M.createContext({}), Zo = /* @__PURE__ */ function(e) {
  ke(r, e);
  var t = Fe(r);
  function r() {
    return fe(this, r), t.apply(this, arguments);
  }
  return de(r, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), r;
}(M.Component);
function Jo(e) {
  var t = M.useReducer(function(a) {
    return a + 1;
  }, 0), r = N(t, 2), o = r[1], n = M.useRef(e), i = ge(function() {
    return n.current;
  }), s = ge(function(a) {
    n.current = typeof a == "function" ? a(n.current) : a, o();
  });
  return [i, s];
}
var J = "none", Me = "appear", Oe = "enter", Re = "leave", cn = "none", W = "prepare", ce = "start", le = "active", Ot = "end", An = "prepared";
function ln(e, t) {
  var r = {};
  return r[e.toLowerCase()] = t.toLowerCase(), r["Webkit".concat(e)] = "webkit".concat(t), r["Moz".concat(e)] = "moz".concat(t), r["ms".concat(e)] = "MS".concat(t), r["O".concat(e)] = "o".concat(t.toLowerCase()), r;
}
function ei(e, t) {
  var r = {
    animationend: ln("Animation", "AnimationEnd"),
    transitionend: ln("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete r.animationend.animation, "TransitionEvent" in t || delete r.transitionend.transition), r;
}
var ti = ei(Ne(), typeof window < "u" ? window : {}), In = {};
if (Ne()) {
  var ni = document.createElement("div");
  In = ni.style;
}
var Le = {};
function $n(e) {
  if (Le[e])
    return Le[e];
  var t = ti[e];
  if (t)
    for (var r = Object.keys(t), o = r.length, n = 0; n < o; n += 1) {
      var i = r[n];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in In)
        return Le[e] = t[i], Le[e];
    }
  return "";
}
var jn = $n("animationend"), Dn = $n("transitionend"), zn = !!(jn && Dn), un = jn || "animationend", fn = Dn || "transitionend";
function dn(e, t) {
  if (!e) return null;
  if (k(e) === "object") {
    var r = t.replace(/-\w/g, function(o) {
      return o[1].toUpperCase();
    });
    return e[r];
  }
  return "".concat(e, "-").concat(t);
}
const ri = function(e) {
  var t = ee();
  function r(n) {
    n && (n.removeEventListener(fn, e), n.removeEventListener(un, e));
  }
  function o(n) {
    t.current && t.current !== n && r(t.current), n && n !== t.current && (n.addEventListener(fn, e), n.addEventListener(un, e), t.current = n);
  }
  return M.useEffect(function() {
    return function() {
      r(t.current);
    };
  }, []), [o, r];
};
var kn = Ne() ? Yn : pe, Fn = function(t) {
  return +setTimeout(t, 16);
}, Nn = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (Fn = function(t) {
  return window.requestAnimationFrame(t);
}, Nn = function(t) {
  return window.cancelAnimationFrame(t);
});
var mn = 0, Rt = /* @__PURE__ */ new Map();
function Hn(e) {
  Rt.delete(e);
}
var St = function(t) {
  var r = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  mn += 1;
  var o = mn;
  function n(i) {
    if (i === 0)
      Hn(o), t();
    else {
      var s = Fn(function() {
        n(i - 1);
      });
      Rt.set(o, s);
    }
  }
  return n(r), o;
};
St.cancel = function(e) {
  var t = Rt.get(e);
  return Hn(e), Nn(t);
};
const oi = function() {
  var e = M.useRef(null);
  function t() {
    St.cancel(e.current);
  }
  function r(o) {
    var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = St(function() {
      n <= 1 ? o({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : r(o, n - 1);
    });
    e.current = i;
  }
  return M.useEffect(function() {
    return function() {
      t();
    };
  }, []), [r, t];
};
var ii = [W, ce, le, Ot], si = [W, An], Vn = !1, ai = !0;
function Bn(e) {
  return e === le || e === Ot;
}
const ci = function(e, t, r) {
  var o = ve(cn), n = N(o, 2), i = n[0], s = n[1], a = oi(), c = N(a, 2), l = c[0], d = c[1];
  function u() {
    s(W, !0);
  }
  var f = t ? si : ii;
  return kn(function() {
    if (i !== cn && i !== Ot) {
      var m = f.indexOf(i), v = f[m + 1], g = r(i);
      g === Vn ? s(v, !0) : v && l(function(h) {
        function S() {
          h.isCanceled() || s(v, !0);
        }
        g === !0 ? S() : Promise.resolve(g).then(S);
      });
    }
  }, [e, i]), M.useEffect(function() {
    return function() {
      d();
    };
  }, []), [u, i];
};
function li(e, t, r, o) {
  var n = o.motionEnter, i = n === void 0 ? !0 : n, s = o.motionAppear, a = s === void 0 ? !0 : s, c = o.motionLeave, l = c === void 0 ? !0 : c, d = o.motionDeadline, u = o.motionLeaveImmediately, f = o.onAppearPrepare, m = o.onEnterPrepare, v = o.onLeavePrepare, g = o.onAppearStart, h = o.onEnterStart, S = o.onLeaveStart, y = o.onAppearActive, _ = o.onEnterActive, b = o.onLeaveActive, w = o.onAppearEnd, p = o.onEnterEnd, P = o.onLeaveEnd, T = o.onVisibleChanged, R = ve(), L = N(R, 2), A = L[0], I = L[1], $ = Jo(J), j = N($, 2), D = j[0], V = j[1], te = ve(null), Z = N(te, 2), ye = Z[0], be = Z[1], B = D(), ne = ee(!1), me = ee(null);
  function G() {
    return r();
  }
  var re = ee(!1);
  function Se() {
    V(J), be(null, !0);
  }
  var Q = ge(function(H) {
    var F = D();
    if (F !== J) {
      var K = G();
      if (!(H && !H.deadline && H.target !== K)) {
        var we = re.current, Te;
        F === Me && we ? Te = w == null ? void 0 : w(K, H) : F === Oe && we ? Te = p == null ? void 0 : p(K, H) : F === Re && we && (Te = P == null ? void 0 : P(K, H)), we && Te !== !1 && Se();
      }
    }
  }), Ye = ri(Q), xe = N(Ye, 1), Ce = xe[0], Ee = function(F) {
    switch (F) {
      case Me:
        return E(E(E({}, W, f), ce, g), le, y);
      case Oe:
        return E(E(E({}, W, m), ce, h), le, _);
      case Re:
        return E(E(E({}, W, v), ce, S), le, b);
      default:
        return {};
    }
  }, oe = M.useMemo(function() {
    return Ee(B);
  }, [B]), _e = ci(B, !e, function(H) {
    if (H === W) {
      var F = oe[W];
      return F ? F(G()) : Vn;
    }
    if (ie in oe) {
      var K;
      be(((K = oe[ie]) === null || K === void 0 ? void 0 : K.call(oe, G(), null)) || null);
    }
    return ie === le && B !== J && (Ce(G()), d > 0 && (clearTimeout(me.current), me.current = setTimeout(function() {
      Q({
        deadline: !0
      });
    }, d))), ie === An && Se(), ai;
  }), Lt = N(_e, 2), Wn = Lt[0], ie = Lt[1], Kn = Bn(ie);
  re.current = Kn;
  var At = ee(null);
  kn(function() {
    if (!(ne.current && At.current === t)) {
      I(t);
      var H = ne.current;
      ne.current = !0;
      var F;
      !H && t && a && (F = Me), H && t && i && (F = Oe), (H && !t && l || !H && u && !t && l) && (F = Re);
      var K = Ee(F);
      F && (e || K[W]) ? (V(F), Wn()) : V(J), At.current = t;
    }
  }, [t]), pe(function() {
    // Cancel appear
    (B === Me && !a || // Cancel enter
    B === Oe && !i || // Cancel leave
    B === Re && !l) && V(J);
  }, [a, i, l]), pe(function() {
    return function() {
      ne.current = !1, clearTimeout(me.current);
    };
  }, []);
  var Ze = M.useRef(!1);
  pe(function() {
    A && (Ze.current = !0), A !== void 0 && B === J && ((Ze.current || A) && (T == null || T(A)), Ze.current = !0);
  }, [A, B]);
  var Je = ye;
  return oe[W] && ie === ce && (Je = C({
    transition: "none"
  }, Je)), [B, ie, Je, A ?? t];
}
function ui(e) {
  var t = e;
  k(e) === "object" && (t = e.transitionSupport);
  function r(n, i) {
    return !!(n.motionName && t && i !== !1);
  }
  var o = /* @__PURE__ */ M.forwardRef(function(n, i) {
    var s = n.visible, a = s === void 0 ? !0 : s, c = n.removeOnLeave, l = c === void 0 ? !0 : c, d = n.forceRender, u = n.children, f = n.motionName, m = n.leavedClassName, v = n.eventProps, g = M.useContext(Yo), h = g.motion, S = r(n, h), y = ee(), _ = ee();
    function b() {
      try {
        return y.current instanceof HTMLElement ? y.current : qo(_.current);
      } catch {
        return null;
      }
    }
    var w = li(S, a, b, n), p = N(w, 4), P = p[0], T = p[1], R = p[2], L = p[3], A = M.useRef(L);
    L && (A.current = !0);
    var I = M.useCallback(function(Z) {
      y.current = Z, Po(i, Z);
    }, [i]), $, j = C(C({}, v), {}, {
      visible: a
    });
    if (!u)
      $ = null;
    else if (P === J)
      L ? $ = u(C({}, j), I) : !l && A.current && m ? $ = u(C(C({}, j), {}, {
        className: m
      }), I) : d || !l && !m ? $ = u(C(C({}, j), {}, {
        style: {
          display: "none"
        }
      }), I) : $ = null;
    else {
      var D;
      T === W ? D = "prepare" : Bn(T) ? D = "active" : T === ce && (D = "start");
      var V = dn(f, "".concat(P, "-").concat(D));
      $ = u(C(C({}, j), {}, {
        className: U(dn(f, P), E(E({}, V, V && D), f, typeof f == "string")),
        style: R
      }), I);
    }
    if (/* @__PURE__ */ M.isValidElement($) && Mo($)) {
      var te = Oo($);
      te || ($ = /* @__PURE__ */ M.cloneElement($, {
        ref: I
      }));
    }
    return /* @__PURE__ */ M.createElement(Zo, {
      ref: _
    }, $);
  });
  return o.displayName = "CSSMotion", o;
}
const Gn = ui(zn);
var xt = "add", Ct = "keep", Et = "remove", ct = "removed";
function fi(e) {
  var t;
  return e && k(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, C(C({}, t), {}, {
    key: String(t.key)
  });
}
function _t() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(fi);
}
function di() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], r = [], o = 0, n = t.length, i = _t(e), s = _t(t);
  i.forEach(function(l) {
    for (var d = !1, u = o; u < n; u += 1) {
      var f = s[u];
      if (f.key === l.key) {
        o < u && (r = r.concat(s.slice(o, u).map(function(m) {
          return C(C({}, m), {}, {
            status: xt
          });
        })), o = u), r.push(C(C({}, f), {}, {
          status: Ct
        })), o += 1, d = !0;
        break;
      }
    }
    d || r.push(C(C({}, l), {}, {
      status: Et
    }));
  }), o < n && (r = r.concat(s.slice(o).map(function(l) {
    return C(C({}, l), {}, {
      status: xt
    });
  })));
  var a = {};
  r.forEach(function(l) {
    var d = l.key;
    a[d] = (a[d] || 0) + 1;
  });
  var c = Object.keys(a).filter(function(l) {
    return a[l] > 1;
  });
  return c.forEach(function(l) {
    r = r.filter(function(d) {
      var u = d.key, f = d.status;
      return u !== l || f !== Et;
    }), r.forEach(function(d) {
      d.key === l && (d.status = Ct);
    });
  }), r;
}
var mi = ["component", "children", "onVisibleChanged", "onAllRemoved"], hi = ["status"], pi = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function gi(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : Gn, r = /* @__PURE__ */ function(o) {
    ke(i, o);
    var n = Fe(i);
    function i() {
      var s;
      fe(this, i);
      for (var a = arguments.length, c = new Array(a), l = 0; l < a; l++)
        c[l] = arguments[l];
      return s = n.call.apply(n, [this].concat(c)), E(se(s), "state", {
        keyEntities: []
      }), E(se(s), "removeKey", function(d) {
        s.setState(function(u) {
          var f = u.keyEntities.map(function(m) {
            return m.key !== d ? m : C(C({}, m), {}, {
              status: ct
            });
          });
          return {
            keyEntities: f
          };
        }, function() {
          var u = s.state.keyEntities, f = u.filter(function(m) {
            var v = m.status;
            return v !== ct;
          }).length;
          f === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return de(i, [{
      key: "render",
      value: function() {
        var a = this, c = this.state.keyEntities, l = this.props, d = l.component, u = l.children, f = l.onVisibleChanged;
        l.onAllRemoved;
        var m = an(l, mi), v = d || M.Fragment, g = {};
        return pi.forEach(function(h) {
          g[h] = m[h], delete m[h];
        }), delete m.keys, /* @__PURE__ */ M.createElement(v, m, c.map(function(h, S) {
          var y = h.status, _ = an(h, hi), b = y === xt || y === Ct;
          return /* @__PURE__ */ M.createElement(t, ue({}, g, {
            key: _.key,
            visible: b,
            eventProps: _,
            onVisibleChanged: function(p) {
              f == null || f(p, {
                key: _.key
              }), p || a.removeKey(_.key);
            }
          }), function(w, p) {
            return u(C(C({}, w), {}, {
              index: S
            }), p);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, c) {
        var l = a.keys, d = c.keyEntities, u = _t(l), f = di(d, u);
        return {
          keyEntities: f.filter(function(m) {
            var v = d.find(function(g) {
              var h = g.key;
              return m.key === h;
            });
            return !(v && v.status === ct && m.status === Et);
          })
        };
      }
    }]), i;
  }(M.Component);
  return E(r, "defaultProps", {
    component: "div"
  }), r;
}
gi(zn);
const lt = () => ({
  height: 0,
  opacity: 0
}), hn = (e) => {
  const {
    scrollHeight: t
  } = e;
  return {
    height: t,
    opacity: 1
  };
}, vi = (e) => ({
  height: e ? e.offsetHeight : 0
}), ut = (e, t) => (t == null ? void 0 : t.deadline) === !0 || t.propertyName === "height", yi = (e = ao) => ({
  motionName: `${e}-motion-collapse`,
  onAppearStart: lt,
  onEnterStart: lt,
  onAppearActive: hn,
  onEnterActive: hn,
  onLeaveStart: vi,
  onLeaveActive: lt,
  onAppearEnd: ut,
  onEnterEnd: ut,
  onLeaveEnd: ut,
  motionDeadline: 500
}), bi = (e, t, r) => {
  const o = typeof e == "boolean" || (e == null ? void 0 : e.expandedKeys) === void 0, [n, i, s] = x.useMemo(() => {
    let u = {
      expandedKeys: [],
      onExpand: () => {
      }
    };
    return e ? (typeof e == "object" && (u = {
      ...u,
      ...e
    }), [!0, u.expandedKeys, u.onExpand]) : [!1, u.expandedKeys, u.onExpand];
  }, [e]), [a, c] = bo(i, {
    value: o ? void 0 : i,
    onChange: s
  }), l = (u) => {
    c((f) => {
      const m = o ? f : i, v = m.includes(u) ? m.filter((g) => g !== u) : [...m, u];
      return s == null || s(v), v;
    });
  }, d = x.useMemo(() => n ? {
    ...yi(r),
    motionAppear: !1,
    leavedClassName: `${t}-content-hidden`
  } : {}, [r, t, n]);
  return [n, a, n ? l : void 0, d];
}, Si = (e) => ({
  [e.componentCls]: {
    // For common/openAnimation
    [`${e.antCls}-motion-collapse-legacy`]: {
      overflow: "hidden",
      "&-active": {
        transition: `height ${e.motionDurationMid} ${e.motionEaseInOut},
        opacity ${e.motionDurationMid} ${e.motionEaseInOut} !important`
      }
    },
    [`${e.antCls}-motion-collapse`]: {
      overflow: "hidden",
      transition: `height ${e.motionDurationMid} ${e.motionEaseInOut},
        opacity ${e.motionDurationMid} ${e.motionEaseInOut} !important`
    }
  }
});
let ft = /* @__PURE__ */ function(e) {
  return e.PENDING = "pending", e.SUCCESS = "success", e.ERROR = "error", e;
}({});
const Un = /* @__PURE__ */ x.createContext(null), xi = (e) => {
  const {
    info: t = {},
    nextStatus: r,
    onClick: o,
    ...n
  } = e, i = En(n, {
    attr: !0,
    aria: !0,
    data: !0
  }), {
    prefixCls: s,
    collapseMotion: a,
    enableCollapse: c,
    expandedKeys: l,
    direction: d,
    classNames: u = {},
    styles: f = {}
  } = x.useContext(Un), m = x.useId(), {
    key: v = m,
    icon: g,
    title: h,
    extra: S,
    content: y,
    footer: _,
    status: b,
    description: w
  } = t, p = `${s}-item`, P = () => o == null ? void 0 : o(v), T = l == null ? void 0 : l.includes(v);
  return /* @__PURE__ */ x.createElement("div", ue({}, i, {
    className: U(p, {
      [`${p}-${b}${r ? `-${r}` : ""}`]: b
    }, e.className),
    style: e.style
  }), /* @__PURE__ */ x.createElement("div", {
    className: U(`${p}-header`, u.itemHeader),
    style: f.itemHeader,
    onClick: P
  }, /* @__PURE__ */ x.createElement(ar, {
    icon: g,
    className: `${p}-icon`
  }), /* @__PURE__ */ x.createElement("div", {
    className: U(`${p}-header-box`, {
      [`${p}-collapsible`]: c && y
    })
  }, /* @__PURE__ */ x.createElement(jt.Text, {
    strong: !0,
    ellipsis: {
      tooltip: {
        placement: d === "rtl" ? "topRight" : "topLeft",
        title: h
      }
    },
    className: `${p}-title`
  }, c && y && (d === "rtl" ? /* @__PURE__ */ x.createElement(fr, {
    className: `${p}-collapse-icon`,
    rotate: T ? -90 : 0
  }) : /* @__PURE__ */ x.createElement(dr, {
    className: `${p}-collapse-icon`,
    rotate: T ? 90 : 0
  })), h), w && /* @__PURE__ */ x.createElement(jt.Text, {
    className: `${p}-desc`,
    ellipsis: {
      tooltip: {
        placement: d === "rtl" ? "topRight" : "topLeft",
        title: w
      }
    },
    type: "secondary"
  }, w)), S && /* @__PURE__ */ x.createElement("div", {
    className: `${p}-extra`
  }, S)), y && /* @__PURE__ */ x.createElement(Gn, ue({}, a, {
    visible: c ? T : !0
  }), ({
    className: R,
    style: L
  }, A) => /* @__PURE__ */ x.createElement("div", {
    className: U(`${p}-content`, R),
    ref: A,
    style: L
  }, /* @__PURE__ */ x.createElement("div", {
    className: U(`${p}-content-box`, u.itemContent),
    style: f.itemContent
  }, y))), _ && /* @__PURE__ */ x.createElement("div", {
    className: U(`${p}-footer`, u.itemFooter),
    style: f.itemFooter
  }, _));
}, Ci = (e) => {
  const {
    componentCls: t
  } = e, r = `${t}-item`, o = {
    [ft.PENDING]: e.colorPrimaryText,
    [ft.SUCCESS]: e.colorSuccessText,
    [ft.ERROR]: e.colorErrorText
  }, n = Object.keys(o);
  return n.reduce((i, s) => {
    const a = o[s];
    return n.forEach((c) => {
      const l = `& ${r}-${s}-${c}`, d = s === c ? {} : {
        backgroundColor: "none !important",
        backgroundImage: `linear-gradient(${a}, ${o[c]})`
      };
      i[l] = {
        [`& ${r}-icon, & > *::before`]: {
          backgroundColor: `${a} !important`
        },
        "& > :last-child::before": d
      };
    }), i;
  }, {});
}, Ei = (e) => {
  const {
    calc: t,
    componentCls: r
  } = e, o = `${r}-item`, n = {
    content: '""',
    width: t(e.lineWidth).mul(2).equal(),
    display: "block",
    position: "absolute",
    insetInlineEnd: "none",
    backgroundColor: e.colorTextPlaceholder
  };
  return {
    "& > :last-child > :last-child": {
      "&::before": {
        display: "none !important"
      },
      [`&${o}-footer`]: {
        "&::before": {
          display: "block !important",
          bottom: 0
        }
      }
    },
    [`& > ${o}`]: {
      [`& ${o}-header, & ${o}-content, & ${o}-footer`]: {
        position: "relative",
        "&::before": {
          bottom: t(e.itemGap).mul(-1).equal()
        }
      },
      [`& ${o}-header, & ${o}-content`]: {
        marginInlineStart: t(e.itemSize).mul(-1).equal(),
        "&::before": {
          ...n,
          insetInlineStart: t(e.itemSize).div(2).sub(e.lineWidth).equal()
        }
      },
      [`& ${o}-header::before`]: {
        top: e.itemSize,
        bottom: t(e.itemGap).mul(-2).equal()
      },
      [`& ${o}-content::before`]: {
        top: "100%"
      },
      [`& ${o}-footer::before`]: {
        ...n,
        top: 0,
        insetInlineStart: t(e.itemSize).div(-2).sub(e.lineWidth).equal()
      }
    }
  };
}, _i = (e) => {
  const {
    componentCls: t
  } = e, r = `${t}-item`;
  return {
    [r]: {
      display: "flex",
      flexDirection: "column",
      [`& ${r}-collapsible`]: {
        cursor: "pointer"
      },
      [`& ${r}-header`]: {
        display: "flex",
        marginBottom: e.itemGap,
        gap: e.itemGap,
        alignItems: "flex-start",
        [`& ${r}-icon`]: {
          height: e.itemSize,
          width: e.itemSize,
          fontSize: e.itemFontSize
        },
        [`& ${r}-extra`]: {
          height: e.itemSize,
          maxHeight: e.itemSize
        },
        [`& ${r}-header-box`]: {
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          [`& ${r}-title`]: {
            height: e.itemSize,
            lineHeight: `${je(e.itemSize)}`,
            maxHeight: e.itemSize,
            fontSize: e.itemFontSize,
            [`& ${r}-collapse-icon`]: {
              marginInlineEnd: e.marginXS
            }
          },
          [`& ${r}-desc`]: {
            fontSize: e.itemFontSize
          }
        }
      },
      [`& ${r}-content`]: {
        [`& ${r}-content-hidden`]: {
          display: "none"
        },
        [`& ${r}-content-box`]: {
          padding: e.itemGap,
          display: "inline-block",
          maxWidth: `calc(100% - ${e.itemSize})`,
          borderRadius: e.borderRadiusLG,
          backgroundColor: e.colorBgContainer,
          border: `${je(e.lineWidth)} ${e.lineType} ${e.colorBorderSecondary}`
        }
      },
      [`& ${r}-footer`]: {
        marginTop: e.itemGap,
        display: "inline-flex"
      }
    }
  };
}, dt = (e, t = "middle") => {
  const {
    componentCls: r
  } = e, o = {
    large: {
      itemSize: e.itemSizeLG,
      itemGap: e.itemGapLG,
      itemFontSize: e.itemFontSizeLG
    },
    middle: {
      itemSize: e.itemSize,
      itemGap: e.itemGap,
      itemFontSize: e.itemFontSize
    },
    small: {
      itemSize: e.itemSizeSM,
      itemGap: e.itemGapSM,
      itemFontSize: e.itemFontSizeSM
    }
  }[t];
  return {
    [`&${r}-${t}`]: {
      paddingInlineStart: o.itemSize,
      gap: o.itemGap,
      ..._i({
        ...e,
        ...o
      }),
      ...Ei({
        ...e,
        ...o
      })
    }
  };
}, wi = (e) => {
  const {
    componentCls: t
  } = e;
  return {
    [t]: {
      display: "flex",
      flexDirection: "column",
      ...Ci(e),
      ...dt(e),
      ...dt(e, "large"),
      ...dt(e, "small"),
      [`&${t}-rtl`]: {
        direction: "rtl"
      }
    }
  };
}, Ti = Wo("ThoughtChain", (e) => {
  const t = Mt(e, {
    // small size tokens
    itemFontSizeSM: e.fontSizeSM,
    itemSizeSM: e.calc(e.controlHeightXS).add(e.controlHeightSM).div(2).equal(),
    itemGapSM: e.marginSM,
    // default size tokens
    itemFontSize: e.fontSize,
    itemSize: e.calc(e.controlHeightSM).add(e.controlHeight).div(2).equal(),
    itemGap: e.margin,
    // large size tokens
    itemFontSizeLG: e.fontSizeLG,
    itemSizeLG: e.calc(e.controlHeight).add(e.controlHeightLG).div(2).equal(),
    itemGapLG: e.marginLG
  });
  return [wi(t), Si(t)];
}), Pi = (e) => {
  const {
    prefixCls: t,
    rootClassName: r,
    className: o,
    items: n,
    collapsible: i,
    styles: s = {},
    style: a,
    classNames: c = {},
    size: l = "middle",
    ...d
  } = e, u = En(d, {
    attr: !0,
    aria: !0,
    data: !0
  }), {
    getPrefixCls: f,
    direction: m
  } = vt(), v = f(), g = f("thought-chain", t), h = so("thoughtChain"), [S, y, _, b] = bi(i, g, v), [w, p, P] = Ti(g), T = U(o, r, g, h.className, p, P, {
    [`${g}-rtl`]: m === "rtl"
  }, `${g}-${l}`);
  return w(/* @__PURE__ */ x.createElement("div", ue({}, u, {
    className: T,
    style: {
      ...h.style,
      ...a
    }
  }), /* @__PURE__ */ x.createElement(Un.Provider, {
    value: {
      prefixCls: g,
      enableCollapse: S,
      collapseMotion: b,
      expandedKeys: y,
      direction: m,
      classNames: {
        itemHeader: U(h.classNames.itemHeader, c.itemHeader),
        itemContent: U(h.classNames.itemContent, c.itemContent),
        itemFooter: U(h.classNames.itemFooter, c.itemFooter)
      },
      styles: {
        itemHeader: {
          ...h.styles.itemHeader,
          ...s.itemHeader
        },
        itemContent: {
          ...h.styles.itemContent,
          ...s.itemContent
        },
        itemFooter: {
          ...h.styles.itemFooter,
          ...s.itemFooter
        }
      }
    }
  }, n == null ? void 0 : n.map((R, L) => {
    var A;
    return /* @__PURE__ */ x.createElement(xi, {
      key: R.key || `key_${L}`,
      className: U(h.classNames.item, c.item),
      style: {
        ...h.styles.item,
        ...s.item
      },
      info: {
        ...R,
        icon: R.icon || L + 1
      },
      onClick: _,
      nextStatus: ((A = n[L + 1]) == null ? void 0 : A.status) || R.status
    });
  }))));
}, Mi = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Oi(e) {
  return e ? Object.keys(e).reduce((t, r) => {
    const o = e[r];
    return t[r] = Ri(r, o), t;
  }, {}) : {};
}
function Ri(e, t) {
  return typeof t == "number" && !Mi.includes(e) ? t + "px" : t;
}
function wt(e) {
  const t = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const n = x.Children.toArray(e._reactElement.props.children).map((i) => {
      if (x.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = wt(i.props.el);
        return x.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...x.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return n.originalChildren = e._reactElement.props.children, t.push(mt(x.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: n
    }), r)), {
      clonedElement: r,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((n) => {
    e.getEventListeners(n).forEach(({
      listener: s,
      type: a,
      useCapture: c
    }) => {
      r.addEventListener(a, s, c);
    });
  });
  const o = Array.from(e.childNodes);
  for (let n = 0; n < o.length; n++) {
    const i = o[n];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = wt(i);
      t.push(...a), r.appendChild(s);
    } else i.nodeType === 3 && r.appendChild(i.cloneNode());
  }
  return {
    clonedElement: r,
    portals: t
  };
}
function Li(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const pn = Zn(({
  slot: e,
  clone: t,
  className: r,
  style: o,
  observeAttributes: n
}, i) => {
  const s = ee(), [a, c] = Jn([]), {
    forceClone: l
  } = or(), d = l ? !0 : t;
  return pe(() => {
    var g;
    if (!s.current || !e)
      return;
    let u = e;
    function f() {
      let h = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (h = u.children[0], h.tagName.toLowerCase() === "react-portal-target" && h.children[0] && (h = h.children[0])), Li(i, h), r && h.classList.add(...r.split(" ")), o) {
        const S = Oi(o);
        Object.keys(S).forEach((y) => {
          h.style[y] = S[y];
        });
      }
    }
    let m = null, v = null;
    if (d && window.MutationObserver) {
      let h = function() {
        var b, w, p;
        (b = s.current) != null && b.contains(u) && ((w = s.current) == null || w.removeChild(u));
        const {
          portals: y,
          clonedElement: _
        } = wt(e);
        u = _, c(y), u.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          f();
        }, 50), (p = s.current) == null || p.appendChild(u);
      };
      h();
      const S = _r(() => {
        h(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: n
        });
      }, 50);
      m = new window.MutationObserver(S), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", f(), (g = s.current) == null || g.appendChild(u);
    return () => {
      var h, S;
      u.style.display = "", (h = s.current) != null && h.contains(u) && ((S = s.current) == null || S.removeChild(u)), m == null || m.disconnect();
    };
  }, [e, d, r, o, i, n, l]), x.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), Ai = ({
  children: e,
  ...t
}) => /* @__PURE__ */ q.jsx(q.Fragment, {
  children: e(t)
});
function Ii(e) {
  return x.createElement(Ai, {
    children: e
  });
}
function Xn(e, t, r) {
  const o = e.filter(Boolean);
  if (o.length !== 0)
    return o.map((n, i) => {
      var l, d;
      if (typeof n != "object")
        return t != null && t.fallback ? t.fallback(n) : n;
      const s = t != null && t.itemPropsTransformer ? t == null ? void 0 : t.itemPropsTransformer({
        ...n.props,
        key: ((l = n.props) == null ? void 0 : l.key) ?? (r ? `${r}-${i}` : `${i}`)
      }) : {
        ...n.props,
        key: ((d = n.props) == null ? void 0 : d.key) ?? (r ? `${r}-${i}` : `${i}`)
      };
      let a = s;
      Object.keys(n.slots).forEach((u) => {
        if (!n.slots[u] || !(n.slots[u] instanceof Element) && !n.slots[u].el)
          return;
        const f = u.split(".");
        f.forEach((y, _) => {
          a[y] || (a[y] = {}), _ !== f.length - 1 && (a = s[y]);
        });
        const m = n.slots[u];
        let v, g, h = (t == null ? void 0 : t.clone) ?? !1, S = t == null ? void 0 : t.forceClone;
        m instanceof Element ? v = m : (v = m.el, g = m.callback, h = m.clone ?? h, S = m.forceClone ?? S), S = S ?? !!g, a[f[f.length - 1]] = v ? g ? (...y) => (g(f[f.length - 1], y), /* @__PURE__ */ q.jsx($t, {
          ...n.ctx,
          params: y,
          forceClone: S,
          children: /* @__PURE__ */ q.jsx(pn, {
            slot: v,
            clone: h
          })
        })) : Ii((y) => /* @__PURE__ */ q.jsx($t, {
          ...n.ctx,
          forceClone: S,
          children: /* @__PURE__ */ q.jsx(pn, {
            ...y,
            slot: v,
            clone: h
          })
        })) : a[f[f.length - 1]], a = s;
      });
      const c = (t == null ? void 0 : t.children) || "children";
      return n[c] ? s[c] = Xn(n[c], t, `${i}`) : t != null && t.children && (s[c] = void 0, Reflect.deleteProperty(s, c)), s;
    });
}
const {
  useItems: $i,
  withItemsContextProvider: ji,
  ItemHandler: ki
} = ir("antdx-thought-chain-items"), Fi = Qr(ji(["default", "items"], ({
  children: e,
  items: t,
  ...r
}) => {
  const {
    items: o
  } = $i(), n = o.items.length > 0 ? o.items : o.default;
  return /* @__PURE__ */ q.jsxs(q.Fragment, {
    children: [/* @__PURE__ */ q.jsx("div", {
      style: {
        display: "none"
      },
      children: e
    }), /* @__PURE__ */ q.jsx(Pi, {
      ...r,
      items: er(() => t || Xn(n, {
        clone: !0
      }), [t, n])
    })]
  });
}));
export {
  Fi as ThoughtChain,
  Fi as default
};
