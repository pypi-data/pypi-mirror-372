import { i as le, a as A, r as ce, Z as T, g as ae } from "./Index-BCHHQUxT.js";
const w = window.ms_globals.React, ne = window.ms_globals.React.forwardRef, re = window.ms_globals.React.useRef, oe = window.ms_globals.React.useState, se = window.ms_globals.React.useEffect, ie = window.ms_globals.React.useMemo, j = window.ms_globals.ReactDOM.createPortal, ue = window.ms_globals.internalContext.useContextPropsContext, de = window.ms_globals.internalContext.useIconFontContext, D = window.ms_globals.antdIcons;
var fe = /\s/;
function me(e) {
  for (var t = e.length; t-- && fe.test(e.charAt(t)); )
    ;
  return t;
}
var pe = /^\s+/;
function _e(e) {
  return e && e.slice(0, me(e) + 1).replace(pe, "");
}
var U = NaN, he = /^[-+]0x[0-9a-f]+$/i, ge = /^0b[01]+$/i, be = /^0o[0-7]+$/i, we = parseInt;
function z(e) {
  if (typeof e == "number")
    return e;
  if (le(e))
    return U;
  if (A(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = A(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = _e(e);
  var s = ge.test(e);
  return s || be.test(e) ? we(e.slice(2), s ? 2 : 8) : he.test(e) ? U : +e;
}
var L = function() {
  return ce.Date.now();
}, ye = "Expected a function", Ee = Math.max, Ce = Math.min;
function xe(e, t, s) {
  var i, o, n, r, l, d, _ = 0, h = !1, c = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(ye);
  t = z(t) || 0, A(s) && (h = !!s.leading, c = "maxWait" in s, n = c ? Ee(z(s.maxWait) || 0, t) : n, g = "trailing" in s ? !!s.trailing : g);
  function m(u) {
    var y = i, R = o;
    return i = o = void 0, _ = u, r = e.apply(R, y), r;
  }
  function E(u) {
    return _ = u, l = setTimeout(p, t), h ? m(u) : r;
  }
  function x(u) {
    var y = u - d, R = u - _, M = t - y;
    return c ? Ce(M, n - R) : M;
  }
  function f(u) {
    var y = u - d, R = u - _;
    return d === void 0 || y >= t || y < 0 || c && R >= n;
  }
  function p() {
    var u = L();
    if (f(u))
      return b(u);
    l = setTimeout(p, x(u));
  }
  function b(u) {
    return l = void 0, g && i ? m(u) : (i = o = void 0, r);
  }
  function S() {
    l !== void 0 && clearTimeout(l), _ = 0, i = d = o = l = void 0;
  }
  function a() {
    return l === void 0 ? r : b(L());
  }
  function v() {
    var u = L(), y = f(u);
    if (i = arguments, o = this, d = u, y) {
      if (l === void 0)
        return E(d);
      if (c)
        return clearTimeout(l), l = setTimeout(p, t), m(d);
    }
    return l === void 0 && (l = setTimeout(p, t)), r;
  }
  return v.cancel = S, v.flush = a, v;
}
var Y = {
  exports: {}
}, P = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var ve = w, Ie = Symbol.for("react.element"), Se = Symbol.for("react.fragment"), Re = Object.prototype.hasOwnProperty, Te = ve.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Oe = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Z(e, t, s) {
  var i, o = {}, n = null, r = null;
  s !== void 0 && (n = "" + s), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (i in t) Re.call(t, i) && !Oe.hasOwnProperty(i) && (o[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) o[i] === void 0 && (o[i] = t[i]);
  return {
    $$typeof: Ie,
    type: e,
    key: n,
    ref: r,
    props: o,
    _owner: Te.current
  };
}
P.Fragment = Se;
P.jsx = Z;
P.jsxs = Z;
Y.exports = P;
var C = Y.exports;
const {
  SvelteComponent: ke,
  assign: B,
  binding_callbacks: G,
  check_outros: Pe,
  children: Q,
  claim_element: $,
  claim_space: Le,
  component_subscribe: H,
  compute_slots: Ne,
  create_slot: je,
  detach: I,
  element: ee,
  empty: K,
  exclude_internal_props: q,
  get_all_dirty_from_scope: Ae,
  get_slot_changes: Fe,
  group_outros: We,
  init: Me,
  insert_hydration: O,
  safe_not_equal: De,
  set_custom_element_data: te,
  space: Ue,
  transition_in: k,
  transition_out: F,
  update_slot_base: ze
} = window.__gradio__svelte__internal, {
  beforeUpdate: Be,
  getContext: Ge,
  onDestroy: He,
  setContext: Ke
} = window.__gradio__svelte__internal;
function V(e) {
  let t, s;
  const i = (
    /*#slots*/
    e[7].default
  ), o = je(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ee("svelte-slot"), o && o.c(), this.h();
    },
    l(n) {
      t = $(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = Q(t);
      o && o.l(r), r.forEach(I), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      O(n, t, r), o && o.m(t, null), e[9](t), s = !0;
    },
    p(n, r) {
      o && o.p && (!s || r & /*$$scope*/
      64) && ze(
        o,
        i,
        n,
        /*$$scope*/
        n[6],
        s ? Fe(
          i,
          /*$$scope*/
          n[6],
          r,
          null
        ) : Ae(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      s || (k(o, n), s = !0);
    },
    o(n) {
      F(o, n), s = !1;
    },
    d(n) {
      n && I(t), o && o.d(n), e[9](null);
    }
  };
}
function qe(e) {
  let t, s, i, o, n = (
    /*$$slots*/
    e[4].default && V(e)
  );
  return {
    c() {
      t = ee("react-portal-target"), s = Ue(), n && n.c(), i = K(), this.h();
    },
    l(r) {
      t = $(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), Q(t).forEach(I), s = Le(r), n && n.l(r), i = K(), this.h();
    },
    h() {
      te(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      O(r, t, l), e[8](t), O(r, s, l), n && n.m(r, l), O(r, i, l), o = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && k(n, 1)) : (n = V(r), n.c(), k(n, 1), n.m(i.parentNode, i)) : n && (We(), F(n, 1, 1, () => {
        n = null;
      }), Pe());
    },
    i(r) {
      o || (k(n), o = !0);
    },
    o(r) {
      F(n), o = !1;
    },
    d(r) {
      r && (I(t), I(s), I(i)), e[8](null), n && n.d(r);
    }
  };
}
function J(e) {
  const {
    svelteInit: t,
    ...s
  } = e;
  return s;
}
function Ve(e, t, s) {
  let i, o, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Ne(n);
  let {
    svelteInit: d
  } = t;
  const _ = T(J(t)), h = T();
  H(e, h, (a) => s(0, i = a));
  const c = T();
  H(e, c, (a) => s(1, o = a));
  const g = [], m = Ge("$$ms-gr-react-wrapper"), {
    slotKey: E,
    slotIndex: x,
    subSlotIndex: f
  } = ae() || {}, p = d({
    parent: m,
    props: _,
    target: h,
    slot: c,
    slotKey: E,
    slotIndex: x,
    subSlotIndex: f,
    onDestroy(a) {
      g.push(a);
    }
  });
  Ke("$$ms-gr-react-wrapper", p), Be(() => {
    _.set(J(t));
  }), He(() => {
    g.forEach((a) => a());
  });
  function b(a) {
    G[a ? "unshift" : "push"](() => {
      i = a, h.set(i);
    });
  }
  function S(a) {
    G[a ? "unshift" : "push"](() => {
      o = a, c.set(o);
    });
  }
  return e.$$set = (a) => {
    s(17, t = B(B({}, t), q(a))), "svelteInit" in a && s(5, d = a.svelteInit), "$$scope" in a && s(6, r = a.$$scope);
  }, t = q(t), [i, o, h, c, l, d, r, n, b, S];
}
class Je extends ke {
  constructor(t) {
    super(), Me(this, t, Ve, qe, De, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: nt
} = window.__gradio__svelte__internal, X = window.ms_globals.rerender, N = window.ms_globals.tree;
function Xe(e, t = {}) {
  function s(i) {
    const o = T(), n = new Je({
      ...i,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: e,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: t.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, d = r.parent ?? N;
          return d.nodes = [...d.nodes, l], X({
            createPortal: j,
            node: N
          }), r.onDestroy(() => {
            d.nodes = d.nodes.filter((_) => _.svelteInstance !== o), X({
              createPortal: j,
              node: N
            });
          }), l;
        },
        ...i.props
      }
    });
    return o.set(n), n;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise.then(() => {
      i(s);
    });
  });
}
const Ye = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Ze(e) {
  return e ? Object.keys(e).reduce((t, s) => {
    const i = e[s];
    return t[s] = Qe(s, i), t;
  }, {}) : {};
}
function Qe(e, t) {
  return typeof t == "number" && !Ye.includes(e) ? t + "px" : t;
}
function W(e) {
  const t = [], s = e.cloneNode(!1);
  if (e._reactElement) {
    const o = w.Children.toArray(e._reactElement.props.children).map((n) => {
      if (w.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = W(n.props.el);
        return w.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...w.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(j(w.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), s)), {
      clonedElement: s,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: r,
      type: l,
      useCapture: d
    }) => {
      s.addEventListener(l, r, d);
    });
  });
  const i = Array.from(e.childNodes);
  for (let o = 0; o < i.length; o++) {
    const n = i[o];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = W(n);
      t.push(...l), s.appendChild(r);
    } else n.nodeType === 3 && s.appendChild(n.cloneNode());
  }
  return {
    clonedElement: s,
    portals: t
  };
}
function $e(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const et = ne(({
  slot: e,
  clone: t,
  className: s,
  style: i,
  observeAttributes: o
}, n) => {
  const r = re(), [l, d] = oe([]), {
    forceClone: _
  } = ue(), h = _ ? !0 : t;
  return se(() => {
    var x;
    if (!r.current || !e)
      return;
    let c = e;
    function g() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), $e(n, f), s && f.classList.add(...s.split(" ")), i) {
        const p = Ze(i);
        Object.keys(p).forEach((b) => {
          f.style[b] = p[b];
        });
      }
    }
    let m = null, E = null;
    if (h && window.MutationObserver) {
      let f = function() {
        var a, v, u;
        (a = r.current) != null && a.contains(c) && ((v = r.current) == null || v.removeChild(c));
        const {
          portals: b,
          clonedElement: S
        } = W(e);
        c = S, d(b), c.style.display = "contents", E && clearTimeout(E), E = setTimeout(() => {
          g();
        }, 50), (u = r.current) == null || u.appendChild(c);
      };
      f();
      const p = xe(() => {
        f(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      m = new window.MutationObserver(p), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", g(), (x = r.current) == null || x.appendChild(c);
    return () => {
      var f, p;
      c.style.display = "", (f = r.current) != null && f.contains(c) && ((p = r.current) == null || p.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, h, s, i, n, o, _]), w.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
}), rt = Xe(({
  value: e,
  slots: t,
  children: s,
  ...i
}) => {
  const o = de(), n = D[e], r = ie(() => () => t.component ? /* @__PURE__ */ C.jsx(et, {
    slot: t.component
  }) : null, [t.component]);
  return t.component ? /* @__PURE__ */ C.jsxs(C.Fragment, {
    children: [/* @__PURE__ */ C.jsx("div", {
      style: {
        display: "none"
      },
      children: s
    }), w.createElement(D.default, {
      ...i,
      component: r
    })]
  }) : /* @__PURE__ */ C.jsx(C.Fragment, {
    children: n ? w.createElement(n, i) : o ? /* @__PURE__ */ C.jsx(o, {
      type: e,
      ...i
    }) : null
  });
});
export {
  rt as Icon,
  rt as default
};
