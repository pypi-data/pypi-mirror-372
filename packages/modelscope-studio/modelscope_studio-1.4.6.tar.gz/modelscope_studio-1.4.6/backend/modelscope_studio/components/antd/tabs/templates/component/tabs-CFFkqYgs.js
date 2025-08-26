import { i as fe, a as W, r as me, Z as j, g as _e, b as he } from "./Index-rodnQZMQ.js";
const w = window.ms_globals.React, ae = window.ms_globals.React.forwardRef, ce = window.ms_globals.React.useRef, ue = window.ms_globals.React.useState, de = window.ms_globals.React.useEffect, $ = window.ms_globals.React.useMemo, N = window.ms_globals.ReactDOM.createPortal, pe = window.ms_globals.internalContext.useContextPropsContext, A = window.ms_globals.internalContext.ContextPropsProvider, ge = window.ms_globals.antd.Tabs, be = window.ms_globals.createItemsContext.createItemsContext;
var xe = /\s/;
function Ce(e) {
  for (var t = e.length; t-- && xe.test(e.charAt(t)); )
    ;
  return t;
}
var Ee = /^\s+/;
function ve(e) {
  return e && e.slice(0, Ce(e) + 1).replace(Ee, "");
}
var U = NaN, we = /^[-+]0x[0-9a-f]+$/i, ye = /^0b[01]+$/i, Ie = /^0o[0-7]+$/i, Se = parseInt;
function H(e) {
  if (typeof e == "number")
    return e;
  if (fe(e))
    return U;
  if (W(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = W(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = ve(e);
  var s = ye.test(e);
  return s || Ie.test(e) ? Se(e.slice(2), s ? 2 : 8) : we.test(e) ? U : +e;
}
var B = function() {
  return me.Date.now();
}, Te = "Expected a function", Pe = Math.max, je = Math.min;
function Re(e, t, s) {
  var l, n, r, o, i, c, g = 0, b = !1, a = !1, p = !0;
  if (typeof e != "function")
    throw new TypeError(Te);
  t = H(t) || 0, W(s) && (b = !!s.leading, a = "maxWait" in s, r = a ? Pe(H(s.maxWait) || 0, t) : r, p = "trailing" in s ? !!s.trailing : p);
  function u(_) {
    var y = l, P = n;
    return l = n = void 0, g = _, o = e.apply(P, y), o;
  }
  function x(_) {
    return g = _, i = setTimeout(m, t), b ? u(_) : o;
  }
  function C(_) {
    var y = _ - c, P = _ - g, D = t - y;
    return a ? je(D, r - P) : D;
  }
  function d(_) {
    var y = _ - c, P = _ - g;
    return c === void 0 || y >= t || y < 0 || a && P >= r;
  }
  function m() {
    var _ = B();
    if (d(_))
      return E(_);
    i = setTimeout(m, C(_));
  }
  function E(_) {
    return i = void 0, p && l ? u(_) : (l = n = void 0, o);
  }
  function T() {
    i !== void 0 && clearTimeout(i), g = 0, l = c = n = i = void 0;
  }
  function f() {
    return i === void 0 ? o : E(B());
  }
  function I() {
    var _ = B(), y = d(_);
    if (l = arguments, n = this, c = _, y) {
      if (i === void 0)
        return x(c);
      if (a)
        return clearTimeout(i), i = setTimeout(m, t), u(c);
    }
    return i === void 0 && (i = setTimeout(m, t)), o;
  }
  return I.cancel = T, I.flush = f, I;
}
var ee = {
  exports: {}
}, k = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Oe = w, ke = Symbol.for("react.element"), Be = Symbol.for("react.fragment"), Fe = Object.prototype.hasOwnProperty, Le = Oe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ne = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function te(e, t, s) {
  var l, n = {}, r = null, o = null;
  s !== void 0 && (r = "" + s), t.key !== void 0 && (r = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (l in t) Fe.call(t, l) && !Ne.hasOwnProperty(l) && (n[l] = t[l]);
  if (e && e.defaultProps) for (l in t = e.defaultProps, t) n[l] === void 0 && (n[l] = t[l]);
  return {
    $$typeof: ke,
    type: e,
    key: r,
    ref: o,
    props: n,
    _owner: Le.current
  };
}
k.Fragment = Be;
k.jsx = te;
k.jsxs = te;
ee.exports = k;
var h = ee.exports;
const {
  SvelteComponent: We,
  assign: G,
  binding_callbacks: q,
  check_outros: Ae,
  children: ne,
  claim_element: re,
  claim_space: Me,
  component_subscribe: V,
  compute_slots: ze,
  create_slot: De,
  detach: S,
  element: oe,
  empty: J,
  exclude_internal_props: X,
  get_all_dirty_from_scope: Ue,
  get_slot_changes: He,
  group_outros: Ge,
  init: qe,
  insert_hydration: R,
  safe_not_equal: Ve,
  set_custom_element_data: se,
  space: Je,
  transition_in: O,
  transition_out: M,
  update_slot_base: Xe
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ye,
  getContext: Ze,
  onDestroy: Ke,
  setContext: Qe
} = window.__gradio__svelte__internal;
function Y(e) {
  let t, s;
  const l = (
    /*#slots*/
    e[7].default
  ), n = De(
    l,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = oe("svelte-slot"), n && n.c(), this.h();
    },
    l(r) {
      t = re(r, "SVELTE-SLOT", {
        class: !0
      });
      var o = ne(t);
      n && n.l(o), o.forEach(S), this.h();
    },
    h() {
      se(t, "class", "svelte-1rt0kpf");
    },
    m(r, o) {
      R(r, t, o), n && n.m(t, null), e[9](t), s = !0;
    },
    p(r, o) {
      n && n.p && (!s || o & /*$$scope*/
      64) && Xe(
        n,
        l,
        r,
        /*$$scope*/
        r[6],
        s ? He(
          l,
          /*$$scope*/
          r[6],
          o,
          null
        ) : Ue(
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
      M(n, r), s = !1;
    },
    d(r) {
      r && S(t), n && n.d(r), e[9](null);
    }
  };
}
function $e(e) {
  let t, s, l, n, r = (
    /*$$slots*/
    e[4].default && Y(e)
  );
  return {
    c() {
      t = oe("react-portal-target"), s = Je(), r && r.c(), l = J(), this.h();
    },
    l(o) {
      t = re(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), ne(t).forEach(S), s = Me(o), r && r.l(o), l = J(), this.h();
    },
    h() {
      se(t, "class", "svelte-1rt0kpf");
    },
    m(o, i) {
      R(o, t, i), e[8](t), R(o, s, i), r && r.m(o, i), R(o, l, i), n = !0;
    },
    p(o, [i]) {
      /*$$slots*/
      o[4].default ? r ? (r.p(o, i), i & /*$$slots*/
      16 && O(r, 1)) : (r = Y(o), r.c(), O(r, 1), r.m(l.parentNode, l)) : r && (Ge(), M(r, 1, 1, () => {
        r = null;
      }), Ae());
    },
    i(o) {
      n || (O(r), n = !0);
    },
    o(o) {
      M(r), n = !1;
    },
    d(o) {
      o && (S(t), S(s), S(l)), e[8](null), r && r.d(o);
    }
  };
}
function Z(e) {
  const {
    svelteInit: t,
    ...s
  } = e;
  return s;
}
function et(e, t, s) {
  let l, n, {
    $$slots: r = {},
    $$scope: o
  } = t;
  const i = ze(r);
  let {
    svelteInit: c
  } = t;
  const g = j(Z(t)), b = j();
  V(e, b, (f) => s(0, l = f));
  const a = j();
  V(e, a, (f) => s(1, n = f));
  const p = [], u = Ze("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: C,
    subSlotIndex: d
  } = _e() || {}, m = c({
    parent: u,
    props: g,
    target: b,
    slot: a,
    slotKey: x,
    slotIndex: C,
    subSlotIndex: d,
    onDestroy(f) {
      p.push(f);
    }
  });
  Qe("$$ms-gr-react-wrapper", m), Ye(() => {
    g.set(Z(t));
  }), Ke(() => {
    p.forEach((f) => f());
  });
  function E(f) {
    q[f ? "unshift" : "push"](() => {
      l = f, b.set(l);
    });
  }
  function T(f) {
    q[f ? "unshift" : "push"](() => {
      n = f, a.set(n);
    });
  }
  return e.$$set = (f) => {
    s(17, t = G(G({}, t), X(f))), "svelteInit" in f && s(5, c = f.svelteInit), "$$scope" in f && s(6, o = f.$$scope);
  }, t = X(t), [l, n, b, a, i, c, o, r, E, T];
}
class tt extends We {
  constructor(t) {
    super(), qe(this, t, et, $e, Ve, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ht
} = window.__gradio__svelte__internal, K = window.ms_globals.rerender, F = window.ms_globals.tree;
function nt(e, t = {}) {
  function s(l) {
    const n = j(), r = new tt({
      ...l,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const i = {
            key: window.ms_globals.autokey,
            svelteInstance: n,
            reactComponent: e,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, c = o.parent ?? F;
          return c.nodes = [...c.nodes, i], K({
            createPortal: N,
            node: F
          }), o.onDestroy(() => {
            c.nodes = c.nodes.filter((g) => g.svelteInstance !== n), K({
              createPortal: N,
              node: F
            });
          }), i;
        },
        ...l.props
      }
    });
    return n.set(r), r;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise.then(() => {
      l(s);
    });
  });
}
const rt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function ot(e) {
  return e ? Object.keys(e).reduce((t, s) => {
    const l = e[s];
    return t[s] = st(s, l), t;
  }, {}) : {};
}
function st(e, t) {
  return typeof t == "number" && !rt.includes(e) ? t + "px" : t;
}
function z(e) {
  const t = [], s = e.cloneNode(!1);
  if (e._reactElement) {
    const n = w.Children.toArray(e._reactElement.props.children).map((r) => {
      if (w.isValidElement(r) && r.props.__slot__) {
        const {
          portals: o,
          clonedElement: i
        } = z(r.props.el);
        return w.cloneElement(r, {
          ...r.props,
          el: i,
          children: [...w.Children.toArray(r.props.children), ...o]
        });
      }
      return null;
    });
    return n.originalChildren = e._reactElement.props.children, t.push(N(w.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: n
    }), s)), {
      clonedElement: s,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((n) => {
    e.getEventListeners(n).forEach(({
      listener: o,
      type: i,
      useCapture: c
    }) => {
      s.addEventListener(i, o, c);
    });
  });
  const l = Array.from(e.childNodes);
  for (let n = 0; n < l.length; n++) {
    const r = l[n];
    if (r.nodeType === 1) {
      const {
        clonedElement: o,
        portals: i
      } = z(r);
      t.push(...i), s.appendChild(o);
    } else r.nodeType === 3 && s.appendChild(r.cloneNode());
  }
  return {
    clonedElement: s,
    portals: t
  };
}
function lt(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const v = ae(({
  slot: e,
  clone: t,
  className: s,
  style: l,
  observeAttributes: n
}, r) => {
  const o = ce(), [i, c] = ue([]), {
    forceClone: g
  } = pe(), b = g ? !0 : t;
  return de(() => {
    var C;
    if (!o.current || !e)
      return;
    let a = e;
    function p() {
      let d = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (d = a.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), lt(r, d), s && d.classList.add(...s.split(" ")), l) {
        const m = ot(l);
        Object.keys(m).forEach((E) => {
          d.style[E] = m[E];
        });
      }
    }
    let u = null, x = null;
    if (b && window.MutationObserver) {
      let d = function() {
        var f, I, _;
        (f = o.current) != null && f.contains(a) && ((I = o.current) == null || I.removeChild(a));
        const {
          portals: E,
          clonedElement: T
        } = z(e);
        a = T, c(E), a.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          p();
        }, 50), (_ = o.current) == null || _.appendChild(a);
      };
      d();
      const m = Re(() => {
        d(), u == null || u.disconnect(), u == null || u.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: n
        });
      }, 50);
      u = new window.MutationObserver(m), u.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", p(), (C = o.current) == null || C.appendChild(a);
    return () => {
      var d, m;
      a.style.display = "", (d = o.current) != null && d.contains(a) && ((m = o.current) == null || m.removeChild(a)), u == null || u.disconnect();
    };
  }, [e, b, s, l, r, n, g]), w.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...i);
});
function it(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function at(e, t = !1) {
  try {
    if (he(e))
      return e;
    if (t && !it(e))
      return;
    if (typeof e == "string") {
      let s = e.trim();
      return s.startsWith(";") && (s = s.slice(1)), s.endsWith(";") && (s = s.slice(0, -1)), new Function(`return (...args) => (${s})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function L(e, t) {
  return $(() => at(e, t), [e, t]);
}
function ct(e, t) {
  return Object.keys(e).reduce((s, l) => (e[l] !== void 0 && (s[l] = e[l]), s), {});
}
const ut = ({
  children: e,
  ...t
}) => /* @__PURE__ */ h.jsx(h.Fragment, {
  children: e(t)
});
function le(e) {
  return w.createElement(ut, {
    children: e
  });
}
function ie(e, t, s) {
  const l = e.filter(Boolean);
  if (l.length !== 0)
    return l.map((n, r) => {
      var g;
      if (typeof n != "object")
        return n;
      const o = {
        ...n.props,
        key: ((g = n.props) == null ? void 0 : g.key) ?? (s ? `${s}-${r}` : `${r}`)
      };
      let i = o;
      Object.keys(n.slots).forEach((b) => {
        if (!n.slots[b] || !(n.slots[b] instanceof Element) && !n.slots[b].el)
          return;
        const a = b.split(".");
        a.forEach((m, E) => {
          i[m] || (i[m] = {}), E !== a.length - 1 && (i = o[m]);
        });
        const p = n.slots[b];
        let u, x, C = !1, d = t == null ? void 0 : t.forceClone;
        p instanceof Element ? u = p : (u = p.el, x = p.callback, C = p.clone ?? C, d = p.forceClone ?? d), d = d ?? !!x, i[a[a.length - 1]] = u ? x ? (...m) => (x(a[a.length - 1], m), /* @__PURE__ */ h.jsx(A, {
          ...n.ctx,
          params: m,
          forceClone: d,
          children: /* @__PURE__ */ h.jsx(v, {
            slot: u,
            clone: C
          })
        })) : le((m) => /* @__PURE__ */ h.jsx(A, {
          ...n.ctx,
          forceClone: d,
          children: /* @__PURE__ */ h.jsx(v, {
            ...m,
            slot: u,
            clone: C
          })
        })) : i[a[a.length - 1]], i = o;
      });
      const c = "children";
      return n[c] && (o[c] = ie(n[c], t, `${r}`)), o;
    });
}
function Q(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? le((s) => /* @__PURE__ */ h.jsx(A, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ h.jsx(v, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...s
    })
  })) : /* @__PURE__ */ h.jsx(v, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function dt({
  key: e,
  slots: t,
  targets: s
}, l) {
  return t[e] ? (...n) => s ? s.map((r, o) => /* @__PURE__ */ h.jsx(w.Fragment, {
    children: Q(r, {
      clone: !0,
      params: n,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ h.jsx(h.Fragment, {
    children: Q(t[e], {
      clone: !0,
      params: n,
      forceClone: !0
    })
  }) : void 0;
}
const {
  withItemsContextProvider: ft,
  useItems: mt,
  ItemHandler: pt
} = be("antd-tabs-items"), gt = nt(ft(["items", "default"], ({
  slots: e,
  indicator: t,
  items: s,
  onChange: l,
  more: n,
  children: r,
  renderTabBar: o,
  setSlotParams: i,
  ...c
}) => {
  const g = L(t == null ? void 0 : t.size), b = L(n == null ? void 0 : n.getPopupContainer), a = L(o), {
    items: p
  } = mt(), u = p.items.length > 0 ? p.items : p.default;
  return /* @__PURE__ */ h.jsxs(h.Fragment, {
    children: [/* @__PURE__ */ h.jsx("div", {
      style: {
        display: "none"
      },
      children: r
    }), /* @__PURE__ */ h.jsx(ge, {
      ...c,
      indicator: g ? {
        ...t,
        size: g
      } : t,
      renderTabBar: e.renderTabBar ? dt({
        slots: e,
        key: "renderTabBar"
      }) : a,
      items: $(() => s || ie(u), [s, u]),
      more: ct({
        ...n || {},
        getPopupContainer: b || (n == null ? void 0 : n.getPopupContainer),
        icon: e["more.icon"] ? /* @__PURE__ */ h.jsx(v, {
          slot: e["more.icon"]
        }) : n == null ? void 0 : n.icon
      }),
      tabBarExtraContent: e.tabBarExtraContent ? /* @__PURE__ */ h.jsx(v, {
        slot: e.tabBarExtraContent
      }) : e["tabBarExtraContent.left"] || e["tabBarExtraContent.right"] ? {
        left: e["tabBarExtraContent.left"] ? /* @__PURE__ */ h.jsx(v, {
          slot: e["tabBarExtraContent.left"]
        }) : void 0,
        right: e["tabBarExtraContent.right"] ? /* @__PURE__ */ h.jsx(v, {
          slot: e["tabBarExtraContent.right"]
        }) : void 0
      } : c.tabBarExtraContent,
      addIcon: e.addIcon ? /* @__PURE__ */ h.jsx(v, {
        slot: e.addIcon
      }) : c.addIcon,
      removeIcon: e.removeIcon ? /* @__PURE__ */ h.jsx(v, {
        slot: e.removeIcon
      }) : c.removeIcon,
      onChange: (x) => {
        l == null || l(x);
      }
    })]
  });
}));
export {
  gt as Tabs,
  gt as default
};
