import { i as de, a as M, r as fe, Z as R, g as me } from "./Index-CrdmwfXA.js";
const p = window.ms_globals.React, oe = window.ms_globals.React.forwardRef, ce = window.ms_globals.React.useRef, ae = window.ms_globals.React.useState, ie = window.ms_globals.React.useEffect, ue = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, W = window.ms_globals.internalContext.ContextPropsProvider, he = window.ms_globals.antd.Menu, ge = window.ms_globals.createItemsContext.createItemsContext;
var xe = /\s/;
function be(t) {
  for (var e = t.length; e-- && xe.test(t.charAt(e)); )
    ;
  return e;
}
var we = /^\s+/;
function ve(t) {
  return t && t.slice(0, be(t) + 1).replace(we, "");
}
var H = NaN, Ce = /^[-+]0x[0-9a-f]+$/i, pe = /^0b[01]+$/i, Ee = /^0o[0-7]+$/i, Ie = parseInt;
function z(t) {
  if (typeof t == "number")
    return t;
  if (de(t))
    return H;
  if (M(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = M(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = ve(t);
  var s = pe.test(t);
  return s || Ee.test(t) ? Ie(t.slice(2), s ? 2 : 8) : Ce.test(t) ? H : +t;
}
var L = function() {
  return fe.Date.now();
}, ye = "Expected a function", Se = Math.max, Pe = Math.min;
function Te(t, e, s) {
  var o, n, r, l, c, i, h = 0, g = !1, a = !1, x = !0;
  if (typeof t != "function")
    throw new TypeError(ye);
  e = z(e) || 0, M(s) && (g = !!s.leading, a = "maxWait" in s, r = a ? Se(z(s.maxWait) || 0, e) : r, x = "trailing" in s ? !!s.trailing : x);
  function u(m) {
    var E = o, P = n;
    return o = n = void 0, h = m, l = t.apply(P, E), l;
  }
  function v(m) {
    return h = m, c = setTimeout(_, e), g ? u(m) : l;
  }
  function C(m) {
    var E = m - i, P = m - h, B = e - E;
    return a ? Pe(B, r - P) : B;
  }
  function d(m) {
    var E = m - i, P = m - h;
    return i === void 0 || E >= e || E < 0 || a && P >= r;
  }
  function _() {
    var m = L();
    if (d(m))
      return b(m);
    c = setTimeout(_, C(m));
  }
  function b(m) {
    return c = void 0, x && o ? u(m) : (o = n = void 0, l);
  }
  function I() {
    c !== void 0 && clearTimeout(c), h = 0, o = i = n = c = void 0;
  }
  function f() {
    return c === void 0 ? l : b(L());
  }
  function y() {
    var m = L(), E = d(m);
    if (o = arguments, n = this, i = m, E) {
      if (c === void 0)
        return v(i);
      if (a)
        return clearTimeout(c), c = setTimeout(_, e), u(i);
    }
    return c === void 0 && (c = setTimeout(_, e)), l;
  }
  return y.cancel = I, y.flush = f, y;
}
var Q = {
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
var Re = p, ke = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), je = Object.prototype.hasOwnProperty, Le = Re.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ne = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function $(t, e, s) {
  var o, n = {}, r = null, l = null;
  s !== void 0 && (r = "" + s), e.key !== void 0 && (r = "" + e.key), e.ref !== void 0 && (l = e.ref);
  for (o in e) je.call(e, o) && !Ne.hasOwnProperty(o) && (n[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) n[o] === void 0 && (n[o] = e[o]);
  return {
    $$typeof: ke,
    type: t,
    key: r,
    ref: l,
    props: n,
    _owner: Le.current
  };
}
j.Fragment = Oe;
j.jsx = $;
j.jsxs = $;
Q.exports = j;
var w = Q.exports;
const {
  SvelteComponent: Ae,
  assign: D,
  binding_callbacks: G,
  check_outros: Me,
  children: ee,
  claim_element: te,
  claim_space: We,
  component_subscribe: q,
  compute_slots: Fe,
  create_slot: Ue,
  detach: S,
  element: re,
  empty: V,
  exclude_internal_props: J,
  get_all_dirty_from_scope: Be,
  get_slot_changes: He,
  group_outros: ze,
  init: De,
  insert_hydration: k,
  safe_not_equal: Ge,
  set_custom_element_data: ne,
  space: qe,
  transition_in: O,
  transition_out: F,
  update_slot_base: Ve
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Ze
} = window.__gradio__svelte__internal;
function X(t) {
  let e, s;
  const o = (
    /*#slots*/
    t[7].default
  ), n = Ue(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = re("svelte-slot"), n && n.c(), this.h();
    },
    l(r) {
      e = te(r, "SVELTE-SLOT", {
        class: !0
      });
      var l = ee(e);
      n && n.l(l), l.forEach(S), this.h();
    },
    h() {
      ne(e, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      k(r, e, l), n && n.m(e, null), t[9](e), s = !0;
    },
    p(r, l) {
      n && n.p && (!s || l & /*$$scope*/
      64) && Ve(
        n,
        o,
        r,
        /*$$scope*/
        r[6],
        s ? He(
          o,
          /*$$scope*/
          r[6],
          l,
          null
        ) : Be(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      s || (O(n, r), s = !0);
    },
    o(r) {
      F(n, r), s = !1;
    },
    d(r) {
      r && S(e), n && n.d(r), t[9](null);
    }
  };
}
function Ke(t) {
  let e, s, o, n, r = (
    /*$$slots*/
    t[4].default && X(t)
  );
  return {
    c() {
      e = re("react-portal-target"), s = qe(), r && r.c(), o = V(), this.h();
    },
    l(l) {
      e = te(l, "REACT-PORTAL-TARGET", {
        class: !0
      }), ee(e).forEach(S), s = We(l), r && r.l(l), o = V(), this.h();
    },
    h() {
      ne(e, "class", "svelte-1rt0kpf");
    },
    m(l, c) {
      k(l, e, c), t[8](e), k(l, s, c), r && r.m(l, c), k(l, o, c), n = !0;
    },
    p(l, [c]) {
      /*$$slots*/
      l[4].default ? r ? (r.p(l, c), c & /*$$slots*/
      16 && O(r, 1)) : (r = X(l), r.c(), O(r, 1), r.m(o.parentNode, o)) : r && (ze(), F(r, 1, 1, () => {
        r = null;
      }), Me());
    },
    i(l) {
      n || (O(r), n = !0);
    },
    o(l) {
      F(r), n = !1;
    },
    d(l) {
      l && (S(e), S(s), S(o)), t[8](null), r && r.d(l);
    }
  };
}
function Y(t) {
  const {
    svelteInit: e,
    ...s
  } = t;
  return s;
}
function Qe(t, e, s) {
  let o, n, {
    $$slots: r = {},
    $$scope: l
  } = e;
  const c = Fe(r);
  let {
    svelteInit: i
  } = e;
  const h = R(Y(e)), g = R();
  q(t, g, (f) => s(0, o = f));
  const a = R();
  q(t, a, (f) => s(1, n = f));
  const x = [], u = Xe("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: C,
    subSlotIndex: d
  } = me() || {}, _ = i({
    parent: u,
    props: h,
    target: g,
    slot: a,
    slotKey: v,
    slotIndex: C,
    subSlotIndex: d,
    onDestroy(f) {
      x.push(f);
    }
  });
  Ze("$$ms-gr-react-wrapper", _), Je(() => {
    h.set(Y(e));
  }), Ye(() => {
    x.forEach((f) => f());
  });
  function b(f) {
    G[f ? "unshift" : "push"](() => {
      o = f, g.set(o);
    });
  }
  function I(f) {
    G[f ? "unshift" : "push"](() => {
      n = f, a.set(n);
    });
  }
  return t.$$set = (f) => {
    s(17, e = D(D({}, e), J(f))), "svelteInit" in f && s(5, i = f.svelteInit), "$$scope" in f && s(6, l = f.$$scope);
  }, e = J(e), [o, n, g, a, c, i, l, r, b, I];
}
class $e extends Ae {
  constructor(e) {
    super(), De(this, e, Qe, Ke, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: dt
} = window.__gradio__svelte__internal, Z = window.ms_globals.rerender, N = window.ms_globals.tree;
function et(t, e = {}) {
  function s(o) {
    const n = R(), r = new $e({
      ...o,
      props: {
        svelteInit(l) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: n,
            reactComponent: t,
            props: l.props,
            slot: l.slot,
            target: l.target,
            slotIndex: l.slotIndex,
            subSlotIndex: l.subSlotIndex,
            ignore: e.ignore,
            slotKey: l.slotKey,
            nodes: []
          }, i = l.parent ?? N;
          return i.nodes = [...i.nodes, c], Z({
            createPortal: A,
            node: N
          }), l.onDestroy(() => {
            i.nodes = i.nodes.filter((h) => h.svelteInstance !== n), Z({
              createPortal: A,
              node: N
            });
          }), c;
        },
        ...o.props
      }
    });
    return n.set(r), r;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise.then(() => {
      o(s);
    });
  });
}
const tt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function rt(t) {
  return t ? Object.keys(t).reduce((e, s) => {
    const o = t[s];
    return e[s] = nt(s, o), e;
  }, {}) : {};
}
function nt(t, e) {
  return typeof e == "number" && !tt.includes(t) ? e + "px" : e;
}
function U(t) {
  const e = [], s = t.cloneNode(!1);
  if (t._reactElement) {
    const n = p.Children.toArray(t._reactElement.props.children).map((r) => {
      if (p.isValidElement(r) && r.props.__slot__) {
        const {
          portals: l,
          clonedElement: c
        } = U(r.props.el);
        return p.cloneElement(r, {
          ...r.props,
          el: c,
          children: [...p.Children.toArray(r.props.children), ...l]
        });
      }
      return null;
    });
    return n.originalChildren = t._reactElement.props.children, e.push(A(p.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: n
    }), s)), {
      clonedElement: s,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((n) => {
    t.getEventListeners(n).forEach(({
      listener: l,
      type: c,
      useCapture: i
    }) => {
      s.addEventListener(c, l, i);
    });
  });
  const o = Array.from(t.childNodes);
  for (let n = 0; n < o.length; n++) {
    const r = o[n];
    if (r.nodeType === 1) {
      const {
        clonedElement: l,
        portals: c
      } = U(r);
      e.push(...c), s.appendChild(l);
    } else r.nodeType === 3 && s.appendChild(r.cloneNode());
  }
  return {
    clonedElement: s,
    portals: e
  };
}
function lt(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const T = oe(({
  slot: t,
  clone: e,
  className: s,
  style: o,
  observeAttributes: n
}, r) => {
  const l = ce(), [c, i] = ae([]), {
    forceClone: h
  } = _e(), g = h ? !0 : e;
  return ie(() => {
    var C;
    if (!l.current || !t)
      return;
    let a = t;
    function x() {
      let d = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (d = a.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), lt(r, d), s && d.classList.add(...s.split(" ")), o) {
        const _ = rt(o);
        Object.keys(_).forEach((b) => {
          d.style[b] = _[b];
        });
      }
    }
    let u = null, v = null;
    if (g && window.MutationObserver) {
      let d = function() {
        var f, y, m;
        (f = l.current) != null && f.contains(a) && ((y = l.current) == null || y.removeChild(a));
        const {
          portals: b,
          clonedElement: I
        } = U(t);
        a = I, i(b), a.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          x();
        }, 50), (m = l.current) == null || m.appendChild(a);
      };
      d();
      const _ = Te(() => {
        d(), u == null || u.disconnect(), u == null || u.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: n
        });
      }, 50);
      u = new window.MutationObserver(_), u.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", x(), (C = l.current) == null || C.appendChild(a);
    return () => {
      var d, _;
      a.style.display = "", (d = l.current) != null && d.contains(a) && ((_ = l.current) == null || _.removeChild(a)), u == null || u.disconnect();
    };
  }, [t, g, s, o, r, n, h]), p.createElement("react-child", {
    ref: l,
    style: {
      display: "contents"
    }
  }, ...c);
});
function st(t, e) {
  return Object.keys(t).reduce((s, o) => (t[o] !== void 0 && (s[o] = t[o]), s), {});
}
const ot = ({
  children: t,
  ...e
}) => /* @__PURE__ */ w.jsx(w.Fragment, {
  children: t(e)
});
function le(t) {
  return p.createElement(ot, {
    children: t
  });
}
function se(t, e, s) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((n, r) => {
      var h, g;
      if (typeof n != "object")
        return e != null && e.fallback ? e.fallback(n) : n;
      const l = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...n.props,
        key: ((h = n.props) == null ? void 0 : h.key) ?? (s ? `${s}-${r}` : `${r}`)
      }) : {
        ...n.props,
        key: ((g = n.props) == null ? void 0 : g.key) ?? (s ? `${s}-${r}` : `${r}`)
      };
      let c = l;
      Object.keys(n.slots).forEach((a) => {
        if (!n.slots[a] || !(n.slots[a] instanceof Element) && !n.slots[a].el)
          return;
        const x = a.split(".");
        x.forEach((b, I) => {
          c[b] || (c[b] = {}), I !== x.length - 1 && (c = l[b]);
        });
        const u = n.slots[a];
        let v, C, d = (e == null ? void 0 : e.clone) ?? !1, _ = e == null ? void 0 : e.forceClone;
        u instanceof Element ? v = u : (v = u.el, C = u.callback, d = u.clone ?? d, _ = u.forceClone ?? _), _ = _ ?? !!C, c[x[x.length - 1]] = v ? C ? (...b) => (C(x[x.length - 1], b), /* @__PURE__ */ w.jsx(W, {
          ...n.ctx,
          params: b,
          forceClone: _,
          children: /* @__PURE__ */ w.jsx(T, {
            slot: v,
            clone: d
          })
        })) : le((b) => /* @__PURE__ */ w.jsx(W, {
          ...n.ctx,
          forceClone: _,
          children: /* @__PURE__ */ w.jsx(T, {
            ...b,
            slot: v,
            clone: d
          })
        })) : c[x[x.length - 1]], c = l;
      });
      const i = (e == null ? void 0 : e.children) || "children";
      return n[i] ? l[i] = se(n[i], e, `${r}`) : e != null && e.children && (l[i] = void 0, Reflect.deleteProperty(l, i)), l;
    });
}
function K(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? le((s) => /* @__PURE__ */ w.jsx(W, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ w.jsx(T, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...s
    })
  })) : /* @__PURE__ */ w.jsx(T, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function ct({
  key: t,
  slots: e,
  targets: s
}, o) {
  return e[t] ? (...n) => s ? s.map((r, l) => /* @__PURE__ */ w.jsx(p.Fragment, {
    children: K(r, {
      clone: !0,
      params: n,
      forceClone: (o == null ? void 0 : o.forceClone) ?? !0
    })
  }, l)) : /* @__PURE__ */ w.jsx(w.Fragment, {
    children: K(e[t], {
      clone: !0,
      params: n,
      forceClone: (o == null ? void 0 : o.forceClone) ?? !0
    })
  }) : void 0;
}
const {
  useItems: at,
  withItemsContextProvider: it,
  ItemHandler: ft
} = ge("antd-menu-items"), mt = et(it(["default", "items"], ({
  slots: t,
  items: e,
  children: s,
  onOpenChange: o,
  onSelect: n,
  onDeselect: r,
  setSlotParams: l,
  ...c
}) => {
  const {
    items: i
  } = at(), h = i.items.length > 0 ? i.items : i.default;
  return /* @__PURE__ */ w.jsxs(w.Fragment, {
    children: [/* @__PURE__ */ w.jsx("div", {
      style: {
        display: "none"
      },
      children: s
    }), /* @__PURE__ */ w.jsx(he, {
      ...st(c),
      onOpenChange: (g) => {
        o == null || o(g);
      },
      onSelect: (g) => {
        n == null || n(g);
      },
      onDeselect: (g) => {
        r == null || r(g);
      },
      items: ue(() => e || se(h, {
        clone: !0
      }), [e, h]),
      expandIcon: t.expandIcon ? ct({
        key: "expandIcon",
        slots: t
      }, {}) : c.expandIcon,
      overflowedIndicator: t.overflowedIndicator ? /* @__PURE__ */ w.jsx(T, {
        slot: t.overflowedIndicator
      }) : c.overflowedIndicator
    })]
  });
}));
export {
  mt as Menu,
  mt as default
};
