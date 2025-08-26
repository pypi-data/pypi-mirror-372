import { i as ae, a as W, r as ue, Z as R, g as de } from "./Index-B5uXeAUO.js";
const y = window.ms_globals.React, oe = window.ms_globals.React.forwardRef, se = window.ms_globals.React.useRef, le = window.ms_globals.React.useState, ie = window.ms_globals.React.useEffect, ce = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, fe = window.ms_globals.internalContext.useContextPropsContext, U = window.ms_globals.internalContext.ContextPropsProvider, me = window.ms_globals.antd.Descriptions, pe = window.ms_globals.createItemsContext.createItemsContext;
var _e = /\s/;
function he(e) {
  for (var t = e.length; t-- && _e.test(e.charAt(t)); )
    ;
  return t;
}
var ge = /^\s+/;
function xe(e) {
  return e && e.slice(0, he(e) + 1).replace(ge, "");
}
var B = NaN, be = /^[-+]0x[0-9a-f]+$/i, we = /^0b[01]+$/i, Ee = /^0o[0-7]+$/i, Ce = parseInt;
function H(e) {
  if (typeof e == "number")
    return e;
  if (ae(e))
    return B;
  if (W(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = W(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = xe(e);
  var s = we.test(e);
  return s || Ee.test(e) ? Ce(e.slice(2), s ? 2 : 8) : be.test(e) ? B : +e;
}
var L = function() {
  return ue.Date.now();
}, ye = "Expected a function", ve = Math.max, Ie = Math.min;
function Se(e, t, s) {
  var l, r, n, o, i, u, _ = 0, h = !1, c = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(ye);
  t = H(t) || 0, W(s) && (h = !!s.leading, c = "maxWait" in s, n = c ? ve(H(s.maxWait) || 0, t) : n, g = "trailing" in s ? !!s.trailing : g);
  function f(p) {
    var C = l, O = r;
    return l = r = void 0, _ = p, o = e.apply(O, C), o;
  }
  function x(p) {
    return _ = p, i = setTimeout(m, t), h ? f(p) : o;
  }
  function w(p) {
    var C = p - u, O = p - _, F = t - C;
    return c ? Ie(F, n - O) : F;
  }
  function a(p) {
    var C = p - u, O = p - _;
    return u === void 0 || C >= t || C < 0 || c && O >= n;
  }
  function m() {
    var p = L();
    if (a(p))
      return E(p);
    i = setTimeout(m, w(p));
  }
  function E(p) {
    return i = void 0, g && l ? f(p) : (l = r = void 0, o);
  }
  function S() {
    i !== void 0 && clearTimeout(i), _ = 0, l = u = r = i = void 0;
  }
  function d() {
    return i === void 0 ? o : E(L());
  }
  function v() {
    var p = L(), C = a(p);
    if (l = arguments, r = this, u = p, C) {
      if (i === void 0)
        return x(u);
      if (c)
        return clearTimeout(i), i = setTimeout(m, t), f(u);
    }
    return i === void 0 && (i = setTimeout(m, t)), o;
  }
  return v.cancel = S, v.flush = d, v;
}
var K = {
  exports: {}
}, j = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Oe = y, Re = Symbol.for("react.element"), Te = Symbol.for("react.fragment"), ke = Object.prototype.hasOwnProperty, Pe = Oe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, je = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Q(e, t, s) {
  var l, r = {}, n = null, o = null;
  s !== void 0 && (n = "" + s), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (l in t) ke.call(t, l) && !je.hasOwnProperty(l) && (r[l] = t[l]);
  if (e && e.defaultProps) for (l in t = e.defaultProps, t) r[l] === void 0 && (r[l] = t[l]);
  return {
    $$typeof: Re,
    type: e,
    key: n,
    ref: o,
    props: r,
    _owner: Pe.current
  };
}
j.Fragment = Te;
j.jsx = Q;
j.jsxs = Q;
K.exports = j;
var b = K.exports;
const {
  SvelteComponent: Le,
  assign: z,
  binding_callbacks: G,
  check_outros: Ne,
  children: $,
  claim_element: ee,
  claim_space: Ae,
  component_subscribe: q,
  compute_slots: We,
  create_slot: De,
  detach: I,
  element: te,
  empty: V,
  exclude_internal_props: J,
  get_all_dirty_from_scope: Me,
  get_slot_changes: Fe,
  group_outros: Ue,
  init: Be,
  insert_hydration: T,
  safe_not_equal: He,
  set_custom_element_data: ne,
  space: ze,
  transition_in: k,
  transition_out: D,
  update_slot_base: Ge
} = window.__gradio__svelte__internal, {
  beforeUpdate: qe,
  getContext: Ve,
  onDestroy: Je,
  setContext: Xe
} = window.__gradio__svelte__internal;
function X(e) {
  let t, s;
  const l = (
    /*#slots*/
    e[7].default
  ), r = De(
    l,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = te("svelte-slot"), r && r.c(), this.h();
    },
    l(n) {
      t = ee(n, "SVELTE-SLOT", {
        class: !0
      });
      var o = $(t);
      r && r.l(o), o.forEach(I), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      T(n, t, o), r && r.m(t, null), e[9](t), s = !0;
    },
    p(n, o) {
      r && r.p && (!s || o & /*$$scope*/
      64) && Ge(
        r,
        l,
        n,
        /*$$scope*/
        n[6],
        s ? Fe(
          l,
          /*$$scope*/
          n[6],
          o,
          null
        ) : Me(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      s || (k(r, n), s = !0);
    },
    o(n) {
      D(r, n), s = !1;
    },
    d(n) {
      n && I(t), r && r.d(n), e[9](null);
    }
  };
}
function Ye(e) {
  let t, s, l, r, n = (
    /*$$slots*/
    e[4].default && X(e)
  );
  return {
    c() {
      t = te("react-portal-target"), s = ze(), n && n.c(), l = V(), this.h();
    },
    l(o) {
      t = ee(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), $(t).forEach(I), s = Ae(o), n && n.l(o), l = V(), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(o, i) {
      T(o, t, i), e[8](t), T(o, s, i), n && n.m(o, i), T(o, l, i), r = !0;
    },
    p(o, [i]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, i), i & /*$$slots*/
      16 && k(n, 1)) : (n = X(o), n.c(), k(n, 1), n.m(l.parentNode, l)) : n && (Ue(), D(n, 1, 1, () => {
        n = null;
      }), Ne());
    },
    i(o) {
      r || (k(n), r = !0);
    },
    o(o) {
      D(n), r = !1;
    },
    d(o) {
      o && (I(t), I(s), I(l)), e[8](null), n && n.d(o);
    }
  };
}
function Y(e) {
  const {
    svelteInit: t,
    ...s
  } = e;
  return s;
}
function Ze(e, t, s) {
  let l, r, {
    $$slots: n = {},
    $$scope: o
  } = t;
  const i = We(n);
  let {
    svelteInit: u
  } = t;
  const _ = R(Y(t)), h = R();
  q(e, h, (d) => s(0, l = d));
  const c = R();
  q(e, c, (d) => s(1, r = d));
  const g = [], f = Ve("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: w,
    subSlotIndex: a
  } = de() || {}, m = u({
    parent: f,
    props: _,
    target: h,
    slot: c,
    slotKey: x,
    slotIndex: w,
    subSlotIndex: a,
    onDestroy(d) {
      g.push(d);
    }
  });
  Xe("$$ms-gr-react-wrapper", m), qe(() => {
    _.set(Y(t));
  }), Je(() => {
    g.forEach((d) => d());
  });
  function E(d) {
    G[d ? "unshift" : "push"](() => {
      l = d, h.set(l);
    });
  }
  function S(d) {
    G[d ? "unshift" : "push"](() => {
      r = d, c.set(r);
    });
  }
  return e.$$set = (d) => {
    s(17, t = z(z({}, t), J(d))), "svelteInit" in d && s(5, u = d.svelteInit), "$$scope" in d && s(6, o = d.$$scope);
  }, t = J(t), [l, r, h, c, i, u, o, n, E, S];
}
class Ke extends Le {
  constructor(t) {
    super(), Be(this, t, Ze, Ye, He, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ct
} = window.__gradio__svelte__internal, Z = window.ms_globals.rerender, N = window.ms_globals.tree;
function Qe(e, t = {}) {
  function s(l) {
    const r = R(), n = new Ke({
      ...l,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const i = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: e,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, u = o.parent ?? N;
          return u.nodes = [...u.nodes, i], Z({
            createPortal: A,
            node: N
          }), o.onDestroy(() => {
            u.nodes = u.nodes.filter((_) => _.svelteInstance !== r), Z({
              createPortal: A,
              node: N
            });
          }), i;
        },
        ...l.props
      }
    });
    return r.set(n), n;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise.then(() => {
      l(s);
    });
  });
}
const $e = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function et(e) {
  return e ? Object.keys(e).reduce((t, s) => {
    const l = e[s];
    return t[s] = tt(s, l), t;
  }, {}) : {};
}
function tt(e, t) {
  return typeof t == "number" && !$e.includes(e) ? t + "px" : t;
}
function M(e) {
  const t = [], s = e.cloneNode(!1);
  if (e._reactElement) {
    const r = y.Children.toArray(e._reactElement.props.children).map((n) => {
      if (y.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: i
        } = M(n.props.el);
        return y.cloneElement(n, {
          ...n.props,
          el: i,
          children: [...y.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return r.originalChildren = e._reactElement.props.children, t.push(A(y.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: r
    }), s)), {
      clonedElement: s,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((r) => {
    e.getEventListeners(r).forEach(({
      listener: o,
      type: i,
      useCapture: u
    }) => {
      s.addEventListener(i, o, u);
    });
  });
  const l = Array.from(e.childNodes);
  for (let r = 0; r < l.length; r++) {
    const n = l[r];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: i
      } = M(n);
      t.push(...i), s.appendChild(o);
    } else n.nodeType === 3 && s.appendChild(n.cloneNode());
  }
  return {
    clonedElement: s,
    portals: t
  };
}
function nt(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const P = oe(({
  slot: e,
  clone: t,
  className: s,
  style: l,
  observeAttributes: r
}, n) => {
  const o = se(), [i, u] = le([]), {
    forceClone: _
  } = fe(), h = _ ? !0 : t;
  return ie(() => {
    var w;
    if (!o.current || !e)
      return;
    let c = e;
    function g() {
      let a = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (a = c.children[0], a.tagName.toLowerCase() === "react-portal-target" && a.children[0] && (a = a.children[0])), nt(n, a), s && a.classList.add(...s.split(" ")), l) {
        const m = et(l);
        Object.keys(m).forEach((E) => {
          a.style[E] = m[E];
        });
      }
    }
    let f = null, x = null;
    if (h && window.MutationObserver) {
      let a = function() {
        var d, v, p;
        (d = o.current) != null && d.contains(c) && ((v = o.current) == null || v.removeChild(c));
        const {
          portals: E,
          clonedElement: S
        } = M(e);
        c = S, u(E), c.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          g();
        }, 50), (p = o.current) == null || p.appendChild(c);
      };
      a();
      const m = Se(() => {
        a(), f == null || f.disconnect(), f == null || f.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      f = new window.MutationObserver(m), f.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", g(), (w = o.current) == null || w.appendChild(c);
    return () => {
      var a, m;
      c.style.display = "", (a = o.current) != null && a.contains(c) && ((m = o.current) == null || m.removeChild(c)), f == null || f.disconnect();
    };
  }, [e, h, s, l, n, r, _]), y.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...i);
}), rt = ({
  children: e,
  ...t
}) => /* @__PURE__ */ b.jsx(b.Fragment, {
  children: e(t)
});
function ot(e) {
  return y.createElement(rt, {
    children: e
  });
}
function re(e, t, s) {
  const l = e.filter(Boolean);
  if (l.length !== 0)
    return l.map((r, n) => {
      var _;
      if (typeof r != "object")
        return r;
      const o = {
        ...r.props,
        key: ((_ = r.props) == null ? void 0 : _.key) ?? (s ? `${s}-${n}` : `${n}`)
      };
      let i = o;
      Object.keys(r.slots).forEach((h) => {
        if (!r.slots[h] || !(r.slots[h] instanceof Element) && !r.slots[h].el)
          return;
        const c = h.split(".");
        c.forEach((m, E) => {
          i[m] || (i[m] = {}), E !== c.length - 1 && (i = o[m]);
        });
        const g = r.slots[h];
        let f, x, w = !1, a = t == null ? void 0 : t.forceClone;
        g instanceof Element ? f = g : (f = g.el, x = g.callback, w = g.clone ?? w, a = g.forceClone ?? a), a = a ?? !!x, i[c[c.length - 1]] = f ? x ? (...m) => (x(c[c.length - 1], m), /* @__PURE__ */ b.jsx(U, {
          ...r.ctx,
          params: m,
          forceClone: a,
          children: /* @__PURE__ */ b.jsx(P, {
            slot: f,
            clone: w
          })
        })) : ot((m) => /* @__PURE__ */ b.jsx(U, {
          ...r.ctx,
          forceClone: a,
          children: /* @__PURE__ */ b.jsx(P, {
            ...m,
            slot: f,
            clone: w
          })
        })) : i[c[c.length - 1]], i = o;
      });
      const u = "children";
      return r[u] && (o[u] = re(r[u], t, `${n}`)), o;
    });
}
const {
  withItemsContextProvider: st,
  useItems: lt,
  ItemHandler: at
} = pe("antd-descriptions-items"), ut = Qe(st(["default", "items"], ({
  slots: e,
  items: t,
  children: s,
  ...l
}) => {
  const {
    items: r
  } = lt(), n = r.items.length > 0 ? r.items : r.default;
  return /* @__PURE__ */ b.jsxs(b.Fragment, {
    children: [/* @__PURE__ */ b.jsx("div", {
      style: {
        display: "none"
      },
      children: s
    }), /* @__PURE__ */ b.jsx(me, {
      ...l,
      extra: e.extra ? /* @__PURE__ */ b.jsx(P, {
        slot: e.extra
      }) : l.extra,
      title: e.title ? /* @__PURE__ */ b.jsx(P, {
        slot: e.title
      }) : l.title,
      items: ce(() => t || re(n), [t, n])
    })]
  });
}));
export {
  ut as Descriptions,
  ut as default
};
