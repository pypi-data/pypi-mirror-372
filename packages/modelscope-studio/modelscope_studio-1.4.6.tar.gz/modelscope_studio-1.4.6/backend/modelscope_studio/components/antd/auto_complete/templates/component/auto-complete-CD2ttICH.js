import { i as me, a as D, r as he, b as _e, Z as j, g as ge, c as pe } from "./Index-HJboNRZp.js";
const v = window.ms_globals.React, re = window.ms_globals.React.forwardRef, W = window.ms_globals.React.useRef, le = window.ms_globals.React.useState, N = window.ms_globals.React.useEffect, H = window.ms_globals.React.useMemo, M = window.ms_globals.ReactDOM.createPortal, Ce = window.ms_globals.internalContext.useContextPropsContext, V = window.ms_globals.internalContext.ContextPropsProvider, we = window.ms_globals.internalContext.AutoCompleteContext, xe = window.ms_globals.antd.AutoComplete, be = window.ms_globals.createItemsContext.createItemsContext;
var ye = /\s/;
function ve(t) {
  for (var e = t.length; e-- && ye.test(t.charAt(e)); )
    ;
  return e;
}
var Ee = /^\s+/;
function Ie(t) {
  return t && t.slice(0, ve(t) + 1).replace(Ee, "");
}
var z = NaN, Re = /^[-+]0x[0-9a-f]+$/i, Se = /^0b[01]+$/i, Pe = /^0o[0-7]+$/i, ke = parseInt;
function G(t) {
  if (typeof t == "number")
    return t;
  if (me(t))
    return z;
  if (D(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = D(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Ie(t);
  var r = Se.test(t);
  return r || Pe.test(t) ? ke(t.slice(2), r ? 2 : 8) : Re.test(t) ? z : +t;
}
var A = function() {
  return he.Date.now();
}, je = "Expected a function", Oe = Math.max, Te = Math.min;
function Fe(t, e, r) {
  var s, l, n, o, c, a, C = 0, x = !1, i = !1, p = !0;
  if (typeof t != "function")
    throw new TypeError(je);
  e = G(e) || 0, D(r) && (x = !!r.leading, i = "maxWait" in r, n = i ? Oe(G(r.maxWait) || 0, e) : n, p = "trailing" in r ? !!r.trailing : p);
  function d(_) {
    var I = s, P = l;
    return s = l = void 0, C = _, o = t.apply(P, I), o;
  }
  function w(_) {
    return C = _, c = setTimeout(m, e), x ? d(_) : o;
  }
  function b(_) {
    var I = _ - a, P = _ - C, q = e - I;
    return i ? Te(q, n - P) : q;
  }
  function f(_) {
    var I = _ - a, P = _ - C;
    return a === void 0 || I >= e || I < 0 || i && P >= n;
  }
  function m() {
    var _ = A();
    if (f(_))
      return h(_);
    c = setTimeout(m, b(_));
  }
  function h(_) {
    return c = void 0, p && s ? d(_) : (s = l = void 0, o);
  }
  function y() {
    c !== void 0 && clearTimeout(c), C = 0, s = a = l = c = void 0;
  }
  function u() {
    return c === void 0 ? o : h(A());
  }
  function E() {
    var _ = A(), I = f(_);
    if (s = arguments, l = this, a = _, I) {
      if (c === void 0)
        return w(a);
      if (i)
        return clearTimeout(c), c = setTimeout(m, e), d(a);
    }
    return c === void 0 && (c = setTimeout(m, e)), o;
  }
  return E.cancel = y, E.flush = u, E;
}
function Ae(t, e) {
  return _e(t, e);
}
var oe = {
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
var Le = v, We = Symbol.for("react.element"), Ne = Symbol.for("react.fragment"), Me = Object.prototype.hasOwnProperty, De = Le.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ve = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function se(t, e, r) {
  var s, l = {}, n = null, o = null;
  r !== void 0 && (n = "" + r), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (o = e.ref);
  for (s in e) Me.call(e, s) && !Ve.hasOwnProperty(s) && (l[s] = e[s]);
  if (t && t.defaultProps) for (s in e = t.defaultProps, e) l[s] === void 0 && (l[s] = e[s]);
  return {
    $$typeof: We,
    type: t,
    key: n,
    ref: o,
    props: l,
    _owner: De.current
  };
}
F.Fragment = Ne;
F.jsx = se;
F.jsxs = se;
oe.exports = F;
var g = oe.exports;
const {
  SvelteComponent: Ue,
  assign: J,
  binding_callbacks: X,
  check_outros: Be,
  children: ce,
  claim_element: ie,
  claim_space: He,
  component_subscribe: Y,
  compute_slots: qe,
  create_slot: ze,
  detach: S,
  element: ae,
  empty: Z,
  exclude_internal_props: K,
  get_all_dirty_from_scope: Ge,
  get_slot_changes: Je,
  group_outros: Xe,
  init: Ye,
  insert_hydration: O,
  safe_not_equal: Ze,
  set_custom_element_data: ue,
  space: Ke,
  transition_in: T,
  transition_out: U,
  update_slot_base: Qe
} = window.__gradio__svelte__internal, {
  beforeUpdate: $e,
  getContext: et,
  onDestroy: tt,
  setContext: nt
} = window.__gradio__svelte__internal;
function Q(t) {
  let e, r;
  const s = (
    /*#slots*/
    t[7].default
  ), l = ze(
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
      O(n, e, o), l && l.m(e, null), t[9](e), r = !0;
    },
    p(n, o) {
      l && l.p && (!r || o & /*$$scope*/
      64) && Qe(
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
        ) : Ge(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      r || (T(l, n), r = !0);
    },
    o(n) {
      U(l, n), r = !1;
    },
    d(n) {
      n && S(e), l && l.d(n), t[9](null);
    }
  };
}
function rt(t) {
  let e, r, s, l, n = (
    /*$$slots*/
    t[4].default && Q(t)
  );
  return {
    c() {
      e = ae("react-portal-target"), r = Ke(), n && n.c(), s = Z(), this.h();
    },
    l(o) {
      e = ie(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), ce(e).forEach(S), r = He(o), n && n.l(o), s = Z(), this.h();
    },
    h() {
      ue(e, "class", "svelte-1rt0kpf");
    },
    m(o, c) {
      O(o, e, c), t[8](e), O(o, r, c), n && n.m(o, c), O(o, s, c), l = !0;
    },
    p(o, [c]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, c), c & /*$$slots*/
      16 && T(n, 1)) : (n = Q(o), n.c(), T(n, 1), n.m(s.parentNode, s)) : n && (Xe(), U(n, 1, 1, () => {
        n = null;
      }), Be());
    },
    i(o) {
      l || (T(n), l = !0);
    },
    o(o) {
      U(n), l = !1;
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
function lt(t, e, r) {
  let s, l, {
    $$slots: n = {},
    $$scope: o
  } = e;
  const c = qe(n);
  let {
    svelteInit: a
  } = e;
  const C = j($(e)), x = j();
  Y(t, x, (u) => r(0, s = u));
  const i = j();
  Y(t, i, (u) => r(1, l = u));
  const p = [], d = et("$$ms-gr-react-wrapper"), {
    slotKey: w,
    slotIndex: b,
    subSlotIndex: f
  } = ge() || {}, m = a({
    parent: d,
    props: C,
    target: x,
    slot: i,
    slotKey: w,
    slotIndex: b,
    subSlotIndex: f,
    onDestroy(u) {
      p.push(u);
    }
  });
  nt("$$ms-gr-react-wrapper", m), $e(() => {
    C.set($(e));
  }), tt(() => {
    p.forEach((u) => u());
  });
  function h(u) {
    X[u ? "unshift" : "push"](() => {
      s = u, x.set(s);
    });
  }
  function y(u) {
    X[u ? "unshift" : "push"](() => {
      l = u, i.set(l);
    });
  }
  return t.$$set = (u) => {
    r(17, e = J(J({}, e), K(u))), "svelteInit" in u && r(5, a = u.svelteInit), "$$scope" in u && r(6, o = u.$$scope);
  }, e = K(e), [s, l, x, i, c, a, o, n, h, y];
}
class ot extends Ue {
  constructor(e) {
    super(), Ye(this, e, lt, rt, Ze, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: wt
} = window.__gradio__svelte__internal, ee = window.ms_globals.rerender, L = window.ms_globals.tree;
function st(t, e = {}) {
  function r(s) {
    const l = j(), n = new ot({
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
          }, a = o.parent ?? L;
          return a.nodes = [...a.nodes, c], ee({
            createPortal: M,
            node: L
          }), o.onDestroy(() => {
            a.nodes = a.nodes.filter((C) => C.svelteInstance !== l), ee({
              createPortal: M,
              node: L
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
const ct = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function it(t) {
  return t ? Object.keys(t).reduce((e, r) => {
    const s = t[r];
    return e[r] = at(r, s), e;
  }, {}) : {};
}
function at(t, e) {
  return typeof e == "number" && !ct.includes(t) ? e + "px" : e;
}
function B(t) {
  const e = [], r = t.cloneNode(!1);
  if (t._reactElement) {
    const l = v.Children.toArray(t._reactElement.props.children).map((n) => {
      if (v.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: c
        } = B(n.props.el);
        return v.cloneElement(n, {
          ...n.props,
          el: c,
          children: [...v.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return l.originalChildren = t._reactElement.props.children, e.push(M(v.cloneElement(t._reactElement, {
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
      useCapture: a
    }) => {
      r.addEventListener(c, o, a);
    });
  });
  const s = Array.from(t.childNodes);
  for (let l = 0; l < s.length; l++) {
    const n = s[l];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: c
      } = B(n);
      e.push(...c), r.appendChild(o);
    } else n.nodeType === 3 && r.appendChild(n.cloneNode());
  }
  return {
    clonedElement: r,
    portals: e
  };
}
function ut(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const R = re(({
  slot: t,
  clone: e,
  className: r,
  style: s,
  observeAttributes: l
}, n) => {
  const o = W(), [c, a] = le([]), {
    forceClone: C
  } = Ce(), x = C ? !0 : e;
  return N(() => {
    var b;
    if (!o.current || !t)
      return;
    let i = t;
    function p() {
      let f = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (f = i.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), ut(n, f), r && f.classList.add(...r.split(" ")), s) {
        const m = it(s);
        Object.keys(m).forEach((h) => {
          f.style[h] = m[h];
        });
      }
    }
    let d = null, w = null;
    if (x && window.MutationObserver) {
      let f = function() {
        var u, E, _;
        (u = o.current) != null && u.contains(i) && ((E = o.current) == null || E.removeChild(i));
        const {
          portals: h,
          clonedElement: y
        } = B(t);
        i = y, a(h), i.style.display = "contents", w && clearTimeout(w), w = setTimeout(() => {
          p();
        }, 50), (_ = o.current) == null || _.appendChild(i);
      };
      f();
      const m = Fe(() => {
        f(), d == null || d.disconnect(), d == null || d.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: l
        });
      }, 50);
      d = new window.MutationObserver(m), d.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", p(), (b = o.current) == null || b.appendChild(i);
    return () => {
      var f, m;
      i.style.display = "", (f = o.current) != null && f.contains(i) && ((m = o.current) == null || m.removeChild(i)), d == null || d.disconnect();
    };
  }, [t, x, r, s, n, l, C]), v.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...c);
});
function dt(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function ft(t, e = !1) {
  try {
    if (pe(t))
      return t;
    if (e && !dt(t))
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
function k(t, e) {
  return H(() => ft(t, e), [t, e]);
}
function mt({
  value: t,
  onValueChange: e
}) {
  const [r, s] = le(t), l = W(e);
  l.current = e;
  const n = W(r);
  return n.current = r, N(() => {
    l.current(r);
  }, [r]), N(() => {
    Ae(t, n.current) || s(t);
  }, [t]), [r, s];
}
const ht = ({
  children: t,
  ...e
}) => /* @__PURE__ */ g.jsx(g.Fragment, {
  children: t(e)
});
function de(t) {
  return v.createElement(ht, {
    children: t
  });
}
function fe(t, e, r) {
  const s = t.filter(Boolean);
  if (s.length !== 0)
    return s.map((l, n) => {
      var C, x;
      if (typeof l != "object")
        return e != null && e.fallback ? e.fallback(l) : l;
      const o = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...l.props,
        key: ((C = l.props) == null ? void 0 : C.key) ?? (r ? `${r}-${n}` : `${n}`)
      }) : {
        ...l.props,
        key: ((x = l.props) == null ? void 0 : x.key) ?? (r ? `${r}-${n}` : `${n}`)
      };
      let c = o;
      Object.keys(l.slots).forEach((i) => {
        if (!l.slots[i] || !(l.slots[i] instanceof Element) && !l.slots[i].el)
          return;
        const p = i.split(".");
        p.forEach((h, y) => {
          c[h] || (c[h] = {}), y !== p.length - 1 && (c = o[h]);
        });
        const d = l.slots[i];
        let w, b, f = (e == null ? void 0 : e.clone) ?? !1, m = e == null ? void 0 : e.forceClone;
        d instanceof Element ? w = d : (w = d.el, b = d.callback, f = d.clone ?? f, m = d.forceClone ?? m), m = m ?? !!b, c[p[p.length - 1]] = w ? b ? (...h) => (b(p[p.length - 1], h), /* @__PURE__ */ g.jsx(V, {
          ...l.ctx,
          params: h,
          forceClone: m,
          children: /* @__PURE__ */ g.jsx(R, {
            slot: w,
            clone: f
          })
        })) : de((h) => /* @__PURE__ */ g.jsx(V, {
          ...l.ctx,
          forceClone: m,
          children: /* @__PURE__ */ g.jsx(R, {
            ...h,
            slot: w,
            clone: f
          })
        })) : c[p[p.length - 1]], c = o;
      });
      const a = (e == null ? void 0 : e.children) || "children";
      return l[a] ? o[a] = fe(l[a], e, `${n}`) : e != null && e.children && (o[a] = void 0, Reflect.deleteProperty(o, a)), o;
    });
}
function te(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? de((r) => /* @__PURE__ */ g.jsx(V, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ g.jsx(R, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...r
    })
  })) : /* @__PURE__ */ g.jsx(R, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function ne({
  key: t,
  slots: e,
  targets: r
}, s) {
  return e[t] ? (...l) => r ? r.map((n, o) => /* @__PURE__ */ g.jsx(v.Fragment, {
    children: te(n, {
      clone: !0,
      params: l,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }, o)) : /* @__PURE__ */ g.jsx(g.Fragment, {
    children: te(e[t], {
      clone: !0,
      params: l,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }) : void 0;
}
const {
  useItems: _t,
  withItemsContextProvider: gt,
  ItemHandler: xt
} = be("antd-auto-complete-options"), pt = re(({
  children: t,
  ...e
}, r) => /* @__PURE__ */ g.jsx(we.Provider, {
  value: H(() => ({
    ...e,
    elRef: r
  }), [e, r]),
  children: t
})), bt = st(gt(["options", "default"], ({
  slots: t,
  children: e,
  onValueChange: r,
  filterOption: s,
  onChange: l,
  options: n,
  getPopupContainer: o,
  dropdownRender: c,
  popupRender: a,
  elRef: C,
  setSlotParams: x,
  ...i
}) => {
  const p = k(o), d = k(s), w = k(c), b = k(a), [f, m] = mt({
    onValueChange: r,
    value: i.value
  }), {
    items: h
  } = _t(), y = h.options.length > 0 ? h.options : h.default;
  return /* @__PURE__ */ g.jsxs(g.Fragment, {
    children: [t.children ? null : /* @__PURE__ */ g.jsx("div", {
      style: {
        display: "none"
      },
      children: e
    }), /* @__PURE__ */ g.jsx(xe, {
      ...i,
      value: f,
      ref: C,
      allowClear: t["allowClear.clearIcon"] ? {
        clearIcon: /* @__PURE__ */ g.jsx(R, {
          slot: t["allowClear.clearIcon"]
        })
      } : i.allowClear,
      options: H(() => n || fe(y, {
        children: "options"
        // clone: true,
      }), [y, n]),
      onChange: (u, ...E) => {
        l == null || l(u, ...E), m(u);
      },
      notFoundContent: t.notFoundContent ? /* @__PURE__ */ g.jsx(R, {
        slot: t.notFoundContent
      }) : i.notFoundContent,
      filterOption: d || s,
      getPopupContainer: p,
      popupRender: t.popupRender ? ne({
        slots: t,
        key: "popupRender"
      }, {}) : b,
      dropdownRender: t.dropdownRender ? ne({
        slots: t,
        key: "dropdownRender"
      }, {}) : w,
      children: t.children ? /* @__PURE__ */ g.jsxs(pt, {
        children: [/* @__PURE__ */ g.jsx("div", {
          style: {
            display: "none"
          },
          children: e
        }), /* @__PURE__ */ g.jsx(R, {
          slot: t.children
        })]
      }) : null
    })]
  });
}));
export {
  bt as AutoComplete,
  bt as default
};
