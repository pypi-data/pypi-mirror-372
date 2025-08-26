import { i as ce, a as A, r as ae, Z as T, g as ue, b as de } from "./Index-BZKwlLrC.js";
const E = window.ms_globals.React, re = window.ms_globals.React.forwardRef, oe = window.ms_globals.React.useRef, ie = window.ms_globals.React.useState, se = window.ms_globals.React.useEffect, le = window.ms_globals.React.useMemo, N = window.ms_globals.ReactDOM.createPortal, fe = window.ms_globals.internalContext.useContextPropsContext, pe = window.ms_globals.antd.FloatButton;
var me = /\s/;
function _e(e) {
  for (var t = e.length; t-- && me.test(e.charAt(t)); )
    ;
  return t;
}
var ge = /^\s+/;
function he(e) {
  return e && e.slice(0, _e(e) + 1).replace(ge, "");
}
var D = NaN, be = /^[-+]0x[0-9a-f]+$/i, ye = /^0b[01]+$/i, we = /^0o[0-7]+$/i, Ce = parseInt;
function U(e) {
  if (typeof e == "number")
    return e;
  if (ce(e))
    return D;
  if (A(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = A(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = he(e);
  var o = ye.test(e);
  return o || we.test(e) ? Ce(e.slice(2), o ? 2 : 8) : be.test(e) ? D : +e;
}
var L = function() {
  return ae.Date.now();
}, Ee = "Expected a function", xe = Math.max, ve = Math.min;
function Ie(e, t, o) {
  var i, s, n, r, l, u, _ = 0, g = !1, c = !1, h = !0;
  if (typeof e != "function")
    throw new TypeError(Ee);
  t = U(t) || 0, A(o) && (g = !!o.leading, c = "maxWait" in o, n = c ? xe(U(o.maxWait) || 0, t) : n, h = "trailing" in o ? !!o.trailing : h);
  function p(d) {
    var w = i, R = s;
    return i = s = void 0, _ = d, r = e.apply(R, w), r;
  }
  function C(d) {
    return _ = d, l = setTimeout(m, t), g ? p(d) : r;
  }
  function x(d) {
    var w = d - u, R = d - _, B = t - w;
    return c ? ve(B, n - R) : B;
  }
  function f(d) {
    var w = d - u, R = d - _;
    return u === void 0 || w >= t || w < 0 || c && R >= n;
  }
  function m() {
    var d = L();
    if (f(d))
      return b(d);
    l = setTimeout(m, x(d));
  }
  function b(d) {
    return l = void 0, h && i ? p(d) : (i = s = void 0, r);
  }
  function S() {
    l !== void 0 && clearTimeout(l), _ = 0, i = u = s = l = void 0;
  }
  function a() {
    return l === void 0 ? r : b(L());
  }
  function v() {
    var d = L(), w = f(d);
    if (i = arguments, s = this, u = d, w) {
      if (l === void 0)
        return C(u);
      if (c)
        return clearTimeout(l), l = setTimeout(m, t), p(u);
    }
    return l === void 0 && (l = setTimeout(m, t)), r;
  }
  return v.cancel = S, v.flush = a, v;
}
var Z = {
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
var Se = E, Re = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), Te = Object.prototype.hasOwnProperty, ke = Se.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Pe = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Q(e, t, o) {
  var i, s = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (i in t) Te.call(t, i) && !Pe.hasOwnProperty(i) && (s[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) s[i] === void 0 && (s[i] = t[i]);
  return {
    $$typeof: Re,
    type: e,
    key: n,
    ref: r,
    props: s,
    _owner: ke.current
  };
}
j.Fragment = Oe;
j.jsx = Q;
j.jsxs = Q;
Z.exports = j;
var y = Z.exports;
const {
  SvelteComponent: je,
  assign: G,
  binding_callbacks: z,
  check_outros: Le,
  children: $,
  claim_element: ee,
  claim_space: Fe,
  component_subscribe: H,
  compute_slots: Ne,
  create_slot: Ae,
  detach: I,
  element: te,
  empty: K,
  exclude_internal_props: q,
  get_all_dirty_from_scope: We,
  get_slot_changes: Me,
  group_outros: Be,
  init: De,
  insert_hydration: k,
  safe_not_equal: Ue,
  set_custom_element_data: ne,
  space: Ge,
  transition_in: P,
  transition_out: W,
  update_slot_base: ze
} = window.__gradio__svelte__internal, {
  beforeUpdate: He,
  getContext: Ke,
  onDestroy: qe,
  setContext: Ve
} = window.__gradio__svelte__internal;
function V(e) {
  let t, o;
  const i = (
    /*#slots*/
    e[7].default
  ), s = Ae(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = te("svelte-slot"), s && s.c(), this.h();
    },
    l(n) {
      t = ee(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = $(t);
      s && s.l(r), r.forEach(I), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      k(n, t, r), s && s.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      s && s.p && (!o || r & /*$$scope*/
      64) && ze(
        s,
        i,
        n,
        /*$$scope*/
        n[6],
        o ? Me(
          i,
          /*$$scope*/
          n[6],
          r,
          null
        ) : We(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (P(s, n), o = !0);
    },
    o(n) {
      W(s, n), o = !1;
    },
    d(n) {
      n && I(t), s && s.d(n), e[9](null);
    }
  };
}
function Je(e) {
  let t, o, i, s, n = (
    /*$$slots*/
    e[4].default && V(e)
  );
  return {
    c() {
      t = te("react-portal-target"), o = Ge(), n && n.c(), i = K(), this.h();
    },
    l(r) {
      t = ee(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), $(t).forEach(I), o = Fe(r), n && n.l(r), i = K(), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      k(r, t, l), e[8](t), k(r, o, l), n && n.m(r, l), k(r, i, l), s = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && P(n, 1)) : (n = V(r), n.c(), P(n, 1), n.m(i.parentNode, i)) : n && (Be(), W(n, 1, 1, () => {
        n = null;
      }), Le());
    },
    i(r) {
      s || (P(n), s = !0);
    },
    o(r) {
      W(n), s = !1;
    },
    d(r) {
      r && (I(t), I(o), I(i)), e[8](null), n && n.d(r);
    }
  };
}
function J(e) {
  const {
    svelteInit: t,
    ...o
  } = e;
  return o;
}
function Xe(e, t, o) {
  let i, s, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Ne(n);
  let {
    svelteInit: u
  } = t;
  const _ = T(J(t)), g = T();
  H(e, g, (a) => o(0, i = a));
  const c = T();
  H(e, c, (a) => o(1, s = a));
  const h = [], p = Ke("$$ms-gr-react-wrapper"), {
    slotKey: C,
    slotIndex: x,
    subSlotIndex: f
  } = ue() || {}, m = u({
    parent: p,
    props: _,
    target: g,
    slot: c,
    slotKey: C,
    slotIndex: x,
    subSlotIndex: f,
    onDestroy(a) {
      h.push(a);
    }
  });
  Ve("$$ms-gr-react-wrapper", m), He(() => {
    _.set(J(t));
  }), qe(() => {
    h.forEach((a) => a());
  });
  function b(a) {
    z[a ? "unshift" : "push"](() => {
      i = a, g.set(i);
    });
  }
  function S(a) {
    z[a ? "unshift" : "push"](() => {
      s = a, c.set(s);
    });
  }
  return e.$$set = (a) => {
    o(17, t = G(G({}, t), q(a))), "svelteInit" in a && o(5, u = a.svelteInit), "$$scope" in a && o(6, r = a.$$scope);
  }, t = q(t), [i, s, g, c, l, u, r, n, b, S];
}
class Ye extends je {
  constructor(t) {
    super(), De(this, t, Xe, Je, Ue, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: st
} = window.__gradio__svelte__internal, X = window.ms_globals.rerender, F = window.ms_globals.tree;
function Ze(e, t = {}) {
  function o(i) {
    const s = T(), n = new Ye({
      ...i,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: e,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: t.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, u = r.parent ?? F;
          return u.nodes = [...u.nodes, l], X({
            createPortal: N,
            node: F
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((_) => _.svelteInstance !== s), X({
              createPortal: N,
              node: F
            });
          }), l;
        },
        ...i.props
      }
    });
    return s.set(n), n;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise.then(() => {
      i(o);
    });
  });
}
const Qe = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function $e(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const i = e[o];
    return t[o] = et(o, i), t;
  }, {}) : {};
}
function et(e, t) {
  return typeof t == "number" && !Qe.includes(e) ? t + "px" : t;
}
function M(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const s = E.Children.toArray(e._reactElement.props.children).map((n) => {
      if (E.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = M(n.props.el);
        return E.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...E.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return s.originalChildren = e._reactElement.props.children, t.push(N(E.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: s
    }), o)), {
      clonedElement: o,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((s) => {
    e.getEventListeners(s).forEach(({
      listener: r,
      type: l,
      useCapture: u
    }) => {
      o.addEventListener(l, r, u);
    });
  });
  const i = Array.from(e.childNodes);
  for (let s = 0; s < i.length; s++) {
    const n = i[s];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = M(n);
      t.push(...l), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: t
  };
}
function tt(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const O = re(({
  slot: e,
  clone: t,
  className: o,
  style: i,
  observeAttributes: s
}, n) => {
  const r = oe(), [l, u] = ie([]), {
    forceClone: _
  } = fe(), g = _ ? !0 : t;
  return se(() => {
    var x;
    if (!r.current || !e)
      return;
    let c = e;
    function h() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), tt(n, f), o && f.classList.add(...o.split(" ")), i) {
        const m = $e(i);
        Object.keys(m).forEach((b) => {
          f.style[b] = m[b];
        });
      }
    }
    let p = null, C = null;
    if (g && window.MutationObserver) {
      let f = function() {
        var a, v, d;
        (a = r.current) != null && a.contains(c) && ((v = r.current) == null || v.removeChild(c));
        const {
          portals: b,
          clonedElement: S
        } = M(e);
        c = S, u(b), c.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          h();
        }, 50), (d = r.current) == null || d.appendChild(c);
      };
      f();
      const m = Ie(() => {
        f(), p == null || p.disconnect(), p == null || p.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: s
        });
      }, 50);
      p = new window.MutationObserver(m), p.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", h(), (x = r.current) == null || x.appendChild(c);
    return () => {
      var f, m;
      c.style.display = "", (f = r.current) != null && f.contains(c) && ((m = r.current) == null || m.removeChild(c)), p == null || p.disconnect();
    };
  }, [e, g, o, i, n, s, _]), E.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
});
function nt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function rt(e, t = !1) {
  try {
    if (de(e))
      return e;
    if (t && !nt(e))
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
function Y(e, t) {
  return le(() => rt(e, t), [e, t]);
}
function ot(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const lt = Ze(({
  slots: e,
  children: t,
  tooltip: o,
  ...i
}) => {
  var u;
  const s = e["tooltip.title"] || typeof o == "object", n = ot(o), r = Y(n.afterOpenChange), l = Y(n.getPopupContainer);
  return /* @__PURE__ */ y.jsxs(y.Fragment, {
    children: [/* @__PURE__ */ y.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ y.jsx(pe, {
      ...i,
      icon: e.icon ? /* @__PURE__ */ y.jsx(O, {
        clone: !0,
        slot: e.icon
      }) : i.icon,
      description: e.description ? /* @__PURE__ */ y.jsx(O, {
        clone: !0,
        slot: e.description
      }) : i.description,
      tooltip: e.tooltip ? /* @__PURE__ */ y.jsx(O, {
        slot: e.tooltip
      }) : s ? {
        ...n,
        afterOpenChange: r,
        getPopupContainer: l,
        title: e["tooltip.title"] ? /* @__PURE__ */ y.jsx(O, {
          slot: e["tooltip.title"]
        }) : n.title
      } : o,
      badge: {
        ...i.badge,
        count: e["badge.count"] ? /* @__PURE__ */ y.jsx(O, {
          slot: e["badge.count"]
        }) : (u = i.badge) == null ? void 0 : u.count
      }
    })]
  });
});
export {
  lt as FloatButton,
  lt as default
};
