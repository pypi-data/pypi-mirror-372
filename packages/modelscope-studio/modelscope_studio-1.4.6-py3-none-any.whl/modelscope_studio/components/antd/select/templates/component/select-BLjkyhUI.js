import { i as _e, a as D, r as ge, Z as O, g as pe, b as xe } from "./Index-C41Wh_9F.js";
const R = window.ms_globals.React, de = window.ms_globals.React.forwardRef, fe = window.ms_globals.React.useRef, me = window.ms_globals.React.useState, he = window.ms_globals.React.useEffect, te = window.ms_globals.React.useMemo, M = window.ms_globals.ReactDOM.createPortal, we = window.ms_globals.internalContext.useContextPropsContext, U = window.ms_globals.internalContext.ContextPropsProvider, be = window.ms_globals.antd.Select, Ce = window.ms_globals.createItemsContext.createItemsContext;
var Ie = /\s/;
function ye(e) {
  for (var t = e.length; t-- && Ie.test(e.charAt(t)); )
    ;
  return t;
}
var ve = /^\s+/;
function Ee(e) {
  return e && e.slice(0, ye(e) + 1).replace(ve, "");
}
var G = NaN, Re = /^[-+]0x[0-9a-f]+$/i, Se = /^0b[01]+$/i, Pe = /^0o[0-7]+$/i, ke = parseInt;
function q(e) {
  if (typeof e == "number")
    return e;
  if (_e(e))
    return G;
  if (D(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = D(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Ee(e);
  var o = Se.test(e);
  return o || Pe.test(e) ? ke(e.slice(2), o ? 2 : 8) : Re.test(e) ? G : +e;
}
var W = function() {
  return ge.Date.now();
}, Te = "Expected a function", je = Math.max, Oe = Math.min;
function Fe(e, t, o) {
  var c, r, n, l, s, a, w = 0, b = !1, i = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(Te);
  t = q(t) || 0, D(o) && (b = !!o.leading, i = "maxWait" in o, n = i ? je(q(o.maxWait) || 0, t) : n, g = "trailing" in o ? !!o.trailing : g);
  function u(m) {
    var I = c, E = r;
    return c = r = void 0, w = m, l = e.apply(E, I), l;
  }
  function C(m) {
    return w = m, s = setTimeout(h, t), b ? u(m) : l;
  }
  function p(m) {
    var I = m - a, E = m - w, j = t - I;
    return i ? Oe(j, n - E) : j;
  }
  function d(m) {
    var I = m - a, E = m - w;
    return a === void 0 || I >= t || I < 0 || i && E >= n;
  }
  function h() {
    var m = W();
    if (d(m))
      return x(m);
    s = setTimeout(h, p(m));
  }
  function x(m) {
    return s = void 0, g && c ? u(m) : (c = r = void 0, l);
  }
  function v() {
    s !== void 0 && clearTimeout(s), w = 0, c = a = r = s = void 0;
  }
  function f() {
    return s === void 0 ? l : x(W());
  }
  function S() {
    var m = W(), I = d(m);
    if (c = arguments, r = this, a = m, I) {
      if (s === void 0)
        return C(a);
      if (i)
        return clearTimeout(s), s = setTimeout(h, t), u(a);
    }
    return s === void 0 && (s = setTimeout(h, t)), l;
  }
  return S.cancel = v, S.flush = f, S;
}
var ne = {
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
var Le = R, Ne = Symbol.for("react.element"), We = Symbol.for("react.fragment"), Ae = Object.prototype.hasOwnProperty, Me = Le.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, De = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function re(e, t, o) {
  var c, r = {}, n = null, l = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (l = t.ref);
  for (c in t) Ae.call(t, c) && !De.hasOwnProperty(c) && (r[c] = t[c]);
  if (e && e.defaultProps) for (c in t = e.defaultProps, t) r[c] === void 0 && (r[c] = t[c]);
  return {
    $$typeof: Ne,
    type: e,
    key: n,
    ref: l,
    props: r,
    _owner: Me.current
  };
}
N.Fragment = We;
N.jsx = re;
N.jsxs = re;
ne.exports = N;
var _ = ne.exports;
const {
  SvelteComponent: Ue,
  assign: V,
  binding_callbacks: J,
  check_outros: Be,
  children: le,
  claim_element: oe,
  claim_space: He,
  component_subscribe: X,
  compute_slots: ze,
  create_slot: Ge,
  detach: T,
  element: ce,
  empty: Y,
  exclude_internal_props: Z,
  get_all_dirty_from_scope: qe,
  get_slot_changes: Ve,
  group_outros: Je,
  init: Xe,
  insert_hydration: F,
  safe_not_equal: Ye,
  set_custom_element_data: se,
  space: Ze,
  transition_in: L,
  transition_out: B,
  update_slot_base: Ke
} = window.__gradio__svelte__internal, {
  beforeUpdate: Qe,
  getContext: $e,
  onDestroy: et,
  setContext: tt
} = window.__gradio__svelte__internal;
function K(e) {
  let t, o;
  const c = (
    /*#slots*/
    e[7].default
  ), r = Ge(
    c,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ce("svelte-slot"), r && r.c(), this.h();
    },
    l(n) {
      t = oe(n, "SVELTE-SLOT", {
        class: !0
      });
      var l = le(t);
      r && r.l(l), l.forEach(T), this.h();
    },
    h() {
      se(t, "class", "svelte-1rt0kpf");
    },
    m(n, l) {
      F(n, t, l), r && r.m(t, null), e[9](t), o = !0;
    },
    p(n, l) {
      r && r.p && (!o || l & /*$$scope*/
      64) && Ke(
        r,
        c,
        n,
        /*$$scope*/
        n[6],
        o ? Ve(
          c,
          /*$$scope*/
          n[6],
          l,
          null
        ) : qe(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (L(r, n), o = !0);
    },
    o(n) {
      B(r, n), o = !1;
    },
    d(n) {
      n && T(t), r && r.d(n), e[9](null);
    }
  };
}
function nt(e) {
  let t, o, c, r, n = (
    /*$$slots*/
    e[4].default && K(e)
  );
  return {
    c() {
      t = ce("react-portal-target"), o = Ze(), n && n.c(), c = Y(), this.h();
    },
    l(l) {
      t = oe(l, "REACT-PORTAL-TARGET", {
        class: !0
      }), le(t).forEach(T), o = He(l), n && n.l(l), c = Y(), this.h();
    },
    h() {
      se(t, "class", "svelte-1rt0kpf");
    },
    m(l, s) {
      F(l, t, s), e[8](t), F(l, o, s), n && n.m(l, s), F(l, c, s), r = !0;
    },
    p(l, [s]) {
      /*$$slots*/
      l[4].default ? n ? (n.p(l, s), s & /*$$slots*/
      16 && L(n, 1)) : (n = K(l), n.c(), L(n, 1), n.m(c.parentNode, c)) : n && (Je(), B(n, 1, 1, () => {
        n = null;
      }), Be());
    },
    i(l) {
      r || (L(n), r = !0);
    },
    o(l) {
      B(n), r = !1;
    },
    d(l) {
      l && (T(t), T(o), T(c)), e[8](null), n && n.d(l);
    }
  };
}
function Q(e) {
  const {
    svelteInit: t,
    ...o
  } = e;
  return o;
}
function rt(e, t, o) {
  let c, r, {
    $$slots: n = {},
    $$scope: l
  } = t;
  const s = ze(n);
  let {
    svelteInit: a
  } = t;
  const w = O(Q(t)), b = O();
  X(e, b, (f) => o(0, c = f));
  const i = O();
  X(e, i, (f) => o(1, r = f));
  const g = [], u = $e("$$ms-gr-react-wrapper"), {
    slotKey: C,
    slotIndex: p,
    subSlotIndex: d
  } = pe() || {}, h = a({
    parent: u,
    props: w,
    target: b,
    slot: i,
    slotKey: C,
    slotIndex: p,
    subSlotIndex: d,
    onDestroy(f) {
      g.push(f);
    }
  });
  tt("$$ms-gr-react-wrapper", h), Qe(() => {
    w.set(Q(t));
  }), et(() => {
    g.forEach((f) => f());
  });
  function x(f) {
    J[f ? "unshift" : "push"](() => {
      c = f, b.set(c);
    });
  }
  function v(f) {
    J[f ? "unshift" : "push"](() => {
      r = f, i.set(r);
    });
  }
  return e.$$set = (f) => {
    o(17, t = V(V({}, t), Z(f))), "svelteInit" in f && o(5, a = f.svelteInit), "$$scope" in f && o(6, l = f.$$scope);
  }, t = Z(t), [c, r, b, i, s, a, l, n, x, v];
}
class lt extends Ue {
  constructor(t) {
    super(), Xe(this, t, rt, nt, Ye, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: gt
} = window.__gradio__svelte__internal, $ = window.ms_globals.rerender, A = window.ms_globals.tree;
function ot(e, t = {}) {
  function o(c) {
    const r = O(), n = new lt({
      ...c,
      props: {
        svelteInit(l) {
          window.ms_globals.autokey += 1;
          const s = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: e,
            props: l.props,
            slot: l.slot,
            target: l.target,
            slotIndex: l.slotIndex,
            subSlotIndex: l.subSlotIndex,
            ignore: t.ignore,
            slotKey: l.slotKey,
            nodes: []
          }, a = l.parent ?? A;
          return a.nodes = [...a.nodes, s], $({
            createPortal: M,
            node: A
          }), l.onDestroy(() => {
            a.nodes = a.nodes.filter((w) => w.svelteInstance !== r), $({
              createPortal: M,
              node: A
            });
          }), s;
        },
        ...c.props
      }
    });
    return r.set(n), n;
  }
  return new Promise((c) => {
    window.ms_globals.initializePromise.then(() => {
      c(o);
    });
  });
}
const ct = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function st(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const c = e[o];
    return t[o] = it(o, c), t;
  }, {}) : {};
}
function it(e, t) {
  return typeof t == "number" && !ct.includes(e) ? t + "px" : t;
}
function H(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const r = R.Children.toArray(e._reactElement.props.children).map((n) => {
      if (R.isValidElement(n) && n.props.__slot__) {
        const {
          portals: l,
          clonedElement: s
        } = H(n.props.el);
        return R.cloneElement(n, {
          ...n.props,
          el: s,
          children: [...R.Children.toArray(n.props.children), ...l]
        });
      }
      return null;
    });
    return r.originalChildren = e._reactElement.props.children, t.push(M(R.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: r
    }), o)), {
      clonedElement: o,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((r) => {
    e.getEventListeners(r).forEach(({
      listener: l,
      type: s,
      useCapture: a
    }) => {
      o.addEventListener(s, l, a);
    });
  });
  const c = Array.from(e.childNodes);
  for (let r = 0; r < c.length; r++) {
    const n = c[r];
    if (n.nodeType === 1) {
      const {
        clonedElement: l,
        portals: s
      } = H(n);
      t.push(...s), o.appendChild(l);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: t
  };
}
function at(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const y = de(({
  slot: e,
  clone: t,
  className: o,
  style: c,
  observeAttributes: r
}, n) => {
  const l = fe(), [s, a] = me([]), {
    forceClone: w
  } = we(), b = w ? !0 : t;
  return he(() => {
    var p;
    if (!l.current || !e)
      return;
    let i = e;
    function g() {
      let d = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (d = i.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), at(n, d), o && d.classList.add(...o.split(" ")), c) {
        const h = st(c);
        Object.keys(h).forEach((x) => {
          d.style[x] = h[x];
        });
      }
    }
    let u = null, C = null;
    if (b && window.MutationObserver) {
      let d = function() {
        var f, S, m;
        (f = l.current) != null && f.contains(i) && ((S = l.current) == null || S.removeChild(i));
        const {
          portals: x,
          clonedElement: v
        } = H(e);
        i = v, a(x), i.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          g();
        }, 50), (m = l.current) == null || m.appendChild(i);
      };
      d();
      const h = Fe(() => {
        d(), u == null || u.disconnect(), u == null || u.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      u = new window.MutationObserver(h), u.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", g(), (p = l.current) == null || p.appendChild(i);
    return () => {
      var d, h;
      i.style.display = "", (d = l.current) != null && d.contains(i) && ((h = l.current) == null || h.removeChild(i)), u == null || u.disconnect();
    };
  }, [e, b, o, c, n, r, w]), R.createElement("react-child", {
    ref: l,
    style: {
      display: "contents"
    }
  }, ...s);
});
function ut(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function dt(e, t = !1) {
  try {
    if (xe(e))
      return e;
    if (t && !ut(e))
      return;
    if (typeof e == "string") {
      let o = e.trim();
      return o.startsWith(";") && (o = o.slice(1)), o.endsWith(";") && (o = o.slice(0, -1)), new Function(`return (...args) => (${o})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function P(e, t) {
  return te(() => dt(e, t), [e, t]);
}
const ft = ({
  children: e,
  ...t
}) => /* @__PURE__ */ _.jsx(_.Fragment, {
  children: e(t)
});
function ie(e) {
  return R.createElement(ft, {
    children: e
  });
}
function ae(e, t, o) {
  const c = e.filter(Boolean);
  if (c.length !== 0)
    return c.map((r, n) => {
      var w, b;
      if (typeof r != "object")
        return t != null && t.fallback ? t.fallback(r) : r;
      const l = t != null && t.itemPropsTransformer ? t == null ? void 0 : t.itemPropsTransformer({
        ...r.props,
        key: ((w = r.props) == null ? void 0 : w.key) ?? (o ? `${o}-${n}` : `${n}`)
      }) : {
        ...r.props,
        key: ((b = r.props) == null ? void 0 : b.key) ?? (o ? `${o}-${n}` : `${n}`)
      };
      let s = l;
      Object.keys(r.slots).forEach((i) => {
        if (!r.slots[i] || !(r.slots[i] instanceof Element) && !r.slots[i].el)
          return;
        const g = i.split(".");
        g.forEach((x, v) => {
          s[x] || (s[x] = {}), v !== g.length - 1 && (s = l[x]);
        });
        const u = r.slots[i];
        let C, p, d = (t == null ? void 0 : t.clone) ?? !1, h = t == null ? void 0 : t.forceClone;
        u instanceof Element ? C = u : (C = u.el, p = u.callback, d = u.clone ?? d, h = u.forceClone ?? h), h = h ?? !!p, s[g[g.length - 1]] = C ? p ? (...x) => (p(g[g.length - 1], x), /* @__PURE__ */ _.jsx(U, {
          ...r.ctx,
          params: x,
          forceClone: h,
          children: /* @__PURE__ */ _.jsx(y, {
            slot: C,
            clone: d
          })
        })) : ie((x) => /* @__PURE__ */ _.jsx(U, {
          ...r.ctx,
          forceClone: h,
          children: /* @__PURE__ */ _.jsx(y, {
            ...x,
            slot: C,
            clone: d
          })
        })) : s[g[g.length - 1]], s = l;
      });
      const a = (t == null ? void 0 : t.children) || "children";
      return r[a] ? l[a] = ae(r[a], t, `${n}`) : t != null && t.children && (l[a] = void 0, Reflect.deleteProperty(l, a)), l;
    });
}
function ee(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ie((o) => /* @__PURE__ */ _.jsx(U, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ _.jsx(y, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...o
    })
  })) : /* @__PURE__ */ _.jsx(y, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function k({
  key: e,
  slots: t,
  targets: o
}, c) {
  return t[e] ? (...r) => o ? o.map((n, l) => /* @__PURE__ */ _.jsx(R.Fragment, {
    children: ee(n, {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }, l)) : /* @__PURE__ */ _.jsx(_.Fragment, {
    children: ee(t[e], {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }) : void 0;
}
const {
  withItemsContextProvider: mt,
  useItems: ht,
  ItemHandler: pt
} = Ce("antd-select-options"), xt = ot(mt(["options", "default"], ({
  slots: e,
  children: t,
  onValueChange: o,
  filterOption: c,
  onChange: r,
  options: n,
  getPopupContainer: l,
  dropdownRender: s,
  popupRender: a,
  optionRender: w,
  tagRender: b,
  labelRender: i,
  filterSort: g,
  elRef: u,
  setSlotParams: C,
  ...p
}) => {
  const d = P(l), h = P(c), x = P(s), v = P(a), f = P(g), S = P(w), m = P(b), I = P(i), {
    items: E
  } = ht(), j = E.options.length > 0 ? E.options : E.default;
  return /* @__PURE__ */ _.jsxs(_.Fragment, {
    children: [/* @__PURE__ */ _.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ _.jsx(be, {
      ...p,
      ref: u,
      options: te(() => n || ae(j, {
        children: "options",
        clone: !0
      }), [j, n]),
      onChange: (z, ...ue) => {
        r == null || r(z, ...ue), o(z);
      },
      allowClear: e["allowClear.clearIcon"] ? {
        clearIcon: /* @__PURE__ */ _.jsx(y, {
          slot: e["allowClear.clearIcon"]
        })
      } : p.allowClear,
      prefix: e.prefix ? /* @__PURE__ */ _.jsx(y, {
        slot: e.prefix
      }) : p.prefix,
      removeIcon: e.removeIcon ? /* @__PURE__ */ _.jsx(y, {
        slot: e.removeIcon
      }) : p.removeIcon,
      suffixIcon: e.suffixIcon ? /* @__PURE__ */ _.jsx(y, {
        slot: e.suffixIcon
      }) : p.suffixIcon,
      notFoundContent: e.notFoundContent ? /* @__PURE__ */ _.jsx(y, {
        slot: e.notFoundContent
      }) : p.notFoundContent,
      menuItemSelectedIcon: e.menuItemSelectedIcon ? /* @__PURE__ */ _.jsx(y, {
        slot: e.menuItemSelectedIcon
      }) : p.menuItemSelectedIcon,
      filterOption: h || c,
      maxTagPlaceholder: e.maxTagPlaceholder ? k({
        slots: e,
        key: "maxTagPlaceholder"
      }) : p.maxTagPlaceholder,
      getPopupContainer: d,
      dropdownRender: e.dropdownRender ? k({
        slots: e,
        key: "dropdownRender"
      }) : x,
      popupRender: e.popupRender ? k({
        slots: e,
        key: "popupRender"
      }) : v,
      optionRender: e.optionRender ? k({
        slots: e,
        key: "optionRender"
      }) : S,
      tagRender: e.tagRender ? k({
        slots: e,
        key: "tagRender"
      }) : m,
      labelRender: e.labelRender ? k({
        slots: e,
        key: "labelRender"
      }) : I,
      filterSort: f
    })]
  });
}));
export {
  xt as Select,
  xt as default
};
