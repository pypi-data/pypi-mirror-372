import { i as fr, a as It, r as pr, Z as Xe, g as mr, t as gr, s as Ae, c as re, b as hr } from "./Index-DVghpKbl.js";
const A = window.ms_globals.React, l = window.ms_globals.React, et = window.ms_globals.React.useMemo, qe = window.ms_globals.React.useState, xe = window.ms_globals.React.useEffect, lr = window.ms_globals.React.forwardRef, be = window.ms_globals.React.useRef, cr = window.ms_globals.React.version, ur = window.ms_globals.React.isValidElement, dr = window.ms_globals.React.useLayoutEffect, Vt = window.ms_globals.ReactDOM, Ze = window.ms_globals.ReactDOM.createPortal, vr = window.ms_globals.internalContext.useContextPropsContext, yr = window.ms_globals.internalContext.ContextPropsProvider, br = window.ms_globals.antd.ConfigProvider, Qe = window.ms_globals.antd.theme, In = window.ms_globals.antd.Upload, Sr = window.ms_globals.antd.Progress, wr = window.ms_globals.antd.Image, gt = window.ms_globals.antd.Button, xr = window.ms_globals.antd.Flex, ht = window.ms_globals.antd.Typography, Tn = window.ms_globals.antdIcons.FileTextFilled, Er = window.ms_globals.antdIcons.CloseCircleFilled, Cr = window.ms_globals.antdIcons.FileExcelFilled, _r = window.ms_globals.antdIcons.FileImageFilled, Rr = window.ms_globals.antdIcons.FileMarkdownFilled, Lr = window.ms_globals.antdIcons.FilePdfFilled, Ir = window.ms_globals.antdIcons.FilePptFilled, Tr = window.ms_globals.antdIcons.FileWordFilled, Pr = window.ms_globals.antdIcons.FileZipFilled, Mr = window.ms_globals.antdIcons.PlusOutlined, Or = window.ms_globals.antdIcons.LeftOutlined, Fr = window.ms_globals.antdIcons.RightOutlined, Xt = window.ms_globals.antdCssinjs.unit, vt = window.ms_globals.antdCssinjs.token2CSSVar, Wt = window.ms_globals.antdCssinjs.useStyleRegister, kr = window.ms_globals.antdCssinjs.useCSSVarRegister, Ar = window.ms_globals.antdCssinjs.createTheme, $r = window.ms_globals.antdCssinjs.useCacheToken;
var jr = /\s/;
function Dr(e) {
  for (var t = e.length; t-- && jr.test(e.charAt(t)); )
    ;
  return t;
}
var Nr = /^\s+/;
function Hr(e) {
  return e && e.slice(0, Dr(e) + 1).replace(Nr, "");
}
var Gt = NaN, zr = /^[-+]0x[0-9a-f]+$/i, Ur = /^0b[01]+$/i, Br = /^0o[0-7]+$/i, Vr = parseInt;
function Kt(e) {
  if (typeof e == "number")
    return e;
  if (fr(e))
    return Gt;
  if (It(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = It(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Hr(e);
  var n = Ur.test(e);
  return n || Br.test(e) ? Vr(e.slice(2), n ? 2 : 8) : zr.test(e) ? Gt : +e;
}
function Xr() {
}
var yt = function() {
  return pr.Date.now();
}, Wr = "Expected a function", Gr = Math.max, Kr = Math.min;
function qr(e, t, n) {
  var o, r, i, s, a, c, u = 0, p = !1, d = !1, f = !0;
  if (typeof e != "function")
    throw new TypeError(Wr);
  t = Kt(t) || 0, It(n) && (p = !!n.leading, d = "maxWait" in n, i = d ? Gr(Kt(n.maxWait) || 0, t) : i, f = "trailing" in n ? !!n.trailing : f);
  function m(h) {
    var L = o, C = r;
    return o = r = void 0, u = h, s = e.apply(C, L), s;
  }
  function y(h) {
    return u = h, a = setTimeout(x, t), p ? m(h) : s;
  }
  function b(h) {
    var L = h - c, C = h - u, M = t - L;
    return d ? Kr(M, i - C) : M;
  }
  function g(h) {
    var L = h - c, C = h - u;
    return c === void 0 || L >= t || L < 0 || d && C >= i;
  }
  function x() {
    var h = yt();
    if (g(h))
      return w(h);
    a = setTimeout(x, b(h));
  }
  function w(h) {
    return a = void 0, f && o ? m(h) : (o = r = void 0, s);
  }
  function S() {
    a !== void 0 && clearTimeout(a), u = 0, o = c = r = a = void 0;
  }
  function v() {
    return a === void 0 ? s : w(yt());
  }
  function R() {
    var h = yt(), L = g(h);
    if (o = arguments, r = this, c = h, L) {
      if (a === void 0)
        return y(c);
      if (d)
        return clearTimeout(a), a = setTimeout(x, t), m(c);
    }
    return a === void 0 && (a = setTimeout(x, t)), s;
  }
  return R.cancel = S, R.flush = v, R;
}
var Pn = {
  exports: {}
}, tt = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Zr = l, Qr = Symbol.for("react.element"), Yr = Symbol.for("react.fragment"), Jr = Object.prototype.hasOwnProperty, eo = Zr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, to = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Mn(e, t, n) {
  var o, r = {}, i = null, s = null;
  n !== void 0 && (i = "" + n), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (o in t) Jr.call(t, o) && !to.hasOwnProperty(o) && (r[o] = t[o]);
  if (e && e.defaultProps) for (o in t = e.defaultProps, t) r[o] === void 0 && (r[o] = t[o]);
  return {
    $$typeof: Qr,
    type: e,
    key: i,
    ref: s,
    props: r,
    _owner: eo.current
  };
}
tt.Fragment = Yr;
tt.jsx = Mn;
tt.jsxs = Mn;
Pn.exports = tt;
var ee = Pn.exports;
const {
  SvelteComponent: no,
  assign: qt,
  binding_callbacks: Zt,
  check_outros: ro,
  children: On,
  claim_element: Fn,
  claim_space: oo,
  component_subscribe: Qt,
  compute_slots: io,
  create_slot: so,
  detach: Re,
  element: kn,
  empty: Yt,
  exclude_internal_props: Jt,
  get_all_dirty_from_scope: ao,
  get_slot_changes: lo,
  group_outros: co,
  init: uo,
  insert_hydration: We,
  safe_not_equal: fo,
  set_custom_element_data: An,
  space: po,
  transition_in: Ge,
  transition_out: Tt,
  update_slot_base: mo
} = window.__gradio__svelte__internal, {
  beforeUpdate: go,
  getContext: ho,
  onDestroy: vo,
  setContext: yo
} = window.__gradio__svelte__internal;
function en(e) {
  let t, n;
  const o = (
    /*#slots*/
    e[7].default
  ), r = so(
    o,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = kn("svelte-slot"), r && r.c(), this.h();
    },
    l(i) {
      t = Fn(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = On(t);
      r && r.l(s), s.forEach(Re), this.h();
    },
    h() {
      An(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      We(i, t, s), r && r.m(t, null), e[9](t), n = !0;
    },
    p(i, s) {
      r && r.p && (!n || s & /*$$scope*/
      64) && mo(
        r,
        o,
        i,
        /*$$scope*/
        i[6],
        n ? lo(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : ao(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      n || (Ge(r, i), n = !0);
    },
    o(i) {
      Tt(r, i), n = !1;
    },
    d(i) {
      i && Re(t), r && r.d(i), e[9](null);
    }
  };
}
function bo(e) {
  let t, n, o, r, i = (
    /*$$slots*/
    e[4].default && en(e)
  );
  return {
    c() {
      t = kn("react-portal-target"), n = po(), i && i.c(), o = Yt(), this.h();
    },
    l(s) {
      t = Fn(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), On(t).forEach(Re), n = oo(s), i && i.l(s), o = Yt(), this.h();
    },
    h() {
      An(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      We(s, t, a), e[8](t), We(s, n, a), i && i.m(s, a), We(s, o, a), r = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && Ge(i, 1)) : (i = en(s), i.c(), Ge(i, 1), i.m(o.parentNode, o)) : i && (co(), Tt(i, 1, 1, () => {
        i = null;
      }), ro());
    },
    i(s) {
      r || (Ge(i), r = !0);
    },
    o(s) {
      Tt(i), r = !1;
    },
    d(s) {
      s && (Re(t), Re(n), Re(o)), e[8](null), i && i.d(s);
    }
  };
}
function tn(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function So(e, t, n) {
  let o, r, {
    $$slots: i = {},
    $$scope: s
  } = t;
  const a = io(i);
  let {
    svelteInit: c
  } = t;
  const u = Xe(tn(t)), p = Xe();
  Qt(e, p, (v) => n(0, o = v));
  const d = Xe();
  Qt(e, d, (v) => n(1, r = v));
  const f = [], m = ho("$$ms-gr-react-wrapper"), {
    slotKey: y,
    slotIndex: b,
    subSlotIndex: g
  } = mr() || {}, x = c({
    parent: m,
    props: u,
    target: p,
    slot: d,
    slotKey: y,
    slotIndex: b,
    subSlotIndex: g,
    onDestroy(v) {
      f.push(v);
    }
  });
  yo("$$ms-gr-react-wrapper", x), go(() => {
    u.set(tn(t));
  }), vo(() => {
    f.forEach((v) => v());
  });
  function w(v) {
    Zt[v ? "unshift" : "push"](() => {
      o = v, p.set(o);
    });
  }
  function S(v) {
    Zt[v ? "unshift" : "push"](() => {
      r = v, d.set(r);
    });
  }
  return e.$$set = (v) => {
    n(17, t = qt(qt({}, t), Jt(v))), "svelteInit" in v && n(5, c = v.svelteInit), "$$scope" in v && n(6, s = v.$$scope);
  }, t = Jt(t), [o, r, p, d, a, c, s, i, w, S];
}
class wo extends no {
  constructor(t) {
    super(), uo(this, t, So, bo, fo, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ms
} = window.__gradio__svelte__internal, nn = window.ms_globals.rerender, bt = window.ms_globals.tree;
function xo(e, t = {}) {
  function n(o) {
    const r = Xe(), i = new wo({
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
          }, c = s.parent ?? bt;
          return c.nodes = [...c.nodes, a], nn({
            createPortal: Ze,
            node: bt
          }), s.onDestroy(() => {
            c.nodes = c.nodes.filter((u) => u.svelteInstance !== r), nn({
              createPortal: Ze,
              node: bt
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
function Eo(e) {
  const [t, n] = qe(() => Ae(e));
  return xe(() => {
    let o = !0;
    return e.subscribe((i) => {
      o && (o = !1, i === t) || n(i);
    });
  }, [e]), t;
}
function Co(e) {
  const t = et(() => gr(e, (n) => n), [e]);
  return Eo(t);
}
const _o = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Ro(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const o = e[n];
    return t[n] = Lo(n, o), t;
  }, {}) : {};
}
function Lo(e, t) {
  return typeof t == "number" && !_o.includes(e) ? t + "px" : t;
}
function Pt(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const r = l.Children.toArray(e._reactElement.props.children).map((i) => {
      if (l.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = Pt(i.props.el);
        return l.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...l.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return r.originalChildren = e._reactElement.props.children, t.push(Ze(l.cloneElement(e._reactElement, {
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
      useCapture: c
    }) => {
      n.addEventListener(a, s, c);
    });
  });
  const o = Array.from(e.childNodes);
  for (let r = 0; r < o.length; r++) {
    const i = o[r];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = Pt(i);
      t.push(...a), n.appendChild(s);
    } else i.nodeType === 3 && n.appendChild(i.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function Io(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const $e = lr(({
  slot: e,
  clone: t,
  className: n,
  style: o,
  observeAttributes: r
}, i) => {
  const s = be(), [a, c] = qe([]), {
    forceClone: u
  } = vr(), p = u ? !0 : t;
  return xe(() => {
    var b;
    if (!s.current || !e)
      return;
    let d = e;
    function f() {
      let g = d;
      if (d.tagName.toLowerCase() === "svelte-slot" && d.children.length === 1 && d.children[0] && (g = d.children[0], g.tagName.toLowerCase() === "react-portal-target" && g.children[0] && (g = g.children[0])), Io(i, g), n && g.classList.add(...n.split(" ")), o) {
        const x = Ro(o);
        Object.keys(x).forEach((w) => {
          g.style[w] = x[w];
        });
      }
    }
    let m = null, y = null;
    if (p && window.MutationObserver) {
      let g = function() {
        var v, R, h;
        (v = s.current) != null && v.contains(d) && ((R = s.current) == null || R.removeChild(d));
        const {
          portals: w,
          clonedElement: S
        } = Pt(e);
        d = S, c(w), d.style.display = "contents", y && clearTimeout(y), y = setTimeout(() => {
          f();
        }, 50), (h = s.current) == null || h.appendChild(d);
      };
      g();
      const x = qr(() => {
        g(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      m = new window.MutationObserver(x), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      d.style.display = "contents", f(), (b = s.current) == null || b.appendChild(d);
    return () => {
      var g, x;
      d.style.display = "", (g = s.current) != null && g.contains(d) && ((x = s.current) == null || x.removeChild(d)), m == null || m.disconnect();
    };
  }, [e, p, n, o, i, r, u]), l.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), To = "1.6.0";
function Te() {
  return Te = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var n = arguments[t];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (e[o] = n[o]);
    }
    return e;
  }, Te.apply(null, arguments);
}
function q(e) {
  "@babel/helpers - typeof";
  return q = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, q(e);
}
function Po(e, t) {
  if (q(e) != "object" || !e) return e;
  var n = e[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(e, t);
    if (q(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function $n(e) {
  var t = Po(e, "string");
  return q(t) == "symbol" ? t : t + "";
}
function T(e, t, n) {
  return (t = $n(t)) in e ? Object.defineProperty(e, t, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = n, e;
}
function rn(e, t) {
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
    t % 2 ? rn(Object(n), !0).forEach(function(o) {
      T(e, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : rn(Object(n)).forEach(function(o) {
      Object.defineProperty(e, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return e;
}
const Mo = /* @__PURE__ */ l.createContext({}), Oo = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, Fo = (e) => {
  const t = l.useContext(Mo);
  return l.useMemo(() => ({
    ...Oo,
    ...t[e]
  }), [t[e]]);
};
function Ye() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = l.useContext(br.ConfigContext);
  return {
    theme: r,
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: o
  };
}
function ko(e) {
  if (Array.isArray(e)) return e;
}
function Ao(e, t) {
  var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (n != null) {
    var o, r, i, s, a = [], c = !0, u = !1;
    try {
      if (i = (n = n.call(e)).next, t === 0) {
        if (Object(n) !== n) return;
        c = !1;
      } else for (; !(c = (o = i.call(n)).done) && (a.push(o.value), a.length !== t); c = !0) ;
    } catch (p) {
      u = !0, r = p;
    } finally {
      try {
        if (!c && n.return != null && (s = n.return(), Object(s) !== s)) return;
      } finally {
        if (u) throw r;
      }
    }
    return a;
  }
}
function on(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var n = 0, o = Array(t); n < t; n++) o[n] = e[n];
  return o;
}
function $o(e, t) {
  if (e) {
    if (typeof e == "string") return on(e, t);
    var n = {}.toString.call(e).slice(8, -1);
    return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? on(e, t) : void 0;
  }
}
function jo() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function Y(e, t) {
  return ko(e) || Ao(e, t) || $o(e, t) || jo();
}
function Me(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function sn(e, t) {
  for (var n = 0; n < t.length; n++) {
    var o = t[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, $n(o.key), o);
  }
}
function Oe(e, t, n) {
  return t && sn(e.prototype, t), n && sn(e, n), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function Ee(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function Mt(e, t) {
  return Mt = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, Mt(e, t);
}
function nt(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && Mt(e, t);
}
function Je(e) {
  return Je = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, Je(e);
}
function jn() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (jn = function() {
    return !!e;
  })();
}
function Do(e, t) {
  if (t && (q(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return Ee(e);
}
function rt(e) {
  var t = jn();
  return function() {
    var n, o = Je(e);
    if (t) {
      var r = Je(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return Do(this, n);
  };
}
var Dn = /* @__PURE__ */ Oe(function e() {
  Me(this, e);
}), Nn = "CALC_UNIT", No = new RegExp(Nn, "g");
function St(e) {
  return typeof e == "number" ? "".concat(e).concat(Nn) : e;
}
var Ho = /* @__PURE__ */ function(e) {
  nt(n, e);
  var t = rt(n);
  function n(o, r) {
    var i;
    Me(this, n), i = t.call(this), T(Ee(i), "result", ""), T(Ee(i), "unitlessCssVar", void 0), T(Ee(i), "lowPriority", void 0);
    var s = q(o);
    return i.unitlessCssVar = r, o instanceof n ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = St(o) : s === "string" && (i.result = o), i;
  }
  return Oe(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(St(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(St(r))), this.lowPriority = !0, this;
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
      return typeof a == "boolean" ? c = a : Array.from(this.unitlessCssVar).some(function(u) {
        return i.result.includes(u);
      }) && (c = !1), this.result = this.result.replace(No, c ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(Dn), zo = /* @__PURE__ */ function(e) {
  nt(n, e);
  var t = rt(n);
  function n(o) {
    var r;
    return Me(this, n), r = t.call(this), T(Ee(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return Oe(n, [{
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
}(Dn), Uo = function(t, n) {
  var o = t === "css" ? Ho : zo;
  return function(r) {
    return new o(r, n);
  };
}, an = function(t, n) {
  return "".concat([n, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function Pe(e) {
  var t = A.useRef();
  t.current = e;
  var n = A.useCallback(function() {
    for (var o, r = arguments.length, i = new Array(r), s = 0; s < r; s++)
      i[s] = arguments[s];
    return (o = t.current) === null || o === void 0 ? void 0 : o.call.apply(o, [t].concat(i));
  }, []);
  return n;
}
function ot() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var ln = ot() ? A.useLayoutEffect : A.useEffect, Bo = function(t, n) {
  var o = A.useRef(!0);
  ln(function() {
    return t(o.current);
  }, n), ln(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, cn = function(t, n) {
  Bo(function(o) {
    if (!o)
      return t();
  }, n);
};
function je(e) {
  var t = A.useRef(!1), n = A.useState(e), o = Y(n, 2), r = o[0], i = o[1];
  A.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function s(a, c) {
    c && t.current || i(a);
  }
  return [r, s];
}
function wt(e) {
  return e !== void 0;
}
function Vo(e, t) {
  var n = t || {}, o = n.defaultValue, r = n.value, i = n.onChange, s = n.postState, a = je(function() {
    return wt(r) ? r : wt(o) ? typeof o == "function" ? o() : o : typeof e == "function" ? e() : e;
  }), c = Y(a, 2), u = c[0], p = c[1], d = r !== void 0 ? r : u, f = s ? s(d) : d, m = Pe(i), y = je([d]), b = Y(y, 2), g = b[0], x = b[1];
  cn(function() {
    var S = g[0];
    u !== S && m(u, S);
  }, [g]), cn(function() {
    wt(r) || p(r);
  }, [r]);
  var w = Pe(function(S, v) {
    p(S, v), x([d], v);
  });
  return [f, w];
}
var Hn = {
  exports: {}
}, $ = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Nt = Symbol.for("react.element"), Ht = Symbol.for("react.portal"), it = Symbol.for("react.fragment"), st = Symbol.for("react.strict_mode"), at = Symbol.for("react.profiler"), lt = Symbol.for("react.provider"), ct = Symbol.for("react.context"), Xo = Symbol.for("react.server_context"), ut = Symbol.for("react.forward_ref"), dt = Symbol.for("react.suspense"), ft = Symbol.for("react.suspense_list"), pt = Symbol.for("react.memo"), mt = Symbol.for("react.lazy"), Wo = Symbol.for("react.offscreen"), zn;
zn = Symbol.for("react.module.reference");
function ce(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case Nt:
        switch (e = e.type, e) {
          case it:
          case at:
          case st:
          case dt:
          case ft:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case Xo:
              case ct:
              case ut:
              case mt:
              case pt:
              case lt:
                return e;
              default:
                return t;
            }
        }
      case Ht:
        return t;
    }
  }
}
$.ContextConsumer = ct;
$.ContextProvider = lt;
$.Element = Nt;
$.ForwardRef = ut;
$.Fragment = it;
$.Lazy = mt;
$.Memo = pt;
$.Portal = Ht;
$.Profiler = at;
$.StrictMode = st;
$.Suspense = dt;
$.SuspenseList = ft;
$.isAsyncMode = function() {
  return !1;
};
$.isConcurrentMode = function() {
  return !1;
};
$.isContextConsumer = function(e) {
  return ce(e) === ct;
};
$.isContextProvider = function(e) {
  return ce(e) === lt;
};
$.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === Nt;
};
$.isForwardRef = function(e) {
  return ce(e) === ut;
};
$.isFragment = function(e) {
  return ce(e) === it;
};
$.isLazy = function(e) {
  return ce(e) === mt;
};
$.isMemo = function(e) {
  return ce(e) === pt;
};
$.isPortal = function(e) {
  return ce(e) === Ht;
};
$.isProfiler = function(e) {
  return ce(e) === at;
};
$.isStrictMode = function(e) {
  return ce(e) === st;
};
$.isSuspense = function(e) {
  return ce(e) === dt;
};
$.isSuspenseList = function(e) {
  return ce(e) === ft;
};
$.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === it || e === at || e === st || e === dt || e === ft || e === Wo || typeof e == "object" && e !== null && (e.$$typeof === mt || e.$$typeof === pt || e.$$typeof === lt || e.$$typeof === ct || e.$$typeof === ut || e.$$typeof === zn || e.getModuleId !== void 0);
};
$.typeOf = ce;
Hn.exports = $;
var xt = Hn.exports, Go = Symbol.for("react.element"), Ko = Symbol.for("react.transitional.element"), qo = Symbol.for("react.fragment");
function Zo(e) {
  return (
    // Base object type
    e && q(e) === "object" && // React Element type
    (e.$$typeof === Go || e.$$typeof === Ko) && // React Fragment type
    e.type === qo
  );
}
var Qo = Number(cr.split(".")[0]), Yo = function(t, n) {
  typeof t == "function" ? t(n) : q(t) === "object" && t && "current" in t && (t.current = n);
}, Jo = function(t) {
  var n, o;
  if (!t)
    return !1;
  if (Un(t) && Qo >= 19)
    return !0;
  var r = xt.isMemo(t) ? t.type.type : t.type;
  return !(typeof r == "function" && !((n = r.prototype) !== null && n !== void 0 && n.render) && r.$$typeof !== xt.ForwardRef || typeof t == "function" && !((o = t.prototype) !== null && o !== void 0 && o.render) && t.$$typeof !== xt.ForwardRef);
};
function Un(e) {
  return /* @__PURE__ */ ur(e) && !Zo(e);
}
var ei = function(t) {
  if (t && Un(t)) {
    var n = t;
    return n.props.propertyIsEnumerable("ref") ? n.props.ref : n.ref;
  }
  return null;
};
function un(e, t, n, o) {
  var r = I({}, t[e]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var c = Y(a, 2), u = c[0], p = c[1];
      if (r != null && r[u] || r != null && r[p]) {
        var d;
        (d = r[p]) !== null && d !== void 0 || (r[p] = r == null ? void 0 : r[u]);
      }
    });
  }
  var s = I(I({}, n), r);
  return Object.keys(s).forEach(function(a) {
    s[a] === t[a] && delete s[a];
  }), s;
}
var Bn = typeof CSSINJS_STATISTIC < "u", Ot = !0;
function zt() {
  for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++)
    t[n] = arguments[n];
  if (!Bn)
    return Object.assign.apply(Object, [{}].concat(t));
  Ot = !1;
  var o = {};
  return t.forEach(function(r) {
    if (q(r) === "object") {
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
  }), Ot = !0, o;
}
var dn = {};
function ti() {
}
var ni = function(t) {
  var n, o = t, r = ti;
  return Bn && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(t, {
    get: function(s, a) {
      if (Ot) {
        var c;
        (c = n) === null || c === void 0 || c.add(a);
      }
      return s[a];
    }
  }), r = function(s, a) {
    var c;
    dn[s] = {
      global: Array.from(n),
      component: I(I({}, (c = dn[s]) === null || c === void 0 ? void 0 : c.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function fn(e, t, n) {
  if (typeof n == "function") {
    var o;
    return n(zt(t, (o = t[e]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function ri(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(i) {
        return Xt(i);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(i) {
        return Xt(i);
      }).join(","), ")");
    }
  };
}
var oi = 1e3 * 60 * 10, ii = /* @__PURE__ */ function() {
  function e() {
    Me(this, e), T(this, "map", /* @__PURE__ */ new Map()), T(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), T(this, "nextID", 0), T(this, "lastAccessBeat", /* @__PURE__ */ new Map()), T(this, "accessBeat", 0);
  }
  return Oe(e, [{
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
        return i && q(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(q(i), "_").concat(i);
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
          o - r > oi && (n.map.delete(i), n.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), pn = new ii();
function si(e, t) {
  return l.useMemo(function() {
    var n = pn.get(t);
    if (n)
      return n;
    var o = e();
    return pn.set(t, o), o;
  }, t);
}
var ai = function() {
  return {};
};
function li(e) {
  var t = e.useCSP, n = t === void 0 ? ai : t, o = e.useToken, r = e.usePrefix, i = e.getResetStyles, s = e.getCommonStyle, a = e.getCompUnitless;
  function c(f, m, y, b) {
    var g = Array.isArray(f) ? f[0] : f;
    function x(C) {
      return "".concat(String(g)).concat(C.slice(0, 1).toUpperCase()).concat(C.slice(1));
    }
    var w = (b == null ? void 0 : b.unitless) || {}, S = typeof a == "function" ? a(f) : {}, v = I(I({}, S), {}, T({}, x("zIndexPopup"), !0));
    Object.keys(w).forEach(function(C) {
      v[x(C)] = w[C];
    });
    var R = I(I({}, b), {}, {
      unitless: v,
      prefixToken: x
    }), h = p(f, m, y, R), L = u(g, y, R);
    return function(C) {
      var M = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : C, E = h(C, M), P = Y(E, 2), _ = P[1], O = L(M), F = Y(O, 2), k = F[0], H = F[1];
      return [k, _, H];
    };
  }
  function u(f, m, y) {
    var b = y.unitless, g = y.injectStyle, x = g === void 0 ? !0 : g, w = y.prefixToken, S = y.ignore, v = function(L) {
      var C = L.rootCls, M = L.cssVar, E = M === void 0 ? {} : M, P = o(), _ = P.realToken;
      return kr({
        path: [f],
        prefix: E.prefix,
        key: E.key,
        unitless: b,
        ignore: S,
        token: _,
        scope: C
      }, function() {
        var O = fn(f, _, m), F = un(f, _, O, {
          deprecatedTokens: y == null ? void 0 : y.deprecatedTokens
        });
        return Object.keys(O).forEach(function(k) {
          F[w(k)] = F[k], delete F[k];
        }), F;
      }), null;
    }, R = function(L) {
      var C = o(), M = C.cssVar;
      return [function(E) {
        return x && M ? /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(v, {
          rootCls: L,
          cssVar: M,
          component: f
        }), E) : E;
      }, M == null ? void 0 : M.key];
    };
    return R;
  }
  function p(f, m, y) {
    var b = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = Array.isArray(f) ? f : [f, f], x = Y(g, 1), w = x[0], S = g.join("-"), v = e.layer || {
      name: "antd"
    };
    return function(R) {
      var h = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : R, L = o(), C = L.theme, M = L.realToken, E = L.hashId, P = L.token, _ = L.cssVar, O = r(), F = O.rootPrefixCls, k = O.iconPrefixCls, H = n(), J = _ ? "css" : "js", j = si(function() {
        var N = /* @__PURE__ */ new Set();
        return _ && Object.keys(b.unitless || {}).forEach(function(Z) {
          N.add(vt(Z, _.prefix)), N.add(vt(Z, an(w, _.prefix)));
        }), Uo(J, N);
      }, [J, w, _ == null ? void 0 : _.prefix]), B = ri(J), de = B.max, X = B.min, oe = {
        theme: C,
        token: P,
        hashId: E,
        nonce: function() {
          return H.nonce;
        },
        clientOnly: b.clientOnly,
        layer: v,
        // antd is always at top of styles
        order: b.order || -999
      };
      typeof i == "function" && Wt(I(I({}, oe), {}, {
        clientOnly: !1,
        path: ["Shared", F]
      }), function() {
        return i(P, {
          prefix: {
            rootPrefixCls: F,
            iconPrefixCls: k
          },
          csp: H
        });
      });
      var U = Wt(I(I({}, oe), {}, {
        path: [S, R, k]
      }), function() {
        if (b.injectStyle === !1)
          return [];
        var N = ni(P), Z = N.token, ie = N.flush, te = fn(w, M, y), Fe = ".".concat(R), ge = un(w, M, te, {
          deprecatedTokens: b.deprecatedTokens
        });
        _ && te && q(te) === "object" && Object.keys(te).forEach(function(Se) {
          te[Se] = "var(".concat(vt(Se, an(w, _.prefix)), ")");
        });
        var fe = zt(Z, {
          componentCls: Fe,
          prefixCls: R,
          iconCls: ".".concat(k),
          antCls: ".".concat(F),
          calc: j,
          // @ts-ignore
          max: de,
          // @ts-ignore
          min: X
        }, _ ? te : ge), he = m(fe, {
          hashId: E,
          prefixCls: R,
          rootPrefixCls: F,
          iconPrefixCls: k
        });
        ie(w, ge);
        var pe = typeof s == "function" ? s(fe, R, h, b.resetFont) : null;
        return [b.resetStyle === !1 ? null : pe, he];
      });
      return [U, E];
    };
  }
  function d(f, m, y) {
    var b = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = p(f, m, y, I({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, b)), x = function(S) {
      var v = S.prefixCls, R = S.rootCls, h = R === void 0 ? v : R;
      return g(v, h), null;
    };
    return x;
  }
  return {
    genStyleHooks: c,
    genSubStyleComponent: d,
    genComponentStyleHook: p
  };
}
const ci = {
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
}, ui = Object.assign(Object.assign({}, ci), {
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
}), W = Math.round;
function Et(e, t) {
  const n = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = t(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const mn = (e, t, n) => n === 0 ? e : e / 100;
function ke(e, t) {
  const n = t || 255;
  return e > n ? n : e < 0 ? 0 : e;
}
class me {
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
    } else if (t instanceof me)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (n("rgb"))
      this.r = ke(t.r), this.g = ke(t.g), this.b = ke(t.b), this.a = typeof t.a == "number" ? ke(t.a, 1) : 1;
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
      t === 0 ? this._h = 0 : this._h = W(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
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
      r: W(i("r")),
      g: W(i("g")),
      b: W(i("b")),
      a: W(i("a") * 100) / 100
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
    const n = this._c(t), o = this.a + n.a * (1 - this.a), r = (i) => W((this[i] * this.a + n[i] * n.a * (1 - this.a)) / o);
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
      const i = W(this.a * 255).toString(16);
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
    const t = this.getHue(), n = W(this.getSaturation() * 100), o = W(this.getLightness() * 100);
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
    return r[t] = ke(n, o), r;
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
      const f = W(o * 255);
      this.r = f, this.g = f, this.b = f;
    }
    let i = 0, s = 0, a = 0;
    const c = t / 60, u = (1 - Math.abs(2 * o - 1)) * n, p = u * (1 - Math.abs(c % 2 - 1));
    c >= 0 && c < 1 ? (i = u, s = p) : c >= 1 && c < 2 ? (i = p, s = u) : c >= 2 && c < 3 ? (s = u, a = p) : c >= 3 && c < 4 ? (s = p, a = u) : c >= 4 && c < 5 ? (i = p, a = u) : c >= 5 && c < 6 && (i = u, a = p);
    const d = o - u / 2;
    this.r = W((i + d) * 255), this.g = W((s + d) * 255), this.b = W((a + d) * 255);
  }
  fromHsv({
    h: t,
    s: n,
    v: o,
    a: r
  }) {
    this._h = t % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const i = W(o * 255);
    if (this.r = i, this.g = i, this.b = i, n <= 0)
      return;
    const s = t / 60, a = Math.floor(s), c = s - a, u = W(o * (1 - n) * 255), p = W(o * (1 - n * c) * 255), d = W(o * (1 - n * (1 - c)) * 255);
    switch (a) {
      case 0:
        this.g = d, this.b = u;
        break;
      case 1:
        this.r = p, this.b = u;
        break;
      case 2:
        this.r = u, this.b = d;
        break;
      case 3:
        this.r = u, this.g = p;
        break;
      case 4:
        this.r = d, this.g = u;
        break;
      case 5:
      default:
        this.g = u, this.b = p;
        break;
    }
  }
  fromHsvString(t) {
    const n = Et(t, mn);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(t) {
    const n = Et(t, mn);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(t) {
    const n = Et(t, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? W(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function Ct(e) {
  return e >= 0 && e <= 255;
}
function Ne(e, t) {
  const {
    r: n,
    g: o,
    b: r,
    a: i
  } = new me(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: s,
    g: a,
    b: c
  } = new me(t).toRgb();
  for (let u = 0.01; u <= 1; u += 0.01) {
    const p = Math.round((n - s * (1 - u)) / u), d = Math.round((o - a * (1 - u)) / u), f = Math.round((r - c * (1 - u)) / u);
    if (Ct(p) && Ct(d) && Ct(f))
      return new me({
        r: p,
        g: d,
        b: f,
        a: Math.round(u * 100) / 100
      }).toRgbString();
  }
  return new me({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var di = function(e, t) {
  var n = {};
  for (var o in e) Object.prototype.hasOwnProperty.call(e, o) && t.indexOf(o) < 0 && (n[o] = e[o]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(e); r < o.length; r++)
    t.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(e, o[r]) && (n[o[r]] = e[o[r]]);
  return n;
};
function fi(e) {
  const {
    override: t
  } = e, n = di(e, ["override"]), o = Object.assign({}, t);
  Object.keys(ui).forEach((f) => {
    delete o[f];
  });
  const r = Object.assign(Object.assign({}, n), o), i = 480, s = 576, a = 768, c = 992, u = 1200, p = 1600;
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
    colorSplit: Ne(r.colorBorderSecondary, r.colorBgContainer),
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
    colorErrorOutline: Ne(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: Ne(r.colorWarningBg, r.colorBgContainer),
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
    controlOutline: Ne(r.colorPrimaryBg, r.colorBgContainer),
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
    screenLGMax: u - 1,
    screenXL: u,
    screenXLMin: u,
    screenXLMax: p - 1,
    screenXXL: p,
    screenXXLMin: p,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new me("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new me("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new me("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const pi = {
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
}, mi = {
  motionBase: !0,
  motionUnit: !0
}, gi = Ar(Qe.defaultAlgorithm), hi = {
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
}, Vn = (e, t, n) => {
  const o = n.getDerivativeToken(e), {
    override: r,
    ...i
  } = t;
  let s = {
    ...o,
    override: r
  };
  return s = fi(s), i && Object.entries(i).forEach(([a, c]) => {
    const {
      theme: u,
      ...p
    } = c;
    let d = p;
    u && (d = Vn({
      ...s,
      ...p
    }, {
      override: p
    }, u)), s[a] = d;
  }), s;
};
function vi() {
  const {
    token: e,
    hashed: t,
    theme: n = gi,
    override: o,
    cssVar: r
  } = l.useContext(Qe._internalContext), [i, s, a] = $r(n, [Qe.defaultSeed, e], {
    salt: `${To}-${t || ""}`,
    override: o,
    getComputedToken: Vn,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: pi,
      ignore: mi,
      preserve: hi
    }
  });
  return [n, a, t ? s : "", i, r];
}
const {
  genStyleHooks: yi
} = li({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = Ye();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, n, o, r] = vi();
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
    } = Ye();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), De = /* @__PURE__ */ l.createContext(null);
function gn(e) {
  const {
    getDropContainer: t,
    className: n,
    prefixCls: o,
    children: r
  } = e, {
    disabled: i
  } = l.useContext(De), [s, a] = l.useState(), [c, u] = l.useState(null);
  if (l.useEffect(() => {
    const f = t == null ? void 0 : t();
    s !== f && a(f);
  }, [t]), l.useEffect(() => {
    if (s) {
      const f = () => {
        u(!0);
      }, m = (g) => {
        g.preventDefault();
      }, y = (g) => {
        g.relatedTarget || u(!1);
      }, b = (g) => {
        u(!1), g.preventDefault();
      };
      return document.addEventListener("dragenter", f), document.addEventListener("dragover", m), document.addEventListener("dragleave", y), document.addEventListener("drop", b), () => {
        document.removeEventListener("dragenter", f), document.removeEventListener("dragover", m), document.removeEventListener("dragleave", y), document.removeEventListener("drop", b);
      };
    }
  }, [!!s]), !(t && s && !i))
    return null;
  const d = `${o}-drop-area`;
  return /* @__PURE__ */ Ze(/* @__PURE__ */ l.createElement("div", {
    className: re(d, n, {
      [`${d}-on-body`]: s.tagName === "BODY"
    }),
    style: {
      display: c ? "block" : "none"
    }
  }, r), s);
}
function hn(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function bi(e) {
  return e && q(e) === "object" && hn(e.nativeElement) ? e.nativeElement : hn(e) ? e : null;
}
function Si(e) {
  var t = bi(e);
  if (t)
    return t;
  if (e instanceof l.Component) {
    var n;
    return (n = Vt.findDOMNode) === null || n === void 0 ? void 0 : n.call(Vt, e);
  }
  return null;
}
function wi(e, t) {
  if (e == null) return {};
  var n = {};
  for (var o in e) if ({}.hasOwnProperty.call(e, o)) {
    if (t.indexOf(o) !== -1) continue;
    n[o] = e[o];
  }
  return n;
}
function vn(e, t) {
  if (e == null) return {};
  var n, o, r = wi(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (o = 0; o < i.length; o++) n = i[o], t.indexOf(n) === -1 && {}.propertyIsEnumerable.call(e, n) && (r[n] = e[n]);
  }
  return r;
}
var xi = /* @__PURE__ */ A.createContext({}), Ei = /* @__PURE__ */ function(e) {
  nt(n, e);
  var t = rt(n);
  function n() {
    return Me(this, n), t.apply(this, arguments);
  }
  return Oe(n, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), n;
}(A.Component);
function Ci(e) {
  var t = A.useReducer(function(a) {
    return a + 1;
  }, 0), n = Y(t, 2), o = n[1], r = A.useRef(e), i = Pe(function() {
    return r.current;
  }), s = Pe(function(a) {
    r.current = typeof a == "function" ? a(r.current) : a, o();
  });
  return [i, s];
}
var ye = "none", He = "appear", ze = "enter", Ue = "leave", yn = "none", ue = "prepare", Le = "start", Ie = "active", Ut = "end", Xn = "prepared";
function bn(e, t) {
  var n = {};
  return n[e.toLowerCase()] = t.toLowerCase(), n["Webkit".concat(e)] = "webkit".concat(t), n["Moz".concat(e)] = "moz".concat(t), n["ms".concat(e)] = "MS".concat(t), n["O".concat(e)] = "o".concat(t.toLowerCase()), n;
}
function _i(e, t) {
  var n = {
    animationend: bn("Animation", "AnimationEnd"),
    transitionend: bn("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete n.animationend.animation, "TransitionEvent" in t || delete n.transitionend.transition), n;
}
var Ri = _i(ot(), typeof window < "u" ? window : {}), Wn = {};
if (ot()) {
  var Li = document.createElement("div");
  Wn = Li.style;
}
var Be = {};
function Gn(e) {
  if (Be[e])
    return Be[e];
  var t = Ri[e];
  if (t)
    for (var n = Object.keys(t), o = n.length, r = 0; r < o; r += 1) {
      var i = n[r];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in Wn)
        return Be[e] = t[i], Be[e];
    }
  return "";
}
var Kn = Gn("animationend"), qn = Gn("transitionend"), Zn = !!(Kn && qn), Sn = Kn || "animationend", wn = qn || "transitionend";
function xn(e, t) {
  if (!e) return null;
  if (q(e) === "object") {
    var n = t.replace(/-\w/g, function(o) {
      return o[1].toUpperCase();
    });
    return e[n];
  }
  return "".concat(e, "-").concat(t);
}
const Ii = function(e) {
  var t = be();
  function n(r) {
    r && (r.removeEventListener(wn, e), r.removeEventListener(Sn, e));
  }
  function o(r) {
    t.current && t.current !== r && n(t.current), r && r !== t.current && (r.addEventListener(wn, e), r.addEventListener(Sn, e), t.current = r);
  }
  return A.useEffect(function() {
    return function() {
      n(t.current);
    };
  }, []), [o, n];
};
var Qn = ot() ? dr : xe, Yn = function(t) {
  return +setTimeout(t, 16);
}, Jn = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (Yn = function(t) {
  return window.requestAnimationFrame(t);
}, Jn = function(t) {
  return window.cancelAnimationFrame(t);
});
var En = 0, Bt = /* @__PURE__ */ new Map();
function er(e) {
  Bt.delete(e);
}
var Ft = function(t) {
  var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  En += 1;
  var o = En;
  function r(i) {
    if (i === 0)
      er(o), t();
    else {
      var s = Yn(function() {
        r(i - 1);
      });
      Bt.set(o, s);
    }
  }
  return r(n), o;
};
Ft.cancel = function(e) {
  var t = Bt.get(e);
  return er(e), Jn(t);
};
const Ti = function() {
  var e = A.useRef(null);
  function t() {
    Ft.cancel(e.current);
  }
  function n(o) {
    var r = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = Ft(function() {
      r <= 1 ? o({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : n(o, r - 1);
    });
    e.current = i;
  }
  return A.useEffect(function() {
    return function() {
      t();
    };
  }, []), [n, t];
};
var Pi = [ue, Le, Ie, Ut], Mi = [ue, Xn], tr = !1, Oi = !0;
function nr(e) {
  return e === Ie || e === Ut;
}
const Fi = function(e, t, n) {
  var o = je(yn), r = Y(o, 2), i = r[0], s = r[1], a = Ti(), c = Y(a, 2), u = c[0], p = c[1];
  function d() {
    s(ue, !0);
  }
  var f = t ? Mi : Pi;
  return Qn(function() {
    if (i !== yn && i !== Ut) {
      var m = f.indexOf(i), y = f[m + 1], b = n(i);
      b === tr ? s(y, !0) : y && u(function(g) {
        function x() {
          g.isCanceled() || s(y, !0);
        }
        b === !0 ? x() : Promise.resolve(b).then(x);
      });
    }
  }, [e, i]), A.useEffect(function() {
    return function() {
      p();
    };
  }, []), [d, i];
};
function ki(e, t, n, o) {
  var r = o.motionEnter, i = r === void 0 ? !0 : r, s = o.motionAppear, a = s === void 0 ? !0 : s, c = o.motionLeave, u = c === void 0 ? !0 : c, p = o.motionDeadline, d = o.motionLeaveImmediately, f = o.onAppearPrepare, m = o.onEnterPrepare, y = o.onLeavePrepare, b = o.onAppearStart, g = o.onEnterStart, x = o.onLeaveStart, w = o.onAppearActive, S = o.onEnterActive, v = o.onLeaveActive, R = o.onAppearEnd, h = o.onEnterEnd, L = o.onLeaveEnd, C = o.onVisibleChanged, M = je(), E = Y(M, 2), P = E[0], _ = E[1], O = Ci(ye), F = Y(O, 2), k = F[0], H = F[1], J = je(null), j = Y(J, 2), B = j[0], de = j[1], X = k(), oe = be(!1), U = be(null);
  function N() {
    return n();
  }
  var Z = be(!1);
  function ie() {
    H(ye), de(null, !0);
  }
  var te = Pe(function(K) {
    var V = k();
    if (V !== ye) {
      var ne = N();
      if (!(K && !K.deadline && K.target !== ne)) {
        var z = Z.current, _e;
        V === He && z ? _e = R == null ? void 0 : R(ne, K) : V === ze && z ? _e = h == null ? void 0 : h(ne, K) : V === Ue && z && (_e = L == null ? void 0 : L(ne, K)), z && _e !== !1 && ie();
      }
    }
  }), Fe = Ii(te), ge = Y(Fe, 1), fe = ge[0], he = function(V) {
    switch (V) {
      case He:
        return T(T(T({}, ue, f), Le, b), Ie, w);
      case ze:
        return T(T(T({}, ue, m), Le, g), Ie, S);
      case Ue:
        return T(T(T({}, ue, y), Le, x), Ie, v);
      default:
        return {};
    }
  }, pe = A.useMemo(function() {
    return he(X);
  }, [X]), Se = Fi(X, !e, function(K) {
    if (K === ue) {
      var V = pe[ue];
      return V ? V(N()) : tr;
    }
    if (D in pe) {
      var ne;
      de(((ne = pe[D]) === null || ne === void 0 ? void 0 : ne.call(pe, N(), null)) || null);
    }
    return D === Ie && X !== ye && (fe(N()), p > 0 && (clearTimeout(U.current), U.current = setTimeout(function() {
      te({
        deadline: !0
      });
    }, p))), D === Xn && ie(), Oi;
  }), Ce = Y(Se, 2), se = Ce[0], D = Ce[1], ae = nr(D);
  Z.current = ae;
  var ve = be(null);
  Qn(function() {
    if (!(oe.current && ve.current === t)) {
      _(t);
      var K = oe.current;
      oe.current = !0;
      var V;
      !K && t && a && (V = He), K && t && i && (V = ze), (K && !t && u || !K && d && !t && u) && (V = Ue);
      var ne = he(V);
      V && (e || ne[ue]) ? (H(V), se()) : H(ye), ve.current = t;
    }
  }, [t]), xe(function() {
    // Cancel appear
    (X === He && !a || // Cancel enter
    X === ze && !i || // Cancel leave
    X === Ue && !u) && H(ye);
  }, [a, i, u]), xe(function() {
    return function() {
      oe.current = !1, clearTimeout(U.current);
    };
  }, []);
  var G = A.useRef(!1);
  xe(function() {
    P && (G.current = !0), P !== void 0 && X === ye && ((G.current || P) && (C == null || C(P)), G.current = !0);
  }, [P, X]);
  var we = B;
  return pe[ue] && D === Le && (we = I({
    transition: "none"
  }, we)), [X, D, we, P ?? t];
}
function Ai(e) {
  var t = e;
  q(e) === "object" && (t = e.transitionSupport);
  function n(r, i) {
    return !!(r.motionName && t && i !== !1);
  }
  var o = /* @__PURE__ */ A.forwardRef(function(r, i) {
    var s = r.visible, a = s === void 0 ? !0 : s, c = r.removeOnLeave, u = c === void 0 ? !0 : c, p = r.forceRender, d = r.children, f = r.motionName, m = r.leavedClassName, y = r.eventProps, b = A.useContext(xi), g = b.motion, x = n(r, g), w = be(), S = be();
    function v() {
      try {
        return w.current instanceof HTMLElement ? w.current : Si(S.current);
      } catch {
        return null;
      }
    }
    var R = ki(x, a, v, r), h = Y(R, 4), L = h[0], C = h[1], M = h[2], E = h[3], P = A.useRef(E);
    E && (P.current = !0);
    var _ = A.useCallback(function(j) {
      w.current = j, Yo(i, j);
    }, [i]), O, F = I(I({}, y), {}, {
      visible: a
    });
    if (!d)
      O = null;
    else if (L === ye)
      E ? O = d(I({}, F), _) : !u && P.current && m ? O = d(I(I({}, F), {}, {
        className: m
      }), _) : p || !u && !m ? O = d(I(I({}, F), {}, {
        style: {
          display: "none"
        }
      }), _) : O = null;
    else {
      var k;
      C === ue ? k = "prepare" : nr(C) ? k = "active" : C === Le && (k = "start");
      var H = xn(f, "".concat(L, "-").concat(k));
      O = d(I(I({}, F), {}, {
        className: re(xn(f, L), T(T({}, H, H && k), f, typeof f == "string")),
        style: M
      }), _);
    }
    if (/* @__PURE__ */ A.isValidElement(O) && Jo(O)) {
      var J = ei(O);
      J || (O = /* @__PURE__ */ A.cloneElement(O, {
        ref: _
      }));
    }
    return /* @__PURE__ */ A.createElement(Ei, {
      ref: S
    }, O);
  });
  return o.displayName = "CSSMotion", o;
}
const $i = Ai(Zn);
var kt = "add", At = "keep", $t = "remove", _t = "removed";
function ji(e) {
  var t;
  return e && q(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, I(I({}, t), {}, {
    key: String(t.key)
  });
}
function jt() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(ji);
}
function Di() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], n = [], o = 0, r = t.length, i = jt(e), s = jt(t);
  i.forEach(function(u) {
    for (var p = !1, d = o; d < r; d += 1) {
      var f = s[d];
      if (f.key === u.key) {
        o < d && (n = n.concat(s.slice(o, d).map(function(m) {
          return I(I({}, m), {}, {
            status: kt
          });
        })), o = d), n.push(I(I({}, f), {}, {
          status: At
        })), o += 1, p = !0;
        break;
      }
    }
    p || n.push(I(I({}, u), {}, {
      status: $t
    }));
  }), o < r && (n = n.concat(s.slice(o).map(function(u) {
    return I(I({}, u), {}, {
      status: kt
    });
  })));
  var a = {};
  n.forEach(function(u) {
    var p = u.key;
    a[p] = (a[p] || 0) + 1;
  });
  var c = Object.keys(a).filter(function(u) {
    return a[u] > 1;
  });
  return c.forEach(function(u) {
    n = n.filter(function(p) {
      var d = p.key, f = p.status;
      return d !== u || f !== $t;
    }), n.forEach(function(p) {
      p.key === u && (p.status = At);
    });
  }), n;
}
var Ni = ["component", "children", "onVisibleChanged", "onAllRemoved"], Hi = ["status"], zi = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function Ui(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : $i, n = /* @__PURE__ */ function(o) {
    nt(i, o);
    var r = rt(i);
    function i() {
      var s;
      Me(this, i);
      for (var a = arguments.length, c = new Array(a), u = 0; u < a; u++)
        c[u] = arguments[u];
      return s = r.call.apply(r, [this].concat(c)), T(Ee(s), "state", {
        keyEntities: []
      }), T(Ee(s), "removeKey", function(p) {
        s.setState(function(d) {
          var f = d.keyEntities.map(function(m) {
            return m.key !== p ? m : I(I({}, m), {}, {
              status: _t
            });
          });
          return {
            keyEntities: f
          };
        }, function() {
          var d = s.state.keyEntities, f = d.filter(function(m) {
            var y = m.status;
            return y !== _t;
          }).length;
          f === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return Oe(i, [{
      key: "render",
      value: function() {
        var a = this, c = this.state.keyEntities, u = this.props, p = u.component, d = u.children, f = u.onVisibleChanged;
        u.onAllRemoved;
        var m = vn(u, Ni), y = p || A.Fragment, b = {};
        return zi.forEach(function(g) {
          b[g] = m[g], delete m[g];
        }), delete m.keys, /* @__PURE__ */ A.createElement(y, m, c.map(function(g, x) {
          var w = g.status, S = vn(g, Hi), v = w === kt || w === At;
          return /* @__PURE__ */ A.createElement(t, Te({}, b, {
            key: S.key,
            visible: v,
            eventProps: S,
            onVisibleChanged: function(h) {
              f == null || f(h, {
                key: S.key
              }), h || a.removeKey(S.key);
            }
          }), function(R, h) {
            return d(I(I({}, R), {}, {
              index: x
            }), h);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, c) {
        var u = a.keys, p = c.keyEntities, d = jt(u), f = Di(p, d);
        return {
          keyEntities: f.filter(function(m) {
            var y = p.find(function(b) {
              var g = b.key;
              return m.key === g;
            });
            return !(y && y.status === _t && m.status === $t);
          })
        };
      }
    }]), i;
  }(A.Component);
  return T(n, "defaultProps", {
    component: "div"
  }), n;
}
const Bi = Ui(Zn);
function Vi(e, t) {
  const {
    children: n,
    upload: o,
    rootClassName: r
  } = e, i = l.useRef(null);
  return l.useImperativeHandle(t, () => i.current), /* @__PURE__ */ l.createElement(In, Te({}, o, {
    showUploadList: !1,
    rootClassName: r,
    ref: i
  }), n);
}
const rr = /* @__PURE__ */ l.forwardRef(Vi), Xi = (e) => {
  const {
    componentCls: t,
    antCls: n,
    calc: o
  } = e, r = `${t}-list-card`, i = o(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [r]: {
      borderRadius: e.borderRadius,
      position: "relative",
      background: e.colorFillContent,
      borderWidth: e.lineWidth,
      borderStyle: "solid",
      borderColor: "transparent",
      flex: "none",
      // =============================== Desc ================================
      [`${r}-name,${r}-desc`]: {
        display: "flex",
        flexWrap: "nowrap",
        maxWidth: "100%"
      },
      [`${r}-ellipsis-prefix`]: {
        flex: "0 1 auto",
        minWidth: 0,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap"
      },
      [`${r}-ellipsis-suffix`]: {
        flex: "none"
      },
      // ============================= Overview ==============================
      "&-type-overview": {
        padding: o(e.paddingSM).sub(e.lineWidth).equal(),
        paddingInlineStart: o(e.padding).add(e.lineWidth).equal(),
        display: "flex",
        flexWrap: "nowrap",
        gap: e.paddingXS,
        alignItems: "flex-start",
        width: 236,
        // Icon
        [`${r}-icon`]: {
          fontSize: o(e.fontSizeLG).mul(2).equal(),
          lineHeight: 1,
          paddingTop: o(e.paddingXXS).mul(1.5).equal(),
          flex: "none"
        },
        // Content
        [`${r}-content`]: {
          flex: "auto",
          minWidth: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch"
        },
        [`${r}-desc`]: {
          color: e.colorTextTertiary
        }
      },
      // ============================== Preview ==============================
      "&-type-preview": {
        width: i,
        height: i,
        lineHeight: 1,
        display: "flex",
        alignItems: "center",
        [`&:not(${r}-status-error)`]: {
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
        [`${r}-img-mask`]: {
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          borderRadius: "inherit",
          background: `rgba(0, 0, 0, ${e.opacityLoading})`
        },
        // Error
        [`&${r}-status-error`]: {
          borderRadius: "inherit",
          [`img, ${r}-img-mask`]: {
            borderRadius: o(e.borderRadius).sub(e.lineWidth).equal()
          },
          [`${r}-desc`]: {
            paddingInline: e.paddingXXS
          }
        },
        // Progress
        [`${r}-progress`]: {}
      },
      // ============================ Remove Icon ============================
      [`${r}-remove`]: {
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
      [`&:hover ${r}-remove`]: {
        display: "block"
      },
      // ============================== Status ===============================
      "&-status-error": {
        borderColor: e.colorError,
        [`${r}-desc`]: {
          color: e.colorError
        }
      },
      // ============================== Motion ===============================
      "&-motion": {
        transition: ["opacity", "width", "margin", "padding"].map((s) => `${s} ${e.motionDurationSlow}`).join(","),
        "&-appear-start": {
          width: 0,
          transition: "none"
        },
        "&-leave-active": {
          opacity: 0,
          width: 0,
          paddingInline: 0,
          borderInlineWidth: 0,
          marginInlineEnd: o(e.paddingSM).mul(-1).equal()
        }
      }
    }
  };
}, Dt = {
  "&, *": {
    boxSizing: "border-box"
  }
}, Wi = (e) => {
  const {
    componentCls: t,
    calc: n,
    antCls: o
  } = e, r = `${t}-drop-area`, i = `${t}-placeholder`;
  return {
    // ============================== Full Screen ==============================
    [r]: {
      position: "absolute",
      inset: 0,
      zIndex: e.zIndexPopupBase,
      ...Dt,
      "&-on-body": {
        position: "fixed",
        inset: 0
      },
      "&-hide-placement": {
        [`${i}-inner`]: {
          display: "none"
        }
      },
      [i]: {
        padding: 0
      }
    },
    "&": {
      // ============================= Placeholder =============================
      [i]: {
        height: "100%",
        borderRadius: e.borderRadius,
        borderWidth: e.lineWidthBold,
        borderStyle: "dashed",
        borderColor: "transparent",
        padding: e.padding,
        position: "relative",
        backdropFilter: "blur(10px)",
        background: e.colorBgPlaceholderHover,
        ...Dt,
        [`${o}-upload-wrapper ${o}-upload${o}-upload-btn`]: {
          padding: 0
        },
        [`&${i}-drag-in`]: {
          borderColor: e.colorPrimaryHover
        },
        [`&${i}-disabled`]: {
          opacity: 0.25,
          pointerEvents: "none"
        },
        [`${i}-inner`]: {
          gap: n(e.paddingXXS).div(2).equal()
        },
        [`${i}-icon`]: {
          fontSize: e.fontSizeHeading2,
          lineHeight: 1
        },
        [`${i}-title${i}-title`]: {
          margin: 0,
          fontSize: e.fontSize,
          lineHeight: e.lineHeight
        },
        [`${i}-description`]: {}
      }
    }
  };
}, Gi = (e) => {
  const {
    componentCls: t,
    calc: n
  } = e, o = `${t}-list`, r = n(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [t]: {
      position: "relative",
      width: "100%",
      ...Dt,
      // =============================== File List ===============================
      [o]: {
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
          maxHeight: n(r).mul(3).equal(),
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
          width: r,
          height: r,
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
          [`&${o}-overflow-ping-start ${o}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${o}-overflow-ping-end ${o}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        },
        "&:dir(rtl)": {
          [`&${o}-overflow-ping-end ${o}-prev-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          },
          [`&${o}-overflow-ping-start ${o}-next-btn`]: {
            opacity: 1,
            pointerEvents: "auto"
          }
        }
      }
    }
  };
}, Ki = (e) => {
  const {
    colorBgContainer: t
  } = e;
  return {
    colorBgPlaceholderHover: new me(t).setA(0.85).toRgbString()
  };
}, or = yi("Attachments", (e) => {
  const t = zt(e, {});
  return [Wi(t), Gi(t), Xi(t)];
}, Ki), qi = (e) => e.indexOf("image/") === 0, Ve = 200;
function Zi(e) {
  return new Promise((t) => {
    if (!e || !e.type || !qi(e.type)) {
      t("");
      return;
    }
    const n = new Image();
    if (n.onload = () => {
      const {
        width: o,
        height: r
      } = n, i = o / r, s = i > 1 ? Ve : Ve * i, a = i > 1 ? Ve / i : Ve, c = document.createElement("canvas");
      c.width = s, c.height = a, c.style.cssText = `position: fixed; left: 0; top: 0; width: ${s}px; height: ${a}px; z-index: 9999; display: none;`, document.body.appendChild(c), c.getContext("2d").drawImage(n, 0, 0, s, a);
      const p = c.toDataURL();
      document.body.removeChild(c), window.URL.revokeObjectURL(n.src), t(p);
    }, n.crossOrigin = "anonymous", e.type.startsWith("image/svg+xml")) {
      const o = new FileReader();
      o.onload = () => {
        o.result && typeof o.result == "string" && (n.src = o.result);
      }, o.readAsDataURL(e);
    } else if (e.type.startsWith("image/gif")) {
      const o = new FileReader();
      o.onload = () => {
        o.result && t(o.result);
      }, o.readAsDataURL(e);
    } else
      n.src = window.URL.createObjectURL(e);
  });
}
function Qi() {
  return /* @__PURE__ */ l.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    //xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ l.createElement("title", null, "audio"), /* @__PURE__ */ l.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ l.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M10.7315824,7.11216117 C10.7428131,7.15148751 10.7485063,7.19218979 10.7485063,7.23309113 L10.7485063,8.07742614 C10.7484199,8.27364959 10.6183424,8.44607275 10.4296853,8.50003683 L8.32984514,9.09986306 L8.32984514,11.7071803 C8.32986605,12.5367078 7.67249692,13.217028 6.84345686,13.2454634 L6.79068592,13.2463395 C6.12766108,13.2463395 5.53916361,12.8217001 5.33010655,12.1924966 C5.1210495,11.563293 5.33842118,10.8709227 5.86959669,10.4741173 C6.40077221,10.0773119 7.12636292,10.0652587 7.67042486,10.4442027 L7.67020842,7.74937024 L7.68449368,7.74937024 C7.72405122,7.59919041 7.83988806,7.48101083 7.98924584,7.4384546 L10.1880418,6.81004755 C10.42156,6.74340323 10.6648954,6.87865515 10.7315824,7.11216117 Z M9.60714286,1.31785714 L12.9678571,4.67857143 L9.60714286,4.67857143 L9.60714286,1.31785714 Z",
    fill: "currentColor"
  })));
}
function Yi(e) {
  const {
    percent: t
  } = e, {
    token: n
  } = Qe.useToken();
  return /* @__PURE__ */ l.createElement(Sr, {
    type: "circle",
    percent: t,
    size: n.fontSizeHeading2 * 2,
    strokeColor: "#FFF",
    trailColor: "rgba(255, 255, 255, 0.3)",
    format: (o) => /* @__PURE__ */ l.createElement("span", {
      style: {
        color: "#FFF"
      }
    }, (o || 0).toFixed(0), "%")
  });
}
function Ji() {
  return /* @__PURE__ */ l.createElement("svg", {
    width: "1em",
    height: "1em",
    viewBox: "0 0 16 16",
    version: "1.1",
    xmlns: "http://www.w3.org/2000/svg"
    // xmlnsXlink="http://www.w3.org/1999/xlink"
  }, /* @__PURE__ */ l.createElement("title", null, "video"), /* @__PURE__ */ l.createElement("g", {
    stroke: "none",
    strokeWidth: "1",
    fill: "none",
    fillRule: "evenodd"
  }, /* @__PURE__ */ l.createElement("path", {
    d: "M14.1178571,4.0125 C14.225,4.11964286 14.2857143,4.26428571 14.2857143,4.41607143 L14.2857143,15.4285714 C14.2857143,15.7446429 14.0303571,16 13.7142857,16 L2.28571429,16 C1.96964286,16 1.71428571,15.7446429 1.71428571,15.4285714 L1.71428571,0.571428571 C1.71428571,0.255357143 1.96964286,0 2.28571429,0 L9.86964286,0 C10.0214286,0 10.1678571,0.0607142857 10.275,0.167857143 L14.1178571,4.0125 Z M12.9678571,4.67857143 L9.60714286,1.31785714 L9.60714286,4.67857143 L12.9678571,4.67857143 Z M10.5379461,10.3101106 L6.68957555,13.0059749 C6.59910784,13.0693494 6.47439406,13.0473861 6.41101953,12.9569184 C6.3874624,12.9232903 6.37482581,12.8832269 6.37482581,12.8421686 L6.37482581,7.45043999 C6.37482581,7.33998304 6.46436886,7.25043999 6.57482581,7.25043999 C6.61588409,7.25043999 6.65594753,7.26307658 6.68957555,7.28663371 L10.5379461,9.98249803 C10.6284138,10.0458726 10.6503772,10.1705863 10.5870027,10.2610541 C10.5736331,10.2801392 10.5570312,10.2967411 10.5379461,10.3101106 Z",
    fill: "currentColor"
  })));
}
const Rt = " ", Ke = "#8c8c8c", ir = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"], Cn = [{
  key: "default",
  icon: /* @__PURE__ */ l.createElement(Tn, null),
  color: Ke,
  ext: []
}, {
  key: "excel",
  icon: /* @__PURE__ */ l.createElement(Cr, null),
  color: "#22b35e",
  ext: ["xlsx", "xls"]
}, {
  key: "image",
  icon: /* @__PURE__ */ l.createElement(_r, null),
  color: Ke,
  ext: ir
}, {
  key: "markdown",
  icon: /* @__PURE__ */ l.createElement(Rr, null),
  color: Ke,
  ext: ["md", "mdx"]
}, {
  key: "pdf",
  icon: /* @__PURE__ */ l.createElement(Lr, null),
  color: "#ff4d4f",
  ext: ["pdf"]
}, {
  key: "ppt",
  icon: /* @__PURE__ */ l.createElement(Ir, null),
  color: "#ff6e31",
  ext: ["ppt", "pptx"]
}, {
  key: "word",
  icon: /* @__PURE__ */ l.createElement(Tr, null),
  color: "#1677ff",
  ext: ["doc", "docx"]
}, {
  key: "zip",
  icon: /* @__PURE__ */ l.createElement(Pr, null),
  color: "#fab714",
  ext: ["zip", "rar", "7z", "tar", "gz"]
}, {
  key: "video",
  icon: /* @__PURE__ */ l.createElement(Ji, null),
  color: "#ff4d4f",
  ext: ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
}, {
  key: "audio",
  icon: /* @__PURE__ */ l.createElement(Qi, null),
  color: "#8c8c8c",
  ext: ["mp3", "wav", "flac", "ape", "aac", "ogg"]
}];
function _n(e, t) {
  return t.some((n) => e.toLowerCase() === `.${n}`);
}
function es(e) {
  let t = e;
  const n = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
  let o = 0;
  for (; t >= 1024 && o < n.length - 1; )
    t /= 1024, o++;
  return `${t.toFixed(0)} ${n[o]}`;
}
function ts(e, t) {
  const {
    prefixCls: n,
    item: o,
    onRemove: r,
    className: i,
    style: s,
    imageProps: a,
    type: c,
    icon: u
  } = e, p = l.useContext(De), {
    disabled: d
  } = p || {}, {
    name: f,
    size: m,
    percent: y,
    status: b = "done",
    description: g
  } = o, {
    getPrefixCls: x
  } = Ye(), w = x("attachment", n), S = `${w}-list-card`, [v, R, h] = or(w), [L, C] = l.useMemo(() => {
    const j = f || "", B = j.match(/^(.*)\.[^.]+$/);
    return B ? [B[1], j.slice(B[1].length)] : [j, ""];
  }, [f]), M = l.useMemo(() => _n(C, ir), [C]), E = l.useMemo(() => g || (b === "uploading" ? `${y || 0}%` : b === "error" ? o.response || Rt : m ? es(m) : Rt), [b, y]), [P, _] = l.useMemo(() => {
    if (u)
      if (typeof u == "string") {
        const j = Cn.find((B) => B.key === u);
        if (j)
          return [j.icon, j.color];
      } else
        return [u, void 0];
    for (const {
      ext: j,
      icon: B,
      color: de
    } of Cn)
      if (_n(C, j))
        return [B, de];
    return [/* @__PURE__ */ l.createElement(Tn, {
      key: "defaultIcon"
    }), Ke];
  }, [C, u]), [O, F] = l.useState();
  l.useEffect(() => {
    if (o.originFileObj) {
      let j = !0;
      return Zi(o.originFileObj).then((B) => {
        j && F(B);
      }), () => {
        j = !1;
      };
    }
    F(void 0);
  }, [o.originFileObj]);
  let k = null;
  const H = o.thumbUrl || o.url || O, J = c === "image" || c !== "file" && M && (o.originFileObj || H);
  return J ? k = /* @__PURE__ */ l.createElement(l.Fragment, null, H && /* @__PURE__ */ l.createElement(wr, Te({
    alt: "preview",
    src: H
  }, a)), b !== "done" && /* @__PURE__ */ l.createElement("div", {
    className: `${S}-img-mask`
  }, b === "uploading" && y !== void 0 && /* @__PURE__ */ l.createElement(Yi, {
    percent: y,
    prefixCls: S
  }), b === "error" && /* @__PURE__ */ l.createElement("div", {
    className: `${S}-desc`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${S}-ellipsis-prefix`
  }, E)))) : k = /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement("div", {
    className: `${S}-icon`,
    style: _ ? {
      color: _
    } : void 0
  }, P), /* @__PURE__ */ l.createElement("div", {
    className: `${S}-content`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${S}-name`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${S}-ellipsis-prefix`
  }, L ?? Rt), /* @__PURE__ */ l.createElement("div", {
    className: `${S}-ellipsis-suffix`
  }, C)), /* @__PURE__ */ l.createElement("div", {
    className: `${S}-desc`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${S}-ellipsis-prefix`
  }, E)))), v(/* @__PURE__ */ l.createElement("div", {
    className: re(S, {
      [`${S}-status-${b}`]: b,
      [`${S}-type-preview`]: J,
      [`${S}-type-overview`]: !J
    }, i, R, h),
    style: s,
    ref: t
  }, k, !d && r && /* @__PURE__ */ l.createElement("button", {
    type: "button",
    className: `${S}-remove`,
    onClick: () => {
      r(o);
    }
  }, /* @__PURE__ */ l.createElement(Er, null))));
}
const sr = /* @__PURE__ */ l.forwardRef(ts), Rn = 1;
function ns(e) {
  const {
    prefixCls: t,
    items: n,
    onRemove: o,
    overflow: r,
    upload: i,
    listClassName: s,
    listStyle: a,
    itemClassName: c,
    uploadClassName: u,
    uploadStyle: p,
    itemStyle: d,
    imageProps: f
  } = e, m = `${t}-list`, y = l.useRef(null), [b, g] = l.useState(!1), {
    disabled: x
  } = l.useContext(De);
  l.useEffect(() => (g(!0), () => {
    g(!1);
  }), []);
  const [w, S] = l.useState(!1), [v, R] = l.useState(!1), h = () => {
    const E = y.current;
    E && (r === "scrollX" ? (S(Math.abs(E.scrollLeft) >= Rn), R(E.scrollWidth - E.clientWidth - Math.abs(E.scrollLeft) >= Rn)) : r === "scrollY" && (S(E.scrollTop !== 0), R(E.scrollHeight - E.clientHeight !== E.scrollTop)));
  };
  l.useEffect(() => {
    h();
  }, [r, n.length]);
  const L = (E) => {
    const P = y.current;
    P && P.scrollTo({
      left: P.scrollLeft + E * P.clientWidth,
      behavior: "smooth"
    });
  }, C = () => {
    L(-1);
  }, M = () => {
    L(1);
  };
  return /* @__PURE__ */ l.createElement("div", {
    className: re(m, {
      [`${m}-overflow-${e.overflow}`]: r,
      [`${m}-overflow-ping-start`]: w,
      [`${m}-overflow-ping-end`]: v
    }, s),
    ref: y,
    onScroll: h,
    style: a
  }, /* @__PURE__ */ l.createElement(Bi, {
    keys: n.map((E) => ({
      key: E.uid,
      item: E
    })),
    motionName: `${m}-card-motion`,
    component: !1,
    motionAppear: b,
    motionLeave: !0,
    motionEnter: !0
  }, ({
    key: E,
    item: P,
    className: _,
    style: O
  }) => /* @__PURE__ */ l.createElement(sr, {
    key: E,
    prefixCls: t,
    item: P,
    onRemove: o,
    className: re(_, c),
    imageProps: f,
    style: {
      ...O,
      ...d
    }
  })), !x && /* @__PURE__ */ l.createElement(rr, {
    upload: i
  }, /* @__PURE__ */ l.createElement(gt, {
    className: re(u, `${m}-upload-btn`),
    style: p,
    type: "dashed"
  }, /* @__PURE__ */ l.createElement(Mr, {
    className: `${m}-upload-btn-icon`
  }))), r === "scrollX" && /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(gt, {
    size: "small",
    shape: "circle",
    className: `${m}-prev-btn`,
    icon: /* @__PURE__ */ l.createElement(Or, null),
    onClick: C
  }), /* @__PURE__ */ l.createElement(gt, {
    size: "small",
    shape: "circle",
    className: `${m}-next-btn`,
    icon: /* @__PURE__ */ l.createElement(Fr, null),
    onClick: M
  })));
}
function rs(e, t) {
  const {
    prefixCls: n,
    placeholder: o = {},
    upload: r,
    className: i,
    style: s
  } = e, a = `${n}-placeholder`, c = o || {}, {
    disabled: u
  } = l.useContext(De), [p, d] = l.useState(!1), f = () => {
    d(!0);
  }, m = (g) => {
    g.currentTarget.contains(g.relatedTarget) || d(!1);
  }, y = () => {
    d(!1);
  }, b = /* @__PURE__ */ l.isValidElement(o) ? o : /* @__PURE__ */ l.createElement(xr, {
    align: "center",
    justify: "center",
    vertical: !0,
    className: `${a}-inner`
  }, /* @__PURE__ */ l.createElement(ht.Text, {
    className: `${a}-icon`
  }, c.icon), /* @__PURE__ */ l.createElement(ht.Title, {
    className: `${a}-title`,
    level: 5
  }, c.title), /* @__PURE__ */ l.createElement(ht.Text, {
    className: `${a}-description`,
    type: "secondary"
  }, c.description));
  return /* @__PURE__ */ l.createElement("div", {
    className: re(a, {
      [`${a}-drag-in`]: p,
      [`${a}-disabled`]: u
    }, i),
    onDragEnter: f,
    onDragLeave: m,
    onDrop: y,
    "aria-hidden": u,
    style: s
  }, /* @__PURE__ */ l.createElement(In.Dragger, Te({
    showUploadList: !1
  }, r, {
    ref: t,
    style: {
      padding: 0,
      border: 0,
      background: "transparent"
    }
  }), b));
}
const os = /* @__PURE__ */ l.forwardRef(rs);
function is(e, t) {
  const {
    prefixCls: n,
    rootClassName: o,
    rootStyle: r,
    className: i,
    style: s,
    items: a,
    children: c,
    getDropContainer: u,
    placeholder: p,
    onChange: d,
    onRemove: f,
    overflow: m,
    imageProps: y,
    disabled: b,
    maxCount: g,
    classNames: x = {},
    styles: w = {},
    ...S
  } = e, {
    getPrefixCls: v,
    direction: R
  } = Ye(), h = v("attachment", n), L = Fo("attachments"), {
    classNames: C,
    styles: M
  } = L, E = l.useRef(null), P = l.useRef(null);
  l.useImperativeHandle(t, () => ({
    nativeElement: E.current,
    upload: (U) => {
      var Z, ie;
      const N = (ie = (Z = P.current) == null ? void 0 : Z.nativeElement) == null ? void 0 : ie.querySelector('input[type="file"]');
      if (N) {
        const te = new DataTransfer();
        te.items.add(U), N.files = te.files, N.dispatchEvent(new Event("change", {
          bubbles: !0
        }));
      }
    }
  }));
  const [_, O, F] = or(h), k = re(O, F), [H, J] = Vo([], {
    value: a
  }), j = Pe((U) => {
    J(U.fileList), d == null || d(U);
  }), B = {
    ...S,
    fileList: H,
    maxCount: g,
    onChange: j
  }, de = (U) => Promise.resolve(typeof f == "function" ? f(U) : f).then((N) => {
    if (N === !1)
      return;
    const Z = H.filter((ie) => ie.uid !== U.uid);
    j({
      file: {
        ...U,
        status: "removed"
      },
      fileList: Z
    });
  });
  let X;
  const oe = (U, N, Z) => {
    const ie = typeof p == "function" ? p(U) : p;
    return /* @__PURE__ */ l.createElement(os, {
      placeholder: ie,
      upload: B,
      prefixCls: h,
      className: re(C.placeholder, x.placeholder),
      style: {
        ...M.placeholder,
        ...w.placeholder,
        ...N == null ? void 0 : N.style
      },
      ref: Z
    });
  };
  if (c)
    X = /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(rr, {
      upload: B,
      rootClassName: o,
      ref: P
    }, c), /* @__PURE__ */ l.createElement(gn, {
      getDropContainer: u,
      prefixCls: h,
      className: re(k, o)
    }, oe("drop")));
  else {
    const U = H.length > 0;
    X = /* @__PURE__ */ l.createElement("div", {
      className: re(h, k, {
        [`${h}-rtl`]: R === "rtl"
      }, i, o),
      style: {
        ...r,
        ...s
      },
      dir: R || "ltr",
      ref: E
    }, /* @__PURE__ */ l.createElement(ns, {
      prefixCls: h,
      items: H,
      onRemove: de,
      overflow: m,
      upload: B,
      listClassName: re(C.list, x.list),
      listStyle: {
        ...M.list,
        ...w.list,
        ...!U && {
          display: "none"
        }
      },
      uploadClassName: re(C.upload, x.upload),
      uploadStyle: {
        ...M.upload,
        ...w.upload
      },
      itemClassName: re(C.item, x.item),
      itemStyle: {
        ...M.item,
        ...w.item
      },
      imageProps: y
    }), oe("inline", U ? {
      style: {
        display: "none"
      }
    } : {}, P), /* @__PURE__ */ l.createElement(gn, {
      getDropContainer: u || (() => E.current),
      prefixCls: h,
      className: k
    }, oe("drop")));
  }
  return _(/* @__PURE__ */ l.createElement(De.Provider, {
    value: {
      disabled: b
    }
  }, X));
}
const ar = /* @__PURE__ */ l.forwardRef(is);
ar.FileCard = sr;
function ss(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function as(e, t = !1) {
  try {
    if (hr(e))
      return e;
    if (t && !ss(e))
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
function Q(e, t) {
  return et(() => as(e, t), [e, t]);
}
function ls(e, t) {
  const n = et(() => l.Children.toArray(e.originalChildren || e).filter((i) => i.props.node && !i.props.node.ignore && (!i.props.nodeSlotKey || t)).sort((i, s) => {
    if (i.props.node.slotIndex && s.props.node.slotIndex) {
      const a = Ae(i.props.node.slotIndex) || 0, c = Ae(s.props.node.slotIndex) || 0;
      return a - c === 0 && i.props.node.subSlotIndex && s.props.node.subSlotIndex ? (Ae(i.props.node.subSlotIndex) || 0) - (Ae(s.props.node.subSlotIndex) || 0) : a - c;
    }
    return 0;
  }).map((i) => i.props.node.target), [e, t]);
  return Co(n);
}
function cs(e, t) {
  return Object.keys(e).reduce((n, o) => (e[o] !== void 0 && (n[o] = e[o]), n), {});
}
const us = ({
  children: e,
  ...t
}) => /* @__PURE__ */ ee.jsx(ee.Fragment, {
  children: e(t)
});
function ds(e) {
  return l.createElement(us, {
    children: e
  });
}
function Ln(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ds((n) => /* @__PURE__ */ ee.jsx(yr, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ ee.jsx($e, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...n
    })
  })) : /* @__PURE__ */ ee.jsx($e, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function le({
  key: e,
  slots: t,
  targets: n
}, o) {
  return t[e] ? (...r) => n ? n.map((i, s) => /* @__PURE__ */ ee.jsx(l.Fragment, {
    children: Ln(i, {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }, s)) : /* @__PURE__ */ ee.jsx(ee.Fragment, {
    children: Ln(t[e], {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }) : void 0;
}
const fs = (e) => !!e.name;
function Lt(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const gs = xo(({
  slots: e,
  upload: t,
  showUploadList: n,
  progress: o,
  beforeUpload: r,
  customRequest: i,
  previewFile: s,
  isImageUrl: a,
  itemRender: c,
  iconRender: u,
  data: p,
  onChange: d,
  onValueChange: f,
  onRemove: m,
  items: y,
  setSlotParams: b,
  placeholder: g,
  getDropContainer: x,
  children: w,
  maxCount: S,
  imageProps: v,
  ...R
}) => {
  const h = Lt(v == null ? void 0 : v.preview), L = e["imageProps.preview.mask"] || e["imageProps.preview.closeIcon"] || e["imageProps.preview.toolbarRender"] || e["imageProps.preview.imageRender"] || (v == null ? void 0 : v.preview) !== !1, C = Q(h.getContainer), M = Q(h.toolbarRender), E = Q(h.imageRender), P = e["showUploadList.downloadIcon"] || e["showUploadList.removeIcon"] || e["showUploadList.previewIcon"] || e["showUploadList.extra"] || typeof n == "object", _ = Lt(n), O = e["placeholder.title"] || e["placeholder.description"] || e["placeholder.icon"] || typeof g == "object", F = Lt(g), k = Q(_.showPreviewIcon), H = Q(_.showRemoveIcon), J = Q(_.showDownloadIcon), j = Q(r), B = Q(i), de = Q(o == null ? void 0 : o.format), X = Q(s), oe = Q(a), U = Q(c), N = Q(u), Z = Q(g, !0), ie = Q(x), te = Q(p), [Fe, ge] = qe(!1), [fe, he] = qe(y);
  xe(() => {
    he(y);
  }, [y]);
  const pe = et(() => {
    const se = {};
    return fe.map((D) => {
      if (!fs(D)) {
        const ae = D.uid || D.url || D.path;
        return se[ae] || (se[ae] = 0), se[ae]++, {
          ...D,
          name: D.orig_name || D.path,
          uid: D.uid || ae + "-" + se[ae],
          status: "done"
        };
      }
      return D;
    }) || [];
  }, [fe]), Se = ls(w), Ce = R.disabled || Fe;
  return /* @__PURE__ */ ee.jsxs(ee.Fragment, {
    children: [/* @__PURE__ */ ee.jsx("div", {
      style: {
        display: "none"
      },
      children: Se.length > 0 ? null : w
    }), /* @__PURE__ */ ee.jsx(ar, {
      ...R,
      disabled: Ce,
      imageProps: {
        ...v,
        preview: L ? cs({
          ...h,
          getContainer: C,
          toolbarRender: e["imageProps.preview.toolbarRender"] ? le({
            slots: e,
            key: "imageProps.preview.toolbarRender"
          }) : M,
          imageRender: e["imageProps.preview.imageRender"] ? le({
            slots: e,
            key: "imageProps.preview.imageRender"
          }) : E,
          ...e["imageProps.preview.mask"] || Reflect.has(h, "mask") ? {
            mask: e["imageProps.preview.mask"] ? /* @__PURE__ */ ee.jsx($e, {
              slot: e["imageProps.preview.mask"]
            }) : h.mask
          } : {},
          closeIcon: e["imageProps.preview.closeIcon"] ? /* @__PURE__ */ ee.jsx($e, {
            slot: e["imageProps.preview.closeIcon"]
          }) : h.closeIcon
        }) : !1,
        placeholder: e["imageProps.placeholder"] ? /* @__PURE__ */ ee.jsx($e, {
          slot: e["imageProps.placeholder"]
        }) : v == null ? void 0 : v.placeholder
      },
      getDropContainer: ie,
      placeholder: e.placeholder ? le({
        slots: e,
        key: "placeholder"
      }) : O ? (...se) => {
        var D, ae, ve;
        return {
          ...F,
          icon: e["placeholder.icon"] ? (D = le({
            slots: e,
            key: "placeholder.icon"
          })) == null ? void 0 : D(...se) : F.icon,
          title: e["placeholder.title"] ? (ae = le({
            slots: e,
            key: "placeholder.title"
          })) == null ? void 0 : ae(...se) : F.title,
          description: e["placeholder.description"] ? (ve = le({
            slots: e,
            key: "placeholder.description"
          })) == null ? void 0 : ve(...se) : F.description
        };
      } : Z || g,
      items: pe,
      data: te || p,
      previewFile: X,
      isImageUrl: oe,
      itemRender: e.itemRender ? le({
        slots: e,
        key: "itemRender"
      }) : U,
      iconRender: e.iconRender ? le({
        slots: e,
        key: "iconRender"
      }) : N,
      maxCount: S,
      onChange: async (se) => {
        try {
          const D = se.file, ae = se.fileList, ve = pe.findIndex((G) => G.uid === D.uid);
          if (ve !== -1) {
            if (Ce)
              return;
            m == null || m(D);
            const G = fe.slice();
            G.splice(ve, 1), f == null || f(G), d == null || d(G.map((we) => we.path));
          } else {
            if (j && !await j(D, ae) || Ce)
              return;
            ge(!0);
            let G = ae.filter((z) => z.status !== "done");
            if (S === 1)
              G = G.slice(0, 1);
            else if (G.length === 0) {
              ge(!1);
              return;
            } else if (typeof S == "number") {
              const z = S - fe.length;
              G = G.slice(0, z < 0 ? 0 : z);
            }
            const we = fe, K = G.map((z) => ({
              ...z,
              size: z.size,
              uid: z.uid,
              name: z.name,
              status: "uploading"
            }));
            he((z) => [...S === 1 ? [] : z, ...K]);
            const V = (await t(G.map((z) => z.originFileObj))).filter(Boolean).map((z, _e) => ({
              ...z,
              uid: K[_e].uid
            })), ne = S === 1 ? V : [...we, ...V];
            ge(!1), he(ne), f == null || f(ne), d == null || d(ne.map((z) => z.path));
          }
        } catch (D) {
          console.error(D), ge(!1);
        }
      },
      customRequest: B || Xr,
      progress: o && {
        ...o,
        format: de
      },
      showUploadList: P ? {
        ..._,
        showDownloadIcon: J || _.showDownloadIcon,
        showRemoveIcon: H || _.showRemoveIcon,
        showPreviewIcon: k || _.showPreviewIcon,
        downloadIcon: e["showUploadList.downloadIcon"] ? le({
          slots: e,
          key: "showUploadList.downloadIcon"
        }) : _.downloadIcon,
        removeIcon: e["showUploadList.removeIcon"] ? le({
          slots: e,
          key: "showUploadList.removeIcon"
        }) : _.removeIcon,
        previewIcon: e["showUploadList.previewIcon"] ? le({
          slots: e,
          key: "showUploadList.previewIcon"
        }) : _.previewIcon,
        extra: e["showUploadList.extra"] ? le({
          slots: e,
          key: "showUploadList.extra"
        }) : _.extra
      } : n,
      children: Se.length > 0 ? w : void 0
    })]
  });
});
export {
  gs as Attachments,
  gs as default
};
