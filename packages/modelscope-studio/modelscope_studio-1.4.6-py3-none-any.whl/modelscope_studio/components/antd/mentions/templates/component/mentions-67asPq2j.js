import { i as ue, a as A, r as de, b as fe, Z as P, g as me, c as _e } from "./Index-C8-ITQHo.js";
const v = window.ms_globals.React, ae = window.ms_globals.React.forwardRef, N = window.ms_globals.React.useRef, ee = window.ms_globals.React.useState, W = window.ms_globals.React.useEffect, te = window.ms_globals.React.useMemo, M = window.ms_globals.ReactDOM.createPortal, he = window.ms_globals.internalContext.useContextPropsContext, H = window.ms_globals.internalContext.ContextPropsProvider, pe = window.ms_globals.antd.Mentions, ge = window.ms_globals.createItemsContext.createItemsContext;
var be = /\s/;
function we(t) {
  for (var e = t.length; e-- && be.test(t.charAt(e)); )
    ;
  return e;
}
var xe = /^\s+/;
function Ce(t) {
  return t && t.slice(0, we(t) + 1).replace(xe, "");
}
var q = NaN, Ee = /^[-+]0x[0-9a-f]+$/i, ve = /^0b[01]+$/i, ye = /^0o[0-7]+$/i, Ie = parseInt;
function z(t) {
  if (typeof t == "number")
    return t;
  if (ue(t))
    return q;
  if (A(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = A(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = Ce(t);
  var o = ve.test(t);
  return o || ye.test(t) ? Ie(t.slice(2), o ? 2 : 8) : Ee.test(t) ? q : +t;
}
var j = function() {
  return de.Date.now();
}, Se = "Expected a function", Re = Math.max, Pe = Math.min;
function ke(t, e, o) {
  var l, r, n, s, i, a, h = 0, b = !1, c = !1, p = !0;
  if (typeof t != "function")
    throw new TypeError(Se);
  e = z(e) || 0, A(o) && (b = !!o.leading, c = "maxWait" in o, n = c ? Re(z(o.maxWait) || 0, e) : n, p = "trailing" in o ? !!o.trailing : p);
  function d(_) {
    var E = l, R = r;
    return l = r = void 0, h = _, s = t.apply(R, E), s;
  }
  function w(_) {
    return h = _, i = setTimeout(f, e), b ? d(_) : s;
  }
  function x(_) {
    var E = _ - a, R = _ - h, B = e - E;
    return c ? Pe(B, n - R) : B;
  }
  function u(_) {
    var E = _ - a, R = _ - h;
    return a === void 0 || E >= e || E < 0 || c && R >= n;
  }
  function f() {
    var _ = j();
    if (u(_))
      return g(_);
    i = setTimeout(f, x(_));
  }
  function g(_) {
    return i = void 0, p && l ? d(_) : (l = r = void 0, s);
  }
  function y() {
    i !== void 0 && clearTimeout(i), h = 0, l = a = r = i = void 0;
  }
  function m() {
    return i === void 0 ? s : g(j());
  }
  function I() {
    var _ = j(), E = u(_);
    if (l = arguments, r = this, a = _, E) {
      if (i === void 0)
        return w(a);
      if (c)
        return clearTimeout(i), i = setTimeout(f, e), d(a);
    }
    return i === void 0 && (i = setTimeout(f, e)), s;
  }
  return I.cancel = y, I.flush = m, I;
}
function Oe(t, e) {
  return fe(t, e);
}
var ne = {
  exports: {}
}, T = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Te = v, je = Symbol.for("react.element"), Fe = Symbol.for("react.fragment"), Le = Object.prototype.hasOwnProperty, Ne = Te.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, We = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function re(t, e, o) {
  var l, r = {}, n = null, s = null;
  o !== void 0 && (n = "" + o), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (s = e.ref);
  for (l in e) Le.call(e, l) && !We.hasOwnProperty(l) && (r[l] = e[l]);
  if (t && t.defaultProps) for (l in e = t.defaultProps, e) r[l] === void 0 && (r[l] = e[l]);
  return {
    $$typeof: je,
    type: t,
    key: n,
    ref: s,
    props: r,
    _owner: Ne.current
  };
}
T.Fragment = Fe;
T.jsx = re;
T.jsxs = re;
ne.exports = T;
var C = ne.exports;
const {
  SvelteComponent: Me,
  assign: G,
  binding_callbacks: J,
  check_outros: Ae,
  children: se,
  claim_element: oe,
  claim_space: De,
  component_subscribe: X,
  compute_slots: Ve,
  create_slot: Ue,
  detach: S,
  element: le,
  empty: Y,
  exclude_internal_props: Z,
  get_all_dirty_from_scope: Be,
  get_slot_changes: He,
  group_outros: qe,
  init: ze,
  insert_hydration: k,
  safe_not_equal: Ge,
  set_custom_element_data: ie,
  space: Je,
  transition_in: O,
  transition_out: D,
  update_slot_base: Xe
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ye,
  getContext: Ze,
  onDestroy: Ke,
  setContext: Qe
} = window.__gradio__svelte__internal;
function K(t) {
  let e, o;
  const l = (
    /*#slots*/
    t[7].default
  ), r = Ue(
    l,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = le("svelte-slot"), r && r.c(), this.h();
    },
    l(n) {
      e = oe(n, "SVELTE-SLOT", {
        class: !0
      });
      var s = se(e);
      r && r.l(s), s.forEach(S), this.h();
    },
    h() {
      ie(e, "class", "svelte-1rt0kpf");
    },
    m(n, s) {
      k(n, e, s), r && r.m(e, null), t[9](e), o = !0;
    },
    p(n, s) {
      r && r.p && (!o || s & /*$$scope*/
      64) && Xe(
        r,
        l,
        n,
        /*$$scope*/
        n[6],
        o ? He(
          l,
          /*$$scope*/
          n[6],
          s,
          null
        ) : Be(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (O(r, n), o = !0);
    },
    o(n) {
      D(r, n), o = !1;
    },
    d(n) {
      n && S(e), r && r.d(n), t[9](null);
    }
  };
}
function $e(t) {
  let e, o, l, r, n = (
    /*$$slots*/
    t[4].default && K(t)
  );
  return {
    c() {
      e = le("react-portal-target"), o = Je(), n && n.c(), l = Y(), this.h();
    },
    l(s) {
      e = oe(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), se(e).forEach(S), o = De(s), n && n.l(s), l = Y(), this.h();
    },
    h() {
      ie(e, "class", "svelte-1rt0kpf");
    },
    m(s, i) {
      k(s, e, i), t[8](e), k(s, o, i), n && n.m(s, i), k(s, l, i), r = !0;
    },
    p(s, [i]) {
      /*$$slots*/
      s[4].default ? n ? (n.p(s, i), i & /*$$slots*/
      16 && O(n, 1)) : (n = K(s), n.c(), O(n, 1), n.m(l.parentNode, l)) : n && (qe(), D(n, 1, 1, () => {
        n = null;
      }), Ae());
    },
    i(s) {
      r || (O(n), r = !0);
    },
    o(s) {
      D(n), r = !1;
    },
    d(s) {
      s && (S(e), S(o), S(l)), t[8](null), n && n.d(s);
    }
  };
}
function Q(t) {
  const {
    svelteInit: e,
    ...o
  } = t;
  return o;
}
function et(t, e, o) {
  let l, r, {
    $$slots: n = {},
    $$scope: s
  } = e;
  const i = Ve(n);
  let {
    svelteInit: a
  } = e;
  const h = P(Q(e)), b = P();
  X(t, b, (m) => o(0, l = m));
  const c = P();
  X(t, c, (m) => o(1, r = m));
  const p = [], d = Ze("$$ms-gr-react-wrapper"), {
    slotKey: w,
    slotIndex: x,
    subSlotIndex: u
  } = me() || {}, f = a({
    parent: d,
    props: h,
    target: b,
    slot: c,
    slotKey: w,
    slotIndex: x,
    subSlotIndex: u,
    onDestroy(m) {
      p.push(m);
    }
  });
  Qe("$$ms-gr-react-wrapper", f), Ye(() => {
    h.set(Q(e));
  }), Ke(() => {
    p.forEach((m) => m());
  });
  function g(m) {
    J[m ? "unshift" : "push"](() => {
      l = m, b.set(l);
    });
  }
  function y(m) {
    J[m ? "unshift" : "push"](() => {
      r = m, c.set(r);
    });
  }
  return t.$$set = (m) => {
    o(17, e = G(G({}, e), Z(m))), "svelteInit" in m && o(5, a = m.svelteInit), "$$scope" in m && o(6, s = m.$$scope);
  }, e = Z(e), [l, r, b, c, i, a, s, n, g, y];
}
class tt extends Me {
  constructor(e) {
    super(), ze(this, e, et, $e, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ht
} = window.__gradio__svelte__internal, $ = window.ms_globals.rerender, F = window.ms_globals.tree;
function nt(t, e = {}) {
  function o(l) {
    const r = P(), n = new tt({
      ...l,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const i = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: t,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: e.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, a = s.parent ?? F;
          return a.nodes = [...a.nodes, i], $({
            createPortal: M,
            node: F
          }), s.onDestroy(() => {
            a.nodes = a.nodes.filter((h) => h.svelteInstance !== r), $({
              createPortal: M,
              node: F
            });
          }), i;
        },
        ...l.props
      }
    });
    return r.set(n), n;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise.then(() => {
      l(o);
    });
  });
}
const rt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function st(t) {
  return t ? Object.keys(t).reduce((e, o) => {
    const l = t[o];
    return e[o] = ot(o, l), e;
  }, {}) : {};
}
function ot(t, e) {
  return typeof e == "number" && !rt.includes(t) ? e + "px" : e;
}
function V(t) {
  const e = [], o = t.cloneNode(!1);
  if (t._reactElement) {
    const r = v.Children.toArray(t._reactElement.props.children).map((n) => {
      if (v.isValidElement(n) && n.props.__slot__) {
        const {
          portals: s,
          clonedElement: i
        } = V(n.props.el);
        return v.cloneElement(n, {
          ...n.props,
          el: i,
          children: [...v.Children.toArray(n.props.children), ...s]
        });
      }
      return null;
    });
    return r.originalChildren = t._reactElement.props.children, e.push(M(v.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: r
    }), o)), {
      clonedElement: o,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((r) => {
    t.getEventListeners(r).forEach(({
      listener: s,
      type: i,
      useCapture: a
    }) => {
      o.addEventListener(i, s, a);
    });
  });
  const l = Array.from(t.childNodes);
  for (let r = 0; r < l.length; r++) {
    const n = l[r];
    if (n.nodeType === 1) {
      const {
        clonedElement: s,
        portals: i
      } = V(n);
      e.push(...i), o.appendChild(s);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: e
  };
}
function lt(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const U = ae(({
  slot: t,
  clone: e,
  className: o,
  style: l,
  observeAttributes: r
}, n) => {
  const s = N(), [i, a] = ee([]), {
    forceClone: h
  } = he(), b = h ? !0 : e;
  return W(() => {
    var x;
    if (!s.current || !t)
      return;
    let c = t;
    function p() {
      let u = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (u = c.children[0], u.tagName.toLowerCase() === "react-portal-target" && u.children[0] && (u = u.children[0])), lt(n, u), o && u.classList.add(...o.split(" ")), l) {
        const f = st(l);
        Object.keys(f).forEach((g) => {
          u.style[g] = f[g];
        });
      }
    }
    let d = null, w = null;
    if (b && window.MutationObserver) {
      let u = function() {
        var m, I, _;
        (m = s.current) != null && m.contains(c) && ((I = s.current) == null || I.removeChild(c));
        const {
          portals: g,
          clonedElement: y
        } = V(t);
        c = y, a(g), c.style.display = "contents", w && clearTimeout(w), w = setTimeout(() => {
          p();
        }, 50), (_ = s.current) == null || _.appendChild(c);
      };
      u();
      const f = ke(() => {
        u(), d == null || d.disconnect(), d == null || d.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      d = new window.MutationObserver(f), d.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", p(), (x = s.current) == null || x.appendChild(c);
    return () => {
      var u, f;
      c.style.display = "", (u = s.current) != null && u.contains(c) && ((f = s.current) == null || f.removeChild(c)), d == null || d.disconnect();
    };
  }, [t, b, o, l, n, r, h]), v.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...i);
});
function it(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function ct(t, e = !1) {
  try {
    if (_e(t))
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
function L(t, e) {
  return te(() => ct(t, e), [t, e]);
}
function at({
  value: t,
  onValueChange: e
}) {
  const [o, l] = ee(t), r = N(e);
  r.current = e;
  const n = N(o);
  return n.current = o, W(() => {
    r.current(o);
  }, [o]), W(() => {
    Oe(t, n.current) || l(t);
  }, [t]), [o, l];
}
const ut = ({
  children: t,
  ...e
}) => /* @__PURE__ */ C.jsx(C.Fragment, {
  children: t(e)
});
function dt(t) {
  return v.createElement(ut, {
    children: t
  });
}
function ce(t, e, o) {
  const l = t.filter(Boolean);
  if (l.length !== 0)
    return l.map((r, n) => {
      var h, b;
      if (typeof r != "object")
        return e != null && e.fallback ? e.fallback(r) : r;
      const s = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...r.props,
        key: ((h = r.props) == null ? void 0 : h.key) ?? (o ? `${o}-${n}` : `${n}`)
      }) : {
        ...r.props,
        key: ((b = r.props) == null ? void 0 : b.key) ?? (o ? `${o}-${n}` : `${n}`)
      };
      let i = s;
      Object.keys(r.slots).forEach((c) => {
        if (!r.slots[c] || !(r.slots[c] instanceof Element) && !r.slots[c].el)
          return;
        const p = c.split(".");
        p.forEach((g, y) => {
          i[g] || (i[g] = {}), y !== p.length - 1 && (i = s[g]);
        });
        const d = r.slots[c];
        let w, x, u = (e == null ? void 0 : e.clone) ?? !1, f = e == null ? void 0 : e.forceClone;
        d instanceof Element ? w = d : (w = d.el, x = d.callback, u = d.clone ?? u, f = d.forceClone ?? f), f = f ?? !!x, i[p[p.length - 1]] = w ? x ? (...g) => (x(p[p.length - 1], g), /* @__PURE__ */ C.jsx(H, {
          ...r.ctx,
          params: g,
          forceClone: f,
          children: /* @__PURE__ */ C.jsx(U, {
            slot: w,
            clone: u
          })
        })) : dt((g) => /* @__PURE__ */ C.jsx(H, {
          ...r.ctx,
          forceClone: f,
          children: /* @__PURE__ */ C.jsx(U, {
            ...g,
            slot: w,
            clone: u
          })
        })) : i[p[p.length - 1]], i = s;
      });
      const a = (e == null ? void 0 : e.children) || "children";
      return r[a] ? s[a] = ce(r[a], e, `${n}`) : e != null && e.children && (s[a] = void 0, Reflect.deleteProperty(s, a)), s;
    });
}
const {
  useItems: ft,
  withItemsContextProvider: mt,
  ItemHandler: pt
} = ge("antd-mentions-options"), gt = nt(mt(["options", "default"], ({
  slots: t,
  children: e,
  onValueChange: o,
  filterOption: l,
  onChange: r,
  options: n,
  validateSearch: s,
  getPopupContainer: i,
  elRef: a,
  ...h
}) => {
  const b = L(i), c = L(l), p = L(s), [d, w] = at({
    onValueChange: o,
    value: h.value
  }), {
    items: x
  } = ft(), u = x.options.length > 0 ? x.options : x.default;
  return /* @__PURE__ */ C.jsxs(C.Fragment, {
    children: [/* @__PURE__ */ C.jsx("div", {
      style: {
        display: "none"
      },
      children: e
    }), /* @__PURE__ */ C.jsx(pe, {
      ...h,
      ref: a,
      value: d,
      options: te(() => n || ce(u, {
        clone: !0
      }), [u, n]),
      onChange: (f, ...g) => {
        r == null || r(f, ...g), w(f);
      },
      validateSearch: p,
      notFoundContent: t.notFoundContent ? /* @__PURE__ */ C.jsx(U, {
        slot: t.notFoundContent
      }) : h.notFoundContent,
      filterOption: c || l,
      getPopupContainer: b
    })]
  });
}));
export {
  gt as Mentions,
  gt as default
};
