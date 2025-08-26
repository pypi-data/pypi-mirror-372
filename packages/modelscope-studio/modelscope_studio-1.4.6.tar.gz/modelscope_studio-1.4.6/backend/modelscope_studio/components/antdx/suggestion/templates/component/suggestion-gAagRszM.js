import { i as Wt, a as oe, r as Gt, b as Kt, Z as te, g as qt, c as Ue, d as St } from "./Index-CAFfSlLd.js";
const z = window.ms_globals.React, w = window.ms_globals.React, vt = window.ms_globals.React.forwardRef, yt = window.ms_globals.React.useRef, He = window.ms_globals.React.useState, xt = window.ms_globals.React.useEffect, Ut = window.ms_globals.React.version, J = window.ms_globals.React.useMemo, Ee = window.ms_globals.ReactDOM.createPortal, Qt = window.ms_globals.internalContext.useContextPropsContext, We = window.ms_globals.internalContext.ContextPropsProvider, Zt = window.ms_globals.internalContext.SuggestionOpenContext, Jt = window.ms_globals.internalContext.SuggestionContext, Yt = window.ms_globals.createItemsContext.createItemsContext, er = window.ms_globals.antd.ConfigProvider, Me = window.ms_globals.antd.theme, tr = window.ms_globals.antd.Cascader, rr = window.ms_globals.antd.version, nr = window.ms_globals.antd.Flex, Ge = window.ms_globals.antdCssinjs.unit, xe = window.ms_globals.antdCssinjs.token2CSSVar, Ke = window.ms_globals.antdCssinjs.useStyleRegister, or = window.ms_globals.antdCssinjs.useCSSVarRegister, sr = window.ms_globals.antdCssinjs.createTheme, ir = window.ms_globals.antdCssinjs.useCacheToken;
var ar = /\s/;
function cr(t) {
  for (var e = t.length; e-- && ar.test(t.charAt(e)); )
    ;
  return e;
}
var lr = /^\s+/;
function ur(t) {
  return t && t.slice(0, cr(t) + 1).replace(lr, "");
}
var qe = NaN, fr = /^[-+]0x[0-9a-f]+$/i, hr = /^0b[01]+$/i, dr = /^0o[0-7]+$/i, gr = parseInt;
function Qe(t) {
  if (typeof t == "number")
    return t;
  if (Wt(t))
    return qe;
  if (oe(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = oe(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = ur(t);
  var n = hr.test(t);
  return n || dr.test(t) ? gr(t.slice(2), n ? 2 : 8) : fr.test(t) ? qe : +t;
}
var Se = function() {
  return Gt.Date.now();
}, pr = "Expected a function", mr = Math.max, br = Math.min;
function vr(t, e, n) {
  var o, r, s, i, a, c, l = 0, d = !1, u = !1, h = !0;
  if (typeof t != "function")
    throw new TypeError(pr);
  e = Qe(e) || 0, oe(n) && (d = !!n.leading, u = "maxWait" in n, s = u ? mr(Qe(n.maxWait) || 0, e) : s, h = "trailing" in n ? !!n.trailing : h);
  function f(x) {
    var T = o, _ = r;
    return o = r = void 0, l = x, i = t.apply(_, T), i;
  }
  function b(x) {
    return l = x, a = setTimeout(m, e), d ? f(x) : i;
  }
  function g(x) {
    var T = x - c, _ = x - l, E = e - T;
    return u ? br(E, s - _) : E;
  }
  function p(x) {
    var T = x - c, _ = x - l;
    return c === void 0 || T >= e || T < 0 || u && _ >= s;
  }
  function m() {
    var x = Se();
    if (p(x))
      return v(x);
    a = setTimeout(m, g(x));
  }
  function v(x) {
    return a = void 0, h && o ? f(x) : (o = r = void 0, i);
  }
  function S() {
    a !== void 0 && clearTimeout(a), l = 0, o = c = r = a = void 0;
  }
  function y() {
    return a === void 0 ? i : v(Se());
  }
  function O() {
    var x = Se(), T = p(x);
    if (o = arguments, r = this, c = x, T) {
      if (a === void 0)
        return b(c);
      if (u)
        return clearTimeout(a), a = setTimeout(m, e), f(c);
    }
    return a === void 0 && (a = setTimeout(m, e)), i;
  }
  return O.cancel = S, O.flush = y, O;
}
function yr(t, e) {
  return Kt(t, e);
}
function Ze(t) {
  return t === void 0;
}
var Ct = {
  exports: {}
}, ae = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var xr = w, Sr = Symbol.for("react.element"), Cr = Symbol.for("react.fragment"), _r = Object.prototype.hasOwnProperty, wr = xr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Or = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function _t(t, e, n) {
  var o, r = {}, s = null, i = null;
  n !== void 0 && (s = "" + n), e.key !== void 0 && (s = "" + e.key), e.ref !== void 0 && (i = e.ref);
  for (o in e) _r.call(e, o) && !Or.hasOwnProperty(o) && (r[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) r[o] === void 0 && (r[o] = e[o]);
  return {
    $$typeof: Sr,
    type: t,
    key: s,
    ref: i,
    props: r,
    _owner: wr.current
  };
}
ae.Fragment = Cr;
ae.jsx = _t;
ae.jsxs = _t;
Ct.exports = ae;
var A = Ct.exports;
const {
  SvelteComponent: Tr,
  assign: Je,
  binding_callbacks: Ye,
  check_outros: Pr,
  children: wt,
  claim_element: Ot,
  claim_space: Er,
  component_subscribe: et,
  compute_slots: Mr,
  create_slot: Ir,
  detach: K,
  element: Tt,
  empty: tt,
  exclude_internal_props: rt,
  get_all_dirty_from_scope: kr,
  get_slot_changes: jr,
  group_outros: Rr,
  init: Lr,
  insert_hydration: re,
  safe_not_equal: Ar,
  set_custom_element_data: Pt,
  space: Dr,
  transition_in: ne,
  transition_out: Ie,
  update_slot_base: Hr
} = window.__gradio__svelte__internal, {
  beforeUpdate: $r,
  getContext: Br,
  onDestroy: Fr,
  setContext: Vr
} = window.__gradio__svelte__internal;
function nt(t) {
  let e, n;
  const o = (
    /*#slots*/
    t[7].default
  ), r = Ir(
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
    l(s) {
      e = Ot(s, "SVELTE-SLOT", {
        class: !0
      });
      var i = wt(e);
      r && r.l(i), i.forEach(K), this.h();
    },
    h() {
      Pt(e, "class", "svelte-1rt0kpf");
    },
    m(s, i) {
      re(s, e, i), r && r.m(e, null), t[9](e), n = !0;
    },
    p(s, i) {
      r && r.p && (!n || i & /*$$scope*/
      64) && Hr(
        r,
        o,
        s,
        /*$$scope*/
        s[6],
        n ? jr(
          o,
          /*$$scope*/
          s[6],
          i,
          null
        ) : kr(
          /*$$scope*/
          s[6]
        ),
        null
      );
    },
    i(s) {
      n || (ne(r, s), n = !0);
    },
    o(s) {
      Ie(r, s), n = !1;
    },
    d(s) {
      s && K(e), r && r.d(s), t[9](null);
    }
  };
}
function zr(t) {
  let e, n, o, r, s = (
    /*$$slots*/
    t[4].default && nt(t)
  );
  return {
    c() {
      e = Tt("react-portal-target"), n = Dr(), s && s.c(), o = tt(), this.h();
    },
    l(i) {
      e = Ot(i, "REACT-PORTAL-TARGET", {
        class: !0
      }), wt(e).forEach(K), n = Er(i), s && s.l(i), o = tt(), this.h();
    },
    h() {
      Pt(e, "class", "svelte-1rt0kpf");
    },
    m(i, a) {
      re(i, e, a), t[8](e), re(i, n, a), s && s.m(i, a), re(i, o, a), r = !0;
    },
    p(i, [a]) {
      /*$$slots*/
      i[4].default ? s ? (s.p(i, a), a & /*$$slots*/
      16 && ne(s, 1)) : (s = nt(i), s.c(), ne(s, 1), s.m(o.parentNode, o)) : s && (Rr(), Ie(s, 1, 1, () => {
        s = null;
      }), Pr());
    },
    i(i) {
      r || (ne(s), r = !0);
    },
    o(i) {
      Ie(s), r = !1;
    },
    d(i) {
      i && (K(e), K(n), K(o)), t[8](null), s && s.d(i);
    }
  };
}
function ot(t) {
  const {
    svelteInit: e,
    ...n
  } = t;
  return n;
}
function Xr(t, e, n) {
  let o, r, {
    $$slots: s = {},
    $$scope: i
  } = e;
  const a = Mr(s);
  let {
    svelteInit: c
  } = e;
  const l = te(ot(e)), d = te();
  et(t, d, (y) => n(0, o = y));
  const u = te();
  et(t, u, (y) => n(1, r = y));
  const h = [], f = Br("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: g,
    subSlotIndex: p
  } = qt() || {}, m = c({
    parent: f,
    props: l,
    target: d,
    slot: u,
    slotKey: b,
    slotIndex: g,
    subSlotIndex: p,
    onDestroy(y) {
      h.push(y);
    }
  });
  Vr("$$ms-gr-react-wrapper", m), $r(() => {
    l.set(ot(e));
  }), Fr(() => {
    h.forEach((y) => y());
  });
  function v(y) {
    Ye[y ? "unshift" : "push"](() => {
      o = y, d.set(o);
    });
  }
  function S(y) {
    Ye[y ? "unshift" : "push"](() => {
      r = y, u.set(r);
    });
  }
  return t.$$set = (y) => {
    n(17, e = Je(Je({}, e), rt(y))), "svelteInit" in y && n(5, c = y.svelteInit), "$$scope" in y && n(6, i = y.$$scope);
  }, e = rt(e), [o, r, d, u, a, c, i, s, v, S];
}
class Nr extends Tr {
  constructor(e) {
    super(), Lr(this, e, Xr, zr, Ar, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Zn
} = window.__gradio__svelte__internal, st = window.ms_globals.rerender, Ce = window.ms_globals.tree;
function Ur(t, e = {}) {
  function n(o) {
    const r = te(), s = new Nr({
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
          }, c = i.parent ?? Ce;
          return c.nodes = [...c.nodes, a], st({
            createPortal: Ee,
            node: Ce
          }), i.onDestroy(() => {
            c.nodes = c.nodes.filter((l) => l.svelteInstance !== r), st({
              createPortal: Ee,
              node: Ce
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
const Wr = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Gr(t) {
  return t ? Object.keys(t).reduce((e, n) => {
    const o = t[n];
    return e[n] = Kr(n, o), e;
  }, {}) : {};
}
function Kr(t, e) {
  return typeof e == "number" && !Wr.includes(t) ? e + "px" : e;
}
function ke(t) {
  const e = [], n = t.cloneNode(!1);
  if (t._reactElement) {
    const r = w.Children.toArray(t._reactElement.props.children).map((s) => {
      if (w.isValidElement(s) && s.props.__slot__) {
        const {
          portals: i,
          clonedElement: a
        } = ke(s.props.el);
        return w.cloneElement(s, {
          ...s.props,
          el: a,
          children: [...w.Children.toArray(s.props.children), ...i]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(Ee(w.cloneElement(t._reactElement, {
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
      useCapture: c
    }) => {
      n.addEventListener(a, i, c);
    });
  });
  const o = Array.from(t.childNodes);
  for (let r = 0; r < o.length; r++) {
    const s = o[r];
    if (s.nodeType === 1) {
      const {
        clonedElement: i,
        portals: a
      } = ke(s);
      e.push(...a), n.appendChild(i);
    } else s.nodeType === 3 && n.appendChild(s.cloneNode());
  }
  return {
    clonedElement: n,
    portals: e
  };
}
function qr(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const je = vt(({
  slot: t,
  clone: e,
  className: n,
  style: o,
  observeAttributes: r
}, s) => {
  const i = yt(), [a, c] = He([]), {
    forceClone: l
  } = Qt(), d = l ? !0 : e;
  return xt(() => {
    var g;
    if (!i.current || !t)
      return;
    let u = t;
    function h() {
      let p = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (p = u.children[0], p.tagName.toLowerCase() === "react-portal-target" && p.children[0] && (p = p.children[0])), qr(s, p), n && p.classList.add(...n.split(" ")), o) {
        const m = Gr(o);
        Object.keys(m).forEach((v) => {
          p.style[v] = m[v];
        });
      }
    }
    let f = null, b = null;
    if (d && window.MutationObserver) {
      let p = function() {
        var y, O, x;
        (y = i.current) != null && y.contains(u) && ((O = i.current) == null || O.removeChild(u));
        const {
          portals: v,
          clonedElement: S
        } = ke(t);
        u = S, c(v), u.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          h();
        }, 50), (x = i.current) == null || x.appendChild(u);
      };
      p();
      const m = vr(() => {
        p(), f == null || f.disconnect(), f == null || f.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      f = new window.MutationObserver(m), f.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", h(), (g = i.current) == null || g.appendChild(u);
    return () => {
      var p, m;
      u.style.display = "", (p = i.current) != null && p.contains(u) && ((m = i.current) == null || m.removeChild(u)), f == null || f.disconnect();
    };
  }, [t, d, n, o, s, r, l]), w.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...a);
}), Qr = "1.6.0";
function Re() {
  return Re = Object.assign ? Object.assign.bind() : function(t) {
    for (var e = 1; e < arguments.length; e++) {
      var n = arguments[e];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (t[o] = n[o]);
    }
    return t;
  }, Re.apply(null, arguments);
}
function $(t) {
  "@babel/helpers - typeof";
  return $ = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, $(t);
}
function Zr(t, e) {
  if ($(t) != "object" || !t) return t;
  var n = t[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(t, e);
    if ($(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function Et(t) {
  var e = Zr(t, "string");
  return $(e) == "symbol" ? e : e + "";
}
function P(t, e, n) {
  return (e = Et(e)) in t ? Object.defineProperty(t, e, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : t[e] = n, t;
}
function it(t, e) {
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
    e % 2 ? it(Object(n), !0).forEach(function(o) {
      P(t, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(t, Object.getOwnPropertyDescriptors(n)) : it(Object(n)).forEach(function(o) {
      Object.defineProperty(t, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return t;
}
const Jr = /* @__PURE__ */ w.createContext({}), Yr = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, en = (t) => {
  const e = w.useContext(Jr);
  return w.useMemo(() => ({
    ...Yr,
    ...e[t]
  }), [e[t]]);
};
function Le() {
  const {
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = w.useContext(er.ConfigContext);
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
    var o, r, s, i, a = [], c = !0, l = !1;
    try {
      if (s = (n = n.call(t)).next, e === 0) {
        if (Object(n) !== n) return;
        c = !1;
      } else for (; !(c = (o = s.call(n)).done) && (a.push(o.value), a.length !== e); c = !0) ;
    } catch (d) {
      l = !0, r = d;
    } finally {
      try {
        if (!c && n.return != null && (i = n.return(), Object(i) !== i)) return;
      } finally {
        if (l) throw r;
      }
    }
    return a;
  }
}
function at(t, e) {
  (e == null || e > t.length) && (e = t.length);
  for (var n = 0, o = Array(e); n < e; n++) o[n] = t[n];
  return o;
}
function nn(t, e) {
  if (t) {
    if (typeof t == "string") return at(t, e);
    var n = {}.toString.call(t).slice(8, -1);
    return n === "Object" && t.constructor && (n = t.constructor.name), n === "Map" || n === "Set" ? Array.from(t) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? at(t, e) : void 0;
  }
}
function on() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function N(t, e) {
  return tn(t) || rn(t, e) || nn(t, e) || on();
}
function ce(t, e) {
  if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function");
}
function sn(t, e) {
  for (var n = 0; n < e.length; n++) {
    var o = e[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, Et(o.key), o);
  }
}
function le(t, e, n) {
  return e && sn(t.prototype, e), Object.defineProperty(t, "prototype", {
    writable: !1
  }), t;
}
function Z(t) {
  if (t === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return t;
}
function Ae(t, e) {
  return Ae = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, Ae(t, e);
}
function Mt(t, e) {
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
function se(t) {
  return se = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
    return e.__proto__ || Object.getPrototypeOf(e);
  }, se(t);
}
function It() {
  try {
    var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (It = function() {
    return !!t;
  })();
}
function an(t, e) {
  if (e && ($(e) == "object" || typeof e == "function")) return e;
  if (e !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return Z(t);
}
function kt(t) {
  var e = It();
  return function() {
    var n, o = se(t);
    if (e) {
      var r = se(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return an(this, n);
  };
}
var jt = /* @__PURE__ */ le(function t() {
  ce(this, t);
}), Rt = "CALC_UNIT", cn = new RegExp(Rt, "g");
function _e(t) {
  return typeof t == "number" ? "".concat(t).concat(Rt) : t;
}
var ln = /* @__PURE__ */ function(t) {
  Mt(n, t);
  var e = kt(n);
  function n(o, r) {
    var s;
    ce(this, n), s = e.call(this), P(Z(s), "result", ""), P(Z(s), "unitlessCssVar", void 0), P(Z(s), "lowPriority", void 0);
    var i = $(o);
    return s.unitlessCssVar = r, o instanceof n ? s.result = "(".concat(o.result, ")") : i === "number" ? s.result = _e(o) : i === "string" && (s.result = o), s;
  }
  return le(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(_e(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(_e(r))), this.lowPriority = !0, this;
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
      var s = this, i = r || {}, a = i.unit, c = !0;
      return typeof a == "boolean" ? c = a : Array.from(this.unitlessCssVar).some(function(l) {
        return s.result.includes(l);
      }) && (c = !1), this.result = this.result.replace(cn, c ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(jt), un = /* @__PURE__ */ function(t) {
  Mt(n, t);
  var e = kt(n);
  function n(o) {
    var r;
    return ce(this, n), r = e.call(this), P(Z(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
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
}(jt), fn = function(e, n) {
  var o = e === "css" ? ln : un;
  return function(r) {
    return new o(r, n);
  };
}, ct = function(e, n) {
  return "".concat([n, e.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function ie(t) {
  var e = z.useRef();
  e.current = t;
  var n = z.useCallback(function() {
    for (var o, r = arguments.length, s = new Array(r), i = 0; i < r; i++)
      s[i] = arguments[i];
    return (o = e.current) === null || o === void 0 ? void 0 : o.call.apply(o, [e].concat(s));
  }, []);
  return n;
}
function hn() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var lt = hn() ? z.useLayoutEffect : z.useEffect, dn = function(e, n) {
  var o = z.useRef(!0);
  lt(function() {
    return e(o.current);
  }, n), lt(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, ut = function(e, n) {
  dn(function(o) {
    if (!o)
      return e();
  }, n);
};
function ft(t) {
  var e = z.useRef(!1), n = z.useState(t), o = N(n, 2), r = o[0], s = o[1];
  z.useEffect(function() {
    return e.current = !1, function() {
      e.current = !0;
    };
  }, []);
  function i(a, c) {
    c && e.current || s(a);
  }
  return [r, i];
}
function we(t) {
  return t !== void 0;
}
function gn(t, e) {
  var n = e || {}, o = n.defaultValue, r = n.value, s = n.onChange, i = n.postState, a = ft(function() {
    return we(r) ? r : we(o) ? typeof o == "function" ? o() : o : t;
  }), c = N(a, 2), l = c[0], d = c[1], u = r !== void 0 ? r : l, h = i ? i(u) : u, f = ie(s), b = ft([u]), g = N(b, 2), p = g[0], m = g[1];
  ut(function() {
    var S = p[0];
    l !== S && f(l, S);
  }, [p]), ut(function() {
    we(r) || d(r);
  }, [r]);
  var v = ie(function(S, y) {
    d(S, y), m([u], y);
  });
  return [h, v];
}
var C = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var $e = Symbol.for("react.element"), Be = Symbol.for("react.portal"), ue = Symbol.for("react.fragment"), fe = Symbol.for("react.strict_mode"), he = Symbol.for("react.profiler"), de = Symbol.for("react.provider"), ge = Symbol.for("react.context"), pn = Symbol.for("react.server_context"), pe = Symbol.for("react.forward_ref"), me = Symbol.for("react.suspense"), be = Symbol.for("react.suspense_list"), ve = Symbol.for("react.memo"), ye = Symbol.for("react.lazy"), mn = Symbol.for("react.offscreen"), Lt;
Lt = Symbol.for("react.module.reference");
function H(t) {
  if (typeof t == "object" && t !== null) {
    var e = t.$$typeof;
    switch (e) {
      case $e:
        switch (t = t.type, t) {
          case ue:
          case he:
          case fe:
          case me:
          case be:
            return t;
          default:
            switch (t = t && t.$$typeof, t) {
              case pn:
              case ge:
              case pe:
              case ye:
              case ve:
              case de:
                return t;
              default:
                return e;
            }
        }
      case Be:
        return e;
    }
  }
}
C.ContextConsumer = ge;
C.ContextProvider = de;
C.Element = $e;
C.ForwardRef = pe;
C.Fragment = ue;
C.Lazy = ye;
C.Memo = ve;
C.Portal = Be;
C.Profiler = he;
C.StrictMode = fe;
C.Suspense = me;
C.SuspenseList = be;
C.isAsyncMode = function() {
  return !1;
};
C.isConcurrentMode = function() {
  return !1;
};
C.isContextConsumer = function(t) {
  return H(t) === ge;
};
C.isContextProvider = function(t) {
  return H(t) === de;
};
C.isElement = function(t) {
  return typeof t == "object" && t !== null && t.$$typeof === $e;
};
C.isForwardRef = function(t) {
  return H(t) === pe;
};
C.isFragment = function(t) {
  return H(t) === ue;
};
C.isLazy = function(t) {
  return H(t) === ye;
};
C.isMemo = function(t) {
  return H(t) === ve;
};
C.isPortal = function(t) {
  return H(t) === Be;
};
C.isProfiler = function(t) {
  return H(t) === he;
};
C.isStrictMode = function(t) {
  return H(t) === fe;
};
C.isSuspense = function(t) {
  return H(t) === me;
};
C.isSuspenseList = function(t) {
  return H(t) === be;
};
C.isValidElementType = function(t) {
  return typeof t == "string" || typeof t == "function" || t === ue || t === he || t === fe || t === me || t === be || t === mn || typeof t == "object" && t !== null && (t.$$typeof === ye || t.$$typeof === ve || t.$$typeof === de || t.$$typeof === ge || t.$$typeof === pe || t.$$typeof === Lt || t.getModuleId !== void 0);
};
C.typeOf = H;
Number(Ut.split(".")[0]);
function ht(t, e, n, o) {
  var r = L({}, e[t]);
  if (o != null && o.deprecatedTokens) {
    var s = o.deprecatedTokens;
    s.forEach(function(a) {
      var c = N(a, 2), l = c[0], d = c[1];
      if (r != null && r[l] || r != null && r[d]) {
        var u;
        (u = r[d]) !== null && u !== void 0 || (r[d] = r == null ? void 0 : r[l]);
      }
    });
  }
  var i = L(L({}, n), r);
  return Object.keys(i).forEach(function(a) {
    i[a] === e[a] && delete i[a];
  }), i;
}
var At = typeof CSSINJS_STATISTIC < "u", De = !0;
function Fe() {
  for (var t = arguments.length, e = new Array(t), n = 0; n < t; n++)
    e[n] = arguments[n];
  if (!At)
    return Object.assign.apply(Object, [{}].concat(e));
  De = !1;
  var o = {};
  return e.forEach(function(r) {
    if ($(r) === "object") {
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
  }), De = !0, o;
}
var dt = {};
function bn() {
}
var vn = function(e) {
  var n, o = e, r = bn;
  return At && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(e, {
    get: function(i, a) {
      if (De) {
        var c;
        (c = n) === null || c === void 0 || c.add(a);
      }
      return i[a];
    }
  }), r = function(i, a) {
    var c;
    dt[i] = {
      global: Array.from(n),
      component: L(L({}, (c = dt[i]) === null || c === void 0 ? void 0 : c.component), a)
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
    return n(Fe(e, (o = e[t]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function yn(t) {
  return t === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(s) {
        return Ge(s);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(s) {
        return Ge(s);
      }).join(","), ")");
    }
  };
}
var xn = 1e3 * 60 * 10, Sn = /* @__PURE__ */ function() {
  function t() {
    ce(this, t), P(this, "map", /* @__PURE__ */ new Map()), P(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), P(this, "nextID", 0), P(this, "lastAccessBeat", /* @__PURE__ */ new Map()), P(this, "accessBeat", 0);
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
      var o = this, r = n.map(function(s) {
        return s && $(s) === "object" ? "obj_".concat(o.getObjectID(s)) : "".concat($(s), "_").concat(s);
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
          o - r > xn && (n.map.delete(s), n.lastAccessBeat.delete(s));
        }), this.accessBeat = 0;
      }
    }
  }]), t;
}(), pt = new Sn();
function Cn(t, e) {
  return w.useMemo(function() {
    var n = pt.get(e);
    if (n)
      return n;
    var o = t();
    return pt.set(e, o), o;
  }, e);
}
var _n = function() {
  return {};
};
function wn(t) {
  var e = t.useCSP, n = e === void 0 ? _n : e, o = t.useToken, r = t.usePrefix, s = t.getResetStyles, i = t.getCommonStyle, a = t.getCompUnitless;
  function c(h, f, b, g) {
    var p = Array.isArray(h) ? h[0] : h;
    function m(_) {
      return "".concat(String(p)).concat(_.slice(0, 1).toUpperCase()).concat(_.slice(1));
    }
    var v = (g == null ? void 0 : g.unitless) || {}, S = typeof a == "function" ? a(h) : {}, y = L(L({}, S), {}, P({}, m("zIndexPopup"), !0));
    Object.keys(v).forEach(function(_) {
      y[m(_)] = v[_];
    });
    var O = L(L({}, g), {}, {
      unitless: y,
      prefixToken: m
    }), x = d(h, f, b, O), T = l(p, b, O);
    return function(_) {
      var E = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : _, j = x(_, E), B = N(j, 2), I = B[1], F = T(E), R = N(F, 2), D = R[0], U = R[1];
      return [D, I, U];
    };
  }
  function l(h, f, b) {
    var g = b.unitless, p = b.injectStyle, m = p === void 0 ? !0 : p, v = b.prefixToken, S = b.ignore, y = function(T) {
      var _ = T.rootCls, E = T.cssVar, j = E === void 0 ? {} : E, B = o(), I = B.realToken;
      return or({
        path: [h],
        prefix: j.prefix,
        key: j.key,
        unitless: g,
        ignore: S,
        token: I,
        scope: _
      }, function() {
        var F = gt(h, I, f), R = ht(h, I, F, {
          deprecatedTokens: b == null ? void 0 : b.deprecatedTokens
        });
        return Object.keys(F).forEach(function(D) {
          R[v(D)] = R[D], delete R[D];
        }), R;
      }), null;
    }, O = function(T) {
      var _ = o(), E = _.cssVar;
      return [function(j) {
        return m && E ? /* @__PURE__ */ w.createElement(w.Fragment, null, /* @__PURE__ */ w.createElement(y, {
          rootCls: T,
          cssVar: E,
          component: h
        }), j) : j;
      }, E == null ? void 0 : E.key];
    };
    return O;
  }
  function d(h, f, b) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = Array.isArray(h) ? h : [h, h], m = N(p, 1), v = m[0], S = p.join("-"), y = t.layer || {
      name: "antd"
    };
    return function(O) {
      var x = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : O, T = o(), _ = T.theme, E = T.realToken, j = T.hashId, B = T.token, I = T.cssVar, F = r(), R = F.rootPrefixCls, D = F.iconPrefixCls, U = n(), W = I ? "css" : "js", q = Cn(function() {
        var X = /* @__PURE__ */ new Set();
        return I && Object.keys(g.unitless || {}).forEach(function(Y) {
          X.add(xe(Y, I.prefix)), X.add(xe(Y, ct(v, I.prefix)));
        }), fn(W, X);
      }, [W, v, I == null ? void 0 : I.prefix]), M = yn(W), $t = M.max, Bt = M.min, Ve = {
        theme: _,
        token: B,
        hashId: j,
        nonce: function() {
          return U.nonce;
        },
        clientOnly: g.clientOnly,
        layer: y,
        // antd is always at top of styles
        order: g.order || -999
      };
      typeof s == "function" && Ke(L(L({}, Ve), {}, {
        clientOnly: !1,
        path: ["Shared", R]
      }), function() {
        return s(B, {
          prefix: {
            rootPrefixCls: R,
            iconPrefixCls: D
          },
          csp: U
        });
      });
      var Ft = Ke(L(L({}, Ve), {}, {
        path: [S, O, D]
      }), function() {
        if (g.injectStyle === !1)
          return [];
        var X = vn(B), Y = X.token, Vt = X.flush, G = gt(v, E, b), zt = ".".concat(O), ze = ht(v, E, G, {
          deprecatedTokens: g.deprecatedTokens
        });
        I && G && $(G) === "object" && Object.keys(G).forEach(function(Ne) {
          G[Ne] = "var(".concat(xe(Ne, ct(v, I.prefix)), ")");
        });
        var Xe = Fe(Y, {
          componentCls: zt,
          prefixCls: O,
          iconCls: ".".concat(D),
          antCls: ".".concat(R),
          calc: q,
          // @ts-ignore
          max: $t,
          // @ts-ignore
          min: Bt
        }, I ? G : ze), Xt = f(Xe, {
          hashId: j,
          prefixCls: O,
          rootPrefixCls: R,
          iconPrefixCls: D
        });
        Vt(v, ze);
        var Nt = typeof i == "function" ? i(Xe, O, x, g.resetFont) : null;
        return [g.resetStyle === !1 ? null : Nt, Xt];
      });
      return [Ft, j];
    };
  }
  function u(h, f, b) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, p = d(h, f, b, L({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, g)), m = function(S) {
      var y = S.prefixCls, O = S.rootCls, x = O === void 0 ? y : O;
      return p(y, x), null;
    };
    return m;
  }
  return {
    genStyleHooks: c,
    genSubStyleComponent: u,
    genComponentStyleHook: d
  };
}
const On = {
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
}, Tn = Object.assign(Object.assign({}, On), {
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
}), k = Math.round;
function Oe(t, e) {
  const n = t.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = e(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const mt = (t, e, n) => n === 0 ? t : t / 100;
function Q(t, e) {
  const n = e || 255;
  return t > n ? n : t < 0 ? 0 : t;
}
class V {
  constructor(e) {
    P(this, "isValid", !0), P(this, "r", 0), P(this, "g", 0), P(this, "b", 0), P(this, "a", 1), P(this, "_h", void 0), P(this, "_s", void 0), P(this, "_l", void 0), P(this, "_v", void 0), P(this, "_max", void 0), P(this, "_min", void 0), P(this, "_brightness", void 0);
    function n(o) {
      return o[0] in e && o[1] in e && o[2] in e;
    }
    if (e) if (typeof e == "string") {
      let r = function(s) {
        return o.startsWith(s);
      };
      const o = e.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (e instanceof V)
      this.r = e.r, this.g = e.g, this.b = e.b, this.a = e.a, this._h = e._h, this._s = e._s, this._l = e._l, this._v = e._v;
    else if (n("rgb"))
      this.r = Q(e.r), this.g = Q(e.g), this.b = Q(e.b), this.a = typeof e.a == "number" ? Q(e.a, 1) : 1;
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
      e === 0 ? this._h = 0 : this._h = k(60 * (this.r === this.getMax() ? (this.g - this.b) / e + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / e + 2 : (this.r - this.g) / e + 4));
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
      r: k(s("r")),
      g: k(s("g")),
      b: k(s("b")),
      a: k(s("a") * 100) / 100
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
    const n = this._c(e), o = this.a + n.a * (1 - this.a), r = (s) => k((this[s] * this.a + n[s] * n.a * (1 - this.a)) / o);
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
      const s = k(this.a * 255).toString(16);
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
    const e = this.getHue(), n = k(this.getSaturation() * 100), o = k(this.getLightness() * 100);
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
    return r[e] = Q(n, o), r;
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
      const h = k(o * 255);
      this.r = h, this.g = h, this.b = h;
    }
    let s = 0, i = 0, a = 0;
    const c = e / 60, l = (1 - Math.abs(2 * o - 1)) * n, d = l * (1 - Math.abs(c % 2 - 1));
    c >= 0 && c < 1 ? (s = l, i = d) : c >= 1 && c < 2 ? (s = d, i = l) : c >= 2 && c < 3 ? (i = l, a = d) : c >= 3 && c < 4 ? (i = d, a = l) : c >= 4 && c < 5 ? (s = d, a = l) : c >= 5 && c < 6 && (s = l, a = d);
    const u = o - l / 2;
    this.r = k((s + u) * 255), this.g = k((i + u) * 255), this.b = k((a + u) * 255);
  }
  fromHsv({
    h: e,
    s: n,
    v: o,
    a: r
  }) {
    this._h = e % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const s = k(o * 255);
    if (this.r = s, this.g = s, this.b = s, n <= 0)
      return;
    const i = e / 60, a = Math.floor(i), c = i - a, l = k(o * (1 - n) * 255), d = k(o * (1 - n * c) * 255), u = k(o * (1 - n * (1 - c)) * 255);
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
  fromHsvString(e) {
    const n = Oe(e, mt);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(e) {
    const n = Oe(e, mt);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(e) {
    const n = Oe(e, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? k(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function Te(t) {
  return t >= 0 && t <= 255;
}
function ee(t, e) {
  const {
    r: n,
    g: o,
    b: r,
    a: s
  } = new V(t).toRgb();
  if (s < 1)
    return t;
  const {
    r: i,
    g: a,
    b: c
  } = new V(e).toRgb();
  for (let l = 0.01; l <= 1; l += 0.01) {
    const d = Math.round((n - i * (1 - l)) / l), u = Math.round((o - a * (1 - l)) / l), h = Math.round((r - c * (1 - l)) / l);
    if (Te(d) && Te(u) && Te(h))
      return new V({
        r: d,
        g: u,
        b: h,
        a: Math.round(l * 100) / 100
      }).toRgbString();
  }
  return new V({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var Pn = function(t, e) {
  var n = {};
  for (var o in t) Object.prototype.hasOwnProperty.call(t, o) && e.indexOf(o) < 0 && (n[o] = t[o]);
  if (t != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(t); r < o.length; r++)
    e.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(t, o[r]) && (n[o[r]] = t[o[r]]);
  return n;
};
function En(t) {
  const {
    override: e
  } = t, n = Pn(t, ["override"]), o = Object.assign({}, e);
  Object.keys(Tn).forEach((h) => {
    delete o[h];
  });
  const r = Object.assign(Object.assign({}, n), o), s = 480, i = 576, a = 768, c = 992, l = 1200, d = 1600;
  if (r.motion === !1) {
    const h = "0s";
    r.motionDurationFast = h, r.motionDurationMid = h, r.motionDurationSlow = h;
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
    screenXS: s,
    screenXSMin: s,
    screenXSMax: i - 1,
    screenSM: i,
    screenSMMin: i,
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
      0 1px 2px -2px ${new V("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new V("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new V("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const Mn = {
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
}, In = {
  motionBase: !0,
  motionUnit: !0
}, kn = sr(Me.defaultAlgorithm), jn = {
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
  return i = En(i), s && Object.entries(s).forEach(([a, c]) => {
    const {
      theme: l,
      ...d
    } = c;
    let u = d;
    l && (u = Dt({
      ...i,
      ...d
    }, {
      override: d
    }, l)), i[a] = u;
  }), i;
};
function Rn() {
  const {
    token: t,
    hashed: e,
    theme: n = kn,
    override: o,
    cssVar: r
  } = w.useContext(Me._internalContext), [s, i, a] = ir(n, [Me.defaultSeed, t], {
    salt: `${Qr}-${e || ""}`,
    override: o,
    getComputedToken: Dt,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: Mn,
      ignore: In,
      preserve: jn
    }
  });
  return [n, a, e ? i : "", s, r];
}
const {
  genStyleHooks: Ln
} = wn({
  usePrefix: () => {
    const {
      getPrefixCls: t,
      iconPrefixCls: e
    } = Le();
    return {
      iconPrefixCls: e,
      rootPrefixCls: t()
    };
  },
  useToken: () => {
    const [t, e, n, o, r] = Rn();
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
    } = Le();
    return t ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), An = (t) => {
  const {
    componentCls: e,
    antCls: n
  } = t;
  return {
    [e]: {
      [`${n}-cascader-menus ${n}-cascader-menu`]: {
        height: "auto"
      },
      [`${e}-item`]: {
        "&-icon": {
          marginInlineEnd: t.paddingXXS
        },
        "&-extra": {
          marginInlineStart: t.padding
        }
      },
      [`&${e}-block`]: {
        [`${e}-item-extra`]: {
          marginInlineStart: "auto"
        }
      }
    }
  };
}, Dn = () => ({}), Hn = Ln("Suggestion", (t) => {
  const e = Fe(t, {});
  return An(e);
}, Dn);
function $n(t, e, n, o, r) {
  const [s, i] = w.useState([]), a = (f, b = s) => {
    let g = t;
    for (let p = 0; p < f - 1; p += 1) {
      const m = b[p], v = g.find((S) => S.value === m);
      if (!v)
        break;
      g = v.children || [];
    }
    return g;
  }, c = (f) => f.map((b, g) => {
    const m = a(g + 1, f).find((v) => v.value === b);
    return m == null ? void 0 : m.value;
  }), l = (f) => {
    const b = s.length || 1, g = a(b), p = g.findIndex((S) => S.value === s[b - 1]), m = g.length, v = g[(p + f + m) % m];
    i([...s.slice(0, b - 1), v.value]);
  }, d = () => {
    s.length > 1 && i(s.slice(0, s.length - 1));
  }, u = () => {
    const f = a(s.length + 1);
    f.length && i([...s, f[0].value]);
  }, h = ie((f) => {
    if (e)
      switch (f.key) {
        case "ArrowDown":
          l(1), f.preventDefault();
          break;
        case "ArrowUp":
          l(-1), f.preventDefault();
          break;
        case "ArrowRight":
          n ? d() : u(), f.preventDefault();
          break;
        case "ArrowLeft":
          n ? u() : d(), f.preventDefault();
          break;
        case "Enter":
          a(s.length + 1).length || o(c(s)), f.preventDefault();
          break;
        case "Escape":
          r(), f.preventDefault();
          break;
      }
  });
  return w.useEffect(() => {
    e && i([t[0].value]);
  }, [e]), [s, h];
}
const Pe = rr.split(".").map(Number), Bn = Pe[0] > 5 || Pe[0] === 5 && Pe[1] >= 25;
function Fn(t) {
  const {
    prefixCls: e,
    className: n,
    rootClassName: o,
    style: r,
    children: s,
    open: i,
    onOpenChange: a,
    items: c,
    onSelect: l,
    block: d
  } = t, {
    direction: u,
    getPrefixCls: h
  } = Le(), f = h("suggestion", e), b = `${f}-item`, g = u === "rtl", p = en("suggestion"), [m, v, S] = Hn(f), [y, O] = gn(!1, {
    value: i
  }), [x, T] = He(), _ = (M) => {
    O(M), a == null || a(M);
  }, E = ie((M) => {
    M === !1 ? _(!1) : (T(M), _(!0));
  }), j = () => {
    _(!1);
  }, B = w.useMemo(() => typeof c == "function" ? c(x) : c, [c, x]), I = (M) => /* @__PURE__ */ w.createElement(nr, {
    className: b
  }, M.icon && /* @__PURE__ */ w.createElement("div", {
    className: `${b}-icon`
  }, M.icon), M.label, M.extra && /* @__PURE__ */ w.createElement("div", {
    className: `${b}-extra`
  }, M.extra)), F = (M) => {
    l && l(M[M.length - 1]), _(!1);
  }, [R, D] = $n(B, y, g, F, j), U = s == null ? void 0 : s({
    onTrigger: E,
    onKeyDown: D
  }), W = (M) => {
    M || j();
  }, q = {};
  return Bn ? q.onOpenChange = W : q.onDropdownVisibleChange = W, m(/* @__PURE__ */ w.createElement(tr, Re({
    options: B,
    open: y,
    value: R,
    placement: g ? "topRight" : "topLeft"
  }, q, {
    optionRender: I,
    rootClassName: Ue(o, f, v, S, {
      [`${f}-block`]: d
    }),
    onChange: F,
    dropdownMatchSelectWidth: d
  }), /* @__PURE__ */ w.createElement("div", {
    className: Ue(f, p.className, o, n, `${f}-wrapper`, v, S),
    style: {
      ...p.style,
      ...r
    }
  }, U)));
}
function Vn(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function zn(t, e = !1) {
  try {
    if (St(t))
      return t;
    if (e && !Vn(t))
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
function bt(t, e) {
  return J(() => zn(t, e), [t, e]);
}
function Xn(t) {
  const e = yt();
  return J(() => yr(t, e.current) ? e.current : (e.current = t, t), [t]);
}
function Nn(t, e) {
  return e((o, r) => St(o) ? r ? (...s) => oe(r) && r.unshift ? o(...t, ...s) : o(...s, ...t) : o(...t) : o);
}
const Un = ({
  children: t,
  ...e
}) => /* @__PURE__ */ A.jsx(A.Fragment, {
  children: t(e)
});
function Wn(t) {
  return w.createElement(Un, {
    children: t
  });
}
function Ht(t, e, n) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((r, s) => {
      var l, d;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const i = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((l = r.props) == null ? void 0 : l.key) ?? (n ? `${n}-${s}` : `${s}`)
      }) : {
        ...r.props,
        key: ((d = r.props) == null ? void 0 : d.key) ?? (n ? `${n}-${s}` : `${s}`)
      };
      let a = i;
      Object.keys(r.slots).forEach((u) => {
        if (!r.slots[u] || !(r.slots[u] instanceof Element) && !r.slots[u].el)
          return;
        const h = u.split(".");
        h.forEach((v, S) => {
          a[v] || (a[v] = {}), S !== h.length - 1 && (a = i[v]);
        });
        const f = r.slots[u];
        let b, g, p = (e == null ? void 0 : e.clone) ?? !1, m = e == null ? void 0 : e.forceClone;
        f instanceof Element ? b = f : (b = f.el, g = f.callback, p = f.clone ?? p, m = f.forceClone ?? m), m = m ?? !!g, a[h[h.length - 1]] = b ? g ? (...v) => (g(h[h.length - 1], v), /* @__PURE__ */ A.jsx(We, {
          ...r.ctx,
          params: v,
          forceClone: m,
          children: /* @__PURE__ */ A.jsx(je, {
            slot: b,
            clone: p
          })
        })) : Wn((v) => /* @__PURE__ */ A.jsx(We, {
          ...r.ctx,
          forceClone: m,
          children: /* @__PURE__ */ A.jsx(je, {
            ...v,
            slot: b,
            clone: p
          })
        })) : a[h[h.length - 1]], a = i;
      });
      const c = (e == null ? void 0 : e.children) || "children";
      return r[c] ? i[c] = Ht(r[c], e, `${s}`) : e != null && e.children && (i[c] = void 0, Reflect.deleteProperty(i, c)), i;
    });
}
const {
  useItems: Gn,
  withItemsContextProvider: Kn,
  ItemHandler: Jn
} = Yt("antdx-suggestion-chain-items"), qn = vt(({
  children: t,
  props: e,
  shouldTrigger: n
}, o) => {
  const r = Xn(e);
  return /* @__PURE__ */ A.jsx(Jt.Provider, {
    value: J(() => ({
      ...r,
      onKeyDown: (s) => {
        var i;
        n ? requestAnimationFrame(() => {
          n(s, {
            onTrigger: r.onTrigger,
            onKeyDown: r.onKeyDown
          });
        }) : (i = r.onKeyDown) == null || i.call(r, s);
      },
      elRef: o
    }), [r, n, o]),
    children: t
  });
}), Yn = Ur(Kn(["default", "items"], ({
  children: t,
  items: e,
  shouldTrigger: n,
  slots: o,
  ...r
}) => {
  const [s, i] = He(() => r.open ?? !1), {
    items: a
  } = Gn(), c = a.items.length > 0 ? a.items : a.default, l = bt(e), d = bt(n), u = J(() => e || Ht(c, {
    clone: !0
  }) || [{}], [e, c]), h = J(() => (...f) => u.map((b) => Nn(f, (g) => {
    const p = (m) => {
      var v;
      return {
        ...m,
        extra: g(m.extra),
        icon: g(m.icon),
        label: g(m.label),
        children: (v = m.children) == null ? void 0 : v.map((S) => p(S))
      };
    };
    return p(b);
  })), [u]);
  return xt(() => {
    Ze(r.open) || i(r.open);
  }, [r.open]), /* @__PURE__ */ A.jsx(A.Fragment, {
    children: /* @__PURE__ */ A.jsx(Fn, {
      ...r,
      items: l || h,
      onOpenChange: (f, ...b) => {
        var g;
        Ze(r.open) && i(f), (g = r.onOpenChange) == null || g.call(r, f, ...b);
      },
      children: (f) => /* @__PURE__ */ A.jsx(Zt.Provider, {
        value: s,
        children: /* @__PURE__ */ A.jsxs(qn, {
          props: f,
          shouldTrigger: d,
          children: [/* @__PURE__ */ A.jsx("div", {
            style: {
              display: "none"
            },
            children: t
          }), o.children ? /* @__PURE__ */ A.jsx(je, {
            slot: o.children
          }) : null]
        })
      })
    })
  });
}));
export {
  Yn as Suggestion,
  Yn as default
};
