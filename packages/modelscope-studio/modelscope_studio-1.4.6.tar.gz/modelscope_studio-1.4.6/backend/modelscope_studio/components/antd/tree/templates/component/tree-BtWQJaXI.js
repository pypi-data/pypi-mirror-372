import { i as he, a as D, r as _e, Z as j, g as ge, b as we } from "./Index-DqhAgZM7.js";
const T = window.ms_globals.React, ue = window.ms_globals.React.forwardRef, fe = window.ms_globals.React.useRef, de = window.ms_globals.React.useState, me = window.ms_globals.React.useEffect, te = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, be = window.ms_globals.internalContext.useContextPropsContext, M = window.ms_globals.internalContext.ContextPropsProvider, z = window.ms_globals.antd.Tree, ye = window.ms_globals.createItemsContext.createItemsContext;
var ve = /\s/;
function xe(t) {
  for (var e = t.length; e-- && ve.test(t.charAt(e)); )
    ;
  return e;
}
var pe = /^\s+/;
function Ce(t) {
  return t && t.slice(0, xe(t) + 1).replace(pe, "");
}
var G = NaN, Ie = /^[-+]0x[0-9a-f]+$/i, Ee = /^0b[01]+$/i, Te = /^0o[0-7]+$/i, Re = parseInt;
function q(t) {
  if (typeof t == "number")
    return t;
  if (he(t))
    return G;
  if (D(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = D(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Ce(t);
  var l = Ee.test(t);
  return l || Te.test(t) ? Re(t.slice(2), l ? 2 : 8) : Ie.test(t) ? G : +t;
}
var N = function() {
  return _e.Date.now();
}, Se = "Expected a function", ke = Math.max, Oe = Math.min;
function je(t, e, l) {
  var s, o, n, r, c, u, b = 0, v = !1, i = !1, g = !0;
  if (typeof t != "function")
    throw new TypeError(Se);
  e = q(e) || 0, D(l) && (v = !!l.leading, i = "maxWait" in l, n = i ? ke(q(l.maxWait) || 0, e) : n, g = "trailing" in l ? !!l.trailing : g);
  function a(h) {
    var _ = s, C = o;
    return s = o = void 0, b = h, r = t.apply(C, _), r;
  }
  function x(h) {
    return b = h, c = setTimeout(m, e), v ? a(h) : r;
  }
  function p(h) {
    var _ = h - u, C = h - b, H = e - _;
    return i ? Oe(H, n - C) : H;
  }
  function d(h) {
    var _ = h - u, C = h - b;
    return u === void 0 || _ >= e || _ < 0 || i && C >= n;
  }
  function m() {
    var h = N();
    if (d(h))
      return w(h);
    c = setTimeout(m, p(h));
  }
  function w(h) {
    return c = void 0, g && s ? a(h) : (s = o = void 0, r);
  }
  function I() {
    c !== void 0 && clearTimeout(c), b = 0, s = u = o = c = void 0;
  }
  function f() {
    return c === void 0 ? r : w(N());
  }
  function E() {
    var h = N(), _ = d(h);
    if (s = arguments, o = this, u = h, _) {
      if (c === void 0)
        return x(u);
      if (i)
        return clearTimeout(c), c = setTimeout(m, e), a(u);
    }
    return c === void 0 && (c = setTimeout(m, e)), r;
  }
  return E.cancel = I, E.flush = f, E;
}
var ne = {
  exports: {}
}, F = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Pe = T, Le = Symbol.for("react.element"), Fe = Symbol.for("react.fragment"), Ne = Object.prototype.hasOwnProperty, We = Pe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ae = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function re(t, e, l) {
  var s, o = {}, n = null, r = null;
  l !== void 0 && (n = "" + l), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (r = e.ref);
  for (s in e) Ne.call(e, s) && !Ae.hasOwnProperty(s) && (o[s] = e[s]);
  if (t && t.defaultProps) for (s in e = t.defaultProps, e) o[s] === void 0 && (o[s] = e[s]);
  return {
    $$typeof: Le,
    type: t,
    key: n,
    ref: r,
    props: o,
    _owner: We.current
  };
}
F.Fragment = Fe;
F.jsx = re;
F.jsxs = re;
ne.exports = F;
var y = ne.exports;
const {
  SvelteComponent: De,
  assign: V,
  binding_callbacks: J,
  check_outros: Me,
  children: le,
  claim_element: oe,
  claim_space: Ue,
  component_subscribe: X,
  compute_slots: Be,
  create_slot: He,
  detach: R,
  element: se,
  empty: Y,
  exclude_internal_props: Z,
  get_all_dirty_from_scope: ze,
  get_slot_changes: Ge,
  group_outros: qe,
  init: Ve,
  insert_hydration: P,
  safe_not_equal: Je,
  set_custom_element_data: ce,
  space: Xe,
  transition_in: L,
  transition_out: U,
  update_slot_base: Ye
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ze,
  getContext: Ke,
  onDestroy: Qe,
  setContext: $e
} = window.__gradio__svelte__internal;
function K(t) {
  let e, l;
  const s = (
    /*#slots*/
    t[7].default
  ), o = He(
    s,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = se("svelte-slot"), o && o.c(), this.h();
    },
    l(n) {
      e = oe(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = le(e);
      o && o.l(r), r.forEach(R), this.h();
    },
    h() {
      ce(e, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      P(n, e, r), o && o.m(e, null), t[9](e), l = !0;
    },
    p(n, r) {
      o && o.p && (!l || r & /*$$scope*/
      64) && Ye(
        o,
        s,
        n,
        /*$$scope*/
        n[6],
        l ? Ge(
          s,
          /*$$scope*/
          n[6],
          r,
          null
        ) : ze(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      l || (L(o, n), l = !0);
    },
    o(n) {
      U(o, n), l = !1;
    },
    d(n) {
      n && R(e), o && o.d(n), t[9](null);
    }
  };
}
function et(t) {
  let e, l, s, o, n = (
    /*$$slots*/
    t[4].default && K(t)
  );
  return {
    c() {
      e = se("react-portal-target"), l = Xe(), n && n.c(), s = Y(), this.h();
    },
    l(r) {
      e = oe(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), le(e).forEach(R), l = Ue(r), n && n.l(r), s = Y(), this.h();
    },
    h() {
      ce(e, "class", "svelte-1rt0kpf");
    },
    m(r, c) {
      P(r, e, c), t[8](e), P(r, l, c), n && n.m(r, c), P(r, s, c), o = !0;
    },
    p(r, [c]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, c), c & /*$$slots*/
      16 && L(n, 1)) : (n = K(r), n.c(), L(n, 1), n.m(s.parentNode, s)) : n && (qe(), U(n, 1, 1, () => {
        n = null;
      }), Me());
    },
    i(r) {
      o || (L(n), o = !0);
    },
    o(r) {
      U(n), o = !1;
    },
    d(r) {
      r && (R(e), R(l), R(s)), t[8](null), n && n.d(r);
    }
  };
}
function Q(t) {
  const {
    svelteInit: e,
    ...l
  } = t;
  return l;
}
function tt(t, e, l) {
  let s, o, {
    $$slots: n = {},
    $$scope: r
  } = e;
  const c = Be(n);
  let {
    svelteInit: u
  } = e;
  const b = j(Q(e)), v = j();
  X(t, v, (f) => l(0, s = f));
  const i = j();
  X(t, i, (f) => l(1, o = f));
  const g = [], a = Ke("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: p,
    subSlotIndex: d
  } = ge() || {}, m = u({
    parent: a,
    props: b,
    target: v,
    slot: i,
    slotKey: x,
    slotIndex: p,
    subSlotIndex: d,
    onDestroy(f) {
      g.push(f);
    }
  });
  $e("$$ms-gr-react-wrapper", m), Ze(() => {
    b.set(Q(e));
  }), Qe(() => {
    g.forEach((f) => f());
  });
  function w(f) {
    J[f ? "unshift" : "push"](() => {
      s = f, v.set(s);
    });
  }
  function I(f) {
    J[f ? "unshift" : "push"](() => {
      o = f, i.set(o);
    });
  }
  return t.$$set = (f) => {
    l(17, e = V(V({}, e), Z(f))), "svelteInit" in f && l(5, u = f.svelteInit), "$$scope" in f && l(6, r = f.$$scope);
  }, e = Z(e), [s, o, v, i, c, u, r, n, w, I];
}
class nt extends De {
  constructor(e) {
    super(), Ve(this, e, tt, et, Je, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: _t
} = window.__gradio__svelte__internal, $ = window.ms_globals.rerender, W = window.ms_globals.tree;
function rt(t, e = {}) {
  function l(s) {
    const o = j(), n = new nt({
      ...s,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: t,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: e.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, u = r.parent ?? W;
          return u.nodes = [...u.nodes, c], $({
            createPortal: A,
            node: W
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((b) => b.svelteInstance !== o), $({
              createPortal: A,
              node: W
            });
          }), c;
        },
        ...s.props
      }
    });
    return o.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise.then(() => {
      s(l);
    });
  });
}
const lt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function ot(t) {
  return t ? Object.keys(t).reduce((e, l) => {
    const s = t[l];
    return e[l] = st(l, s), e;
  }, {}) : {};
}
function st(t, e) {
  return typeof e == "number" && !lt.includes(t) ? e + "px" : e;
}
function B(t) {
  const e = [], l = t.cloneNode(!1);
  if (t._reactElement) {
    const o = T.Children.toArray(t._reactElement.props.children).map((n) => {
      if (T.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: c
        } = B(n.props.el);
        return T.cloneElement(n, {
          ...n.props,
          el: c,
          children: [...T.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return o.originalChildren = t._reactElement.props.children, e.push(A(T.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: o
    }), l)), {
      clonedElement: l,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((o) => {
    t.getEventListeners(o).forEach(({
      listener: r,
      type: c,
      useCapture: u
    }) => {
      l.addEventListener(c, r, u);
    });
  });
  const s = Array.from(t.childNodes);
  for (let o = 0; o < s.length; o++) {
    const n = s[o];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: c
      } = B(n);
      e.push(...c), l.appendChild(r);
    } else n.nodeType === 3 && l.appendChild(n.cloneNode());
  }
  return {
    clonedElement: l,
    portals: e
  };
}
function ct(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const S = ue(({
  slot: t,
  clone: e,
  className: l,
  style: s,
  observeAttributes: o
}, n) => {
  const r = fe(), [c, u] = de([]), {
    forceClone: b
  } = be(), v = b ? !0 : e;
  return me(() => {
    var p;
    if (!r.current || !t)
      return;
    let i = t;
    function g() {
      let d = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (d = i.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), ct(n, d), l && d.classList.add(...l.split(" ")), s) {
        const m = ot(s);
        Object.keys(m).forEach((w) => {
          d.style[w] = m[w];
        });
      }
    }
    let a = null, x = null;
    if (v && window.MutationObserver) {
      let d = function() {
        var f, E, h;
        (f = r.current) != null && f.contains(i) && ((E = r.current) == null || E.removeChild(i));
        const {
          portals: w,
          clonedElement: I
        } = B(t);
        i = I, u(w), i.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          g();
        }, 50), (h = r.current) == null || h.appendChild(i);
      };
      d();
      const m = je(() => {
        d(), a == null || a.disconnect(), a == null || a.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      a = new window.MutationObserver(m), a.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", g(), (p = r.current) == null || p.appendChild(i);
    return () => {
      var d, m;
      i.style.display = "", (d = r.current) != null && d.contains(i) && ((m = r.current) == null || m.removeChild(i)), a == null || a.disconnect();
    };
  }, [t, v, l, s, n, o, b]), T.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...c);
});
function it(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function at(t, e = !1) {
  try {
    if (we(t))
      return t;
    if (e && !it(t))
      return;
    if (typeof t == "string") {
      let l = t.trim();
      return l.startsWith(";") && (l = l.slice(1)), l.endsWith(";") && (l = l.slice(0, -1)), new Function(`return (...args) => (${l})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function k(t, e) {
  return te(() => at(t, e), [t, e]);
}
function ut(t, e) {
  return Object.keys(t).reduce((l, s) => (t[s] !== void 0 && (l[s] = t[s]), l), {});
}
const ft = ({
  children: t,
  ...e
}) => /* @__PURE__ */ y.jsx(y.Fragment, {
  children: t(e)
});
function ie(t) {
  return T.createElement(ft, {
    children: t
  });
}
function ae(t, e, l) {
  const s = t.filter(Boolean);
  if (s.length !== 0)
    return s.map((o, n) => {
      var b, v;
      if (typeof o != "object")
        return e != null && e.fallback ? e.fallback(o) : o;
      const r = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...o.props,
        key: ((b = o.props) == null ? void 0 : b.key) ?? (l ? `${l}-${n}` : `${n}`)
      }) : {
        ...o.props,
        key: ((v = o.props) == null ? void 0 : v.key) ?? (l ? `${l}-${n}` : `${n}`)
      };
      let c = r;
      Object.keys(o.slots).forEach((i) => {
        if (!o.slots[i] || !(o.slots[i] instanceof Element) && !o.slots[i].el)
          return;
        const g = i.split(".");
        g.forEach((w, I) => {
          c[w] || (c[w] = {}), I !== g.length - 1 && (c = r[w]);
        });
        const a = o.slots[i];
        let x, p, d = (e == null ? void 0 : e.clone) ?? !1, m = e == null ? void 0 : e.forceClone;
        a instanceof Element ? x = a : (x = a.el, p = a.callback, d = a.clone ?? d, m = a.forceClone ?? m), m = m ?? !!p, c[g[g.length - 1]] = x ? p ? (...w) => (p(g[g.length - 1], w), /* @__PURE__ */ y.jsx(M, {
          ...o.ctx,
          params: w,
          forceClone: m,
          children: /* @__PURE__ */ y.jsx(S, {
            slot: x,
            clone: d
          })
        })) : ie((w) => /* @__PURE__ */ y.jsx(M, {
          ...o.ctx,
          forceClone: m,
          children: /* @__PURE__ */ y.jsx(S, {
            ...w,
            slot: x,
            clone: d
          })
        })) : c[g[g.length - 1]], c = r;
      });
      const u = (e == null ? void 0 : e.children) || "children";
      return o[u] ? r[u] = ae(o[u], e, `${n}`) : e != null && e.children && (r[u] = void 0, Reflect.deleteProperty(r, u)), r;
    });
}
function ee(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? ie((l) => /* @__PURE__ */ y.jsx(M, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ y.jsx(S, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...l
    })
  })) : /* @__PURE__ */ y.jsx(S, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function O({
  key: t,
  slots: e,
  targets: l
}, s) {
  return e[t] ? (...o) => l ? l.map((n, r) => /* @__PURE__ */ y.jsx(T.Fragment, {
    children: ee(n, {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }, r)) : /* @__PURE__ */ y.jsx(y.Fragment, {
    children: ee(e[t], {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }) : void 0;
}
const {
  withItemsContextProvider: dt,
  useItems: mt,
  ItemHandler: gt
} = ye("antd-tree-tree-nodes"), wt = rt(dt(["default", "treeData"], ({
  slots: t,
  filterTreeNode: e,
  treeData: l,
  draggable: s,
  allowDrop: o,
  onCheck: n,
  onSelect: r,
  onExpand: c,
  children: u,
  directory: b,
  setSlotParams: v,
  onLoadData: i,
  titleRender: g,
  ...a
}) => {
  const x = k(e), p = k(s), d = k(g), m = k(typeof s == "object" ? s.nodeDraggable : void 0), w = k(o), I = b ? z.DirectoryTree : z, {
    items: f
  } = mt(), E = f.treeData.length > 0 ? f.treeData : f.default, h = te(() => ({
    ...a,
    treeData: l || ae(E, {
      clone: !0,
      itemPropsTransformer: (_) => _.value && _.key && _.value !== _.key ? {
        ..._,
        key: void 0
      } : _
    }),
    showLine: t["showLine.showLeafIcon"] ? {
      showLeafIcon: O({
        slots: t,
        key: "showLine.showLeafIcon"
      })
    } : a.showLine,
    icon: t.icon ? O({
      slots: t,
      key: "icon"
    }) : a.icon,
    switcherLoadingIcon: t.switcherLoadingIcon ? /* @__PURE__ */ y.jsx(S, {
      slot: t.switcherLoadingIcon
    }) : a.switcherLoadingIcon,
    switcherIcon: t.switcherIcon ? O({
      slots: t,
      key: "switcherIcon"
    }) : a.switcherIcon,
    titleRender: t.titleRender ? O({
      slots: t,
      key: "titleRender"
    }) : d,
    draggable: t["draggable.icon"] || m ? {
      icon: t["draggable.icon"] ? /* @__PURE__ */ y.jsx(S, {
        slot: t["draggable.icon"]
      }) : typeof s == "object" ? s.icon : void 0,
      nodeDraggable: m
    } : p || s,
    // eslint-disable-next-line require-await
    loadData: async (..._) => i == null ? void 0 : i(..._)
  }), [a, l, E, t, v, m, s, d, p, i]);
  return /* @__PURE__ */ y.jsxs(y.Fragment, {
    children: [/* @__PURE__ */ y.jsx("div", {
      style: {
        display: "none"
      },
      children: u
    }), /* @__PURE__ */ y.jsx(I, {
      ...ut(h),
      filterTreeNode: x,
      allowDrop: w,
      onSelect: (_, ...C) => {
        r == null || r(_, ...C);
      },
      onExpand: (_, ...C) => {
        c == null || c(_, ...C);
      },
      onCheck: (_, ...C) => {
        n == null || n(_, ...C);
      }
    })]
  });
}));
export {
  wt as Tree,
  wt as default
};
