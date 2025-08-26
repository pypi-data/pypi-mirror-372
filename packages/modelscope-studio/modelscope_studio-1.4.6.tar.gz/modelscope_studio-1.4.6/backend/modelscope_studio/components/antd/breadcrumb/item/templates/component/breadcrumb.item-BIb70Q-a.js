import { i as me, a as B, r as he, Z as k, g as pe, b as _e } from "./Index-D04DuM2G.js";
const C = window.ms_globals.React, ie = window.ms_globals.React.forwardRef, de = window.ms_globals.React.useRef, ue = window.ms_globals.React.useState, fe = window.ms_globals.React.useEffect, A = window.ms_globals.ReactDOM.createPortal, we = window.ms_globals.internalContext.useContextPropsContext, M = window.ms_globals.internalContext.ContextPropsProvider, re = window.ms_globals.createItemsContext.createItemsContext;
var ge = /\s/;
function ve(r) {
  for (var e = r.length; e-- && ge.test(r.charAt(e)); )
    ;
  return e;
}
var xe = /^\s+/;
function be(r) {
  return r && r.slice(0, ve(r) + 1).replace(xe, "");
}
var G = NaN, Ie = /^[-+]0x[0-9a-f]+$/i, Ce = /^0b[01]+$/i, ye = /^0o[0-7]+$/i, Ee = parseInt;
function q(r) {
  if (typeof r == "number")
    return r;
  if (me(r))
    return G;
  if (B(r)) {
    var e = typeof r.valueOf == "function" ? r.valueOf() : r;
    r = B(e) ? e + "" : e;
  }
  if (typeof r != "string")
    return r === 0 ? r : +r;
  r = be(r);
  var l = Ce.test(r);
  return l || ye.test(r) ? Ee(r.slice(2), l ? 2 : 8) : Ie.test(r) ? G : +r;
}
var W = function() {
  return he.Date.now();
}, Pe = "Expected a function", Se = Math.max, Re = Math.min;
function ke(r, e, l) {
  var s, o, t, n, c, i, w = 0, g = !1, a = !1, p = !0;
  if (typeof r != "function")
    throw new TypeError(Pe);
  e = q(e) || 0, B(l) && (g = !!l.leading, a = "maxWait" in l, t = a ? Se(q(l.maxWait) || 0, e) : t, p = "trailing" in l ? !!l.trailing : p);
  function d(h) {
    var y = s, S = o;
    return s = o = void 0, w = h, n = r.apply(S, y), n;
  }
  function v(h) {
    return w = h, c = setTimeout(m, e), g ? d(h) : n;
  }
  function x(h) {
    var y = h - i, S = h - w, z = e - y;
    return a ? Re(z, t - S) : z;
  }
  function u(h) {
    var y = h - i, S = h - w;
    return i === void 0 || y >= e || y < 0 || a && S >= t;
  }
  function m() {
    var h = W();
    if (u(h))
      return _(h);
    c = setTimeout(m, x(h));
  }
  function _(h) {
    return c = void 0, p && s ? d(h) : (s = o = void 0, n);
  }
  function I() {
    c !== void 0 && clearTimeout(c), w = 0, s = i = o = c = void 0;
  }
  function f() {
    return c === void 0 ? n : _(W());
  }
  function E() {
    var h = W(), y = u(h);
    if (s = arguments, o = this, i = h, y) {
      if (c === void 0)
        return v(i);
      if (a)
        return clearTimeout(c), c = setTimeout(m, e), d(i);
    }
    return c === void 0 && (c = setTimeout(m, e)), n;
  }
  return E.cancel = I, E.flush = f, E;
}
var te = {
  exports: {}
}, N = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Oe = C, Te = Symbol.for("react.element"), je = Symbol.for("react.fragment"), Le = Object.prototype.hasOwnProperty, Ne = Oe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, We = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ne(r, e, l) {
  var s, o = {}, t = null, n = null;
  l !== void 0 && (t = "" + l), e.key !== void 0 && (t = "" + e.key), e.ref !== void 0 && (n = e.ref);
  for (s in e) Le.call(e, s) && !We.hasOwnProperty(s) && (o[s] = e[s]);
  if (r && r.defaultProps) for (s in e = r.defaultProps, e) o[s] === void 0 && (o[s] = e[s]);
  return {
    $$typeof: Te,
    type: r,
    key: t,
    ref: n,
    props: o,
    _owner: Ne.current
  };
}
N.Fragment = je;
N.jsx = ne;
N.jsxs = ne;
te.exports = N;
var b = te.exports;
const {
  SvelteComponent: Fe,
  assign: V,
  binding_callbacks: J,
  check_outros: Ae,
  children: oe,
  claim_element: le,
  claim_space: Be,
  component_subscribe: X,
  compute_slots: Me,
  create_slot: De,
  detach: P,
  element: se,
  empty: Y,
  exclude_internal_props: Z,
  get_all_dirty_from_scope: He,
  get_slot_changes: Ue,
  group_outros: ze,
  init: Ge,
  insert_hydration: O,
  safe_not_equal: qe,
  set_custom_element_data: ce,
  space: Ve,
  transition_in: T,
  transition_out: D,
  update_slot_base: Je
} = window.__gradio__svelte__internal, {
  beforeUpdate: Xe,
  getContext: Ye,
  onDestroy: Ze,
  setContext: Ke
} = window.__gradio__svelte__internal;
function K(r) {
  let e, l;
  const s = (
    /*#slots*/
    r[7].default
  ), o = De(
    s,
    r,
    /*$$scope*/
    r[6],
    null
  );
  return {
    c() {
      e = se("svelte-slot"), o && o.c(), this.h();
    },
    l(t) {
      e = le(t, "SVELTE-SLOT", {
        class: !0
      });
      var n = oe(e);
      o && o.l(n), n.forEach(P), this.h();
    },
    h() {
      ce(e, "class", "svelte-1rt0kpf");
    },
    m(t, n) {
      O(t, e, n), o && o.m(e, null), r[9](e), l = !0;
    },
    p(t, n) {
      o && o.p && (!l || n & /*$$scope*/
      64) && Je(
        o,
        s,
        t,
        /*$$scope*/
        t[6],
        l ? Ue(
          s,
          /*$$scope*/
          t[6],
          n,
          null
        ) : He(
          /*$$scope*/
          t[6]
        ),
        null
      );
    },
    i(t) {
      l || (T(o, t), l = !0);
    },
    o(t) {
      D(o, t), l = !1;
    },
    d(t) {
      t && P(e), o && o.d(t), r[9](null);
    }
  };
}
function Qe(r) {
  let e, l, s, o, t = (
    /*$$slots*/
    r[4].default && K(r)
  );
  return {
    c() {
      e = se("react-portal-target"), l = Ve(), t && t.c(), s = Y(), this.h();
    },
    l(n) {
      e = le(n, "REACT-PORTAL-TARGET", {
        class: !0
      }), oe(e).forEach(P), l = Be(n), t && t.l(n), s = Y(), this.h();
    },
    h() {
      ce(e, "class", "svelte-1rt0kpf");
    },
    m(n, c) {
      O(n, e, c), r[8](e), O(n, l, c), t && t.m(n, c), O(n, s, c), o = !0;
    },
    p(n, [c]) {
      /*$$slots*/
      n[4].default ? t ? (t.p(n, c), c & /*$$slots*/
      16 && T(t, 1)) : (t = K(n), t.c(), T(t, 1), t.m(s.parentNode, s)) : t && (ze(), D(t, 1, 1, () => {
        t = null;
      }), Ae());
    },
    i(n) {
      o || (T(t), o = !0);
    },
    o(n) {
      D(t), o = !1;
    },
    d(n) {
      n && (P(e), P(l), P(s)), r[8](null), t && t.d(n);
    }
  };
}
function Q(r) {
  const {
    svelteInit: e,
    ...l
  } = r;
  return l;
}
function $e(r, e, l) {
  let s, o, {
    $$slots: t = {},
    $$scope: n
  } = e;
  const c = Me(t);
  let {
    svelteInit: i
  } = e;
  const w = k(Q(e)), g = k();
  X(r, g, (f) => l(0, s = f));
  const a = k();
  X(r, a, (f) => l(1, o = f));
  const p = [], d = Ye("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: x,
    subSlotIndex: u
  } = pe() || {}, m = i({
    parent: d,
    props: w,
    target: g,
    slot: a,
    slotKey: v,
    slotIndex: x,
    subSlotIndex: u,
    onDestroy(f) {
      p.push(f);
    }
  });
  Ke("$$ms-gr-react-wrapper", m), Xe(() => {
    w.set(Q(e));
  }), Ze(() => {
    p.forEach((f) => f());
  });
  function _(f) {
    J[f ? "unshift" : "push"](() => {
      s = f, g.set(s);
    });
  }
  function I(f) {
    J[f ? "unshift" : "push"](() => {
      o = f, a.set(o);
    });
  }
  return r.$$set = (f) => {
    l(17, e = V(V({}, e), Z(f))), "svelteInit" in f && l(5, i = f.svelteInit), "$$scope" in f && l(6, n = f.$$scope);
  }, e = Z(e), [s, o, g, a, c, i, n, t, _, I];
}
class er extends Fe {
  constructor(e) {
    super(), Ge(this, e, $e, Qe, qe, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: fr
} = window.__gradio__svelte__internal, $ = window.ms_globals.rerender, F = window.ms_globals.tree;
function rr(r, e = {}) {
  function l(s) {
    const o = k(), t = new er({
      ...s,
      props: {
        svelteInit(n) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: r,
            props: n.props,
            slot: n.slot,
            target: n.target,
            slotIndex: n.slotIndex,
            subSlotIndex: n.subSlotIndex,
            ignore: e.ignore,
            slotKey: n.slotKey,
            nodes: []
          }, i = n.parent ?? F;
          return i.nodes = [...i.nodes, c], $({
            createPortal: A,
            node: F
          }), n.onDestroy(() => {
            i.nodes = i.nodes.filter((w) => w.svelteInstance !== o), $({
              createPortal: A,
              node: F
            });
          }), c;
        },
        ...s.props
      }
    });
    return o.set(t), t;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise.then(() => {
      s(l);
    });
  });
}
function tr(r) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(r.trim());
}
function ee(r, e = !1) {
  try {
    if (_e(r))
      return r;
    if (e && !tr(r))
      return;
    if (typeof r == "string") {
      let l = r.trim();
      return l.startsWith(";") && (l = l.slice(1)), l.endsWith(";") && (l = l.slice(0, -1)), new Function(`return (...args) => (${l})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
const nr = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function or(r) {
  return r ? Object.keys(r).reduce((e, l) => {
    const s = r[l];
    return e[l] = lr(l, s), e;
  }, {}) : {};
}
function lr(r, e) {
  return typeof e == "number" && !nr.includes(r) ? e + "px" : e;
}
function H(r) {
  const e = [], l = r.cloneNode(!1);
  if (r._reactElement) {
    const o = C.Children.toArray(r._reactElement.props.children).map((t) => {
      if (C.isValidElement(t) && t.props.__slot__) {
        const {
          portals: n,
          clonedElement: c
        } = H(t.props.el);
        return C.cloneElement(t, {
          ...t.props,
          el: c,
          children: [...C.Children.toArray(t.props.children), ...n]
        });
      }
      return null;
    });
    return o.originalChildren = r._reactElement.props.children, e.push(A(C.cloneElement(r._reactElement, {
      ...r._reactElement.props,
      children: o
    }), l)), {
      clonedElement: l,
      portals: e
    };
  }
  Object.keys(r.getEventListeners()).forEach((o) => {
    r.getEventListeners(o).forEach(({
      listener: n,
      type: c,
      useCapture: i
    }) => {
      l.addEventListener(c, n, i);
    });
  });
  const s = Array.from(r.childNodes);
  for (let o = 0; o < s.length; o++) {
    const t = s[o];
    if (t.nodeType === 1) {
      const {
        clonedElement: n,
        portals: c
      } = H(t);
      e.push(...c), l.appendChild(n);
    } else t.nodeType === 3 && l.appendChild(t.cloneNode());
  }
  return {
    clonedElement: l,
    portals: e
  };
}
function sr(r, e) {
  r && (typeof r == "function" ? r(e) : r.current = e);
}
const j = ie(({
  slot: r,
  clone: e,
  className: l,
  style: s,
  observeAttributes: o
}, t) => {
  const n = de(), [c, i] = ue([]), {
    forceClone: w
  } = we(), g = w ? !0 : e;
  return fe(() => {
    var x;
    if (!n.current || !r)
      return;
    let a = r;
    function p() {
      let u = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (u = a.children[0], u.tagName.toLowerCase() === "react-portal-target" && u.children[0] && (u = u.children[0])), sr(t, u), l && u.classList.add(...l.split(" ")), s) {
        const m = or(s);
        Object.keys(m).forEach((_) => {
          u.style[_] = m[_];
        });
      }
    }
    let d = null, v = null;
    if (g && window.MutationObserver) {
      let u = function() {
        var f, E, h;
        (f = n.current) != null && f.contains(a) && ((E = n.current) == null || E.removeChild(a));
        const {
          portals: _,
          clonedElement: I
        } = H(r);
        a = I, i(_), a.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          p();
        }, 50), (h = n.current) == null || h.appendChild(a);
      };
      u();
      const m = ke(() => {
        u(), d == null || d.disconnect(), d == null || d.observe(r, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      d = new window.MutationObserver(m), d.observe(r, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", p(), (x = n.current) == null || x.appendChild(a);
    return () => {
      var u, m;
      a.style.display = "", (u = n.current) != null && u.contains(a) && ((m = n.current) == null || m.removeChild(a)), d == null || d.disconnect();
    };
  }, [r, g, l, s, t, o, w]), C.createElement("react-child", {
    ref: n,
    style: {
      display: "contents"
    }
  }, ...c);
}), cr = ({
  children: r,
  ...e
}) => /* @__PURE__ */ b.jsx(b.Fragment, {
  children: r(e)
});
function ae(r) {
  return C.createElement(cr, {
    children: r
  });
}
function U(r, e, l) {
  const s = r.filter(Boolean);
  if (s.length !== 0)
    return s.map((o, t) => {
      var w, g;
      if (typeof o != "object")
        return e != null && e.fallback ? e.fallback(o) : o;
      const n = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...o.props,
        key: ((w = o.props) == null ? void 0 : w.key) ?? (l ? `${l}-${t}` : `${t}`)
      }) : {
        ...o.props,
        key: ((g = o.props) == null ? void 0 : g.key) ?? (l ? `${l}-${t}` : `${t}`)
      };
      let c = n;
      Object.keys(o.slots).forEach((a) => {
        if (!o.slots[a] || !(o.slots[a] instanceof Element) && !o.slots[a].el)
          return;
        const p = a.split(".");
        p.forEach((_, I) => {
          c[_] || (c[_] = {}), I !== p.length - 1 && (c = n[_]);
        });
        const d = o.slots[a];
        let v, x, u = (e == null ? void 0 : e.clone) ?? !1, m = e == null ? void 0 : e.forceClone;
        d instanceof Element ? v = d : (v = d.el, x = d.callback, u = d.clone ?? u, m = d.forceClone ?? m), m = m ?? !!x, c[p[p.length - 1]] = v ? x ? (..._) => (x(p[p.length - 1], _), /* @__PURE__ */ b.jsx(M, {
          ...o.ctx,
          params: _,
          forceClone: m,
          children: /* @__PURE__ */ b.jsx(j, {
            slot: v,
            clone: u
          })
        })) : ae((_) => /* @__PURE__ */ b.jsx(M, {
          ...o.ctx,
          forceClone: m,
          children: /* @__PURE__ */ b.jsx(j, {
            ..._,
            slot: v,
            clone: u
          })
        })) : c[p[p.length - 1]], c = n;
      });
      const i = (e == null ? void 0 : e.children) || "children";
      return o[i] ? n[i] = U(o[i], e, `${t}`) : e != null && e.children && (n[i] = void 0, Reflect.deleteProperty(n, i)), n;
    });
}
function L(r, e) {
  return r ? e != null && e.forceClone || e != null && e.params ? ae((l) => /* @__PURE__ */ b.jsx(M, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ b.jsx(j, {
      slot: r,
      clone: e == null ? void 0 : e.clone,
      ...l
    })
  })) : /* @__PURE__ */ b.jsx(j, {
    slot: r,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function R({
  key: r,
  slots: e,
  targets: l
}, s) {
  return e[r] ? (...o) => l ? l.map((t, n) => /* @__PURE__ */ b.jsx(C.Fragment, {
    children: L(t, {
      clone: !0,
      params: o,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }, n)) : /* @__PURE__ */ b.jsx(b.Fragment, {
    children: L(e[r], {
      clone: !0,
      params: o,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }) : void 0;
}
const {
  useItems: ar,
  withItemsContextProvider: ir,
  ItemHandler: mr
} = re("antd-menu-items"), {
  useItems: hr,
  withItemsContextProvider: pr,
  ItemHandler: dr
} = re("antd-breadcrumb-items"), _r = rr(ir(["menu.items", "dropdownProps.menu.items"], ({
  setSlotParams: r,
  itemSlots: e,
  ...l
}) => {
  const {
    items: {
      "menu.items": s,
      "dropdownProps.menu.items": o
    }
  } = ar();
  return /* @__PURE__ */ b.jsx(dr, {
    ...l,
    itemProps: (t) => {
      var w, g, a, p, d, v, x, u, m, _, I, f;
      const n = {
        ...t.menu || {},
        items: (w = t.menu) != null && w.items || s.length > 0 ? U(s, {
          clone: !0
        }) : void 0,
        expandIcon: R({
          slots: e,
          key: "menu.expandIcon"
        }, {}) || ((g = t.menu) == null ? void 0 : g.expandIcon),
        overflowedIndicator: L(e["menu.overflowedIndicator"]) || ((a = t.menu) == null ? void 0 : a.overflowedIndicator)
      }, c = {
        ...((p = t.dropdownProps) == null ? void 0 : p.menu) || {},
        items: (v = (d = t.dropdownProps) == null ? void 0 : d.menu) != null && v.items || o.length > 0 ? U(o, {
          clone: !0
        }) : void 0,
        expandIcon: R({
          slots: e,
          key: "dropdownProps.menu.expandIcon"
        }, {}) || ((u = (x = t.dropdownProps) == null ? void 0 : x.menu) == null ? void 0 : u.expandIcon),
        overflowedIndicator: L(e["dropdownProps.menu.overflowedIndicator"]) || ((_ = (m = t.dropdownProps) == null ? void 0 : m.menu) == null ? void 0 : _.overflowedIndicator)
      }, i = {
        ...t.dropdownProps || {},
        dropdownRender: e["dropdownProps.dropdownRender"] ? R({
          slots: e,
          key: "dropdownProps.dropdownRender"
        }, {}) : ee((I = t.dropdownProps) == null ? void 0 : I.dropdownRender),
        popupRender: e["dropdownProps.popupRender"] ? R({
          slots: e,
          key: "dropdownProps.popupRender"
        }, {}) : ee((f = t.dropdownProps) == null ? void 0 : f.popupRender),
        menu: Object.values(c).filter(Boolean).length > 0 ? c : void 0
      };
      return {
        ...t,
        menu: Object.values(n).filter(Boolean).length > 0 ? n : void 0,
        dropdownProps: Object.values(i).filter(Boolean).length > 0 ? i : void 0
      };
    }
  });
}));
export {
  _r as BreadcrumbItem,
  _r as default
};
