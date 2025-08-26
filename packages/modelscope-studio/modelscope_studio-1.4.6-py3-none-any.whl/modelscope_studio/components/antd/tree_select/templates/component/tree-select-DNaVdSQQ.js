import { i as he, a as U, r as _e, Z as j, g as ge, b as pe } from "./Index-DABSO7jw.js";
const R = window.ms_globals.React, ue = window.ms_globals.React.forwardRef, de = window.ms_globals.React.useRef, fe = window.ms_globals.React.useState, me = window.ms_globals.React.useEffect, ee = window.ms_globals.React.useMemo, M = window.ms_globals.ReactDOM.createPortal, xe = window.ms_globals.internalContext.useContextPropsContext, D = window.ms_globals.internalContext.ContextPropsProvider, we = window.ms_globals.antd.TreeSelect, Ce = window.ms_globals.createItemsContext.createItemsContext;
var ye = /\s/;
function be(t) {
  for (var e = t.length; e-- && ye.test(t.charAt(e)); )
    ;
  return e;
}
var ve = /^\s+/;
function Ie(t) {
  return t && t.slice(0, be(t) + 1).replace(ve, "");
}
var z = NaN, Ee = /^[-+]0x[0-9a-f]+$/i, Re = /^0b[01]+$/i, Se = /^0o[0-7]+$/i, Te = parseInt;
function G(t) {
  if (typeof t == "number")
    return t;
  if (he(t))
    return z;
  if (U(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = U(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Ie(t);
  var l = Re.test(t);
  return l || Se.test(t) ? Te(t.slice(2), l ? 2 : 8) : Ee.test(t) ? z : +t;
}
var L = function() {
  return _e.Date.now();
}, ke = "Expected a function", Pe = Math.max, Oe = Math.min;
function je(t, e, l) {
  var c, o, n, r, s, a, g = 0, y = !1, i = !1, p = !0;
  if (typeof t != "function")
    throw new TypeError(ke);
  e = G(e) || 0, U(l) && (y = !!l.leading, i = "maxWait" in l, n = i ? Pe(G(l.maxWait) || 0, e) : n, p = "trailing" in l ? !!l.trailing : p);
  function f(m) {
    var v = c, T = o;
    return c = o = void 0, g = m, r = t.apply(T, v), r;
  }
  function C(m) {
    return g = m, s = setTimeout(h, e), y ? f(m) : r;
  }
  function w(m) {
    var v = m - a, T = m - g, b = e - v;
    return i ? Oe(b, n - T) : b;
  }
  function u(m) {
    var v = m - a, T = m - g;
    return a === void 0 || v >= e || v < 0 || i && T >= n;
  }
  function h() {
    var m = L();
    if (u(m))
      return _(m);
    s = setTimeout(h, w(m));
  }
  function _(m) {
    return s = void 0, p && c ? f(m) : (c = o = void 0, r);
  }
  function I() {
    s !== void 0 && clearTimeout(s), g = 0, c = a = o = s = void 0;
  }
  function d() {
    return s === void 0 ? r : _(L());
  }
  function E() {
    var m = L(), v = u(m);
    if (c = arguments, o = this, a = m, v) {
      if (s === void 0)
        return C(a);
      if (i)
        return clearTimeout(s), s = setTimeout(h, e), f(a);
    }
    return s === void 0 && (s = setTimeout(h, e)), r;
  }
  return E.cancel = I, E.flush = d, E;
}
var te = {
  exports: {}
}, W = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Fe = R, Ne = Symbol.for("react.element"), We = Symbol.for("react.fragment"), Le = Object.prototype.hasOwnProperty, Ae = Fe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Me = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ne(t, e, l) {
  var c, o = {}, n = null, r = null;
  l !== void 0 && (n = "" + l), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (r = e.ref);
  for (c in e) Le.call(e, c) && !Me.hasOwnProperty(c) && (o[c] = e[c]);
  if (t && t.defaultProps) for (c in e = t.defaultProps, e) o[c] === void 0 && (o[c] = e[c]);
  return {
    $$typeof: Ne,
    type: t,
    key: n,
    ref: r,
    props: o,
    _owner: Ae.current
  };
}
W.Fragment = We;
W.jsx = ne;
W.jsxs = ne;
te.exports = W;
var x = te.exports;
const {
  SvelteComponent: Ue,
  assign: q,
  binding_callbacks: V,
  check_outros: De,
  children: re,
  claim_element: le,
  claim_space: Be,
  component_subscribe: J,
  compute_slots: He,
  create_slot: ze,
  detach: O,
  element: oe,
  empty: X,
  exclude_internal_props: Y,
  get_all_dirty_from_scope: Ge,
  get_slot_changes: qe,
  group_outros: Ve,
  init: Je,
  insert_hydration: F,
  safe_not_equal: Xe,
  set_custom_element_data: ce,
  space: Ye,
  transition_in: N,
  transition_out: B,
  update_slot_base: Ze
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ke,
  getContext: Qe,
  onDestroy: $e,
  setContext: et
} = window.__gradio__svelte__internal;
function Z(t) {
  let e, l;
  const c = (
    /*#slots*/
    t[7].default
  ), o = ze(
    c,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = oe("svelte-slot"), o && o.c(), this.h();
    },
    l(n) {
      e = le(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = re(e);
      o && o.l(r), r.forEach(O), this.h();
    },
    h() {
      ce(e, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      F(n, e, r), o && o.m(e, null), t[9](e), l = !0;
    },
    p(n, r) {
      o && o.p && (!l || r & /*$$scope*/
      64) && Ze(
        o,
        c,
        n,
        /*$$scope*/
        n[6],
        l ? qe(
          c,
          /*$$scope*/
          n[6],
          r,
          null
        ) : Ge(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      l || (N(o, n), l = !0);
    },
    o(n) {
      B(o, n), l = !1;
    },
    d(n) {
      n && O(e), o && o.d(n), t[9](null);
    }
  };
}
function tt(t) {
  let e, l, c, o, n = (
    /*$$slots*/
    t[4].default && Z(t)
  );
  return {
    c() {
      e = oe("react-portal-target"), l = Ye(), n && n.c(), c = X(), this.h();
    },
    l(r) {
      e = le(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), re(e).forEach(O), l = Be(r), n && n.l(r), c = X(), this.h();
    },
    h() {
      ce(e, "class", "svelte-1rt0kpf");
    },
    m(r, s) {
      F(r, e, s), t[8](e), F(r, l, s), n && n.m(r, s), F(r, c, s), o = !0;
    },
    p(r, [s]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, s), s & /*$$slots*/
      16 && N(n, 1)) : (n = Z(r), n.c(), N(n, 1), n.m(c.parentNode, c)) : n && (Ve(), B(n, 1, 1, () => {
        n = null;
      }), De());
    },
    i(r) {
      o || (N(n), o = !0);
    },
    o(r) {
      B(n), o = !1;
    },
    d(r) {
      r && (O(e), O(l), O(c)), t[8](null), n && n.d(r);
    }
  };
}
function K(t) {
  const {
    svelteInit: e,
    ...l
  } = t;
  return l;
}
function nt(t, e, l) {
  let c, o, {
    $$slots: n = {},
    $$scope: r
  } = e;
  const s = He(n);
  let {
    svelteInit: a
  } = e;
  const g = j(K(e)), y = j();
  J(t, y, (d) => l(0, c = d));
  const i = j();
  J(t, i, (d) => l(1, o = d));
  const p = [], f = Qe("$$ms-gr-react-wrapper"), {
    slotKey: C,
    slotIndex: w,
    subSlotIndex: u
  } = ge() || {}, h = a({
    parent: f,
    props: g,
    target: y,
    slot: i,
    slotKey: C,
    slotIndex: w,
    subSlotIndex: u,
    onDestroy(d) {
      p.push(d);
    }
  });
  et("$$ms-gr-react-wrapper", h), Ke(() => {
    g.set(K(e));
  }), $e(() => {
    p.forEach((d) => d());
  });
  function _(d) {
    V[d ? "unshift" : "push"](() => {
      c = d, y.set(c);
    });
  }
  function I(d) {
    V[d ? "unshift" : "push"](() => {
      o = d, i.set(o);
    });
  }
  return t.$$set = (d) => {
    l(17, e = q(q({}, e), Y(d))), "svelteInit" in d && l(5, a = d.svelteInit), "$$scope" in d && l(6, r = d.$$scope);
  }, e = Y(e), [c, o, y, i, s, a, r, n, _, I];
}
class rt extends Ue {
  constructor(e) {
    super(), Je(this, e, nt, tt, Xe, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: gt
} = window.__gradio__svelte__internal, Q = window.ms_globals.rerender, A = window.ms_globals.tree;
function lt(t, e = {}) {
  function l(c) {
    const o = j(), n = new rt({
      ...c,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const s = {
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
          }, a = r.parent ?? A;
          return a.nodes = [...a.nodes, s], Q({
            createPortal: M,
            node: A
          }), r.onDestroy(() => {
            a.nodes = a.nodes.filter((g) => g.svelteInstance !== o), Q({
              createPortal: M,
              node: A
            });
          }), s;
        },
        ...c.props
      }
    });
    return o.set(n), n;
  }
  return new Promise((c) => {
    window.ms_globals.initializePromise.then(() => {
      c(l);
    });
  });
}
const ot = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function ct(t) {
  return t ? Object.keys(t).reduce((e, l) => {
    const c = t[l];
    return e[l] = st(l, c), e;
  }, {}) : {};
}
function st(t, e) {
  return typeof e == "number" && !ot.includes(t) ? e + "px" : e;
}
function H(t) {
  const e = [], l = t.cloneNode(!1);
  if (t._reactElement) {
    const o = R.Children.toArray(t._reactElement.props.children).map((n) => {
      if (R.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: s
        } = H(n.props.el);
        return R.cloneElement(n, {
          ...n.props,
          el: s,
          children: [...R.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return o.originalChildren = t._reactElement.props.children, e.push(M(R.cloneElement(t._reactElement, {
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
      type: s,
      useCapture: a
    }) => {
      l.addEventListener(s, r, a);
    });
  });
  const c = Array.from(t.childNodes);
  for (let o = 0; o < c.length; o++) {
    const n = c[o];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: s
      } = H(n);
      e.push(...s), l.appendChild(r);
    } else n.nodeType === 3 && l.appendChild(n.cloneNode());
  }
  return {
    clonedElement: l,
    portals: e
  };
}
function it(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const S = ue(({
  slot: t,
  clone: e,
  className: l,
  style: c,
  observeAttributes: o
}, n) => {
  const r = de(), [s, a] = fe([]), {
    forceClone: g
  } = xe(), y = g ? !0 : e;
  return me(() => {
    var w;
    if (!r.current || !t)
      return;
    let i = t;
    function p() {
      let u = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (u = i.children[0], u.tagName.toLowerCase() === "react-portal-target" && u.children[0] && (u = u.children[0])), it(n, u), l && u.classList.add(...l.split(" ")), c) {
        const h = ct(c);
        Object.keys(h).forEach((_) => {
          u.style[_] = h[_];
        });
      }
    }
    let f = null, C = null;
    if (y && window.MutationObserver) {
      let u = function() {
        var d, E, m;
        (d = r.current) != null && d.contains(i) && ((E = r.current) == null || E.removeChild(i));
        const {
          portals: _,
          clonedElement: I
        } = H(t);
        i = I, a(_), i.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          p();
        }, 50), (m = r.current) == null || m.appendChild(i);
      };
      u();
      const h = je(() => {
        u(), f == null || f.disconnect(), f == null || f.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      f = new window.MutationObserver(h), f.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", p(), (w = r.current) == null || w.appendChild(i);
    return () => {
      var u, h;
      i.style.display = "", (u = r.current) != null && u.contains(i) && ((h = r.current) == null || h.removeChild(i)), f == null || f.disconnect();
    };
  }, [t, y, l, c, n, o, g]), R.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...s);
});
function at(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function ut(t, e = !1) {
  try {
    if (pe(t))
      return t;
    if (e && !at(t))
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
  return ee(() => ut(t, e), [t, e]);
}
function dt(t, e) {
  return Object.keys(t).reduce((l, c) => (t[c] !== void 0 && (l[c] = t[c]), l), {});
}
const ft = ({
  children: t,
  ...e
}) => /* @__PURE__ */ x.jsx(x.Fragment, {
  children: t(e)
});
function se(t) {
  return R.createElement(ft, {
    children: t
  });
}
function ie(t, e, l) {
  const c = t.filter(Boolean);
  if (c.length !== 0)
    return c.map((o, n) => {
      var g, y;
      if (typeof o != "object")
        return e != null && e.fallback ? e.fallback(o) : o;
      const r = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...o.props,
        key: ((g = o.props) == null ? void 0 : g.key) ?? (l ? `${l}-${n}` : `${n}`)
      }) : {
        ...o.props,
        key: ((y = o.props) == null ? void 0 : y.key) ?? (l ? `${l}-${n}` : `${n}`)
      };
      let s = r;
      Object.keys(o.slots).forEach((i) => {
        if (!o.slots[i] || !(o.slots[i] instanceof Element) && !o.slots[i].el)
          return;
        const p = i.split(".");
        p.forEach((_, I) => {
          s[_] || (s[_] = {}), I !== p.length - 1 && (s = r[_]);
        });
        const f = o.slots[i];
        let C, w, u = (e == null ? void 0 : e.clone) ?? !1, h = e == null ? void 0 : e.forceClone;
        f instanceof Element ? C = f : (C = f.el, w = f.callback, u = f.clone ?? u, h = f.forceClone ?? h), h = h ?? !!w, s[p[p.length - 1]] = C ? w ? (..._) => (w(p[p.length - 1], _), /* @__PURE__ */ x.jsx(D, {
          ...o.ctx,
          params: _,
          forceClone: h,
          children: /* @__PURE__ */ x.jsx(S, {
            slot: C,
            clone: u
          })
        })) : se((_) => /* @__PURE__ */ x.jsx(D, {
          ...o.ctx,
          forceClone: h,
          children: /* @__PURE__ */ x.jsx(S, {
            ..._,
            slot: C,
            clone: u
          })
        })) : s[p[p.length - 1]], s = r;
      });
      const a = (e == null ? void 0 : e.children) || "children";
      return o[a] ? r[a] = ie(o[a], e, `${n}`) : e != null && e.children && (r[a] = void 0, Reflect.deleteProperty(r, a)), r;
    });
}
function $(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? se((l) => /* @__PURE__ */ x.jsx(D, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ x.jsx(S, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...l
    })
  })) : /* @__PURE__ */ x.jsx(S, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function P({
  key: t,
  slots: e,
  targets: l
}, c) {
  return e[t] ? (...o) => l ? l.map((n, r) => /* @__PURE__ */ x.jsx(R.Fragment, {
    children: $(n, {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }, r)) : /* @__PURE__ */ x.jsx(x.Fragment, {
    children: $(e[t], {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }) : void 0;
}
const {
  withItemsContextProvider: mt,
  useItems: ht,
  ItemHandler: pt
} = Ce("antd-tree-select-tree-nodes"), xt = lt(mt(["default", "treeData"], ({
  slots: t,
  filterTreeNode: e,
  getPopupContainer: l,
  dropdownRender: c,
  popupRender: o,
  tagRender: n,
  treeTitleRender: r,
  treeData: s,
  onValueChange: a,
  onChange: g,
  children: y,
  maxTagPlaceholder: i,
  elRef: p,
  setSlotParams: f,
  onLoadData: C,
  ...w
}) => {
  const u = k(e), h = k(l), _ = k(n), I = k(c), d = k(o), E = k(r), {
    items: m
  } = ht(), v = m.treeData.length > 0 ? m.treeData : m.default, T = ee(() => ({
    ...w,
    // eslint-disable-next-line require-await
    loadData: async (...b) => C == null ? void 0 : C(...b),
    treeData: s || ie(v, {
      clone: !0,
      itemPropsTransformer: (b) => b.value && b.key && b.value !== b.key ? {
        ...b,
        key: void 0
      } : b
    }),
    dropdownRender: t.dropdownRender ? P({
      slots: t,
      key: "dropdownRender"
    }) : I,
    popupRender: t.popupRender ? P({
      slots: t,
      key: "popupRender"
    }) : d,
    allowClear: t["allowClear.clearIcon"] ? {
      clearIcon: /* @__PURE__ */ x.jsx(S, {
        slot: t["allowClear.clearIcon"]
      })
    } : w.allowClear,
    suffixIcon: t.suffixIcon ? /* @__PURE__ */ x.jsx(S, {
      slot: t.suffixIcon
    }) : w.suffixIcon,
    prefix: t.prefix ? /* @__PURE__ */ x.jsx(S, {
      slot: t.prefix
    }) : w.prefix,
    switcherIcon: t.switcherIcon ? P({
      slots: t,
      key: "switcherIcon"
    }) : w.switcherIcon,
    getPopupContainer: h,
    tagRender: t.tagRender ? P({
      slots: t,
      key: "tagRender"
    }) : _,
    treeTitleRender: t.treeTitleRender ? P({
      slots: t,
      key: "treeTitleRender"
    }) : E,
    filterTreeNode: u || e,
    maxTagPlaceholder: t.maxTagPlaceholder ? P({
      slots: t,
      key: "maxTagPlaceholder"
    }) : i,
    notFoundContent: t.notFoundContent ? /* @__PURE__ */ x.jsx(S, {
      slot: t.notFoundContent
    }) : w.notFoundContent
  }), [I, d, e, u, h, i, C, w, f, v, t, _, s, E]);
  return /* @__PURE__ */ x.jsxs(x.Fragment, {
    children: [/* @__PURE__ */ x.jsx("div", {
      style: {
        display: "none"
      },
      children: y
    }), /* @__PURE__ */ x.jsx(we, {
      ...dt(T),
      ref: p,
      onChange: (b, ...ae) => {
        g == null || g(b, ...ae), a(b);
      }
    })]
  });
}));
export {
  xt as TreeSelect,
  xt as default
};
