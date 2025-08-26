import { i as Wt, a as ge, r as Ut, Z as ue, g as Gt, c as Q, b as Kt } from "./Index-D11XQ0Lt.js";
const w = window.ms_globals.React, h = window.ms_globals.React, zt = window.ms_globals.React.forwardRef, Ft = window.ms_globals.React.useRef, Nt = window.ms_globals.React.useState, Xt = window.ms_globals.React.useEffect, Vt = window.ms_globals.React.version, vt = window.ms_globals.React.useMemo, De = window.ms_globals.ReactDOM.createPortal, qt = window.ms_globals.internalContext.useContextPropsContext, Yt = window.ms_globals.internalContext.ContextPropsProvider, Qt = window.ms_globals.antd.ConfigProvider, He = window.ms_globals.antd.theme, Zt = window.ms_globals.antd.Avatar, ie = window.ms_globals.antdCssinjs.unit, Ie = window.ms_globals.antdCssinjs.token2CSSVar, Ye = window.ms_globals.antdCssinjs.useStyleRegister, Jt = window.ms_globals.antdCssinjs.useCSSVarRegister, er = window.ms_globals.antdCssinjs.createTheme, tr = window.ms_globals.antdCssinjs.useCacheToken, xt = window.ms_globals.antdCssinjs.Keyframes;
var rr = /\s/;
function nr(t) {
  for (var e = t.length; e-- && rr.test(t.charAt(e)); )
    ;
  return e;
}
var or = /^\s+/;
function ir(t) {
  return t && t.slice(0, nr(t) + 1).replace(or, "");
}
var Qe = NaN, sr = /^[-+]0x[0-9a-f]+$/i, ar = /^0b[01]+$/i, cr = /^0o[0-7]+$/i, lr = parseInt;
function Ze(t) {
  if (typeof t == "number")
    return t;
  if (Wt(t))
    return Qe;
  if (ge(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = ge(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = ir(t);
  var n = ar.test(t);
  return n || cr.test(t) ? lr(t.slice(2), n ? 2 : 8) : sr.test(t) ? Qe : +t;
}
var je = function() {
  return Ut.Date.now();
}, ur = "Expected a function", fr = Math.max, dr = Math.min;
function hr(t, e, n) {
  var o, r, i, s, a, c, l = 0, f = !1, u = !1, d = !0;
  if (typeof t != "function")
    throw new TypeError(ur);
  e = Ze(e) || 0, ge(n) && (f = !!n.leading, u = "maxWait" in n, i = u ? fr(Ze(n.maxWait) || 0, e) : i, d = "trailing" in n ? !!n.trailing : d);
  function x(m) {
    var _ = o, P = r;
    return o = r = void 0, l = m, s = t.apply(P, _), s;
  }
  function b(m) {
    return l = m, a = setTimeout(y, e), f ? x(m) : s;
  }
  function S(m) {
    var _ = m - c, P = m - l, I = e - _;
    return u ? dr(I, i - P) : I;
  }
  function p(m) {
    var _ = m - c, P = m - l;
    return c === void 0 || _ >= e || _ < 0 || u && P >= i;
  }
  function y() {
    var m = je();
    if (p(m))
      return C(m);
    a = setTimeout(y, S(m));
  }
  function C(m) {
    return a = void 0, d && o ? x(m) : (o = r = void 0, s);
  }
  function j() {
    a !== void 0 && clearTimeout(a), l = 0, o = c = r = a = void 0;
  }
  function g() {
    return a === void 0 ? s : C(je());
  }
  function v() {
    var m = je(), _ = p(m);
    if (o = arguments, r = this, c = m, _) {
      if (a === void 0)
        return b(c);
      if (u)
        return clearTimeout(a), a = setTimeout(y, e), x(c);
    }
    return a === void 0 && (a = setTimeout(y, e)), s;
  }
  return v.cancel = j, v.flush = g, v;
}
var St = {
  exports: {}
}, be = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var gr = h, mr = Symbol.for("react.element"), pr = Symbol.for("react.fragment"), br = Object.prototype.hasOwnProperty, yr = gr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, vr = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Ct(t, e, n) {
  var o, r = {}, i = null, s = null;
  n !== void 0 && (i = "" + n), e.key !== void 0 && (i = "" + e.key), e.ref !== void 0 && (s = e.ref);
  for (o in e) br.call(e, o) && !vr.hasOwnProperty(o) && (r[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) r[o] === void 0 && (r[o] = e[o]);
  return {
    $$typeof: mr,
    type: t,
    key: i,
    ref: s,
    props: r,
    _owner: yr.current
  };
}
be.Fragment = pr;
be.jsx = Ct;
be.jsxs = Ct;
St.exports = be;
var B = St.exports;
const {
  SvelteComponent: xr,
  assign: Je,
  binding_callbacks: et,
  check_outros: Sr,
  children: _t,
  claim_element: wt,
  claim_space: Cr,
  component_subscribe: tt,
  compute_slots: _r,
  create_slot: wr,
  detach: Z,
  element: Tt,
  empty: rt,
  exclude_internal_props: nt,
  get_all_dirty_from_scope: Tr,
  get_slot_changes: Er,
  group_outros: Mr,
  init: Pr,
  insert_hydration: fe,
  safe_not_equal: Or,
  set_custom_element_data: Et,
  space: Rr,
  transition_in: de,
  transition_out: Ae,
  update_slot_base: Ir
} = window.__gradio__svelte__internal, {
  beforeUpdate: jr,
  getContext: kr,
  onDestroy: Lr,
  setContext: $r
} = window.__gradio__svelte__internal;
function ot(t) {
  let e, n;
  const o = (
    /*#slots*/
    t[7].default
  ), r = wr(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = Tt("svelte-slot"), r && r.c(), this.h();
    },
    l(i) {
      e = wt(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = _t(e);
      r && r.l(s), s.forEach(Z), this.h();
    },
    h() {
      Et(e, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      fe(i, e, s), r && r.m(e, null), t[9](e), n = !0;
    },
    p(i, s) {
      r && r.p && (!n || s & /*$$scope*/
      64) && Ir(
        r,
        o,
        i,
        /*$$scope*/
        i[6],
        n ? Er(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : Tr(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      n || (de(r, i), n = !0);
    },
    o(i) {
      Ae(r, i), n = !1;
    },
    d(i) {
      i && Z(e), r && r.d(i), t[9](null);
    }
  };
}
function Br(t) {
  let e, n, o, r, i = (
    /*$$slots*/
    t[4].default && ot(t)
  );
  return {
    c() {
      e = Tt("react-portal-target"), n = Rr(), i && i.c(), o = rt(), this.h();
    },
    l(s) {
      e = wt(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), _t(e).forEach(Z), n = Cr(s), i && i.l(s), o = rt(), this.h();
    },
    h() {
      Et(e, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      fe(s, e, a), t[8](e), fe(s, n, a), i && i.m(s, a), fe(s, o, a), r = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && de(i, 1)) : (i = ot(s), i.c(), de(i, 1), i.m(o.parentNode, o)) : i && (Mr(), Ae(i, 1, 1, () => {
        i = null;
      }), Sr());
    },
    i(s) {
      r || (de(i), r = !0);
    },
    o(s) {
      Ae(i), r = !1;
    },
    d(s) {
      s && (Z(e), Z(n), Z(o)), t[8](null), i && i.d(s);
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
function Dr(t, e, n) {
  let o, r, {
    $$slots: i = {},
    $$scope: s
  } = e;
  const a = _r(i);
  let {
    svelteInit: c
  } = e;
  const l = ue(it(e)), f = ue();
  tt(t, f, (g) => n(0, o = g));
  const u = ue();
  tt(t, u, (g) => n(1, r = g));
  const d = [], x = kr("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: S,
    subSlotIndex: p
  } = Gt() || {}, y = c({
    parent: x,
    props: l,
    target: f,
    slot: u,
    slotKey: b,
    slotIndex: S,
    subSlotIndex: p,
    onDestroy(g) {
      d.push(g);
    }
  });
  $r("$$ms-gr-react-wrapper", y), jr(() => {
    l.set(it(e));
  }), Lr(() => {
    d.forEach((g) => g());
  });
  function C(g) {
    et[g ? "unshift" : "push"](() => {
      o = g, f.set(o);
    });
  }
  function j(g) {
    et[g ? "unshift" : "push"](() => {
      r = g, u.set(r);
    });
  }
  return t.$$set = (g) => {
    n(17, e = Je(Je({}, e), nt(g))), "svelteInit" in g && n(5, c = g.svelteInit), "$$scope" in g && n(6, s = g.$$scope);
  }, e = nt(e), [o, r, f, u, a, c, s, i, C, j];
}
class Hr extends xr {
  constructor(e) {
    super(), Pr(this, e, Dr, Br, Or, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: no
} = window.__gradio__svelte__internal, st = window.ms_globals.rerender, ke = window.ms_globals.tree;
function Ar(t, e = {}) {
  function n(o) {
    const r = ue(), i = new Hr({
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
          }, c = s.parent ?? ke;
          return c.nodes = [...c.nodes, a], st({
            createPortal: De,
            node: ke
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((l) => l.svelteInstance !== r), st({
              createPortal: De,
              node: ke
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
const zr = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Fr(t) {
  return t ? Object.keys(t).reduce((e, n) => {
    const o = t[n];
    return e[n] = Nr(n, o), e;
  }, {}) : {};
}
function Nr(t, e) {
  return typeof e == "number" && !zr.includes(t) ? e + "px" : e;
}
function ze(t) {
  const e = [], n = t.cloneNode(!1);
  if (t._reactElement) {
    const r = h.Children.toArray(t._reactElement.props.children).map((i) => {
      if (h.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = ze(i.props.el);
        return h.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...h.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(De(h.cloneElement(t._reactElement, {
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
      useCapture: c
    }) => {
      n.addEventListener(a, s, c);
    });
  });
  const o = Array.from(t.childNodes);
  for (let r = 0; r < o.length; r++) {
    const i = o[r];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = ze(i);
      e.push(...a), n.appendChild(s);
    } else i.nodeType === 3 && n.appendChild(i.cloneNode());
  }
  return {
    clonedElement: n,
    portals: e
  };
}
function Xr(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const U = zt(({
  slot: t,
  clone: e,
  className: n,
  style: o,
  observeAttributes: r
}, i) => {
  const s = Ft(), [a, c] = Nt([]), {
    forceClone: l
  } = qt(), f = l ? !0 : e;
  return Xt(() => {
    var S;
    if (!s.current || !t)
      return;
    let u = t;
    function d() {
      let p = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (p = u.children[0], p.tagName.toLowerCase() === "react-portal-target" && p.children[0] && (p = p.children[0])), Xr(i, p), n && p.classList.add(...n.split(" ")), o) {
        const y = Fr(o);
        Object.keys(y).forEach((C) => {
          p.style[C] = y[C];
        });
      }
    }
    let x = null, b = null;
    if (f && window.MutationObserver) {
      let p = function() {
        var g, v, m;
        (g = s.current) != null && g.contains(u) && ((v = s.current) == null || v.removeChild(u));
        const {
          portals: C,
          clonedElement: j
        } = ze(t);
        u = j, c(C), u.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          d();
        }, 50), (m = s.current) == null || m.appendChild(u);
      };
      p();
      const y = hr(() => {
        p(), x == null || x.disconnect(), x == null || x.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      x = new window.MutationObserver(y), x.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", d(), (S = s.current) == null || S.appendChild(u);
    return () => {
      var p, y;
      u.style.display = "", (p = s.current) != null && p.contains(u) && ((y = s.current) == null || y.removeChild(u)), x == null || x.disconnect();
    };
  }, [t, f, n, o, i, r, l]), h.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), Vr = "1.6.0";
function J() {
  return J = Object.assign ? Object.assign.bind() : function(t) {
    for (var e = 1; e < arguments.length; e++) {
      var n = arguments[e];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (t[o] = n[o]);
    }
    return t;
  }, J.apply(null, arguments);
}
function N(t) {
  "@babel/helpers - typeof";
  return N = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, N(t);
}
function Wr(t, e) {
  if (N(t) != "object" || !t) return t;
  var n = t[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(t, e);
    if (N(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function Mt(t) {
  var e = Wr(t, "string");
  return N(e) == "symbol" ? e : e + "";
}
function R(t, e, n) {
  return (e = Mt(e)) in t ? Object.defineProperty(t, e, {
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
function H(t) {
  for (var e = 1; e < arguments.length; e++) {
    var n = arguments[e] != null ? arguments[e] : {};
    e % 2 ? at(Object(n), !0).forEach(function(o) {
      R(t, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(n)) : at(Object(n)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return t;
}
var Ur = `accept acceptCharset accessKey action allowFullScreen allowTransparency
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
    summary tabIndex target title type useMap value width wmode wrap`, Gr = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, Kr = "".concat(Ur, " ").concat(Gr).split(/[\s\n]+/), qr = "aria-", Yr = "data-";
function ct(t, e) {
  return t.indexOf(e) === 0;
}
function Qr(t) {
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
    (n.aria && (r === "role" || ct(r, qr)) || // Data
    n.data && ct(r, Yr) || // Attr
    n.attr && Kr.includes(r)) && (o[r] = t[r]);
  }), o;
}
const Zr = /* @__PURE__ */ h.createContext({}), Jr = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, en = (t) => {
  const e = h.useContext(Zr);
  return h.useMemo(() => ({
    ...Jr,
    ...e[t]
  }), [e[t]]);
};
function me() {
  const {
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = h.useContext(Qt.ConfigContext);
  return {
    theme: r,
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o
  };
}
function tn(t) {
  if (Array.isArray(t)) return t;
}
function rn(t, e) {
  var n = t == null ? null : typeof Symbol < "u" && t[Symbol.iterator] || t["@@iterator"];
  if (n != null) {
    var o, r, i, s, a = [], c = !0, l = !1;
    try {
      if (i = (n = n.call(t)).next, e === 0) {
        if (Object(n) !== n) return;
        c = !1;
      } else for (; !(c = (o = i.call(n)).done) && (a.push(o.value), a.length !== e); c = !0) ;
    } catch (f) {
      l = !0, r = f;
    } finally {
      try {
        if (!c && n.return != null && (s = n.return(), Object(s) !== s)) return;
      } finally {
        if (l) throw r;
      }
    }
    return a;
  }
}
function lt(t, e) {
  (e == null || e > t.length) && (e = t.length);
  for (var n = 0, o = Array(e); n < e; n++) o[n] = t[n];
  return o;
}
function nn(t, e) {
  if (t) {
    if (typeof t == "string") return lt(t, e);
    var n = {}.toString.call(t).slice(8, -1);
    return n === "Object" && t.constructor && (n = t.constructor.name), n === "Map" || n === "Set" ? Array.from(t) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? lt(t, e) : void 0;
  }
}
function on() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function he(t, e) {
  return tn(t) || rn(t, e) || nn(t, e) || on();
}
function ye(t, e) {
  if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function");
}
function sn(t, e) {
  for (var n = 0; n < e.length; n++) {
    var o = e[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, Mt(o.key), o);
  }
}
function ve(t, e, n) {
  return e && sn(t.prototype, e), Object.defineProperty(t, "prototype", {
    writable: !1
  }), t;
}
function oe(t) {
  if (t === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return t;
}
function Fe(t, e) {
  return Fe = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, Fe(t, e);
}
function Pt(t, e) {
  if (typeof e != "function" && e !== null) throw new TypeError("Super expression must either be null or a function");
  t.prototype = Object.create(e && e.prototype, {
    constructor: {
      value: t,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(t, "prototype", {
    writable: !1
  }), e && Fe(t, e);
}
function pe(t) {
  return pe = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
    return e.__proto__ || Object.getPrototypeOf(e);
  }, pe(t);
}
function Ot() {
  try {
    var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Ot = function() {
    return !!t;
  })();
}
function an(t, e) {
  if (e && (N(e) == "object" || typeof e == "function")) return e;
  if (e !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return oe(t);
}
function Rt(t) {
  var e = Ot();
  return function() {
    var n, o = pe(t);
    if (e) {
      var r = pe(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return an(this, n);
  };
}
var It = /* @__PURE__ */ ve(function t() {
  ye(this, t);
}), jt = "CALC_UNIT", cn = new RegExp(jt, "g");
function Le(t) {
  return typeof t == "number" ? "".concat(t).concat(jt) : t;
}
var ln = /* @__PURE__ */ function(t) {
  Pt(n, t);
  var e = Rt(n);
  function n(o, r) {
    var i;
    ye(this, n), i = e.call(this), R(oe(i), "result", ""), R(oe(i), "unitlessCssVar", void 0), R(oe(i), "lowPriority", void 0);
    var s = N(o);
    return i.unitlessCssVar = r, o instanceof n ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = Le(o) : s === "string" && (i.result = o), i;
  }
  return ve(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(Le(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(Le(r))), this.lowPriority = !0, this;
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
      var i = this, s = r || {}, a = s.unit, c = !0;
      return typeof a == "boolean" ? c = a : Array.from(this.unitlessCssVar).some(function(l) {
        return i.result.includes(l);
      }) && (c = !1), this.result = this.result.replace(cn, c ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(It), un = /* @__PURE__ */ function(t) {
  Pt(n, t);
  var e = Rt(n);
  function n(o) {
    var r;
    return ye(this, n), r = e.call(this), R(oe(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return ve(n, [{
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
}(It), fn = function(e, n) {
  var o = e === "css" ? ln : un;
  return function(r) {
    return new o(r, n);
  };
}, ut = function(e, n) {
  return "".concat([n, e.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function dn(t) {
  var e = w.useRef();
  e.current = t;
  var n = w.useCallback(function() {
    for (var o, r = arguments.length, i = new Array(r), s = 0; s < r; s++)
      i[s] = arguments[s];
    return (o = e.current) === null || o === void 0 ? void 0 : o.call.apply(o, [e].concat(i));
  }, []);
  return n;
}
function hn() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var ft = hn() ? w.useLayoutEffect : w.useEffect, gn = function(e, n) {
  var o = w.useRef(!0);
  ft(function() {
    return e(o.current);
  }, n), ft(function() {
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
var Xe = Symbol.for("react.element"), Ve = Symbol.for("react.portal"), xe = Symbol.for("react.fragment"), Se = Symbol.for("react.strict_mode"), Ce = Symbol.for("react.profiler"), _e = Symbol.for("react.provider"), we = Symbol.for("react.context"), mn = Symbol.for("react.server_context"), Te = Symbol.for("react.forward_ref"), Ee = Symbol.for("react.suspense"), Me = Symbol.for("react.suspense_list"), Pe = Symbol.for("react.memo"), Oe = Symbol.for("react.lazy"), pn = Symbol.for("react.offscreen"), kt;
kt = Symbol.for("react.module.reference");
function F(t) {
  if (typeof t == "object" && t !== null) {
    var e = t.$$typeof;
    switch (e) {
      case Xe:
        switch (t = t.type, t) {
          case xe:
          case Ce:
          case Se:
          case Ee:
          case Me:
            return t;
          default:
            switch (t = t && t.$$typeof, t) {
              case mn:
              case we:
              case Te:
              case Oe:
              case Pe:
              case _e:
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
T.ContextProvider = _e;
T.Element = Xe;
T.ForwardRef = Te;
T.Fragment = xe;
T.Lazy = Oe;
T.Memo = Pe;
T.Portal = Ve;
T.Profiler = Ce;
T.StrictMode = Se;
T.Suspense = Ee;
T.SuspenseList = Me;
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
  return F(t) === _e;
};
T.isElement = function(t) {
  return typeof t == "object" && t !== null && t.$$typeof === Xe;
};
T.isForwardRef = function(t) {
  return F(t) === Te;
};
T.isFragment = function(t) {
  return F(t) === xe;
};
T.isLazy = function(t) {
  return F(t) === Oe;
};
T.isMemo = function(t) {
  return F(t) === Pe;
};
T.isPortal = function(t) {
  return F(t) === Ve;
};
T.isProfiler = function(t) {
  return F(t) === Ce;
};
T.isStrictMode = function(t) {
  return F(t) === Se;
};
T.isSuspense = function(t) {
  return F(t) === Ee;
};
T.isSuspenseList = function(t) {
  return F(t) === Me;
};
T.isValidElementType = function(t) {
  return typeof t == "string" || typeof t == "function" || t === xe || t === Ce || t === Se || t === Ee || t === Me || t === pn || typeof t == "object" && t !== null && (t.$$typeof === Oe || t.$$typeof === Pe || t.$$typeof === _e || t.$$typeof === we || t.$$typeof === Te || t.$$typeof === kt || t.getModuleId !== void 0);
};
T.typeOf = F;
Number(Vt.split(".")[0]);
function dt(t, e, n, o) {
  var r = H({}, e[t]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var c = he(a, 2), l = c[0], f = c[1];
      if (r != null && r[l] || r != null && r[f]) {
        var u;
        (u = r[f]) !== null && u !== void 0 || (r[f] = r == null ? void 0 : r[l]);
      }
    });
  }
  var s = H(H({}, n), r);
  return Object.keys(s).forEach(function(a) {
    s[a] === e[a] && delete s[a];
  }), s;
}
var Lt = typeof CSSINJS_STATISTIC < "u", Ne = !0;
function We() {
  for (var t = arguments.length, e = new Array(t), n = 0; n < t; n++)
    e[n] = arguments[n];
  if (!Lt)
    return Object.assign.apply(Object, [{}].concat(e));
  Ne = !1;
  var o = {};
  return e.forEach(function(r) {
    if (N(r) === "object") {
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
  }), Ne = !0, o;
}
var ht = {};
function bn() {
}
var yn = function(e) {
  var n, o = e, r = bn;
  return Lt && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(e, {
    get: function(s, a) {
      if (Ne) {
        var c;
        (c = n) === null || c === void 0 || c.add(a);
      }
      return s[a];
    }
  }), r = function(s, a) {
    var c;
    ht[s] = {
      global: Array.from(n),
      component: H(H({}, (c = ht[s]) === null || c === void 0 ? void 0 : c.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function gt(t, e, n) {
  if (typeof n == "function") {
    var o;
    return n(We(e, (o = e[t]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function vn(t) {
  return t === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(i) {
        return ie(i);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(i) {
        return ie(i);
      }).join(","), ")");
    }
  };
}
var xn = 1e3 * 60 * 10, Sn = /* @__PURE__ */ function() {
  function t() {
    ye(this, t), R(this, "map", /* @__PURE__ */ new Map()), R(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), R(this, "nextID", 0), R(this, "lastAccessBeat", /* @__PURE__ */ new Map()), R(this, "accessBeat", 0);
  }
  return ve(t, [{
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
        return i && N(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(N(i), "_").concat(i);
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
          o - r > xn && (n.map.delete(i), n.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), t;
}(), mt = new Sn();
function Cn(t, e) {
  return h.useMemo(function() {
    var n = mt.get(e);
    if (n)
      return n;
    var o = t();
    return mt.set(e, o), o;
  }, e);
}
var _n = function() {
  return {};
};
function wn(t) {
  var e = t.useCSP, n = e === void 0 ? _n : e, o = t.useToken, r = t.usePrefix, i = t.getResetStyles, s = t.getCommonStyle, a = t.getCompUnitless;
  function c(d, x, b, S) {
    var p = Array.isArray(d) ? d[0] : d;
    function y(P) {
      return "".concat(String(p)).concat(P.slice(0, 1).toUpperCase()).concat(P.slice(1));
    }
    var C = (S == null ? void 0 : S.unitless) || {}, j = typeof a == "function" ? a(d) : {}, g = H(H({}, j), {}, R({}, y("zIndexPopup"), !0));
    Object.keys(C).forEach(function(P) {
      g[y(P)] = C[P];
    });
    var v = H(H({}, S), {}, {
      unitless: g,
      prefixToken: y
    }), m = f(d, x, b, v), _ = l(p, b, v);
    return function(P) {
      var I = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : P, E = m(P, I), k = he(E, 2), L = k[1], O = _(I), M = he(O, 2), $ = M[0], A = M[1];
      return [$, L, A];
    };
  }
  function l(d, x, b) {
    var S = b.unitless, p = b.injectStyle, y = p === void 0 ? !0 : p, C = b.prefixToken, j = b.ignore, g = function(_) {
      var P = _.rootCls, I = _.cssVar, E = I === void 0 ? {} : I, k = o(), L = k.realToken;
      return Jt({
        path: [d],
        prefix: E.prefix,
        key: E.key,
        unitless: S,
        ignore: j,
        token: L,
        scope: P
      }, function() {
        var O = gt(d, L, x), M = dt(d, L, O, {
          deprecatedTokens: b == null ? void 0 : b.deprecatedTokens
        });
        return Object.keys(O).forEach(function($) {
          M[C($)] = M[$], delete M[$];
        }), M;
      }), null;
    }, v = function(_) {
      var P = o(), I = P.cssVar;
      return [function(E) {
        return y && I ? /* @__PURE__ */ h.createElement(h.Fragment, null, /* @__PURE__ */ h.createElement(g, {
          rootCls: _,
          cssVar: I,
          component: d
        }), E) : E;
      }, I == null ? void 0 : I.key];
    };
    return v;
  }
  function f(d, x, b) {
    var S = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = Array.isArray(d) ? d : [d, d], y = he(p, 1), C = y[0], j = p.join("-"), g = t.layer || {
      name: "antd"
    };
    return function(v) {
      var m = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : v, _ = o(), P = _.theme, I = _.realToken, E = _.hashId, k = _.token, L = _.cssVar, O = r(), M = O.rootPrefixCls, $ = O.iconPrefixCls, A = n(), z = L ? "css" : "js", V = Cn(function() {
        var W = /* @__PURE__ */ new Set();
        return L && Object.keys(S.unitless || {}).forEach(function(q) {
          W.add(Ie(q, L.prefix)), W.add(Ie(q, ut(C, L.prefix)));
        }), fn(z, W);
      }, [z, C, L == null ? void 0 : L.prefix]), K = vn(z), ee = K.max, se = K.min, Y = {
        theme: P,
        token: k,
        hashId: E,
        nonce: function() {
          return A.nonce;
        },
        clientOnly: S.clientOnly,
        layer: g,
        // antd is always at top of styles
        order: S.order || -999
      };
      typeof i == "function" && Ye(H(H({}, Y), {}, {
        clientOnly: !1,
        path: ["Shared", M]
      }), function() {
        return i(k, {
          prefix: {
            rootPrefixCls: M,
            iconPrefixCls: $
          },
          csp: A
        });
      });
      var Re = Ye(H(H({}, Y), {}, {
        path: [j, v, $]
      }), function() {
        if (S.injectStyle === !1)
          return [];
        var W = yn(k), q = W.token, te = W.flush, X = gt(C, I, b), re = ".".concat(v), Ge = dt(C, I, X, {
          deprecatedTokens: S.deprecatedTokens
        });
        L && X && N(X) === "object" && Object.keys(X).forEach(function(qe) {
          X[qe] = "var(".concat(Ie(qe, ut(C, L.prefix)), ")");
        });
        var Ke = We(q, {
          componentCls: re,
          prefixCls: v,
          iconCls: ".".concat($),
          antCls: ".".concat(M),
          calc: V,
          // @ts-ignore
          max: ee,
          // @ts-ignore
          min: se
        }, L ? X : Ge), Ht = x(Ke, {
          hashId: E,
          prefixCls: v,
          rootPrefixCls: M,
          iconPrefixCls: $
        });
        te(C, Ge);
        var At = typeof s == "function" ? s(Ke, v, m, S.resetFont) : null;
        return [S.resetStyle === !1 ? null : At, Ht];
      });
      return [Re, E];
    };
  }
  function u(d, x, b) {
    var S = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = f(d, x, b, H({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, S)), y = function(j) {
      var g = j.prefixCls, v = j.rootCls, m = v === void 0 ? g : v;
      return p(g, m), null;
    };
    return y;
  }
  return {
    genStyleHooks: c,
    genSubStyleComponent: u,
    genComponentStyleHook: f
  };
}
const Tn = {
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
}, En = Object.assign(Object.assign({}, Tn), {
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
}), D = Math.round;
function $e(t, e) {
  const n = t.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = e(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const pt = (t, e, n) => n === 0 ? t : t / 100;
function ne(t, e) {
  const n = e || 255;
  return t > n ? n : t < 0 ? 0 : t;
}
class G {
  constructor(e) {
    R(this, "isValid", !0), R(this, "r", 0), R(this, "g", 0), R(this, "b", 0), R(this, "a", 1), R(this, "_h", void 0), R(this, "_s", void 0), R(this, "_l", void 0), R(this, "_v", void 0), R(this, "_max", void 0), R(this, "_min", void 0), R(this, "_brightness", void 0);
    function n(o) {
      return o[0] in e && o[1] in e && o[2] in e;
    }
    if (e) if (typeof e == "string") {
      let r = function(i) {
        return o.startsWith(i);
      };
      const o = e.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (e instanceof G)
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
      e === 0 ? this._h = 0 : this._h = D(60 * (this.r === this.getMax() ? (this.g - this.b) / e + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / e + 2 : (this.r - this.g) / e + 4));
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
      r: D(i("r")),
      g: D(i("g")),
      b: D(i("b")),
      a: D(i("a") * 100) / 100
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
    const n = this._c(e), o = this.a + n.a * (1 - this.a), r = (i) => D((this[i] * this.a + n[i] * n.a * (1 - this.a)) / o);
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
      const i = D(this.a * 255).toString(16);
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
    const e = this.getHue(), n = D(this.getSaturation() * 100), o = D(this.getLightness() * 100);
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
      const d = D(o * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let i = 0, s = 0, a = 0;
    const c = e / 60, l = (1 - Math.abs(2 * o - 1)) * n, f = l * (1 - Math.abs(c % 2 - 1));
    c >= 0 && c < 1 ? (i = l, s = f) : c >= 1 && c < 2 ? (i = f, s = l) : c >= 2 && c < 3 ? (s = l, a = f) : c >= 3 && c < 4 ? (s = f, a = l) : c >= 4 && c < 5 ? (i = f, a = l) : c >= 5 && c < 6 && (i = l, a = f);
    const u = o - l / 2;
    this.r = D((i + u) * 255), this.g = D((s + u) * 255), this.b = D((a + u) * 255);
  }
  fromHsv({
    h: e,
    s: n,
    v: o,
    a: r
  }) {
    this._h = e % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const i = D(o * 255);
    if (this.r = i, this.g = i, this.b = i, n <= 0)
      return;
    const s = e / 60, a = Math.floor(s), c = s - a, l = D(o * (1 - n) * 255), f = D(o * (1 - n * c) * 255), u = D(o * (1 - n * (1 - c)) * 255);
    switch (a) {
      case 0:
        this.g = u, this.b = l;
        break;
      case 1:
        this.r = f, this.b = l;
        break;
      case 2:
        this.r = l, this.b = u;
        break;
      case 3:
        this.r = l, this.g = f;
        break;
      case 4:
        this.r = u, this.g = l;
        break;
      case 5:
      default:
        this.g = l, this.b = f;
        break;
    }
  }
  fromHsvString(e) {
    const n = $e(e, pt);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(e) {
    const n = $e(e, pt);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(e) {
    const n = $e(e, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? D(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function Be(t) {
  return t >= 0 && t <= 255;
}
function ae(t, e) {
  const {
    r: n,
    g: o,
    b: r,
    a: i
  } = new G(t).toRgb();
  if (i < 1)
    return t;
  const {
    r: s,
    g: a,
    b: c
  } = new G(e).toRgb();
  for (let l = 0.01; l <= 1; l += 0.01) {
    const f = Math.round((n - s * (1 - l)) / l), u = Math.round((o - a * (1 - l)) / l), d = Math.round((r - c * (1 - l)) / l);
    if (Be(f) && Be(u) && Be(d))
      return new G({
        r: f,
        g: u,
        b: d,
        a: Math.round(l * 100) / 100
      }).toRgbString();
  }
  return new G({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var Mn = function(t, e) {
  var n = {};
  for (var o in t) Object.prototype.hasOwnProperty.call(t, o) && e.indexOf(o) < 0 && (n[o] = t[o]);
  if (t != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(t); r < o.length; r++)
    e.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(t, o[r]) && (n[o[r]] = t[o[r]]);
  return n;
};
function Pn(t) {
  const {
    override: e
  } = t, n = Mn(t, ["override"]), o = Object.assign({}, e);
  Object.keys(En).forEach((d) => {
    delete o[d];
  });
  const r = Object.assign(Object.assign({}, n), o), i = 480, s = 576, a = 768, c = 992, l = 1200, f = 1600;
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
    screenXLMax: f - 1,
    screenXXL: f,
    screenXXLMin: f,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new G("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new G("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new G("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const On = {
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
}, Rn = {
  motionBase: !0,
  motionUnit: !0
}, In = er(He.defaultAlgorithm), jn = {
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
}, $t = (t, e, n) => {
  const o = n.getDerivativeToken(t), {
    override: r,
    ...i
  } = e;
  let s = {
    ...o,
    override: r
  };
  return s = Pn(s), i && Object.entries(i).forEach(([a, c]) => {
    const {
      theme: l,
      ...f
    } = c;
    let u = f;
    l && (u = $t({
      ...s,
      ...f
    }, {
      override: f
    }, l)), s[a] = u;
  }), s;
};
function kn() {
  const {
    token: t,
    hashed: e,
    theme: n = In,
    override: o,
    cssVar: r
  } = h.useContext(He._internalContext), [i, s, a] = tr(n, [He.defaultSeed, t], {
    salt: `${Vr}-${e || ""}`,
    override: o,
    getComputedToken: $t,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: On,
      ignore: Rn,
      preserve: jn
    }
  });
  return [n, a, e ? s : "", i, r];
}
const {
  genStyleHooks: Ln
} = wn({
  usePrefix: () => {
    const {
      getPrefixCls: t,
      iconPrefixCls: e
    } = me();
    return {
      iconPrefixCls: e,
      rootPrefixCls: t()
    };
  },
  useToken: () => {
    const [t, e, n, o, r] = kn();
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
    } = me();
    return t ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
});
function ce(t) {
  return typeof t == "string";
}
const $n = (t, e, n, o) => {
  const r = w.useRef(""), [i, s] = w.useState(1), a = e && ce(t);
  return gn(() => {
    !a && ce(t) ? s(t.length) : ce(t) && ce(r.current) && t.indexOf(r.current) !== 0 && s(1), r.current = t;
  }, [t]), w.useEffect(() => {
    if (a && i < t.length) {
      const l = setTimeout(() => {
        s((f) => f + n);
      }, o);
      return () => {
        clearTimeout(l);
      };
    }
  }, [i, e, t]), [a ? t.slice(0, i) : t, a && i < t.length];
};
function Bn(t) {
  return w.useMemo(() => {
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
const Dn = ({
  prefixCls: t
}) => /* @__PURE__ */ h.createElement("span", {
  className: `${t}-dot`
}, /* @__PURE__ */ h.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-1"
}), /* @__PURE__ */ h.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-2"
}), /* @__PURE__ */ h.createElement("i", {
  className: `${t}-dot-item`,
  key: "item-3"
})), Hn = (t) => {
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
          padding: `${ie(n)} ${ie(o)}`,
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
}, An = (t) => {
  const {
    componentCls: e,
    fontSize: n,
    lineHeight: o,
    paddingSM: r,
    padding: i,
    calc: s
  } = t, a = s(n).mul(o).div(2).add(r).equal(), c = `${e}-content`;
  return {
    [e]: {
      [c]: {
        // round:
        "&-round": {
          borderRadius: {
            _skip_check_: !0,
            value: a
          },
          paddingInline: s(i).mul(1.25).equal()
        }
      },
      // corner:
      [`&-start ${c}-corner`]: {
        borderStartStartRadius: t.borderRadiusXS
      },
      [`&-end ${c}-corner`]: {
        borderStartEndRadius: t.borderRadiusXS
      }
    }
  };
}, zn = (t) => {
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
}, Fn = new xt("loadingMove", {
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
}), Nn = new xt("cursorBlink", {
  "0%": {
    opacity: 1
  },
  "50%": {
    opacity: 0
  },
  "100%": {
    opacity: 1
  }
}), Xn = (t) => {
  const {
    componentCls: e,
    fontSize: n,
    lineHeight: o,
    paddingSM: r,
    colorText: i,
    calc: s
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
        animationName: Nn,
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
        color: i,
        fontSize: t.fontSize,
        lineHeight: t.lineHeight,
        minHeight: s(r).mul(2).add(s(o).mul(n)).equal(),
        wordBreak: "break-word",
        [`& ${e}-dot`]: {
          position: "relative",
          height: "100%",
          display: "flex",
          alignItems: "center",
          columnGap: t.marginXS,
          padding: `0 ${ie(t.paddingXXS)}`,
          "&-item": {
            backgroundColor: t.colorPrimary,
            borderRadius: "100%",
            width: 4,
            height: 4,
            animationName: Fn,
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
}, Vn = () => ({}), Bt = Ln("Bubble", (t) => {
  const e = We(t, {});
  return [Xn(e), zn(e), Hn(e), An(e)];
}, Vn), Dt = /* @__PURE__ */ h.createContext({}), Wn = (t, e) => {
  const {
    prefixCls: n,
    className: o,
    rootClassName: r,
    style: i,
    classNames: s = {},
    styles: a = {},
    avatar: c,
    placement: l = "start",
    loading: f = !1,
    loadingRender: u,
    typing: d,
    content: x = "",
    messageRender: b,
    variant: S = "filled",
    shape: p,
    onTypingComplete: y,
    header: C,
    footer: j,
    _key: g,
    ...v
  } = t, {
    onUpdate: m
  } = h.useContext(Dt), _ = h.useRef(null);
  h.useImperativeHandle(e, () => ({
    nativeElement: _.current
  }));
  const {
    direction: P,
    getPrefixCls: I
  } = me(), E = I("bubble", n), k = en("bubble"), [L, O, M, $] = Bn(d), [A, z] = $n(x, L, O, M);
  h.useEffect(() => {
    m == null || m();
  }, [A]);
  const V = h.useRef(!1);
  h.useEffect(() => {
    !z && !f ? V.current || (V.current = !0, y == null || y()) : V.current = !1;
  }, [z, f]);
  const [K, ee, se] = Bt(E), Y = Q(E, r, k.className, o, ee, se, `${E}-${l}`, {
    [`${E}-rtl`]: P === "rtl",
    [`${E}-typing`]: z && !f && !b && !$
  }), Re = h.useMemo(() => /* @__PURE__ */ h.isValidElement(c) ? c : /* @__PURE__ */ h.createElement(Zt, c), [c]), W = h.useMemo(() => b ? b(A) : A, [A, b]), q = (re) => typeof re == "function" ? re(A, {
    key: g
  }) : re;
  let te;
  f ? te = u ? u() : /* @__PURE__ */ h.createElement(Dn, {
    prefixCls: E
  }) : te = /* @__PURE__ */ h.createElement(h.Fragment, null, W, z && $);
  let X = /* @__PURE__ */ h.createElement("div", {
    style: {
      ...k.styles.content,
      ...a.content
    },
    className: Q(`${E}-content`, `${E}-content-${S}`, p && `${E}-content-${p}`, k.classNames.content, s.content)
  }, te);
  return (C || j) && (X = /* @__PURE__ */ h.createElement("div", {
    className: `${E}-content-wrapper`
  }, C && /* @__PURE__ */ h.createElement("div", {
    className: Q(`${E}-header`, k.classNames.header, s.header),
    style: {
      ...k.styles.header,
      ...a.header
    }
  }, q(C)), X, j && /* @__PURE__ */ h.createElement("div", {
    className: Q(`${E}-footer`, k.classNames.footer, s.footer),
    style: {
      ...k.styles.footer,
      ...a.footer
    }
  }, q(j)))), K(/* @__PURE__ */ h.createElement("div", J({
    style: {
      ...k.style,
      ...i
    },
    className: Y
  }, v, {
    ref: _
  }), c && /* @__PURE__ */ h.createElement("div", {
    style: {
      ...k.styles.avatar,
      ...a.avatar
    },
    className: Q(`${E}-avatar`, k.classNames.avatar, s.avatar)
  }, Re), X));
}, Ue = /* @__PURE__ */ h.forwardRef(Wn);
function Un(t, e) {
  const n = w.useCallback((o, r) => typeof e == "function" ? e(o, r) : e ? e[o.role] || {} : {}, [e]);
  return w.useMemo(() => (t || []).map((o, r) => {
    const i = o.key ?? `preset_${r}`;
    return {
      ...n(o, r),
      ...o,
      key: i
    };
  }), [t, n]);
}
const Gn = ({
  _key: t,
  ...e
}, n) => /* @__PURE__ */ w.createElement(Ue, J({}, e, {
  _key: t,
  ref: (o) => {
    var r;
    o ? n.current[t] = o : (r = n.current) == null || delete r[t];
  }
})), Kn = /* @__PURE__ */ w.memo(/* @__PURE__ */ w.forwardRef(Gn)), qn = 1, Yn = (t, e) => {
  const {
    prefixCls: n,
    rootClassName: o,
    className: r,
    items: i,
    autoScroll: s = !0,
    roles: a,
    onScroll: c,
    ...l
  } = t, f = Qr(l, {
    attr: !0,
    aria: !0
  }), u = w.useRef(null), d = w.useRef({}), {
    getPrefixCls: x
  } = me(), b = x("bubble", n), S = `${b}-list`, [p, y, C] = Bt(b), [j, g] = w.useState(!1);
  w.useEffect(() => (g(!0), () => {
    g(!1);
  }), []);
  const v = Un(i, a), [m, _] = w.useState(!0), [P, I] = w.useState(0), E = (O) => {
    const M = O.target;
    _(M.scrollHeight - Math.abs(M.scrollTop) - M.clientHeight <= qn), c == null || c(O);
  };
  w.useEffect(() => {
    s && u.current && m && u.current.scrollTo({
      top: u.current.scrollHeight
    });
  }, [P]), w.useEffect(() => {
    var O;
    if (s) {
      const M = (O = v[v.length - 2]) == null ? void 0 : O.key, $ = d.current[M];
      if ($) {
        const {
          nativeElement: A
        } = $, {
          top: z,
          bottom: V
        } = A.getBoundingClientRect(), {
          top: K,
          bottom: ee
        } = u.current.getBoundingClientRect();
        z < ee && V > K && (I((Y) => Y + 1), _(!0));
      }
    }
  }, [v.length]), w.useImperativeHandle(e, () => ({
    nativeElement: u.current,
    scrollTo: ({
      key: O,
      offset: M,
      behavior: $ = "smooth",
      block: A
    }) => {
      if (typeof M == "number")
        u.current.scrollTo({
          top: M,
          behavior: $
        });
      else if (O !== void 0) {
        const z = d.current[O];
        if (z) {
          const V = v.findIndex((K) => K.key === O);
          _(V === v.length - 1), z.nativeElement.scrollIntoView({
            behavior: $,
            block: A
          });
        }
      }
    }
  }));
  const k = dn(() => {
    s && I((O) => O + 1);
  }), L = w.useMemo(() => ({
    onUpdate: k
  }), []);
  return p(/* @__PURE__ */ w.createElement(Dt.Provider, {
    value: L
  }, /* @__PURE__ */ w.createElement("div", J({}, f, {
    className: Q(S, o, r, y, C, {
      [`${S}-reach-end`]: m
    }),
    ref: u,
    onScroll: E
  }), v.map(({
    key: O,
    ...M
  }) => /* @__PURE__ */ w.createElement(Kn, J({}, M, {
    key: O,
    _key: O,
    ref: d,
    typing: j ? M.typing : !1
  }))))));
}, Qn = /* @__PURE__ */ w.forwardRef(Yn);
Ue.List = Qn;
function Zn(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function Jn(t, e = !1) {
  try {
    if (Kt(t))
      return t;
    if (e && !Zn(t))
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
function le(t, e) {
  return vt(() => Jn(t, e), [t, e]);
}
const eo = ({
  children: t,
  ...e
}) => /* @__PURE__ */ B.jsx(B.Fragment, {
  children: t(e)
});
function to(t) {
  return h.createElement(eo, {
    children: t
  });
}
function bt(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? to((n) => /* @__PURE__ */ B.jsx(Yt, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ B.jsx(U, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...n
    })
  })) : /* @__PURE__ */ B.jsx(U, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function yt({
  key: t,
  slots: e,
  targets: n
}, o) {
  return e[t] ? (...r) => n ? n.map((i, s) => /* @__PURE__ */ B.jsx(h.Fragment, {
    children: bt(i, {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }, s)) : /* @__PURE__ */ B.jsx(B.Fragment, {
    children: bt(e[t], {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }) : void 0;
}
const oo = Ar(({
  loadingRender: t,
  messageRender: e,
  slots: n,
  setSlotParams: o,
  children: r,
  ...i
}) => {
  const s = le(t), a = le(e), c = le(i.header, !0), l = le(i.footer, !0), f = vt(() => {
    var u, d;
    return n.avatar ? /* @__PURE__ */ B.jsx(U, {
      slot: n.avatar
    }) : n["avatar.icon"] || n["avatar.src"] ? {
      ...i.avatar || {},
      icon: n["avatar.icon"] ? /* @__PURE__ */ B.jsx(U, {
        slot: n["avatar.icon"]
      }) : (u = i.avatar) == null ? void 0 : u.icon,
      src: n["avatar.src"] ? /* @__PURE__ */ B.jsx(U, {
        slot: n["avatar.src"]
      }) : (d = i.avatar) == null ? void 0 : d.src
    } : i.avatar;
  }, [i.avatar, n]);
  return /* @__PURE__ */ B.jsxs(B.Fragment, {
    children: [/* @__PURE__ */ B.jsx("div", {
      style: {
        display: "none"
      },
      children: r
    }), /* @__PURE__ */ B.jsx(Ue, {
      ...i,
      avatar: f,
      typing: n["typing.suffix"] ? {
        ...ge(i.typing) ? i.typing : {},
        suffix: /* @__PURE__ */ B.jsx(U, {
          slot: n["typing.suffix"]
        })
      } : i.typing,
      content: n.content ? /* @__PURE__ */ B.jsx(U, {
        slot: n.content
      }) : i.content,
      footer: n.footer ? /* @__PURE__ */ B.jsx(U, {
        slot: n.footer
      }) : l || i.footer,
      header: n.header ? /* @__PURE__ */ B.jsx(U, {
        slot: n.header
      }) : c || i.header,
      loadingRender: n.loadingRender ? yt({
        slots: n,
        key: "loadingRender"
      }) : s,
      messageRender: n.messageRender ? yt({
        slots: n,
        key: "messageRender"
      }) : a
    })]
  });
});
export {
  oo as Bubble,
  oo as default
};
