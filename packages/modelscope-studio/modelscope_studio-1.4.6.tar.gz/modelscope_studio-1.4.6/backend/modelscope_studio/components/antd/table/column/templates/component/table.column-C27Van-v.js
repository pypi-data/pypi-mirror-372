import { i as me, a as W, r as pe, Z as k, g as he, c as G } from "./Index-DHGU-0iG.js";
const b = window.ms_globals.React, ie = window.ms_globals.React.forwardRef, de = window.ms_globals.React.useRef, ue = window.ms_globals.React.useState, fe = window.ms_globals.React.useEffect, A = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, F = window.ms_globals.internalContext.ContextPropsProvider, R = window.ms_globals.createItemsContext.createItemsContext;
var we = /\s/;
function ge(t) {
  for (var e = t.length; e-- && we.test(t.charAt(e)); )
    ;
  return e;
}
var xe = /^\s+/;
function Ie(t) {
  return t && t.slice(0, ge(t) + 1).replace(xe, "");
}
var q = NaN, Ce = /^[-+]0x[0-9a-f]+$/i, be = /^0b[01]+$/i, ve = /^0o[0-7]+$/i, Ee = parseInt;
function V(t) {
  if (typeof t == "number")
    return t;
  if (me(t))
    return q;
  if (W(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = W(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Ie(t);
  var o = be.test(t);
  return o || ve.test(t) ? Ee(t.slice(2), o ? 2 : 8) : Ce.test(t) ? q : +t;
}
var L = function() {
  return pe.Date.now();
}, ye = "Expected a function", Pe = Math.max, Se = Math.min;
function Re(t, e, o) {
  var s, r, n, l, c, i, _ = 0, g = !1, a = !1, p = !0;
  if (typeof t != "function")
    throw new TypeError(ye);
  e = V(e) || 0, W(o) && (g = !!o.leading, a = "maxWait" in o, n = a ? Pe(V(o.maxWait) || 0, e) : n, p = "trailing" in o ? !!o.trailing : p);
  function d(m) {
    var v = s, S = r;
    return s = r = void 0, _ = m, l = t.apply(S, v), l;
  }
  function x(m) {
    return _ = m, c = setTimeout(h, e), g ? d(m) : l;
  }
  function I(m) {
    var v = m - i, S = m - _, z = e - v;
    return a ? Se(z, n - S) : z;
  }
  function u(m) {
    var v = m - i, S = m - _;
    return i === void 0 || v >= e || v < 0 || a && S >= n;
  }
  function h() {
    var m = L();
    if (u(m))
      return w(m);
    c = setTimeout(h, I(m));
  }
  function w(m) {
    return c = void 0, p && s ? d(m) : (s = r = void 0, l);
  }
  function E() {
    c !== void 0 && clearTimeout(c), _ = 0, s = i = r = c = void 0;
  }
  function f() {
    return c === void 0 ? l : w(L());
  }
  function y() {
    var m = L(), v = u(m);
    if (s = arguments, r = this, i = m, v) {
      if (c === void 0)
        return x(i);
      if (a)
        return clearTimeout(c), c = setTimeout(h, e), d(i);
    }
    return c === void 0 && (c = setTimeout(h, e)), l;
  }
  return y.cancel = E, y.flush = f, y;
}
var te = {
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
var ke = b, Te = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), De = Object.prototype.hasOwnProperty, je = ke.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Le = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function re(t, e, o) {
  var s, r = {}, n = null, l = null;
  o !== void 0 && (n = "" + o), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (l = e.ref);
  for (s in e) De.call(e, s) && !Le.hasOwnProperty(s) && (r[s] = e[s]);
  if (t && t.defaultProps) for (s in e = t.defaultProps, e) r[s] === void 0 && (r[s] = e[s]);
  return {
    $$typeof: Te,
    type: t,
    key: n,
    ref: l,
    props: r,
    _owner: je.current
  };
}
j.Fragment = Oe;
j.jsx = re;
j.jsxs = re;
te.exports = j;
var C = te.exports;
const {
  SvelteComponent: Ne,
  assign: J,
  binding_callbacks: X,
  check_outros: He,
  children: ne,
  claim_element: le,
  claim_space: Ae,
  component_subscribe: Y,
  compute_slots: We,
  create_slot: Fe,
  detach: P,
  element: oe,
  empty: Z,
  exclude_internal_props: K,
  get_all_dirty_from_scope: Me,
  get_slot_changes: Be,
  group_outros: Ue,
  init: ze,
  insert_hydration: T,
  safe_not_equal: Ge,
  set_custom_element_data: se,
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
function Q(t) {
  let e, o;
  const s = (
    /*#slots*/
    t[7].default
  ), r = Fe(
    s,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = oe("svelte-slot"), r && r.c(), this.h();
    },
    l(n) {
      e = le(n, "SVELTE-SLOT", {
        class: !0
      });
      var l = ne(e);
      r && r.l(l), l.forEach(P), this.h();
    },
    h() {
      se(e, "class", "svelte-1rt0kpf");
    },
    m(n, l) {
      T(n, e, l), r && r.m(e, null), t[9](e), o = !0;
    },
    p(n, l) {
      r && r.p && (!o || l & /*$$scope*/
      64) && Ve(
        r,
        s,
        n,
        /*$$scope*/
        n[6],
        o ? Be(
          s,
          /*$$scope*/
          n[6],
          l,
          null
        ) : Me(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (O(r, n), o = !0);
    },
    o(n) {
      M(r, n), o = !1;
    },
    d(n) {
      n && P(e), r && r.d(n), t[9](null);
    }
  };
}
function Ke(t) {
  let e, o, s, r, n = (
    /*$$slots*/
    t[4].default && Q(t)
  );
  return {
    c() {
      e = oe("react-portal-target"), o = qe(), n && n.c(), s = Z(), this.h();
    },
    l(l) {
      e = le(l, "REACT-PORTAL-TARGET", {
        class: !0
      }), ne(e).forEach(P), o = Ae(l), n && n.l(l), s = Z(), this.h();
    },
    h() {
      se(e, "class", "svelte-1rt0kpf");
    },
    m(l, c) {
      T(l, e, c), t[8](e), T(l, o, c), n && n.m(l, c), T(l, s, c), r = !0;
    },
    p(l, [c]) {
      /*$$slots*/
      l[4].default ? n ? (n.p(l, c), c & /*$$slots*/
      16 && O(n, 1)) : (n = Q(l), n.c(), O(n, 1), n.m(s.parentNode, s)) : n && (Ue(), M(n, 1, 1, () => {
        n = null;
      }), He());
    },
    i(l) {
      r || (O(n), r = !0);
    },
    o(l) {
      M(n), r = !1;
    },
    d(l) {
      l && (P(e), P(o), P(s)), t[8](null), n && n.d(l);
    }
  };
}
function $(t) {
  const {
    svelteInit: e,
    ...o
  } = t;
  return o;
}
function Qe(t, e, o) {
  let s, r, {
    $$slots: n = {},
    $$scope: l
  } = e;
  const c = We(n);
  let {
    svelteInit: i
  } = e;
  const _ = k($(e)), g = k();
  Y(t, g, (f) => o(0, s = f));
  const a = k();
  Y(t, a, (f) => o(1, r = f));
  const p = [], d = Xe("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: I,
    subSlotIndex: u
  } = he() || {}, h = i({
    parent: d,
    props: _,
    target: g,
    slot: a,
    slotKey: x,
    slotIndex: I,
    subSlotIndex: u,
    onDestroy(f) {
      p.push(f);
    }
  });
  Ze("$$ms-gr-react-wrapper", h), Je(() => {
    _.set($(e));
  }), Ye(() => {
    p.forEach((f) => f());
  });
  function w(f) {
    X[f ? "unshift" : "push"](() => {
      s = f, g.set(s);
    });
  }
  function E(f) {
    X[f ? "unshift" : "push"](() => {
      r = f, a.set(r);
    });
  }
  return t.$$set = (f) => {
    o(17, e = J(J({}, e), K(f))), "svelteInit" in f && o(5, i = f.svelteInit), "$$scope" in f && o(6, l = f.$$scope);
  }, e = K(e), [s, r, g, a, c, i, l, n, w, E];
}
class $e extends Ne {
  constructor(e) {
    super(), ze(this, e, Qe, Ke, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: dt
} = window.__gradio__svelte__internal, ee = window.ms_globals.rerender, N = window.ms_globals.tree;
function et(t, e = {}) {
  function o(s) {
    const r = k(), n = new $e({
      ...s,
      props: {
        svelteInit(l) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
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
          return i.nodes = [...i.nodes, c], ee({
            createPortal: A,
            node: N
          }), l.onDestroy(() => {
            i.nodes = i.nodes.filter((_) => _.svelteInstance !== r), ee({
              createPortal: A,
              node: N
            });
          }), c;
        },
        ...s.props
      }
    });
    return r.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise.then(() => {
      s(o);
    });
  });
}
const tt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function rt(t) {
  return t ? Object.keys(t).reduce((e, o) => {
    const s = t[o];
    return e[o] = nt(o, s), e;
  }, {}) : {};
}
function nt(t, e) {
  return typeof e == "number" && !tt.includes(t) ? e + "px" : e;
}
function B(t) {
  const e = [], o = t.cloneNode(!1);
  if (t._reactElement) {
    const r = b.Children.toArray(t._reactElement.props.children).map((n) => {
      if (b.isValidElement(n) && n.props.__slot__) {
        const {
          portals: l,
          clonedElement: c
        } = B(n.props.el);
        return b.cloneElement(n, {
          ...n.props,
          el: c,
          children: [...b.Children.toArray(n.props.children), ...l]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(A(b.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: r
    }), o)), {
      clonedElement: o,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((r) => {
    t.getEventListeners(r).forEach(({
      listener: l,
      type: c,
      useCapture: i
    }) => {
      o.addEventListener(c, l, i);
    });
  });
  const s = Array.from(t.childNodes);
  for (let r = 0; r < s.length; r++) {
    const n = s[r];
    if (n.nodeType === 1) {
      const {
        clonedElement: l,
        portals: c
      } = B(n);
      e.push(...c), o.appendChild(l);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: e
  };
}
function lt(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const D = ie(({
  slot: t,
  clone: e,
  className: o,
  style: s,
  observeAttributes: r
}, n) => {
  const l = de(), [c, i] = ue([]), {
    forceClone: _
  } = _e(), g = _ ? !0 : e;
  return fe(() => {
    var I;
    if (!l.current || !t)
      return;
    let a = t;
    function p() {
      let u = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (u = a.children[0], u.tagName.toLowerCase() === "react-portal-target" && u.children[0] && (u = u.children[0])), lt(n, u), o && u.classList.add(...o.split(" ")), s) {
        const h = rt(s);
        Object.keys(h).forEach((w) => {
          u.style[w] = h[w];
        });
      }
    }
    let d = null, x = null;
    if (g && window.MutationObserver) {
      let u = function() {
        var f, y, m;
        (f = l.current) != null && f.contains(a) && ((y = l.current) == null || y.removeChild(a));
        const {
          portals: w,
          clonedElement: E
        } = B(t);
        a = E, i(w), a.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          p();
        }, 50), (m = l.current) == null || m.appendChild(a);
      };
      u();
      const h = Re(() => {
        u(), d == null || d.disconnect(), d == null || d.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      d = new window.MutationObserver(h), d.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", p(), (I = l.current) == null || I.appendChild(a);
    return () => {
      var u, h;
      a.style.display = "", (u = l.current) != null && u.contains(a) && ((h = l.current) == null || h.removeChild(a)), d == null || d.disconnect();
    };
  }, [t, g, o, s, n, r, _]), b.createElement("react-child", {
    ref: l,
    style: {
      display: "contents"
    }
  }, ...c);
}), ot = ({
  children: t,
  ...e
}) => /* @__PURE__ */ C.jsx(C.Fragment, {
  children: t(e)
});
function ce(t) {
  return b.createElement(ot, {
    children: t
  });
}
function ae(t, e, o) {
  const s = t.filter(Boolean);
  if (s.length !== 0)
    return s.map((r, n) => {
      var _, g;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const l = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((_ = r.props) == null ? void 0 : _.key) ?? (o ? `${o}-${n}` : `${n}`)
      }) : {
        ...r.props,
        key: ((g = r.props) == null ? void 0 : g.key) ?? (o ? `${o}-${n}` : `${n}`)
      };
      let c = l;
      Object.keys(r.slots).forEach((a) => {
        if (!r.slots[a] || !(r.slots[a] instanceof Element) && !r.slots[a].el)
          return;
        const p = a.split(".");
        p.forEach((w, E) => {
          c[w] || (c[w] = {}), E !== p.length - 1 && (c = l[w]);
        });
        const d = r.slots[a];
        let x, I, u = (e == null ? void 0 : e.clone) ?? !1, h = e == null ? void 0 : e.forceClone;
        d instanceof Element ? x = d : (x = d.el, I = d.callback, u = d.clone ?? u, h = d.forceClone ?? h), h = h ?? !!I, c[p[p.length - 1]] = x ? I ? (...w) => (I(p[p.length - 1], w), /* @__PURE__ */ C.jsx(F, {
          ...r.ctx,
          params: w,
          forceClone: h,
          children: /* @__PURE__ */ C.jsx(D, {
            slot: x,
            clone: u
          })
        })) : ce((w) => /* @__PURE__ */ C.jsx(F, {
          ...r.ctx,
          forceClone: h,
          children: /* @__PURE__ */ C.jsx(D, {
            ...w,
            slot: x,
            clone: u
          })
        })) : c[p[p.length - 1]], c = l;
      });
      const i = (e == null ? void 0 : e.children) || "children";
      return r[i] ? l[i] = ae(r[i], e, `${n}`) : e != null && e.children && (l[i] = void 0, Reflect.deleteProperty(l, i)), l;
    });
}
function U(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? ce((o) => /* @__PURE__ */ C.jsx(F, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ C.jsx(D, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...o
    })
  })) : /* @__PURE__ */ C.jsx(D, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function H({
  key: t,
  slots: e,
  targets: o
}, s) {
  return e[t] ? (...r) => o ? o.map((n, l) => /* @__PURE__ */ C.jsx(b.Fragment, {
    children: U(n, {
      clone: !0,
      params: r,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }, l)) : /* @__PURE__ */ C.jsx(C.Fragment, {
    children: U(e[t], {
      clone: !0,
      params: r,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }) : void 0;
}
const {
  useItems: st,
  withItemsContextProvider: ct,
  ItemHandler: ut
} = R("antd-menu-items"), {
  useItems: ft,
  withItemsContextProvider: mt,
  ItemHandler: at
} = R("antd-table-columns"), {
  useItems: pt,
  withItemsContextProvider: ht,
  ItemHandler: _t
} = R("antd-table-row-selection-selections"), {
  useItems: wt,
  withItemsContextProvider: gt,
  ItemHandler: xt
} = R("antd-table-row-selection"), {
  useItems: It,
  withItemsContextProvider: Ct,
  ItemHandler: bt
} = R("antd-table-expandable"), vt = et(ct(["filterDropdownProps.menu.items"], ({
  setSlotParams: t,
  itemSlots: e,
  ...o
}) => {
  const {
    items: {
      "filterDropdownProps.menu.items": s
    }
  } = st();
  return /* @__PURE__ */ C.jsx(at, {
    ...o,
    itemProps: (r) => {
      var c, i, _, g, a, p, d, x, I;
      const n = {
        ...((c = r.filterDropdownProps) == null ? void 0 : c.menu) || {},
        items: (_ = (i = r.filterDropdownProps) == null ? void 0 : i.menu) != null && _.items || s.length > 0 ? ae(s, {
          clone: !0
        }) : void 0,
        expandIcon: H({
          slots: e,
          key: "filterDropdownProps.menu.expandIcon"
        }, {}) || ((a = (g = r.filterDropdownProps) == null ? void 0 : g.menu) == null ? void 0 : a.expandIcon),
        overflowedIndicator: U(e["filterDropdownProps.menu.overflowedIndicator"]) || ((d = (p = r.filterDropdownProps) == null ? void 0 : p.menu) == null ? void 0 : d.overflowedIndicator)
      }, l = {
        ...r.filterDropdownProps || {},
        dropdownRender: e["filterDropdownProps.dropdownRender"] ? H({
          slots: e,
          key: "filterDropdownProps.dropdownRender"
        }, {}) : G((x = r.filterDropdownProps) == null ? void 0 : x.dropdownRender),
        popupRender: e["filterDropdownProps.popupRender"] ? H({
          slots: e,
          key: "filterDropdownProps.popupRender"
        }, {}) : G((I = r.filterDropdownProps) == null ? void 0 : I.popupRender),
        menu: Object.values(n).filter(Boolean).length > 0 ? n : void 0
      };
      return {
        ...r,
        filterDropdownProps: Object.values(l).filter(Boolean).length > 0 ? l : void 0
      };
    }
  });
}));
export {
  vt as TableColumn,
  vt as default
};
