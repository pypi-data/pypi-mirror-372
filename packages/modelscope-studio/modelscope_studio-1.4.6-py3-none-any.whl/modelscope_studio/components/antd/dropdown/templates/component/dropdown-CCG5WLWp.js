import { i as me, a as D, r as _e, Z as k, g as he, b as ge } from "./Index-CRB2DReA.js";
const v = window.ms_globals.React, ae = window.ms_globals.React.forwardRef, ue = window.ms_globals.React.useRef, de = window.ms_globals.React.useState, fe = window.ms_globals.React.useEffect, ee = window.ms_globals.React.useMemo, A = window.ms_globals.ReactDOM.createPortal, pe = window.ms_globals.internalContext.useContextPropsContext, M = window.ms_globals.internalContext.ContextPropsProvider, we = window.ms_globals.antd.Dropdown, xe = window.ms_globals.createItemsContext.createItemsContext;
var be = /\s/;
function Ce(t) {
  for (var e = t.length; e-- && be.test(t.charAt(e)); )
    ;
  return e;
}
var ve = /^\s+/;
function ye(t) {
  return t && t.slice(0, Ce(t) + 1).replace(ve, "");
}
var z = NaN, Ee = /^[-+]0x[0-9a-f]+$/i, Ie = /^0b[01]+$/i, Re = /^0o[0-7]+$/i, Se = parseInt;
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
  t = ye(t);
  var o = Ie.test(t);
  return o || Re.test(t) ? Se(t.slice(2), o ? 2 : 8) : Ee.test(t) ? z : +t;
}
var F = function() {
  return _e.Date.now();
}, Pe = "Expected a function", ke = Math.max, Te = Math.min;
function Oe(t, e, o) {
  var s, l, n, r, c, a, g = 0, b = !1, i = !1, _ = !0;
  if (typeof t != "function")
    throw new TypeError(Pe);
  e = G(e) || 0, D(o) && (b = !!o.leading, i = "maxWait" in o, n = i ? ke(G(o.maxWait) || 0, e) : n, _ = "trailing" in o ? !!o.trailing : _);
  function u(m) {
    var y = s, S = l;
    return s = l = void 0, g = m, r = t.apply(S, y), r;
  }
  function x(m) {
    return g = m, c = setTimeout(h, e), b ? u(m) : r;
  }
  function C(m) {
    var y = m - a, S = m - g, H = e - y;
    return i ? Te(H, n - S) : H;
  }
  function d(m) {
    var y = m - a, S = m - g;
    return a === void 0 || y >= e || y < 0 || i && S >= n;
  }
  function h() {
    var m = F();
    if (d(m))
      return p(m);
    c = setTimeout(h, C(m));
  }
  function p(m) {
    return c = void 0, _ && s ? u(m) : (s = l = void 0, r);
  }
  function E() {
    c !== void 0 && clearTimeout(c), g = 0, s = a = l = c = void 0;
  }
  function f() {
    return c === void 0 ? r : p(F());
  }
  function I() {
    var m = F(), y = d(m);
    if (s = arguments, l = this, a = m, y) {
      if (c === void 0)
        return x(a);
      if (i)
        return clearTimeout(c), c = setTimeout(h, e), u(a);
    }
    return c === void 0 && (c = setTimeout(h, e)), r;
  }
  return I.cancel = E, I.flush = f, I;
}
var te = {
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
var je = v, Fe = Symbol.for("react.element"), Le = Symbol.for("react.fragment"), Ne = Object.prototype.hasOwnProperty, We = je.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ae = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ne(t, e, o) {
  var s, l = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (r = e.ref);
  for (s in e) Ne.call(e, s) && !Ae.hasOwnProperty(s) && (l[s] = e[s]);
  if (t && t.defaultProps) for (s in e = t.defaultProps, e) l[s] === void 0 && (l[s] = e[s]);
  return {
    $$typeof: Fe,
    type: t,
    key: n,
    ref: r,
    props: l,
    _owner: We.current
  };
}
j.Fragment = Le;
j.jsx = ne;
j.jsxs = ne;
te.exports = j;
var w = te.exports;
const {
  SvelteComponent: De,
  assign: q,
  binding_callbacks: V,
  check_outros: Me,
  children: re,
  claim_element: le,
  claim_space: Ue,
  component_subscribe: J,
  compute_slots: Be,
  create_slot: He,
  detach: R,
  element: oe,
  empty: X,
  exclude_internal_props: Y,
  get_all_dirty_from_scope: ze,
  get_slot_changes: Ge,
  group_outros: qe,
  init: Ve,
  insert_hydration: T,
  safe_not_equal: Je,
  set_custom_element_data: se,
  space: Xe,
  transition_in: O,
  transition_out: U,
  update_slot_base: Ye
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ze,
  getContext: Ke,
  onDestroy: Qe,
  setContext: $e
} = window.__gradio__svelte__internal;
function Z(t) {
  let e, o;
  const s = (
    /*#slots*/
    t[7].default
  ), l = He(
    s,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = oe("svelte-slot"), l && l.c(), this.h();
    },
    l(n) {
      e = le(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = re(e);
      l && l.l(r), r.forEach(R), this.h();
    },
    h() {
      se(e, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      T(n, e, r), l && l.m(e, null), t[9](e), o = !0;
    },
    p(n, r) {
      l && l.p && (!o || r & /*$$scope*/
      64) && Ye(
        l,
        s,
        n,
        /*$$scope*/
        n[6],
        o ? Ge(
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
      o || (O(l, n), o = !0);
    },
    o(n) {
      U(l, n), o = !1;
    },
    d(n) {
      n && R(e), l && l.d(n), t[9](null);
    }
  };
}
function et(t) {
  let e, o, s, l, n = (
    /*$$slots*/
    t[4].default && Z(t)
  );
  return {
    c() {
      e = oe("react-portal-target"), o = Xe(), n && n.c(), s = X(), this.h();
    },
    l(r) {
      e = le(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), re(e).forEach(R), o = Ue(r), n && n.l(r), s = X(), this.h();
    },
    h() {
      se(e, "class", "svelte-1rt0kpf");
    },
    m(r, c) {
      T(r, e, c), t[8](e), T(r, o, c), n && n.m(r, c), T(r, s, c), l = !0;
    },
    p(r, [c]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, c), c & /*$$slots*/
      16 && O(n, 1)) : (n = Z(r), n.c(), O(n, 1), n.m(s.parentNode, s)) : n && (qe(), U(n, 1, 1, () => {
        n = null;
      }), Me());
    },
    i(r) {
      l || (O(n), l = !0);
    },
    o(r) {
      U(n), l = !1;
    },
    d(r) {
      r && (R(e), R(o), R(s)), t[8](null), n && n.d(r);
    }
  };
}
function K(t) {
  const {
    svelteInit: e,
    ...o
  } = t;
  return o;
}
function tt(t, e, o) {
  let s, l, {
    $$slots: n = {},
    $$scope: r
  } = e;
  const c = Be(n);
  let {
    svelteInit: a
  } = e;
  const g = k(K(e)), b = k();
  J(t, b, (f) => o(0, s = f));
  const i = k();
  J(t, i, (f) => o(1, l = f));
  const _ = [], u = Ke("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: C,
    subSlotIndex: d
  } = he() || {}, h = a({
    parent: u,
    props: g,
    target: b,
    slot: i,
    slotKey: x,
    slotIndex: C,
    subSlotIndex: d,
    onDestroy(f) {
      _.push(f);
    }
  });
  $e("$$ms-gr-react-wrapper", h), Ze(() => {
    g.set(K(e));
  }), Qe(() => {
    _.forEach((f) => f());
  });
  function p(f) {
    V[f ? "unshift" : "push"](() => {
      s = f, b.set(s);
    });
  }
  function E(f) {
    V[f ? "unshift" : "push"](() => {
      l = f, i.set(l);
    });
  }
  return t.$$set = (f) => {
    o(17, e = q(q({}, e), Y(f))), "svelteInit" in f && o(5, a = f.svelteInit), "$$scope" in f && o(6, r = f.$$scope);
  }, e = Y(e), [s, l, b, i, c, a, r, n, p, E];
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
} = window.__gradio__svelte__internal, Q = window.ms_globals.rerender, L = window.ms_globals.tree;
function rt(t, e = {}) {
  function o(s) {
    const l = k(), n = new nt({
      ...s,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: l,
            reactComponent: t,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: e.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, a = r.parent ?? L;
          return a.nodes = [...a.nodes, c], Q({
            createPortal: A,
            node: L
          }), r.onDestroy(() => {
            a.nodes = a.nodes.filter((g) => g.svelteInstance !== l), Q({
              createPortal: A,
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
      s(o);
    });
  });
}
const lt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function ot(t) {
  return t ? Object.keys(t).reduce((e, o) => {
    const s = t[o];
    return e[o] = st(o, s), e;
  }, {}) : {};
}
function st(t, e) {
  return typeof e == "number" && !lt.includes(t) ? e + "px" : e;
}
function B(t) {
  const e = [], o = t.cloneNode(!1);
  if (t._reactElement) {
    const l = v.Children.toArray(t._reactElement.props.children).map((n) => {
      if (v.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: c
        } = B(n.props.el);
        return v.cloneElement(n, {
          ...n.props,
          el: c,
          children: [...v.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return l.originalChildren = t._reactElement.props.children, e.push(A(v.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: l
    }), o)), {
      clonedElement: o,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((l) => {
    t.getEventListeners(l).forEach(({
      listener: r,
      type: c,
      useCapture: a
    }) => {
      o.addEventListener(c, r, a);
    });
  });
  const s = Array.from(t.childNodes);
  for (let l = 0; l < s.length; l++) {
    const n = s[l];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: c
      } = B(n);
      e.push(...c), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: e
  };
}
function ct(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const P = ae(({
  slot: t,
  clone: e,
  className: o,
  style: s,
  observeAttributes: l
}, n) => {
  const r = ue(), [c, a] = de([]), {
    forceClone: g
  } = pe(), b = g ? !0 : e;
  return fe(() => {
    var C;
    if (!r.current || !t)
      return;
    let i = t;
    function _() {
      let d = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (d = i.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), ct(n, d), o && d.classList.add(...o.split(" ")), s) {
        const h = ot(s);
        Object.keys(h).forEach((p) => {
          d.style[p] = h[p];
        });
      }
    }
    let u = null, x = null;
    if (b && window.MutationObserver) {
      let d = function() {
        var f, I, m;
        (f = r.current) != null && f.contains(i) && ((I = r.current) == null || I.removeChild(i));
        const {
          portals: p,
          clonedElement: E
        } = B(t);
        i = E, a(p), i.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          _();
        }, 50), (m = r.current) == null || m.appendChild(i);
      };
      d();
      const h = Oe(() => {
        d(), u == null || u.disconnect(), u == null || u.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: l
        });
      }, 50);
      u = new window.MutationObserver(h), u.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", _(), (C = r.current) == null || C.appendChild(i);
    return () => {
      var d, h;
      i.style.display = "", (d = r.current) != null && d.contains(i) && ((h = r.current) == null || h.removeChild(i)), u == null || u.disconnect();
    };
  }, [t, b, o, s, n, l, g]), v.createElement("react-child", {
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
    if (ge(t))
      return t;
    if (e && !it(t))
      return;
    if (typeof t == "string") {
      let o = t.trim();
      return o.startsWith(";") && (o = o.slice(1)), o.endsWith(";") && (o = o.slice(0, -1)), new Function(`return (...args) => (${o})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function N(t, e) {
  return ee(() => at(t, e), [t, e]);
}
const ut = ({
  children: t,
  ...e
}) => /* @__PURE__ */ w.jsx(w.Fragment, {
  children: t(e)
});
function ce(t) {
  return v.createElement(ut, {
    children: t
  });
}
function ie(t, e, o) {
  const s = t.filter(Boolean);
  if (s.length !== 0)
    return s.map((l, n) => {
      var g, b;
      if (typeof l != "object")
        return e != null && e.fallback ? e.fallback(l) : l;
      const r = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...l.props,
        key: ((g = l.props) == null ? void 0 : g.key) ?? (o ? `${o}-${n}` : `${n}`)
      }) : {
        ...l.props,
        key: ((b = l.props) == null ? void 0 : b.key) ?? (o ? `${o}-${n}` : `${n}`)
      };
      let c = r;
      Object.keys(l.slots).forEach((i) => {
        if (!l.slots[i] || !(l.slots[i] instanceof Element) && !l.slots[i].el)
          return;
        const _ = i.split(".");
        _.forEach((p, E) => {
          c[p] || (c[p] = {}), E !== _.length - 1 && (c = r[p]);
        });
        const u = l.slots[i];
        let x, C, d = (e == null ? void 0 : e.clone) ?? !1, h = e == null ? void 0 : e.forceClone;
        u instanceof Element ? x = u : (x = u.el, C = u.callback, d = u.clone ?? d, h = u.forceClone ?? h), h = h ?? !!C, c[_[_.length - 1]] = x ? C ? (...p) => (C(_[_.length - 1], p), /* @__PURE__ */ w.jsx(M, {
          ...l.ctx,
          params: p,
          forceClone: h,
          children: /* @__PURE__ */ w.jsx(P, {
            slot: x,
            clone: d
          })
        })) : ce((p) => /* @__PURE__ */ w.jsx(M, {
          ...l.ctx,
          forceClone: h,
          children: /* @__PURE__ */ w.jsx(P, {
            ...p,
            slot: x,
            clone: d
          })
        })) : c[_[_.length - 1]], c = r;
      });
      const a = (e == null ? void 0 : e.children) || "children";
      return l[a] ? r[a] = ie(l[a], e, `${n}`) : e != null && e.children && (r[a] = void 0, Reflect.deleteProperty(r, a)), r;
    });
}
function $(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? ce((o) => /* @__PURE__ */ w.jsx(M, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ w.jsx(P, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...o
    })
  })) : /* @__PURE__ */ w.jsx(P, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function W({
  key: t,
  slots: e,
  targets: o
}, s) {
  return e[t] ? (...l) => o ? o.map((n, r) => /* @__PURE__ */ w.jsx(v.Fragment, {
    children: $(n, {
      clone: !0,
      params: l,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }, r)) : /* @__PURE__ */ w.jsx(w.Fragment, {
    children: $(e[t], {
      clone: !0,
      params: l,
      forceClone: (s == null ? void 0 : s.forceClone) ?? !0
    })
  }) : void 0;
}
const {
  useItems: dt,
  withItemsContextProvider: ft,
  ItemHandler: ht
} = xe("antd-menu-items"), gt = rt(ft(["menu.items"], ({
  getPopupContainer: t,
  innerStyle: e,
  children: o,
  slots: s,
  dropdownRender: l,
  popupRender: n,
  setSlotParams: r,
  ...c
}) => {
  var _, u, x;
  const a = N(t), g = N(l), b = N(n), {
    items: {
      "menu.items": i
    }
  } = dt();
  return /* @__PURE__ */ w.jsx(w.Fragment, {
    children: /* @__PURE__ */ w.jsx(we, {
      ...c,
      menu: {
        ...c.menu,
        items: ee(() => {
          var C;
          return ((C = c.menu) == null ? void 0 : C.items) || ie(i, {
            clone: !0
          }) || [];
        }, [i, (_ = c.menu) == null ? void 0 : _.items]),
        expandIcon: s["menu.expandIcon"] ? W({
          slots: s,
          key: "menu.expandIcon"
        }, {}) : (u = c.menu) == null ? void 0 : u.expandIcon,
        overflowedIndicator: s["menu.overflowedIndicator"] ? /* @__PURE__ */ w.jsx(P, {
          slot: s["menu.overflowedIndicator"]
        }) : (x = c.menu) == null ? void 0 : x.overflowedIndicator
      },
      getPopupContainer: a,
      dropdownRender: s.dropdownRender ? W({
        slots: s,
        key: "dropdownRender"
      }, {}) : g,
      popupRender: s.popupRender ? W({
        slots: s,
        key: "popupRender"
      }, {}) : b,
      children: /* @__PURE__ */ w.jsx("div", {
        className: "ms-gr-antd-dropdown-content",
        style: {
          display: "inline-block",
          ...e
        },
        children: o
      })
    })
  });
}));
export {
  gt as Dropdown,
  gt as default
};
