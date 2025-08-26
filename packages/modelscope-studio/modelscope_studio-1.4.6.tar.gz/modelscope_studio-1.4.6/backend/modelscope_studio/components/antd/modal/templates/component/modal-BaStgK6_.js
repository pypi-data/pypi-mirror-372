import { i as ue, a as W, r as de, Z as k, g as fe, b as me } from "./Index-Coqt6LvD.js";
const C = window.ms_globals.React, le = window.ms_globals.React.forwardRef, ie = window.ms_globals.React.useRef, se = window.ms_globals.React.useState, ce = window.ms_globals.React.useEffect, ae = window.ms_globals.React.useMemo, N = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, he = window.ms_globals.internalContext.ContextPropsProvider, ge = window.ms_globals.antd.Modal;
var pe = /\s/;
function xe(e) {
  for (var t = e.length; t-- && pe.test(e.charAt(t)); )
    ;
  return t;
}
var be = /^\s+/;
function we(e) {
  return e && e.slice(0, xe(e) + 1).replace(be, "");
}
var U = NaN, ye = /^[-+]0x[0-9a-f]+$/i, Ce = /^0b[01]+$/i, ve = /^0o[0-7]+$/i, Ee = parseInt;
function z(e) {
  if (typeof e == "number")
    return e;
  if (ue(e))
    return U;
  if (W(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = W(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = we(e);
  var o = Ce.test(e);
  return o || ve.test(e) ? Ee(e.slice(2), o ? 2 : 8) : ye.test(e) ? U : +e;
}
var L = function() {
  return de.Date.now();
}, Ie = "Expected a function", Se = Math.max, Pe = Math.min;
function Te(e, t, o) {
  var i, l, n, r, s, u, h = 0, p = !1, c = !1, x = !0;
  if (typeof e != "function")
    throw new TypeError(Ie);
  t = z(t) || 0, W(o) && (p = !!o.leading, c = "maxWait" in o, n = c ? Se(z(o.maxWait) || 0, t) : n, x = "trailing" in o ? !!o.trailing : x);
  function f(d) {
    var v = i, T = l;
    return i = l = void 0, h = d, r = e.apply(T, v), r;
  }
  function b(d) {
    return h = d, s = setTimeout(g, t), p ? f(d) : r;
  }
  function E(d) {
    var v = d - u, T = d - h, D = t - v;
    return c ? Pe(D, n - T) : D;
  }
  function m(d) {
    var v = d - u, T = d - h;
    return u === void 0 || v >= t || v < 0 || c && T >= n;
  }
  function g() {
    var d = L();
    if (m(d))
      return w(d);
    s = setTimeout(g, E(d));
  }
  function w(d) {
    return s = void 0, x && i ? f(d) : (i = l = void 0, r);
  }
  function P() {
    s !== void 0 && clearTimeout(s), h = 0, i = u = l = s = void 0;
  }
  function a() {
    return s === void 0 ? r : w(L());
  }
  function I() {
    var d = L(), v = m(d);
    if (i = arguments, l = this, u = d, v) {
      if (s === void 0)
        return b(u);
      if (c)
        return clearTimeout(s), s = setTimeout(g, t), f(u);
    }
    return s === void 0 && (s = setTimeout(g, t)), r;
  }
  return I.cancel = P, I.flush = a, I;
}
var $ = {
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
var Re = C, ke = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), je = Object.prototype.hasOwnProperty, Fe = Re.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Le = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ee(e, t, o) {
  var i, l = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (i in t) je.call(t, i) && !Le.hasOwnProperty(i) && (l[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) l[i] === void 0 && (l[i] = t[i]);
  return {
    $$typeof: ke,
    type: e,
    key: n,
    ref: r,
    props: l,
    _owner: Fe.current
  };
}
F.Fragment = Oe;
F.jsx = ee;
F.jsxs = ee;
$.exports = F;
var _ = $.exports;
const {
  SvelteComponent: Be,
  assign: G,
  binding_callbacks: H,
  check_outros: Ne,
  children: te,
  claim_element: ne,
  claim_space: We,
  component_subscribe: K,
  compute_slots: Ae,
  create_slot: Me,
  detach: S,
  element: re,
  empty: q,
  exclude_internal_props: V,
  get_all_dirty_from_scope: De,
  get_slot_changes: Ue,
  group_outros: ze,
  init: Ge,
  insert_hydration: O,
  safe_not_equal: He,
  set_custom_element_data: oe,
  space: Ke,
  transition_in: j,
  transition_out: A,
  update_slot_base: qe
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ve,
  getContext: Je,
  onDestroy: Xe,
  setContext: Ye
} = window.__gradio__svelte__internal;
function J(e) {
  let t, o;
  const i = (
    /*#slots*/
    e[7].default
  ), l = Me(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = re("svelte-slot"), l && l.c(), this.h();
    },
    l(n) {
      t = ne(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = te(t);
      l && l.l(r), r.forEach(S), this.h();
    },
    h() {
      oe(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      O(n, t, r), l && l.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      l && l.p && (!o || r & /*$$scope*/
      64) && qe(
        l,
        i,
        n,
        /*$$scope*/
        n[6],
        o ? Ue(
          i,
          /*$$scope*/
          n[6],
          r,
          null
        ) : De(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (j(l, n), o = !0);
    },
    o(n) {
      A(l, n), o = !1;
    },
    d(n) {
      n && S(t), l && l.d(n), e[9](null);
    }
  };
}
function Ze(e) {
  let t, o, i, l, n = (
    /*$$slots*/
    e[4].default && J(e)
  );
  return {
    c() {
      t = re("react-portal-target"), o = Ke(), n && n.c(), i = q(), this.h();
    },
    l(r) {
      t = ne(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), te(t).forEach(S), o = We(r), n && n.l(r), i = q(), this.h();
    },
    h() {
      oe(t, "class", "svelte-1rt0kpf");
    },
    m(r, s) {
      O(r, t, s), e[8](t), O(r, o, s), n && n.m(r, s), O(r, i, s), l = !0;
    },
    p(r, [s]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, s), s & /*$$slots*/
      16 && j(n, 1)) : (n = J(r), n.c(), j(n, 1), n.m(i.parentNode, i)) : n && (ze(), A(n, 1, 1, () => {
        n = null;
      }), Ne());
    },
    i(r) {
      l || (j(n), l = !0);
    },
    o(r) {
      A(n), l = !1;
    },
    d(r) {
      r && (S(t), S(o), S(i)), e[8](null), n && n.d(r);
    }
  };
}
function X(e) {
  const {
    svelteInit: t,
    ...o
  } = e;
  return o;
}
function Qe(e, t, o) {
  let i, l, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const s = Ae(n);
  let {
    svelteInit: u
  } = t;
  const h = k(X(t)), p = k();
  K(e, p, (a) => o(0, i = a));
  const c = k();
  K(e, c, (a) => o(1, l = a));
  const x = [], f = Je("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: E,
    subSlotIndex: m
  } = fe() || {}, g = u({
    parent: f,
    props: h,
    target: p,
    slot: c,
    slotKey: b,
    slotIndex: E,
    subSlotIndex: m,
    onDestroy(a) {
      x.push(a);
    }
  });
  Ye("$$ms-gr-react-wrapper", g), Ve(() => {
    h.set(X(t));
  }), Xe(() => {
    x.forEach((a) => a());
  });
  function w(a) {
    H[a ? "unshift" : "push"](() => {
      i = a, p.set(i);
    });
  }
  function P(a) {
    H[a ? "unshift" : "push"](() => {
      l = a, c.set(l);
    });
  }
  return e.$$set = (a) => {
    o(17, t = G(G({}, t), V(a))), "svelteInit" in a && o(5, u = a.svelteInit), "$$scope" in a && o(6, r = a.$$scope);
  }, t = V(t), [i, l, p, c, s, u, r, n, w, P];
}
class $e extends Be {
  constructor(t) {
    super(), Ge(this, t, Qe, Ze, He, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ut
} = window.__gradio__svelte__internal, Y = window.ms_globals.rerender, B = window.ms_globals.tree;
function et(e, t = {}) {
  function o(i) {
    const l = k(), n = new $e({
      ...i,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const s = {
            key: window.ms_globals.autokey,
            svelteInstance: l,
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
          return u.nodes = [...u.nodes, s], Y({
            createPortal: N,
            node: B
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((h) => h.svelteInstance !== l), Y({
              createPortal: N,
              node: B
            });
          }), s;
        },
        ...i.props
      }
    });
    return l.set(n), n;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise.then(() => {
      i(o);
    });
  });
}
const tt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function nt(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const i = e[o];
    return t[o] = rt(o, i), t;
  }, {}) : {};
}
function rt(e, t) {
  return typeof t == "number" && !tt.includes(e) ? t + "px" : t;
}
function M(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const l = C.Children.toArray(e._reactElement.props.children).map((n) => {
      if (C.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: s
        } = M(n.props.el);
        return C.cloneElement(n, {
          ...n.props,
          el: s,
          children: [...C.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return l.originalChildren = e._reactElement.props.children, t.push(N(C.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: l
    }), o)), {
      clonedElement: o,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((l) => {
    e.getEventListeners(l).forEach(({
      listener: r,
      type: s,
      useCapture: u
    }) => {
      o.addEventListener(s, r, u);
    });
  });
  const i = Array.from(e.childNodes);
  for (let l = 0; l < i.length; l++) {
    const n = i[l];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: s
      } = M(n);
      t.push(...s), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: t
  };
}
function ot(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const y = le(({
  slot: e,
  clone: t,
  className: o,
  style: i,
  observeAttributes: l
}, n) => {
  const r = ie(), [s, u] = se([]), {
    forceClone: h
  } = _e(), p = h ? !0 : t;
  return ce(() => {
    var E;
    if (!r.current || !e)
      return;
    let c = e;
    function x() {
      let m = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (m = c.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), ot(n, m), o && m.classList.add(...o.split(" ")), i) {
        const g = nt(i);
        Object.keys(g).forEach((w) => {
          m.style[w] = g[w];
        });
      }
    }
    let f = null, b = null;
    if (p && window.MutationObserver) {
      let m = function() {
        var a, I, d;
        (a = r.current) != null && a.contains(c) && ((I = r.current) == null || I.removeChild(c));
        const {
          portals: w,
          clonedElement: P
        } = M(e);
        c = P, u(w), c.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          x();
        }, 50), (d = r.current) == null || d.appendChild(c);
      };
      m();
      const g = Te(() => {
        m(), f == null || f.disconnect(), f == null || f.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: l
        });
      }, 50);
      f = new window.MutationObserver(g), f.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", x(), (E = r.current) == null || E.appendChild(c);
    return () => {
      var m, g;
      c.style.display = "", (m = r.current) != null && m.contains(c) && ((g = r.current) == null || g.removeChild(c)), f == null || f.disconnect();
    };
  }, [e, p, o, i, n, l, h]), C.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...s);
});
function lt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function it(e, t = !1) {
  try {
    if (me(e))
      return e;
    if (t && !lt(e))
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
function R(e, t) {
  return ae(() => it(e, t), [e, t]);
}
const st = ({
  children: e,
  ...t
}) => /* @__PURE__ */ _.jsx(_.Fragment, {
  children: e(t)
});
function ct(e) {
  return C.createElement(st, {
    children: e
  });
}
function Z(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ct((o) => /* @__PURE__ */ _.jsx(he, {
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
function Q({
  key: e,
  slots: t,
  targets: o
}, i) {
  return t[e] ? (...l) => o ? o.map((n, r) => /* @__PURE__ */ _.jsx(C.Fragment, {
    children: Z(n, {
      clone: !0,
      params: l,
      forceClone: !0
    })
  }, r)) : /* @__PURE__ */ _.jsx(_.Fragment, {
    children: Z(t[e], {
      clone: !0,
      params: l,
      forceClone: !0
    })
  }) : void 0;
}
const dt = et(({
  slots: e,
  afterClose: t,
  afterOpenChange: o,
  getContainer: i,
  children: l,
  modalRender: n,
  setSlotParams: r,
  ...s
}) => {
  var f, b;
  const u = R(o), h = R(t), p = R(i), c = R(n), x = R(s.footer, !0);
  return /* @__PURE__ */ _.jsx(ge, {
    ...s,
    afterOpenChange: u,
    afterClose: h,
    okText: e.okText ? /* @__PURE__ */ _.jsx(y, {
      slot: e.okText
    }) : s.okText,
    okButtonProps: {
      ...s.okButtonProps || {},
      icon: e["okButtonProps.icon"] ? /* @__PURE__ */ _.jsx(y, {
        slot: e["okButtonProps.icon"]
      }) : (f = s.okButtonProps) == null ? void 0 : f.icon
    },
    cancelText: e.cancelText ? /* @__PURE__ */ _.jsx(y, {
      slot: e.cancelText
    }) : s.cancelText,
    cancelButtonProps: {
      ...s.cancelButtonProps || {},
      icon: e["cancelButtonProps.icon"] ? /* @__PURE__ */ _.jsx(y, {
        slot: e["cancelButtonProps.icon"]
      }) : (b = s.cancelButtonProps) == null ? void 0 : b.icon
    },
    closable: e["closable.closeIcon"] ? {
      ...typeof s.closable == "object" ? s.closable : {},
      closeIcon: /* @__PURE__ */ _.jsx(y, {
        slot: e["closable.closeIcon"]
      })
    } : s.closable,
    closeIcon: e.closeIcon ? /* @__PURE__ */ _.jsx(y, {
      slot: e.closeIcon
    }) : s.closeIcon,
    footer: e.footer ? Q({
      slots: e,
      key: "footer"
    }) : x || (s.footer === "DEFAULT_FOOTER" ? void 0 : s.footer == null ? null : s.footer),
    title: e.title ? /* @__PURE__ */ _.jsx(y, {
      slot: e.title
    }) : s.title,
    modalRender: e.modalRender ? Q({
      slots: e,
      key: "modalRender"
    }) : c,
    getContainer: typeof i == "string" ? p : i,
    children: l
  });
});
export {
  dt as Modal,
  dt as default
};
