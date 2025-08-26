import { i as Je, a as q, r as Qe, Z as W, g as Xe, b as ze } from "./Index-CMzAlPbO.js";
const O = window.ms_globals.React, He = window.ms_globals.React.forwardRef, De = window.ms_globals.React.useRef, Be = window.ms_globals.React.useState, Ge = window.ms_globals.React.useEffect, N = window.ms_globals.React.useMemo, z = window.ms_globals.ReactDOM.createPortal, qe = window.ms_globals.internalContext.useContextPropsContext, V = window.ms_globals.internalContext.ContextPropsProvider, j = window.ms_globals.antd.Table, G = window.ms_globals.createItemsContext.createItemsContext;
var Ve = /\s/;
function Ke(t) {
  for (var e = t.length; e-- && Ve.test(t.charAt(e)); )
    ;
  return e;
}
var Ye = /^\s+/;
function Ze(t) {
  return t && t.slice(0, Ke(t) + 1).replace(Ye, "");
}
var ce = NaN, $e = /^[-+]0x[0-9a-f]+$/i, et = /^0b[01]+$/i, tt = /^0o[0-7]+$/i, rt = parseInt;
function ue(t) {
  if (typeof t == "number")
    return t;
  if (Je(t))
    return ce;
  if (q(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = q(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Ze(t);
  var n = et.test(t);
  return n || tt.test(t) ? rt(t.slice(2), n ? 2 : 8) : $e.test(t) ? ce : +t;
}
var Q = function() {
  return Qe.Date.now();
}, nt = "Expected a function", lt = Math.max, it = Math.min;
function ot(t, e, n) {
  var o, i, r, l, s, u, C = 0, b = !1, c = !1, _ = !0;
  if (typeof t != "function")
    throw new TypeError(nt);
  e = ue(e) || 0, q(n) && (b = !!n.leading, c = "maxWait" in n, r = c ? lt(ue(n.maxWait) || 0, e) : r, _ = "trailing" in n ? !!n.trailing : _);
  function d(h) {
    var v = o, T = i;
    return o = i = void 0, C = h, l = t.apply(T, v), l;
  }
  function x(h) {
    return C = h, s = setTimeout(m, e), b ? d(h) : l;
  }
  function y(h) {
    var v = h - u, T = h - C, L = e - v;
    return c ? it(L, r - T) : L;
  }
  function a(h) {
    var v = h - u, T = h - C;
    return u === void 0 || v >= e || v < 0 || c && T >= r;
  }
  function m() {
    var h = Q();
    if (a(h))
      return g(h);
    s = setTimeout(m, y(h));
  }
  function g(h) {
    return s = void 0, _ && o ? d(h) : (o = i = void 0, l);
  }
  function E() {
    s !== void 0 && clearTimeout(s), C = 0, o = u = i = s = void 0;
  }
  function f() {
    return s === void 0 ? l : g(Q());
  }
  function P() {
    var h = Q(), v = a(h);
    if (o = arguments, i = this, u = h, v) {
      if (s === void 0)
        return x(u);
      if (c)
        return clearTimeout(s), s = setTimeout(m, e), d(u);
    }
    return s === void 0 && (s = setTimeout(m, e)), l;
  }
  return P.cancel = E, P.flush = f, P;
}
var pe = {
  exports: {}
}, J = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var at = O, st = Symbol.for("react.element"), ct = Symbol.for("react.fragment"), ut = Object.prototype.hasOwnProperty, dt = at.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ft = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function xe(t, e, n) {
  var o, i = {}, r = null, l = null;
  n !== void 0 && (r = "" + n), e.key !== void 0 && (r = "" + e.key), e.ref !== void 0 && (l = e.ref);
  for (o in e) ut.call(e, o) && !ft.hasOwnProperty(o) && (i[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) i[o] === void 0 && (i[o] = e[o]);
  return {
    $$typeof: st,
    type: t,
    key: r,
    ref: l,
    props: i,
    _owner: dt.current
  };
}
J.Fragment = ct;
J.jsx = xe;
J.jsxs = xe;
pe.exports = J;
var w = pe.exports;
const {
  SvelteComponent: ht,
  assign: de,
  binding_callbacks: fe,
  check_outros: mt,
  children: ye,
  claim_element: Ie,
  claim_space: gt,
  component_subscribe: he,
  compute_slots: _t,
  create_slot: wt,
  detach: k,
  element: Ee,
  empty: me,
  exclude_internal_props: ge,
  get_all_dirty_from_scope: Ct,
  get_slot_changes: bt,
  group_outros: pt,
  init: xt,
  insert_hydration: H,
  safe_not_equal: yt,
  set_custom_element_data: ve,
  space: It,
  transition_in: D,
  transition_out: K,
  update_slot_base: Et
} = window.__gradio__svelte__internal, {
  beforeUpdate: vt,
  getContext: St,
  onDestroy: Pt,
  setContext: Tt
} = window.__gradio__svelte__internal;
function _e(t) {
  let e, n;
  const o = (
    /*#slots*/
    t[7].default
  ), i = wt(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = Ee("svelte-slot"), i && i.c(), this.h();
    },
    l(r) {
      e = Ie(r, "SVELTE-SLOT", {
        class: !0
      });
      var l = ye(e);
      i && i.l(l), l.forEach(k), this.h();
    },
    h() {
      ve(e, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      H(r, e, l), i && i.m(e, null), t[9](e), n = !0;
    },
    p(r, l) {
      i && i.p && (!n || l & /*$$scope*/
      64) && Et(
        i,
        o,
        r,
        /*$$scope*/
        r[6],
        n ? bt(
          o,
          /*$$scope*/
          r[6],
          l,
          null
        ) : Ct(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      n || (D(i, r), n = !0);
    },
    o(r) {
      K(i, r), n = !1;
    },
    d(r) {
      r && k(e), i && i.d(r), t[9](null);
    }
  };
}
function Ot(t) {
  let e, n, o, i, r = (
    /*$$slots*/
    t[4].default && _e(t)
  );
  return {
    c() {
      e = Ee("react-portal-target"), n = It(), r && r.c(), o = me(), this.h();
    },
    l(l) {
      e = Ie(l, "REACT-PORTAL-TARGET", {
        class: !0
      }), ye(e).forEach(k), n = gt(l), r && r.l(l), o = me(), this.h();
    },
    h() {
      ve(e, "class", "svelte-1rt0kpf");
    },
    m(l, s) {
      H(l, e, s), t[8](e), H(l, n, s), r && r.m(l, s), H(l, o, s), i = !0;
    },
    p(l, [s]) {
      /*$$slots*/
      l[4].default ? r ? (r.p(l, s), s & /*$$slots*/
      16 && D(r, 1)) : (r = _e(l), r.c(), D(r, 1), r.m(o.parentNode, o)) : r && (pt(), K(r, 1, 1, () => {
        r = null;
      }), mt());
    },
    i(l) {
      i || (D(r), i = !0);
    },
    o(l) {
      K(r), i = !1;
    },
    d(l) {
      l && (k(e), k(n), k(o)), t[8](null), r && r.d(l);
    }
  };
}
function we(t) {
  const {
    svelteInit: e,
    ...n
  } = t;
  return n;
}
function Rt(t, e, n) {
  let o, i, {
    $$slots: r = {},
    $$scope: l
  } = e;
  const s = _t(r);
  let {
    svelteInit: u
  } = e;
  const C = W(we(e)), b = W();
  he(t, b, (f) => n(0, o = f));
  const c = W();
  he(t, c, (f) => n(1, i = f));
  const _ = [], d = St("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: y,
    subSlotIndex: a
  } = Xe() || {}, m = u({
    parent: d,
    props: C,
    target: b,
    slot: c,
    slotKey: x,
    slotIndex: y,
    subSlotIndex: a,
    onDestroy(f) {
      _.push(f);
    }
  });
  Tt("$$ms-gr-react-wrapper", m), vt(() => {
    C.set(we(e));
  }), Pt(() => {
    _.forEach((f) => f());
  });
  function g(f) {
    fe[f ? "unshift" : "push"](() => {
      o = f, b.set(o);
    });
  }
  function E(f) {
    fe[f ? "unshift" : "push"](() => {
      i = f, c.set(i);
    });
  }
  return t.$$set = (f) => {
    n(17, e = de(de({}, e), ge(f))), "svelteInit" in f && n(5, u = f.svelteInit), "$$scope" in f && n(6, l = f.$$scope);
  }, e = ge(e), [o, i, b, c, s, u, l, r, g, E];
}
class kt extends ht {
  constructor(e) {
    super(), xt(this, e, Rt, Ot, yt, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: zt
} = window.__gradio__svelte__internal, Ce = window.ms_globals.rerender, X = window.ms_globals.tree;
function jt(t, e = {}) {
  function n(o) {
    const i = W(), r = new kt({
      ...o,
      props: {
        svelteInit(l) {
          window.ms_globals.autokey += 1;
          const s = {
            key: window.ms_globals.autokey,
            svelteInstance: i,
            reactComponent: t,
            props: l.props,
            slot: l.slot,
            target: l.target,
            slotIndex: l.slotIndex,
            subSlotIndex: l.subSlotIndex,
            ignore: e.ignore,
            slotKey: l.slotKey,
            nodes: []
          }, u = l.parent ?? X;
          return u.nodes = [...u.nodes, s], Ce({
            createPortal: z,
            node: X
          }), l.onDestroy(() => {
            u.nodes = u.nodes.filter((C) => C.svelteInstance !== i), Ce({
              createPortal: z,
              node: X
            });
          }), s;
        },
        ...o.props
      }
    });
    return i.set(r), r;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise.then(() => {
      o(n);
    });
  });
}
const Nt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Lt(t) {
  return t ? Object.keys(t).reduce((e, n) => {
    const o = t[n];
    return e[n] = Ft(n, o), e;
  }, {}) : {};
}
function Ft(t, e) {
  return typeof e == "number" && !Nt.includes(t) ? e + "px" : e;
}
function Y(t) {
  const e = [], n = t.cloneNode(!1);
  if (t._reactElement) {
    const i = O.Children.toArray(t._reactElement.props.children).map((r) => {
      if (O.isValidElement(r) && r.props.__slot__) {
        const {
          portals: l,
          clonedElement: s
        } = Y(r.props.el);
        return O.cloneElement(r, {
          ...r.props,
          el: s,
          children: [...O.Children.toArray(r.props.children), ...l]
        });
      }
      return null;
    });
    return i.originalChildren = t._reactElement.props.children, e.push(z(O.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: i
    }), n)), {
      clonedElement: n,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((i) => {
    t.getEventListeners(i).forEach(({
      listener: l,
      type: s,
      useCapture: u
    }) => {
      n.addEventListener(s, l, u);
    });
  });
  const o = Array.from(t.childNodes);
  for (let i = 0; i < o.length; i++) {
    const r = o[i];
    if (r.nodeType === 1) {
      const {
        clonedElement: l,
        portals: s
      } = Y(r);
      e.push(...s), n.appendChild(l);
    } else r.nodeType === 3 && n.appendChild(r.cloneNode());
  }
  return {
    clonedElement: n,
    portals: e
  };
}
function At(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const R = He(({
  slot: t,
  clone: e,
  className: n,
  style: o,
  observeAttributes: i
}, r) => {
  const l = De(), [s, u] = Be([]), {
    forceClone: C
  } = qe(), b = C ? !0 : e;
  return Ge(() => {
    var y;
    if (!l.current || !t)
      return;
    let c = t;
    function _() {
      let a = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (a = c.children[0], a.tagName.toLowerCase() === "react-portal-target" && a.children[0] && (a = a.children[0])), At(r, a), n && a.classList.add(...n.split(" ")), o) {
        const m = Lt(o);
        Object.keys(m).forEach((g) => {
          a.style[g] = m[g];
        });
      }
    }
    let d = null, x = null;
    if (b && window.MutationObserver) {
      let a = function() {
        var f, P, h;
        (f = l.current) != null && f.contains(c) && ((P = l.current) == null || P.removeChild(c));
        const {
          portals: g,
          clonedElement: E
        } = Y(t);
        c = E, u(g), c.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          _();
        }, 50), (h = l.current) == null || h.appendChild(c);
      };
      a();
      const m = ot(() => {
        a(), d == null || d.disconnect(), d == null || d.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      d = new window.MutationObserver(m), d.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", _(), (y = l.current) == null || y.appendChild(c);
    return () => {
      var a, m;
      c.style.display = "", (a = l.current) != null && a.contains(c) && ((m = l.current) == null || m.removeChild(c)), d == null || d.disconnect();
    };
  }, [t, b, n, o, r, i, C]), O.createElement("react-child", {
    ref: l,
    style: {
      display: "contents"
    }
  }, ...s);
});
function Mt(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function S(t, e = !1) {
  try {
    if (ze(t))
      return t;
    if (e && !Mt(t))
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
function I(t, e) {
  return N(() => S(t, e), [t, e]);
}
function Ut(t, e) {
  return Object.keys(t).reduce((n, o) => (t[o] !== void 0 && (n[o] = t[o]), n), {});
}
const Wt = ({
  children: t,
  ...e
}) => /* @__PURE__ */ w.jsx(w.Fragment, {
  children: t(e)
});
function Se(t) {
  return O.createElement(Wt, {
    children: t
  });
}
function B(t, e, n) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((i, r) => {
      var C, b;
      if (typeof i != "object")
        return e != null && e.fallback ? e.fallback(i) : i;
      const l = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...i.props,
        key: ((C = i.props) == null ? void 0 : C.key) ?? (n ? `${n}-${r}` : `${r}`)
      }) : {
        ...i.props,
        key: ((b = i.props) == null ? void 0 : b.key) ?? (n ? `${n}-${r}` : `${r}`)
      };
      let s = l;
      Object.keys(i.slots).forEach((c) => {
        if (!i.slots[c] || !(i.slots[c] instanceof Element) && !i.slots[c].el)
          return;
        const _ = c.split(".");
        _.forEach((g, E) => {
          s[g] || (s[g] = {}), E !== _.length - 1 && (s = l[g]);
        });
        const d = i.slots[c];
        let x, y, a = (e == null ? void 0 : e.clone) ?? !1, m = e == null ? void 0 : e.forceClone;
        d instanceof Element ? x = d : (x = d.el, y = d.callback, a = d.clone ?? a, m = d.forceClone ?? m), m = m ?? !!y, s[_[_.length - 1]] = x ? y ? (...g) => (y(_[_.length - 1], g), /* @__PURE__ */ w.jsx(V, {
          ...i.ctx,
          params: g,
          forceClone: m,
          children: /* @__PURE__ */ w.jsx(R, {
            slot: x,
            clone: a
          })
        })) : Se((g) => /* @__PURE__ */ w.jsx(V, {
          ...i.ctx,
          forceClone: m,
          children: /* @__PURE__ */ w.jsx(R, {
            ...g,
            slot: x,
            clone: a
          })
        })) : s[_[_.length - 1]], s = l;
      });
      const u = (e == null ? void 0 : e.children) || "children";
      return i[u] ? l[u] = B(i[u], e, `${r}`) : e != null && e.children && (l[u] = void 0, Reflect.deleteProperty(l, u)), l;
    });
}
function be(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? Se((n) => /* @__PURE__ */ w.jsx(V, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ w.jsx(R, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...n
    })
  })) : /* @__PURE__ */ w.jsx(R, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function M({
  key: t,
  slots: e,
  targets: n
}, o) {
  return e[t] ? (...i) => n ? n.map((r, l) => /* @__PURE__ */ w.jsx(O.Fragment, {
    children: be(r, {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }, l)) : /* @__PURE__ */ w.jsx(w.Fragment, {
    children: be(e[t], {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }) : void 0;
}
const {
  useItems: Ht,
  withItemsContextProvider: Dt,
  ItemHandler: qt
} = G("antd-table-columns"), {
  useItems: Vt,
  withItemsContextProvider: Kt,
  ItemHandler: Yt
} = G("antd-table-row-selection-selections"), {
  useItems: Bt,
  withItemsContextProvider: Gt,
  ItemHandler: Zt
} = G("antd-table-row-selection"), {
  useItems: Jt,
  withItemsContextProvider: Qt,
  ItemHandler: $t
} = G("antd-table-expandable");
function U(t) {
  return typeof t == "object" && t !== null ? t : {};
}
const er = jt(Gt(["rowSelection"], Qt(["expandable"], Dt(["default"], ({
  children: t,
  slots: e,
  columns: n,
  getPopupContainer: o,
  pagination: i,
  loading: r,
  rowKey: l,
  rowClassName: s,
  summary: u,
  rowSelection: C,
  expandable: b,
  sticky: c,
  footer: _,
  showSorterTooltip: d,
  onRow: x,
  onHeaderRow: y,
  components: a,
  setSlotParams: m,
  ...g
}) => {
  const {
    items: {
      default: E
    }
  } = Ht(), {
    items: {
      expandable: f
    }
  } = Jt(), {
    items: {
      rowSelection: P
    }
  } = Bt(), h = I(o), v = e["loading.tip"] || e["loading.indicator"], T = U(r), L = e["pagination.showQuickJumper.goButton"] || e["pagination.itemRender"], F = U(i), Pe = I(F.showTotal), Te = I(s), Oe = I(l, !0), Re = e["showSorterTooltip.title"] || typeof d == "object", A = U(d), ke = I(A.afterOpenChange), je = I(A.getPopupContainer), Ne = typeof c == "object", Z = U(c), Le = I(Z.getContainer), Fe = I(x), Ae = I(y), Me = I(u), Ue = I(_), We = N(() => {
    var re, ne, le, ie, oe, ae, se;
    const p = S((re = a == null ? void 0 : a.header) == null ? void 0 : re.table), $ = S((ne = a == null ? void 0 : a.header) == null ? void 0 : ne.row), ee = S((le = a == null ? void 0 : a.header) == null ? void 0 : le.cell), te = S((ie = a == null ? void 0 : a.header) == null ? void 0 : ie.wrapper);
    return {
      table: S(a == null ? void 0 : a.table),
      header: p || $ || ee || te ? {
        table: p,
        row: $,
        cell: ee,
        wrapper: te
      } : void 0,
      body: typeof (a == null ? void 0 : a.body) == "object" ? {
        wrapper: S((oe = a == null ? void 0 : a.body) == null ? void 0 : oe.wrapper),
        row: S((ae = a == null ? void 0 : a.body) == null ? void 0 : ae.row),
        cell: S((se = a == null ? void 0 : a.body) == null ? void 0 : se.cell)
      } : S(a == null ? void 0 : a.body)
    };
  }, [a]);
  return /* @__PURE__ */ w.jsxs(w.Fragment, {
    children: [/* @__PURE__ */ w.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ w.jsx(j, {
      ...g,
      components: We,
      columns: N(() => (n == null ? void 0 : n.map((p) => p === "EXPAND_COLUMN" ? j.EXPAND_COLUMN : p === "SELECTION_COLUMN" ? j.SELECTION_COLUMN : p)) || B(E, {
        fallback: (p) => p === "EXPAND_COLUMN" ? j.EXPAND_COLUMN : p === "SELECTION_COLUMN" ? j.SELECTION_COLUMN : p
      }), [E, n]),
      onRow: Fe,
      onHeaderRow: Ae,
      summary: e.summary ? M({
        slots: e,
        key: "summary"
      }) : Me,
      rowSelection: N(() => {
        var p;
        return C || ((p = B(P)) == null ? void 0 : p[0]);
      }, [C, P]),
      expandable: N(() => {
        var p;
        return b || ((p = B(f)) == null ? void 0 : p[0]);
      }, [b, f]),
      rowClassName: Te,
      rowKey: Oe || l,
      sticky: Ne ? {
        ...Z,
        getContainer: Le
      } : c,
      showSorterTooltip: Re ? {
        ...A,
        afterOpenChange: ke,
        getPopupContainer: je,
        title: e["showSorterTooltip.title"] ? /* @__PURE__ */ w.jsx(R, {
          slot: e["showSorterTooltip.title"]
        }) : A.title
      } : d,
      pagination: L ? Ut({
        ...F,
        showTotal: Pe,
        showQuickJumper: e["pagination.showQuickJumper.goButton"] ? {
          goButton: /* @__PURE__ */ w.jsx(R, {
            slot: e["pagination.showQuickJumper.goButton"]
          })
        } : F.showQuickJumper,
        itemRender: e["pagination.itemRender"] ? M({
          slots: e,
          key: "pagination.itemRender"
        }) : F.itemRender
      }) : i,
      getPopupContainer: h,
      loading: v ? {
        ...T,
        tip: e["loading.tip"] ? /* @__PURE__ */ w.jsx(R, {
          slot: e["loading.tip"]
        }) : T.tip,
        indicator: e["loading.indicator"] ? /* @__PURE__ */ w.jsx(R, {
          slot: e["loading.indicator"]
        }) : T.indicator
      } : r,
      footer: e.footer ? M({
        slots: e,
        key: "footer"
      }) : Ue,
      title: e.title ? M({
        slots: e,
        key: "title"
      }) : g.title
    })]
  });
}))));
export {
  er as Table,
  er as default
};
