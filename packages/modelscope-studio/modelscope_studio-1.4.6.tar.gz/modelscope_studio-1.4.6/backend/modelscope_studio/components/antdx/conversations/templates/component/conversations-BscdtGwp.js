import { i as rr, a as ke, r as nr, Z as te, g as or, c as Q, b as wt } from "./Index-drdcBF3u.js";
const X = window.ms_globals.React, x = window.ms_globals.React, Zt = window.ms_globals.React.forwardRef, Jt = window.ms_globals.React.useRef, Yt = window.ms_globals.React.useState, er = window.ms_globals.React.useEffect, tr = window.ms_globals.React.version, je = window.ms_globals.React.useMemo, Ie = window.ms_globals.ReactDOM.createPortal, ir = window.ms_globals.internalContext.useContextPropsContext, Le = window.ms_globals.internalContext.ContextPropsProvider, Tt = window.ms_globals.createItemsContext.createItemsContext, sr = window.ms_globals.antd.ConfigProvider, Re = window.ms_globals.antd.theme, Pt = window.ms_globals.antd.Typography, ar = window.ms_globals.antd.Dropdown, lr = window.ms_globals.antdIcons.EllipsisOutlined, oe = window.ms_globals.antdCssinjs.unit, Se = window.ms_globals.antdCssinjs.token2CSSVar, Qe = window.ms_globals.antdCssinjs.useStyleRegister, cr = window.ms_globals.antdCssinjs.useCSSVarRegister, ur = window.ms_globals.antdCssinjs.createTheme, fr = window.ms_globals.antdCssinjs.useCacheToken;
var dr = /\s/;
function hr(t) {
  for (var e = t.length; e-- && dr.test(t.charAt(e)); )
    ;
  return e;
}
var gr = /^\s+/;
function mr(t) {
  return t && t.slice(0, hr(t) + 1).replace(gr, "");
}
var Ze = NaN, pr = /^[-+]0x[0-9a-f]+$/i, br = /^0b[01]+$/i, yr = /^0o[0-7]+$/i, vr = parseInt;
function Je(t) {
  if (typeof t == "number")
    return t;
  if (rr(t))
    return Ze;
  if (ke(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = ke(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = mr(t);
  var n = br.test(t);
  return n || yr.test(t) ? vr(t.slice(2), n ? 2 : 8) : pr.test(t) ? Ze : +t;
}
var Ce = function() {
  return nr.Date.now();
}, xr = "Expected a function", Sr = Math.max, Cr = Math.min;
function _r(t, e, n) {
  var o, r, i, s, a, l, c = 0, f = !1, u = !1, d = !0;
  if (typeof t != "function")
    throw new TypeError(xr);
  e = Je(e) || 0, ke(n) && (f = !!n.leading, u = "maxWait" in n, i = u ? Sr(Je(n.maxWait) || 0, e) : i, d = "trailing" in n ? !!n.trailing : d);
  function g(S) {
    var P = o, M = r;
    return o = r = void 0, c = S, s = t.apply(M, P), s;
  }
  function m(S) {
    return c = S, a = setTimeout(v, e), f ? g(S) : s;
  }
  function y(S) {
    var P = S - l, M = S - c, E = e - P;
    return u ? Cr(E, i - M) : E;
  }
  function h(S) {
    var P = S - l, M = S - c;
    return l === void 0 || P >= e || P < 0 || u && M >= i;
  }
  function v() {
    var S = Ce();
    if (h(S))
      return p(S);
    a = setTimeout(v, y(S));
  }
  function p(S) {
    return a = void 0, d && o ? g(S) : (o = r = void 0, s);
  }
  function T() {
    a !== void 0 && clearTimeout(a), c = 0, o = l = r = a = void 0;
  }
  function b() {
    return a === void 0 ? s : p(Ce());
  }
  function C() {
    var S = Ce(), P = h(S);
    if (o = arguments, r = this, l = S, P) {
      if (a === void 0)
        return m(l);
      if (u)
        return clearTimeout(a), a = setTimeout(v, e), g(l);
    }
    return a === void 0 && (a = setTimeout(v, e)), s;
  }
  return C.cancel = T, C.flush = b, C;
}
var Ot = {
  exports: {}
}, se = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var wr = x, Tr = Symbol.for("react.element"), Pr = Symbol.for("react.fragment"), Or = Object.prototype.hasOwnProperty, Mr = wr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Er = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Mt(t, e, n) {
  var o, r = {}, i = null, s = null;
  n !== void 0 && (i = "" + n), e.key !== void 0 && (i = "" + e.key), e.ref !== void 0 && (s = e.ref);
  for (o in e) Or.call(e, o) && !Er.hasOwnProperty(o) && (r[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) r[o] === void 0 && (r[o] = e[o]);
  return {
    $$typeof: Tr,
    type: t,
    key: i,
    ref: s,
    props: r,
    _owner: Mr.current
  };
}
se.Fragment = Pr;
se.jsx = Mt;
se.jsxs = Mt;
Ot.exports = se;
var I = Ot.exports;
const {
  SvelteComponent: jr,
  assign: Ye,
  binding_callbacks: et,
  check_outros: Ir,
  children: Et,
  claim_element: jt,
  claim_space: kr,
  component_subscribe: tt,
  compute_slots: Lr,
  create_slot: Rr,
  detach: U,
  element: It,
  empty: rt,
  exclude_internal_props: nt,
  get_all_dirty_from_scope: $r,
  get_slot_changes: Dr,
  group_outros: Hr,
  init: Ar,
  insert_hydration: re,
  safe_not_equal: Br,
  set_custom_element_data: kt,
  space: zr,
  transition_in: ne,
  transition_out: $e,
  update_slot_base: Fr
} = window.__gradio__svelte__internal, {
  beforeUpdate: Xr,
  getContext: Vr,
  onDestroy: Nr,
  setContext: Gr
} = window.__gradio__svelte__internal;
function ot(t) {
  let e, n;
  const o = (
    /*#slots*/
    t[7].default
  ), r = Rr(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = It("svelte-slot"), r && r.c(), this.h();
    },
    l(i) {
      e = jt(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = Et(e);
      r && r.l(s), s.forEach(U), this.h();
    },
    h() {
      kt(e, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      re(i, e, s), r && r.m(e, null), t[9](e), n = !0;
    },
    p(i, s) {
      r && r.p && (!n || s & /*$$scope*/
      64) && Fr(
        r,
        o,
        i,
        /*$$scope*/
        i[6],
        n ? Dr(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : $r(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      n || (ne(r, i), n = !0);
    },
    o(i) {
      $e(r, i), n = !1;
    },
    d(i) {
      i && U(e), r && r.d(i), t[9](null);
    }
  };
}
function Ur(t) {
  let e, n, o, r, i = (
    /*$$slots*/
    t[4].default && ot(t)
  );
  return {
    c() {
      e = It("react-portal-target"), n = zr(), i && i.c(), o = rt(), this.h();
    },
    l(s) {
      e = jt(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), Et(e).forEach(U), n = kr(s), i && i.l(s), o = rt(), this.h();
    },
    h() {
      kt(e, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      re(s, e, a), t[8](e), re(s, n, a), i && i.m(s, a), re(s, o, a), r = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && ne(i, 1)) : (i = ot(s), i.c(), ne(i, 1), i.m(o.parentNode, o)) : i && (Hr(), $e(i, 1, 1, () => {
        i = null;
      }), Ir());
    },
    i(s) {
      r || (ne(i), r = !0);
    },
    o(s) {
      $e(i), r = !1;
    },
    d(s) {
      s && (U(e), U(n), U(o)), t[8](null), i && i.d(s);
    }
  };
}
function it(t) {
  const {
    svelteInit: e,
    ...n
  } = t;
  return n;
}
function Wr(t, e, n) {
  let o, r, {
    $$slots: i = {},
    $$scope: s
  } = e;
  const a = Lr(i);
  let {
    svelteInit: l
  } = e;
  const c = te(it(e)), f = te();
  tt(t, f, (b) => n(0, o = b));
  const u = te();
  tt(t, u, (b) => n(1, r = b));
  const d = [], g = Vr("$$ms-gr-react-wrapper"), {
    slotKey: m,
    slotIndex: y,
    subSlotIndex: h
  } = or() || {}, v = l({
    parent: g,
    props: c,
    target: f,
    slot: u,
    slotKey: m,
    slotIndex: y,
    subSlotIndex: h,
    onDestroy(b) {
      d.push(b);
    }
  });
  Gr("$$ms-gr-react-wrapper", v), Xr(() => {
    c.set(it(e));
  }), Nr(() => {
    d.forEach((b) => b());
  });
  function p(b) {
    et[b ? "unshift" : "push"](() => {
      o = b, f.set(o);
    });
  }
  function T(b) {
    et[b ? "unshift" : "push"](() => {
      r = b, u.set(r);
    });
  }
  return t.$$set = (b) => {
    n(17, e = Ye(Ye({}, e), nt(b))), "svelteInit" in b && n(5, l = b.svelteInit), "$$scope" in b && n(6, s = b.$$scope);
  }, e = nt(e), [o, r, f, u, a, l, s, i, p, T];
}
class Kr extends jr {
  constructor(e) {
    super(), Ar(this, e, Wr, Ur, Br, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: io
} = window.__gradio__svelte__internal, st = window.ms_globals.rerender, _e = window.ms_globals.tree;
function qr(t, e = {}) {
  function n(o) {
    const r = te(), i = new Kr({
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
          }, l = s.parent ?? _e;
          return l.nodes = [...l.nodes, a], st({
            createPortal: Ie,
            node: _e
          }), s.onDestroy(() => {
            l.nodes = l.nodes.filter((c) => c.svelteInstance !== r), st({
              createPortal: Ie,
              node: _e
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
const Qr = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Zr(t) {
  return t ? Object.keys(t).reduce((e, n) => {
    const o = t[n];
    return e[n] = Jr(n, o), e;
  }, {}) : {};
}
function Jr(t, e) {
  return typeof e == "number" && !Qr.includes(t) ? e + "px" : e;
}
function De(t) {
  const e = [], n = t.cloneNode(!1);
  if (t._reactElement) {
    const r = x.Children.toArray(t._reactElement.props.children).map((i) => {
      if (x.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = De(i.props.el);
        return x.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...x.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(Ie(x.cloneElement(t._reactElement, {
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
      } = De(i);
      e.push(...a), n.appendChild(s);
    } else i.nodeType === 3 && n.appendChild(i.cloneNode());
  }
  return {
    clonedElement: n,
    portals: e
  };
}
function Yr(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const Z = Zt(({
  slot: t,
  clone: e,
  className: n,
  style: o,
  observeAttributes: r
}, i) => {
  const s = Jt(), [a, l] = Yt([]), {
    forceClone: c
  } = ir(), f = c ? !0 : e;
  return er(() => {
    var y;
    if (!s.current || !t)
      return;
    let u = t;
    function d() {
      let h = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (h = u.children[0], h.tagName.toLowerCase() === "react-portal-target" && h.children[0] && (h = h.children[0])), Yr(i, h), n && h.classList.add(...n.split(" ")), o) {
        const v = Zr(o);
        Object.keys(v).forEach((p) => {
          h.style[p] = v[p];
        });
      }
    }
    let g = null, m = null;
    if (f && window.MutationObserver) {
      let h = function() {
        var b, C, S;
        (b = s.current) != null && b.contains(u) && ((C = s.current) == null || C.removeChild(u));
        const {
          portals: p,
          clonedElement: T
        } = De(t);
        u = T, l(p), u.style.display = "contents", m && clearTimeout(m), m = setTimeout(() => {
          d();
        }, 50), (S = s.current) == null || S.appendChild(u);
      };
      h();
      const v = _r(() => {
        h(), g == null || g.disconnect(), g == null || g.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      g = new window.MutationObserver(v), g.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", d(), (y = s.current) == null || y.appendChild(u);
    return () => {
      var h, v;
      u.style.display = "", (h = s.current) != null && h.contains(u) && ((v = s.current) == null || v.removeChild(u)), g == null || g.disconnect();
    };
  }, [t, f, n, o, i, r, c]), x.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), en = "1.6.0";
function J() {
  return J = Object.assign ? Object.assign.bind() : function(t) {
    for (var e = 1; e < arguments.length; e++) {
      var n = arguments[e];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (t[o] = n[o]);
    }
    return t;
  }, J.apply(null, arguments);
}
function A(t) {
  "@babel/helpers - typeof";
  return A = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, A(t);
}
function tn(t, e) {
  if (A(t) != "object" || !t) return t;
  var n = t[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(t, e);
    if (A(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function Lt(t) {
  var e = tn(t, "string");
  return A(e) == "symbol" ? e : e + "";
}
function O(t, e, n) {
  return (e = Lt(e)) in t ? Object.defineProperty(t, e, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : t[e] = n, t;
}
function at(t, e) {
  var n = Object.keys(t);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(t);
    e && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(t, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function L(t) {
  for (var e = 1; e < arguments.length; e++) {
    var n = arguments[e] != null ? arguments[e] : {};
    e % 2 ? at(Object(n), !0).forEach(function(o) {
      O(t, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(n)) : at(Object(n)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return t;
}
var rn = `accept acceptCharset accessKey action allowFullScreen allowTransparency
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
    summary tabIndex target title type useMap value width wmode wrap`, nn = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, on = "".concat(rn, " ").concat(nn).split(/[\s\n]+/), sn = "aria-", an = "data-";
function lt(t, e) {
  return t.indexOf(e) === 0;
}
function Rt(t) {
  var e = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, n;
  e === !1 ? n = {
    aria: !0,
    data: !0,
    attr: !0
  } : e === !0 ? n = {
    aria: !0
  } : n = L({}, e);
  var o = {};
  return Object.keys(t).forEach(function(r) {
    // Aria
    (n.aria && (r === "role" || lt(r, sn)) || // Data
    n.data && lt(r, an) || // Attr
    n.attr && on.includes(r)) && (o[r] = t[r]);
  }), o;
}
const ln = /* @__PURE__ */ x.createContext({}), cn = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, un = (t) => {
  const e = x.useContext(ln);
  return x.useMemo(() => ({
    ...cn,
    ...e[t]
  }), [e[t]]);
};
function He() {
  const {
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = x.useContext(sr.ConfigContext);
  return {
    theme: r,
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o
  };
}
function fn(t) {
  if (Array.isArray(t)) return t;
}
function dn(t, e) {
  var n = t == null ? null : typeof Symbol < "u" && t[Symbol.iterator] || t["@@iterator"];
  if (n != null) {
    var o, r, i, s, a = [], l = !0, c = !1;
    try {
      if (i = (n = n.call(t)).next, e === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (o = i.call(n)).done) && (a.push(o.value), a.length !== e); l = !0) ;
    } catch (f) {
      c = !0, r = f;
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
function ct(t, e) {
  (e == null || e > t.length) && (e = t.length);
  for (var n = 0, o = Array(e); n < e; n++) o[n] = t[n];
  return o;
}
function hn(t, e) {
  if (t) {
    if (typeof t == "string") return ct(t, e);
    var n = {}.toString.call(t).slice(8, -1);
    return n === "Object" && t.constructor && (n = t.constructor.name), n === "Map" || n === "Set" ? Array.from(t) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? ct(t, e) : void 0;
  }
}
function gn() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function N(t, e) {
  return fn(t) || dn(t, e) || hn(t, e) || gn();
}
function ae(t, e) {
  if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function");
}
function mn(t, e) {
  for (var n = 0; n < e.length; n++) {
    var o = e[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, Lt(o.key), o);
  }
}
function le(t, e, n) {
  return e && mn(t.prototype, e), Object.defineProperty(t, "prototype", {
    writable: !1
  }), t;
}
function q(t) {
  if (t === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return t;
}
function Ae(t, e) {
  return Ae = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, Ae(t, e);
}
function $t(t, e) {
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
function ie(t) {
  return ie = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
    return e.__proto__ || Object.getPrototypeOf(e);
  }, ie(t);
}
function Dt() {
  try {
    var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Dt = function() {
    return !!t;
  })();
}
function pn(t, e) {
  if (e && (A(e) == "object" || typeof e == "function")) return e;
  if (e !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return q(t);
}
function Ht(t) {
  var e = Dt();
  return function() {
    var n, o = ie(t);
    if (e) {
      var r = ie(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return pn(this, n);
  };
}
var At = /* @__PURE__ */ le(function t() {
  ae(this, t);
}), Bt = "CALC_UNIT", bn = new RegExp(Bt, "g");
function we(t) {
  return typeof t == "number" ? "".concat(t).concat(Bt) : t;
}
var yn = /* @__PURE__ */ function(t) {
  $t(n, t);
  var e = Ht(n);
  function n(o, r) {
    var i;
    ae(this, n), i = e.call(this), O(q(i), "result", ""), O(q(i), "unitlessCssVar", void 0), O(q(i), "lowPriority", void 0);
    var s = A(o);
    return i.unitlessCssVar = r, o instanceof n ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = we(o) : s === "string" && (i.result = o), i;
  }
  return le(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(we(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(we(r))), this.lowPriority = !0, this;
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
      }) && (l = !1), this.result = this.result.replace(bn, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(At), vn = /* @__PURE__ */ function(t) {
  $t(n, t);
  var e = Ht(n);
  function n(o) {
    var r;
    return ae(this, n), r = e.call(this), O(q(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return le(n, [{
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
}(At), xn = function(e, n) {
  var o = e === "css" ? yn : vn;
  return function(r) {
    return new o(r, n);
  };
}, ut = function(e, n) {
  return "".concat([n, e.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function ft(t) {
  var e = X.useRef();
  e.current = t;
  var n = X.useCallback(function() {
    for (var o, r = arguments.length, i = new Array(r), s = 0; s < r; s++)
      i[s] = arguments[s];
    return (o = e.current) === null || o === void 0 ? void 0 : o.call.apply(o, [e].concat(i));
  }, []);
  return n;
}
function Sn() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var dt = Sn() ? X.useLayoutEffect : X.useEffect, Cn = function(e, n) {
  var o = X.useRef(!0);
  dt(function() {
    return e(o.current);
  }, n), dt(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, ht = function(e, n) {
  Cn(function(o) {
    if (!o)
      return e();
  }, n);
};
function gt(t) {
  var e = X.useRef(!1), n = X.useState(t), o = N(n, 2), r = o[0], i = o[1];
  X.useEffect(function() {
    return e.current = !1, function() {
      e.current = !0;
    };
  }, []);
  function s(a, l) {
    l && e.current || i(a);
  }
  return [r, s];
}
function Te(t) {
  return t !== void 0;
}
function _n(t, e) {
  var n = e || {}, o = n.defaultValue, r = n.value, i = n.onChange, s = n.postState, a = gt(function() {
    return Te(r) ? r : Te(o) ? typeof o == "function" ? o() : o : typeof t == "function" ? t() : t;
  }), l = N(a, 2), c = l[0], f = l[1], u = r !== void 0 ? r : c, d = s ? s(u) : u, g = ft(i), m = gt([u]), y = N(m, 2), h = y[0], v = y[1];
  ht(function() {
    var T = h[0];
    c !== T && g(c, T);
  }, [h]), ht(function() {
    Te(r) || f(r);
  }, [r]);
  var p = ft(function(T, b) {
    f(T, b), v([u], b);
  });
  return [d, p];
}
var w = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Fe = Symbol.for("react.element"), Xe = Symbol.for("react.portal"), ce = Symbol.for("react.fragment"), ue = Symbol.for("react.strict_mode"), fe = Symbol.for("react.profiler"), de = Symbol.for("react.provider"), he = Symbol.for("react.context"), wn = Symbol.for("react.server_context"), ge = Symbol.for("react.forward_ref"), me = Symbol.for("react.suspense"), pe = Symbol.for("react.suspense_list"), be = Symbol.for("react.memo"), ye = Symbol.for("react.lazy"), Tn = Symbol.for("react.offscreen"), zt;
zt = Symbol.for("react.module.reference");
function H(t) {
  if (typeof t == "object" && t !== null) {
    var e = t.$$typeof;
    switch (e) {
      case Fe:
        switch (t = t.type, t) {
          case ce:
          case fe:
          case ue:
          case me:
          case pe:
            return t;
          default:
            switch (t = t && t.$$typeof, t) {
              case wn:
              case he:
              case ge:
              case ye:
              case be:
              case de:
                return t;
              default:
                return e;
            }
        }
      case Xe:
        return e;
    }
  }
}
w.ContextConsumer = he;
w.ContextProvider = de;
w.Element = Fe;
w.ForwardRef = ge;
w.Fragment = ce;
w.Lazy = ye;
w.Memo = be;
w.Portal = Xe;
w.Profiler = fe;
w.StrictMode = ue;
w.Suspense = me;
w.SuspenseList = pe;
w.isAsyncMode = function() {
  return !1;
};
w.isConcurrentMode = function() {
  return !1;
};
w.isContextConsumer = function(t) {
  return H(t) === he;
};
w.isContextProvider = function(t) {
  return H(t) === de;
};
w.isElement = function(t) {
  return typeof t == "object" && t !== null && t.$$typeof === Fe;
};
w.isForwardRef = function(t) {
  return H(t) === ge;
};
w.isFragment = function(t) {
  return H(t) === ce;
};
w.isLazy = function(t) {
  return H(t) === ye;
};
w.isMemo = function(t) {
  return H(t) === be;
};
w.isPortal = function(t) {
  return H(t) === Xe;
};
w.isProfiler = function(t) {
  return H(t) === fe;
};
w.isStrictMode = function(t) {
  return H(t) === ue;
};
w.isSuspense = function(t) {
  return H(t) === me;
};
w.isSuspenseList = function(t) {
  return H(t) === pe;
};
w.isValidElementType = function(t) {
  return typeof t == "string" || typeof t == "function" || t === ce || t === fe || t === ue || t === me || t === pe || t === Tn || typeof t == "object" && t !== null && (t.$$typeof === ye || t.$$typeof === be || t.$$typeof === de || t.$$typeof === he || t.$$typeof === ge || t.$$typeof === zt || t.getModuleId !== void 0);
};
w.typeOf = H;
Number(tr.split(".")[0]);
function mt(t, e, n, o) {
  var r = L({}, e[t]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var l = N(a, 2), c = l[0], f = l[1];
      if (r != null && r[c] || r != null && r[f]) {
        var u;
        (u = r[f]) !== null && u !== void 0 || (r[f] = r == null ? void 0 : r[c]);
      }
    });
  }
  var s = L(L({}, n), r);
  return Object.keys(s).forEach(function(a) {
    s[a] === e[a] && delete s[a];
  }), s;
}
var Ft = typeof CSSINJS_STATISTIC < "u", Be = !0;
function Ve() {
  for (var t = arguments.length, e = new Array(t), n = 0; n < t; n++)
    e[n] = arguments[n];
  if (!Ft)
    return Object.assign.apply(Object, [{}].concat(e));
  Be = !1;
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
  }), Be = !0, o;
}
var pt = {};
function Pn() {
}
var On = function(e) {
  var n, o = e, r = Pn;
  return Ft && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(e, {
    get: function(s, a) {
      if (Be) {
        var l;
        (l = n) === null || l === void 0 || l.add(a);
      }
      return s[a];
    }
  }), r = function(s, a) {
    var l;
    pt[s] = {
      global: Array.from(n),
      component: L(L({}, (l = pt[s]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function bt(t, e, n) {
  if (typeof n == "function") {
    var o;
    return n(Ve(e, (o = e[t]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function Mn(t) {
  return t === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(i) {
        return oe(i);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(i) {
        return oe(i);
      }).join(","), ")");
    }
  };
}
var En = 1e3 * 60 * 10, jn = /* @__PURE__ */ function() {
  function t() {
    ae(this, t), O(this, "map", /* @__PURE__ */ new Map()), O(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), O(this, "nextID", 0), O(this, "lastAccessBeat", /* @__PURE__ */ new Map()), O(this, "accessBeat", 0);
  }
  return le(t, [{
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
          o - r > En && (n.map.delete(i), n.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), t;
}(), yt = new jn();
function In(t, e) {
  return x.useMemo(function() {
    var n = yt.get(e);
    if (n)
      return n;
    var o = t();
    return yt.set(e, o), o;
  }, e);
}
var kn = function() {
  return {};
};
function Ln(t) {
  var e = t.useCSP, n = e === void 0 ? kn : e, o = t.useToken, r = t.usePrefix, i = t.getResetStyles, s = t.getCommonStyle, a = t.getCompUnitless;
  function l(d, g, m, y) {
    var h = Array.isArray(d) ? d[0] : d;
    function v(M) {
      return "".concat(String(h)).concat(M.slice(0, 1).toUpperCase()).concat(M.slice(1));
    }
    var p = (y == null ? void 0 : y.unitless) || {}, T = typeof a == "function" ? a(d) : {}, b = L(L({}, T), {}, O({}, v("zIndexPopup"), !0));
    Object.keys(p).forEach(function(M) {
      b[v(M)] = p[M];
    });
    var C = L(L({}, y), {}, {
      unitless: b,
      prefixToken: v
    }), S = f(d, g, m, C), P = c(h, m, C);
    return function(M) {
      var E = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : M, R = S(M, E), B = N(R, 2), _ = B[1], z = P(E), k = N(z, 2), $ = k[0], D = k[1];
      return [$, _, D];
    };
  }
  function c(d, g, m) {
    var y = m.unitless, h = m.injectStyle, v = h === void 0 ? !0 : h, p = m.prefixToken, T = m.ignore, b = function(P) {
      var M = P.rootCls, E = P.cssVar, R = E === void 0 ? {} : E, B = o(), _ = B.realToken;
      return cr({
        path: [d],
        prefix: R.prefix,
        key: R.key,
        unitless: y,
        ignore: T,
        token: _,
        scope: M
      }, function() {
        var z = bt(d, _, g), k = mt(d, _, z, {
          deprecatedTokens: m == null ? void 0 : m.deprecatedTokens
        });
        return Object.keys(z).forEach(function($) {
          k[p($)] = k[$], delete k[$];
        }), k;
      }), null;
    }, C = function(P) {
      var M = o(), E = M.cssVar;
      return [function(R) {
        return v && E ? /* @__PURE__ */ x.createElement(x.Fragment, null, /* @__PURE__ */ x.createElement(b, {
          rootCls: P,
          cssVar: E,
          component: d
        }), R) : R;
      }, E == null ? void 0 : E.key];
    };
    return C;
  }
  function f(d, g, m) {
    var y = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = Array.isArray(d) ? d : [d, d], v = N(h, 1), p = v[0], T = h.join("-"), b = t.layer || {
      name: "antd"
    };
    return function(C) {
      var S = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : C, P = o(), M = P.theme, E = P.realToken, R = P.hashId, B = P.token, _ = P.cssVar, z = r(), k = z.rootPrefixCls, $ = z.iconPrefixCls, D = n(), W = _ ? "css" : "js", Ne = In(function() {
        var V = /* @__PURE__ */ new Set();
        return _ && Object.keys(y.unitless || {}).forEach(function(Y) {
          V.add(Se(Y, _.prefix)), V.add(Se(Y, ut(p, _.prefix)));
        }), xn(W, V);
      }, [W, p, _ == null ? void 0 : _.prefix]), ve = Mn(W), Ge = ve.max, xe = ve.min, Ue = {
        theme: M,
        token: B,
        hashId: R,
        nonce: function() {
          return D.nonce;
        },
        clientOnly: y.clientOnly,
        layer: b,
        // antd is always at top of styles
        order: y.order || -999
      };
      typeof i == "function" && Qe(L(L({}, Ue), {}, {
        clientOnly: !1,
        path: ["Shared", k]
      }), function() {
        return i(B, {
          prefix: {
            rootPrefixCls: k,
            iconPrefixCls: $
          },
          csp: D
        });
      });
      var Ut = Qe(L(L({}, Ue), {}, {
        path: [T, C, $]
      }), function() {
        if (y.injectStyle === !1)
          return [];
        var V = On(B), Y = V.token, Wt = V.flush, G = bt(p, E, m), Kt = ".".concat(C), We = mt(p, E, G, {
          deprecatedTokens: y.deprecatedTokens
        });
        _ && G && A(G) === "object" && Object.keys(G).forEach(function(qe) {
          G[qe] = "var(".concat(Se(qe, ut(p, _.prefix)), ")");
        });
        var Ke = Ve(Y, {
          componentCls: Kt,
          prefixCls: C,
          iconCls: ".".concat($),
          antCls: ".".concat(k),
          calc: Ne,
          // @ts-ignore
          max: Ge,
          // @ts-ignore
          min: xe
        }, _ ? G : We), qt = g(Ke, {
          hashId: R,
          prefixCls: C,
          rootPrefixCls: k,
          iconPrefixCls: $
        });
        Wt(p, We);
        var Qt = typeof s == "function" ? s(Ke, C, S, y.resetFont) : null;
        return [y.resetStyle === !1 ? null : Qt, qt];
      });
      return [Ut, R];
    };
  }
  function u(d, g, m) {
    var y = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = f(d, g, m, L({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, y)), v = function(T) {
      var b = T.prefixCls, C = T.rootCls, S = C === void 0 ? b : C;
      return h(b, S), null;
    };
    return v;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: u,
    genComponentStyleHook: f
  };
}
const Rn = {
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
}, $n = Object.assign(Object.assign({}, Rn), {
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
}), j = Math.round;
function Pe(t, e) {
  const n = t.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = e(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const vt = (t, e, n) => n === 0 ? t : t / 100;
function K(t, e) {
  const n = e || 255;
  return t > n ? n : t < 0 ? 0 : t;
}
class F {
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
    } else if (e instanceof F)
      this.r = e.r, this.g = e.g, this.b = e.b, this.a = e.a, this._h = e._h, this._s = e._s, this._l = e._l, this._v = e._v;
    else if (n("rgb"))
      this.r = K(e.r), this.g = K(e.g), this.b = K(e.b), this.a = typeof e.a == "number" ? K(e.a, 1) : 1;
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
      e === 0 ? this._h = 0 : this._h = j(60 * (this.r === this.getMax() ? (this.g - this.b) / e + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / e + 2 : (this.r - this.g) / e + 4));
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
      r: j(i("r")),
      g: j(i("g")),
      b: j(i("b")),
      a: j(i("a") * 100) / 100
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
    const n = this._c(e), o = this.a + n.a * (1 - this.a), r = (i) => j((this[i] * this.a + n[i] * n.a * (1 - this.a)) / o);
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
      const i = j(this.a * 255).toString(16);
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
    const e = this.getHue(), n = j(this.getSaturation() * 100), o = j(this.getLightness() * 100);
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
    return r[e] = K(n, o), r;
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
      const d = j(o * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let i = 0, s = 0, a = 0;
    const l = e / 60, c = (1 - Math.abs(2 * o - 1)) * n, f = c * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (i = c, s = f) : l >= 1 && l < 2 ? (i = f, s = c) : l >= 2 && l < 3 ? (s = c, a = f) : l >= 3 && l < 4 ? (s = f, a = c) : l >= 4 && l < 5 ? (i = f, a = c) : l >= 5 && l < 6 && (i = c, a = f);
    const u = o - c / 2;
    this.r = j((i + u) * 255), this.g = j((s + u) * 255), this.b = j((a + u) * 255);
  }
  fromHsv({
    h: e,
    s: n,
    v: o,
    a: r
  }) {
    this._h = e % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const i = j(o * 255);
    if (this.r = i, this.g = i, this.b = i, n <= 0)
      return;
    const s = e / 60, a = Math.floor(s), l = s - a, c = j(o * (1 - n) * 255), f = j(o * (1 - n * l) * 255), u = j(o * (1 - n * (1 - l)) * 255);
    switch (a) {
      case 0:
        this.g = u, this.b = c;
        break;
      case 1:
        this.r = f, this.b = c;
        break;
      case 2:
        this.r = c, this.b = u;
        break;
      case 3:
        this.r = c, this.g = f;
        break;
      case 4:
        this.r = u, this.g = c;
        break;
      case 5:
      default:
        this.g = c, this.b = f;
        break;
    }
  }
  fromHsvString(e) {
    const n = Pe(e, vt);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(e) {
    const n = Pe(e, vt);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(e) {
    const n = Pe(e, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? j(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function Oe(t) {
  return t >= 0 && t <= 255;
}
function ee(t, e) {
  const {
    r: n,
    g: o,
    b: r,
    a: i
  } = new F(t).toRgb();
  if (i < 1)
    return t;
  const {
    r: s,
    g: a,
    b: l
  } = new F(e).toRgb();
  for (let c = 0.01; c <= 1; c += 0.01) {
    const f = Math.round((n - s * (1 - c)) / c), u = Math.round((o - a * (1 - c)) / c), d = Math.round((r - l * (1 - c)) / c);
    if (Oe(f) && Oe(u) && Oe(d))
      return new F({
        r: f,
        g: u,
        b: d,
        a: Math.round(c * 100) / 100
      }).toRgbString();
  }
  return new F({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var Dn = function(t, e) {
  var n = {};
  for (var o in t) Object.prototype.hasOwnProperty.call(t, o) && e.indexOf(o) < 0 && (n[o] = t[o]);
  if (t != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(t); r < o.length; r++)
    e.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(t, o[r]) && (n[o[r]] = t[o[r]]);
  return n;
};
function Hn(t) {
  const {
    override: e
  } = t, n = Dn(t, ["override"]), o = Object.assign({}, e);
  Object.keys($n).forEach((d) => {
    delete o[d];
  });
  const r = Object.assign(Object.assign({}, n), o), i = 480, s = 576, a = 768, l = 992, c = 1200, f = 1600;
  if (r.motion === !1) {
    const d = "0s";
    r.motionDurationFast = d, r.motionDurationMid = d, r.motionDurationSlow = d;
  }
  return Object.assign(Object.assign(Object.assign({}, r), {
    // ============== Background ============== //
    colorFillContent: r.colorFillSecondary,
    colorFillContentHover: r.colorFill,
    colorFillAlter: r.colorFillQuaternary,
    colorBgContainerDisabled: r.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: r.colorBgContainer,
    colorSplit: ee(r.colorBorderSecondary, r.colorBgContainer),
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
    colorErrorOutline: ee(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: ee(r.colorWarningBg, r.colorBgContainer),
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
    controlOutline: ee(r.colorPrimaryBg, r.colorBgContainer),
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
    screenXLMax: f - 1,
    screenXXL: f,
    screenXXLMin: f,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new F("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new F("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new F("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const An = {
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
}, Bn = {
  motionBase: !0,
  motionUnit: !0
}, zn = ur(Re.defaultAlgorithm), Fn = {
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
}, Xt = (t, e, n) => {
  const o = n.getDerivativeToken(t), {
    override: r,
    ...i
  } = e;
  let s = {
    ...o,
    override: r
  };
  return s = Hn(s), i && Object.entries(i).forEach(([a, l]) => {
    const {
      theme: c,
      ...f
    } = l;
    let u = f;
    c && (u = Xt({
      ...s,
      ...f
    }, {
      override: f
    }, c)), s[a] = u;
  }), s;
};
function Xn() {
  const {
    token: t,
    hashed: e,
    theme: n = zn,
    override: o,
    cssVar: r
  } = x.useContext(Re._internalContext), [i, s, a] = fr(n, [Re.defaultSeed, t], {
    salt: `${en}-${e || ""}`,
    override: o,
    getComputedToken: Xt,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: An,
      ignore: Bn,
      preserve: Fn
    }
  });
  return [n, a, e ? s : "", i, r];
}
const {
  genStyleHooks: Vn
} = Ln({
  usePrefix: () => {
    const {
      getPrefixCls: t,
      iconPrefixCls: e
    } = He();
    return {
      iconPrefixCls: e,
      rootPrefixCls: t()
    };
  },
  useToken: () => {
    const [t, e, n, o, r] = Xn();
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
    } = He();
    return t ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), Vt = /* @__PURE__ */ x.createContext(null), xt = ({
  children: t
}) => {
  const {
    prefixCls: e
  } = x.useContext(Vt);
  return /* @__PURE__ */ x.createElement("div", {
    className: Q(`${e}-group-title`)
  }, t && /* @__PURE__ */ x.createElement(Pt.Text, null, t));
}, St = (t) => {
  t.stopPropagation();
}, Nn = (t) => {
  const {
    prefixCls: e,
    info: n,
    className: o,
    direction: r,
    onClick: i,
    active: s,
    menu: a,
    ...l
  } = t, c = Rt(l, {
    aria: !0,
    data: !0,
    attr: !0
  }), {
    disabled: f
  } = n, u = Q(o, `${e}-item`, {
    [`${e}-item-active`]: s && !f
  }, {
    [`${e}-item-disabled`]: f
  }), d = () => {
    !f && i && i(n);
  }, {
    trigger: g,
    ...m
  } = a || {}, y = m == null ? void 0 : m.getPopupContainer, h = (v) => {
    const p = /* @__PURE__ */ x.createElement(lr, {
      onClick: St,
      className: `${e}-menu-icon`
    });
    return g ? typeof g == "function" ? g(v, {
      originNode: p
    }) : g : p;
  };
  return /* @__PURE__ */ x.createElement("li", J({
    title: typeof n.label == "object" ? void 0 : `${n.label}`
  }, c, {
    className: u,
    onClick: d
  }), n.icon && /* @__PURE__ */ x.createElement("div", {
    className: `${e}-icon`
  }, n.icon), /* @__PURE__ */ x.createElement(Pt.Text, {
    className: `${e}-label`
  }, n.label), !f && a && /* @__PURE__ */ x.createElement("div", {
    onClick: St
  }, /* @__PURE__ */ x.createElement(ar, {
    menu: m,
    placement: r === "rtl" ? "bottomLeft" : "bottomRight",
    trigger: ["click"],
    disabled: f,
    getPopupContainer: y
  }, h(n))));
}, Me = "__ungrouped", Gn = (t, e = []) => {
  const [n, o, r] = x.useMemo(() => {
    if (!t)
      return [!1, void 0, void 0];
    let i = {
      sort: void 0,
      title: void 0
    };
    return typeof t == "object" && (i = {
      ...i,
      ...t
    }), [!0, i.sort, i.title];
  }, [t]);
  return x.useMemo(() => {
    if (!n)
      return [[{
        name: Me,
        data: e,
        title: void 0
      }], n];
    const i = e.reduce((l, c) => {
      const f = c.group || Me;
      return l[f] || (l[f] = []), l[f].push(c), l;
    }, {});
    return [(o ? Object.keys(i).sort(o) : Object.keys(i)).map((l) => ({
      name: l === Me ? void 0 : l,
      title: r,
      data: i[l]
    })), n];
  }, [e, t]);
}, Un = (t) => {
  const {
    componentCls: e
  } = t;
  return {
    [e]: {
      display: "flex",
      flexDirection: "column",
      gap: t.paddingXXS,
      overflowY: "auto",
      padding: t.paddingSM,
      margin: 0,
      listStyle: "none",
      "ul, ol": {
        margin: 0,
        padding: 0,
        listStyle: "none"
      },
      [`&${e}-rtl`]: {
        direction: "rtl"
      },
      // 会话列表
      [`& ${e}-list`]: {
        display: "flex",
        gap: t.paddingXXS,
        flexDirection: "column",
        [`& ${e}-item`]: {
          paddingInlineStart: t.paddingXL
        },
        [`& ${e}-label`]: {
          color: t.colorTextDescription,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap"
        }
      },
      // 会话列表项
      [`& ${e}-item`]: {
        display: "flex",
        height: t.controlHeightLG,
        minHeight: t.controlHeightLG,
        gap: t.paddingXS,
        padding: `0 ${oe(t.paddingXS)}`,
        alignItems: "center",
        borderRadius: t.borderRadiusLG,
        cursor: "pointer",
        transition: `all ${t.motionDurationMid} ${t.motionEaseInOut}`,
        // 悬浮样式
        "&:hover": {
          backgroundColor: t.colorBgTextHover
        },
        // 选中样式
        "&-active": {
          backgroundColor: t.colorBgTextHover,
          [`& ${e}-label, ${e}-menu-icon`]: {
            color: t.colorText
          }
        },
        // 禁用样式
        "&-disabled": {
          cursor: "not-allowed",
          [`& ${e}-label`]: {
            color: t.colorTextDisabled
          }
        },
        // 悬浮、选中时激活操作菜单
        "&:hover, &-active": {
          [`& ${e}-menu-icon`]: {
            opacity: 0.6
          }
        },
        [`${e}-menu-icon:hover`]: {
          opacity: 1
        }
      },
      // 会话名
      [`& ${e}-label`]: {
        flex: 1,
        color: t.colorText,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap"
      },
      // 会话操作菜单
      [`& ${e}-menu-icon`]: {
        opacity: 0,
        fontSize: t.fontSizeXL
      },
      // 会话图标
      [`& ${e}-group-title`]: {
        display: "flex",
        alignItems: "center",
        height: t.controlHeightLG,
        minHeight: t.controlHeightLG,
        padding: `0 ${oe(t.paddingXS)}`
      }
    }
  };
}, Wn = () => ({}), Kn = Vn("Conversations", (t) => {
  const e = Ve(t, {});
  return Un(e);
}, Wn), qn = (t) => {
  const {
    prefixCls: e,
    rootClassName: n,
    items: o,
    activeKey: r,
    defaultActiveKey: i,
    onActiveChange: s,
    menu: a,
    styles: l = {},
    classNames: c = {},
    groupable: f,
    className: u,
    style: d,
    ...g
  } = t, m = Rt(g, {
    attr: !0,
    aria: !0,
    data: !0
  }), [y, h] = _n(i, {
    value: r
  }), [v, p] = Gn(f, o), {
    getPrefixCls: T,
    direction: b
  } = He(), C = T("conversations", e), S = un("conversations"), [P, M, E] = Kn(C), R = Q(C, S.className, u, n, M, E, {
    [`${C}-rtl`]: b === "rtl"
  }), B = (_) => {
    h(_.key), s && s(_.key);
  };
  return P(/* @__PURE__ */ x.createElement("ul", J({}, m, {
    style: {
      ...S.style,
      ...d
    },
    className: R
  }), v.map((_, z) => {
    var $;
    const k = _.data.map((D, W) => {
      const {
        label: Ne,
        disabled: ve,
        icon: Ge,
        ...xe
      } = D;
      return /* @__PURE__ */ x.createElement(Nn, J({}, xe, {
        key: D.key || `key-${W}`,
        info: D,
        prefixCls: C,
        direction: b,
        className: Q(c.item, S.classNames.item, D.className),
        style: {
          ...S.styles.item,
          ...l.item,
          ...D.style
        },
        menu: typeof a == "function" ? a(D) : a,
        active: y === D.key,
        onClick: B
      }));
    });
    return p ? /* @__PURE__ */ x.createElement("li", {
      key: _.name || `key-${z}`
    }, /* @__PURE__ */ x.createElement(Vt.Provider, {
      value: {
        prefixCls: C
      }
    }, (($ = _.title) == null ? void 0 : $.call(_, _.name, {
      components: {
        GroupTitle: xt
      }
    })) || /* @__PURE__ */ x.createElement(xt, {
      key: _.name
    }, _.name)), /* @__PURE__ */ x.createElement("ul", {
      className: `${C}-list`
    }, k)) : k;
  })));
};
function Qn(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function Nt(t, e = !1) {
  try {
    if (wt(t))
      return t;
    if (e && !Qn(t))
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
function Ct(t, e) {
  return je(() => Nt(t, e), [t, e]);
}
const Zn = ({
  children: t,
  ...e
}) => /* @__PURE__ */ I.jsx(I.Fragment, {
  children: t(e)
});
function Gt(t) {
  return x.createElement(Zn, {
    children: t
  });
}
function ze(t, e, n) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((r, i) => {
      var c, f;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const s = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((c = r.props) == null ? void 0 : c.key) ?? (n ? `${n}-${i}` : `${i}`)
      }) : {
        ...r.props,
        key: ((f = r.props) == null ? void 0 : f.key) ?? (n ? `${n}-${i}` : `${i}`)
      };
      let a = s;
      Object.keys(r.slots).forEach((u) => {
        if (!r.slots[u] || !(r.slots[u] instanceof Element) && !r.slots[u].el)
          return;
        const d = u.split(".");
        d.forEach((p, T) => {
          a[p] || (a[p] = {}), T !== d.length - 1 && (a = s[p]);
        });
        const g = r.slots[u];
        let m, y, h = (e == null ? void 0 : e.clone) ?? !1, v = e == null ? void 0 : e.forceClone;
        g instanceof Element ? m = g : (m = g.el, y = g.callback, h = g.clone ?? h, v = g.forceClone ?? v), v = v ?? !!y, a[d[d.length - 1]] = m ? y ? (...p) => (y(d[d.length - 1], p), /* @__PURE__ */ I.jsx(Le, {
          ...r.ctx,
          params: p,
          forceClone: v,
          children: /* @__PURE__ */ I.jsx(Z, {
            slot: m,
            clone: h
          })
        })) : Gt((p) => /* @__PURE__ */ I.jsx(Le, {
          ...r.ctx,
          forceClone: v,
          children: /* @__PURE__ */ I.jsx(Z, {
            ...p,
            slot: m,
            clone: h
          })
        })) : a[d[d.length - 1]], a = s;
      });
      const l = (e == null ? void 0 : e.children) || "children";
      return r[l] ? s[l] = ze(r[l], e, `${i}`) : e != null && e.children && (s[l] = void 0, Reflect.deleteProperty(s, l)), s;
    });
}
function _t(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? Gt((n) => /* @__PURE__ */ I.jsx(Le, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ I.jsx(Z, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...n
    })
  })) : /* @__PURE__ */ I.jsx(Z, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function Ee({
  key: t,
  slots: e,
  targets: n
}, o) {
  return e[t] ? (...r) => n ? n.map((i, s) => /* @__PURE__ */ I.jsx(x.Fragment, {
    children: _t(i, {
      clone: !0,
      params: r,
      forceClone: (o == null ? void 0 : o.forceClone) ?? !0
    })
  }, s)) : /* @__PURE__ */ I.jsx(I.Fragment, {
    children: _t(e[t], {
      clone: !0,
      params: r,
      forceClone: (o == null ? void 0 : o.forceClone) ?? !0
    })
  }) : void 0;
}
const {
  useItems: Jn,
  withItemsContextProvider: Yn,
  ItemHandler: so
} = Tt("antd-menu-items"), {
  useItems: eo,
  withItemsContextProvider: to,
  ItemHandler: ao
} = Tt("antdx-conversations-items");
function ro(t) {
  return typeof t == "object" && t !== null ? t : {};
}
function no(t, e) {
  return Object.keys(t).reduce((n, o) => {
    if (o.startsWith("on") && wt(t[o])) {
      const r = t[o];
      o === "onClick" ? n[o] = (i, ...s) => {
        i.domEvent.stopPropagation(), r == null || r(e, i, ...s);
      } : n[o] = (...i) => {
        r == null || r(e, ...i);
      };
    } else
      n[o] = t[o];
    return n;
  }, {});
}
const lo = qr(Yn(["menu.items"], to(["default", "items"], ({
  slots: t,
  setSlotParams: e,
  children: n,
  items: o,
  ...r
}) => {
  var m;
  const {
    items: {
      "menu.items": i
    }
  } = Jn(), s = Ct(r.menu), a = typeof r.groupable == "object" || t["groupable.title"], l = ro(r.groupable), c = Ct(r.groupable), f = je(() => {
    var y;
    if (typeof r.menu == "string")
      return s;
    {
      const h = r.menu || {};
      return ((y = h.items) == null ? void 0 : y.length) || i.length > 0 ? (p) => ({
        ...no(h, p),
        items: h.items || ze(i, {
          clone: !0
        }) || [],
        trigger: t["menu.trigger"] ? Ee({
          slots: t,
          key: "menu.trigger"
        }, {}) : Nt(h.trigger, !0) || h.trigger,
        expandIcon: t["menu.expandIcon"] ? Ee({
          slots: t,
          key: "menu.expandIcon"
        }, {}) : h.expandIcon,
        overflowedIndicator: t["menu.overflowedIndicator"] ? /* @__PURE__ */ I.jsx(Z, {
          slot: t["menu.overflowedIndicator"]
        }) : h.overflowedIndicator
      }) : void 0;
    }
  }, [s, i, r.menu, e, t]), {
    items: u
  } = eo(), d = u.items.length > 0 ? u.items : u.default, g = je(() => o || ze(d, {
    clone: !0
  }), [o, d]);
  return /* @__PURE__ */ I.jsxs(I.Fragment, {
    children: [/* @__PURE__ */ I.jsx("div", {
      style: {
        display: "none"
      },
      children: n
    }), /* @__PURE__ */ I.jsx(qn, {
      ...r,
      menu: f,
      classNames: {
        ...r.classNames,
        item: Q((m = r.classNames) == null ? void 0 : m.item, "ms-gr-antdx-conversations-item")
      },
      items: g,
      groupable: a ? {
        ...l,
        title: t["groupable.title"] ? Ee({
          slots: t,
          key: "groupable.title"
        }) : l.title,
        sort: c || l.sort
      } : r.groupable
    })]
  });
})));
export {
  lo as Conversations,
  lo as default
};
