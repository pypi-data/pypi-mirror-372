import { i as ue, a as N, r as de, Z as k, g as fe, b as me } from "./Index-DfKZ7mS4.js";
const I = window.ms_globals.React, ce = window.ms_globals.React.forwardRef, $ = window.ms_globals.React.useRef, ie = window.ms_globals.React.useState, ee = window.ms_globals.React.useEffect, ae = window.ms_globals.React.useMemo, M = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, he = window.ms_globals.internalContext.ContextPropsProvider, ge = window.ms_globals.antd.Modal;
var pe = /\s/;
function xe(e) {
  for (var t = e.length; t-- && pe.test(e.charAt(t)); )
    ;
  return t;
}
var ye = /^\s+/;
function we(e) {
  return e && e.slice(0, xe(e) + 1).replace(ye, "");
}
var U = NaN, ve = /^[-+]0x[0-9a-f]+$/i, Ce = /^0b[01]+$/i, be = /^0o[0-7]+$/i, Ee = parseInt;
function H(e) {
  if (typeof e == "number")
    return e;
  if (ue(e))
    return U;
  if (N(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = N(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = we(e);
  var o = Ce.test(e);
  return o || be.test(e) ? Ee(e.slice(2), o ? 2 : 8) : ve.test(e) ? U : +e;
}
var L = function() {
  return de.Date.now();
}, Ie = "Expected a function", Se = Math.max, Pe = Math.min;
function Re(e, t, o) {
  var s, l, n, r, c, f, g = 0, x = !1, i = !1, u = !0;
  if (typeof e != "function")
    throw new TypeError(Ie);
  t = H(t) || 0, N(o) && (x = !!o.leading, i = "maxWait" in o, n = i ? Se(H(o.maxWait) || 0, t) : n, u = "trailing" in o ? !!o.trailing : u);
  function _(d) {
    var y = s, R = l;
    return s = l = void 0, g = d, r = e.apply(R, y), r;
  }
  function v(d) {
    return g = d, c = setTimeout(p, t), x ? _(d) : r;
  }
  function S(d) {
    var y = d - f, R = d - g, D = t - y;
    return i ? Pe(D, n - R) : D;
  }
  function m(d) {
    var y = d - f, R = d - g;
    return f === void 0 || y >= t || y < 0 || i && R >= n;
  }
  function p() {
    var d = L();
    if (m(d))
      return w(d);
    c = setTimeout(p, S(d));
  }
  function w(d) {
    return c = void 0, u && s ? _(d) : (s = l = void 0, r);
  }
  function C() {
    c !== void 0 && clearTimeout(c), g = 0, s = f = l = c = void 0;
  }
  function a() {
    return c === void 0 ? r : w(L());
  }
  function b() {
    var d = L(), y = m(d);
    if (s = arguments, l = this, f = d, y) {
      if (c === void 0)
        return v(f);
      if (i)
        return clearTimeout(c), c = setTimeout(p, t), _(f);
    }
    return c === void 0 && (c = setTimeout(p, t)), r;
  }
  return b.cancel = C, b.flush = a, b;
}
var te = {
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
var Te = I, ke = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), je = Object.prototype.hasOwnProperty, Fe = Te.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Le = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ne(e, t, o) {
  var s, l = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (s in t) je.call(t, s) && !Le.hasOwnProperty(s) && (l[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) l[s] === void 0 && (l[s] = t[s]);
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
F.jsx = ne;
F.jsxs = ne;
te.exports = F;
var h = te.exports;
const {
  SvelteComponent: Be,
  assign: z,
  binding_callbacks: G,
  check_outros: Me,
  children: re,
  claim_element: oe,
  claim_space: Ne,
  component_subscribe: K,
  compute_slots: We,
  create_slot: Ae,
  detach: P,
  element: le,
  empty: q,
  exclude_internal_props: J,
  get_all_dirty_from_scope: De,
  get_slot_changes: Ue,
  group_outros: He,
  init: ze,
  insert_hydration: O,
  safe_not_equal: Ge,
  set_custom_element_data: se,
  space: Ke,
  transition_in: j,
  transition_out: W,
  update_slot_base: qe
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Ze
} = window.__gradio__svelte__internal;
function X(e) {
  let t, o;
  const s = (
    /*#slots*/
    e[7].default
  ), l = Ae(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = le("svelte-slot"), l && l.c(), this.h();
    },
    l(n) {
      t = oe(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = re(t);
      l && l.l(r), r.forEach(P), this.h();
    },
    h() {
      se(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      O(n, t, r), l && l.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      l && l.p && (!o || r & /*$$scope*/
      64) && qe(
        l,
        s,
        n,
        /*$$scope*/
        n[6],
        o ? Ue(
          s,
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
      W(l, n), o = !1;
    },
    d(n) {
      n && P(t), l && l.d(n), e[9](null);
    }
  };
}
function Qe(e) {
  let t, o, s, l, n = (
    /*$$slots*/
    e[4].default && X(e)
  );
  return {
    c() {
      t = le("react-portal-target"), o = Ke(), n && n.c(), s = q(), this.h();
    },
    l(r) {
      t = oe(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), re(t).forEach(P), o = Ne(r), n && n.l(r), s = q(), this.h();
    },
    h() {
      se(t, "class", "svelte-1rt0kpf");
    },
    m(r, c) {
      O(r, t, c), e[8](t), O(r, o, c), n && n.m(r, c), O(r, s, c), l = !0;
    },
    p(r, [c]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, c), c & /*$$slots*/
      16 && j(n, 1)) : (n = X(r), n.c(), j(n, 1), n.m(s.parentNode, s)) : n && (He(), W(n, 1, 1, () => {
        n = null;
      }), Me());
    },
    i(r) {
      l || (j(n), l = !0);
    },
    o(r) {
      W(n), l = !1;
    },
    d(r) {
      r && (P(t), P(o), P(s)), e[8](null), n && n.d(r);
    }
  };
}
function Y(e) {
  const {
    svelteInit: t,
    ...o
  } = e;
  return o;
}
function Ve(e, t, o) {
  let s, l, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const c = We(n);
  let {
    svelteInit: f
  } = t;
  const g = k(Y(t)), x = k();
  K(e, x, (a) => o(0, s = a));
  const i = k();
  K(e, i, (a) => o(1, l = a));
  const u = [], _ = Xe("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: S,
    subSlotIndex: m
  } = fe() || {}, p = f({
    parent: _,
    props: g,
    target: x,
    slot: i,
    slotKey: v,
    slotIndex: S,
    subSlotIndex: m,
    onDestroy(a) {
      u.push(a);
    }
  });
  Ze("$$ms-gr-react-wrapper", p), Je(() => {
    g.set(Y(t));
  }), Ye(() => {
    u.forEach((a) => a());
  });
  function w(a) {
    G[a ? "unshift" : "push"](() => {
      s = a, x.set(s);
    });
  }
  function C(a) {
    G[a ? "unshift" : "push"](() => {
      l = a, i.set(l);
    });
  }
  return e.$$set = (a) => {
    o(17, t = z(z({}, t), J(a))), "svelteInit" in a && o(5, f = a.svelteInit), "$$scope" in a && o(6, r = a.$$scope);
  }, t = J(t), [s, l, x, i, c, f, r, n, w, C];
}
class $e extends Be {
  constructor(t) {
    super(), ze(this, t, Ve, Qe, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ut
} = window.__gradio__svelte__internal, Z = window.ms_globals.rerender, B = window.ms_globals.tree;
function et(e, t = {}) {
  function o(s) {
    const l = k(), n = new $e({
      ...s,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const c = {
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
          }, f = r.parent ?? B;
          return f.nodes = [...f.nodes, c], Z({
            createPortal: M,
            node: B
          }), r.onDestroy(() => {
            f.nodes = f.nodes.filter((g) => g.svelteInstance !== l), Z({
              createPortal: M,
              node: B
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
const tt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function nt(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const s = e[o];
    return t[o] = rt(o, s), t;
  }, {}) : {};
}
function rt(e, t) {
  return typeof t == "number" && !tt.includes(e) ? t + "px" : t;
}
function A(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const l = I.Children.toArray(e._reactElement.props.children).map((n) => {
      if (I.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: c
        } = A(n.props.el);
        return I.cloneElement(n, {
          ...n.props,
          el: c,
          children: [...I.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return l.originalChildren = e._reactElement.props.children, t.push(M(I.cloneElement(e._reactElement, {
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
      type: c,
      useCapture: f
    }) => {
      o.addEventListener(c, r, f);
    });
  });
  const s = Array.from(e.childNodes);
  for (let l = 0; l < s.length; l++) {
    const n = s[l];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: c
      } = A(n);
      t.push(...c), o.appendChild(r);
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
const E = ce(({
  slot: e,
  clone: t,
  className: o,
  style: s,
  observeAttributes: l
}, n) => {
  const r = $(), [c, f] = ie([]), {
    forceClone: g
  } = _e(), x = g ? !0 : t;
  return ee(() => {
    var S;
    if (!r.current || !e)
      return;
    let i = e;
    function u() {
      let m = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (m = i.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), ot(n, m), o && m.classList.add(...o.split(" ")), s) {
        const p = nt(s);
        Object.keys(p).forEach((w) => {
          m.style[w] = p[w];
        });
      }
    }
    let _ = null, v = null;
    if (x && window.MutationObserver) {
      let m = function() {
        var a, b, d;
        (a = r.current) != null && a.contains(i) && ((b = r.current) == null || b.removeChild(i));
        const {
          portals: w,
          clonedElement: C
        } = A(e);
        i = C, f(w), i.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          u();
        }, 50), (d = r.current) == null || d.appendChild(i);
      };
      m();
      const p = Re(() => {
        m(), _ == null || _.disconnect(), _ == null || _.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: l
        });
      }, 50);
      _ = new window.MutationObserver(p), _.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", u(), (S = r.current) == null || S.appendChild(i);
    return () => {
      var m, p;
      i.style.display = "", (m = r.current) != null && m.contains(i) && ((p = r.current) == null || p.removeChild(i)), _ == null || _.disconnect();
    };
  }, [e, x, o, s, n, l, g]), I.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...c);
});
function lt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function st(e, t = !1) {
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
function T(e, t) {
  return ae(() => st(e, t), [e, t]);
}
const ct = ({
  children: e,
  ...t
}) => /* @__PURE__ */ h.jsx(h.Fragment, {
  children: e(t)
});
function it(e) {
  return I.createElement(ct, {
    children: e
  });
}
function Q(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? it((o) => /* @__PURE__ */ h.jsx(he, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ h.jsx(E, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...o
    })
  })) : /* @__PURE__ */ h.jsx(E, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function V({
  key: e,
  slots: t,
  targets: o
}, s) {
  return t[e] ? (...l) => o ? o.map((n, r) => /* @__PURE__ */ h.jsx(I.Fragment, {
    children: Q(n, {
      clone: !0,
      params: l,
      forceClone: !0
    })
  }, r)) : /* @__PURE__ */ h.jsx(h.Fragment, {
    children: Q(t[e], {
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
  getContainer: s,
  children: l,
  modalRender: n,
  setSlotParams: r,
  onVisible: c,
  onCancel: f,
  onOk: g,
  visible: x,
  type: i,
  ...u
}) => {
  const _ = T(o), v = T(t), S = T(s), m = T(n), [p, w] = ge.useModal(), C = $(null);
  return ee(() => {
    var a, b, d;
    x ? C.current = p[i || "info"]({
      ...u,
      autoFocusButton: u.autoFocusButton === void 0 ? null : u.autoFocusButton,
      afterOpenChange: _,
      afterClose: v,
      getContainer: typeof s == "string" ? S : s,
      okText: e.okText ? /* @__PURE__ */ h.jsx(E, {
        slot: e.okText
      }) : u.okText,
      okButtonProps: {
        ...u.okButtonProps || {},
        icon: e["okButtonProps.icon"] ? /* @__PURE__ */ h.jsx(E, {
          slot: e["okButtonProps.icon"]
        }) : (a = u.okButtonProps) == null ? void 0 : a.icon
      },
      cancelText: e.cancelText ? /* @__PURE__ */ h.jsx(E, {
        slot: e.cancelText
      }) : u.cancelText,
      cancelButtonProps: {
        ...u.cancelButtonProps || {},
        icon: e["cancelButtonProps.icon"] ? /* @__PURE__ */ h.jsx(E, {
          slot: e["cancelButtonProps.icon"]
        }) : (b = u.cancelButtonProps) == null ? void 0 : b.icon
      },
      closable: e["closable.closeIcon"] ? {
        ...typeof u.closable == "object" ? u.closable : {},
        closeIcon: /* @__PURE__ */ h.jsx(E, {
          slot: e["closable.closeIcon"]
        })
      } : u.closable,
      closeIcon: e.closeIcon ? /* @__PURE__ */ h.jsx(E, {
        slot: e.closeIcon
      }) : u.closeIcon,
      footer: e.footer ? V({
        slots: e,
        key: "footer"
      }) : u.footer,
      title: e.title ? /* @__PURE__ */ h.jsx(E, {
        slot: e.title
      }) : u.title,
      modalRender: e.modalRender ? V({
        slots: e,
        key: "modalRender"
      }) : m,
      onCancel(...y) {
        f == null || f(...y), c == null || c(!1);
      },
      onOk(...y) {
        g == null || g(...y), c == null || c(!1);
      }
    }) : ((d = C.current) == null || d.destroy(), C.current = null);
  }, [x]), /* @__PURE__ */ h.jsxs(h.Fragment, {
    children: [/* @__PURE__ */ h.jsx("div", {
      style: {
        display: "none"
      },
      children: l
    }), w]
  });
});
export {
  dt as ModalStatic,
  dt as default
};
