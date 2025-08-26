import { i as Kt, a as J, r as qt, Z as ce, g as Yt, c as Y, b as Ne } from "./Index-BYK17Tg-.js";
const _ = window.ms_globals.React, g = window.ms_globals.React, Xt = window.ms_globals.React.version, Vt = window.ms_globals.React.forwardRef, St = window.ms_globals.React.useRef, Wt = window.ms_globals.React.useState, Ut = window.ms_globals.React.useEffect, Gt = window.ms_globals.React.useCallback, he = window.ms_globals.React.useMemo, Be = window.ms_globals.ReactDOM.createPortal, Qt = window.ms_globals.internalContext.useContextPropsContext, Qe = window.ms_globals.internalContext.ContextPropsProvider, Ct = window.ms_globals.createItemsContext.createItemsContext, Jt = window.ms_globals.antd.ConfigProvider, He = window.ms_globals.antd.theme, Zt = window.ms_globals.antd.Avatar, se = window.ms_globals.antdCssinjs.unit, Ie = window.ms_globals.antdCssinjs.token2CSSVar, Je = window.ms_globals.antdCssinjs.useStyleRegister, er = window.ms_globals.antdCssinjs.useCSSVarRegister, tr = window.ms_globals.antdCssinjs.createTheme, rr = window.ms_globals.antdCssinjs.useCacheToken, wt = window.ms_globals.antdCssinjs.Keyframes;
var nr = /\s/;
function or(t) {
  for (var e = t.length; e-- && nr.test(t.charAt(e)); )
    ;
  return e;
}
var sr = /^\s+/;
function ir(t) {
  return t && t.slice(0, or(t) + 1).replace(sr, "");
}
var Ze = NaN, ar = /^[-+]0x[0-9a-f]+$/i, lr = /^0b[01]+$/i, cr = /^0o[0-7]+$/i, ur = parseInt;
function et(t) {
  if (typeof t == "number")
    return t;
  if (Kt(t))
    return Ze;
  if (J(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = J(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = ir(t);
  var n = lr.test(t);
  return n || cr.test(t) ? ur(t.slice(2), n ? 2 : 8) : ar.test(t) ? Ze : +t;
}
var Re = function() {
  return qt.Date.now();
}, fr = "Expected a function", dr = Math.max, hr = Math.min;
function gr(t, e, n) {
  var o, r, s, i, a, l, u = 0, d = !1, c = !1, f = !0;
  if (typeof t != "function")
    throw new TypeError(fr);
  e = et(e) || 0, J(n) && (d = !!n.leading, c = "maxWait" in n, s = c ? dr(et(n.maxWait) || 0, e) : s, f = "trailing" in n ? !!n.trailing : f);
  function h(S) {
    var w = o, P = r;
    return o = r = void 0, u = S, i = t.apply(P, w), i;
  }
  function m(S) {
    return u = S, a = setTimeout(v, e), d ? h(S) : i;
  }
  function y(S) {
    var w = S - l, P = S - u, k = e - w;
    return c ? hr(k, s - P) : k;
  }
  function p(S) {
    var w = S - l, P = S - u;
    return l === void 0 || w >= e || w < 0 || c && P >= s;
  }
  function v() {
    var S = Re();
    if (p(S))
      return x(S);
    a = setTimeout(v, y(S));
  }
  function x(S) {
    return a = void 0, f && o ? h(S) : (o = r = void 0, i);
  }
  function R() {
    a !== void 0 && clearTimeout(a), u = 0, o = l = r = a = void 0;
  }
  function b() {
    return a === void 0 ? i : x(Re());
  }
  function C() {
    var S = Re(), w = p(S);
    if (o = arguments, r = this, l = S, w) {
      if (a === void 0)
        return m(l);
      if (c)
        return clearTimeout(a), a = setTimeout(v, e), h(l);
    }
    return a === void 0 && (a = setTimeout(v, e)), i;
  }
  return C.cancel = R, C.flush = b, C;
}
var _t = {
  exports: {}
}, pe = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var mr = g, pr = Symbol.for("react.element"), br = Symbol.for("react.fragment"), yr = Object.prototype.hasOwnProperty, vr = mr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, xr = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Tt(t, e, n) {
  var o, r = {}, s = null, i = null;
  n !== void 0 && (s = "" + n), e.key !== void 0 && (s = "" + e.key), e.ref !== void 0 && (i = e.ref);
  for (o in e) yr.call(e, o) && !xr.hasOwnProperty(o) && (r[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) r[o] === void 0 && (r[o] = e[o]);
  return {
    $$typeof: pr,
    type: t,
    key: s,
    ref: i,
    props: r,
    _owner: vr.current
  };
}
pe.Fragment = br;
pe.jsx = Tt;
pe.jsxs = Tt;
_t.exports = pe;
var z = _t.exports;
const {
  SvelteComponent: Sr,
  assign: tt,
  binding_callbacks: rt,
  check_outros: Cr,
  children: Et,
  claim_element: Mt,
  claim_space: wr,
  component_subscribe: nt,
  compute_slots: _r,
  create_slot: Tr,
  detach: Q,
  element: Pt,
  empty: ot,
  exclude_internal_props: st,
  get_all_dirty_from_scope: Er,
  get_slot_changes: Mr,
  group_outros: Pr,
  init: Or,
  insert_hydration: ue,
  safe_not_equal: Ir,
  set_custom_element_data: Ot,
  space: Rr,
  transition_in: fe,
  transition_out: De,
  update_slot_base: kr
} = window.__gradio__svelte__internal, {
  beforeUpdate: jr,
  getContext: Lr,
  onDestroy: $r,
  setContext: Br
} = window.__gradio__svelte__internal;
function it(t) {
  let e, n;
  const o = (
    /*#slots*/
    t[7].default
  ), r = Tr(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = Pt("svelte-slot"), r && r.c(), this.h();
    },
    l(s) {
      e = Mt(s, "SVELTE-SLOT", {
        class: !0
      });
      var i = Et(e);
      r && r.l(i), i.forEach(Q), this.h();
    },
    h() {
      Ot(e, "class", "svelte-1rt0kpf");
    },
    m(s, i) {
      ue(s, e, i), r && r.m(e, null), t[9](e), n = !0;
    },
    p(s, i) {
      r && r.p && (!n || i & /*$$scope*/
      64) && kr(
        r,
        o,
        s,
        /*$$scope*/
        s[6],
        n ? Mr(
          o,
          /*$$scope*/
          s[6],
          i,
          null
        ) : Er(
          /*$$scope*/
          s[6]
        ),
        null
      );
    },
    i(s) {
      n || (fe(r, s), n = !0);
    },
    o(s) {
      De(r, s), n = !1;
    },
    d(s) {
      s && Q(e), r && r.d(s), t[9](null);
    }
  };
}
function Hr(t) {
  let e, n, o, r, s = (
    /*$$slots*/
    t[4].default && it(t)
  );
  return {
    c() {
      e = Pt("react-portal-target"), n = Rr(), s && s.c(), o = ot(), this.h();
    },
    l(i) {
      e = Mt(i, "REACT-PORTAL-TARGET", {
        class: !0
      }), Et(e).forEach(Q), n = wr(i), s && s.l(i), o = ot(), this.h();
    },
    h() {
      Ot(e, "class", "svelte-1rt0kpf");
    },
    m(i, a) {
      ue(i, e, a), t[8](e), ue(i, n, a), s && s.m(i, a), ue(i, o, a), r = !0;
    },
    p(i, [a]) {
      /*$$slots*/
      i[4].default ? s ? (s.p(i, a), a & /*$$slots*/
      16 && fe(s, 1)) : (s = it(i), s.c(), fe(s, 1), s.m(o.parentNode, o)) : s && (Pr(), De(s, 1, 1, () => {
        s = null;
      }), Cr());
    },
    i(i) {
      r || (fe(s), r = !0);
    },
    o(i) {
      De(s), r = !1;
    },
    d(i) {
      i && (Q(e), Q(n), Q(o)), t[8](null), s && s.d(i);
    }
  };
}
function at(t) {
  const {
    svelteInit: e,
    ...n
  } = t;
  return n;
}
function Dr(t, e, n) {
  let o, r, {
    $$slots: s = {},
    $$scope: i
  } = e;
  const a = _r(s);
  let {
    svelteInit: l
  } = e;
  const u = ce(at(e)), d = ce();
  nt(t, d, (b) => n(0, o = b));
  const c = ce();
  nt(t, c, (b) => n(1, r = b));
  const f = [], h = Lr("$$ms-gr-react-wrapper"), {
    slotKey: m,
    slotIndex: y,
    subSlotIndex: p
  } = Yt() || {}, v = l({
    parent: h,
    props: u,
    target: d,
    slot: c,
    slotKey: m,
    slotIndex: y,
    subSlotIndex: p,
    onDestroy(b) {
      f.push(b);
    }
  });
  Br("$$ms-gr-react-wrapper", v), jr(() => {
    u.set(at(e));
  }), $r(() => {
    f.forEach((b) => b());
  });
  function x(b) {
    rt[b ? "unshift" : "push"](() => {
      o = b, d.set(o);
    });
  }
  function R(b) {
    rt[b ? "unshift" : "push"](() => {
      r = b, c.set(r);
    });
  }
  return t.$$set = (b) => {
    n(17, e = tt(tt({}, e), st(b))), "svelteInit" in b && n(5, l = b.svelteInit), "$$scope" in b && n(6, i = b.$$scope);
  }, e = st(e), [o, r, d, c, a, l, i, s, x, R];
}
class Ar extends Sr {
  constructor(e) {
    super(), Or(this, e, Dr, Hr, Ir, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: go
} = window.__gradio__svelte__internal, lt = window.ms_globals.rerender, ke = window.ms_globals.tree;
function zr(t, e = {}) {
  function n(o) {
    const r = ce(), s = new Ar({
      ...o,
      props: {
        svelteInit(i) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: t,
            props: i.props,
            slot: i.slot,
            target: i.target,
            slotIndex: i.slotIndex,
            subSlotIndex: i.subSlotIndex,
            ignore: e.ignore,
            slotKey: i.slotKey,
            nodes: []
          }, l = i.parent ?? ke;
          return l.nodes = [...l.nodes, a], lt({
            createPortal: Be,
            node: ke
          }), i.onDestroy(() => {
            l.nodes = l.nodes.filter((u) => u.svelteInstance !== r), lt({
              createPortal: Be,
              node: ke
            });
          }), a;
        },
        ...o.props
      }
    });
    return r.set(s), s;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise.then(() => {
      o(n);
    });
  });
}
const Fr = "1.6.0";
function Z() {
  return Z = Object.assign ? Object.assign.bind() : function(t) {
    for (var e = 1; e < arguments.length; e++) {
      var n = arguments[e];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (t[o] = n[o]);
    }
    return t;
  }, Z.apply(null, arguments);
}
function N(t) {
  "@babel/helpers - typeof";
  return N = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, N(t);
}
function Nr(t, e) {
  if (N(t) != "object" || !t) return t;
  var n = t[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(t, e);
    if (N(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function It(t) {
  var e = Nr(t, "string");
  return N(e) == "symbol" ? e : e + "";
}
function I(t, e, n) {
  return (e = It(e)) in t ? Object.defineProperty(t, e, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : t[e] = n, t;
}
function ct(t, e) {
  var n = Object.keys(t);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(t);
    e && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(t, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function H(t) {
  for (var e = 1; e < arguments.length; e++) {
    var n = arguments[e] != null ? arguments[e] : {};
    e % 2 ? ct(Object(n), !0).forEach(function(o) {
      I(t, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(n)) : ct(Object(n)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return t;
}
var Xr = `accept acceptCharset accessKey action allowFullScreen allowTransparency
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
    summary tabIndex target title type useMap value width wmode wrap`, Vr = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, Wr = "".concat(Xr, " ").concat(Vr).split(/[\s\n]+/), Ur = "aria-", Gr = "data-";
function ut(t, e) {
  return t.indexOf(e) === 0;
}
function Kr(t) {
  var e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, n;
  e === !1 ? n = {
    aria: !0,
    data: !0,
    attr: !0
  } : e === !0 ? n = {
    aria: !0
  } : n = H({}, e);
  var o = {};
  return Object.keys(t).forEach(function(r) {
    // Aria
    (n.aria && (r === "role" || ut(r, Ur)) || // Data
    n.data && ut(r, Gr) || // Attr
    n.attr && Wr.includes(r)) && (o[r] = t[r]);
  }), o;
}
const qr = /* @__PURE__ */ g.createContext({}), Yr = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, Qr = (t) => {
  const e = g.useContext(qr);
  return g.useMemo(() => ({
    ...Yr,
    ...e[t]
  }), [e[t]]);
};
function ge() {
  const {
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = g.useContext(Jt.ConfigContext);
  return {
    theme: r,
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o
  };
}
function Jr(t) {
  if (Array.isArray(t)) return t;
}
function Zr(t, e) {
  var n = t == null ? null : typeof Symbol < "u" && t[Symbol.iterator] || t["@@iterator"];
  if (n != null) {
    var o, r, s, i, a = [], l = !0, u = !1;
    try {
      if (s = (n = n.call(t)).next, e === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (o = s.call(n)).done) && (a.push(o.value), a.length !== e); l = !0) ;
    } catch (d) {
      u = !0, r = d;
    } finally {
      try {
        if (!l && n.return != null && (i = n.return(), Object(i) !== i)) return;
      } finally {
        if (u) throw r;
      }
    }
    return a;
  }
}
function ft(t, e) {
  (e == null || e > t.length) && (e = t.length);
  for (var n = 0, o = Array(e); n < e; n++) o[n] = t[n];
  return o;
}
function en(t, e) {
  if (t) {
    if (typeof t == "string") return ft(t, e);
    var n = {}.toString.call(t).slice(8, -1);
    return n === "Object" && t.constructor && (n = t.constructor.name), n === "Map" || n === "Set" ? Array.from(t) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? ft(t, e) : void 0;
  }
}
function tn() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function de(t, e) {
  return Jr(t) || Zr(t, e) || en(t, e) || tn();
}
function be(t, e) {
  if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function");
}
function rn(t, e) {
  for (var n = 0; n < e.length; n++) {
    var o = e[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, It(o.key), o);
  }
}
function ye(t, e, n) {
  return e && rn(t.prototype, e), Object.defineProperty(t, "prototype", {
    writable: !1
  }), t;
}
function oe(t) {
  if (t === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return t;
}
function Ae(t, e) {
  return Ae = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, Ae(t, e);
}
function Rt(t, e) {
  if (typeof e != "function" && e !== null) throw new TypeError("Super expression must either be null or a function");
  t.prototype = Object.create(e && e.prototype, {
    constructor: {
      value: t,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(t, "prototype", {
    writable: !1
  }), e && Ae(t, e);
}
function me(t) {
  return me = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
    return e.__proto__ || Object.getPrototypeOf(e);
  }, me(t);
}
function kt() {
  try {
    var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (kt = function() {
    return !!t;
  })();
}
function nn(t, e) {
  if (e && (N(e) == "object" || typeof e == "function")) return e;
  if (e !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return oe(t);
}
function jt(t) {
  var e = kt();
  return function() {
    var n, o = me(t);
    if (e) {
      var r = me(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return nn(this, n);
  };
}
var Lt = /* @__PURE__ */ ye(function t() {
  be(this, t);
}), $t = "CALC_UNIT", on = new RegExp($t, "g");
function je(t) {
  return typeof t == "number" ? "".concat(t).concat($t) : t;
}
var sn = /* @__PURE__ */ function(t) {
  Rt(n, t);
  var e = jt(n);
  function n(o, r) {
    var s;
    be(this, n), s = e.call(this), I(oe(s), "result", ""), I(oe(s), "unitlessCssVar", void 0), I(oe(s), "lowPriority", void 0);
    var i = N(o);
    return s.unitlessCssVar = r, o instanceof n ? s.result = "(".concat(o.result, ")") : i === "number" ? s.result = je(o) : i === "string" && (s.result = o), s;
  }
  return ye(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(je(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(je(r))), this.lowPriority = !0, this;
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
      var s = this, i = r || {}, a = i.unit, l = !0;
      return typeof a == "boolean" ? l = a : Array.from(this.unitlessCssVar).some(function(u) {
        return s.result.includes(u);
      }) && (l = !1), this.result = this.result.replace(on, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(Lt), an = /* @__PURE__ */ function(t) {
  Rt(n, t);
  var e = jt(n);
  function n(o) {
    var r;
    return be(this, n), r = e.call(this), I(oe(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return ye(n, [{
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
}(Lt), ln = function(e, n) {
  var o = e === "css" ? sn : an;
  return function(r) {
    return new o(r, n);
  };
}, dt = function(e, n) {
  return "".concat([n, e.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function cn(t) {
  var e = _.useRef();
  e.current = t;
  var n = _.useCallback(function() {
    for (var o, r = arguments.length, s = new Array(r), i = 0; i < r; i++)
      s[i] = arguments[i];
    return (o = e.current) === null || o === void 0 ? void 0 : o.call.apply(o, [e].concat(s));
  }, []);
  return n;
}
function un() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var ht = un() ? _.useLayoutEffect : _.useEffect, fn = function(e, n) {
  var o = _.useRef(!0);
  ht(function() {
    return e(o.current);
  }, n), ht(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, T = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Xe = Symbol.for("react.element"), Ve = Symbol.for("react.portal"), ve = Symbol.for("react.fragment"), xe = Symbol.for("react.strict_mode"), Se = Symbol.for("react.profiler"), Ce = Symbol.for("react.provider"), we = Symbol.for("react.context"), dn = Symbol.for("react.server_context"), _e = Symbol.for("react.forward_ref"), Te = Symbol.for("react.suspense"), Ee = Symbol.for("react.suspense_list"), Me = Symbol.for("react.memo"), Pe = Symbol.for("react.lazy"), hn = Symbol.for("react.offscreen"), Bt;
Bt = Symbol.for("react.module.reference");
function F(t) {
  if (typeof t == "object" && t !== null) {
    var e = t.$$typeof;
    switch (e) {
      case Xe:
        switch (t = t.type, t) {
          case ve:
          case Se:
          case xe:
          case Te:
          case Ee:
            return t;
          default:
            switch (t = t && t.$$typeof, t) {
              case dn:
              case we:
              case _e:
              case Pe:
              case Me:
              case Ce:
                return t;
              default:
                return e;
            }
        }
      case Ve:
        return e;
    }
  }
}
T.ContextConsumer = we;
T.ContextProvider = Ce;
T.Element = Xe;
T.ForwardRef = _e;
T.Fragment = ve;
T.Lazy = Pe;
T.Memo = Me;
T.Portal = Ve;
T.Profiler = Se;
T.StrictMode = xe;
T.Suspense = Te;
T.SuspenseList = Ee;
T.isAsyncMode = function() {
  return !1;
};
T.isConcurrentMode = function() {
  return !1;
};
T.isContextConsumer = function(t) {
  return F(t) === we;
};
T.isContextProvider = function(t) {
  return F(t) === Ce;
};
T.isElement = function(t) {
  return typeof t == "object" && t !== null && t.$$typeof === Xe;
};
T.isForwardRef = function(t) {
  return F(t) === _e;
};
T.isFragment = function(t) {
  return F(t) === ve;
};
T.isLazy = function(t) {
  return F(t) === Pe;
};
T.isMemo = function(t) {
  return F(t) === Me;
};
T.isPortal = function(t) {
  return F(t) === Ve;
};
T.isProfiler = function(t) {
  return F(t) === Se;
};
T.isStrictMode = function(t) {
  return F(t) === xe;
};
T.isSuspense = function(t) {
  return F(t) === Te;
};
T.isSuspenseList = function(t) {
  return F(t) === Ee;
};
T.isValidElementType = function(t) {
  return typeof t == "string" || typeof t == "function" || t === ve || t === Se || t === xe || t === Te || t === Ee || t === hn || typeof t == "object" && t !== null && (t.$$typeof === Pe || t.$$typeof === Me || t.$$typeof === Ce || t.$$typeof === we || t.$$typeof === _e || t.$$typeof === Bt || t.getModuleId !== void 0);
};
T.typeOf = F;
Number(Xt.split(".")[0]);
function gt(t, e, n, o) {
  var r = H({}, e[t]);
  if (o != null && o.deprecatedTokens) {
    var s = o.deprecatedTokens;
    s.forEach(function(a) {
      var l = de(a, 2), u = l[0], d = l[1];
      if (r != null && r[u] || r != null && r[d]) {
        var c;
        (c = r[d]) !== null && c !== void 0 || (r[d] = r == null ? void 0 : r[u]);
      }
    });
  }
  var i = H(H({}, n), r);
  return Object.keys(i).forEach(function(a) {
    i[a] === e[a] && delete i[a];
  }), i;
}
var Ht = typeof CSSINJS_STATISTIC < "u", ze = !0;
function We() {
  for (var t = arguments.length, e = new Array(t), n = 0; n < t; n++)
    e[n] = arguments[n];
  if (!Ht)
    return Object.assign.apply(Object, [{}].concat(e));
  ze = !1;
  var o = {};
  return e.forEach(function(r) {
    if (N(r) === "object") {
      var s = Object.keys(r);
      s.forEach(function(i) {
        Object.defineProperty(o, i, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return r[i];
          }
        });
      });
    }
  }), ze = !0, o;
}
var mt = {};
function gn() {
}
var mn = function(e) {
  var n, o = e, r = gn;
  return Ht && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(e, {
    get: function(i, a) {
      if (ze) {
        var l;
        (l = n) === null || l === void 0 || l.add(a);
      }
      return i[a];
    }
  }), r = function(i, a) {
    var l;
    mt[i] = {
      global: Array.from(n),
      component: H(H({}, (l = mt[i]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function pt(t, e, n) {
  if (typeof n == "function") {
    var o;
    return n(We(e, (o = e[t]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function pn(t) {
  return t === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(s) {
        return se(s);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(s) {
        return se(s);
      }).join(","), ")");
    }
  };
}
var bn = 1e3 * 60 * 10, yn = /* @__PURE__ */ function() {
  function t() {
    be(this, t), I(this, "map", /* @__PURE__ */ new Map()), I(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), I(this, "nextID", 0), I(this, "lastAccessBeat", /* @__PURE__ */ new Map()), I(this, "accessBeat", 0);
  }
  return ye(t, [{
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
      var o = this, r = n.map(function(s) {
        return s && N(s) === "object" ? "obj_".concat(o.getObjectID(s)) : "".concat(N(s), "_").concat(s);
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
        this.lastAccessBeat.forEach(function(r, s) {
          o - r > bn && (n.map.delete(s), n.lastAccessBeat.delete(s));
        }), this.accessBeat = 0;
      }
    }
  }]), t;
}(), bt = new yn();
function vn(t, e) {
  return g.useMemo(function() {
    var n = bt.get(e);
    if (n)
      return n;
    var o = t();
    return bt.set(e, o), o;
  }, e);
}
var xn = function() {
  return {};
};
function Sn(t) {
  var e = t.useCSP, n = e === void 0 ? xn : e, o = t.useToken, r = t.usePrefix, s = t.getResetStyles, i = t.getCommonStyle, a = t.getCompUnitless;
  function l(f, h, m, y) {
    var p = Array.isArray(f) ? f[0] : f;
    function v(P) {
      return "".concat(String(p)).concat(P.slice(0, 1).toUpperCase()).concat(P.slice(1));
    }
    var x = (y == null ? void 0 : y.unitless) || {}, R = typeof a == "function" ? a(f) : {}, b = H(H({}, R), {}, I({}, v("zIndexPopup"), !0));
    Object.keys(x).forEach(function(P) {
      b[v(P)] = x[P];
    });
    var C = H(H({}, y), {}, {
      unitless: b,
      prefixToken: v
    }), S = d(f, h, m, C), w = u(p, m, C);
    return function(P) {
      var k = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : P, E = S(P, k), j = de(E, 2), L = j[1], O = w(k), M = de(O, 2), $ = M[0], D = M[1];
      return [$, L, D];
    };
  }
  function u(f, h, m) {
    var y = m.unitless, p = m.injectStyle, v = p === void 0 ? !0 : p, x = m.prefixToken, R = m.ignore, b = function(w) {
      var P = w.rootCls, k = w.cssVar, E = k === void 0 ? {} : k, j = o(), L = j.realToken;
      return er({
        path: [f],
        prefix: E.prefix,
        key: E.key,
        unitless: y,
        ignore: R,
        token: L,
        scope: P
      }, function() {
        var O = pt(f, L, h), M = gt(f, L, O, {
          deprecatedTokens: m == null ? void 0 : m.deprecatedTokens
        });
        return Object.keys(O).forEach(function($) {
          M[x($)] = M[$], delete M[$];
        }), M;
      }), null;
    }, C = function(w) {
      var P = o(), k = P.cssVar;
      return [function(E) {
        return v && k ? /* @__PURE__ */ g.createElement(g.Fragment, null, /* @__PURE__ */ g.createElement(b, {
          rootCls: w,
          cssVar: k,
          component: f
        }), E) : E;
      }, k == null ? void 0 : k.key];
    };
    return C;
  }
  function d(f, h, m) {
    var y = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = Array.isArray(f) ? f : [f, f], v = de(p, 1), x = v[0], R = p.join("-"), b = t.layer || {
      name: "antd"
    };
    return function(C) {
      var S = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : C, w = o(), P = w.theme, k = w.realToken, E = w.hashId, j = w.token, L = w.cssVar, O = r(), M = O.rootPrefixCls, $ = O.iconPrefixCls, D = n(), A = L ? "css" : "js", V = vn(function() {
        var W = /* @__PURE__ */ new Set();
        return L && Object.keys(y.unitless || {}).forEach(function(K) {
          W.add(Ie(K, L.prefix)), W.add(Ie(K, dt(x, L.prefix)));
        }), ln(A, W);
      }, [A, x, L == null ? void 0 : L.prefix]), G = pn(A), ee = G.max, ie = G.min, q = {
        theme: P,
        token: j,
        hashId: E,
        nonce: function() {
          return D.nonce;
        },
        clientOnly: y.clientOnly,
        layer: b,
        // antd is always at top of styles
        order: y.order || -999
      };
      typeof s == "function" && Je(H(H({}, q), {}, {
        clientOnly: !1,
        path: ["Shared", M]
      }), function() {
        return s(j, {
          prefix: {
            rootPrefixCls: M,
            iconPrefixCls: $
          },
          csp: D
        });
      });
      var Oe = Je(H(H({}, q), {}, {
        path: [R, C, $]
      }), function() {
        if (y.injectStyle === !1)
          return [];
        var W = mn(j), K = W.token, te = W.flush, X = pt(x, k, m), re = ".".concat(C), Ke = gt(x, k, X, {
          deprecatedTokens: y.deprecatedTokens
        });
        L && X && N(X) === "object" && Object.keys(X).forEach(function(Ye) {
          X[Ye] = "var(".concat(Ie(Ye, dt(x, L.prefix)), ")");
        });
        var qe = We(K, {
          componentCls: re,
          prefixCls: C,
          iconCls: ".".concat($),
          antCls: ".".concat(M),
          calc: V,
          // @ts-ignore
          max: ee,
          // @ts-ignore
          min: ie
        }, L ? X : Ke), Ft = h(qe, {
          hashId: E,
          prefixCls: C,
          rootPrefixCls: M,
          iconPrefixCls: $
        });
        te(x, Ke);
        var Nt = typeof i == "function" ? i(qe, C, S, y.resetFont) : null;
        return [y.resetStyle === !1 ? null : Nt, Ft];
      });
      return [Oe, E];
    };
  }
  function c(f, h, m) {
    var y = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = d(f, h, m, H({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, y)), v = function(R) {
      var b = R.prefixCls, C = R.rootCls, S = C === void 0 ? b : C;
      return p(b, S), null;
    };
    return v;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: c,
    genComponentStyleHook: d
  };
}
const Cn = {
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
}, wn = Object.assign(Object.assign({}, Cn), {
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
}), B = Math.round;
function Le(t, e) {
  const n = t.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = e(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const yt = (t, e, n) => n === 0 ? t : t / 100;
function ne(t, e) {
  const n = e || 255;
  return t > n ? n : t < 0 ? 0 : t;
}
class U {
  constructor(e) {
    I(this, "isValid", !0), I(this, "r", 0), I(this, "g", 0), I(this, "b", 0), I(this, "a", 1), I(this, "_h", void 0), I(this, "_s", void 0), I(this, "_l", void 0), I(this, "_v", void 0), I(this, "_max", void 0), I(this, "_min", void 0), I(this, "_brightness", void 0);
    function n(o) {
      return o[0] in e && o[1] in e && o[2] in e;
    }
    if (e) if (typeof e == "string") {
      let r = function(s) {
        return o.startsWith(s);
      };
      const o = e.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (e instanceof U)
      this.r = e.r, this.g = e.g, this.b = e.b, this.a = e.a, this._h = e._h, this._s = e._s, this._l = e._l, this._v = e._v;
    else if (n("rgb"))
      this.r = ne(e.r), this.g = ne(e.g), this.b = ne(e.b), this.a = typeof e.a == "number" ? ne(e.a, 1) : 1;
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
    function e(s) {
      const i = s / 255;
      return i <= 0.03928 ? i / 12.92 : Math.pow((i + 0.055) / 1.055, 2.4);
    }
    const n = e(this.r), o = e(this.g), r = e(this.b);
    return 0.2126 * n + 0.7152 * o + 0.0722 * r;
  }
  getHue() {
    if (typeof this._h > "u") {
      const e = this.getMax() - this.getMin();
      e === 0 ? this._h = 0 : this._h = B(60 * (this.r === this.getMax() ? (this.g - this.b) / e + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / e + 2 : (this.r - this.g) / e + 4));
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
    const o = this._c(e), r = n / 100, s = (a) => (o[a] - this[a]) * r + this[a], i = {
      r: B(s("r")),
      g: B(s("g")),
      b: B(s("b")),
      a: B(s("a") * 100) / 100
    };
    return this._c(i);
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
    const n = this._c(e), o = this.a + n.a * (1 - this.a), r = (s) => B((this[s] * this.a + n[s] * n.a * (1 - this.a)) / o);
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
      const s = B(this.a * 255).toString(16);
      e += s.length === 2 ? s : "0" + s;
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
    const e = this.getHue(), n = B(this.getSaturation() * 100), o = B(this.getLightness() * 100);
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
    return r[e] = ne(n, o), r;
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
    function o(r, s) {
      return parseInt(n[r] + n[s || r], 16);
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
      const f = B(o * 255);
      this.r = f, this.g = f, this.b = f;
    }
    let s = 0, i = 0, a = 0;
    const l = e / 60, u = (1 - Math.abs(2 * o - 1)) * n, d = u * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (s = u, i = d) : l >= 1 && l < 2 ? (s = d, i = u) : l >= 2 && l < 3 ? (i = u, a = d) : l >= 3 && l < 4 ? (i = d, a = u) : l >= 4 && l < 5 ? (s = d, a = u) : l >= 5 && l < 6 && (s = u, a = d);
    const c = o - u / 2;
    this.r = B((s + c) * 255), this.g = B((i + c) * 255), this.b = B((a + c) * 255);
  }
  fromHsv({
    h: e,
    s: n,
    v: o,
    a: r
  }) {
    this._h = e % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const s = B(o * 255);
    if (this.r = s, this.g = s, this.b = s, n <= 0)
      return;
    const i = e / 60, a = Math.floor(i), l = i - a, u = B(o * (1 - n) * 255), d = B(o * (1 - n * l) * 255), c = B(o * (1 - n * (1 - l)) * 255);
    switch (a) {
      case 0:
        this.g = c, this.b = u;
        break;
      case 1:
        this.r = d, this.b = u;
        break;
      case 2:
        this.r = u, this.b = c;
        break;
      case 3:
        this.r = u, this.g = d;
        break;
      case 4:
        this.r = c, this.g = u;
        break;
      case 5:
      default:
        this.g = u, this.b = d;
        break;
    }
  }
  fromHsvString(e) {
    const n = Le(e, yt);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(e) {
    const n = Le(e, yt);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(e) {
    const n = Le(e, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? B(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function $e(t) {
  return t >= 0 && t <= 255;
}
function ae(t, e) {
  const {
    r: n,
    g: o,
    b: r,
    a: s
  } = new U(t).toRgb();
  if (s < 1)
    return t;
  const {
    r: i,
    g: a,
    b: l
  } = new U(e).toRgb();
  for (let u = 0.01; u <= 1; u += 0.01) {
    const d = Math.round((n - i * (1 - u)) / u), c = Math.round((o - a * (1 - u)) / u), f = Math.round((r - l * (1 - u)) / u);
    if ($e(d) && $e(c) && $e(f))
      return new U({
        r: d,
        g: c,
        b: f,
        a: Math.round(u * 100) / 100
      }).toRgbString();
  }
  return new U({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var _n = function(t, e) {
  var n = {};
  for (var o in t) Object.prototype.hasOwnProperty.call(t, o) && e.indexOf(o) < 0 && (n[o] = t[o]);
  if (t != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(t); r < o.length; r++)
    e.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(t, o[r]) && (n[o[r]] = t[o[r]]);
  return n;
};
function Tn(t) {
  const {
    override: e
  } = t, n = _n(t, ["override"]), o = Object.assign({}, e);
  Object.keys(wn).forEach((f) => {
    delete o[f];
  });
  const r = Object.assign(Object.assign({}, n), o), s = 480, i = 576, a = 768, l = 992, u = 1200, d = 1600;
  if (r.motion === !1) {
    const f = "0s";
    r.motionDurationFast = f, r.motionDurationMid = f, r.motionDurationSlow = f;
  }
  return Object.assign(Object.assign(Object.assign({}, r), {
    // ============== Background ============== //
    colorFillContent: r.colorFillSecondary,
    colorFillContentHover: r.colorFill,
    colorFillAlter: r.colorFillQuaternary,
    colorBgContainerDisabled: r.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: r.colorBgContainer,
    colorSplit: ae(r.colorBorderSecondary, r.colorBgContainer),
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
    colorErrorOutline: ae(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: ae(r.colorWarningBg, r.colorBgContainer),
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
    controlOutline: ae(r.colorPrimaryBg, r.colorBgContainer),
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
    screenXLMax: d - 1,
    screenXXL: d,
    screenXXLMin: d,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new U("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new U("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new U("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const En = {
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
}, Mn = {
  motionBase: !0,
  motionUnit: !0
}, Pn = tr(He.defaultAlgorithm), On = {
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
}, Dt = (t, e, n) => {
  const o = n.getDerivativeToken(t), {
    override: r,
    ...s
  } = e;
  let i = {
    ...o,
    override: r
  };
  return i = Tn(i), s && Object.entries(s).forEach(([a, l]) => {
    const {
      theme: u,
      ...d
    } = l;
    let c = d;
    u && (c = Dt({
      ...i,
      ...d
    }, {
      override: d
    }, u)), i[a] = c;
  }), i;
};
function In() {
  const {
    token: t,
    hashed: e,
    theme: n = Pn,
    override: o,
    cssVar: r
  } = g.useContext(He._internalContext), [s, i, a] = rr(n, [He.defaultSeed, t], {
    salt: `${Fr}-${e || ""}`,
    override: o,
    getComputedToken: Dt,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: En,
      ignore: Mn,
      preserve: On
    }
  });
  return [n, a, e ? i : "", s, r];
}
const {
  genStyleHooks: Rn
} = Sn({
  usePrefix: () => {
    const {
      getPrefixCls: t,
      iconPrefixCls: e
    } = ge();
    return {
      iconPrefixCls: e,
      rootPrefixCls: t()
    };
  },
  useToken: () => {
    const [t, e, n, o, r] = In();
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
    } = ge();
    return t ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
});
function le(t) {
  return typeof t == "string";
}
const kn = (t, e, n, o) => {
  const r = _.useRef(""), [s, i] = _.useState(1), a = e && le(t);
  return fn(() => {
    !a && le(t) ? i(t.length) : le(t) && le(r.current) && t.indexOf(r.current) !== 0 && i(1), r.current = t;
  }, [t]), _.useEffect(() => {
    if (a && s < t.length) {
      const u = setTimeout(() => {
        i((d) => d + n);
      }, o);
      return () => {
        clearTimeout(u);
      };
    }
  }, [s, e, t]), [a ? t.slice(0, s) : t, a && s < t.length];
};
function jn(t) {
  return _.useMemo(() => {
    if (!t)
      return [!1, 0, 0, null];
    let e = {
      step: 1,
      interval: 50,
      // set default suffix is empty
      suffix: null
    };
    return typeof t == "object" && (e = {
      ...e,
      ...t
    }), [!0, e.step, e.interval, e.suffix];
  }, [t]);
}
const Ln = ({
  prefixCls: t
}) => /* @__PURE__ */ g.createElement("span", {
  className: `${t}-dot`
}, /* @__PURE__ */ g.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-1"
}), /* @__PURE__ */ g.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-2"
}), /* @__PURE__ */ g.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-3"
})), $n = (t) => {
  const {
    componentCls: e,
    paddingSM: n,
    padding: o
  } = t;
  return {
    [e]: {
      [`${e}-content`]: {
        // Shared: filled, outlined, shadow
        "&-filled,&-outlined,&-shadow": {
          padding: `${se(n)} ${se(o)}`,
          borderRadius: t.borderRadiusLG
        },
        // Filled:
        "&-filled": {
          backgroundColor: t.colorFillContent
        },
        // Outlined:
        "&-outlined": {
          border: `1px solid ${t.colorBorderSecondary}`
        },
        // Shadow:
        "&-shadow": {
          boxShadow: t.boxShadowTertiary
        }
      }
    }
  };
}, Bn = (t) => {
  const {
    componentCls: e,
    fontSize: n,
    lineHeight: o,
    paddingSM: r,
    padding: s,
    calc: i
  } = t, a = i(n).mul(o).div(2).add(r).equal(), l = `${e}-content`;
  return {
    [e]: {
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
        borderStartStartRadius: t.borderRadiusXS
      },
      [`&-end ${l}-corner`]: {
        borderStartEndRadius: t.borderRadiusXS
      }
    }
  };
}, Hn = (t) => {
  const {
    componentCls: e,
    padding: n
  } = t;
  return {
    [`${e}-list`]: {
      display: "flex",
      flexDirection: "column",
      gap: n,
      overflowY: "auto",
      "&::-webkit-scrollbar": {
        width: 8,
        backgroundColor: "transparent"
      },
      "&::-webkit-scrollbar-thumb": {
        backgroundColor: t.colorTextTertiary,
        borderRadius: t.borderRadiusSM
      },
      // For Firefox
      "&": {
        scrollbarWidth: "thin",
        scrollbarColor: `${t.colorTextTertiary} transparent`
      }
    }
  };
}, Dn = new wt("loadingMove", {
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
}), An = new wt("cursorBlink", {
  "0%": {
    opacity: 1
  },
  "50%": {
    opacity: 0
  },
  "100%": {
    opacity: 1
  }
}), zn = (t) => {
  const {
    componentCls: e,
    fontSize: n,
    lineHeight: o,
    paddingSM: r,
    colorText: s,
    calc: i
  } = t;
  return {
    [e]: {
      display: "flex",
      columnGap: r,
      [`&${e}-end`]: {
        justifyContent: "end",
        flexDirection: "row-reverse",
        [`& ${e}-content-wrapper`]: {
          alignItems: "flex-end"
        }
      },
      [`&${e}-rtl`]: {
        direction: "rtl"
      },
      [`&${e}-typing ${e}-content:last-child::after`]: {
        content: '"|"',
        fontWeight: 900,
        userSelect: "none",
        opacity: 1,
        marginInlineStart: "0.1em",
        animationName: An,
        animationDuration: "0.8s",
        animationIterationCount: "infinite",
        animationTimingFunction: "linear"
      },
      // ============================ Avatar =============================
      [`& ${e}-avatar`]: {
        display: "inline-flex",
        justifyContent: "center",
        alignSelf: "flex-start"
      },
      // ======================== Header & Footer ========================
      [`& ${e}-header, & ${e}-footer`]: {
        fontSize: n,
        lineHeight: o,
        color: t.colorText
      },
      [`& ${e}-header`]: {
        marginBottom: t.paddingXXS
      },
      [`& ${e}-footer`]: {
        marginTop: r
      },
      // =========================== Content =============================
      [`& ${e}-content-wrapper`]: {
        flex: "auto",
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        minWidth: 0,
        maxWidth: "100%"
      },
      [`& ${e}-content`]: {
        position: "relative",
        boxSizing: "border-box",
        minWidth: 0,
        maxWidth: "100%",
        color: s,
        fontSize: t.fontSize,
        lineHeight: t.lineHeight,
        minHeight: i(r).mul(2).add(i(o).mul(n)).equal(),
        wordBreak: "break-word",
        [`& ${e}-dot`]: {
          position: "relative",
          height: "100%",
          display: "flex",
          alignItems: "center",
          columnGap: t.marginXS,
          padding: `0 ${se(t.paddingXXS)}`,
          "&-item": {
            backgroundColor: t.colorPrimary,
            borderRadius: "100%",
            width: 4,
            height: 4,
            animationName: Dn,
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
}, Fn = () => ({}), At = Rn("Bubble", (t) => {
  const e = We(t, {});
  return [zn(e), Hn(e), $n(e), Bn(e)];
}, Fn), zt = /* @__PURE__ */ g.createContext({}), Nn = (t, e) => {
  const {
    prefixCls: n,
    className: o,
    rootClassName: r,
    style: s,
    classNames: i = {},
    styles: a = {},
    avatar: l,
    placement: u = "start",
    loading: d = !1,
    loadingRender: c,
    typing: f,
    content: h = "",
    messageRender: m,
    variant: y = "filled",
    shape: p,
    onTypingComplete: v,
    header: x,
    footer: R,
    _key: b,
    ...C
  } = t, {
    onUpdate: S
  } = g.useContext(zt), w = g.useRef(null);
  g.useImperativeHandle(e, () => ({
    nativeElement: w.current
  }));
  const {
    direction: P,
    getPrefixCls: k
  } = ge(), E = k("bubble", n), j = Qr("bubble"), [L, O, M, $] = jn(f), [D, A] = kn(h, L, O, M);
  g.useEffect(() => {
    S == null || S();
  }, [D]);
  const V = g.useRef(!1);
  g.useEffect(() => {
    !A && !d ? V.current || (V.current = !0, v == null || v()) : V.current = !1;
  }, [A, d]);
  const [G, ee, ie] = At(E), q = Y(E, r, j.className, o, ee, ie, `${E}-${u}`, {
    [`${E}-rtl`]: P === "rtl",
    [`${E}-typing`]: A && !d && !m && !$
  }), Oe = g.useMemo(() => /* @__PURE__ */ g.isValidElement(l) ? l : /* @__PURE__ */ g.createElement(Zt, l), [l]), W = g.useMemo(() => m ? m(D) : D, [D, m]), K = (re) => typeof re == "function" ? re(D, {
    key: b
  }) : re;
  let te;
  d ? te = c ? c() : /* @__PURE__ */ g.createElement(Ln, {
    prefixCls: E
  }) : te = /* @__PURE__ */ g.createElement(g.Fragment, null, W, A && $);
  let X = /* @__PURE__ */ g.createElement("div", {
    style: {
      ...j.styles.content,
      ...a.content
    },
    className: Y(`${E}-content`, `${E}-content-${y}`, p && `${E}-content-${p}`, j.classNames.content, i.content)
  }, te);
  return (x || R) && (X = /* @__PURE__ */ g.createElement("div", {
    className: `${E}-content-wrapper`
  }, x && /* @__PURE__ */ g.createElement("div", {
    className: Y(`${E}-header`, j.classNames.header, i.header),
    style: {
      ...j.styles.header,
      ...a.header
    }
  }, K(x)), X, R && /* @__PURE__ */ g.createElement("div", {
    className: Y(`${E}-footer`, j.classNames.footer, i.footer),
    style: {
      ...j.styles.footer,
      ...a.footer
    }
  }, K(R)))), G(/* @__PURE__ */ g.createElement("div", Z({
    style: {
      ...j.style,
      ...s
    },
    className: q
  }, C, {
    ref: w
  }), l && /* @__PURE__ */ g.createElement("div", {
    style: {
      ...j.styles.avatar,
      ...a.avatar
    },
    className: Y(`${E}-avatar`, j.classNames.avatar, i.avatar)
  }, Oe), X));
}, Ue = /* @__PURE__ */ g.forwardRef(Nn);
function Xn(t, e) {
  const n = _.useCallback((o, r) => typeof e == "function" ? e(o, r) : e ? e[o.role] || {} : {}, [e]);
  return _.useMemo(() => (t || []).map((o, r) => {
    const s = o.key ?? `preset_${r}`;
    return {
      ...n(o, r),
      ...o,
      key: s
    };
  }), [t, n]);
}
const Vn = ({
  _key: t,
  ...e
}, n) => /* @__PURE__ */ _.createElement(Ue, Z({}, e, {
  _key: t,
  ref: (o) => {
    var r;
    o ? n.current[t] = o : (r = n.current) == null || delete r[t];
  }
})), Wn = /* @__PURE__ */ _.memo(/* @__PURE__ */ _.forwardRef(Vn)), Un = 1, Gn = (t, e) => {
  const {
    prefixCls: n,
    rootClassName: o,
    className: r,
    items: s,
    autoScroll: i = !0,
    roles: a,
    onScroll: l,
    ...u
  } = t, d = Kr(u, {
    attr: !0,
    aria: !0
  }), c = _.useRef(null), f = _.useRef({}), {
    getPrefixCls: h
  } = ge(), m = h("bubble", n), y = `${m}-list`, [p, v, x] = At(m), [R, b] = _.useState(!1);
  _.useEffect(() => (b(!0), () => {
    b(!1);
  }), []);
  const C = Xn(s, a), [S, w] = _.useState(!0), [P, k] = _.useState(0), E = (O) => {
    const M = O.target;
    w(M.scrollHeight - Math.abs(M.scrollTop) - M.clientHeight <= Un), l == null || l(O);
  };
  _.useEffect(() => {
    i && c.current && S && c.current.scrollTo({
      top: c.current.scrollHeight
    });
  }, [P]), _.useEffect(() => {
    var O;
    if (i) {
      const M = (O = C[C.length - 2]) == null ? void 0 : O.key, $ = f.current[M];
      if ($) {
        const {
          nativeElement: D
        } = $, {
          top: A,
          bottom: V
        } = D.getBoundingClientRect(), {
          top: G,
          bottom: ee
        } = c.current.getBoundingClientRect();
        A < ee && V > G && (k((q) => q + 1), w(!0));
      }
    }
  }, [C.length]), _.useImperativeHandle(e, () => ({
    nativeElement: c.current,
    scrollTo: ({
      key: O,
      offset: M,
      behavior: $ = "smooth",
      block: D
    }) => {
      if (typeof M == "number")
        c.current.scrollTo({
          top: M,
          behavior: $
        });
      else if (O !== void 0) {
        const A = f.current[O];
        if (A) {
          const V = C.findIndex((G) => G.key === O);
          w(V === C.length - 1), A.nativeElement.scrollIntoView({
            behavior: $,
            block: D
          });
        }
      }
    }
  }));
  const j = cn(() => {
    i && k((O) => O + 1);
  }), L = _.useMemo(() => ({
    onUpdate: j
  }), []);
  return p(/* @__PURE__ */ _.createElement(zt.Provider, {
    value: L
  }, /* @__PURE__ */ _.createElement("div", Z({}, d, {
    className: Y(y, o, r, v, x, {
      [`${y}-reach-end`]: S
    }),
    ref: c,
    onScroll: E
  }), C.map(({
    key: O,
    ...M
  }) => /* @__PURE__ */ _.createElement(Wn, Z({}, M, {
    key: O,
    _key: O,
    ref: f,
    typing: R ? M.typing : !1
  }))))));
}, Kn = /* @__PURE__ */ _.forwardRef(Gn);
Ue.List = Kn;
const qn = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Yn(t) {
  return t ? Object.keys(t).reduce((e, n) => {
    const o = t[n];
    return e[n] = Qn(n, o), e;
  }, {}) : {};
}
function Qn(t, e) {
  return typeof e == "number" && !qn.includes(t) ? e + "px" : e;
}
function Fe(t) {
  const e = [], n = t.cloneNode(!1);
  if (t._reactElement) {
    const r = g.Children.toArray(t._reactElement.props.children).map((s) => {
      if (g.isValidElement(s) && s.props.__slot__) {
        const {
          portals: i,
          clonedElement: a
        } = Fe(s.props.el);
        return g.cloneElement(s, {
          ...s.props,
          el: a,
          children: [...g.Children.toArray(s.props.children), ...i]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(Be(g.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: r
    }), n)), {
      clonedElement: n,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((r) => {
    t.getEventListeners(r).forEach(({
      listener: i,
      type: a,
      useCapture: l
    }) => {
      n.addEventListener(a, i, l);
    });
  });
  const o = Array.from(t.childNodes);
  for (let r = 0; r < o.length; r++) {
    const s = o[r];
    if (s.nodeType === 1) {
      const {
        clonedElement: i,
        portals: a
      } = Fe(s);
      e.push(...a), n.appendChild(i);
    } else s.nodeType === 3 && n.appendChild(s.cloneNode());
  }
  return {
    clonedElement: n,
    portals: e
  };
}
function Jn(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const vt = Vt(({
  slot: t,
  clone: e,
  className: n,
  style: o,
  observeAttributes: r
}, s) => {
  const i = St(), [a, l] = Wt([]), {
    forceClone: u
  } = Qt(), d = u ? !0 : e;
  return Ut(() => {
    var y;
    if (!i.current || !t)
      return;
    let c = t;
    function f() {
      let p = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (p = c.children[0], p.tagName.toLowerCase() === "react-portal-target" && p.children[0] && (p = p.children[0])), Jn(s, p), n && p.classList.add(...n.split(" ")), o) {
        const v = Yn(o);
        Object.keys(v).forEach((x) => {
          p.style[x] = v[x];
        });
      }
    }
    let h = null, m = null;
    if (d && window.MutationObserver) {
      let p = function() {
        var b, C, S;
        (b = i.current) != null && b.contains(c) && ((C = i.current) == null || C.removeChild(c));
        const {
          portals: x,
          clonedElement: R
        } = Fe(t);
        c = R, l(x), c.style.display = "contents", m && clearTimeout(m), m = setTimeout(() => {
          f();
        }, 50), (S = i.current) == null || S.appendChild(c);
      };
      p();
      const v = gr(() => {
        p(), h == null || h.disconnect(), h == null || h.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      h = new window.MutationObserver(v), h.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", f(), (y = i.current) == null || y.appendChild(c);
    return () => {
      var p, v;
      c.style.display = "", (p = i.current) != null && p.contains(c) && ((v = i.current) == null || v.removeChild(c)), h == null || h.disconnect();
    };
  }, [t, d, n, o, s, r, u]), g.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...a);
});
function xt(t) {
  const e = St(t);
  return e.current = t, Gt((...n) => {
    var o;
    return (o = e.current) == null ? void 0 : o.call(e, ...n);
  }, []);
}
const Zn = ({
  children: t,
  ...e
}) => /* @__PURE__ */ z.jsx(z.Fragment, {
  children: t(e)
});
function eo(t) {
  return g.createElement(Zn, {
    children: t
  });
}
function Ge(t, e, n) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((r, s) => {
      var u, d;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const i = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((u = r.props) == null ? void 0 : u.key) ?? (n ? `${n}-${s}` : `${s}`)
      }) : {
        ...r.props,
        key: ((d = r.props) == null ? void 0 : d.key) ?? (n ? `${n}-${s}` : `${s}`)
      };
      let a = i;
      Object.keys(r.slots).forEach((c) => {
        if (!r.slots[c] || !(r.slots[c] instanceof Element) && !r.slots[c].el)
          return;
        const f = c.split(".");
        f.forEach((x, R) => {
          a[x] || (a[x] = {}), R !== f.length - 1 && (a = i[x]);
        });
        const h = r.slots[c];
        let m, y, p = (e == null ? void 0 : e.clone) ?? !1, v = e == null ? void 0 : e.forceClone;
        h instanceof Element ? m = h : (m = h.el, y = h.callback, p = h.clone ?? p, v = h.forceClone ?? v), v = v ?? !!y, a[f[f.length - 1]] = m ? y ? (...x) => (y(f[f.length - 1], x), /* @__PURE__ */ z.jsx(Qe, {
          ...r.ctx,
          params: x,
          forceClone: v,
          children: /* @__PURE__ */ z.jsx(vt, {
            slot: m,
            clone: p
          })
        })) : eo((x) => /* @__PURE__ */ z.jsx(Qe, {
          ...r.ctx,
          forceClone: v,
          children: /* @__PURE__ */ z.jsx(vt, {
            ...x,
            slot: m,
            clone: p
          })
        })) : a[f[f.length - 1]], a = i;
      });
      const l = (e == null ? void 0 : e.children) || "children";
      return r[l] ? i[l] = Ge(r[l], e, `${s}`) : e != null && e.children && (i[l] = void 0, Reflect.deleteProperty(i, l)), i;
    });
}
const {
  useItems: to,
  withItemsContextProvider: ro,
  ItemHandler: mo
} = Ct("antdx-bubble.list-items"), {
  useItems: no,
  withItemsContextProvider: oo,
  ItemHandler: po
} = Ct("antdx-bubble.list-roles");
function so(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function io(t, e = !1) {
  try {
    if (Ne(t))
      return t;
    if (e && !so(t))
      return;
    if (typeof t == "string") {
      let n = t.trim();
      return n.startsWith(";") && (n = n.slice(1)), n.endsWith(";") && (n = n.slice(0, -1)), new Function(`return (...args) => (${n})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function ao(t, e) {
  return he(() => io(t, e), [t, e]);
}
function lo(t, e) {
  return e((o, r) => Ne(o) ? r ? (...s) => J(r) && r.unshift ? o(...t, ...s) : o(...s, ...t) : o(...t) : o);
}
const co = Symbol();
function uo(t, e) {
  return lo(e, (n) => {
    var o, r;
    return {
      ...t,
      avatar: Ne(t.avatar) ? n(t.avatar) : J(t.avatar) ? {
        ...t.avatar,
        icon: n((o = t.avatar) == null ? void 0 : o.icon),
        src: n((r = t.avatar) == null ? void 0 : r.src)
      } : t.avatar,
      footer: n(t.footer, {
        unshift: !0
      }),
      header: n(t.header, {
        unshift: !0
      }),
      loadingRender: n(t.loadingRender, !0),
      messageRender: n(t.messageRender, !0)
    };
  });
}
function fo({
  roles: t,
  preProcess: e,
  postProcess: n
}, o = []) {
  const r = ao(t), s = xt(e), i = xt(n), {
    items: {
      roles: a
    }
  } = no(), l = he(() => {
    var d;
    return t || ((d = Ge(a, {
      clone: !0,
      forceClone: !0
    })) == null ? void 0 : d.reduce((c, f) => (f.role !== void 0 && (c[f.role] = f), c), {}));
  }, [a, t]), u = he(() => (d, c) => {
    const f = c ?? d[co], h = s(d, f) || d;
    if (h.role && (l || {})[h.role])
      return uo((l || {})[h.role], [h, f]);
    let m;
    return m = i(h, f), m || {
      messageRender(y) {
        return /* @__PURE__ */ z.jsx(z.Fragment, {
          children: J(y) ? JSON.stringify(y) : y
        });
      }
    };
  }, [l, i, s, ...o]);
  return r || u;
}
const bo = zr(oo(["roles"], ro(["items", "default"], ({
  items: t,
  roles: e,
  children: n,
  ...o
}) => {
  const {
    items: r
  } = to(), s = fo({
    roles: e
  }), i = r.items.length > 0 ? r.items : r.default;
  return /* @__PURE__ */ z.jsxs(z.Fragment, {
    children: [/* @__PURE__ */ z.jsx("div", {
      style: {
        display: "none"
      },
      children: n
    }), /* @__PURE__ */ z.jsx(Ue.List, {
      ...o,
      items: he(() => t || Ge(i), [t, i]),
      roles: s
    })]
  });
})));
export {
  bo as BubbleList,
  bo as default
};
