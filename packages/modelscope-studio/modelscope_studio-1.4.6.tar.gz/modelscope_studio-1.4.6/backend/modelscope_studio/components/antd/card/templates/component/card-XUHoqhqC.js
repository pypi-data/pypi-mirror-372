import { i as pe, a as M, r as he, Z as B, g as xe, t as _e, s as T, b as ge } from "./Index-BznjFuSX.js";
const I = window.ms_globals.React, k = window.ms_globals.React.useMemo, ne = window.ms_globals.React.useState, re = window.ms_globals.React.useEffect, fe = window.ms_globals.React.forwardRef, me = window.ms_globals.React.useRef, W = window.ms_globals.ReactDOM.createPortal, be = window.ms_globals.internalContext.useContextPropsContext, z = window.ms_globals.internalContext.ContextPropsProvider, H = window.ms_globals.antd.Card, Ce = window.ms_globals.createItemsContext.createItemsContext;
var Ee = /\s/;
function ve(e) {
  for (var t = e.length; t-- && Ee.test(e.charAt(t)); )
    ;
  return t;
}
var Ie = /^\s+/;
function we(e) {
  return e && e.slice(0, ve(e) + 1).replace(Ie, "");
}
var V = NaN, ye = /^[-+]0x[0-9a-f]+$/i, Se = /^0b[01]+$/i, je = /^0o[0-7]+$/i, Pe = parseInt;
function q(e) {
  if (typeof e == "number")
    return e;
  if (pe(e))
    return V;
  if (M(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = M(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = we(e);
  var n = Se.test(e);
  return n || je.test(e) ? Pe(e.slice(2), n ? 2 : 8) : ye.test(e) ? V : +e;
}
var F = function() {
  return he.Date.now();
}, Te = "Expected a function", Be = Math.max, Re = Math.min;
function Oe(e, t, n) {
  var a, s, r, o, l, c, x = 0, d = !1, i = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(Te);
  t = q(t) || 0, M(n) && (d = !!n.leading, i = "maxWait" in n, r = i ? Be(q(n.maxWait) || 0, t) : r, g = "trailing" in n ? !!n.trailing : g);
  function m(_) {
    var w = a, P = s;
    return a = s = void 0, x = _, o = e.apply(P, w), o;
  }
  function C(_) {
    return x = _, l = setTimeout(h, t), d ? m(_) : o;
  }
  function E(_) {
    var w = _ - c, P = _ - x, G = t - w;
    return i ? Re(G, r - P) : G;
  }
  function u(_) {
    var w = _ - c, P = _ - x;
    return c === void 0 || w >= t || w < 0 || i && P >= r;
  }
  function h() {
    var _ = F();
    if (u(_))
      return v(_);
    l = setTimeout(h, E(_));
  }
  function v(_) {
    return l = void 0, g && a ? m(_) : (a = s = void 0, o);
  }
  function j() {
    l !== void 0 && clearTimeout(l), x = 0, a = c = s = l = void 0;
  }
  function p() {
    return l === void 0 ? o : v(F());
  }
  function y() {
    var _ = F(), w = u(_);
    if (a = arguments, s = this, c = _, w) {
      if (l === void 0)
        return C(c);
      if (i)
        return clearTimeout(l), l = setTimeout(h, t), m(c);
    }
    return l === void 0 && (l = setTimeout(h, t)), o;
  }
  return y.cancel = j, y.flush = p, y;
}
var oe = {
  exports: {}
}, L = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var ke = I, Le = Symbol.for("react.element"), Fe = Symbol.for("react.fragment"), Ae = Object.prototype.hasOwnProperty, Ne = ke.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, We = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function se(e, t, n) {
  var a, s = {}, r = null, o = null;
  n !== void 0 && (r = "" + n), t.key !== void 0 && (r = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (a in t) Ae.call(t, a) && !We.hasOwnProperty(a) && (s[a] = t[a]);
  if (e && e.defaultProps) for (a in t = e.defaultProps, t) s[a] === void 0 && (s[a] = t[a]);
  return {
    $$typeof: Le,
    type: e,
    key: r,
    ref: o,
    props: s,
    _owner: Ne.current
  };
}
L.Fragment = Fe;
L.jsx = se;
L.jsxs = se;
oe.exports = L;
var f = oe.exports;
const {
  SvelteComponent: Me,
  assign: J,
  binding_callbacks: X,
  check_outros: ze,
  children: ae,
  claim_element: le,
  claim_space: De,
  component_subscribe: Y,
  compute_slots: Ue,
  create_slot: Ge,
  detach: S,
  element: ie,
  empty: Z,
  exclude_internal_props: K,
  get_all_dirty_from_scope: He,
  get_slot_changes: Ve,
  group_outros: qe,
  init: Je,
  insert_hydration: R,
  safe_not_equal: Xe,
  set_custom_element_data: ce,
  space: Ye,
  transition_in: O,
  transition_out: D,
  update_slot_base: Ze
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ke,
  getContext: Qe,
  onDestroy: $e,
  setContext: et
} = window.__gradio__svelte__internal;
function Q(e) {
  let t, n;
  const a = (
    /*#slots*/
    e[7].default
  ), s = Ge(
    a,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ie("svelte-slot"), s && s.c(), this.h();
    },
    l(r) {
      t = le(r, "SVELTE-SLOT", {
        class: !0
      });
      var o = ae(t);
      s && s.l(o), o.forEach(S), this.h();
    },
    h() {
      ce(t, "class", "svelte-1rt0kpf");
    },
    m(r, o) {
      R(r, t, o), s && s.m(t, null), e[9](t), n = !0;
    },
    p(r, o) {
      s && s.p && (!n || o & /*$$scope*/
      64) && Ze(
        s,
        a,
        r,
        /*$$scope*/
        r[6],
        n ? Ve(
          a,
          /*$$scope*/
          r[6],
          o,
          null
        ) : He(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      n || (O(s, r), n = !0);
    },
    o(r) {
      D(s, r), n = !1;
    },
    d(r) {
      r && S(t), s && s.d(r), e[9](null);
    }
  };
}
function tt(e) {
  let t, n, a, s, r = (
    /*$$slots*/
    e[4].default && Q(e)
  );
  return {
    c() {
      t = ie("react-portal-target"), n = Ye(), r && r.c(), a = Z(), this.h();
    },
    l(o) {
      t = le(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), ae(t).forEach(S), n = De(o), r && r.l(o), a = Z(), this.h();
    },
    h() {
      ce(t, "class", "svelte-1rt0kpf");
    },
    m(o, l) {
      R(o, t, l), e[8](t), R(o, n, l), r && r.m(o, l), R(o, a, l), s = !0;
    },
    p(o, [l]) {
      /*$$slots*/
      o[4].default ? r ? (r.p(o, l), l & /*$$slots*/
      16 && O(r, 1)) : (r = Q(o), r.c(), O(r, 1), r.m(a.parentNode, a)) : r && (qe(), D(r, 1, 1, () => {
        r = null;
      }), ze());
    },
    i(o) {
      s || (O(r), s = !0);
    },
    o(o) {
      D(r), s = !1;
    },
    d(o) {
      o && (S(t), S(n), S(a)), e[8](null), r && r.d(o);
    }
  };
}
function $(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function nt(e, t, n) {
  let a, s, {
    $$slots: r = {},
    $$scope: o
  } = t;
  const l = Ue(r);
  let {
    svelteInit: c
  } = t;
  const x = B($(t)), d = B();
  Y(e, d, (p) => n(0, a = p));
  const i = B();
  Y(e, i, (p) => n(1, s = p));
  const g = [], m = Qe("$$ms-gr-react-wrapper"), {
    slotKey: C,
    slotIndex: E,
    subSlotIndex: u
  } = xe() || {}, h = c({
    parent: m,
    props: x,
    target: d,
    slot: i,
    slotKey: C,
    slotIndex: E,
    subSlotIndex: u,
    onDestroy(p) {
      g.push(p);
    }
  });
  et("$$ms-gr-react-wrapper", h), Ke(() => {
    x.set($(t));
  }), $e(() => {
    g.forEach((p) => p());
  });
  function v(p) {
    X[p ? "unshift" : "push"](() => {
      a = p, d.set(a);
    });
  }
  function j(p) {
    X[p ? "unshift" : "push"](() => {
      s = p, i.set(s);
    });
  }
  return e.$$set = (p) => {
    n(17, t = J(J({}, t), K(p))), "svelteInit" in p && n(5, c = p.svelteInit), "$$scope" in p && n(6, o = p.$$scope);
  }, t = K(t), [a, s, d, i, l, c, o, r, v, j];
}
class rt extends Me {
  constructor(t) {
    super(), Je(this, t, nt, tt, Xe, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Ct
} = window.__gradio__svelte__internal, ee = window.ms_globals.rerender, A = window.ms_globals.tree;
function ot(e, t = {}) {
  function n(a) {
    const s = B(), r = new rt({
      ...a,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: e,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, c = o.parent ?? A;
          return c.nodes = [...c.nodes, l], ee({
            createPortal: W,
            node: A
          }), o.onDestroy(() => {
            c.nodes = c.nodes.filter((x) => x.svelteInstance !== s), ee({
              createPortal: W,
              node: A
            });
          }), l;
        },
        ...a.props
      }
    });
    return s.set(r), r;
  }
  return new Promise((a) => {
    window.ms_globals.initializePromise.then(() => {
      a(n);
    });
  });
}
function st(e) {
  const [t, n] = ne(() => T(e));
  return re(() => {
    let a = !0;
    return e.subscribe((r) => {
      a && (a = !1, r === t) || n(r);
    });
  }, [e]), t;
}
function at(e) {
  const t = k(() => _e(e, (n) => n), [e]);
  return st(t);
}
const lt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function it(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const a = e[n];
    return t[n] = ct(n, a), t;
  }, {}) : {};
}
function ct(e, t) {
  return typeof t == "number" && !lt.includes(e) ? t + "px" : t;
}
function U(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const s = I.Children.toArray(e._reactElement.props.children).map((r) => {
      if (I.isValidElement(r) && r.props.__slot__) {
        const {
          portals: o,
          clonedElement: l
        } = U(r.props.el);
        return I.cloneElement(r, {
          ...r.props,
          el: l,
          children: [...I.Children.toArray(r.props.children), ...o]
        });
      }
      return null;
    });
    return s.originalChildren = e._reactElement.props.children, t.push(W(I.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: s
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((s) => {
    e.getEventListeners(s).forEach(({
      listener: o,
      type: l,
      useCapture: c
    }) => {
      n.addEventListener(l, o, c);
    });
  });
  const a = Array.from(e.childNodes);
  for (let s = 0; s < a.length; s++) {
    const r = a[s];
    if (r.nodeType === 1) {
      const {
        clonedElement: o,
        portals: l
      } = U(r);
      t.push(...l), n.appendChild(o);
    } else r.nodeType === 3 && n.appendChild(r.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function ut(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const b = fe(({
  slot: e,
  clone: t,
  className: n,
  style: a,
  observeAttributes: s
}, r) => {
  const o = me(), [l, c] = ne([]), {
    forceClone: x
  } = be(), d = x ? !0 : t;
  return re(() => {
    var E;
    if (!o.current || !e)
      return;
    let i = e;
    function g() {
      let u = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (u = i.children[0], u.tagName.toLowerCase() === "react-portal-target" && u.children[0] && (u = u.children[0])), ut(r, u), n && u.classList.add(...n.split(" ")), a) {
        const h = it(a);
        Object.keys(h).forEach((v) => {
          u.style[v] = h[v];
        });
      }
    }
    let m = null, C = null;
    if (d && window.MutationObserver) {
      let u = function() {
        var p, y, _;
        (p = o.current) != null && p.contains(i) && ((y = o.current) == null || y.removeChild(i));
        const {
          portals: v,
          clonedElement: j
        } = U(e);
        i = j, c(v), i.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          g();
        }, 50), (_ = o.current) == null || _.appendChild(i);
      };
      u();
      const h = Oe(() => {
        u(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: s
        });
      }, 50);
      m = new window.MutationObserver(h), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", g(), (E = o.current) == null || E.appendChild(i);
    return () => {
      var u, h;
      i.style.display = "", (u = o.current) != null && u.contains(i) && ((h = o.current) == null || h.removeChild(i)), m == null || m.disconnect();
    };
  }, [e, d, n, a, r, s, x]), I.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...l);
});
function dt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function ft(e, t = !1) {
  try {
    if (ge(e))
      return e;
    if (t && !dt(e))
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
function N(e, t) {
  return k(() => ft(e, t), [e, t]);
}
function mt(e, t) {
  const n = k(() => I.Children.toArray(e.originalChildren || e).filter((r) => r.props.node && !r.props.node.ignore && t === r.props.nodeSlotKey).sort((r, o) => {
    if (r.props.node.slotIndex && o.props.node.slotIndex) {
      const l = T(r.props.node.slotIndex) || 0, c = T(o.props.node.slotIndex) || 0;
      return l - c === 0 && r.props.node.subSlotIndex && o.props.node.subSlotIndex ? (T(r.props.node.subSlotIndex) || 0) - (T(o.props.node.subSlotIndex) || 0) : l - c;
    }
    return 0;
  }).map((r) => r.props.node.target), [e, t]);
  return at(n);
}
function pt(e, t) {
  return Object.keys(e).reduce((n, a) => (e[a] !== void 0 && (n[a] = e[a]), n), {});
}
const ht = ({
  children: e,
  ...t
}) => /* @__PURE__ */ f.jsx(f.Fragment, {
  children: e(t)
});
function ue(e) {
  return I.createElement(ht, {
    children: e
  });
}
function de(e, t, n) {
  const a = e.filter(Boolean);
  if (a.length !== 0)
    return a.map((s, r) => {
      var x;
      if (typeof s != "object")
        return s;
      const o = {
        ...s.props,
        key: ((x = s.props) == null ? void 0 : x.key) ?? (n ? `${n}-${r}` : `${r}`)
      };
      let l = o;
      Object.keys(s.slots).forEach((d) => {
        if (!s.slots[d] || !(s.slots[d] instanceof Element) && !s.slots[d].el)
          return;
        const i = d.split(".");
        i.forEach((h, v) => {
          l[h] || (l[h] = {}), v !== i.length - 1 && (l = o[h]);
        });
        const g = s.slots[d];
        let m, C, E = !1, u = t == null ? void 0 : t.forceClone;
        g instanceof Element ? m = g : (m = g.el, C = g.callback, E = g.clone ?? E, u = g.forceClone ?? u), u = u ?? !!C, l[i[i.length - 1]] = m ? C ? (...h) => (C(i[i.length - 1], h), /* @__PURE__ */ f.jsx(z, {
          ...s.ctx,
          params: h,
          forceClone: u,
          children: /* @__PURE__ */ f.jsx(b, {
            slot: m,
            clone: E
          })
        })) : ue((h) => /* @__PURE__ */ f.jsx(z, {
          ...s.ctx,
          forceClone: u,
          children: /* @__PURE__ */ f.jsx(b, {
            ...h,
            slot: m,
            clone: E
          })
        })) : l[i[i.length - 1]], l = o;
      });
      const c = "children";
      return s[c] && (o[c] = de(s[c], t, `${r}`)), o;
    });
}
function te(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ue((n) => /* @__PURE__ */ f.jsx(z, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ f.jsx(b, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...n
    })
  })) : /* @__PURE__ */ f.jsx(b, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function xt({
  key: e,
  slots: t,
  targets: n
}, a) {
  return t[e] ? (...s) => n ? n.map((r, o) => /* @__PURE__ */ f.jsx(I.Fragment, {
    children: te(r, {
      clone: !0,
      params: s,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ f.jsx(f.Fragment, {
    children: te(t[e], {
      clone: !0,
      params: s,
      forceClone: !0
    })
  }) : void 0;
}
const {
  withItemsContextProvider: _t,
  useItems: gt,
  ItemHandler: Et
} = Ce("antd-tabs-items"), vt = ot(_t(["tabList"], ({
  children: e,
  containsGrid: t,
  slots: n,
  tabList: a,
  tabProps: s,
  setSlotParams: r,
  ...o
}) => {
  const l = mt(e, "actions"), {
    items: {
      tabList: c
    }
  } = gt(), {
    indicator: x,
    more: d,
    renderTabBar: i
  } = s || {}, g = N(x == null ? void 0 : x.size), m = N(d == null ? void 0 : d.getPopupContainer), C = N(i);
  return /* @__PURE__ */ f.jsxs(H, {
    ...o,
    tabProps: {
      ...s || {},
      indicator: g ? {
        ...x,
        size: g
      } : x,
      renderTabBar: n["tabProps.renderTabBar"] ? xt({
        slots: n,
        key: "tabProps.renderTabBar"
      }) : C,
      more: pt({
        ...d || {},
        getPopupContainer: m || (d == null ? void 0 : d.getPopupContainer),
        icon: n["tabProps.more.icon"] ? /* @__PURE__ */ f.jsx(b, {
          slot: n["tabProps.more.icon"]
        }) : d == null ? void 0 : d.icon
      }),
      tabBarExtraContent: n["tabProps.tabBarExtraContent"] ? /* @__PURE__ */ f.jsx(b, {
        slot: n["tabProps.tabBarExtraContent"]
      }) : n["tabProps.tabBarExtraContent.left"] || n["tabProps.tabBarExtraContent.right"] ? {
        left: n["tabProps.tabBarExtraContent.left"] ? /* @__PURE__ */ f.jsx(b, {
          slot: n["tabProps.tabBarExtraContent.left"]
        }) : void 0,
        right: n["tabProps.tabBarExtraContent.right"] ? /* @__PURE__ */ f.jsx(b, {
          slot: n["tabProps.tabBarExtraContent.right"]
        }) : void 0
      } : s == null ? void 0 : s.tabBarExtraContent,
      addIcon: n["tabProps.addIcon"] ? /* @__PURE__ */ f.jsx(b, {
        slot: n["tabProps.addIcon"]
      }) : s == null ? void 0 : s.addIcon,
      removeIcon: n["tabProps.removeIcon"] ? /* @__PURE__ */ f.jsx(b, {
        slot: n["tabProps.removeIcon"]
      }) : s == null ? void 0 : s.removeIcon
    },
    tabList: k(() => a || de(c), [a, c]),
    title: n.title ? /* @__PURE__ */ f.jsx(b, {
      slot: n.title
    }) : o.title,
    extra: n.extra ? /* @__PURE__ */ f.jsx(b, {
      slot: n.extra
    }) : o.extra,
    cover: n.cover ? /* @__PURE__ */ f.jsx(b, {
      slot: n.cover
    }) : o.cover,
    tabBarExtraContent: n.tabBarExtraContent ? /* @__PURE__ */ f.jsx(b, {
      slot: n.tabBarExtraContent
    }) : n["tabBarExtraContent.left"] || n["tabBarExtraContent.right"] ? {
      left: n["tabBarExtraContent.left"] ? /* @__PURE__ */ f.jsx(b, {
        slot: n["tabBarExtraContent.left"]
      }) : void 0,
      right: n["tabBarExtraContent.right"] ? /* @__PURE__ */ f.jsx(b, {
        slot: n["tabBarExtraContent.right"]
      }) : void 0
    } : o.tabBarExtraContent,
    actions: l.length > 0 ? l.map((E, u) => /* @__PURE__ */ f.jsx(b, {
      slot: E
    }, u)) : o.actions,
    children: [t ? /* @__PURE__ */ f.jsx(H.Grid, {
      style: {
        display: "none"
      }
    }) : null, e]
  });
}));
export {
  vt as Card,
  vt as default
};
