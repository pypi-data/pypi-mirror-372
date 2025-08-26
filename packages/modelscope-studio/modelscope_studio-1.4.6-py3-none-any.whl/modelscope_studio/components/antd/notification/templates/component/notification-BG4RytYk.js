import { i as se, a as W, r as le, Z as O, g as ce } from "./Index-CqE_VSEK.js";
const x = window.ms_globals.React, re = window.ms_globals.React.forwardRef, oe = window.ms_globals.React.useRef, ie = window.ms_globals.React.useState, K = window.ms_globals.React.useEffect, A = window.ms_globals.ReactDOM.createPortal, ae = window.ms_globals.internalContext.useContextPropsContext, ue = window.ms_globals.antd.notification;
var de = /\s/;
function fe(e) {
  for (var t = e.length; t-- && de.test(e.charAt(t)); )
    ;
  return t;
}
var me = /^\s+/;
function _e(e) {
  return e && e.slice(0, fe(e) + 1).replace(me, "");
}
var H = NaN, he = /^[-+]0x[0-9a-f]+$/i, ge = /^0b[01]+$/i, pe = /^0o[0-7]+$/i, be = parseInt;
function U(e) {
  if (typeof e == "number")
    return e;
  if (se(e))
    return H;
  if (W(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = W(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = _e(e);
  var i = ge.test(e);
  return i || pe.test(e) ? be(e.slice(2), i ? 2 : 8) : he.test(e) ? H : +e;
}
var N = function() {
  return le.Date.now();
}, ye = "Expected a function", we = Math.max, Ee = Math.min;
function xe(e, t, i) {
  var s, o, n, r, l, u, h = 0, c = !1, a = !1, p = !0;
  if (typeof e != "function")
    throw new TypeError(ye);
  t = U(t) || 0, W(i) && (c = !!i.leading, a = "maxWait" in i, n = a ? we(U(i.maxWait) || 0, t) : n, p = "trailing" in i ? !!i.trailing : p);
  function m(f) {
    var y = s, R = o;
    return s = o = void 0, h = f, r = e.apply(R, y), r;
  }
  function E(f) {
    return h = f, l = setTimeout(g, t), c ? m(f) : r;
  }
  function v(f) {
    var y = f - u, R = f - h, M = t - y;
    return a ? Ee(M, n - R) : M;
  }
  function _(f) {
    var y = f - u, R = f - h;
    return u === void 0 || y >= t || y < 0 || a && R >= n;
  }
  function g() {
    var f = N();
    if (_(f))
      return b(f);
    l = setTimeout(g, v(f));
  }
  function b(f) {
    return l = void 0, p && s ? m(f) : (s = o = void 0, r);
  }
  function T() {
    l !== void 0 && clearTimeout(l), h = 0, s = u = o = l = void 0;
  }
  function d() {
    return l === void 0 ? r : b(N());
  }
  function C() {
    var f = N(), y = _(f);
    if (s = arguments, o = this, u = f, y) {
      if (l === void 0)
        return E(u);
      if (a)
        return clearTimeout(l), l = setTimeout(g, t), m(u);
    }
    return l === void 0 && (l = setTimeout(g, t)), r;
  }
  return C.cancel = T, C.flush = d, C;
}
var Q = {
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
var ve = x, Ce = Symbol.for("react.element"), Ie = Symbol.for("react.fragment"), Se = Object.prototype.hasOwnProperty, Te = ve.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Re = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function V(e, t, i) {
  var s, o = {}, n = null, r = null;
  i !== void 0 && (n = "" + i), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (s in t) Se.call(t, s) && !Re.hasOwnProperty(s) && (o[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) o[s] === void 0 && (o[s] = t[s]);
  return {
    $$typeof: Ce,
    type: e,
    key: n,
    ref: r,
    props: o,
    _owner: Te.current
  };
}
L.Fragment = Ie;
L.jsx = V;
L.jsxs = V;
Q.exports = L;
var w = Q.exports;
const {
  SvelteComponent: Oe,
  assign: z,
  binding_callbacks: B,
  check_outros: ke,
  children: $,
  claim_element: ee,
  claim_space: Pe,
  component_subscribe: G,
  compute_slots: Le,
  create_slot: Ne,
  detach: S,
  element: te,
  empty: q,
  exclude_internal_props: J,
  get_all_dirty_from_scope: je,
  get_slot_changes: Ae,
  group_outros: We,
  init: De,
  insert_hydration: k,
  safe_not_equal: Fe,
  set_custom_element_data: ne,
  space: Me,
  transition_in: P,
  transition_out: D,
  update_slot_base: He
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ue,
  getContext: ze,
  onDestroy: Be,
  setContext: Ge
} = window.__gradio__svelte__internal;
function X(e) {
  let t, i;
  const s = (
    /*#slots*/
    e[7].default
  ), o = Ne(
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
      o && o.l(r), r.forEach(S), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      k(n, t, r), o && o.m(t, null), e[9](t), i = !0;
    },
    p(n, r) {
      o && o.p && (!i || r & /*$$scope*/
      64) && He(
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
        ) : je(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      i || (P(o, n), i = !0);
    },
    o(n) {
      D(o, n), i = !1;
    },
    d(n) {
      n && S(t), o && o.d(n), e[9](null);
    }
  };
}
function qe(e) {
  let t, i, s, o, n = (
    /*$$slots*/
    e[4].default && X(e)
  );
  return {
    c() {
      t = te("react-portal-target"), i = Me(), n && n.c(), s = q(), this.h();
    },
    l(r) {
      t = ee(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), $(t).forEach(S), i = Pe(r), n && n.l(r), s = q(), this.h();
    },
    h() {
      ne(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      k(r, t, l), e[8](t), k(r, i, l), n && n.m(r, l), k(r, s, l), o = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && P(n, 1)) : (n = X(r), n.c(), P(n, 1), n.m(s.parentNode, s)) : n && (We(), D(n, 1, 1, () => {
        n = null;
      }), ke());
    },
    i(r) {
      o || (P(n), o = !0);
    },
    o(r) {
      D(n), o = !1;
    },
    d(r) {
      r && (S(t), S(i), S(s)), e[8](null), n && n.d(r);
    }
  };
}
function Y(e) {
  const {
    svelteInit: t,
    ...i
  } = e;
  return i;
}
function Je(e, t, i) {
  let s, o, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Le(n);
  let {
    svelteInit: u
  } = t;
  const h = O(Y(t)), c = O();
  G(e, c, (d) => i(0, s = d));
  const a = O();
  G(e, a, (d) => i(1, o = d));
  const p = [], m = ze("$$ms-gr-react-wrapper"), {
    slotKey: E,
    slotIndex: v,
    subSlotIndex: _
  } = ce() || {}, g = u({
    parent: m,
    props: h,
    target: c,
    slot: a,
    slotKey: E,
    slotIndex: v,
    subSlotIndex: _,
    onDestroy(d) {
      p.push(d);
    }
  });
  Ge("$$ms-gr-react-wrapper", g), Ue(() => {
    h.set(Y(t));
  }), Be(() => {
    p.forEach((d) => d());
  });
  function b(d) {
    B[d ? "unshift" : "push"](() => {
      s = d, c.set(s);
    });
  }
  function T(d) {
    B[d ? "unshift" : "push"](() => {
      o = d, a.set(o);
    });
  }
  return e.$$set = (d) => {
    i(17, t = z(z({}, t), J(d))), "svelteInit" in d && i(5, u = d.svelteInit), "$$scope" in d && i(6, r = d.$$scope);
  }, t = J(t), [s, o, c, a, l, u, r, n, b, T];
}
class Xe extends Oe {
  constructor(t) {
    super(), De(this, t, Je, qe, Fe, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: et
} = window.__gradio__svelte__internal, Z = window.ms_globals.rerender, j = window.ms_globals.tree;
function Ye(e, t = {}) {
  function i(s) {
    const o = O(), n = new Xe({
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
          }, u = r.parent ?? j;
          return u.nodes = [...u.nodes, l], Z({
            createPortal: A,
            node: j
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((h) => h.svelteInstance !== o), Z({
              createPortal: A,
              node: j
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
const Ze = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Ke(e) {
  return e ? Object.keys(e).reduce((t, i) => {
    const s = e[i];
    return t[i] = Qe(i, s), t;
  }, {}) : {};
}
function Qe(e, t) {
  return typeof t == "number" && !Ze.includes(e) ? t + "px" : t;
}
function F(e) {
  const t = [], i = e.cloneNode(!1);
  if (e._reactElement) {
    const o = x.Children.toArray(e._reactElement.props.children).map((n) => {
      if (x.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = F(n.props.el);
        return x.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...x.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(A(x.cloneElement(e._reactElement, {
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
      } = F(n);
      t.push(...l), i.appendChild(r);
    } else n.nodeType === 3 && i.appendChild(n.cloneNode());
  }
  return {
    clonedElement: i,
    portals: t
  };
}
function Ve(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const I = re(({
  slot: e,
  clone: t,
  className: i,
  style: s,
  observeAttributes: o
}, n) => {
  const r = oe(), [l, u] = ie([]), {
    forceClone: h
  } = ae(), c = h ? !0 : t;
  return K(() => {
    var v;
    if (!r.current || !e)
      return;
    let a = e;
    function p() {
      let _ = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (_ = a.children[0], _.tagName.toLowerCase() === "react-portal-target" && _.children[0] && (_ = _.children[0])), Ve(n, _), i && _.classList.add(...i.split(" ")), s) {
        const g = Ke(s);
        Object.keys(g).forEach((b) => {
          _.style[b] = g[b];
        });
      }
    }
    let m = null, E = null;
    if (c && window.MutationObserver) {
      let _ = function() {
        var d, C, f;
        (d = r.current) != null && d.contains(a) && ((C = r.current) == null || C.removeChild(a));
        const {
          portals: b,
          clonedElement: T
        } = F(e);
        a = T, u(b), a.style.display = "contents", E && clearTimeout(E), E = setTimeout(() => {
          p();
        }, 50), (f = r.current) == null || f.appendChild(a);
      };
      _();
      const g = xe(() => {
        _(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      m = new window.MutationObserver(g), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", p(), (v = r.current) == null || v.appendChild(a);
    return () => {
      var _, g;
      a.style.display = "", (_ = r.current) != null && _.contains(a) && ((g = r.current) == null || g.removeChild(a)), m == null || m.disconnect();
    };
  }, [e, c, i, s, n, o, h]), x.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
}), tt = Ye(({
  slots: e,
  bottom: t,
  rtl: i,
  stack: s,
  top: o,
  children: n,
  visible: r,
  notificationKey: l,
  onClose: u,
  onVisible: h,
  ...c
}) => {
  const [a, p] = ue.useNotification({
    bottom: t,
    rtl: i,
    stack: s,
    top: o
  });
  return K(() => (r ? a.open({
    ...c,
    key: l,
    btn: e.btn ? /* @__PURE__ */ w.jsx(I, {
      slot: e.btn
    }) : c.btn,
    actions: e.actions ? /* @__PURE__ */ w.jsx(I, {
      slot: e.actions
    }) : c.actions,
    closeIcon: e.closeIcon ? /* @__PURE__ */ w.jsx(I, {
      slot: e.closeIcon
    }) : c.closeIcon,
    description: e.description ? /* @__PURE__ */ w.jsx(I, {
      slot: e.description
    }) : c.description,
    message: e.message ? /* @__PURE__ */ w.jsx(I, {
      slot: e.message
    }) : c.message,
    icon: e.icon ? /* @__PURE__ */ w.jsx(I, {
      slot: e.icon
    }) : c.icon,
    onClose(...m) {
      h == null || h(!1), u == null || u(...m);
    }
  }) : a.destroy(l), () => {
    a.destroy(l);
  }), [r, l, c.btn, c.actions, c.closeIcon, c.className, c.description, c.duration, c.showProgress, c.pauseOnHover, c.icon, c.message, c.placement, c.style, c.role, c.props]), /* @__PURE__ */ w.jsxs(w.Fragment, {
    children: [n, p]
  });
});
export {
  tt as Notification,
  tt as default
};
