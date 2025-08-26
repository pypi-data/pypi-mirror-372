import { i as fe, a as W, r as de, Z as R, g as me, b as _e } from "./Index-BuyVLakd.js";
const v = window.ms_globals.React, Q = window.ms_globals.React.useMemo, ce = window.ms_globals.React.forwardRef, ie = window.ms_globals.React.useRef, ae = window.ms_globals.React.useState, ue = window.ms_globals.React.useEffect, N = window.ms_globals.ReactDOM.createPortal, he = window.ms_globals.internalContext.useContextPropsContext, A = window.ms_globals.internalContext.ContextPropsProvider, ge = window.ms_globals.antd.Collapse, pe = window.ms_globals.createItemsContext.createItemsContext;
var xe = /\s/;
function be(t) {
  for (var e = t.length; e-- && xe.test(t.charAt(e)); )
    ;
  return e;
}
var we = /^\s+/;
function Ce(t) {
  return t && t.slice(0, be(t) + 1).replace(we, "");
}
var B = NaN, ve = /^[-+]0x[0-9a-f]+$/i, ye = /^0b[01]+$/i, Ee = /^0o[0-7]+$/i, Ie = parseInt;
function H(t) {
  if (typeof t == "number")
    return t;
  if (fe(t))
    return B;
  if (W(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = W(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Ce(t);
  var s = ye.test(t);
  return s || Ee.test(t) ? Ie(t.slice(2), s ? 2 : 8) : ve.test(t) ? B : +t;
}
var L = function() {
  return de.Date.now();
}, Se = "Expected a function", Pe = Math.max, Re = Math.min;
function ke(t, e, s) {
  var o, l, r, n, c, a, h = 0, b = !1, i = !1, g = !0;
  if (typeof t != "function")
    throw new TypeError(Se);
  e = H(e) || 0, W(s) && (b = !!s.leading, i = "maxWait" in s, r = i ? Pe(H(s.maxWait) || 0, e) : r, g = "trailing" in s ? !!s.trailing : g);
  function u(m) {
    var y = o, P = l;
    return o = l = void 0, h = m, n = t.apply(P, y), n;
  }
  function w(m) {
    return h = m, c = setTimeout(_, e), b ? u(m) : n;
  }
  function C(m) {
    var y = m - a, P = m - h, U = e - y;
    return i ? Re(U, r - P) : U;
  }
  function f(m) {
    var y = m - a, P = m - h;
    return a === void 0 || y >= e || y < 0 || i && P >= r;
  }
  function _() {
    var m = L();
    if (f(m))
      return p(m);
    c = setTimeout(_, C(m));
  }
  function p(m) {
    return c = void 0, g && o ? u(m) : (o = l = void 0, n);
  }
  function E() {
    c !== void 0 && clearTimeout(c), h = 0, o = a = l = c = void 0;
  }
  function d() {
    return c === void 0 ? n : p(L());
  }
  function I() {
    var m = L(), y = f(m);
    if (o = arguments, l = this, a = m, y) {
      if (c === void 0)
        return w(a);
      if (i)
        return clearTimeout(c), c = setTimeout(_, e), u(a);
    }
    return c === void 0 && (c = setTimeout(_, e)), n;
  }
  return I.cancel = E, I.flush = d, I;
}
var $ = {
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
var Te = v, Oe = Symbol.for("react.element"), je = Symbol.for("react.fragment"), Le = Object.prototype.hasOwnProperty, Fe = Te.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ne = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ee(t, e, s) {
  var o, l = {}, r = null, n = null;
  s !== void 0 && (r = "" + s), e.key !== void 0 && (r = "" + e.key), e.ref !== void 0 && (n = e.ref);
  for (o in e) Le.call(e, o) && !Ne.hasOwnProperty(o) && (l[o] = e[o]);
  if (t && t.defaultProps) for (o in e = t.defaultProps, e) l[o] === void 0 && (l[o] = e[o]);
  return {
    $$typeof: Oe,
    type: t,
    key: r,
    ref: n,
    props: l,
    _owner: Fe.current
  };
}
j.Fragment = je;
j.jsx = ee;
j.jsxs = ee;
$.exports = j;
var x = $.exports;
const {
  SvelteComponent: We,
  assign: z,
  binding_callbacks: G,
  check_outros: Ae,
  children: te,
  claim_element: re,
  claim_space: Me,
  component_subscribe: q,
  compute_slots: De,
  create_slot: Ue,
  detach: S,
  element: ne,
  empty: V,
  exclude_internal_props: J,
  get_all_dirty_from_scope: Be,
  get_slot_changes: He,
  group_outros: ze,
  init: Ge,
  insert_hydration: k,
  safe_not_equal: qe,
  set_custom_element_data: le,
  space: Ve,
  transition_in: T,
  transition_out: M,
  update_slot_base: Je
} = window.__gradio__svelte__internal, {
  beforeUpdate: Xe,
  getContext: Ye,
  onDestroy: Ze,
  setContext: Ke
} = window.__gradio__svelte__internal;
function X(t) {
  let e, s;
  const o = (
    /*#slots*/
    t[7].default
  ), l = Ue(
    o,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = ne("svelte-slot"), l && l.c(), this.h();
    },
    l(r) {
      e = re(r, "SVELTE-SLOT", {
        class: !0
      });
      var n = te(e);
      l && l.l(n), n.forEach(S), this.h();
    },
    h() {
      le(e, "class", "svelte-1rt0kpf");
    },
    m(r, n) {
      k(r, e, n), l && l.m(e, null), t[9](e), s = !0;
    },
    p(r, n) {
      l && l.p && (!s || n & /*$$scope*/
      64) && Je(
        l,
        o,
        r,
        /*$$scope*/
        r[6],
        s ? He(
          o,
          /*$$scope*/
          r[6],
          n,
          null
        ) : Be(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      s || (T(l, r), s = !0);
    },
    o(r) {
      M(l, r), s = !1;
    },
    d(r) {
      r && S(e), l && l.d(r), t[9](null);
    }
  };
}
function Qe(t) {
  let e, s, o, l, r = (
    /*$$slots*/
    t[4].default && X(t)
  );
  return {
    c() {
      e = ne("react-portal-target"), s = Ve(), r && r.c(), o = V(), this.h();
    },
    l(n) {
      e = re(n, "REACT-PORTAL-TARGET", {
        class: !0
      }), te(e).forEach(S), s = Me(n), r && r.l(n), o = V(), this.h();
    },
    h() {
      le(e, "class", "svelte-1rt0kpf");
    },
    m(n, c) {
      k(n, e, c), t[8](e), k(n, s, c), r && r.m(n, c), k(n, o, c), l = !0;
    },
    p(n, [c]) {
      /*$$slots*/
      n[4].default ? r ? (r.p(n, c), c & /*$$slots*/
      16 && T(r, 1)) : (r = X(n), r.c(), T(r, 1), r.m(o.parentNode, o)) : r && (ze(), M(r, 1, 1, () => {
        r = null;
      }), Ae());
    },
    i(n) {
      l || (T(r), l = !0);
    },
    o(n) {
      M(r), l = !1;
    },
    d(n) {
      n && (S(e), S(s), S(o)), t[8](null), r && r.d(n);
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
function $e(t, e, s) {
  let o, l, {
    $$slots: r = {},
    $$scope: n
  } = e;
  const c = De(r);
  let {
    svelteInit: a
  } = e;
  const h = R(Y(e)), b = R();
  q(t, b, (d) => s(0, o = d));
  const i = R();
  q(t, i, (d) => s(1, l = d));
  const g = [], u = Ye("$$ms-gr-react-wrapper"), {
    slotKey: w,
    slotIndex: C,
    subSlotIndex: f
  } = me() || {}, _ = a({
    parent: u,
    props: h,
    target: b,
    slot: i,
    slotKey: w,
    slotIndex: C,
    subSlotIndex: f,
    onDestroy(d) {
      g.push(d);
    }
  });
  Ke("$$ms-gr-react-wrapper", _), Xe(() => {
    h.set(Y(e));
  }), Ze(() => {
    g.forEach((d) => d());
  });
  function p(d) {
    G[d ? "unshift" : "push"](() => {
      o = d, b.set(o);
    });
  }
  function E(d) {
    G[d ? "unshift" : "push"](() => {
      l = d, i.set(l);
    });
  }
  return t.$$set = (d) => {
    s(17, e = z(z({}, e), J(d))), "svelteInit" in d && s(5, a = d.svelteInit), "$$scope" in d && s(6, n = d.$$scope);
  }, e = J(e), [o, l, b, i, c, a, n, r, p, E];
}
class et extends We {
  constructor(e) {
    super(), Ge(this, e, $e, Qe, qe, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: _t
} = window.__gradio__svelte__internal, Z = window.ms_globals.rerender, F = window.ms_globals.tree;
function tt(t, e = {}) {
  function s(o) {
    const l = R(), r = new et({
      ...o,
      props: {
        svelteInit(n) {
          window.ms_globals.autokey += 1;
          const c = {
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
          }, a = n.parent ?? F;
          return a.nodes = [...a.nodes, c], Z({
            createPortal: N,
            node: F
          }), n.onDestroy(() => {
            a.nodes = a.nodes.filter((h) => h.svelteInstance !== l), Z({
              createPortal: N,
              node: F
            });
          }), c;
        },
        ...o.props
      }
    });
    return l.set(r), r;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise.then(() => {
      o(s);
    });
  });
}
function rt(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function nt(t, e = !1) {
  try {
    if (_e(t))
      return t;
    if (e && !rt(t))
      return;
    if (typeof t == "string") {
      let s = t.trim();
      return s.startsWith(";") && (s = s.slice(1)), s.endsWith(";") && (s = s.slice(0, -1)), new Function(`return (...args) => (${s})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function lt(t, e) {
  return Q(() => nt(t, e), [t, e]);
}
const st = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function ot(t) {
  return t ? Object.keys(t).reduce((e, s) => {
    const o = t[s];
    return e[s] = ct(s, o), e;
  }, {}) : {};
}
function ct(t, e) {
  return typeof e == "number" && !st.includes(t) ? e + "px" : e;
}
function D(t) {
  const e = [], s = t.cloneNode(!1);
  if (t._reactElement) {
    const l = v.Children.toArray(t._reactElement.props.children).map((r) => {
      if (v.isValidElement(r) && r.props.__slot__) {
        const {
          portals: n,
          clonedElement: c
        } = D(r.props.el);
        return v.cloneElement(r, {
          ...r.props,
          el: c,
          children: [...v.Children.toArray(r.props.children), ...n]
        });
      }
      return null;
    });
    return l.originalChildren = t._reactElement.props.children, e.push(N(v.cloneElement(t._reactElement, {
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
      type: c,
      useCapture: a
    }) => {
      s.addEventListener(c, n, a);
    });
  });
  const o = Array.from(t.childNodes);
  for (let l = 0; l < o.length; l++) {
    const r = o[l];
    if (r.nodeType === 1) {
      const {
        clonedElement: n,
        portals: c
      } = D(r);
      e.push(...c), s.appendChild(n);
    } else r.nodeType === 3 && s.appendChild(r.cloneNode());
  }
  return {
    clonedElement: s,
    portals: e
  };
}
function it(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const O = ce(({
  slot: t,
  clone: e,
  className: s,
  style: o,
  observeAttributes: l
}, r) => {
  const n = ie(), [c, a] = ae([]), {
    forceClone: h
  } = he(), b = h ? !0 : e;
  return ue(() => {
    var C;
    if (!n.current || !t)
      return;
    let i = t;
    function g() {
      let f = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (f = i.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), it(r, f), s && f.classList.add(...s.split(" ")), o) {
        const _ = ot(o);
        Object.keys(_).forEach((p) => {
          f.style[p] = _[p];
        });
      }
    }
    let u = null, w = null;
    if (b && window.MutationObserver) {
      let f = function() {
        var d, I, m;
        (d = n.current) != null && d.contains(i) && ((I = n.current) == null || I.removeChild(i));
        const {
          portals: p,
          clonedElement: E
        } = D(t);
        i = E, a(p), i.style.display = "contents", w && clearTimeout(w), w = setTimeout(() => {
          g();
        }, 50), (m = n.current) == null || m.appendChild(i);
      };
      f();
      const _ = ke(() => {
        f(), u == null || u.disconnect(), u == null || u.observe(t, {
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
      i.style.display = "contents", g(), (C = n.current) == null || C.appendChild(i);
    return () => {
      var f, _;
      i.style.display = "", (f = n.current) != null && f.contains(i) && ((_ = n.current) == null || _.removeChild(i)), u == null || u.disconnect();
    };
  }, [t, b, s, o, r, l, h]), v.createElement("react-child", {
    ref: n,
    style: {
      display: "contents"
    }
  }, ...c);
}), at = ({
  children: t,
  ...e
}) => /* @__PURE__ */ x.jsx(x.Fragment, {
  children: t(e)
});
function se(t) {
  return v.createElement(at, {
    children: t
  });
}
function oe(t, e, s) {
  const o = t.filter(Boolean);
  if (o.length !== 0)
    return o.map((l, r) => {
      var h, b;
      if (typeof l != "object")
        return e != null && e.fallback ? e.fallback(l) : l;
      const n = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...l.props,
        key: ((h = l.props) == null ? void 0 : h.key) ?? (s ? `${s}-${r}` : `${r}`)
      }) : {
        ...l.props,
        key: ((b = l.props) == null ? void 0 : b.key) ?? (s ? `${s}-${r}` : `${r}`)
      };
      let c = n;
      Object.keys(l.slots).forEach((i) => {
        if (!l.slots[i] || !(l.slots[i] instanceof Element) && !l.slots[i].el)
          return;
        const g = i.split(".");
        g.forEach((p, E) => {
          c[p] || (c[p] = {}), E !== g.length - 1 && (c = n[p]);
        });
        const u = l.slots[i];
        let w, C, f = (e == null ? void 0 : e.clone) ?? !1, _ = e == null ? void 0 : e.forceClone;
        u instanceof Element ? w = u : (w = u.el, C = u.callback, f = u.clone ?? f, _ = u.forceClone ?? _), _ = _ ?? !!C, c[g[g.length - 1]] = w ? C ? (...p) => (C(g[g.length - 1], p), /* @__PURE__ */ x.jsx(A, {
          ...l.ctx,
          params: p,
          forceClone: _,
          children: /* @__PURE__ */ x.jsx(O, {
            slot: w,
            clone: f
          })
        })) : se((p) => /* @__PURE__ */ x.jsx(A, {
          ...l.ctx,
          forceClone: _,
          children: /* @__PURE__ */ x.jsx(O, {
            ...p,
            slot: w,
            clone: f
          })
        })) : c[g[g.length - 1]], c = n;
      });
      const a = (e == null ? void 0 : e.children) || "children";
      return l[a] ? n[a] = oe(l[a], e, `${r}`) : e != null && e.children && (n[a] = void 0, Reflect.deleteProperty(n, a)), n;
    });
}
function K(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? se((s) => /* @__PURE__ */ x.jsx(A, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ x.jsx(O, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...s
    })
  })) : /* @__PURE__ */ x.jsx(O, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function ut({
  key: t,
  slots: e,
  targets: s
}, o) {
  return e[t] ? (...l) => s ? s.map((r, n) => /* @__PURE__ */ x.jsx(v.Fragment, {
    children: K(r, {
      clone: !0,
      params: l,
      forceClone: !0
    })
  }, n)) : /* @__PURE__ */ x.jsx(x.Fragment, {
    children: K(e[t], {
      clone: !0,
      params: l,
      forceClone: !0
    })
  }) : void 0;
}
const {
  withItemsContextProvider: ft,
  useItems: dt,
  ItemHandler: ht
} = pe("antd-collapse-items"), gt = tt(ft(["default", "items"], ({
  slots: t,
  items: e,
  children: s,
  onChange: o,
  setSlotParams: l,
  expandIcon: r,
  ...n
}) => {
  const {
    items: c
  } = dt(), a = c.items.length > 0 ? c.items : c.default, h = lt(r);
  return /* @__PURE__ */ x.jsxs(x.Fragment, {
    children: [/* @__PURE__ */ x.jsx("div", {
      style: {
        display: "none"
      },
      children: s
    }), /* @__PURE__ */ x.jsx(ge, {
      ...n,
      onChange: (b) => {
        o == null || o(b);
      },
      expandIcon: t.expandIcon ? ut({
        slots: t,
        key: "expandIcon"
      }) : h,
      items: Q(() => e || oe(a, {
        // for the children slot
        // clone: true,
      }), [e, a])
    })]
  });
}));
export {
  gt as Collapse,
  gt as default
};
