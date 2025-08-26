import { i as At, a as _e, r as Bt, Z as Q, g as zt, c as V } from "./Index-_z-cNxRS.js";
const _ = window.ms_globals.React, jt = window.ms_globals.React.forwardRef, kt = window.ms_globals.React.useRef, Rt = window.ms_globals.React.useState, $t = window.ms_globals.React.useEffect, Lt = window.ms_globals.React.version, Ht = window.ms_globals.React.useMemo, Se = window.ms_globals.ReactDOM.createPortal, Dt = window.ms_globals.internalContext.useContextPropsContext, De = window.ms_globals.internalContext.ContextPropsProvider, Xt = window.ms_globals.createItemsContext.createItemsContext, Ft = window.ms_globals.antd.ConfigProvider, Ce = window.ms_globals.antd.theme, Nt = window.ms_globals.antd.Typography, we = window.ms_globals.antdCssinjs.unit, pe = window.ms_globals.antdCssinjs.token2CSSVar, Xe = window.ms_globals.antdCssinjs.useStyleRegister, Vt = window.ms_globals.antdCssinjs.useCSSVarRegister, Wt = window.ms_globals.antdCssinjs.createTheme, Gt = window.ms_globals.antdCssinjs.useCacheToken;
var Ut = /\s/;
function qt(t) {
  for (var e = t.length; e-- && Ut.test(t.charAt(e)); )
    ;
  return e;
}
var Kt = /^\s+/;
function Qt(t) {
  return t && t.slice(0, qt(t) + 1).replace(Kt, "");
}
var Fe = NaN, Zt = /^[-+]0x[0-9a-f]+$/i, Jt = /^0b[01]+$/i, Yt = /^0o[0-7]+$/i, er = parseInt;
function Ne(t) {
  if (typeof t == "number")
    return t;
  if (At(t))
    return Fe;
  if (_e(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = _e(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Qt(t);
  var n = Jt.test(t);
  return n || Yt.test(t) ? er(t.slice(2), n ? 2 : 8) : Zt.test(t) ? Fe : +t;
}
var me = function() {
  return Bt.Date.now();
}, tr = "Expected a function", rr = Math.max, nr = Math.min;
function or(t, e, n) {
  var o, r, s, i, a, l, c = 0, f = !1, u = !1, d = !0;
  if (typeof t != "function")
    throw new TypeError(tr);
  e = Ne(e) || 0, _e(n) && (f = !!n.leading, u = "maxWait" in n, s = u ? rr(Ne(n.maxWait) || 0, e) : s, d = "trailing" in n ? !!n.trailing : d);
  function b(p) {
    var T = o, C = r;
    return o = r = void 0, c = p, i = t.apply(C, T), i;
  }
  function x(p) {
    return c = p, a = setTimeout(y, e), f ? b(p) : i;
  }
  function g(p) {
    var T = p - l, C = p - c, I = e - T;
    return u ? nr(I, s - C) : I;
  }
  function h(p) {
    var T = p - l, C = p - c;
    return l === void 0 || T >= e || T < 0 || u && C >= s;
  }
  function y() {
    var p = me();
    if (h(p))
      return v(p);
    a = setTimeout(y, g(p));
  }
  function v(p) {
    return a = void 0, d && o ? b(p) : (o = r = void 0, i);
  }
  function P() {
    a !== void 0 && clearTimeout(a), c = 0, o = l = r = a = void 0;
  }
  function m() {
    return a === void 0 ? i : v(me());
  }
  function w() {
    var p = me(), T = h(p);
    if (o = arguments, r = this, l = p, T) {
      if (a === void 0)
        return x(l);
      if (u)
        return clearTimeout(a), a = setTimeout(y, e), b(l);
    }
    return a === void 0 && (a = setTimeout(y, e)), i;
  }
  return w.cancel = P, w.flush = m, w;
}
var it = {
  exports: {}
}, te = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var sr = _, ir = Symbol.for("react.element"), ar = Symbol.for("react.fragment"), lr = Object.prototype.hasOwnProperty, cr = sr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ur = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function at(t, e, n) {
  var o, r = {}, s = null, i = null;
  n !== void 0 && (s = "" + n), e.key !== void 0 && (s = "" + e.key), e.ref !== void 0 && (i = e.ref);
  for (o in e) lr.call(e, o) && !ur.hasOwnProperty(o) && (r[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) r[o] === void 0 && (r[o] = e[o]);
  return {
    $$typeof: ir,
    type: t,
    key: s,
    ref: i,
    props: r,
    _owner: cr.current
  };
}
te.Fragment = ar;
te.jsx = at;
te.jsxs = at;
it.exports = te;
var L = it.exports;
const {
  SvelteComponent: fr,
  assign: Ve,
  binding_callbacks: We,
  check_outros: dr,
  children: lt,
  claim_element: ct,
  claim_space: hr,
  component_subscribe: Ge,
  compute_slots: gr,
  create_slot: pr,
  detach: N,
  element: ut,
  empty: Ue,
  exclude_internal_props: qe,
  get_all_dirty_from_scope: mr,
  get_slot_changes: br,
  group_outros: yr,
  init: vr,
  insert_hydration: Z,
  safe_not_equal: xr,
  set_custom_element_data: ft,
  space: Sr,
  transition_in: J,
  transition_out: Te,
  update_slot_base: _r
} = window.__gradio__svelte__internal, {
  beforeUpdate: Cr,
  getContext: wr,
  onDestroy: Tr,
  setContext: Or
} = window.__gradio__svelte__internal;
function Ke(t) {
  let e, n;
  const o = (
    /*#slots*/
    t[7].default
  ), r = pr(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = ut("svelte-slot"), r && r.c(), this.h();
    },
    l(s) {
      e = ct(s, "SVELTE-SLOT", {
        class: !0
      });
      var i = lt(e);
      r && r.l(i), i.forEach(N), this.h();
    },
    h() {
      ft(e, "class", "svelte-1rt0kpf");
    },
    m(s, i) {
      Z(s, e, i), r && r.m(e, null), t[9](e), n = !0;
    },
    p(s, i) {
      r && r.p && (!n || i & /*$$scope*/
      64) && _r(
        r,
        o,
        s,
        /*$$scope*/
        s[6],
        n ? br(
          o,
          /*$$scope*/
          s[6],
          i,
          null
        ) : mr(
          /*$$scope*/
          s[6]
        ),
        null
      );
    },
    i(s) {
      n || (J(r, s), n = !0);
    },
    o(s) {
      Te(r, s), n = !1;
    },
    d(s) {
      s && N(e), r && r.d(s), t[9](null);
    }
  };
}
function Pr(t) {
  let e, n, o, r, s = (
    /*$$slots*/
    t[4].default && Ke(t)
  );
  return {
    c() {
      e = ut("react-portal-target"), n = Sr(), s && s.c(), o = Ue(), this.h();
    },
    l(i) {
      e = ct(i, "REACT-PORTAL-TARGET", {
        class: !0
      }), lt(e).forEach(N), n = hr(i), s && s.l(i), o = Ue(), this.h();
    },
    h() {
      ft(e, "class", "svelte-1rt0kpf");
    },
    m(i, a) {
      Z(i, e, a), t[8](e), Z(i, n, a), s && s.m(i, a), Z(i, o, a), r = !0;
    },
    p(i, [a]) {
      /*$$slots*/
      i[4].default ? s ? (s.p(i, a), a & /*$$slots*/
      16 && J(s, 1)) : (s = Ke(i), s.c(), J(s, 1), s.m(o.parentNode, o)) : s && (yr(), Te(s, 1, 1, () => {
        s = null;
      }), dr());
    },
    i(i) {
      r || (J(s), r = !0);
    },
    o(i) {
      Te(s), r = !1;
    },
    d(i) {
      i && (N(e), N(n), N(o)), t[8](null), s && s.d(i);
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
function Mr(t, e, n) {
  let o, r, {
    $$slots: s = {},
    $$scope: i
  } = e;
  const a = gr(s);
  let {
    svelteInit: l
  } = e;
  const c = Q(Qe(e)), f = Q();
  Ge(t, f, (m) => n(0, o = m));
  const u = Q();
  Ge(t, u, (m) => n(1, r = m));
  const d = [], b = wr("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: g,
    subSlotIndex: h
  } = zt() || {}, y = l({
    parent: b,
    props: c,
    target: f,
    slot: u,
    slotKey: x,
    slotIndex: g,
    subSlotIndex: h,
    onDestroy(m) {
      d.push(m);
    }
  });
  Or("$$ms-gr-react-wrapper", y), Cr(() => {
    c.set(Qe(e));
  }), Tr(() => {
    d.forEach((m) => m());
  });
  function v(m) {
    We[m ? "unshift" : "push"](() => {
      o = m, f.set(o);
    });
  }
  function P(m) {
    We[m ? "unshift" : "push"](() => {
      r = m, u.set(r);
    });
  }
  return t.$$set = (m) => {
    n(17, e = Ve(Ve({}, e), qe(m))), "svelteInit" in m && n(5, l = m.svelteInit), "$$scope" in m && n(6, i = m.$$scope);
  }, e = qe(e), [o, r, f, u, a, l, i, s, v, P];
}
class Ir extends fr {
  constructor(e) {
    super(), vr(this, e, Mr, Pr, xr, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: On
} = window.__gradio__svelte__internal, Ze = window.ms_globals.rerender, be = window.ms_globals.tree;
function Er(t, e = {}) {
  function n(o) {
    const r = Q(), s = new Ir({
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
          }, l = i.parent ?? be;
          return l.nodes = [...l.nodes, a], Ze({
            createPortal: Se,
            node: be
          }), i.onDestroy(() => {
            l.nodes = l.nodes.filter((c) => c.svelteInstance !== r), Ze({
              createPortal: Se,
              node: be
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
const jr = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function kr(t) {
  return t ? Object.keys(t).reduce((e, n) => {
    const o = t[n];
    return e[n] = Rr(n, o), e;
  }, {}) : {};
}
function Rr(t, e) {
  return typeof e == "number" && !jr.includes(t) ? e + "px" : e;
}
function Oe(t) {
  const e = [], n = t.cloneNode(!1);
  if (t._reactElement) {
    const r = _.Children.toArray(t._reactElement.props.children).map((s) => {
      if (_.isValidElement(s) && s.props.__slot__) {
        const {
          portals: i,
          clonedElement: a
        } = Oe(s.props.el);
        return _.cloneElement(s, {
          ...s.props,
          el: a,
          children: [..._.Children.toArray(s.props.children), ...i]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(Se(_.cloneElement(t._reactElement, {
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
      } = Oe(s);
      e.push(...a), n.appendChild(i);
    } else s.nodeType === 3 && n.appendChild(s.cloneNode());
  }
  return {
    clonedElement: n,
    portals: e
  };
}
function $r(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const Pe = jt(({
  slot: t,
  clone: e,
  className: n,
  style: o,
  observeAttributes: r
}, s) => {
  const i = kt(), [a, l] = Rt([]), {
    forceClone: c
  } = Dt(), f = c ? !0 : e;
  return $t(() => {
    var g;
    if (!i.current || !t)
      return;
    let u = t;
    function d() {
      let h = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (h = u.children[0], h.tagName.toLowerCase() === "react-portal-target" && h.children[0] && (h = h.children[0])), $r(s, h), n && h.classList.add(...n.split(" ")), o) {
        const y = kr(o);
        Object.keys(y).forEach((v) => {
          h.style[v] = y[v];
        });
      }
    }
    let b = null, x = null;
    if (f && window.MutationObserver) {
      let h = function() {
        var m, w, p;
        (m = i.current) != null && m.contains(u) && ((w = i.current) == null || w.removeChild(u));
        const {
          portals: v,
          clonedElement: P
        } = Oe(t);
        u = P, l(v), u.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          d();
        }, 50), (p = i.current) == null || p.appendChild(u);
      };
      h();
      const y = or(() => {
        h(), b == null || b.disconnect(), b == null || b.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      b = new window.MutationObserver(y), b.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", d(), (g = i.current) == null || g.appendChild(u);
    return () => {
      var h, y;
      u.style.display = "", (h = i.current) != null && h.contains(u) && ((y = i.current) == null || y.removeChild(u)), b == null || b.disconnect();
    };
  }, [t, f, n, o, s, r, c]), _.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...a);
}), Lr = "1.6.0";
function Me() {
  return Me = Object.assign ? Object.assign.bind() : function(t) {
    for (var e = 1; e < arguments.length; e++) {
      var n = arguments[e];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (t[o] = n[o]);
    }
    return t;
  }, Me.apply(null, arguments);
}
function H(t) {
  "@babel/helpers - typeof";
  return H = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(e) {
    return typeof e;
  } : function(e) {
    return e && typeof Symbol == "function" && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e;
  }, H(t);
}
function Hr(t, e) {
  if (H(t) != "object" || !t) return t;
  var n = t[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(t, e);
    if (H(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (e === "string" ? String : Number)(t);
}
function dt(t) {
  var e = Hr(t, "string");
  return H(e) == "symbol" ? e : e + "";
}
function O(t, e, n) {
  return (e = dt(e)) in t ? Object.defineProperty(t, e, {
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
function j(t) {
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
const Ar = /* @__PURE__ */ _.createContext({}), Br = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, zr = (t) => {
  const e = _.useContext(Ar);
  return _.useMemo(() => ({
    ...Br,
    ...e[t]
  }), [e[t]]);
};
function Ie() {
  const {
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = _.useContext(Ft.ConfigContext);
  return {
    theme: r,
    getPrefixCls: t,
    direction: e,
    csp: n,
    iconPrefixCls: o
  };
}
function Dr(t) {
  if (Array.isArray(t)) return t;
}
function Xr(t, e) {
  var n = t == null ? null : typeof Symbol < "u" && t[Symbol.iterator] || t["@@iterator"];
  if (n != null) {
    var o, r, s, i, a = [], l = !0, c = !1;
    try {
      if (s = (n = n.call(t)).next, e === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (o = s.call(n)).done) && (a.push(o.value), a.length !== e); l = !0) ;
    } catch (f) {
      c = !0, r = f;
    } finally {
      try {
        if (!l && n.return != null && (i = n.return(), Object(i) !== i)) return;
      } finally {
        if (c) throw r;
      }
    }
    return a;
  }
}
function Ye(t, e) {
  (e == null || e > t.length) && (e = t.length);
  for (var n = 0, o = Array(e); n < e; n++) o[n] = t[n];
  return o;
}
function Fr(t, e) {
  if (t) {
    if (typeof t == "string") return Ye(t, e);
    var n = {}.toString.call(t).slice(8, -1);
    return n === "Object" && t.constructor && (n = t.constructor.name), n === "Map" || n === "Set" ? Array.from(t) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? Ye(t, e) : void 0;
  }
}
function Nr() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function Y(t, e) {
  return Dr(t) || Xr(t, e) || Fr(t, e) || Nr();
}
function re(t, e) {
  if (!(t instanceof e)) throw new TypeError("Cannot call a class as a function");
}
function Vr(t, e) {
  for (var n = 0; n < e.length; n++) {
    var o = e[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(t, dt(o.key), o);
  }
}
function ne(t, e, n) {
  return e && Vr(t.prototype, e), Object.defineProperty(t, "prototype", {
    writable: !1
  }), t;
}
function G(t) {
  if (t === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return t;
}
function Ee(t, e) {
  return Ee = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, Ee(t, e);
}
function ht(t, e) {
  if (typeof e != "function" && e !== null) throw new TypeError("Super expression must either be null or a function");
  t.prototype = Object.create(e && e.prototype, {
    constructor: {
      value: t,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(t, "prototype", {
    writable: !1
  }), e && Ee(t, e);
}
function ee(t) {
  return ee = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(e) {
    return e.__proto__ || Object.getPrototypeOf(e);
  }, ee(t);
}
function gt() {
  try {
    var t = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (gt = function() {
    return !!t;
  })();
}
function Wr(t, e) {
  if (e && (H(e) == "object" || typeof e == "function")) return e;
  if (e !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return G(t);
}
function pt(t) {
  var e = gt();
  return function() {
    var n, o = ee(t);
    if (e) {
      var r = ee(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return Wr(this, n);
  };
}
var mt = /* @__PURE__ */ ne(function t() {
  re(this, t);
}), bt = "CALC_UNIT", Gr = new RegExp(bt, "g");
function ye(t) {
  return typeof t == "number" ? "".concat(t).concat(bt) : t;
}
var Ur = /* @__PURE__ */ function(t) {
  ht(n, t);
  var e = pt(n);
  function n(o, r) {
    var s;
    re(this, n), s = e.call(this), O(G(s), "result", ""), O(G(s), "unitlessCssVar", void 0), O(G(s), "lowPriority", void 0);
    var i = H(o);
    return s.unitlessCssVar = r, o instanceof n ? s.result = "(".concat(o.result, ")") : i === "number" ? s.result = ye(o) : i === "string" && (s.result = o), s;
  }
  return ne(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(ye(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(ye(r))), this.lowPriority = !0, this;
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
      return typeof a == "boolean" ? l = a : Array.from(this.unitlessCssVar).some(function(c) {
        return s.result.includes(c);
      }) && (l = !1), this.result = this.result.replace(Gr, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(mt), qr = /* @__PURE__ */ function(t) {
  ht(n, t);
  var e = pt(n);
  function n(o) {
    var r;
    return re(this, n), r = e.call(this), O(G(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return ne(n, [{
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
}(mt), Kr = function(e, n) {
  var o = e === "css" ? Ur : qr;
  return function(r) {
    return new o(r, n);
  };
}, et = function(e, n) {
  return "".concat([n, e.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
}, S = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var ke = Symbol.for("react.element"), Re = Symbol.for("react.portal"), oe = Symbol.for("react.fragment"), se = Symbol.for("react.strict_mode"), ie = Symbol.for("react.profiler"), ae = Symbol.for("react.provider"), le = Symbol.for("react.context"), Qr = Symbol.for("react.server_context"), ce = Symbol.for("react.forward_ref"), ue = Symbol.for("react.suspense"), fe = Symbol.for("react.suspense_list"), de = Symbol.for("react.memo"), he = Symbol.for("react.lazy"), Zr = Symbol.for("react.offscreen"), yt;
yt = Symbol.for("react.module.reference");
function R(t) {
  if (typeof t == "object" && t !== null) {
    var e = t.$$typeof;
    switch (e) {
      case ke:
        switch (t = t.type, t) {
          case oe:
          case ie:
          case se:
          case ue:
          case fe:
            return t;
          default:
            switch (t = t && t.$$typeof, t) {
              case Qr:
              case le:
              case ce:
              case he:
              case de:
              case ae:
                return t;
              default:
                return e;
            }
        }
      case Re:
        return e;
    }
  }
}
S.ContextConsumer = le;
S.ContextProvider = ae;
S.Element = ke;
S.ForwardRef = ce;
S.Fragment = oe;
S.Lazy = he;
S.Memo = de;
S.Portal = Re;
S.Profiler = ie;
S.StrictMode = se;
S.Suspense = ue;
S.SuspenseList = fe;
S.isAsyncMode = function() {
  return !1;
};
S.isConcurrentMode = function() {
  return !1;
};
S.isContextConsumer = function(t) {
  return R(t) === le;
};
S.isContextProvider = function(t) {
  return R(t) === ae;
};
S.isElement = function(t) {
  return typeof t == "object" && t !== null && t.$$typeof === ke;
};
S.isForwardRef = function(t) {
  return R(t) === ce;
};
S.isFragment = function(t) {
  return R(t) === oe;
};
S.isLazy = function(t) {
  return R(t) === he;
};
S.isMemo = function(t) {
  return R(t) === de;
};
S.isPortal = function(t) {
  return R(t) === Re;
};
S.isProfiler = function(t) {
  return R(t) === ie;
};
S.isStrictMode = function(t) {
  return R(t) === se;
};
S.isSuspense = function(t) {
  return R(t) === ue;
};
S.isSuspenseList = function(t) {
  return R(t) === fe;
};
S.isValidElementType = function(t) {
  return typeof t == "string" || typeof t == "function" || t === oe || t === ie || t === se || t === ue || t === fe || t === Zr || typeof t == "object" && t !== null && (t.$$typeof === he || t.$$typeof === de || t.$$typeof === ae || t.$$typeof === le || t.$$typeof === ce || t.$$typeof === yt || t.getModuleId !== void 0);
};
S.typeOf = R;
Number(Lt.split(".")[0]);
function tt(t, e, n, o) {
  var r = j({}, e[t]);
  if (o != null && o.deprecatedTokens) {
    var s = o.deprecatedTokens;
    s.forEach(function(a) {
      var l = Y(a, 2), c = l[0], f = l[1];
      if (r != null && r[c] || r != null && r[f]) {
        var u;
        (u = r[f]) !== null && u !== void 0 || (r[f] = r == null ? void 0 : r[c]);
      }
    });
  }
  var i = j(j({}, n), r);
  return Object.keys(i).forEach(function(a) {
    i[a] === e[a] && delete i[a];
  }), i;
}
var vt = typeof CSSINJS_STATISTIC < "u", je = !0;
function $e() {
  for (var t = arguments.length, e = new Array(t), n = 0; n < t; n++)
    e[n] = arguments[n];
  if (!vt)
    return Object.assign.apply(Object, [{}].concat(e));
  je = !1;
  var o = {};
  return e.forEach(function(r) {
    if (H(r) === "object") {
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
  }), je = !0, o;
}
var rt = {};
function Jr() {
}
var Yr = function(e) {
  var n, o = e, r = Jr;
  return vt && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(e, {
    get: function(i, a) {
      if (je) {
        var l;
        (l = n) === null || l === void 0 || l.add(a);
      }
      return i[a];
    }
  }), r = function(i, a) {
    var l;
    rt[i] = {
      global: Array.from(n),
      component: j(j({}, (l = rt[i]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function nt(t, e, n) {
  if (typeof n == "function") {
    var o;
    return n($e(e, (o = e[t]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function en(t) {
  return t === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(s) {
        return we(s);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(s) {
        return we(s);
      }).join(","), ")");
    }
  };
}
var tn = 1e3 * 60 * 10, rn = /* @__PURE__ */ function() {
  function t() {
    re(this, t), O(this, "map", /* @__PURE__ */ new Map()), O(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), O(this, "nextID", 0), O(this, "lastAccessBeat", /* @__PURE__ */ new Map()), O(this, "accessBeat", 0);
  }
  return ne(t, [{
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
        return s && H(s) === "object" ? "obj_".concat(o.getObjectID(s)) : "".concat(H(s), "_").concat(s);
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
          o - r > tn && (n.map.delete(s), n.lastAccessBeat.delete(s));
        }), this.accessBeat = 0;
      }
    }
  }]), t;
}(), ot = new rn();
function nn(t, e) {
  return _.useMemo(function() {
    var n = ot.get(e);
    if (n)
      return n;
    var o = t();
    return ot.set(e, o), o;
  }, e);
}
var on = function() {
  return {};
};
function sn(t) {
  var e = t.useCSP, n = e === void 0 ? on : e, o = t.useToken, r = t.usePrefix, s = t.getResetStyles, i = t.getCommonStyle, a = t.getCompUnitless;
  function l(d, b, x, g) {
    var h = Array.isArray(d) ? d[0] : d;
    function y(C) {
      return "".concat(String(h)).concat(C.slice(0, 1).toUpperCase()).concat(C.slice(1));
    }
    var v = (g == null ? void 0 : g.unitless) || {}, P = typeof a == "function" ? a(d) : {}, m = j(j({}, P), {}, O({}, y("zIndexPopup"), !0));
    Object.keys(v).forEach(function(C) {
      m[y(C)] = v[C];
    });
    var w = j(j({}, g), {}, {
      unitless: m,
      prefixToken: y
    }), p = f(d, b, x, w), T = c(h, x, w);
    return function(C) {
      var I = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : C, $ = p(C, I), z = Y($, 2), E = z[1], D = T(I), k = Y(D, 2), A = k[0], U = k[1];
      return [A, E, U];
    };
  }
  function c(d, b, x) {
    var g = x.unitless, h = x.injectStyle, y = h === void 0 ? !0 : h, v = x.prefixToken, P = x.ignore, m = function(T) {
      var C = T.rootCls, I = T.cssVar, $ = I === void 0 ? {} : I, z = o(), E = z.realToken;
      return Vt({
        path: [d],
        prefix: $.prefix,
        key: $.key,
        unitless: g,
        ignore: P,
        token: E,
        scope: C
      }, function() {
        var D = nt(d, E, b), k = tt(d, E, D, {
          deprecatedTokens: x == null ? void 0 : x.deprecatedTokens
        });
        return Object.keys(D).forEach(function(A) {
          k[v(A)] = k[A], delete k[A];
        }), k;
      }), null;
    }, w = function(T) {
      var C = o(), I = C.cssVar;
      return [function($) {
        return y && I ? /* @__PURE__ */ _.createElement(_.Fragment, null, /* @__PURE__ */ _.createElement(m, {
          rootCls: T,
          cssVar: I,
          component: d
        }), $) : $;
      }, I == null ? void 0 : I.key];
    };
    return w;
  }
  function f(d, b, x) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = Array.isArray(d) ? d : [d, d], y = Y(h, 1), v = y[0], P = h.join("-"), m = t.layer || {
      name: "antd"
    };
    return function(w) {
      var p = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : w, T = o(), C = T.theme, I = T.realToken, $ = T.hashId, z = T.token, E = T.cssVar, D = r(), k = D.rootPrefixCls, A = D.iconPrefixCls, U = n(), ge = E ? "css" : "js", Ct = nn(function() {
        var X = /* @__PURE__ */ new Set();
        return E && Object.keys(g.unitless || {}).forEach(function(q) {
          X.add(pe(q, E.prefix)), X.add(pe(q, et(v, E.prefix)));
        }), Kr(ge, X);
      }, [ge, v, E == null ? void 0 : E.prefix]), Le = en(ge), wt = Le.max, Tt = Le.min, He = {
        theme: C,
        token: z,
        hashId: $,
        nonce: function() {
          return U.nonce;
        },
        clientOnly: g.clientOnly,
        layer: m,
        // antd is always at top of styles
        order: g.order || -999
      };
      typeof s == "function" && Xe(j(j({}, He), {}, {
        clientOnly: !1,
        path: ["Shared", k]
      }), function() {
        return s(z, {
          prefix: {
            rootPrefixCls: k,
            iconPrefixCls: A
          },
          csp: U
        });
      });
      var Ot = Xe(j(j({}, He), {}, {
        path: [P, w, A]
      }), function() {
        if (g.injectStyle === !1)
          return [];
        var X = Yr(z), q = X.token, Pt = X.flush, F = nt(v, I, x), Mt = ".".concat(w), Ae = tt(v, I, F, {
          deprecatedTokens: g.deprecatedTokens
        });
        E && F && H(F) === "object" && Object.keys(F).forEach(function(ze) {
          F[ze] = "var(".concat(pe(ze, et(v, E.prefix)), ")");
        });
        var Be = $e(q, {
          componentCls: Mt,
          prefixCls: w,
          iconCls: ".".concat(A),
          antCls: ".".concat(k),
          calc: Ct,
          // @ts-ignore
          max: wt,
          // @ts-ignore
          min: Tt
        }, E ? F : Ae), It = b(Be, {
          hashId: $,
          prefixCls: w,
          rootPrefixCls: k,
          iconPrefixCls: A
        });
        Pt(v, Ae);
        var Et = typeof i == "function" ? i(Be, w, p, g.resetFont) : null;
        return [g.resetStyle === !1 ? null : Et, It];
      });
      return [Ot, $];
    };
  }
  function u(d, b, x) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = f(d, b, x, j({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, g)), y = function(P) {
      var m = P.prefixCls, w = P.rootCls, p = w === void 0 ? m : w;
      return h(m, p), null;
    };
    return y;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: u,
    genComponentStyleHook: f
  };
}
const an = {
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
}, ln = Object.assign(Object.assign({}, an), {
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
function ve(t, e) {
  const n = t.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = e(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const st = (t, e, n) => n === 0 ? t : t / 100;
function W(t, e) {
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
      let r = function(s) {
        return o.startsWith(s);
      };
      const o = e.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (e instanceof B)
      this.r = e.r, this.g = e.g, this.b = e.b, this.a = e.a, this._h = e._h, this._s = e._s, this._l = e._l, this._v = e._v;
    else if (n("rgb"))
      this.r = W(e.r), this.g = W(e.g), this.b = W(e.b), this.a = typeof e.a == "number" ? W(e.a, 1) : 1;
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
      e === 0 ? this._h = 0 : this._h = M(60 * (this.r === this.getMax() ? (this.g - this.b) / e + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / e + 2 : (this.r - this.g) / e + 4));
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
      r: M(s("r")),
      g: M(s("g")),
      b: M(s("b")),
      a: M(s("a") * 100) / 100
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
    const n = this._c(e), o = this.a + n.a * (1 - this.a), r = (s) => M((this[s] * this.a + n[s] * n.a * (1 - this.a)) / o);
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
      const s = M(this.a * 255).toString(16);
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
    const e = this.getHue(), n = M(this.getSaturation() * 100), o = M(this.getLightness() * 100);
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
    return r[e] = W(n, o), r;
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
      const d = M(o * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let s = 0, i = 0, a = 0;
    const l = e / 60, c = (1 - Math.abs(2 * o - 1)) * n, f = c * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (s = c, i = f) : l >= 1 && l < 2 ? (s = f, i = c) : l >= 2 && l < 3 ? (i = c, a = f) : l >= 3 && l < 4 ? (i = f, a = c) : l >= 4 && l < 5 ? (s = f, a = c) : l >= 5 && l < 6 && (s = c, a = f);
    const u = o - c / 2;
    this.r = M((s + u) * 255), this.g = M((i + u) * 255), this.b = M((a + u) * 255);
  }
  fromHsv({
    h: e,
    s: n,
    v: o,
    a: r
  }) {
    this._h = e % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const s = M(o * 255);
    if (this.r = s, this.g = s, this.b = s, n <= 0)
      return;
    const i = e / 60, a = Math.floor(i), l = i - a, c = M(o * (1 - n) * 255), f = M(o * (1 - n * l) * 255), u = M(o * (1 - n * (1 - l)) * 255);
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
    const n = ve(e, st);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(e) {
    const n = ve(e, st);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(e) {
    const n = ve(e, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? M(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function xe(t) {
  return t >= 0 && t <= 255;
}
function K(t, e) {
  const {
    r: n,
    g: o,
    b: r,
    a: s
  } = new B(t).toRgb();
  if (s < 1)
    return t;
  const {
    r: i,
    g: a,
    b: l
  } = new B(e).toRgb();
  for (let c = 0.01; c <= 1; c += 0.01) {
    const f = Math.round((n - i * (1 - c)) / c), u = Math.round((o - a * (1 - c)) / c), d = Math.round((r - l * (1 - c)) / c);
    if (xe(f) && xe(u) && xe(d))
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
var cn = function(t, e) {
  var n = {};
  for (var o in t) Object.prototype.hasOwnProperty.call(t, o) && e.indexOf(o) < 0 && (n[o] = t[o]);
  if (t != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(t); r < o.length; r++)
    e.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(t, o[r]) && (n[o[r]] = t[o[r]]);
  return n;
};
function un(t) {
  const {
    override: e
  } = t, n = cn(t, ["override"]), o = Object.assign({}, e);
  Object.keys(ln).forEach((d) => {
    delete o[d];
  });
  const r = Object.assign(Object.assign({}, n), o), s = 480, i = 576, a = 768, l = 992, c = 1200, f = 1600;
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
    colorSplit: K(r.colorBorderSecondary, r.colorBgContainer),
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
    colorErrorOutline: K(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: K(r.colorWarningBg, r.colorBgContainer),
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
    controlOutline: K(r.colorPrimaryBg, r.colorBgContainer),
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
const fn = {
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
}, dn = {
  motionBase: !0,
  motionUnit: !0
}, hn = Wt(Ce.defaultAlgorithm), gn = {
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
}, xt = (t, e, n) => {
  const o = n.getDerivativeToken(t), {
    override: r,
    ...s
  } = e;
  let i = {
    ...o,
    override: r
  };
  return i = un(i), s && Object.entries(s).forEach(([a, l]) => {
    const {
      theme: c,
      ...f
    } = l;
    let u = f;
    c && (u = xt({
      ...i,
      ...f
    }, {
      override: f
    }, c)), i[a] = u;
  }), i;
};
function pn() {
  const {
    token: t,
    hashed: e,
    theme: n = hn,
    override: o,
    cssVar: r
  } = _.useContext(Ce._internalContext), [s, i, a] = Gt(n, [Ce.defaultSeed, t], {
    salt: `${Lr}-${e || ""}`,
    override: o,
    getComputedToken: xt,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: fn,
      ignore: dn,
      preserve: gn
    }
  });
  return [n, a, e ? i : "", s, r];
}
const {
  genStyleHooks: mn
} = sn({
  usePrefix: () => {
    const {
      getPrefixCls: t,
      iconPrefixCls: e
    } = Ie();
    return {
      iconPrefixCls: e,
      rootPrefixCls: t()
    };
  },
  useToken: () => {
    const [t, e, n, o, r] = pn();
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
    } = Ie();
    return t ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), bn = (t) => {
  const {
    componentCls: e
  } = t;
  return {
    [e]: {
      // ======================== Prompt ========================
      "&, & *": {
        boxSizing: "border-box"
      },
      maxWidth: "100%",
      [`&${e}-rtl`]: {
        direction: "rtl"
      },
      [`& ${e}-title`]: {
        marginBlockStart: 0,
        fontWeight: "normal",
        color: t.colorTextTertiary
      },
      [`& ${e}-list`]: {
        display: "flex",
        gap: t.paddingSM,
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
      [`${e}-item`]: {
        flex: "none",
        display: "flex",
        gap: t.paddingXS,
        height: "auto",
        paddingBlock: t.paddingSM,
        paddingInline: t.padding,
        alignItems: "flex-start",
        justifyContent: "flex-start",
        background: t.colorBgContainer,
        borderRadius: t.borderRadiusLG,
        transition: ["border", "background"].map((n) => `${n} ${t.motionDurationSlow}`).join(","),
        border: `${we(t.lineWidth)} ${t.lineType} ${t.colorBorderSecondary}`,
        [`&:not(${e}-item-has-nest)`]: {
          "&:hover": {
            cursor: "pointer",
            background: t.colorFillTertiary
          },
          "&:active": {
            background: t.colorFill
          }
        },
        [`${e}-content`]: {
          flex: "auto",
          minWidth: 0,
          display: "flex",
          gap: t.paddingXXS,
          flexDirection: "column",
          alignItems: "flex-start"
        },
        [`${e}-icon, ${e}-label, ${e}-desc`]: {
          margin: 0,
          padding: 0,
          fontSize: t.fontSize,
          lineHeight: t.lineHeight,
          textAlign: "start",
          whiteSpace: "normal"
        },
        [`${e}-label`]: {
          color: t.colorTextHeading,
          fontWeight: 500
        },
        [`${e}-label + ${e}-desc`]: {
          color: t.colorTextTertiary
        },
        // Disabled
        [`&${e}-item-disabled`]: {
          pointerEvents: "none",
          background: t.colorBgContainerDisabled,
          [`${e}-label, ${e}-desc`]: {
            color: t.colorTextTertiary
          }
        }
      }
    }
  };
}, yn = (t) => {
  const {
    componentCls: e
  } = t;
  return {
    [e]: {
      // ========================= Parent =========================
      [`${e}-item-has-nest`]: {
        [`> ${e}-content`]: {
          // gap: token.paddingSM,
          [`> ${e}-label`]: {
            fontSize: t.fontSizeLG,
            lineHeight: t.lineHeightLG
          }
        }
      },
      // ========================= Nested =========================
      [`&${e}-nested`]: {
        marginTop: t.paddingXS,
        // ======================== Prompt ========================
        alignSelf: "stretch",
        [`${e}-list`]: {
          alignItems: "stretch"
        },
        // ========================= Item =========================
        [`${e}-item`]: {
          border: 0,
          background: t.colorFillQuaternary
        }
      }
    }
  };
}, vn = () => ({}), xn = mn("Prompts", (t) => {
  const e = $e(t, {});
  return [bn(e), yn(e)];
}, vn), St = (t) => {
  const {
    prefixCls: e,
    title: n,
    className: o,
    items: r,
    onItemClick: s,
    vertical: i,
    wrap: a,
    rootClassName: l,
    styles: c = {},
    classNames: f = {},
    style: u,
    ...d
  } = t, {
    getPrefixCls: b,
    direction: x
  } = Ie(), g = b("prompts", e), h = zr("prompts"), [y, v, P] = xn(g), m = V(g, h.className, o, l, v, P, {
    [`${g}-rtl`]: x === "rtl"
  }), w = V(`${g}-list`, h.classNames.list, f.list, {
    [`${g}-list-wrap`]: a
  }, {
    [`${g}-list-vertical`]: i
  });
  return y(/* @__PURE__ */ _.createElement("div", Me({}, d, {
    className: m,
    style: {
      ...u,
      ...h.style
    }
  }), n && /* @__PURE__ */ _.createElement(Nt.Title, {
    level: 5,
    className: V(`${g}-title`, h.classNames.title, f.title),
    style: {
      ...h.styles.title,
      ...c.title
    }
  }, n), /* @__PURE__ */ _.createElement("div", {
    className: w,
    style: {
      ...h.styles.list,
      ...c.list
    }
  }, r == null ? void 0 : r.map((p, T) => {
    const C = p.children && p.children.length > 0;
    return /* @__PURE__ */ _.createElement("div", {
      key: p.key || `key_${T}`,
      style: {
        ...h.styles.item,
        ...c.item
      },
      className: V(`${g}-item`, h.classNames.item, f.item, {
        [`${g}-item-disabled`]: p.disabled,
        [`${g}-item-has-nest`]: C
      }),
      onClick: () => {
        !C && s && s({
          data: p
        });
      }
    }, p.icon && /* @__PURE__ */ _.createElement("div", {
      className: `${g}-icon`
    }, p.icon), /* @__PURE__ */ _.createElement("div", {
      className: V(`${g}-content`, h.classNames.itemContent, f.itemContent),
      style: {
        ...h.styles.itemContent,
        ...c.itemContent
      }
    }, p.label && /* @__PURE__ */ _.createElement("h6", {
      className: `${g}-label`
    }, p.label), p.description && /* @__PURE__ */ _.createElement("p", {
      className: `${g}-desc`
    }, p.description), C && /* @__PURE__ */ _.createElement(St, {
      className: `${g}-nested`,
      items: p.children,
      vertical: !0,
      onItemClick: s,
      classNames: {
        list: f.subList,
        item: f.subItem
      },
      styles: {
        list: c.subList,
        item: c.subItem
      }
    })));
  }))));
}, Sn = ({
  children: t,
  ...e
}) => /* @__PURE__ */ L.jsx(L.Fragment, {
  children: t(e)
});
function _n(t) {
  return _.createElement(Sn, {
    children: t
  });
}
function _t(t, e, n) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((r, s) => {
      var c, f;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const i = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((c = r.props) == null ? void 0 : c.key) ?? (n ? `${n}-${s}` : `${s}`)
      }) : {
        ...r.props,
        key: ((f = r.props) == null ? void 0 : f.key) ?? (n ? `${n}-${s}` : `${s}`)
      };
      let a = i;
      Object.keys(r.slots).forEach((u) => {
        if (!r.slots[u] || !(r.slots[u] instanceof Element) && !r.slots[u].el)
          return;
        const d = u.split(".");
        d.forEach((v, P) => {
          a[v] || (a[v] = {}), P !== d.length - 1 && (a = i[v]);
        });
        const b = r.slots[u];
        let x, g, h = (e == null ? void 0 : e.clone) ?? !1, y = e == null ? void 0 : e.forceClone;
        b instanceof Element ? x = b : (x = b.el, g = b.callback, h = b.clone ?? h, y = b.forceClone ?? y), y = y ?? !!g, a[d[d.length - 1]] = x ? g ? (...v) => (g(d[d.length - 1], v), /* @__PURE__ */ L.jsx(De, {
          ...r.ctx,
          params: v,
          forceClone: y,
          children: /* @__PURE__ */ L.jsx(Pe, {
            slot: x,
            clone: h
          })
        })) : _n((v) => /* @__PURE__ */ L.jsx(De, {
          ...r.ctx,
          forceClone: y,
          children: /* @__PURE__ */ L.jsx(Pe, {
            ...v,
            slot: x,
            clone: h
          })
        })) : a[d[d.length - 1]], a = i;
      });
      const l = (e == null ? void 0 : e.children) || "children";
      return r[l] ? i[l] = _t(r[l], e, `${s}`) : e != null && e.children && (i[l] = void 0, Reflect.deleteProperty(i, l)), i;
    });
}
const {
  useItems: Cn,
  withItemsContextProvider: wn,
  ItemHandler: Pn
} = Xt("antdx-prompts-items"), Mn = Er(wn(["default", "items"], ({
  slots: t,
  children: e,
  items: n,
  ...o
}) => {
  const {
    items: r
  } = Cn(), s = r.items.length > 0 ? r.items : r.default;
  return /* @__PURE__ */ L.jsxs(L.Fragment, {
    children: [/* @__PURE__ */ L.jsx("div", {
      style: {
        display: "none"
      },
      children: e
    }), /* @__PURE__ */ L.jsx(St, {
      ...o,
      title: t.title ? /* @__PURE__ */ L.jsx(Pe, {
        slot: t.title
      }) : o.title,
      items: Ht(() => n || _t(s, {
        clone: !0
      }), [n, s])
    })]
  });
}));
export {
  Mn as Prompts,
  Mn as default
};
