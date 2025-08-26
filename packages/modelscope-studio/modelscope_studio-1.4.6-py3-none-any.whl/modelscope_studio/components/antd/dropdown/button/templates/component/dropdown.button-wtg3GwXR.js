import { i as he, a as B, r as pe, Z as j, g as ge, t as xe, s as k, b as we } from "./Index-yU2GZ9At.js";
const y = window.ms_globals.React, A = window.ms_globals.React.useMemo, re = window.ms_globals.React.useState, oe = window.ms_globals.React.useEffect, me = window.ms_globals.React.forwardRef, _e = window.ms_globals.React.useRef, M = window.ms_globals.ReactDOM.createPortal, be = window.ms_globals.internalContext.useContextPropsContext, U = window.ms_globals.internalContext.ContextPropsProvider, Ce = window.ms_globals.antd.Dropdown, Ie = window.ms_globals.createItemsContext.createItemsContext;
var ye = /\s/;
function ve(t) {
  for (var e = t.length; e-- && ye.test(t.charAt(e)); )
    ;
  return e;
}
var Ee = /^\s+/;
function Se(t) {
  return t && t.slice(0, ve(t) + 1).replace(Ee, "");
}
var V = NaN, Re = /^[-+]0x[0-9a-f]+$/i, Pe = /^0b[01]+$/i, ke = /^0o[0-7]+$/i, Te = parseInt;
function q(t) {
  if (typeof t == "number")
    return t;
  if (he(t))
    return V;
  if (B(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = B(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Se(t);
  var r = Pe.test(t);
  return r || ke.test(t) ? Te(t.slice(2), r ? 2 : 8) : Re.test(t) ? V : +t;
}
var W = function() {
  return pe.Date.now();
}, Oe = "Expected a function", je = Math.max, Fe = Math.min;
function Le(t, e, r) {
  var s, l, n, o, c, i, g = 0, b = !1, a = !1, p = !0;
  if (typeof t != "function")
    throw new TypeError(Oe);
  e = q(e) || 0, B(r) && (b = !!r.leading, a = "maxWait" in r, n = a ? je(q(r.maxWait) || 0, e) : n, p = "trailing" in r ? !!r.trailing : p);
  function u(_) {
    var v = s, P = l;
    return s = l = void 0, g = _, o = t.apply(P, v), o;
  }
  function w(_) {
    return g = _, c = setTimeout(f, e), b ? u(_) : o;
  }
  function C(_) {
    var v = _ - i, P = _ - g, G = e - v;
    return a ? Fe(G, n - P) : G;
  }
  function d(_) {
    var v = _ - i, P = _ - g;
    return i === void 0 || v >= e || v < 0 || a && P >= n;
  }
  function f() {
    var _ = W();
    if (d(_))
      return h(_);
    c = setTimeout(f, C(_));
  }
  function h(_) {
    return c = void 0, p && s ? u(_) : (s = l = void 0, o);
  }
  function I() {
    c !== void 0 && clearTimeout(c), g = 0, s = i = l = c = void 0;
  }
  function m() {
    return c === void 0 ? o : h(W());
  }
  function E() {
    var _ = W(), v = d(_);
    if (s = arguments, l = this, i = _, v) {
      if (c === void 0)
        return w(i);
      if (a)
        return clearTimeout(c), c = setTimeout(f, e), u(i);
    }
    return c === void 0 && (c = setTimeout(f, e)), o;
  }
  return E.cancel = I, E.flush = m, E;
}
var le = {
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
var Ae = y, Ne = Symbol.for("react.element"), We = Symbol.for("react.fragment"), De = Object.prototype.hasOwnProperty, Me = Ae.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Be = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function se(t, e, r) {
  var s, l = {}, n = null, o = null;
  r !== void 0 && (n = "" + r), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (o = e.ref);
  for (s in e) De.call(e, s) && !Be.hasOwnProperty(s) && (l[s] = e[s]);
  if (t && t.defaultProps) for (s in e = t.defaultProps, e) l[s] === void 0 && (l[s] = e[s]);
  return {
    $$typeof: Ne,
    type: t,
    key: n,
    ref: o,
    props: l,
    _owner: Me.current
  };
}
N.Fragment = We;
N.jsx = se;
N.jsxs = se;
le.exports = N;
var x = le.exports;
const {
  SvelteComponent: Ue,
  assign: J,
  binding_callbacks: X,
  check_outros: He,
  children: ce,
  claim_element: ie,
  claim_space: ze,
  component_subscribe: Y,
  compute_slots: Ge,
  create_slot: Ve,
  detach: S,
  element: ae,
  empty: Z,
  exclude_internal_props: Q,
  get_all_dirty_from_scope: qe,
  get_slot_changes: Je,
  group_outros: Xe,
  init: Ye,
  insert_hydration: F,
  safe_not_equal: Ze,
  set_custom_element_data: ue,
  space: Qe,
  transition_in: L,
  transition_out: H,
  update_slot_base: Ke
} = window.__gradio__svelte__internal, {
  beforeUpdate: $e,
  getContext: et,
  onDestroy: tt,
  setContext: nt
} = window.__gradio__svelte__internal;
function K(t) {
  let e, r;
  const s = (
    /*#slots*/
    t[7].default
  ), l = Ve(
    s,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = ae("svelte-slot"), l && l.c(), this.h();
    },
    l(n) {
      e = ie(n, "SVELTE-SLOT", {
        class: !0
      });
      var o = ce(e);
      l && l.l(o), o.forEach(S), this.h();
    },
    h() {
      ue(e, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      F(n, e, o), l && l.m(e, null), t[9](e), r = !0;
    },
    p(n, o) {
      l && l.p && (!r || o & /*$$scope*/
      64) && Ke(
        l,
        s,
        n,
        /*$$scope*/
        n[6],
        r ? Je(
          s,
          /*$$scope*/
          n[6],
          o,
          null
        ) : qe(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      r || (L(l, n), r = !0);
    },
    o(n) {
      H(l, n), r = !1;
    },
    d(n) {
      n && S(e), l && l.d(n), t[9](null);
    }
  };
}
function rt(t) {
  let e, r, s, l, n = (
    /*$$slots*/
    t[4].default && K(t)
  );
  return {
    c() {
      e = ae("react-portal-target"), r = Qe(), n && n.c(), s = Z(), this.h();
    },
    l(o) {
      e = ie(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), ce(e).forEach(S), r = ze(o), n && n.l(o), s = Z(), this.h();
    },
    h() {
      ue(e, "class", "svelte-1rt0kpf");
    },
    m(o, c) {
      F(o, e, c), t[8](e), F(o, r, c), n && n.m(o, c), F(o, s, c), l = !0;
    },
    p(o, [c]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, c), c & /*$$slots*/
      16 && L(n, 1)) : (n = K(o), n.c(), L(n, 1), n.m(s.parentNode, s)) : n && (Xe(), H(n, 1, 1, () => {
        n = null;
      }), He());
    },
    i(o) {
      l || (L(n), l = !0);
    },
    o(o) {
      H(n), l = !1;
    },
    d(o) {
      o && (S(e), S(r), S(s)), t[8](null), n && n.d(o);
    }
  };
}
function $(t) {
  const {
    svelteInit: e,
    ...r
  } = t;
  return r;
}
function ot(t, e, r) {
  let s, l, {
    $$slots: n = {},
    $$scope: o
  } = e;
  const c = Ge(n);
  let {
    svelteInit: i
  } = e;
  const g = j($(e)), b = j();
  Y(t, b, (m) => r(0, s = m));
  const a = j();
  Y(t, a, (m) => r(1, l = m));
  const p = [], u = et("$$ms-gr-react-wrapper"), {
    slotKey: w,
    slotIndex: C,
    subSlotIndex: d
  } = ge() || {}, f = i({
    parent: u,
    props: g,
    target: b,
    slot: a,
    slotKey: w,
    slotIndex: C,
    subSlotIndex: d,
    onDestroy(m) {
      p.push(m);
    }
  });
  nt("$$ms-gr-react-wrapper", f), $e(() => {
    g.set($(e));
  }), tt(() => {
    p.forEach((m) => m());
  });
  function h(m) {
    X[m ? "unshift" : "push"](() => {
      s = m, b.set(s);
    });
  }
  function I(m) {
    X[m ? "unshift" : "push"](() => {
      l = m, a.set(l);
    });
  }
  return t.$$set = (m) => {
    r(17, e = J(J({}, e), Q(m))), "svelteInit" in m && r(5, i = m.svelteInit), "$$scope" in m && r(6, o = m.$$scope);
  }, e = Q(e), [s, l, b, a, c, i, o, n, h, I];
}
class lt extends Ue {
  constructor(e) {
    super(), Ye(this, e, ot, rt, Ze, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: wt
} = window.__gradio__svelte__internal, ee = window.ms_globals.rerender, D = window.ms_globals.tree;
function st(t, e = {}) {
  function r(s) {
    const l = j(), n = new lt({
      ...s,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: l,
            reactComponent: t,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: e.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, i = o.parent ?? D;
          return i.nodes = [...i.nodes, c], ee({
            createPortal: M,
            node: D
          }), o.onDestroy(() => {
            i.nodes = i.nodes.filter((g) => g.svelteInstance !== l), ee({
              createPortal: M,
              node: D
            });
          }), c;
        },
        ...s.props
      }
    });
    return l.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise.then(() => {
      s(r);
    });
  });
}
function ct(t) {
  const [e, r] = re(() => k(t));
  return oe(() => {
    let s = !0;
    return t.subscribe((n) => {
      s && (s = !1, n === e) || r(n);
    });
  }, [t]), e;
}
function it(t) {
  const e = A(() => xe(t, (r) => r), [t]);
  return ct(e);
}
const at = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function ut(t) {
  return t ? Object.keys(t).reduce((e, r) => {
    const s = t[r];
    return e[r] = dt(r, s), e;
  }, {}) : {};
}
function dt(t, e) {
  return typeof e == "number" && !at.includes(t) ? e + "px" : e;
}
function z(t) {
  const e = [], r = t.cloneNode(!1);
  if (t._reactElement) {
    const l = y.Children.toArray(t._reactElement.props.children).map((n) => {
      if (y.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: c
        } = z(n.props.el);
        return y.cloneElement(n, {
          ...n.props,
          el: c,
          children: [...y.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return l.originalChildren = t._reactElement.props.children, e.push(M(y.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: l
    }), r)), {
      clonedElement: r,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((l) => {
    t.getEventListeners(l).forEach(({
      listener: o,
      type: c,
      useCapture: i
    }) => {
      r.addEventListener(c, o, i);
    });
  });
  const s = Array.from(t.childNodes);
  for (let l = 0; l < s.length; l++) {
    const n = s[l];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: c
      } = z(n);
      e.push(...c), r.appendChild(o);
    } else n.nodeType === 3 && r.appendChild(n.cloneNode());
  }
  return {
    clonedElement: r,
    portals: e
  };
}
function ft(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const R = me(({
  slot: t,
  clone: e,
  className: r,
  style: s,
  observeAttributes: l
}, n) => {
  const o = _e(), [c, i] = re([]), {
    forceClone: g
  } = be(), b = g ? !0 : e;
  return oe(() => {
    var C;
    if (!o.current || !t)
      return;
    let a = t;
    function p() {
      let d = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (d = a.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), ft(n, d), r && d.classList.add(...r.split(" ")), s) {
        const f = ut(s);
        Object.keys(f).forEach((h) => {
          d.style[h] = f[h];
        });
      }
    }
    let u = null, w = null;
    if (b && window.MutationObserver) {
      let d = function() {
        var m, E, _;
        (m = o.current) != null && m.contains(a) && ((E = o.current) == null || E.removeChild(a));
        const {
          portals: h,
          clonedElement: I
        } = z(t);
        a = I, i(h), a.style.display = "contents", w && clearTimeout(w), w = setTimeout(() => {
          p();
        }, 50), (_ = o.current) == null || _.appendChild(a);
      };
      d();
      const f = Le(() => {
        d(), u == null || u.disconnect(), u == null || u.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: l
        });
      }, 50);
      u = new window.MutationObserver(f), u.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", p(), (C = o.current) == null || C.appendChild(a);
    return () => {
      var d, f;
      a.style.display = "", (d = o.current) != null && d.contains(a) && ((f = o.current) == null || f.removeChild(a)), u == null || u.disconnect();
    };
  }, [t, b, r, s, n, l, g]), y.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...c);
});
function mt(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function _t(t, e = !1) {
  try {
    if (we(t))
      return t;
    if (e && !mt(t))
      return;
    if (typeof t == "string") {
      let r = t.trim();
      return r.startsWith(";") && (r = r.slice(1)), r.endsWith(";") && (r = r.slice(0, -1)), new Function(`return (...args) => (${r})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function T(t, e) {
  return A(() => _t(t, e), [t, e]);
}
function te(t, e) {
  const r = A(() => y.Children.toArray(t.originalChildren || t).filter((n) => n.props.node && !n.props.node.ignore && (!e && !n.props.nodeSlotKey || e && e === n.props.nodeSlotKey)).sort((n, o) => {
    if (n.props.node.slotIndex && o.props.node.slotIndex) {
      const c = k(n.props.node.slotIndex) || 0, i = k(o.props.node.slotIndex) || 0;
      return c - i === 0 && n.props.node.subSlotIndex && o.props.node.subSlotIndex ? (k(n.props.node.subSlotIndex) || 0) - (k(o.props.node.subSlotIndex) || 0) : c - i;
    }
    return 0;
  }).map((n) => n.props.node.target), [t, e]);
  return it(r);
}
const ht = ({
  children: t,
  ...e
}) => /* @__PURE__ */ x.jsx(x.Fragment, {
  children: t(e)
});
function de(t) {
  return y.createElement(ht, {
    children: t
  });
}
function fe(t, e, r) {
  const s = t.filter(Boolean);
  if (s.length !== 0)
    return s.map((l, n) => {
      var g, b;
      if (typeof l != "object")
        return e != null && e.fallback ? e.fallback(l) : l;
      const o = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...l.props,
        key: ((g = l.props) == null ? void 0 : g.key) ?? (r ? `${r}-${n}` : `${n}`)
      }) : {
        ...l.props,
        key: ((b = l.props) == null ? void 0 : b.key) ?? (r ? `${r}-${n}` : `${n}`)
      };
      let c = o;
      Object.keys(l.slots).forEach((a) => {
        if (!l.slots[a] || !(l.slots[a] instanceof Element) && !l.slots[a].el)
          return;
        const p = a.split(".");
        p.forEach((h, I) => {
          c[h] || (c[h] = {}), I !== p.length - 1 && (c = o[h]);
        });
        const u = l.slots[a];
        let w, C, d = (e == null ? void 0 : e.clone) ?? !1, f = e == null ? void 0 : e.forceClone;
        u instanceof Element ? w = u : (w = u.el, C = u.callback, d = u.clone ?? d, f = u.forceClone ?? f), f = f ?? !!C, c[p[p.length - 1]] = w ? C ? (...h) => (C(p[p.length - 1], h), /* @__PURE__ */ x.jsx(U, {
          ...l.ctx,
          params: h,
          forceClone: f,
          children: /* @__PURE__ */ x.jsx(R, {
            slot: w,
            clone: d
          })
        })) : de((h) => /* @__PURE__ */ x.jsx(U, {
          ...l.ctx,
          forceClone: f,
          children: /* @__PURE__ */ x.jsx(R, {
            ...h,
            slot: w,
            clone: d
          })
        })) : c[p[p.length - 1]], c = o;
      });
      const i = (e == null ? void 0 : e.children) || "children";
      return l[i] ? o[i] = fe(l[i], e, `${n}`) : e != null && e.children && (o[i] = void 0, Reflect.deleteProperty(o, i)), o;
    });
}
function ne(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? de((r) => /* @__PURE__ */ x.jsx(U, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ x.jsx(R, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...r
    })
  })) : /* @__PURE__ */ x.jsx(R, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function O({
  key: t,
  slots: e,
  targets: r
}, s) {
  return e[t] ? (...l) => r ? r.map((n, o) => /* @__PURE__ */ x.jsx(y.Fragment, {
    children: ne(n, {
      clone: !0,
      params: l,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }, o)) : /* @__PURE__ */ x.jsx(x.Fragment, {
    children: ne(e[t], {
      clone: !0,
      params: l,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }) : void 0;
}
const {
  useItems: pt,
  withItemsContextProvider: gt,
  ItemHandler: bt
} = Ie("antd-menu-items"), Ct = st(gt(["menu.items"], ({
  getPopupContainer: t,
  slots: e,
  children: r,
  dropdownRender: s,
  popupRender: l,
  buttonsRender: n,
  setSlotParams: o,
  value: c,
  ...i
}) => {
  var d, f, h;
  const g = T(t), b = T(s), a = T(n), p = T(l), u = te(r, "buttonsRender"), w = te(r), {
    items: {
      "menu.items": C
    }
  } = pt();
  return /* @__PURE__ */ x.jsxs(x.Fragment, {
    children: [/* @__PURE__ */ x.jsx("div", {
      style: {
        display: "none"
      },
      children: w.length > 0 ? null : r
    }), /* @__PURE__ */ x.jsx(Ce.Button, {
      ...i,
      buttonsRender: u.length ? O({
        key: "buttonsRender",
        slots: e,
        targets: u
      }) : a,
      menu: {
        ...i.menu,
        items: A(() => {
          var I;
          return ((I = i.menu) == null ? void 0 : I.items) || fe(C, {
            clone: !0
          }) || [];
        }, [C, (d = i.menu) == null ? void 0 : d.items]),
        expandIcon: e["menu.expandIcon"] ? O({
          slots: e,
          key: "menu.expandIcon"
        }, {}) : (f = i.menu) == null ? void 0 : f.expandIcon,
        overflowedIndicator: e["menu.overflowedIndicator"] ? /* @__PURE__ */ x.jsx(R, {
          slot: e["menu.overflowedIndicator"]
        }) : (h = i.menu) == null ? void 0 : h.overflowedIndicator
      },
      getPopupContainer: g,
      dropdownRender: e.dropdownRender ? O({
        slots: e,
        key: "dropdownRender"
      }) : b,
      popupRender: e.popupRender ? O({
        slots: e,
        key: "popupRender"
      }, {}) : p,
      icon: e.icon ? /* @__PURE__ */ x.jsx(R, {
        slot: e.icon
      }) : i.icon,
      children: w.length > 0 ? r : c
    })]
  });
}));
export {
  Ct as DropdownButton,
  Ct as default
};
