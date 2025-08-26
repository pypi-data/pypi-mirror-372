import { i as de, a as W, r as fe, Z as T, g as me } from "./Index-BOt1-rMB.js";
const E = window.ms_globals.React, ce = window.ms_globals.React.forwardRef, oe = window.ms_globals.React.useRef, ae = window.ms_globals.React.useState, ie = window.ms_globals.React.useEffect, ue = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, F = window.ms_globals.internalContext.ContextPropsProvider, he = window.ms_globals.antd.Breadcrumb, ge = window.ms_globals.createItemsContext.createItemsContext;
var be = /\s/;
function xe(t) {
  for (var e = t.length; e-- && be.test(t.charAt(e)); )
    ;
  return e;
}
var pe = /^\s+/;
function Ce(t) {
  return t && t.slice(0, xe(t) + 1).replace(pe, "");
}
var U = NaN, we = /^[-+]0x[0-9a-f]+$/i, Ee = /^0b[01]+$/i, ve = /^0o[0-7]+$/i, ye = parseInt;
function H(t) {
  if (typeof t == "number")
    return t;
  if (de(t))
    return U;
  if (W(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = W(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Ce(t);
  var s = Ee.test(t);
  return s || ve.test(t) ? ye(t.slice(2), s ? 2 : 8) : we.test(t) ? U : +t;
}
var L = function() {
  return fe.Date.now();
}, Ie = "Expected a function", Se = Math.max, Re = Math.min;
function Pe(t, e, s) {
  var c, l, r, n, o, i, x = 0, p = !1, a = !1, h = !0;
  if (typeof t != "function")
    throw new TypeError(Ie);
  e = H(e) || 0, W(s) && (p = !!s.leading, a = "maxWait" in s, r = a ? Se(H(s.maxWait) || 0, e) : r, h = "trailing" in s ? !!s.trailing : h);
  function u(m) {
    var v = c, R = l;
    return c = l = void 0, x = m, n = t.apply(R, v), n;
  }
  function C(m) {
    return x = m, o = setTimeout(_, e), p ? u(m) : n;
  }
  function w(m) {
    var v = m - i, R = m - x, D = e - v;
    return a ? Re(D, r - R) : D;
  }
  function d(m) {
    var v = m - i, R = m - x;
    return i === void 0 || v >= e || v < 0 || a && R >= r;
  }
  function _() {
    var m = L();
    if (d(m))
      return g(m);
    o = setTimeout(_, w(m));
  }
  function g(m) {
    return o = void 0, h && c ? u(m) : (c = l = void 0, n);
  }
  function y() {
    o !== void 0 && clearTimeout(o), x = 0, c = i = l = o = void 0;
  }
  function f() {
    return o === void 0 ? n : g(L());
  }
  function I() {
    var m = L(), v = d(m);
    if (c = arguments, l = this, i = m, v) {
      if (o === void 0)
        return C(i);
      if (a)
        return clearTimeout(o), o = setTimeout(_, e), u(i);
    }
    return o === void 0 && (o = setTimeout(_, e)), n;
  }
  return I.cancel = y, I.flush = f, I;
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
var Te = E, ke = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), je = Object.prototype.hasOwnProperty, Le = Te.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ne = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function $(t, e, s) {
  var c, l = {}, r = null, n = null;
  s !== void 0 && (r = "" + s), e.key !== void 0 && (r = "" + e.key), e.ref !== void 0 && (n = e.ref);
  for (c in e) je.call(e, c) && !Ne.hasOwnProperty(c) && (l[c] = e[c]);
  if (t && t.defaultProps) for (c in e = t.defaultProps, e) l[c] === void 0 && (l[c] = e[c]);
  return {
    $$typeof: ke,
    type: t,
    key: r,
    ref: n,
    props: l,
    _owner: Le.current
  };
}
j.Fragment = Oe;
j.jsx = $;
j.jsxs = $;
Q.exports = j;
var b = Q.exports;
const {
  SvelteComponent: Ae,
  assign: z,
  binding_callbacks: G,
  check_outros: We,
  children: ee,
  claim_element: te,
  claim_space: Fe,
  component_subscribe: q,
  compute_slots: Me,
  create_slot: Be,
  detach: S,
  element: re,
  empty: V,
  exclude_internal_props: J,
  get_all_dirty_from_scope: De,
  get_slot_changes: Ue,
  group_outros: He,
  init: ze,
  insert_hydration: k,
  safe_not_equal: Ge,
  set_custom_element_data: ne,
  space: qe,
  transition_in: O,
  transition_out: M,
  update_slot_base: Ve
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Ze
} = window.__gradio__svelte__internal;
function X(t) {
  let e, s;
  const c = (
    /*#slots*/
    t[7].default
  ), l = Be(
    c,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = re("svelte-slot"), l && l.c(), this.h();
    },
    l(r) {
      e = te(r, "SVELTE-SLOT", {
        class: !0
      });
      var n = ee(e);
      l && l.l(n), n.forEach(S), this.h();
    },
    h() {
      ne(e, "class", "svelte-1rt0kpf");
    },
    m(r, n) {
      k(r, e, n), l && l.m(e, null), t[9](e), s = !0;
    },
    p(r, n) {
      l && l.p && (!s || n & /*$$scope*/
      64) && Ve(
        l,
        c,
        r,
        /*$$scope*/
        r[6],
        s ? Ue(
          c,
          /*$$scope*/
          r[6],
          n,
          null
        ) : De(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      s || (O(l, r), s = !0);
    },
    o(r) {
      M(l, r), s = !1;
    },
    d(r) {
      r && S(e), l && l.d(r), t[9](null);
    }
  };
}
function Ke(t) {
  let e, s, c, l, r = (
    /*$$slots*/
    t[4].default && X(t)
  );
  return {
    c() {
      e = re("react-portal-target"), s = qe(), r && r.c(), c = V(), this.h();
    },
    l(n) {
      e = te(n, "REACT-PORTAL-TARGET", {
        class: !0
      }), ee(e).forEach(S), s = Fe(n), r && r.l(n), c = V(), this.h();
    },
    h() {
      ne(e, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      k(n, e, o), t[8](e), k(n, s, o), r && r.m(n, o), k(n, c, o), l = !0;
    },
    p(n, [o]) {
      /*$$slots*/
      n[4].default ? r ? (r.p(n, o), o & /*$$slots*/
      16 && O(r, 1)) : (r = X(n), r.c(), O(r, 1), r.m(c.parentNode, c)) : r && (He(), M(r, 1, 1, () => {
        r = null;
      }), We());
    },
    i(n) {
      l || (O(r), l = !0);
    },
    o(n) {
      M(r), l = !1;
    },
    d(n) {
      n && (S(e), S(s), S(c)), t[8](null), r && r.d(n);
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
  let c, l, {
    $$slots: r = {},
    $$scope: n
  } = e;
  const o = Me(r);
  let {
    svelteInit: i
  } = e;
  const x = T(Y(e)), p = T();
  q(t, p, (f) => s(0, c = f));
  const a = T();
  q(t, a, (f) => s(1, l = f));
  const h = [], u = Xe("$$ms-gr-react-wrapper"), {
    slotKey: C,
    slotIndex: w,
    subSlotIndex: d
  } = me() || {}, _ = i({
    parent: u,
    props: x,
    target: p,
    slot: a,
    slotKey: C,
    slotIndex: w,
    subSlotIndex: d,
    onDestroy(f) {
      h.push(f);
    }
  });
  Ze("$$ms-gr-react-wrapper", _), Je(() => {
    x.set(Y(e));
  }), Ye(() => {
    h.forEach((f) => f());
  });
  function g(f) {
    G[f ? "unshift" : "push"](() => {
      c = f, p.set(c);
    });
  }
  function y(f) {
    G[f ? "unshift" : "push"](() => {
      l = f, a.set(l);
    });
  }
  return t.$$set = (f) => {
    s(17, e = z(z({}, e), J(f))), "svelteInit" in f && s(5, i = f.svelteInit), "$$scope" in f && s(6, n = f.$$scope);
  }, e = J(e), [c, l, p, a, o, i, n, r, g, y];
}
class $e extends Ae {
  constructor(e) {
    super(), ze(this, e, Qe, Ke, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ut
} = window.__gradio__svelte__internal, Z = window.ms_globals.rerender, N = window.ms_globals.tree;
function et(t, e = {}) {
  function s(c) {
    const l = T(), r = new $e({
      ...c,
      props: {
        svelteInit(n) {
          window.ms_globals.autokey += 1;
          const o = {
            key: window.ms_globals.autokey,
            svelteInstance: l,
            reactComponent: t,
            props: n.props,
            slot: n.slot,
            target: n.target,
            slotIndex: n.slotIndex,
            subSlotIndex: n.subSlotIndex,
            ignore: e.ignore,
            slotKey: n.slotKey,
            nodes: []
          }, i = n.parent ?? N;
          return i.nodes = [...i.nodes, o], Z({
            createPortal: A,
            node: N
          }), n.onDestroy(() => {
            i.nodes = i.nodes.filter((x) => x.svelteInstance !== l), Z({
              createPortal: A,
              node: N
            });
          }), o;
        },
        ...c.props
      }
    });
    return l.set(r), r;
  }
  return new Promise((c) => {
    window.ms_globals.initializePromise.then(() => {
      c(s);
    });
  });
}
const tt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function rt(t) {
  return t ? Object.keys(t).reduce((e, s) => {
    const c = t[s];
    return e[s] = nt(s, c), e;
  }, {}) : {};
}
function nt(t, e) {
  return typeof e == "number" && !tt.includes(t) ? e + "px" : e;
}
function B(t) {
  const e = [], s = t.cloneNode(!1);
  if (t._reactElement) {
    const l = E.Children.toArray(t._reactElement.props.children).map((r) => {
      if (E.isValidElement(r) && r.props.__slot__) {
        const {
          portals: n,
          clonedElement: o
        } = B(r.props.el);
        return E.cloneElement(r, {
          ...r.props,
          el: o,
          children: [...E.Children.toArray(r.props.children), ...n]
        });
      }
      return null;
    });
    return l.originalChildren = t._reactElement.props.children, e.push(A(E.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: l
    }), s)), {
      clonedElement: s,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((l) => {
    t.getEventListeners(l).forEach(({
      listener: n,
      type: o,
      useCapture: i
    }) => {
      s.addEventListener(o, n, i);
    });
  });
  const c = Array.from(t.childNodes);
  for (let l = 0; l < c.length; l++) {
    const r = c[l];
    if (r.nodeType === 1) {
      const {
        clonedElement: n,
        portals: o
      } = B(r);
      e.push(...o), s.appendChild(n);
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
const P = ce(({
  slot: t,
  clone: e,
  className: s,
  style: c,
  observeAttributes: l
}, r) => {
  const n = oe(), [o, i] = ae([]), {
    forceClone: x
  } = _e(), p = x ? !0 : e;
  return ie(() => {
    var w;
    if (!n.current || !t)
      return;
    let a = t;
    function h() {
      let d = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (d = a.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), lt(r, d), s && d.classList.add(...s.split(" ")), c) {
        const _ = rt(c);
        Object.keys(_).forEach((g) => {
          d.style[g] = _[g];
        });
      }
    }
    let u = null, C = null;
    if (p && window.MutationObserver) {
      let d = function() {
        var f, I, m;
        (f = n.current) != null && f.contains(a) && ((I = n.current) == null || I.removeChild(a));
        const {
          portals: g,
          clonedElement: y
        } = B(t);
        a = y, i(g), a.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          h();
        }, 50), (m = n.current) == null || m.appendChild(a);
      };
      d();
      const _ = Pe(() => {
        d(), u == null || u.disconnect(), u == null || u.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: l
        });
      }, 50);
      u = new window.MutationObserver(_), u.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", h(), (w = n.current) == null || w.appendChild(a);
    return () => {
      var d, _;
      a.style.display = "", (d = n.current) != null && d.contains(a) && ((_ = n.current) == null || _.removeChild(a)), u == null || u.disconnect();
    };
  }, [t, p, s, c, r, l, x]), E.createElement("react-child", {
    ref: n,
    style: {
      display: "contents"
    }
  }, ...o);
}), st = ({
  children: t,
  ...e
}) => /* @__PURE__ */ b.jsx(b.Fragment, {
  children: t(e)
});
function le(t) {
  return E.createElement(st, {
    children: t
  });
}
function se(t, e, s) {
  const c = t.filter(Boolean);
  if (c.length !== 0)
    return c.map((l, r) => {
      var x, p;
      if (typeof l != "object")
        return e != null && e.fallback ? e.fallback(l) : l;
      const n = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...l.props,
        key: ((x = l.props) == null ? void 0 : x.key) ?? (s ? `${s}-${r}` : `${r}`)
      }) : {
        ...l.props,
        key: ((p = l.props) == null ? void 0 : p.key) ?? (s ? `${s}-${r}` : `${r}`)
      };
      let o = n;
      Object.keys(l.slots).forEach((a) => {
        if (!l.slots[a] || !(l.slots[a] instanceof Element) && !l.slots[a].el)
          return;
        const h = a.split(".");
        h.forEach((g, y) => {
          o[g] || (o[g] = {}), y !== h.length - 1 && (o = n[g]);
        });
        const u = l.slots[a];
        let C, w, d = (e == null ? void 0 : e.clone) ?? !1, _ = e == null ? void 0 : e.forceClone;
        u instanceof Element ? C = u : (C = u.el, w = u.callback, d = u.clone ?? d, _ = u.forceClone ?? _), _ = _ ?? !!w, o[h[h.length - 1]] = C ? w ? (...g) => (w(h[h.length - 1], g), /* @__PURE__ */ b.jsx(F, {
          ...l.ctx,
          params: g,
          forceClone: _,
          children: /* @__PURE__ */ b.jsx(P, {
            slot: C,
            clone: d
          })
        })) : le((g) => /* @__PURE__ */ b.jsx(F, {
          ...l.ctx,
          forceClone: _,
          children: /* @__PURE__ */ b.jsx(P, {
            ...g,
            slot: C,
            clone: d
          })
        })) : o[h[h.length - 1]], o = n;
      });
      const i = (e == null ? void 0 : e.children) || "children";
      return l[i] ? n[i] = se(l[i], e, `${r}`) : e != null && e.children && (n[i] = void 0, Reflect.deleteProperty(n, i)), n;
    });
}
function K(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? le((s) => /* @__PURE__ */ b.jsx(F, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ b.jsx(P, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...s
    })
  })) : /* @__PURE__ */ b.jsx(P, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function ct({
  key: t,
  slots: e,
  targets: s
}, c) {
  return e[t] ? (...l) => s ? s.map((r, n) => /* @__PURE__ */ b.jsx(E.Fragment, {
    children: K(r, {
      clone: !0,
      params: l,
      forceClone: (c == null ? void 0 : c.forceClone) ?? !0
    })
  }, n)) : /* @__PURE__ */ b.jsx(b.Fragment, {
    children: K(e[t], {
      clone: !0,
      params: l,
      forceClone: (c == null ? void 0 : c.forceClone) ?? !0
    })
  }) : void 0;
}
const {
  useItems: ot,
  withItemsContextProvider: at,
  ItemHandler: dt
} = ge("antd-breadcrumb-items"), ft = et(at(["default", "items"], ({
  slots: t,
  items: e,
  setSlotParams: s,
  children: c,
  ...l
}) => {
  const {
    items: r
  } = ot(), n = r.items.length > 0 ? r.items : r.default;
  return /* @__PURE__ */ b.jsxs(b.Fragment, {
    children: [/* @__PURE__ */ b.jsx("div", {
      style: {
        display: "none"
      },
      children: c
    }), /* @__PURE__ */ b.jsx(he, {
      ...l,
      itemRender: t.itemRender ? ct({
        slots: t,
        key: "itemRender"
      }, {}) : l.itemRender,
      items: ue(() => e || se(n, {
        // clone: true,
      }), [e, n]),
      separator: t.separator ? /* @__PURE__ */ b.jsx(P, {
        slot: t.separator,
        clone: !0
      }) : l.separator
    })]
  });
}));
export {
  ft as Breadcrumb,
  ft as default
};
