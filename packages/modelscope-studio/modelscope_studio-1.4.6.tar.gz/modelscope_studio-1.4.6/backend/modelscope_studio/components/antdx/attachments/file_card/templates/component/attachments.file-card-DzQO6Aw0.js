var Nt = (e) => {
  throw TypeError(e);
};
var Ht = (e, t, n) => t.has(e) || Nt("Cannot " + n);
var de = (e, t, n) => (Ht(e, t, "read from private field"), n ? n.call(e) : t.get(e)), zt = (e, t, n) => t.has(e) ? Nt("Cannot add the same private member more than once") : t instanceof WeakSet ? t.add(e) : t.set(e, n), Bt = (e, t, n, r) => (Ht(e, t, "write to private field"), r ? r.call(e, n) : t.set(e, n), n);
import { i as vr, a as xt, r as br, Z as je, g as yr, b as Sr, c as Z } from "./Index-BEKSkSSi.js";
const O = window.ms_globals.React, l = window.ms_globals.React, dr = window.ms_globals.React.forwardRef, le = window.ms_globals.React.useRef, pr = window.ms_globals.React.useState, we = window.ms_globals.React.useEffect, Ln = window.ms_globals.React.useMemo, mr = window.ms_globals.React.version, gr = window.ms_globals.React.isValidElement, hr = window.ms_globals.React.useLayoutEffect, Vt = window.ms_globals.ReactDOM, ze = window.ms_globals.ReactDOM.createPortal, xr = window.ms_globals.internalContext.useContextPropsContext, wr = window.ms_globals.internalContext.ContextPropsProvider, Er = window.ms_globals.antd.ConfigProvider, Be = window.ms_globals.antd.theme, Mn = window.ms_globals.antd.Upload, Cr = window.ms_globals.antd.Progress, _r = window.ms_globals.antd.Image, lt = window.ms_globals.antd.Button, Rr = window.ms_globals.antd.Flex, ct = window.ms_globals.antd.Typography, In = window.ms_globals.antdIcons.FileTextFilled, Tr = window.ms_globals.antdIcons.CloseCircleFilled, Pr = window.ms_globals.antdIcons.FileExcelFilled, Lr = window.ms_globals.antdIcons.FileImageFilled, Mr = window.ms_globals.antdIcons.FileMarkdownFilled, Ir = window.ms_globals.antdIcons.FilePdfFilled, Or = window.ms_globals.antdIcons.FilePptFilled, $r = window.ms_globals.antdIcons.FileWordFilled, Ar = window.ms_globals.antdIcons.FileZipFilled, kr = window.ms_globals.antdIcons.PlusOutlined, Fr = window.ms_globals.antdIcons.LeftOutlined, jr = window.ms_globals.antdIcons.RightOutlined, Ut = window.ms_globals.antdCssinjs.unit, ut = window.ms_globals.antdCssinjs.token2CSSVar, Xt = window.ms_globals.antdCssinjs.useStyleRegister, Dr = window.ms_globals.antdCssinjs.useCSSVarRegister, Nr = window.ms_globals.antdCssinjs.createTheme, Hr = window.ms_globals.antdCssinjs.useCacheToken;
var zr = /\s/;
function Br(e) {
  for (var t = e.length; t-- && zr.test(e.charAt(t)); )
    ;
  return t;
}
var Vr = /^\s+/;
function Ur(e) {
  return e && e.slice(0, Br(e) + 1).replace(Vr, "");
}
var Wt = NaN, Xr = /^[-+]0x[0-9a-f]+$/i, Wr = /^0b[01]+$/i, Gr = /^0o[0-7]+$/i, qr = parseInt;
function Gt(e) {
  if (typeof e == "number")
    return e;
  if (vr(e))
    return Wt;
  if (xt(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = xt(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Ur(e);
  var n = Wr.test(e);
  return n || Gr.test(e) ? qr(e.slice(2), n ? 2 : 8) : Xr.test(e) ? Wt : +e;
}
var ft = function() {
  return br.Date.now();
}, Kr = "Expected a function", Zr = Math.max, Qr = Math.min;
function Yr(e, t, n) {
  var r, o, i, s, a, u, c = 0, d = !1, f = !1, p = !0;
  if (typeof e != "function")
    throw new TypeError(Kr);
  t = Gt(t) || 0, xt(n) && (d = !!n.leading, f = "maxWait" in n, i = f ? Zr(Gt(n.maxWait) || 0, t) : i, p = "trailing" in n ? !!n.trailing : p);
  function m(v) {
    var P = r, C = o;
    return r = o = void 0, c = v, s = e.apply(C, P), s;
  }
  function b(v) {
    return c = v, a = setTimeout(x, t), d ? m(v) : s;
  }
  function h(v) {
    var P = v - u, C = v - c, I = t - P;
    return f ? Qr(I, i - C) : I;
  }
  function g(v) {
    var P = v - u, C = v - c;
    return u === void 0 || P >= t || P < 0 || f && C >= i;
  }
  function x() {
    var v = ft();
    if (g(v))
      return w(v);
    a = setTimeout(x, h(v));
  }
  function w(v) {
    return a = void 0, p && r ? m(v) : (r = o = void 0, s);
  }
  function y() {
    a !== void 0 && clearTimeout(a), c = 0, r = u = o = a = void 0;
  }
  function S() {
    return a === void 0 ? s : w(ft());
  }
  function _() {
    var v = ft(), P = g(v);
    if (r = arguments, o = this, u = v, P) {
      if (a === void 0)
        return b(u);
      if (f)
        return clearTimeout(a), a = setTimeout(x, t), m(u);
    }
    return a === void 0 && (a = setTimeout(x, t)), s;
  }
  return _.cancel = y, _.flush = S, _;
}
var On = {
  exports: {}
}, Xe = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Jr = l, eo = Symbol.for("react.element"), to = Symbol.for("react.fragment"), no = Object.prototype.hasOwnProperty, ro = Jr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, oo = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function $n(e, t, n) {
  var r, o = {}, i = null, s = null;
  n !== void 0 && (i = "" + n), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (r in t) no.call(t, r) && !oo.hasOwnProperty(r) && (o[r] = t[r]);
  if (e && e.defaultProps) for (r in t = e.defaultProps, t) o[r] === void 0 && (o[r] = t[r]);
  return {
    $$typeof: eo,
    type: e,
    key: i,
    ref: s,
    props: o,
    _owner: ro.current
  };
}
Xe.Fragment = to;
Xe.jsx = $n;
Xe.jsxs = $n;
On.exports = Xe;
var V = On.exports;
const {
  SvelteComponent: io,
  assign: qt,
  binding_callbacks: Kt,
  check_outros: so,
  children: An,
  claim_element: kn,
  claim_space: ao,
  component_subscribe: Zt,
  compute_slots: lo,
  create_slot: co,
  detach: pe,
  element: Fn,
  empty: Qt,
  exclude_internal_props: Yt,
  get_all_dirty_from_scope: uo,
  get_slot_changes: fo,
  group_outros: po,
  init: mo,
  insert_hydration: De,
  safe_not_equal: go,
  set_custom_element_data: jn,
  space: ho,
  transition_in: Ne,
  transition_out: wt,
  update_slot_base: vo
} = window.__gradio__svelte__internal, {
  beforeUpdate: bo,
  getContext: yo,
  onDestroy: So,
  setContext: xo
} = window.__gradio__svelte__internal;
function Jt(e) {
  let t, n;
  const r = (
    /*#slots*/
    e[7].default
  ), o = co(
    r,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = Fn("svelte-slot"), o && o.c(), this.h();
    },
    l(i) {
      t = kn(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = An(t);
      o && o.l(s), s.forEach(pe), this.h();
    },
    h() {
      jn(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      De(i, t, s), o && o.m(t, null), e[9](t), n = !0;
    },
    p(i, s) {
      o && o.p && (!n || s & /*$$scope*/
      64) && vo(
        o,
        r,
        i,
        /*$$scope*/
        i[6],
        n ? fo(
          r,
          /*$$scope*/
          i[6],
          s,
          null
        ) : uo(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      n || (Ne(o, i), n = !0);
    },
    o(i) {
      wt(o, i), n = !1;
    },
    d(i) {
      i && pe(t), o && o.d(i), e[9](null);
    }
  };
}
function wo(e) {
  let t, n, r, o, i = (
    /*$$slots*/
    e[4].default && Jt(e)
  );
  return {
    c() {
      t = Fn("react-portal-target"), n = ho(), i && i.c(), r = Qt(), this.h();
    },
    l(s) {
      t = kn(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), An(t).forEach(pe), n = ao(s), i && i.l(s), r = Qt(), this.h();
    },
    h() {
      jn(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      De(s, t, a), e[8](t), De(s, n, a), i && i.m(s, a), De(s, r, a), o = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && Ne(i, 1)) : (i = Jt(s), i.c(), Ne(i, 1), i.m(r.parentNode, r)) : i && (po(), wt(i, 1, 1, () => {
        i = null;
      }), so());
    },
    i(s) {
      o || (Ne(i), o = !0);
    },
    o(s) {
      wt(i), o = !1;
    },
    d(s) {
      s && (pe(t), pe(n), pe(r)), e[8](null), i && i.d(s);
    }
  };
}
function en(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function Eo(e, t, n) {
  let r, o, {
    $$slots: i = {},
    $$scope: s
  } = t;
  const a = lo(i);
  let {
    svelteInit: u
  } = t;
  const c = je(en(t)), d = je();
  Zt(e, d, (S) => n(0, r = S));
  const f = je();
  Zt(e, f, (S) => n(1, o = S));
  const p = [], m = yo("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: h,
    subSlotIndex: g
  } = yr() || {}, x = u({
    parent: m,
    props: c,
    target: d,
    slot: f,
    slotKey: b,
    slotIndex: h,
    subSlotIndex: g,
    onDestroy(S) {
      p.push(S);
    }
  });
  xo("$$ms-gr-react-wrapper", x), bo(() => {
    c.set(en(t));
  }), So(() => {
    p.forEach((S) => S());
  });
  function w(S) {
    Kt[S ? "unshift" : "push"](() => {
      r = S, d.set(r);
    });
  }
  function y(S) {
    Kt[S ? "unshift" : "push"](() => {
      o = S, f.set(o);
    });
  }
  return e.$$set = (S) => {
    n(17, t = qt(qt({}, t), Yt(S))), "svelteInit" in S && n(5, u = S.svelteInit), "$$scope" in S && n(6, s = S.$$scope);
  }, t = Yt(t), [r, o, d, f, a, u, s, i, w, y];
}
class Co extends io {
  constructor(t) {
    super(), mo(this, t, Eo, wo, go, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ys
} = window.__gradio__svelte__internal, tn = window.ms_globals.rerender, dt = window.ms_globals.tree;
function _o(e, t = {}) {
  function n(r) {
    const o = je(), i = new Co({
      ...r,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: e,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, u = s.parent ?? dt;
          return u.nodes = [...u.nodes, a], tn({
            createPortal: ze,
            node: dt
          }), s.onDestroy(() => {
            u.nodes = u.nodes.filter((c) => c.svelteInstance !== o), tn({
              createPortal: ze,
              node: dt
            });
          }), a;
        },
        ...r.props
      }
    });
    return o.set(i), i;
  }
  return new Promise((r) => {
    window.ms_globals.initializePromise.then(() => {
      r(n);
    });
  });
}
const Ro = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function To(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const r = e[n];
    return t[n] = Po(n, r), t;
  }, {}) : {};
}
function Po(e, t) {
  return typeof t == "number" && !Ro.includes(e) ? t + "px" : t;
}
function Et(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const o = l.Children.toArray(e._reactElement.props.children).map((i) => {
      if (l.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = Et(i.props.el);
        return l.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...l.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(ze(l.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: s,
      type: a,
      useCapture: u
    }) => {
      n.addEventListener(a, s, u);
    });
  });
  const r = Array.from(e.childNodes);
  for (let o = 0; o < r.length; o++) {
    const i = r[o];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = Et(i);
      t.push(...a), n.appendChild(s);
    } else i.nodeType === 3 && n.appendChild(i.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function Lo(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const me = dr(({
  slot: e,
  clone: t,
  className: n,
  style: r,
  observeAttributes: o
}, i) => {
  const s = le(), [a, u] = pr([]), {
    forceClone: c
  } = xr(), d = c ? !0 : t;
  return we(() => {
    var h;
    if (!s.current || !e)
      return;
    let f = e;
    function p() {
      let g = f;
      if (f.tagName.toLowerCase() === "svelte-slot" && f.children.length === 1 && f.children[0] && (g = f.children[0], g.tagName.toLowerCase() === "react-portal-target" && g.children[0] && (g = g.children[0])), Lo(i, g), n && g.classList.add(...n.split(" ")), r) {
        const x = To(r);
        Object.keys(x).forEach((w) => {
          g.style[w] = x[w];
        });
      }
    }
    let m = null, b = null;
    if (d && window.MutationObserver) {
      let g = function() {
        var S, _, v;
        (S = s.current) != null && S.contains(f) && ((_ = s.current) == null || _.removeChild(f));
        const {
          portals: w,
          clonedElement: y
        } = Et(e);
        f = y, u(w), f.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          p();
        }, 50), (v = s.current) == null || v.appendChild(f);
      };
      g();
      const x = Yr(() => {
        g(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      m = new window.MutationObserver(x), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      f.style.display = "contents", p(), (h = s.current) == null || h.appendChild(f);
    return () => {
      var g, x;
      f.style.display = "", (g = s.current) != null && g.contains(f) && ((x = s.current) == null || x.removeChild(f)), m == null || m.disconnect();
    };
  }, [e, d, n, r, i, o, c]), l.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
});
function Mo(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function Io(e, t = !1) {
  try {
    if (Sr(e))
      return e;
    if (t && !Mo(e))
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
function pt(e, t) {
  return Ln(() => Io(e, t), [e, t]);
}
function Oo(e, t) {
  return Object.keys(e).reduce((n, r) => (e[r] !== void 0 && (n[r] = e[r]), n), {});
}
const $o = ({
  children: e,
  ...t
}) => /* @__PURE__ */ V.jsx(V.Fragment, {
  children: e(t)
});
function Ao(e) {
  return l.createElement($o, {
    children: e
  });
}
function nn(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? Ao((n) => /* @__PURE__ */ V.jsx(wr, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ V.jsx(me, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...n
    })
  })) : /* @__PURE__ */ V.jsx(me, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function rn({
  key: e,
  slots: t,
  targets: n
}, r) {
  return t[e] ? (...o) => n ? n.map((i, s) => /* @__PURE__ */ V.jsx(l.Fragment, {
    children: nn(i, {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }, s)) : /* @__PURE__ */ V.jsx(V.Fragment, {
    children: nn(t[e], {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }) : void 0;
}
const ko = "1.6.0";
function ve() {
  return ve = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var n = arguments[t];
      for (var r in n) ({}).hasOwnProperty.call(n, r) && (e[r] = n[r]);
    }
    return e;
  }, ve.apply(null, arguments);
}
function U(e) {
  "@babel/helpers - typeof";
  return U = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, U(e);
}
function Fo(e, t) {
  if (U(e) != "object" || !e) return e;
  var n = e[Symbol.toPrimitive];
  if (n !== void 0) {
    var r = n.call(e, t);
    if (U(r) != "object") return r;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function Dn(e) {
  var t = Fo(e, "string");
  return U(t) == "symbol" ? t : t + "";
}
function T(e, t, n) {
  return (t = Dn(t)) in e ? Object.defineProperty(e, t, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = n, e;
}
function on(e, t) {
  var n = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var r = Object.getOwnPropertySymbols(e);
    t && (r = r.filter(function(o) {
      return Object.getOwnPropertyDescriptor(e, o).enumerable;
    })), n.push.apply(n, r);
  }
  return n;
}
function R(e) {
  for (var t = 1; t < arguments.length; t++) {
    var n = arguments[t] != null ? arguments[t] : {};
    t % 2 ? on(Object(n), !0).forEach(function(r) {
      T(e, r, n[r]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : on(Object(n)).forEach(function(r) {
      Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(n, r));
    });
  }
  return e;
}
const jo = /* @__PURE__ */ l.createContext({}), Do = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, No = (e) => {
  const t = l.useContext(jo);
  return l.useMemo(() => ({
    ...Do,
    ...t[e]
  }), [t[e]]);
};
function Ve() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: r,
    theme: o
  } = l.useContext(Er.ConfigContext);
  return {
    theme: o,
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: r
  };
}
function Ho(e) {
  if (Array.isArray(e)) return e;
}
function zo(e, t) {
  var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (n != null) {
    var r, o, i, s, a = [], u = !0, c = !1;
    try {
      if (i = (n = n.call(e)).next, t === 0) {
        if (Object(n) !== n) return;
        u = !1;
      } else for (; !(u = (r = i.call(n)).done) && (a.push(r.value), a.length !== t); u = !0) ;
    } catch (d) {
      c = !0, o = d;
    } finally {
      try {
        if (!u && n.return != null && (s = n.return(), Object(s) !== s)) return;
      } finally {
        if (c) throw o;
      }
    }
    return a;
  }
}
function sn(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
  return r;
}
function Bo(e, t) {
  if (e) {
    if (typeof e == "string") return sn(e, t);
    var n = {}.toString.call(e).slice(8, -1);
    return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? sn(e, t) : void 0;
  }
}
function Vo() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function G(e, t) {
  return Ho(e) || zo(e, t) || Bo(e, t) || Vo();
}
function ye(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function an(e, t) {
  for (var n = 0; n < t.length; n++) {
    var r = t[n];
    r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, Dn(r.key), r);
  }
}
function Se(e, t, n) {
  return t && an(e.prototype, t), n && an(e, n), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function fe(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function Ct(e, t) {
  return Ct = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, r) {
    return n.__proto__ = r, n;
  }, Ct(e, t);
}
function We(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && Ct(e, t);
}
function Ue(e) {
  return Ue = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, Ue(e);
}
function Nn() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Nn = function() {
    return !!e;
  })();
}
function Uo(e, t) {
  if (t && (U(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return fe(e);
}
function Ge(e) {
  var t = Nn();
  return function() {
    var n, r = Ue(e);
    if (t) {
      var o = Ue(this).constructor;
      n = Reflect.construct(r, arguments, o);
    } else n = r.apply(this, arguments);
    return Uo(this, n);
  };
}
var Hn = /* @__PURE__ */ Se(function e() {
  ye(this, e);
}), zn = "CALC_UNIT", Xo = new RegExp(zn, "g");
function mt(e) {
  return typeof e == "number" ? "".concat(e).concat(zn) : e;
}
var Wo = /* @__PURE__ */ function(e) {
  We(n, e);
  var t = Ge(n);
  function n(r, o) {
    var i;
    ye(this, n), i = t.call(this), T(fe(i), "result", ""), T(fe(i), "unitlessCssVar", void 0), T(fe(i), "lowPriority", void 0);
    var s = U(r);
    return i.unitlessCssVar = o, r instanceof n ? i.result = "(".concat(r.result, ")") : s === "number" ? i.result = mt(r) : s === "string" && (i.result = r), i;
  }
  return Se(n, [{
    key: "add",
    value: function(o) {
      return o instanceof n ? this.result = "".concat(this.result, " + ").concat(o.getResult()) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " + ").concat(mt(o))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(o) {
      return o instanceof n ? this.result = "".concat(this.result, " - ").concat(o.getResult()) : (typeof o == "number" || typeof o == "string") && (this.result = "".concat(this.result, " - ").concat(mt(o))), this.lowPriority = !0, this;
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
      var i = this, s = o || {}, a = s.unit, u = !0;
      return typeof a == "boolean" ? u = a : Array.from(this.unitlessCssVar).some(function(c) {
        return i.result.includes(c);
      }) && (u = !1), this.result = this.result.replace(Xo, u ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(Hn), Go = /* @__PURE__ */ function(e) {
  We(n, e);
  var t = Ge(n);
  function n(r) {
    var o;
    return ye(this, n), o = t.call(this), T(fe(o), "result", 0), r instanceof n ? o.result = r.result : typeof r == "number" && (o.result = r), o;
  }
  return Se(n, [{
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
}(Hn), qo = function(t, n) {
  var r = t === "css" ? Wo : Go;
  return function(o) {
    return new r(o, n);
  };
}, ln = function(t, n) {
  return "".concat([n, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function be(e) {
  var t = O.useRef();
  t.current = e;
  var n = O.useCallback(function() {
    for (var r, o = arguments.length, i = new Array(o), s = 0; s < o; s++)
      i[s] = arguments[s];
    return (r = t.current) === null || r === void 0 ? void 0 : r.call.apply(r, [t].concat(i));
  }, []);
  return n;
}
function qe() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var cn = qe() ? O.useLayoutEffect : O.useEffect, Ko = function(t, n) {
  var r = O.useRef(!0);
  cn(function() {
    return t(r.current);
  }, n), cn(function() {
    return r.current = !1, function() {
      r.current = !0;
    };
  }, []);
}, un = function(t, n) {
  Ko(function(r) {
    if (!r)
      return t();
  }, n);
};
function Ee(e) {
  var t = O.useRef(!1), n = O.useState(e), r = G(n, 2), o = r[0], i = r[1];
  O.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function s(a, u) {
    u && t.current || i(a);
  }
  return [o, s];
}
function gt(e) {
  return e !== void 0;
}
function Zo(e, t) {
  var n = t || {}, r = n.defaultValue, o = n.value, i = n.onChange, s = n.postState, a = Ee(function() {
    return gt(o) ? o : gt(r) ? typeof r == "function" ? r() : r : typeof e == "function" ? e() : e;
  }), u = G(a, 2), c = u[0], d = u[1], f = o !== void 0 ? o : c, p = s ? s(f) : f, m = be(i), b = Ee([f]), h = G(b, 2), g = h[0], x = h[1];
  un(function() {
    var y = g[0];
    c !== y && m(c, y);
  }, [g]), un(function() {
    gt(o) || d(o);
  }, [o]);
  var w = be(function(y, S) {
    d(y, S), x([f], S);
  });
  return [p, w];
}
var Bn = {
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
var Ot = Symbol.for("react.element"), $t = Symbol.for("react.portal"), Ke = Symbol.for("react.fragment"), Ze = Symbol.for("react.strict_mode"), Qe = Symbol.for("react.profiler"), Ye = Symbol.for("react.provider"), Je = Symbol.for("react.context"), Qo = Symbol.for("react.server_context"), et = Symbol.for("react.forward_ref"), tt = Symbol.for("react.suspense"), nt = Symbol.for("react.suspense_list"), rt = Symbol.for("react.memo"), ot = Symbol.for("react.lazy"), Yo = Symbol.for("react.offscreen"), Vn;
Vn = Symbol.for("react.module.reference");
function J(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case Ot:
        switch (e = e.type, e) {
          case Ke:
          case Qe:
          case Ze:
          case tt:
          case nt:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case Qo:
              case Je:
              case et:
              case ot:
              case rt:
              case Ye:
                return e;
              default:
                return t;
            }
        }
      case $t:
        return t;
    }
  }
}
$.ContextConsumer = Je;
$.ContextProvider = Ye;
$.Element = Ot;
$.ForwardRef = et;
$.Fragment = Ke;
$.Lazy = ot;
$.Memo = rt;
$.Portal = $t;
$.Profiler = Qe;
$.StrictMode = Ze;
$.Suspense = tt;
$.SuspenseList = nt;
$.isAsyncMode = function() {
  return !1;
};
$.isConcurrentMode = function() {
  return !1;
};
$.isContextConsumer = function(e) {
  return J(e) === Je;
};
$.isContextProvider = function(e) {
  return J(e) === Ye;
};
$.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === Ot;
};
$.isForwardRef = function(e) {
  return J(e) === et;
};
$.isFragment = function(e) {
  return J(e) === Ke;
};
$.isLazy = function(e) {
  return J(e) === ot;
};
$.isMemo = function(e) {
  return J(e) === rt;
};
$.isPortal = function(e) {
  return J(e) === $t;
};
$.isProfiler = function(e) {
  return J(e) === Qe;
};
$.isStrictMode = function(e) {
  return J(e) === Ze;
};
$.isSuspense = function(e) {
  return J(e) === tt;
};
$.isSuspenseList = function(e) {
  return J(e) === nt;
};
$.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === Ke || e === Qe || e === Ze || e === tt || e === nt || e === Yo || typeof e == "object" && e !== null && (e.$$typeof === ot || e.$$typeof === rt || e.$$typeof === Ye || e.$$typeof === Je || e.$$typeof === et || e.$$typeof === Vn || e.getModuleId !== void 0);
};
$.typeOf = J;
Bn.exports = $;
var ht = Bn.exports, Jo = Symbol.for("react.element"), ei = Symbol.for("react.transitional.element"), ti = Symbol.for("react.fragment");
function ni(e) {
  return (
    // Base object type
    e && U(e) === "object" && // React Element type
    (e.$$typeof === Jo || e.$$typeof === ei) && // React Fragment type
    e.type === ti
  );
}
var ri = Number(mr.split(".")[0]), oi = function(t, n) {
  typeof t == "function" ? t(n) : U(t) === "object" && t && "current" in t && (t.current = n);
}, ii = function(t) {
  var n, r;
  if (!t)
    return !1;
  if (Un(t) && ri >= 19)
    return !0;
  var o = ht.isMemo(t) ? t.type.type : t.type;
  return !(typeof o == "function" && !((n = o.prototype) !== null && n !== void 0 && n.render) && o.$$typeof !== ht.ForwardRef || typeof t == "function" && !((r = t.prototype) !== null && r !== void 0 && r.render) && t.$$typeof !== ht.ForwardRef);
};
function Un(e) {
  return /* @__PURE__ */ gr(e) && !ni(e);
}
var si = function(t) {
  if (t && Un(t)) {
    var n = t;
    return n.props.propertyIsEnumerable("ref") ? n.props.ref : n.ref;
  }
  return null;
};
function fn(e, t, n, r) {
  var o = R({}, t[e]);
  if (r != null && r.deprecatedTokens) {
    var i = r.deprecatedTokens;
    i.forEach(function(a) {
      var u = G(a, 2), c = u[0], d = u[1];
      if (o != null && o[c] || o != null && o[d]) {
        var f;
        (f = o[d]) !== null && f !== void 0 || (o[d] = o == null ? void 0 : o[c]);
      }
    });
  }
  var s = R(R({}, n), o);
  return Object.keys(s).forEach(function(a) {
    s[a] === t[a] && delete s[a];
  }), s;
}
var Xn = typeof CSSINJS_STATISTIC < "u", _t = !0;
function At() {
  for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++)
    t[n] = arguments[n];
  if (!Xn)
    return Object.assign.apply(Object, [{}].concat(t));
  _t = !1;
  var r = {};
  return t.forEach(function(o) {
    if (U(o) === "object") {
      var i = Object.keys(o);
      i.forEach(function(s) {
        Object.defineProperty(r, s, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return o[s];
          }
        });
      });
    }
  }), _t = !0, r;
}
var dn = {};
function ai() {
}
var li = function(t) {
  var n, r = t, o = ai;
  return Xn && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), r = new Proxy(t, {
    get: function(s, a) {
      if (_t) {
        var u;
        (u = n) === null || u === void 0 || u.add(a);
      }
      return s[a];
    }
  }), o = function(s, a) {
    var u;
    dn[s] = {
      global: Array.from(n),
      component: R(R({}, (u = dn[s]) === null || u === void 0 ? void 0 : u.component), a)
    };
  }), {
    token: r,
    keys: n,
    flush: o
  };
};
function pn(e, t, n) {
  if (typeof n == "function") {
    var r;
    return n(At(t, (r = t[e]) !== null && r !== void 0 ? r : {}));
  }
  return n ?? {};
}
function ci(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, r = new Array(n), o = 0; o < n; o++)
        r[o] = arguments[o];
      return "max(".concat(r.map(function(i) {
        return Ut(i);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, r = new Array(n), o = 0; o < n; o++)
        r[o] = arguments[o];
      return "min(".concat(r.map(function(i) {
        return Ut(i);
      }).join(","), ")");
    }
  };
}
var ui = 1e3 * 60 * 10, fi = /* @__PURE__ */ function() {
  function e() {
    ye(this, e), T(this, "map", /* @__PURE__ */ new Map()), T(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), T(this, "nextID", 0), T(this, "lastAccessBeat", /* @__PURE__ */ new Map()), T(this, "accessBeat", 0);
  }
  return Se(e, [{
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
      var r = this, o = n.map(function(i) {
        return i && U(i) === "object" ? "obj_".concat(r.getObjectID(i)) : "".concat(U(i), "_").concat(i);
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
        this.lastAccessBeat.forEach(function(o, i) {
          r - o > ui && (n.map.delete(i), n.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), mn = new fi();
function di(e, t) {
  return l.useMemo(function() {
    var n = mn.get(t);
    if (n)
      return n;
    var r = e();
    return mn.set(t, r), r;
  }, t);
}
var pi = function() {
  return {};
};
function mi(e) {
  var t = e.useCSP, n = t === void 0 ? pi : t, r = e.useToken, o = e.usePrefix, i = e.getResetStyles, s = e.getCommonStyle, a = e.getCompUnitless;
  function u(p, m, b, h) {
    var g = Array.isArray(p) ? p[0] : p;
    function x(C) {
      return "".concat(String(g)).concat(C.slice(0, 1).toUpperCase()).concat(C.slice(1));
    }
    var w = (h == null ? void 0 : h.unitless) || {}, y = typeof a == "function" ? a(p) : {}, S = R(R({}, y), {}, T({}, x("zIndexPopup"), !0));
    Object.keys(w).forEach(function(C) {
      S[x(C)] = w[C];
    });
    var _ = R(R({}, h), {}, {
      unitless: S,
      prefixToken: x
    }), v = d(p, m, b, _), P = c(g, b, _);
    return function(C) {
      var I = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : C, E = v(C, I), L = G(E, 2), M = L[1], A = P(I), F = G(A, 2), k = F[0], N = F[1];
      return [k, M, N];
    };
  }
  function c(p, m, b) {
    var h = b.unitless, g = b.injectStyle, x = g === void 0 ? !0 : g, w = b.prefixToken, y = b.ignore, S = function(P) {
      var C = P.rootCls, I = P.cssVar, E = I === void 0 ? {} : I, L = r(), M = L.realToken;
      return Dr({
        path: [p],
        prefix: E.prefix,
        key: E.key,
        unitless: h,
        ignore: y,
        token: M,
        scope: C
      }, function() {
        var A = pn(p, M, m), F = fn(p, M, A, {
          deprecatedTokens: b == null ? void 0 : b.deprecatedTokens
        });
        return Object.keys(A).forEach(function(k) {
          F[w(k)] = F[k], delete F[k];
        }), F;
      }), null;
    }, _ = function(P) {
      var C = r(), I = C.cssVar;
      return [function(E) {
        return x && I ? /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(S, {
          rootCls: P,
          cssVar: I,
          component: p
        }), E) : E;
      }, I == null ? void 0 : I.key];
    };
    return _;
  }
  function d(p, m, b) {
    var h = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = Array.isArray(p) ? p : [p, p], x = G(g, 1), w = x[0], y = g.join("-"), S = e.layer || {
      name: "antd"
    };
    return function(_) {
      var v = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : _, P = r(), C = P.theme, I = P.realToken, E = P.hashId, L = P.token, M = P.cssVar, A = o(), F = A.rootPrefixCls, k = A.iconPrefixCls, N = n(), Q = M ? "css" : "js", j = di(function() {
        var D = /* @__PURE__ */ new Set();
        return M && Object.keys(h.unitless || {}).forEach(function(q) {
          D.add(ut(q, M.prefix)), D.add(ut(q, ln(w, M.prefix)));
        }), qo(Q, D);
      }, [Q, w, M == null ? void 0 : M.prefix]), z = ci(Q), se = z.max, X = z.min, ee = {
        theme: C,
        token: L,
        hashId: E,
        nonce: function() {
          return N.nonce;
        },
        clientOnly: h.clientOnly,
        layer: S,
        // antd is always at top of styles
        order: h.order || -999
      };
      typeof i == "function" && Xt(R(R({}, ee), {}, {
        clientOnly: !1,
        path: ["Shared", F]
      }), function() {
        return i(L, {
          prefix: {
            rootPrefixCls: F,
            iconPrefixCls: k
          },
          csp: N
        });
      });
      var H = Xt(R(R({}, ee), {}, {
        path: [y, _, k]
      }), function() {
        if (h.injectStyle === !1)
          return [];
        var D = li(L), q = D.token, te = D.flush, Y = pn(w, I, b), it = ".".concat(_), _e = fn(w, I, Y, {
          deprecatedTokens: h.deprecatedTokens
        });
        M && Y && U(Y) === "object" && Object.keys(Y).forEach(function(Pe) {
          Y[Pe] = "var(".concat(ut(Pe, ln(w, M.prefix)), ")");
        });
        var Re = At(q, {
          componentCls: it,
          prefixCls: _,
          iconCls: ".".concat(k),
          antCls: ".".concat(F),
          calc: j,
          // @ts-ignore
          max: se,
          // @ts-ignore
          min: X
        }, M ? Y : _e), Te = m(Re, {
          hashId: E,
          prefixCls: _,
          rootPrefixCls: F,
          iconPrefixCls: k
        });
        te(w, _e);
        var ce = typeof s == "function" ? s(Re, _, v, h.resetFont) : null;
        return [h.resetStyle === !1 ? null : ce, Te];
      });
      return [H, E];
    };
  }
  function f(p, m, b) {
    var h = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, g = d(p, m, b, R({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, h)), x = function(y) {
      var S = y.prefixCls, _ = y.rootCls, v = _ === void 0 ? S : _;
      return g(S, v), null;
    };
    return x;
  }
  return {
    genStyleHooks: u,
    genSubStyleComponent: f,
    genComponentStyleHook: d
  };
}
const gi = {
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
}, hi = Object.assign(Object.assign({}, gi), {
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
function vt(e, t) {
  const n = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], r = n.map((o) => parseFloat(o));
  for (let o = 0; o < 3; o += 1)
    r[o] = t(r[o] || 0, n[o] || "", o);
  return n[3] ? r[3] = n[3].includes("%") ? r[3] / 100 : r[3] : r[3] = 1, r;
}
const gn = (e, t, n) => n === 0 ? e : e / 100;
function xe(e, t) {
  const n = t || 255;
  return e > n ? n : e < 0 ? 0 : e;
}
class oe {
  constructor(t) {
    T(this, "isValid", !0), T(this, "r", 0), T(this, "g", 0), T(this, "b", 0), T(this, "a", 1), T(this, "_h", void 0), T(this, "_s", void 0), T(this, "_l", void 0), T(this, "_v", void 0), T(this, "_max", void 0), T(this, "_min", void 0), T(this, "_brightness", void 0);
    function n(r) {
      return r[0] in t && r[1] in t && r[2] in t;
    }
    if (t) if (typeof t == "string") {
      let o = function(i) {
        return r.startsWith(i);
      };
      const r = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(r) ? this.fromHexString(r) : o("rgb") ? this.fromRgbString(r) : o("hsl") ? this.fromHslString(r) : (o("hsv") || o("hsb")) && this.fromHsvString(r);
    } else if (t instanceof oe)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (n("rgb"))
      this.r = xe(t.r), this.g = xe(t.g), this.b = xe(t.b), this.a = typeof t.a == "number" ? xe(t.a, 1) : 1;
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
    const n = t(this.r), r = t(this.g), o = t(this.b);
    return 0.2126 * n + 0.7152 * r + 0.0722 * o;
  }
  getHue() {
    if (typeof this._h > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._h = 0 : this._h = B(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
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
    const r = this._c(t), o = n / 100, i = (a) => (r[a] - this[a]) * o + this[a], s = {
      r: B(i("r")),
      g: B(i("g")),
      b: B(i("b")),
      a: B(i("a") * 100) / 100
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
    const n = this._c(t), r = this.a + n.a * (1 - this.a), o = (i) => B((this[i] * this.a + n[i] * n.a * (1 - this.a)) / r);
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
      const i = B(this.a * 255).toString(16);
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
    const t = this.getHue(), n = B(this.getSaturation() * 100), r = B(this.getLightness() * 100);
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
    return o[t] = xe(n, r), o;
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
    function r(o, i) {
      return parseInt(n[o] + n[i || o], 16);
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
      const p = B(r * 255);
      this.r = p, this.g = p, this.b = p;
    }
    let i = 0, s = 0, a = 0;
    const u = t / 60, c = (1 - Math.abs(2 * r - 1)) * n, d = c * (1 - Math.abs(u % 2 - 1));
    u >= 0 && u < 1 ? (i = c, s = d) : u >= 1 && u < 2 ? (i = d, s = c) : u >= 2 && u < 3 ? (s = c, a = d) : u >= 3 && u < 4 ? (s = d, a = c) : u >= 4 && u < 5 ? (i = d, a = c) : u >= 5 && u < 6 && (i = c, a = d);
    const f = r - c / 2;
    this.r = B((i + f) * 255), this.g = B((s + f) * 255), this.b = B((a + f) * 255);
  }
  fromHsv({
    h: t,
    s: n,
    v: r,
    a: o
  }) {
    this._h = t % 360, this._s = n, this._v = r, this.a = typeof o == "number" ? o : 1;
    const i = B(r * 255);
    if (this.r = i, this.g = i, this.b = i, n <= 0)
      return;
    const s = t / 60, a = Math.floor(s), u = s - a, c = B(r * (1 - n) * 255), d = B(r * (1 - n * u) * 255), f = B(r * (1 - n * (1 - u)) * 255);
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
  fromHsvString(t) {
    const n = vt(t, gn);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(t) {
    const n = vt(t, gn);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(t) {
    const n = vt(t, (r, o) => (
      // Convert percentage to number. e.g. 50% -> 128
      o.includes("%") ? B(r / 100 * 255) : r
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function bt(e) {
  return e >= 0 && e <= 255;
}
function Ie(e, t) {
  const {
    r: n,
    g: r,
    b: o,
    a: i
  } = new oe(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: s,
    g: a,
    b: u
  } = new oe(t).toRgb();
  for (let c = 0.01; c <= 1; c += 0.01) {
    const d = Math.round((n - s * (1 - c)) / c), f = Math.round((r - a * (1 - c)) / c), p = Math.round((o - u * (1 - c)) / c);
    if (bt(d) && bt(f) && bt(p))
      return new oe({
        r: d,
        g: f,
        b: p,
        a: Math.round(c * 100) / 100
      }).toRgbString();
  }
  return new oe({
    r: n,
    g: r,
    b: o,
    a: 1
  }).toRgbString();
}
var vi = function(e, t) {
  var n = {};
  for (var r in e) Object.prototype.hasOwnProperty.call(e, r) && t.indexOf(r) < 0 && (n[r] = e[r]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var o = 0, r = Object.getOwnPropertySymbols(e); o < r.length; o++)
    t.indexOf(r[o]) < 0 && Object.prototype.propertyIsEnumerable.call(e, r[o]) && (n[r[o]] = e[r[o]]);
  return n;
};
function bi(e) {
  const {
    override: t
  } = e, n = vi(e, ["override"]), r = Object.assign({}, t);
  Object.keys(hi).forEach((p) => {
    delete r[p];
  });
  const o = Object.assign(Object.assign({}, n), r), i = 480, s = 576, a = 768, u = 992, c = 1200, d = 1600;
  if (o.motion === !1) {
    const p = "0s";
    o.motionDurationFast = p, o.motionDurationMid = p, o.motionDurationSlow = p;
  }
  return Object.assign(Object.assign(Object.assign({}, o), {
    // ============== Background ============== //
    colorFillContent: o.colorFillSecondary,
    colorFillContentHover: o.colorFill,
    colorFillAlter: o.colorFillQuaternary,
    colorBgContainerDisabled: o.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: o.colorBgContainer,
    colorSplit: Ie(o.colorBorderSecondary, o.colorBgContainer),
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
    colorErrorOutline: Ie(o.colorErrorBg, o.colorBgContainer),
    colorWarningOutline: Ie(o.colorWarningBg, o.colorBgContainer),
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
    controlOutline: Ie(o.colorPrimaryBg, o.colorBgContainer),
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
    screenXS: i,
    screenXSMin: i,
    screenXSMax: s - 1,
    screenSM: s,
    screenSMMin: s,
    screenSMMax: a - 1,
    screenMD: a,
    screenMDMin: a,
    screenMDMax: u - 1,
    screenLG: u,
    screenLGMin: u,
    screenLGMax: c - 1,
    screenXL: c,
    screenXLMin: c,
    screenXLMax: d - 1,
    screenXXL: d,
    screenXXLMin: d,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new oe("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new oe("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new oe("rgba(0, 0, 0, 0.09)").toRgbString()}
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
const yi = {
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
}, Si = {
  motionBase: !0,
  motionUnit: !0
}, xi = Nr(Be.defaultAlgorithm), wi = {
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
}, Wn = (e, t, n) => {
  const r = n.getDerivativeToken(e), {
    override: o,
    ...i
  } = t;
  let s = {
    ...r,
    override: o
  };
  return s = bi(s), i && Object.entries(i).forEach(([a, u]) => {
    const {
      theme: c,
      ...d
    } = u;
    let f = d;
    c && (f = Wn({
      ...s,
      ...d
    }, {
      override: d
    }, c)), s[a] = f;
  }), s;
};
function Ei() {
  const {
    token: e,
    hashed: t,
    theme: n = xi,
    override: r,
    cssVar: o
  } = l.useContext(Be._internalContext), [i, s, a] = Hr(n, [Be.defaultSeed, e], {
    salt: `${ko}-${t || ""}`,
    override: r,
    getComputedToken: Wn,
    cssVar: o && {
      prefix: o.prefix,
      key: o.key,
      unitless: yi,
      ignore: Si,
      preserve: wi
    }
  });
  return [n, a, t ? s : "", i, o];
}
const {
  genStyleHooks: Ci
} = mi({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = Ve();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, n, r, o] = Ei();
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
    } = Ve();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
}), Ce = /* @__PURE__ */ l.createContext(null);
function hn(e) {
  const {
    getDropContainer: t,
    className: n,
    prefixCls: r,
    children: o
  } = e, {
    disabled: i
  } = l.useContext(Ce), [s, a] = l.useState(), [u, c] = l.useState(null);
  if (l.useEffect(() => {
    const p = t == null ? void 0 : t();
    s !== p && a(p);
  }, [t]), l.useEffect(() => {
    if (s) {
      const p = () => {
        c(!0);
      }, m = (g) => {
        g.preventDefault();
      }, b = (g) => {
        g.relatedTarget || c(!1);
      }, h = (g) => {
        c(!1), g.preventDefault();
      };
      return document.addEventListener("dragenter", p), document.addEventListener("dragover", m), document.addEventListener("dragleave", b), document.addEventListener("drop", h), () => {
        document.removeEventListener("dragenter", p), document.removeEventListener("dragover", m), document.removeEventListener("dragleave", b), document.removeEventListener("drop", h);
      };
    }
  }, [!!s]), !(t && s && !i))
    return null;
  const f = `${r}-drop-area`;
  return /* @__PURE__ */ ze(/* @__PURE__ */ l.createElement("div", {
    className: Z(f, n, {
      [`${f}-on-body`]: s.tagName === "BODY"
    }),
    style: {
      display: u ? "block" : "none"
    }
  }, o), s);
}
function vn(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function _i(e) {
  return e && U(e) === "object" && vn(e.nativeElement) ? e.nativeElement : vn(e) ? e : null;
}
function Ri(e) {
  var t = _i(e);
  if (t)
    return t;
  if (e instanceof l.Component) {
    var n;
    return (n = Vt.findDOMNode) === null || n === void 0 ? void 0 : n.call(Vt, e);
  }
  return null;
}
function Ti(e, t) {
  if (e == null) return {};
  var n = {};
  for (var r in e) if ({}.hasOwnProperty.call(e, r)) {
    if (t.indexOf(r) !== -1) continue;
    n[r] = e[r];
  }
  return n;
}
function bn(e, t) {
  if (e == null) return {};
  var n, r, o = Ti(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (r = 0; r < i.length; r++) n = i[r], t.indexOf(n) === -1 && {}.propertyIsEnumerable.call(e, n) && (o[n] = e[n]);
  }
  return o;
}
var Pi = /* @__PURE__ */ O.createContext({}), Li = /* @__PURE__ */ function(e) {
  We(n, e);
  var t = Ge(n);
  function n() {
    return ye(this, n), t.apply(this, arguments);
  }
  return Se(n, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), n;
}(O.Component);
function Mi(e) {
  var t = O.useReducer(function(a) {
    return a + 1;
  }, 0), n = G(t, 2), r = n[1], o = O.useRef(e), i = be(function() {
    return o.current;
  }), s = be(function(a) {
    o.current = typeof a == "function" ? a(o.current) : a, r();
  });
  return [i, s];
}
var ae = "none", Oe = "appear", $e = "enter", Ae = "leave", yn = "none", ne = "prepare", ge = "start", he = "active", kt = "end", Gn = "prepared";
function Sn(e, t) {
  var n = {};
  return n[e.toLowerCase()] = t.toLowerCase(), n["Webkit".concat(e)] = "webkit".concat(t), n["Moz".concat(e)] = "moz".concat(t), n["ms".concat(e)] = "MS".concat(t), n["O".concat(e)] = "o".concat(t.toLowerCase()), n;
}
function Ii(e, t) {
  var n = {
    animationend: Sn("Animation", "AnimationEnd"),
    transitionend: Sn("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete n.animationend.animation, "TransitionEvent" in t || delete n.transitionend.transition), n;
}
var Oi = Ii(qe(), typeof window < "u" ? window : {}), qn = {};
if (qe()) {
  var $i = document.createElement("div");
  qn = $i.style;
}
var ke = {};
function Kn(e) {
  if (ke[e])
    return ke[e];
  var t = Oi[e];
  if (t)
    for (var n = Object.keys(t), r = n.length, o = 0; o < r; o += 1) {
      var i = n[o];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in qn)
        return ke[e] = t[i], ke[e];
    }
  return "";
}
var Zn = Kn("animationend"), Qn = Kn("transitionend"), Yn = !!(Zn && Qn), xn = Zn || "animationend", wn = Qn || "transitionend";
function En(e, t) {
  if (!e) return null;
  if (U(e) === "object") {
    var n = t.replace(/-\w/g, function(r) {
      return r[1].toUpperCase();
    });
    return e[n];
  }
  return "".concat(e, "-").concat(t);
}
const Ai = function(e) {
  var t = le();
  function n(o) {
    o && (o.removeEventListener(wn, e), o.removeEventListener(xn, e));
  }
  function r(o) {
    t.current && t.current !== o && n(t.current), o && o !== t.current && (o.addEventListener(wn, e), o.addEventListener(xn, e), t.current = o);
  }
  return O.useEffect(function() {
    return function() {
      n(t.current);
    };
  }, []), [r, n];
};
var Jn = qe() ? hr : we, er = function(t) {
  return +setTimeout(t, 16);
}, tr = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (er = function(t) {
  return window.requestAnimationFrame(t);
}, tr = function(t) {
  return window.cancelAnimationFrame(t);
});
var Cn = 0, Ft = /* @__PURE__ */ new Map();
function nr(e) {
  Ft.delete(e);
}
var Rt = function(t) {
  var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  Cn += 1;
  var r = Cn;
  function o(i) {
    if (i === 0)
      nr(r), t();
    else {
      var s = er(function() {
        o(i - 1);
      });
      Ft.set(r, s);
    }
  }
  return o(n), r;
};
Rt.cancel = function(e) {
  var t = Ft.get(e);
  return nr(e), tr(t);
};
const ki = function() {
  var e = O.useRef(null);
  function t() {
    Rt.cancel(e.current);
  }
  function n(r) {
    var o = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = Rt(function() {
      o <= 1 ? r({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : n(r, o - 1);
    });
    e.current = i;
  }
  return O.useEffect(function() {
    return function() {
      t();
    };
  }, []), [n, t];
};
var Fi = [ne, ge, he, kt], ji = [ne, Gn], rr = !1, Di = !0;
function or(e) {
  return e === he || e === kt;
}
const Ni = function(e, t, n) {
  var r = Ee(yn), o = G(r, 2), i = o[0], s = o[1], a = ki(), u = G(a, 2), c = u[0], d = u[1];
  function f() {
    s(ne, !0);
  }
  var p = t ? ji : Fi;
  return Jn(function() {
    if (i !== yn && i !== kt) {
      var m = p.indexOf(i), b = p[m + 1], h = n(i);
      h === rr ? s(b, !0) : b && c(function(g) {
        function x() {
          g.isCanceled() || s(b, !0);
        }
        h === !0 ? x() : Promise.resolve(h).then(x);
      });
    }
  }, [e, i]), O.useEffect(function() {
    return function() {
      d();
    };
  }, []), [f, i];
};
function Hi(e, t, n, r) {
  var o = r.motionEnter, i = o === void 0 ? !0 : o, s = r.motionAppear, a = s === void 0 ? !0 : s, u = r.motionLeave, c = u === void 0 ? !0 : u, d = r.motionDeadline, f = r.motionLeaveImmediately, p = r.onAppearPrepare, m = r.onEnterPrepare, b = r.onLeavePrepare, h = r.onAppearStart, g = r.onEnterStart, x = r.onLeaveStart, w = r.onAppearActive, y = r.onEnterActive, S = r.onLeaveActive, _ = r.onAppearEnd, v = r.onEnterEnd, P = r.onLeaveEnd, C = r.onVisibleChanged, I = Ee(), E = G(I, 2), L = E[0], M = E[1], A = Mi(ae), F = G(A, 2), k = F[0], N = F[1], Q = Ee(null), j = G(Q, 2), z = j[0], se = j[1], X = k(), ee = le(!1), H = le(null);
  function D() {
    return n();
  }
  var q = le(!1);
  function te() {
    N(ae), se(null, !0);
  }
  var Y = be(function(K) {
    var W = k();
    if (W !== ae) {
      var re = D();
      if (!(K && !K.deadline && K.target !== re)) {
        var Le = q.current, Me;
        W === Oe && Le ? Me = _ == null ? void 0 : _(re, K) : W === $e && Le ? Me = v == null ? void 0 : v(re, K) : W === Ae && Le && (Me = P == null ? void 0 : P(re, K)), Le && Me !== !1 && te();
      }
    }
  }), it = Ai(Y), _e = G(it, 1), Re = _e[0], Te = function(W) {
    switch (W) {
      case Oe:
        return T(T(T({}, ne, p), ge, h), he, w);
      case $e:
        return T(T(T({}, ne, m), ge, g), he, y);
      case Ae:
        return T(T(T({}, ne, b), ge, x), he, S);
      default:
        return {};
    }
  }, ce = O.useMemo(function() {
    return Te(X);
  }, [X]), Pe = Ni(X, !e, function(K) {
    if (K === ne) {
      var W = ce[ne];
      return W ? W(D()) : rr;
    }
    if (ue in ce) {
      var re;
      se(((re = ce[ue]) === null || re === void 0 ? void 0 : re.call(ce, D(), null)) || null);
    }
    return ue === he && X !== ae && (Re(D()), d > 0 && (clearTimeout(H.current), H.current = setTimeout(function() {
      Y({
        deadline: !0
      });
    }, d))), ue === Gn && te(), Di;
  }), jt = G(Pe, 2), ur = jt[0], ue = jt[1], fr = or(ue);
  q.current = fr;
  var Dt = le(null);
  Jn(function() {
    if (!(ee.current && Dt.current === t)) {
      M(t);
      var K = ee.current;
      ee.current = !0;
      var W;
      !K && t && a && (W = Oe), K && t && i && (W = $e), (K && !t && c || !K && f && !t && c) && (W = Ae);
      var re = Te(W);
      W && (e || re[ne]) ? (N(W), ur()) : N(ae), Dt.current = t;
    }
  }, [t]), we(function() {
    // Cancel appear
    (X === Oe && !a || // Cancel enter
    X === $e && !i || // Cancel leave
    X === Ae && !c) && N(ae);
  }, [a, i, c]), we(function() {
    return function() {
      ee.current = !1, clearTimeout(H.current);
    };
  }, []);
  var st = O.useRef(!1);
  we(function() {
    L && (st.current = !0), L !== void 0 && X === ae && ((st.current || L) && (C == null || C(L)), st.current = !0);
  }, [L, X]);
  var at = z;
  return ce[ne] && ue === ge && (at = R({
    transition: "none"
  }, at)), [X, ue, at, L ?? t];
}
function zi(e) {
  var t = e;
  U(e) === "object" && (t = e.transitionSupport);
  function n(o, i) {
    return !!(o.motionName && t && i !== !1);
  }
  var r = /* @__PURE__ */ O.forwardRef(function(o, i) {
    var s = o.visible, a = s === void 0 ? !0 : s, u = o.removeOnLeave, c = u === void 0 ? !0 : u, d = o.forceRender, f = o.children, p = o.motionName, m = o.leavedClassName, b = o.eventProps, h = O.useContext(Pi), g = h.motion, x = n(o, g), w = le(), y = le();
    function S() {
      try {
        return w.current instanceof HTMLElement ? w.current : Ri(y.current);
      } catch {
        return null;
      }
    }
    var _ = Hi(x, a, S, o), v = G(_, 4), P = v[0], C = v[1], I = v[2], E = v[3], L = O.useRef(E);
    E && (L.current = !0);
    var M = O.useCallback(function(j) {
      w.current = j, oi(i, j);
    }, [i]), A, F = R(R({}, b), {}, {
      visible: a
    });
    if (!f)
      A = null;
    else if (P === ae)
      E ? A = f(R({}, F), M) : !c && L.current && m ? A = f(R(R({}, F), {}, {
        className: m
      }), M) : d || !c && !m ? A = f(R(R({}, F), {}, {
        style: {
          display: "none"
        }
      }), M) : A = null;
    else {
      var k;
      C === ne ? k = "prepare" : or(C) ? k = "active" : C === ge && (k = "start");
      var N = En(p, "".concat(P, "-").concat(k));
      A = f(R(R({}, F), {}, {
        className: Z(En(p, P), T(T({}, N, N && k), p, typeof p == "string")),
        style: I
      }), M);
    }
    if (/* @__PURE__ */ O.isValidElement(A) && ii(A)) {
      var Q = si(A);
      Q || (A = /* @__PURE__ */ O.cloneElement(A, {
        ref: M
      }));
    }
    return /* @__PURE__ */ O.createElement(Li, {
      ref: y
    }, A);
  });
  return r.displayName = "CSSMotion", r;
}
const Bi = zi(Yn);
var Tt = "add", Pt = "keep", Lt = "remove", yt = "removed";
function Vi(e) {
  var t;
  return e && U(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, R(R({}, t), {}, {
    key: String(t.key)
  });
}
function Mt() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(Vi);
}
function Ui() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], n = [], r = 0, o = t.length, i = Mt(e), s = Mt(t);
  i.forEach(function(c) {
    for (var d = !1, f = r; f < o; f += 1) {
      var p = s[f];
      if (p.key === c.key) {
        r < f && (n = n.concat(s.slice(r, f).map(function(m) {
          return R(R({}, m), {}, {
            status: Tt
          });
        })), r = f), n.push(R(R({}, p), {}, {
          status: Pt
        })), r += 1, d = !0;
        break;
      }
    }
    d || n.push(R(R({}, c), {}, {
      status: Lt
    }));
  }), r < o && (n = n.concat(s.slice(r).map(function(c) {
    return R(R({}, c), {}, {
      status: Tt
    });
  })));
  var a = {};
  n.forEach(function(c) {
    var d = c.key;
    a[d] = (a[d] || 0) + 1;
  });
  var u = Object.keys(a).filter(function(c) {
    return a[c] > 1;
  });
  return u.forEach(function(c) {
    n = n.filter(function(d) {
      var f = d.key, p = d.status;
      return f !== c || p !== Lt;
    }), n.forEach(function(d) {
      d.key === c && (d.status = Pt);
    });
  }), n;
}
var Xi = ["component", "children", "onVisibleChanged", "onAllRemoved"], Wi = ["status"], Gi = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function qi(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : Bi, n = /* @__PURE__ */ function(r) {
    We(i, r);
    var o = Ge(i);
    function i() {
      var s;
      ye(this, i);
      for (var a = arguments.length, u = new Array(a), c = 0; c < a; c++)
        u[c] = arguments[c];
      return s = o.call.apply(o, [this].concat(u)), T(fe(s), "state", {
        keyEntities: []
      }), T(fe(s), "removeKey", function(d) {
        s.setState(function(f) {
          var p = f.keyEntities.map(function(m) {
            return m.key !== d ? m : R(R({}, m), {}, {
              status: yt
            });
          });
          return {
            keyEntities: p
          };
        }, function() {
          var f = s.state.keyEntities, p = f.filter(function(m) {
            var b = m.status;
            return b !== yt;
          }).length;
          p === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return Se(i, [{
      key: "render",
      value: function() {
        var a = this, u = this.state.keyEntities, c = this.props, d = c.component, f = c.children, p = c.onVisibleChanged;
        c.onAllRemoved;
        var m = bn(c, Xi), b = d || O.Fragment, h = {};
        return Gi.forEach(function(g) {
          h[g] = m[g], delete m[g];
        }), delete m.keys, /* @__PURE__ */ O.createElement(b, m, u.map(function(g, x) {
          var w = g.status, y = bn(g, Wi), S = w === Tt || w === Pt;
          return /* @__PURE__ */ O.createElement(t, ve({}, h, {
            key: y.key,
            visible: S,
            eventProps: y,
            onVisibleChanged: function(v) {
              p == null || p(v, {
                key: y.key
              }), v || a.removeKey(y.key);
            }
          }), function(_, v) {
            return f(R(R({}, _), {}, {
              index: x
            }), v);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, u) {
        var c = a.keys, d = u.keyEntities, f = Mt(c), p = Ui(d, f);
        return {
          keyEntities: p.filter(function(m) {
            var b = d.find(function(h) {
              var g = h.key;
              return m.key === g;
            });
            return !(b && b.status === yt && m.status === Lt);
          })
        };
      }
    }]), i;
  }(O.Component);
  return T(n, "defaultProps", {
    component: "div"
  }), n;
}
const Ki = qi(Yn);
function Zi(e, t) {
  const {
    children: n,
    upload: r,
    rootClassName: o
  } = e, i = l.useRef(null);
  return l.useImperativeHandle(t, () => i.current), /* @__PURE__ */ l.createElement(Mn, ve({}, r, {
    showUploadList: !1,
    rootClassName: o,
    ref: i
  }), n);
}
const ir = /* @__PURE__ */ l.forwardRef(Zi), Qi = (e) => {
  const {
    componentCls: t,
    antCls: n,
    calc: r
  } = e, o = `${t}-list-card`, i = r(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
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
        width: i,
        height: i,
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
          marginInlineEnd: r(e.paddingSM).mul(-1).equal()
        }
      }
    }
  };
}, It = {
  "&, *": {
    boxSizing: "border-box"
  }
}, Yi = (e) => {
  const {
    componentCls: t,
    calc: n,
    antCls: r
  } = e, o = `${t}-drop-area`, i = `${t}-placeholder`;
  return {
    // ============================== Full Screen ==============================
    [o]: {
      position: "absolute",
      inset: 0,
      zIndex: e.zIndexPopupBase,
      ...It,
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
        ...It,
        [`${r}-upload-wrapper ${r}-upload${r}-upload-btn`]: {
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
}, Ji = (e) => {
  const {
    componentCls: t,
    calc: n
  } = e, r = `${t}-list`, o = n(e.fontSize).mul(e.lineHeight).mul(2).add(e.paddingSM).add(e.paddingSM).equal();
  return {
    [t]: {
      position: "relative",
      width: "100%",
      ...It,
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
}, es = (e) => {
  const {
    colorBgContainer: t
  } = e;
  return {
    colorBgPlaceholderHover: new oe(t).setA(0.85).toRgbString()
  };
}, sr = Ci("Attachments", (e) => {
  const t = At(e, {});
  return [Yi(t), Ji(t), Qi(t)];
}, es), ts = (e) => e.indexOf("image/") === 0, Fe = 200;
function ns(e) {
  return new Promise((t) => {
    if (!e || !e.type || !ts(e.type)) {
      t("");
      return;
    }
    const n = new Image();
    if (n.onload = () => {
      const {
        width: r,
        height: o
      } = n, i = r / o, s = i > 1 ? Fe : Fe * i, a = i > 1 ? Fe / i : Fe, u = document.createElement("canvas");
      u.width = s, u.height = a, u.style.cssText = `position: fixed; left: 0; top: 0; width: ${s}px; height: ${a}px; z-index: 9999; display: none;`, document.body.appendChild(u), u.getContext("2d").drawImage(n, 0, 0, s, a);
      const d = u.toDataURL();
      document.body.removeChild(u), window.URL.revokeObjectURL(n.src), t(d);
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
function rs() {
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
function os(e) {
  const {
    percent: t
  } = e, {
    token: n
  } = Be.useToken();
  return /* @__PURE__ */ l.createElement(Cr, {
    type: "circle",
    percent: t,
    size: n.fontSizeHeading2 * 2,
    strokeColor: "#FFF",
    trailColor: "rgba(255, 255, 255, 0.3)",
    format: (r) => /* @__PURE__ */ l.createElement("span", {
      style: {
        color: "#FFF"
      }
    }, (r || 0).toFixed(0), "%")
  });
}
function is() {
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
const St = " ", He = "#8c8c8c", ar = ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"], _n = [{
  key: "default",
  icon: /* @__PURE__ */ l.createElement(In, null),
  color: He,
  ext: []
}, {
  key: "excel",
  icon: /* @__PURE__ */ l.createElement(Pr, null),
  color: "#22b35e",
  ext: ["xlsx", "xls"]
}, {
  key: "image",
  icon: /* @__PURE__ */ l.createElement(Lr, null),
  color: He,
  ext: ar
}, {
  key: "markdown",
  icon: /* @__PURE__ */ l.createElement(Mr, null),
  color: He,
  ext: ["md", "mdx"]
}, {
  key: "pdf",
  icon: /* @__PURE__ */ l.createElement(Ir, null),
  color: "#ff4d4f",
  ext: ["pdf"]
}, {
  key: "ppt",
  icon: /* @__PURE__ */ l.createElement(Or, null),
  color: "#ff6e31",
  ext: ["ppt", "pptx"]
}, {
  key: "word",
  icon: /* @__PURE__ */ l.createElement($r, null),
  color: "#1677ff",
  ext: ["doc", "docx"]
}, {
  key: "zip",
  icon: /* @__PURE__ */ l.createElement(Ar, null),
  color: "#fab714",
  ext: ["zip", "rar", "7z", "tar", "gz"]
}, {
  key: "video",
  icon: /* @__PURE__ */ l.createElement(is, null),
  color: "#ff4d4f",
  ext: ["mp4", "avi", "mov", "wmv", "flv", "mkv"]
}, {
  key: "audio",
  icon: /* @__PURE__ */ l.createElement(rs, null),
  color: "#8c8c8c",
  ext: ["mp3", "wav", "flac", "ape", "aac", "ogg"]
}];
function Rn(e, t) {
  return t.some((n) => e.toLowerCase() === `.${n}`);
}
function ss(e) {
  let t = e;
  const n = ["B", "KB", "MB", "GB", "TB", "PB", "EB"];
  let r = 0;
  for (; t >= 1024 && r < n.length - 1; )
    t /= 1024, r++;
  return `${t.toFixed(0)} ${n[r]}`;
}
function as(e, t) {
  const {
    prefixCls: n,
    item: r,
    onRemove: o,
    className: i,
    style: s,
    imageProps: a,
    type: u,
    icon: c
  } = e, d = l.useContext(Ce), {
    disabled: f
  } = d || {}, {
    name: p,
    size: m,
    percent: b,
    status: h = "done",
    description: g
  } = r, {
    getPrefixCls: x
  } = Ve(), w = x("attachment", n), y = `${w}-list-card`, [S, _, v] = sr(w), [P, C] = l.useMemo(() => {
    const j = p || "", z = j.match(/^(.*)\.[^.]+$/);
    return z ? [z[1], j.slice(z[1].length)] : [j, ""];
  }, [p]), I = l.useMemo(() => Rn(C, ar), [C]), E = l.useMemo(() => g || (h === "uploading" ? `${b || 0}%` : h === "error" ? r.response || St : m ? ss(m) : St), [h, b]), [L, M] = l.useMemo(() => {
    if (c)
      if (typeof c == "string") {
        const j = _n.find((z) => z.key === c);
        if (j)
          return [j.icon, j.color];
      } else
        return [c, void 0];
    for (const {
      ext: j,
      icon: z,
      color: se
    } of _n)
      if (Rn(C, j))
        return [z, se];
    return [/* @__PURE__ */ l.createElement(In, {
      key: "defaultIcon"
    }), He];
  }, [C, c]), [A, F] = l.useState();
  l.useEffect(() => {
    if (r.originFileObj) {
      let j = !0;
      return ns(r.originFileObj).then((z) => {
        j && F(z);
      }), () => {
        j = !1;
      };
    }
    F(void 0);
  }, [r.originFileObj]);
  let k = null;
  const N = r.thumbUrl || r.url || A, Q = u === "image" || u !== "file" && I && (r.originFileObj || N);
  return Q ? k = /* @__PURE__ */ l.createElement(l.Fragment, null, N && /* @__PURE__ */ l.createElement(_r, ve({
    alt: "preview",
    src: N
  }, a)), h !== "done" && /* @__PURE__ */ l.createElement("div", {
    className: `${y}-img-mask`
  }, h === "uploading" && b !== void 0 && /* @__PURE__ */ l.createElement(os, {
    percent: b,
    prefixCls: y
  }), h === "error" && /* @__PURE__ */ l.createElement("div", {
    className: `${y}-desc`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${y}-ellipsis-prefix`
  }, E)))) : k = /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement("div", {
    className: `${y}-icon`,
    style: M ? {
      color: M
    } : void 0
  }, L), /* @__PURE__ */ l.createElement("div", {
    className: `${y}-content`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${y}-name`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${y}-ellipsis-prefix`
  }, P ?? St), /* @__PURE__ */ l.createElement("div", {
    className: `${y}-ellipsis-suffix`
  }, C)), /* @__PURE__ */ l.createElement("div", {
    className: `${y}-desc`
  }, /* @__PURE__ */ l.createElement("div", {
    className: `${y}-ellipsis-prefix`
  }, E)))), S(/* @__PURE__ */ l.createElement("div", {
    className: Z(y, {
      [`${y}-status-${h}`]: h,
      [`${y}-type-preview`]: Q,
      [`${y}-type-overview`]: !Q
    }, i, _, v),
    style: s,
    ref: t
  }, k, !f && o && /* @__PURE__ */ l.createElement("button", {
    type: "button",
    className: `${y}-remove`,
    onClick: () => {
      o(r);
    }
  }, /* @__PURE__ */ l.createElement(Tr, null))));
}
const lr = /* @__PURE__ */ l.forwardRef(as), Tn = 1;
function ls(e) {
  const {
    prefixCls: t,
    items: n,
    onRemove: r,
    overflow: o,
    upload: i,
    listClassName: s,
    listStyle: a,
    itemClassName: u,
    uploadClassName: c,
    uploadStyle: d,
    itemStyle: f,
    imageProps: p
  } = e, m = `${t}-list`, b = l.useRef(null), [h, g] = l.useState(!1), {
    disabled: x
  } = l.useContext(Ce);
  l.useEffect(() => (g(!0), () => {
    g(!1);
  }), []);
  const [w, y] = l.useState(!1), [S, _] = l.useState(!1), v = () => {
    const E = b.current;
    E && (o === "scrollX" ? (y(Math.abs(E.scrollLeft) >= Tn), _(E.scrollWidth - E.clientWidth - Math.abs(E.scrollLeft) >= Tn)) : o === "scrollY" && (y(E.scrollTop !== 0), _(E.scrollHeight - E.clientHeight !== E.scrollTop)));
  };
  l.useEffect(() => {
    v();
  }, [o, n.length]);
  const P = (E) => {
    const L = b.current;
    L && L.scrollTo({
      left: L.scrollLeft + E * L.clientWidth,
      behavior: "smooth"
    });
  }, C = () => {
    P(-1);
  }, I = () => {
    P(1);
  };
  return /* @__PURE__ */ l.createElement("div", {
    className: Z(m, {
      [`${m}-overflow-${e.overflow}`]: o,
      [`${m}-overflow-ping-start`]: w,
      [`${m}-overflow-ping-end`]: S
    }, s),
    ref: b,
    onScroll: v,
    style: a
  }, /* @__PURE__ */ l.createElement(Ki, {
    keys: n.map((E) => ({
      key: E.uid,
      item: E
    })),
    motionName: `${m}-card-motion`,
    component: !1,
    motionAppear: h,
    motionLeave: !0,
    motionEnter: !0
  }, ({
    key: E,
    item: L,
    className: M,
    style: A
  }) => /* @__PURE__ */ l.createElement(lr, {
    key: E,
    prefixCls: t,
    item: L,
    onRemove: r,
    className: Z(M, u),
    imageProps: p,
    style: {
      ...A,
      ...f
    }
  })), !x && /* @__PURE__ */ l.createElement(ir, {
    upload: i
  }, /* @__PURE__ */ l.createElement(lt, {
    className: Z(c, `${m}-upload-btn`),
    style: d,
    type: "dashed"
  }, /* @__PURE__ */ l.createElement(kr, {
    className: `${m}-upload-btn-icon`
  }))), o === "scrollX" && /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(lt, {
    size: "small",
    shape: "circle",
    className: `${m}-prev-btn`,
    icon: /* @__PURE__ */ l.createElement(Fr, null),
    onClick: C
  }), /* @__PURE__ */ l.createElement(lt, {
    size: "small",
    shape: "circle",
    className: `${m}-next-btn`,
    icon: /* @__PURE__ */ l.createElement(jr, null),
    onClick: I
  })));
}
function cs(e, t) {
  const {
    prefixCls: n,
    placeholder: r = {},
    upload: o,
    className: i,
    style: s
  } = e, a = `${n}-placeholder`, u = r || {}, {
    disabled: c
  } = l.useContext(Ce), [d, f] = l.useState(!1), p = () => {
    f(!0);
  }, m = (g) => {
    g.currentTarget.contains(g.relatedTarget) || f(!1);
  }, b = () => {
    f(!1);
  }, h = /* @__PURE__ */ l.isValidElement(r) ? r : /* @__PURE__ */ l.createElement(Rr, {
    align: "center",
    justify: "center",
    vertical: !0,
    className: `${a}-inner`
  }, /* @__PURE__ */ l.createElement(ct.Text, {
    className: `${a}-icon`
  }, u.icon), /* @__PURE__ */ l.createElement(ct.Title, {
    className: `${a}-title`,
    level: 5
  }, u.title), /* @__PURE__ */ l.createElement(ct.Text, {
    className: `${a}-description`,
    type: "secondary"
  }, u.description));
  return /* @__PURE__ */ l.createElement("div", {
    className: Z(a, {
      [`${a}-drag-in`]: d,
      [`${a}-disabled`]: c
    }, i),
    onDragEnter: p,
    onDragLeave: m,
    onDrop: b,
    "aria-hidden": c,
    style: s
  }, /* @__PURE__ */ l.createElement(Mn.Dragger, ve({
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
const us = /* @__PURE__ */ l.forwardRef(cs);
function fs(e, t) {
  const {
    prefixCls: n,
    rootClassName: r,
    rootStyle: o,
    className: i,
    style: s,
    items: a,
    children: u,
    getDropContainer: c,
    placeholder: d,
    onChange: f,
    onRemove: p,
    overflow: m,
    imageProps: b,
    disabled: h,
    maxCount: g,
    classNames: x = {},
    styles: w = {},
    ...y
  } = e, {
    getPrefixCls: S,
    direction: _
  } = Ve(), v = S("attachment", n), P = No("attachments"), {
    classNames: C,
    styles: I
  } = P, E = l.useRef(null), L = l.useRef(null);
  l.useImperativeHandle(t, () => ({
    nativeElement: E.current,
    upload: (H) => {
      var q, te;
      const D = (te = (q = L.current) == null ? void 0 : q.nativeElement) == null ? void 0 : te.querySelector('input[type="file"]');
      if (D) {
        const Y = new DataTransfer();
        Y.items.add(H), D.files = Y.files, D.dispatchEvent(new Event("change", {
          bubbles: !0
        }));
      }
    }
  }));
  const [M, A, F] = sr(v), k = Z(A, F), [N, Q] = Zo([], {
    value: a
  }), j = be((H) => {
    Q(H.fileList), f == null || f(H);
  }), z = {
    ...y,
    fileList: N,
    maxCount: g,
    onChange: j
  }, se = (H) => Promise.resolve(typeof p == "function" ? p(H) : p).then((D) => {
    if (D === !1)
      return;
    const q = N.filter((te) => te.uid !== H.uid);
    j({
      file: {
        ...H,
        status: "removed"
      },
      fileList: q
    });
  });
  let X;
  const ee = (H, D, q) => {
    const te = typeof d == "function" ? d(H) : d;
    return /* @__PURE__ */ l.createElement(us, {
      placeholder: te,
      upload: z,
      prefixCls: v,
      className: Z(C.placeholder, x.placeholder),
      style: {
        ...I.placeholder,
        ...w.placeholder,
        ...D == null ? void 0 : D.style
      },
      ref: q
    });
  };
  if (u)
    X = /* @__PURE__ */ l.createElement(l.Fragment, null, /* @__PURE__ */ l.createElement(ir, {
      upload: z,
      rootClassName: r,
      ref: L
    }, u), /* @__PURE__ */ l.createElement(hn, {
      getDropContainer: c,
      prefixCls: v,
      className: Z(k, r)
    }, ee("drop")));
  else {
    const H = N.length > 0;
    X = /* @__PURE__ */ l.createElement("div", {
      className: Z(v, k, {
        [`${v}-rtl`]: _ === "rtl"
      }, i, r),
      style: {
        ...o,
        ...s
      },
      dir: _ || "ltr",
      ref: E
    }, /* @__PURE__ */ l.createElement(ls, {
      prefixCls: v,
      items: N,
      onRemove: se,
      overflow: m,
      upload: z,
      listClassName: Z(C.list, x.list),
      listStyle: {
        ...I.list,
        ...w.list,
        ...!H && {
          display: "none"
        }
      },
      uploadClassName: Z(C.upload, x.upload),
      uploadStyle: {
        ...I.upload,
        ...w.upload
      },
      itemClassName: Z(C.item, x.item),
      itemStyle: {
        ...I.item,
        ...w.item
      },
      imageProps: b
    }), ee("inline", H ? {
      style: {
        display: "none"
      }
    } : {}, L), /* @__PURE__ */ l.createElement(hn, {
      getDropContainer: c || (() => E.current),
      prefixCls: v,
      className: k
    }, ee("drop")));
  }
  return M(/* @__PURE__ */ l.createElement(Ce.Provider, {
    value: {
      disabled: h
    }
  }, X));
}
const cr = /* @__PURE__ */ l.forwardRef(fs);
cr.FileCard = lr;
new Intl.Collator(0, {
  numeric: 1
}).compare;
typeof process < "u" && process.versions && process.versions.node;
var ie;
class Ss extends TransformStream {
  /** Constructs a new instance. */
  constructor(n = {
    allowCR: !1
  }) {
    super({
      transform: (r, o) => {
        for (r = de(this, ie) + r; ; ) {
          const i = r.indexOf(`
`), s = n.allowCR ? r.indexOf("\r") : -1;
          if (s !== -1 && s !== r.length - 1 && (i === -1 || i - 1 > s)) {
            o.enqueue(r.slice(0, s)), r = r.slice(s + 1);
            continue;
          }
          if (i === -1) break;
          const a = r[i - 1] === "\r" ? i - 1 : i;
          o.enqueue(r.slice(0, a)), r = r.slice(i + 1);
        }
        Bt(this, ie, r);
      },
      flush: (r) => {
        if (de(this, ie) === "") return;
        const o = n.allowCR && de(this, ie).endsWith("\r") ? de(this, ie).slice(0, -1) : de(this, ie);
        r.enqueue(o);
      }
    });
    zt(this, ie, "");
  }
}
ie = new WeakMap();
function ds(e) {
  try {
    const t = new URL(e);
    return t.protocol === "http:" || t.protocol === "https:";
  } catch {
    return !1;
  }
}
function ps() {
  const e = document.querySelector(".gradio-container");
  if (!e)
    return "";
  const t = e.className.match(/gradio-container-(.+)/);
  return t ? t[1] : "";
}
const ms = +ps()[0];
function Pn(e, t, n) {
  const r = ms >= 5 ? "gradio_api/" : "";
  return e == null ? n ? `/proxy=${n}${r}file=` : `${t}${r}file=` : ds(e) ? e : n ? `/proxy=${n}${r}file=${e}` : `${t}/${r}file=${e}`;
}
const gs = ({
  item: e,
  urlRoot: t,
  urlProxyUrl: n,
  ...r
}) => {
  const o = Ln(() => e ? typeof e == "string" ? {
    url: e.startsWith("http") ? e : Pn(e, t, n),
    uid: e,
    name: e.split("/").pop()
  } : {
    ...e,
    uid: e.uid || e.path || e.url,
    name: e.name || e.orig_name || (e.url || e.path).split("/").pop(),
    url: e.url || Pn(e.path, t, n)
  } : {}, [e, n, t]);
  return /* @__PURE__ */ V.jsx(cr.FileCard, {
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
};
function hs(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const xs = _o(({
  setSlotParams: e,
  imageProps: t,
  slots: n,
  children: r,
  ...o
}) => {
  const i = hs(t == null ? void 0 : t.preview), s = n["imageProps.preview.mask"] || n["imageProps.preview.closeIcon"] || n["imageProps.preview.toolbarRender"] || n["imageProps.preview.imageRender"] || (t == null ? void 0 : t.preview) !== !1, a = pt(i.getContainer), u = pt(i.toolbarRender), c = pt(i.imageRender);
  return /* @__PURE__ */ V.jsxs(V.Fragment, {
    children: [/* @__PURE__ */ V.jsx("div", {
      style: {
        display: "none"
      },
      children: r
    }), /* @__PURE__ */ V.jsx(gs, {
      ...o,
      icon: n.icon ? /* @__PURE__ */ V.jsx(me, {
        slot: n.icon
      }) : o.icon,
      imageProps: {
        ...t,
        preview: s ? Oo({
          ...i,
          getContainer: a,
          toolbarRender: n["imageProps.preview.toolbarRender"] ? rn({
            slots: n,
            key: "imageProps.preview.toolbarRender"
          }) : u,
          imageRender: n["imageProps.preview.imageRender"] ? rn({
            slots: n,
            key: "imageProps.preview.imageRender"
          }) : c,
          ...n["imageProps.preview.mask"] || Reflect.has(i, "mask") ? {
            mask: n["imageProps.preview.mask"] ? /* @__PURE__ */ V.jsx(me, {
              slot: n["imageProps.preview.mask"]
            }) : i.mask
          } : {},
          closeIcon: n["imageProps.preview.closeIcon"] ? /* @__PURE__ */ V.jsx(me, {
            slot: n["imageProps.preview.closeIcon"]
          }) : i.closeIcon
        }) : !1,
        placeholder: n["imageProps.placeholder"] ? /* @__PURE__ */ V.jsx(me, {
          slot: n["imageProps.placeholder"]
        }) : t == null ? void 0 : t.placeholder
      }
    })]
  });
});
export {
  xs as AttachmentsFileCard,
  xs as default
};
