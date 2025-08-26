import { i as ce, a as F, r as ae, Z as k, g as ue, b as de } from "./Index-cUJV5Ush.js";
const E = window.ms_globals.React, re = window.ms_globals.React.forwardRef, oe = window.ms_globals.React.useRef, ie = window.ms_globals.React.useState, se = window.ms_globals.React.useEffect, le = window.ms_globals.React.useMemo, N = window.ms_globals.ReactDOM.createPortal, fe = window.ms_globals.internalContext.useContextPropsContext, me = window.ms_globals.antd.Popconfirm;
var pe = /\s/;
function _e(e) {
  for (var t = e.length; t-- && pe.test(e.charAt(t)); )
    ;
  return t;
}
var he = /^\s+/;
function ge(e) {
  return e && e.slice(0, _e(e) + 1).replace(he, "");
}
var D = NaN, we = /^[-+]0x[0-9a-f]+$/i, xe = /^0b[01]+$/i, be = /^0o[0-7]+$/i, ye = parseInt;
function U(e) {
  if (typeof e == "number")
    return e;
  if (ce(e))
    return D;
  if (F(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = F(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = ge(e);
  var i = xe.test(e);
  return i || be.test(e) ? ye(e.slice(2), i ? 2 : 8) : we.test(e) ? D : +e;
}
var j = function() {
  return ae.Date.now();
}, Ee = "Expected a function", ve = Math.max, Ce = Math.min;
function Te(e, t, i) {
  var s, o, n, r, l, u, _ = 0, h = !1, c = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(Ee);
  t = U(t) || 0, F(i) && (h = !!i.leading, c = "maxWait" in i, n = c ? ve(U(i.maxWait) || 0, t) : n, g = "trailing" in i ? !!i.trailing : g);
  function m(d) {
    var x = s, S = o;
    return s = o = void 0, _ = d, r = e.apply(S, x), r;
  }
  function b(d) {
    return _ = d, l = setTimeout(p, t), h ? m(d) : r;
  }
  function v(d) {
    var x = d - u, S = d - _, M = t - x;
    return c ? Ce(M, n - S) : M;
  }
  function f(d) {
    var x = d - u, S = d - _;
    return u === void 0 || x >= t || x < 0 || c && S >= n;
  }
  function p() {
    var d = j();
    if (f(d))
      return w(d);
    l = setTimeout(p, v(d));
  }
  function w(d) {
    return l = void 0, g && s ? m(d) : (s = o = void 0, r);
  }
  function P() {
    l !== void 0 && clearTimeout(l), _ = 0, s = u = o = l = void 0;
  }
  function a() {
    return l === void 0 ? r : w(j());
  }
  function C() {
    var d = j(), x = f(d);
    if (s = arguments, o = this, u = d, x) {
      if (l === void 0)
        return b(u);
      if (c)
        return clearTimeout(l), l = setTimeout(p, t), m(u);
    }
    return l === void 0 && (l = setTimeout(p, t)), r;
  }
  return C.cancel = P, C.flush = a, C;
}
var Z = {
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
var Ie = E, Pe = Symbol.for("react.element"), Se = Symbol.for("react.fragment"), ke = Object.prototype.hasOwnProperty, Re = Ie.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Oe = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Q(e, t, i) {
  var s, o = {}, n = null, r = null;
  i !== void 0 && (n = "" + i), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (s in t) ke.call(t, s) && !Oe.hasOwnProperty(s) && (o[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) o[s] === void 0 && (o[s] = t[s]);
  return {
    $$typeof: Pe,
    type: e,
    key: n,
    ref: r,
    props: o,
    _owner: Re.current
  };
}
L.Fragment = Se;
L.jsx = Q;
L.jsxs = Q;
Z.exports = L;
var y = Z.exports;
const {
  SvelteComponent: Le,
  assign: z,
  binding_callbacks: G,
  check_outros: je,
  children: $,
  claim_element: ee,
  claim_space: Be,
  component_subscribe: H,
  compute_slots: Ne,
  create_slot: Fe,
  detach: I,
  element: te,
  empty: K,
  exclude_internal_props: q,
  get_all_dirty_from_scope: We,
  get_slot_changes: Ae,
  group_outros: Me,
  init: De,
  insert_hydration: R,
  safe_not_equal: Ue,
  set_custom_element_data: ne,
  space: ze,
  transition_in: O,
  transition_out: W,
  update_slot_base: Ge
} = window.__gradio__svelte__internal, {
  beforeUpdate: He,
  getContext: Ke,
  onDestroy: qe,
  setContext: Ve
} = window.__gradio__svelte__internal;
function V(e) {
  let t, i;
  const s = (
    /*#slots*/
    e[7].default
  ), o = Fe(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = te("svelte-slot"), o && o.c(), this.h();
    },
    l(n) {
      t = ee(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = $(t);
      o && o.l(r), r.forEach(I), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      R(n, t, r), o && o.m(t, null), e[9](t), i = !0;
    },
    p(n, r) {
      o && o.p && (!i || r & /*$$scope*/
      64) && Ge(
        o,
        s,
        n,
        /*$$scope*/
        n[6],
        i ? Ae(
          s,
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
      i || (O(o, n), i = !0);
    },
    o(n) {
      W(o, n), i = !1;
    },
    d(n) {
      n && I(t), o && o.d(n), e[9](null);
    }
  };
}
function Je(e) {
  let t, i, s, o, n = (
    /*$$slots*/
    e[4].default && V(e)
  );
  return {
    c() {
      t = te("react-portal-target"), i = ze(), n && n.c(), s = K(), this.h();
    },
    l(r) {
      t = ee(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), $(t).forEach(I), i = Be(r), n && n.l(r), s = K(), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      R(r, t, l), e[8](t), R(r, i, l), n && n.m(r, l), R(r, s, l), o = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && O(n, 1)) : (n = V(r), n.c(), O(n, 1), n.m(s.parentNode, s)) : n && (Me(), W(n, 1, 1, () => {
        n = null;
      }), je());
    },
    i(r) {
      o || (O(n), o = !0);
    },
    o(r) {
      W(n), o = !1;
    },
    d(r) {
      r && (I(t), I(i), I(s)), e[8](null), n && n.d(r);
    }
  };
}
function J(e) {
  const {
    svelteInit: t,
    ...i
  } = e;
  return i;
}
function Xe(e, t, i) {
  let s, o, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Ne(n);
  let {
    svelteInit: u
  } = t;
  const _ = k(J(t)), h = k();
  H(e, h, (a) => i(0, s = a));
  const c = k();
  H(e, c, (a) => i(1, o = a));
  const g = [], m = Ke("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: v,
    subSlotIndex: f
  } = ue() || {}, p = u({
    parent: m,
    props: _,
    target: h,
    slot: c,
    slotKey: b,
    slotIndex: v,
    subSlotIndex: f,
    onDestroy(a) {
      g.push(a);
    }
  });
  Ve("$$ms-gr-react-wrapper", p), He(() => {
    _.set(J(t));
  }), qe(() => {
    g.forEach((a) => a());
  });
  function w(a) {
    G[a ? "unshift" : "push"](() => {
      s = a, h.set(s);
    });
  }
  function P(a) {
    G[a ? "unshift" : "push"](() => {
      o = a, c.set(o);
    });
  }
  return e.$$set = (a) => {
    i(17, t = z(z({}, t), q(a))), "svelteInit" in a && i(5, u = a.svelteInit), "$$scope" in a && i(6, r = a.$$scope);
  }, t = q(t), [s, o, h, c, l, u, r, n, w, P];
}
class Ye extends Le {
  constructor(t) {
    super(), De(this, t, Xe, Je, Ue, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: it
} = window.__gradio__svelte__internal, X = window.ms_globals.rerender, B = window.ms_globals.tree;
function Ze(e, t = {}) {
  function i(s) {
    const o = k(), n = new Ye({
      ...s,
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
          }, u = r.parent ?? B;
          return u.nodes = [...u.nodes, l], X({
            createPortal: N,
            node: B
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((_) => _.svelteInstance !== o), X({
              createPortal: N,
              node: B
            });
          }), l;
        },
        ...s.props
      }
    });
    return o.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise.then(() => {
      s(i);
    });
  });
}
const Qe = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function $e(e) {
  return e ? Object.keys(e).reduce((t, i) => {
    const s = e[i];
    return t[i] = et(i, s), t;
  }, {}) : {};
}
function et(e, t) {
  return typeof t == "number" && !Qe.includes(e) ? t + "px" : t;
}
function A(e) {
  const t = [], i = e.cloneNode(!1);
  if (e._reactElement) {
    const o = E.Children.toArray(e._reactElement.props.children).map((n) => {
      if (E.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = A(n.props.el);
        return E.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...E.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(N(E.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), i)), {
      clonedElement: i,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: r,
      type: l,
      useCapture: u
    }) => {
      i.addEventListener(l, r, u);
    });
  });
  const s = Array.from(e.childNodes);
  for (let o = 0; o < s.length; o++) {
    const n = s[o];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = A(n);
      t.push(...l), i.appendChild(r);
    } else n.nodeType === 3 && i.appendChild(n.cloneNode());
  }
  return {
    clonedElement: i,
    portals: t
  };
}
function tt(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const T = re(({
  slot: e,
  clone: t,
  className: i,
  style: s,
  observeAttributes: o
}, n) => {
  const r = oe(), [l, u] = ie([]), {
    forceClone: _
  } = fe(), h = _ ? !0 : t;
  return se(() => {
    var v;
    if (!r.current || !e)
      return;
    let c = e;
    function g() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), tt(n, f), i && f.classList.add(...i.split(" ")), s) {
        const p = $e(s);
        Object.keys(p).forEach((w) => {
          f.style[w] = p[w];
        });
      }
    }
    let m = null, b = null;
    if (h && window.MutationObserver) {
      let f = function() {
        var a, C, d;
        (a = r.current) != null && a.contains(c) && ((C = r.current) == null || C.removeChild(c));
        const {
          portals: w,
          clonedElement: P
        } = A(e);
        c = P, u(w), c.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          g();
        }, 50), (d = r.current) == null || d.appendChild(c);
      };
      f();
      const p = Te(() => {
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
      c.style.display = "contents", g(), (v = r.current) == null || v.appendChild(c);
    return () => {
      var f, p;
      c.style.display = "", (f = r.current) != null && f.contains(c) && ((p = r.current) == null || p.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, h, i, s, n, o, _]), E.createElement("react-child", {
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
      let i = e.trim();
      return i.startsWith(";") && (i = i.slice(1)), i.endsWith(";") && (i = i.slice(0, -1)), new Function(`return (...args) => (${i})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function Y(e, t) {
  return le(() => rt(e, t), [e, t]);
}
const st = Ze(({
  slots: e,
  afterOpenChange: t,
  getPopupContainer: i,
  children: s,
  ...o
}) => {
  var l, u;
  const n = Y(t), r = Y(i);
  return /* @__PURE__ */ y.jsx(me, {
    ...o,
    afterOpenChange: n,
    getPopupContainer: r,
    okText: e.okText ? /* @__PURE__ */ y.jsx(T, {
      slot: e.okText
    }) : o.okText,
    okButtonProps: {
      ...o.okButtonProps || {},
      icon: e["okButtonProps.icon"] ? /* @__PURE__ */ y.jsx(T, {
        slot: e["okButtonProps.icon"]
      }) : (l = o.okButtonProps) == null ? void 0 : l.icon
    },
    cancelText: e.cancelText ? /* @__PURE__ */ y.jsx(T, {
      slot: e.cancelText
    }) : o.cancelText,
    cancelButtonProps: {
      ...o.cancelButtonProps || {},
      icon: e["cancelButtonProps.icon"] ? /* @__PURE__ */ y.jsx(T, {
        slot: e["cancelButtonProps.icon"]
      }) : (u = o.cancelButtonProps) == null ? void 0 : u.icon
    },
    title: e.title ? /* @__PURE__ */ y.jsx(T, {
      slot: e.title
    }) : o.title,
    description: e.description ? /* @__PURE__ */ y.jsx(T, {
      slot: e.description
    }) : o.description,
    children: s
  });
});
export {
  st as Popconfirm,
  st as default
};
