var Xe = (e) => {
  throw TypeError(e);
};
var Fe = (e, t, n) => t.has(e) || Xe("Cannot " + n);
var V = (e, t, n) => (Fe(e, t, "read from private field"), n ? n.call(e) : t.get(e)), Ne = (e, t, n) => t.has(e) ? Xe("Cannot add the same private member more than once") : t instanceof WeakSet ? t.add(e) : t.set(e, n), Ve = (e, t, n, o) => (Fe(e, t, "write to private field"), o ? o.call(e, n) : t.set(e, n), n);
import { i as Dt, a as Oe, r as Xt, Z as Y, g as Ft, c as U } from "./Index-Dr9Rh2sB.js";
const b = window.ms_globals.React, Ht = window.ms_globals.React.forwardRef, At = window.ms_globals.React.useRef, $t = window.ms_globals.React.useState, Bt = window.ms_globals.React.useEffect, zt = window.ms_globals.React.version, Te = window.ms_globals.ReactDOM.createPortal, Nt = window.ms_globals.internalContext.useContextPropsContext, Vt = window.ms_globals.antd.ConfigProvider, Me = window.ms_globals.antd.theme, We = window.ms_globals.antd.Typography, ye = window.ms_globals.antd.Flex, Ue = window.ms_globals.antdCssinjs.unit, ve = window.ms_globals.antdCssinjs.token2CSSVar, Ge = window.ms_globals.antdCssinjs.useStyleRegister, Wt = window.ms_globals.antdCssinjs.useCSSVarRegister, Ut = window.ms_globals.antdCssinjs.createTheme, Gt = window.ms_globals.antdCssinjs.useCacheToken;
var qt = /\s/;
function Kt(e) {
  for (var t = e.length; t-- && qt.test(e.charAt(t)); )
    ;
  return t;
}
var Qt = /^\s+/;
function Zt(e) {
  return e && e.slice(0, Kt(e) + 1).replace(Qt, "");
}
var qe = NaN, Jt = /^[-+]0x[0-9a-f]+$/i, Yt = /^0b[01]+$/i, er = /^0o[0-7]+$/i, tr = parseInt;
function Ke(e) {
  if (typeof e == "number")
    return e;
  if (Dt(e))
    return qe;
  if (Oe(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = Oe(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Zt(e);
  var n = Yt.test(e);
  return n || er.test(e) ? tr(e.slice(2), n ? 2 : 8) : Jt.test(e) ? qe : +e;
}
var xe = function() {
  return Xt.Date.now();
}, rr = "Expected a function", nr = Math.max, or = Math.min;
function ir(e, t, n) {
  var o, r, i, s, a, l, c = 0, f = !1, u = !1, d = !0;
  if (typeof e != "function")
    throw new TypeError(rr);
  t = Ke(t) || 0, Oe(n) && (f = !!n.leading, u = "maxWait" in n, i = u ? nr(Ke(n.maxWait) || 0, t) : i, d = "trailing" in n ? !!n.trailing : d);
  function v(m) {
    var w = o, O = r;
    return o = r = void 0, c = m, s = e.apply(O, w), s;
  }
  function S(m) {
    return c = m, a = setTimeout(x, t), f ? v(m) : s;
  }
  function p(m) {
    var w = m - l, O = m - c, P = t - w;
    return u ? or(P, i - O) : P;
  }
  function h(m) {
    var w = m - l, O = m - c;
    return l === void 0 || w >= t || w < 0 || u && O >= i;
  }
  function x() {
    var m = xe();
    if (h(m))
      return _(m);
    a = setTimeout(x, p(m));
  }
  function _(m) {
    return a = void 0, d && o ? v(m) : (o = r = void 0, s);
  }
  function E() {
    a !== void 0 && clearTimeout(a), c = 0, o = l = r = a = void 0;
  }
  function g() {
    return a === void 0 ? s : _(xe());
  }
  function C() {
    var m = xe(), w = h(m);
    if (o = arguments, r = this, l = m, w) {
      if (a === void 0)
        return S(l);
      if (u)
        return clearTimeout(a), a = setTimeout(x, t), v(l);
    }
    return a === void 0 && (a = setTimeout(x, t)), s;
  }
  return C.cancel = E, C.flush = g, C;
}
var dt = {
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
var sr = b, ar = Symbol.for("react.element"), lr = Symbol.for("react.fragment"), cr = Object.prototype.hasOwnProperty, ur = sr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, fr = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ht(e, t, n) {
  var o, r = {}, i = null, s = null;
  n !== void 0 && (i = "" + n), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (o in t) cr.call(t, o) && !fr.hasOwnProperty(o) && (r[o] = t[o]);
  if (e && e.defaultProps) for (o in t = e.defaultProps, t) r[o] === void 0 && (r[o] = t[o]);
  return {
    $$typeof: ar,
    type: e,
    key: i,
    ref: s,
    props: r,
    _owner: ur.current
  };
}
oe.Fragment = lr;
oe.jsx = ht;
oe.jsxs = ht;
dt.exports = oe;
var z = dt.exports;
const {
  SvelteComponent: dr,
  assign: Qe,
  binding_callbacks: Ze,
  check_outros: hr,
  children: gt,
  claim_element: pt,
  claim_space: gr,
  component_subscribe: Je,
  compute_slots: pr,
  create_slot: mr,
  detach: W,
  element: mt,
  empty: Ye,
  exclude_internal_props: et,
  get_all_dirty_from_scope: br,
  get_slot_changes: yr,
  group_outros: vr,
  init: xr,
  insert_hydration: ee,
  safe_not_equal: Sr,
  set_custom_element_data: bt,
  space: _r,
  transition_in: te,
  transition_out: Pe,
  update_slot_base: Cr
} = window.__gradio__svelte__internal, {
  beforeUpdate: wr,
  getContext: Tr,
  onDestroy: Or,
  setContext: Mr
} = window.__gradio__svelte__internal;
function tt(e) {
  let t, n;
  const o = (
    /*#slots*/
    e[7].default
  ), r = mr(
    o,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = mt("svelte-slot"), r && r.c(), this.h();
    },
    l(i) {
      t = pt(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = gt(t);
      r && r.l(s), s.forEach(W), this.h();
    },
    h() {
      bt(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      ee(i, t, s), r && r.m(t, null), e[9](t), n = !0;
    },
    p(i, s) {
      r && r.p && (!n || s & /*$$scope*/
      64) && Cr(
        r,
        o,
        i,
        /*$$scope*/
        i[6],
        n ? yr(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : br(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      n || (te(r, i), n = !0);
    },
    o(i) {
      Pe(r, i), n = !1;
    },
    d(i) {
      i && W(t), r && r.d(i), e[9](null);
    }
  };
}
function Pr(e) {
  let t, n, o, r, i = (
    /*$$slots*/
    e[4].default && tt(e)
  );
  return {
    c() {
      t = mt("react-portal-target"), n = _r(), i && i.c(), o = Ye(), this.h();
    },
    l(s) {
      t = pt(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), gt(t).forEach(W), n = gr(s), i && i.l(s), o = Ye(), this.h();
    },
    h() {
      bt(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      ee(s, t, a), e[8](t), ee(s, n, a), i && i.m(s, a), ee(s, o, a), r = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && te(i, 1)) : (i = tt(s), i.c(), te(i, 1), i.m(o.parentNode, o)) : i && (vr(), Pe(i, 1, 1, () => {
        i = null;
      }), hr());
    },
    i(s) {
      r || (te(i), r = !0);
    },
    o(s) {
      Pe(i), r = !1;
    },
    d(s) {
      s && (W(t), W(n), W(o)), e[8](null), i && i.d(s);
    }
  };
}
function rt(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function Er(e, t, n) {
  let o, r, {
    $$slots: i = {},
    $$scope: s
  } = t;
  const a = pr(i);
  let {
    svelteInit: l
  } = t;
  const c = Y(rt(t)), f = Y();
  Je(e, f, (g) => n(0, o = g));
  const u = Y();
  Je(e, u, (g) => n(1, r = g));
  const d = [], v = Tr("$$ms-gr-react-wrapper"), {
    slotKey: S,
    slotIndex: p,
    subSlotIndex: h
  } = Ft() || {}, x = l({
    parent: v,
    props: c,
    target: f,
    slot: u,
    slotKey: S,
    slotIndex: p,
    subSlotIndex: h,
    onDestroy(g) {
      d.push(g);
    }
  });
  Mr("$$ms-gr-react-wrapper", x), wr(() => {
    c.set(rt(t));
  }), Or(() => {
    d.forEach((g) => g());
  });
  function _(g) {
    Ze[g ? "unshift" : "push"](() => {
      o = g, f.set(o);
    });
  }
  function E(g) {
    Ze[g ? "unshift" : "push"](() => {
      r = g, u.set(r);
    });
  }
  return e.$$set = (g) => {
    n(17, t = Qe(Qe({}, t), et(g))), "svelteInit" in g && n(5, l = g.svelteInit), "$$scope" in g && n(6, s = g.$$scope);
  }, t = et(t), [o, r, f, u, a, l, s, i, _, E];
}
class jr extends dr {
  constructor(t) {
    super(), xr(this, t, Er, Pr, Sr, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: kn
} = window.__gradio__svelte__internal, nt = window.ms_globals.rerender, Se = window.ms_globals.tree;
function Ir(e, t = {}) {
  function n(o) {
    const r = Y(), i = new jr({
      ...o,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: e,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, l = s.parent ?? Se;
          return l.nodes = [...l.nodes, a], nt({
            createPortal: Te,
            node: Se
          }), s.onDestroy(() => {
            l.nodes = l.nodes.filter((c) => c.svelteInstance !== r), nt({
              createPortal: Te,
              node: Se
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
const kr = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Rr(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const o = e[n];
    return t[n] = Lr(n, o), t;
  }, {}) : {};
}
function Lr(e, t) {
  return typeof t == "number" && !kr.includes(e) ? t + "px" : t;
}
function Ee(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const r = b.Children.toArray(e._reactElement.props.children).map((i) => {
      if (b.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = Ee(i.props.el);
        return b.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...b.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return r.originalChildren = e._reactElement.props.children, t.push(Te(b.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: r
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((r) => {
    e.getEventListeners(r).forEach(({
      listener: s,
      type: a,
      useCapture: l
    }) => {
      n.addEventListener(a, s, l);
    });
  });
  const o = Array.from(e.childNodes);
  for (let r = 0; r < o.length; r++) {
    const i = o[r];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = Ee(i);
      t.push(...a), n.appendChild(s);
    } else i.nodeType === 3 && n.appendChild(i.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function Hr(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Z = Ht(({
  slot: e,
  clone: t,
  className: n,
  style: o,
  observeAttributes: r
}, i) => {
  const s = At(), [a, l] = $t([]), {
    forceClone: c
  } = Nt(), f = c ? !0 : t;
  return Bt(() => {
    var p;
    if (!s.current || !e)
      return;
    let u = e;
    function d() {
      let h = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (h = u.children[0], h.tagName.toLowerCase() === "react-portal-target" && h.children[0] && (h = h.children[0])), Hr(i, h), n && h.classList.add(...n.split(" ")), o) {
        const x = Rr(o);
        Object.keys(x).forEach((_) => {
          h.style[_] = x[_];
        });
      }
    }
    let v = null, S = null;
    if (f && window.MutationObserver) {
      let h = function() {
        var g, C, m;
        (g = s.current) != null && g.contains(u) && ((C = s.current) == null || C.removeChild(u));
        const {
          portals: _,
          clonedElement: E
        } = Ee(e);
        u = E, l(_), u.style.display = "contents", S && clearTimeout(S), S = setTimeout(() => {
          d();
        }, 50), (m = s.current) == null || m.appendChild(u);
      };
      h();
      const x = ir(() => {
        h(), v == null || v.disconnect(), v == null || v.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      v = new window.MutationObserver(x), v.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", d(), (p = s.current) == null || p.appendChild(u);
    return () => {
      var h, x;
      u.style.display = "", (h = s.current) != null && h.contains(u) && ((x = s.current) == null || x.removeChild(u)), v == null || v.disconnect();
    };
  }, [e, f, n, o, i, r, c]), b.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), Ar = "1.6.0";
function H(e) {
  "@babel/helpers - typeof";
  return H = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, H(e);
}
function $r(e, t) {
  if (H(e) != "object" || !e) return e;
  var n = e[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(e, t);
    if (H(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function yt(e) {
  var t = $r(e, "string");
  return H(t) == "symbol" ? t : t + "";
}
function T(e, t, n) {
  return (t = yt(t)) in e ? Object.defineProperty(e, t, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = n, e;
}
function ot(e, t) {
  var n = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(e);
    t && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(e, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function I(e) {
  for (var t = 1; t < arguments.length; t++) {
    var n = arguments[t] != null ? arguments[t] : {};
    t % 2 ? ot(Object(n), !0).forEach(function(o) {
      T(e, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : ot(Object(n)).forEach(function(o) {
      Object.defineProperty(e, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return e;
}
const Br = /* @__PURE__ */ b.createContext({}), zr = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, Dr = (e) => {
  const t = b.useContext(Br);
  return b.useMemo(() => ({
    ...zr,
    ...t[e]
  }), [t[e]]);
};
function je() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = b.useContext(Vt.ConfigContext);
  return {
    theme: r,
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: o
  };
}
function Xr(e) {
  if (Array.isArray(e)) return e;
}
function Fr(e, t) {
  var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (n != null) {
    var o, r, i, s, a = [], l = !0, c = !1;
    try {
      if (i = (n = n.call(e)).next, t === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (o = i.call(n)).done) && (a.push(o.value), a.length !== t); l = !0) ;
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
function it(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var n = 0, o = Array(t); n < t; n++) o[n] = e[n];
  return o;
}
function Nr(e, t) {
  if (e) {
    if (typeof e == "string") return it(e, t);
    var n = {}.toString.call(e).slice(8, -1);
    return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? it(e, t) : void 0;
  }
}
function Vr() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function re(e, t) {
  return Xr(e) || Fr(e, t) || Nr(e, t) || Vr();
}
function ie(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function Wr(e, t) {
  for (var n = 0; n < t.length; n++) {
    var o = t[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, yt(o.key), o);
  }
}
function se(e, t, n) {
  return t && Wr(e.prototype, t), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function q(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function Ie(e, t) {
  return Ie = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, Ie(e, t);
}
function vt(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && Ie(e, t);
}
function ne(e) {
  return ne = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, ne(e);
}
function xt() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (xt = function() {
    return !!e;
  })();
}
function Ur(e, t) {
  if (t && (H(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return q(e);
}
function St(e) {
  var t = xt();
  return function() {
    var n, o = ne(e);
    if (t) {
      var r = ne(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return Ur(this, n);
  };
}
var _t = /* @__PURE__ */ se(function e() {
  ie(this, e);
}), Ct = "CALC_UNIT", Gr = new RegExp(Ct, "g");
function _e(e) {
  return typeof e == "number" ? "".concat(e).concat(Ct) : e;
}
var qr = /* @__PURE__ */ function(e) {
  vt(n, e);
  var t = St(n);
  function n(o, r) {
    var i;
    ie(this, n), i = t.call(this), T(q(i), "result", ""), T(q(i), "unitlessCssVar", void 0), T(q(i), "lowPriority", void 0);
    var s = H(o);
    return i.unitlessCssVar = r, o instanceof n ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = _e(o) : s === "string" && (i.result = o), i;
  }
  return se(n, [{
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
      var i = this, s = r || {}, a = s.unit, l = !0;
      return typeof a == "boolean" ? l = a : Array.from(this.unitlessCssVar).some(function(c) {
        return i.result.includes(c);
      }) && (l = !1), this.result = this.result.replace(Gr, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(_t), Kr = /* @__PURE__ */ function(e) {
  vt(n, e);
  var t = St(n);
  function n(o) {
    var r;
    return ie(this, n), r = t.call(this), T(q(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
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
}(_t), Qr = function(t, n) {
  var o = t === "css" ? qr : Kr;
  return function(r) {
    return new o(r, n);
  };
}, st = function(t, n) {
  return "".concat([n, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
}, y = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Re = Symbol.for("react.element"), Le = Symbol.for("react.portal"), ae = Symbol.for("react.fragment"), le = Symbol.for("react.strict_mode"), ce = Symbol.for("react.profiler"), ue = Symbol.for("react.provider"), fe = Symbol.for("react.context"), Zr = Symbol.for("react.server_context"), de = Symbol.for("react.forward_ref"), he = Symbol.for("react.suspense"), ge = Symbol.for("react.suspense_list"), pe = Symbol.for("react.memo"), me = Symbol.for("react.lazy"), Jr = Symbol.for("react.offscreen"), wt;
wt = Symbol.for("react.module.reference");
function R(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case Re:
        switch (e = e.type, e) {
          case ae:
          case ce:
          case le:
          case he:
          case ge:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case Zr:
              case fe:
              case de:
              case me:
              case pe:
              case ue:
                return e;
              default:
                return t;
            }
        }
      case Le:
        return t;
    }
  }
}
y.ContextConsumer = fe;
y.ContextProvider = ue;
y.Element = Re;
y.ForwardRef = de;
y.Fragment = ae;
y.Lazy = me;
y.Memo = pe;
y.Portal = Le;
y.Profiler = ce;
y.StrictMode = le;
y.Suspense = he;
y.SuspenseList = ge;
y.isAsyncMode = function() {
  return !1;
};
y.isConcurrentMode = function() {
  return !1;
};
y.isContextConsumer = function(e) {
  return R(e) === fe;
};
y.isContextProvider = function(e) {
  return R(e) === ue;
};
y.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === Re;
};
y.isForwardRef = function(e) {
  return R(e) === de;
};
y.isFragment = function(e) {
  return R(e) === ae;
};
y.isLazy = function(e) {
  return R(e) === me;
};
y.isMemo = function(e) {
  return R(e) === pe;
};
y.isPortal = function(e) {
  return R(e) === Le;
};
y.isProfiler = function(e) {
  return R(e) === ce;
};
y.isStrictMode = function(e) {
  return R(e) === le;
};
y.isSuspense = function(e) {
  return R(e) === he;
};
y.isSuspenseList = function(e) {
  return R(e) === ge;
};
y.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === ae || e === ce || e === le || e === he || e === ge || e === Jr || typeof e == "object" && e !== null && (e.$$typeof === me || e.$$typeof === pe || e.$$typeof === ue || e.$$typeof === fe || e.$$typeof === de || e.$$typeof === wt || e.getModuleId !== void 0);
};
y.typeOf = R;
Number(zt.split(".")[0]);
function at(e, t, n, o) {
  var r = I({}, t[e]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var l = re(a, 2), c = l[0], f = l[1];
      if (r != null && r[c] || r != null && r[f]) {
        var u;
        (u = r[f]) !== null && u !== void 0 || (r[f] = r == null ? void 0 : r[c]);
      }
    });
  }
  var s = I(I({}, n), r);
  return Object.keys(s).forEach(function(a) {
    s[a] === t[a] && delete s[a];
  }), s;
}
var Tt = typeof CSSINJS_STATISTIC < "u", ke = !0;
function He() {
  for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++)
    t[n] = arguments[n];
  if (!Tt)
    return Object.assign.apply(Object, [{}].concat(t));
  ke = !1;
  var o = {};
  return t.forEach(function(r) {
    if (H(r) === "object") {
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
  }), ke = !0, o;
}
var lt = {};
function Yr() {
}
var en = function(t) {
  var n, o = t, r = Yr;
  return Tt && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(t, {
    get: function(s, a) {
      if (ke) {
        var l;
        (l = n) === null || l === void 0 || l.add(a);
      }
      return s[a];
    }
  }), r = function(s, a) {
    var l;
    lt[s] = {
      global: Array.from(n),
      component: I(I({}, (l = lt[s]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function ct(e, t, n) {
  if (typeof n == "function") {
    var o;
    return n(He(t, (o = t[e]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function tn(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(i) {
        return Ue(i);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(i) {
        return Ue(i);
      }).join(","), ")");
    }
  };
}
var rn = 1e3 * 60 * 10, nn = /* @__PURE__ */ function() {
  function e() {
    ie(this, e), T(this, "map", /* @__PURE__ */ new Map()), T(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), T(this, "nextID", 0), T(this, "lastAccessBeat", /* @__PURE__ */ new Map()), T(this, "accessBeat", 0);
  }
  return se(e, [{
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
        return i && H(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(H(i), "_").concat(i);
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
          o - r > rn && (n.map.delete(i), n.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), ut = new nn();
function on(e, t) {
  return b.useMemo(function() {
    var n = ut.get(t);
    if (n)
      return n;
    var o = e();
    return ut.set(t, o), o;
  }, t);
}
var sn = function() {
  return {};
};
function an(e) {
  var t = e.useCSP, n = t === void 0 ? sn : t, o = e.useToken, r = e.usePrefix, i = e.getResetStyles, s = e.getCommonStyle, a = e.getCompUnitless;
  function l(d, v, S, p) {
    var h = Array.isArray(d) ? d[0] : d;
    function x(O) {
      return "".concat(String(h)).concat(O.slice(0, 1).toUpperCase()).concat(O.slice(1));
    }
    var _ = (p == null ? void 0 : p.unitless) || {}, E = typeof a == "function" ? a(d) : {}, g = I(I({}, E), {}, T({}, x("zIndexPopup"), !0));
    Object.keys(_).forEach(function(O) {
      g[x(O)] = _[O];
    });
    var C = I(I({}, p), {}, {
      unitless: g,
      prefixToken: x
    }), m = f(d, v, S, C), w = c(h, S, C);
    return function(O) {
      var P = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : O, L = m(O, P), D = re(L, 2), j = D[1], X = w(P), k = re(X, 2), A = k[0], K = k[1];
      return [A, j, K];
    };
  }
  function c(d, v, S) {
    var p = S.unitless, h = S.injectStyle, x = h === void 0 ? !0 : h, _ = S.prefixToken, E = S.ignore, g = function(w) {
      var O = w.rootCls, P = w.cssVar, L = P === void 0 ? {} : P, D = o(), j = D.realToken;
      return Wt({
        path: [d],
        prefix: L.prefix,
        key: L.key,
        unitless: p,
        ignore: E,
        token: j,
        scope: O
      }, function() {
        var X = ct(d, j, v), k = at(d, j, X, {
          deprecatedTokens: S == null ? void 0 : S.deprecatedTokens
        });
        return Object.keys(X).forEach(function(A) {
          k[_(A)] = k[A], delete k[A];
        }), k;
      }), null;
    }, C = function(w) {
      var O = o(), P = O.cssVar;
      return [function(L) {
        return x && P ? /* @__PURE__ */ b.createElement(b.Fragment, null, /* @__PURE__ */ b.createElement(g, {
          rootCls: w,
          cssVar: P,
          component: d
        }), L) : L;
      }, P == null ? void 0 : P.key];
    };
    return C;
  }
  function f(d, v, S) {
    var p = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = Array.isArray(d) ? d : [d, d], x = re(h, 1), _ = x[0], E = h.join("-"), g = e.layer || {
      name: "antd"
    };
    return function(C) {
      var m = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : C, w = o(), O = w.theme, P = w.realToken, L = w.hashId, D = w.token, j = w.cssVar, X = r(), k = X.rootPrefixCls, A = X.iconPrefixCls, K = n(), be = j ? "css" : "js", Mt = on(function() {
        var F = /* @__PURE__ */ new Set();
        return j && Object.keys(p.unitless || {}).forEach(function(Q) {
          F.add(ve(Q, j.prefix)), F.add(ve(Q, st(_, j.prefix)));
        }), Qr(be, F);
      }, [be, _, j == null ? void 0 : j.prefix]), Ae = tn(be), Pt = Ae.max, Et = Ae.min, $e = {
        theme: O,
        token: D,
        hashId: L,
        nonce: function() {
          return K.nonce;
        },
        clientOnly: p.clientOnly,
        layer: g,
        // antd is always at top of styles
        order: p.order || -999
      };
      typeof i == "function" && Ge(I(I({}, $e), {}, {
        clientOnly: !1,
        path: ["Shared", k]
      }), function() {
        return i(D, {
          prefix: {
            rootPrefixCls: k,
            iconPrefixCls: A
          },
          csp: K
        });
      });
      var jt = Ge(I(I({}, $e), {}, {
        path: [E, C, A]
      }), function() {
        if (p.injectStyle === !1)
          return [];
        var F = en(D), Q = F.token, It = F.flush, N = ct(_, P, S), kt = ".".concat(C), Be = at(_, P, N, {
          deprecatedTokens: p.deprecatedTokens
        });
        j && N && H(N) === "object" && Object.keys(N).forEach(function(De) {
          N[De] = "var(".concat(ve(De, st(_, j.prefix)), ")");
        });
        var ze = He(Q, {
          componentCls: kt,
          prefixCls: C,
          iconCls: ".".concat(A),
          antCls: ".".concat(k),
          calc: Mt,
          // @ts-ignore
          max: Pt,
          // @ts-ignore
          min: Et
        }, j ? N : Be), Rt = v(ze, {
          hashId: L,
          prefixCls: C,
          rootPrefixCls: k,
          iconPrefixCls: A
        });
        It(_, Be);
        var Lt = typeof s == "function" ? s(ze, C, m, p.resetFont) : null;
        return [p.resetStyle === !1 ? null : Lt, Rt];
      });
      return [jt, L];
    };
  }
  function u(d, v, S) {
    var p = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = f(d, v, S, I({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, p)), x = function(E) {
      var g = E.prefixCls, C = E.rootCls, m = C === void 0 ? g : C;
      return h(g, m), null;
    };
    return x;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: u,
    genComponentStyleHook: f
  };
}
const ln = {
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
}, cn = Object.assign(Object.assign({}, ln), {
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
}), M = Math.round;
function Ce(e, t) {
  const n = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = t(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const ft = (e, t, n) => n === 0 ? e : e / 100;
function G(e, t) {
  const n = t || 255;
  return e > n ? n : e < 0 ? 0 : e;
}
class B {
  constructor(t) {
    T(this, "isValid", !0), T(this, "r", 0), T(this, "g", 0), T(this, "b", 0), T(this, "a", 1), T(this, "_h", void 0), T(this, "_s", void 0), T(this, "_l", void 0), T(this, "_v", void 0), T(this, "_max", void 0), T(this, "_min", void 0), T(this, "_brightness", void 0);
    function n(o) {
      return o[0] in t && o[1] in t && o[2] in t;
    }
    if (t) if (typeof t == "string") {
      let r = function(i) {
        return o.startsWith(i);
      };
      const o = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (t instanceof B)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (n("rgb"))
      this.r = G(t.r), this.g = G(t.g), this.b = G(t.b), this.a = typeof t.a == "number" ? G(t.a, 1) : 1;
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
    function t(i) {
      const s = i / 255;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    }
    const n = t(this.r), o = t(this.g), r = t(this.b);
    return 0.2126 * n + 0.7152 * o + 0.0722 * r;
  }
  getHue() {
    if (typeof this._h > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._h = 0 : this._h = M(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
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
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() - t / 100;
    return r < 0 && (r = 0), this._c({
      h: n,
      s: o,
      l: r,
      a: this.a
    });
  }
  lighten(t = 10) {
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() + t / 100;
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
  mix(t, n = 50) {
    const o = this._c(t), r = n / 100, i = (a) => (o[a] - this[a]) * r + this[a], s = {
      r: M(i("r")),
      g: M(i("g")),
      b: M(i("b")),
      a: M(i("a") * 100) / 100
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
    const n = this._c(t), o = this.a + n.a * (1 - this.a), r = (i) => M((this[i] * this.a + n[i] * n.a * (1 - this.a)) / o);
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
    const o = (this.g || 0).toString(16);
    t += o.length === 2 ? o : "0" + o;
    const r = (this.b || 0).toString(16);
    if (t += r.length === 2 ? r : "0" + r, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const i = M(this.a * 255).toString(16);
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
    const t = this.getHue(), n = M(this.getSaturation() * 100), o = M(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${t},${n}%,${o}%,${this.a})` : `hsl(${t},${n}%,${o}%)`;
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
  _sc(t, n, o) {
    const r = this.clone();
    return r[t] = G(n, o), r;
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
    function o(r, i) {
      return parseInt(n[r] + n[i || r], 16);
    }
    n.length < 6 ? (this.r = o(0), this.g = o(1), this.b = o(2), this.a = n[3] ? o(3) / 255 : 1) : (this.r = o(0, 1), this.g = o(2, 3), this.b = o(4, 5), this.a = n[6] ? o(6, 7) / 255 : 1);
  }
  fromHsl({
    h: t,
    s: n,
    l: o,
    a: r
  }) {
    if (this._h = t % 360, this._s = n, this._l = o, this.a = typeof r == "number" ? r : 1, n <= 0) {
      const d = M(o * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let i = 0, s = 0, a = 0;
    const l = t / 60, c = (1 - Math.abs(2 * o - 1)) * n, f = c * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (i = c, s = f) : l >= 1 && l < 2 ? (i = f, s = c) : l >= 2 && l < 3 ? (s = c, a = f) : l >= 3 && l < 4 ? (s = f, a = c) : l >= 4 && l < 5 ? (i = f, a = c) : l >= 5 && l < 6 && (i = c, a = f);
    const u = o - c / 2;
    this.r = M((i + u) * 255), this.g = M((s + u) * 255), this.b = M((a + u) * 255);
  }
  fromHsv({
    h: t,
    s: n,
    v: o,
    a: r
  }) {
    this._h = t % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const i = M(o * 255);
    if (this.r = i, this.g = i, this.b = i, n <= 0)
      return;
    const s = t / 60, a = Math.floor(s), l = s - a, c = M(o * (1 - n) * 255), f = M(o * (1 - n * l) * 255), u = M(o * (1 - n * (1 - l)) * 255);
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
  fromHsvString(t) {
    const n = Ce(t, ft);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(t) {
    const n = Ce(t, ft);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(t) {
    const n = Ce(t, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? M(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function we(e) {
  return e >= 0 && e <= 255;
}
function J(e, t) {
  const {
    r: n,
    g: o,
    b: r,
    a: i
  } = new B(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: s,
    g: a,
    b: l
  } = new B(t).toRgb();
  for (let c = 0.01; c <= 1; c += 0.01) {
    const f = Math.round((n - s * (1 - c)) / c), u = Math.round((o - a * (1 - c)) / c), d = Math.round((r - l * (1 - c)) / c);
    if (we(f) && we(u) && we(d))
      return new B({
        r: f,
        g: u,
        b: d,
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
var un = function(e, t) {
  var n = {};
  for (var o in e) Object.prototype.hasOwnProperty.call(e, o) && t.indexOf(o) < 0 && (n[o] = e[o]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(e); r < o.length; r++)
    t.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(e, o[r]) && (n[o[r]] = e[o[r]]);
  return n;
};
function fn(e) {
  const {
    override: t
  } = e, n = un(e, ["override"]), o = Object.assign({}, t);
  Object.keys(cn).forEach((d) => {
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
    colorSplit: J(r.colorBorderSecondary, r.colorBgContainer),
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
    colorErrorOutline: J(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: J(r.colorWarningBg, r.colorBgContainer),
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
    controlOutline: J(r.colorPrimaryBg, r.colorBgContainer),
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
const dn = {
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
}, hn = {
  motionBase: !0,
  motionUnit: !0
}, gn = Ut(Me.defaultAlgorithm), pn = {
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
}, Ot = (e, t, n) => {
  const o = n.getDerivativeToken(e), {
    override: r,
    ...i
  } = t;
  let s = {
    ...o,
    override: r
  };
  return s = fn(s), i && Object.entries(i).forEach(([a, l]) => {
    const {
      theme: c,
      ...f
    } = l;
    let u = f;
    c && (u = Ot({
      ...s,
      ...f
    }, {
      override: f
    }, c)), s[a] = u;
  }), s;
};
function mn() {
  const {
    token: e,
    hashed: t,
    theme: n = gn,
    override: o,
    cssVar: r
  } = b.useContext(Me._internalContext), [i, s, a] = Gt(n, [Me.defaultSeed, e], {
    salt: `${Ar}-${t || ""}`,
    override: o,
    getComputedToken: Ot,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: dn,
      ignore: hn,
      preserve: pn
    }
  });
  return [n, a, t ? s : "", i, r];
}
const {
  genStyleHooks: bn
} = an({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = je();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, n, o, r] = mn();
    return {
      theme: e,
      realToken: t,
      hashId: n,
      token: o,
      cssVar: r
    };
  },
  useCSP: () => {
    const {
      csp: e
    } = je();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), yn = (e) => {
  const {
    componentCls: t,
    calc: n
  } = e, o = n(e.fontSizeHeading3).mul(e.lineHeightHeading3).equal(), r = n(e.fontSize).mul(e.lineHeight).equal();
  return {
    [t]: {
      gap: e.padding,
      // ======================== Icon ========================
      [`${t}-icon`]: {
        height: n(o).add(r).add(e.paddingXXS).equal(),
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
}, vn = (e) => {
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
}, xn = () => ({}), Sn = bn("Welcome", (e) => {
  const t = He(e, {});
  return [yn(t), vn(t)];
}, xn);
function _n(e, t) {
  const {
    prefixCls: n,
    rootClassName: o,
    className: r,
    style: i,
    variant: s = "filled",
    // Semantic
    classNames: a = {},
    styles: l = {},
    // Layout
    icon: c,
    title: f,
    description: u,
    extra: d
  } = e, {
    direction: v,
    getPrefixCls: S
  } = je(), p = S("welcome", n), h = Dr("welcome"), [x, _, E] = Sn(p), g = b.useMemo(() => {
    if (!c)
      return null;
    let w = c;
    return typeof c == "string" && c.startsWith("http") && (w = /* @__PURE__ */ b.createElement("img", {
      src: c,
      alt: "icon"
    })), /* @__PURE__ */ b.createElement("div", {
      className: U(`${p}-icon`, h.classNames.icon, a.icon),
      style: l.icon
    }, w);
  }, [c]), C = b.useMemo(() => f ? /* @__PURE__ */ b.createElement(We.Title, {
    level: 4,
    className: U(`${p}-title`, h.classNames.title, a.title),
    style: l.title
  }, f) : null, [f]), m = b.useMemo(() => d ? /* @__PURE__ */ b.createElement("div", {
    className: U(`${p}-extra`, h.classNames.extra, a.extra),
    style: l.extra
  }, d) : null, [d]);
  return x(/* @__PURE__ */ b.createElement(ye, {
    ref: t,
    className: U(p, h.className, r, o, _, E, `${p}-${s}`, {
      [`${p}-rtl`]: v === "rtl"
    }),
    style: i
  }, g, /* @__PURE__ */ b.createElement(ye, {
    vertical: !0,
    className: `${p}-content-wrapper`
  }, d ? /* @__PURE__ */ b.createElement(ye, {
    align: "flex-start",
    className: `${p}-title-wrapper`
  }, C, m) : C, u && /* @__PURE__ */ b.createElement(We.Text, {
    className: U(`${p}-description`, h.classNames.description, a.description),
    style: l.description
  }, u))));
}
const Cn = /* @__PURE__ */ b.forwardRef(_n);
new Intl.Collator(0, {
  numeric: 1
}).compare;
typeof process < "u" && process.versions && process.versions.node;
var $;
class Rn extends TransformStream {
  /** Constructs a new instance. */
  constructor(n = {
    allowCR: !1
  }) {
    super({
      transform: (o, r) => {
        for (o = V(this, $) + o; ; ) {
          const i = o.indexOf(`
`), s = n.allowCR ? o.indexOf("\r") : -1;
          if (s !== -1 && s !== o.length - 1 && (i === -1 || i - 1 > s)) {
            r.enqueue(o.slice(0, s)), o = o.slice(s + 1);
            continue;
          }
          if (i === -1) break;
          const a = o[i - 1] === "\r" ? i - 1 : i;
          r.enqueue(o.slice(0, a)), o = o.slice(i + 1);
        }
        Ve(this, $, o);
      },
      flush: (o) => {
        if (V(this, $) === "") return;
        const r = n.allowCR && V(this, $).endsWith("\r") ? V(this, $).slice(0, -1) : V(this, $);
        o.enqueue(r);
      }
    });
    Ne(this, $, "");
  }
}
$ = new WeakMap();
function wn(e) {
  try {
    const t = new URL(e);
    return t.protocol === "http:" || t.protocol === "https:";
  } catch {
    return !1;
  }
}
function Tn() {
  const e = document.querySelector(".gradio-container");
  if (!e)
    return "";
  const t = e.className.match(/gradio-container-(.+)/);
  return t ? t[1] : "";
}
const On = +Tn()[0];
function Mn(e, t, n) {
  const o = On >= 5 ? "gradio_api/" : "";
  return e == null ? n ? `/proxy=${n}${o}file=` : `${t}${o}file=` : wn(e) ? e : n ? `/proxy=${n}${o}file=${e}` : `${t}/${o}file=${e}`;
}
const Pn = (e) => !!e.url;
function En(e, t, n) {
  if (e)
    return Pn(e) ? e.url : typeof e == "string" ? e.startsWith("http") ? e : Mn(e, t, n) : e;
}
const Ln = Ir(({
  slots: e,
  children: t,
  urlProxyUrl: n,
  urlRoot: o,
  ...r
}) => /* @__PURE__ */ z.jsxs(z.Fragment, {
  children: [/* @__PURE__ */ z.jsx("div", {
    style: {
      display: "none"
    },
    children: t
  }), /* @__PURE__ */ z.jsx(Cn, {
    ...r,
    extra: e.extra ? /* @__PURE__ */ z.jsx(Z, {
      slot: e.extra
    }) : r.extra,
    icon: e.icon ? /* @__PURE__ */ z.jsx(Z, {
      slot: e.icon
    }) : En(r.icon, o, n),
    title: e.title ? /* @__PURE__ */ z.jsx(Z, {
      slot: e.title
    }) : r.title,
    description: e.description ? /* @__PURE__ */ z.jsx(Z, {
      slot: e.description
    }) : r.description
  })]
}));
export {
  Ln as Welcome,
  Ln as default
};
