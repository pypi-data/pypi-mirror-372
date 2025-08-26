import { i as ae, a as A, r as ue, b as de, Z as P, g as fe, c as me } from "./Index-DtKkHIQ0.js";
const y = window.ms_globals.React, ie = window.ms_globals.React.useMemo, ee = window.ms_globals.React.useState, F = window.ms_globals.React.useRef, N = window.ms_globals.React.useEffect, ce = window.ms_globals.React.forwardRef, W = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, pe = window.ms_globals.internalContext.ContextPropsProvider, he = window.ms_globals.antd.Input;
var ge = /\s/;
function we(e) {
  for (var t = e.length; t-- && ge.test(e.charAt(t)); )
    ;
  return t;
}
var be = /^\s+/;
function ye(e) {
  return e && e.slice(0, we(e) + 1).replace(be, "");
}
var U = NaN, Ee = /^[-+]0x[0-9a-f]+$/i, xe = /^0b[01]+$/i, ve = /^0o[0-7]+$/i, Ce = parseInt;
function q(e) {
  if (typeof e == "number")
    return e;
  if (ae(e))
    return U;
  if (A(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = A(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = ye(e);
  var r = xe.test(e);
  return r || ve.test(e) ? Ce(e.slice(2), r ? 2 : 8) : Ee.test(e) ? U : +e;
}
var L = function() {
  return ue.Date.now();
}, Ie = "Expected a function", Se = Math.max, Re = Math.min;
function Pe(e, t, r) {
  var l, s, n, o, i, u, _ = 0, h = !1, c = !1, w = !0;
  if (typeof e != "function")
    throw new TypeError(Ie);
  t = q(t) || 0, A(r) && (h = !!r.leading, c = "maxWait" in r, n = c ? Se(q(r.maxWait) || 0, t) : n, w = "trailing" in r ? !!r.trailing : w);
  function f(d) {
    var E = l, R = s;
    return l = s = void 0, _ = d, o = e.apply(R, E), o;
  }
  function x(d) {
    return _ = d, i = setTimeout(p, t), h ? f(d) : o;
  }
  function v(d) {
    var E = d - u, R = d - _, V = t - E;
    return c ? Re(V, n - R) : V;
  }
  function m(d) {
    var E = d - u, R = d - _;
    return u === void 0 || E >= t || E < 0 || c && R >= n;
  }
  function p() {
    var d = L();
    if (m(d))
      return b(d);
    i = setTimeout(p, v(d));
  }
  function b(d) {
    return i = void 0, w && l ? f(d) : (l = s = void 0, o);
  }
  function S() {
    i !== void 0 && clearTimeout(i), _ = 0, l = u = s = i = void 0;
  }
  function a() {
    return i === void 0 ? o : b(L());
  }
  function C() {
    var d = L(), E = m(d);
    if (l = arguments, s = this, u = d, E) {
      if (i === void 0)
        return x(u);
      if (c)
        return clearTimeout(i), i = setTimeout(p, t), f(u);
    }
    return i === void 0 && (i = setTimeout(p, t)), o;
  }
  return C.cancel = S, C.flush = a, C;
}
function Te(e, t) {
  return de(e, t);
}
var te = {
  exports: {}
}, k = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Oe = y, ke = Symbol.for("react.element"), Le = Symbol.for("react.fragment"), je = Object.prototype.hasOwnProperty, Fe = Oe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ne = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ne(e, t, r) {
  var l, s = {}, n = null, o = null;
  r !== void 0 && (n = "" + r), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (l in t) je.call(t, l) && !Ne.hasOwnProperty(l) && (s[l] = t[l]);
  if (e && e.defaultProps) for (l in t = e.defaultProps, t) s[l] === void 0 && (s[l] = t[l]);
  return {
    $$typeof: ke,
    type: e,
    key: n,
    ref: o,
    props: s,
    _owner: Fe.current
  };
}
k.Fragment = Le;
k.jsx = ne;
k.jsxs = ne;
te.exports = k;
var g = te.exports;
const {
  SvelteComponent: We,
  assign: z,
  binding_callbacks: B,
  check_outros: Ae,
  children: re,
  claim_element: oe,
  claim_space: Me,
  component_subscribe: G,
  compute_slots: De,
  create_slot: Ve,
  detach: I,
  element: se,
  empty: H,
  exclude_internal_props: K,
  get_all_dirty_from_scope: Ue,
  get_slot_changes: qe,
  group_outros: ze,
  init: Be,
  insert_hydration: T,
  safe_not_equal: Ge,
  set_custom_element_data: le,
  space: He,
  transition_in: O,
  transition_out: M,
  update_slot_base: Ke
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Ze
} = window.__gradio__svelte__internal;
function J(e) {
  let t, r;
  const l = (
    /*#slots*/
    e[7].default
  ), s = Ve(
    l,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = se("svelte-slot"), s && s.c(), this.h();
    },
    l(n) {
      t = oe(n, "SVELTE-SLOT", {
        class: !0
      });
      var o = re(t);
      s && s.l(o), o.forEach(I), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      T(n, t, o), s && s.m(t, null), e[9](t), r = !0;
    },
    p(n, o) {
      s && s.p && (!r || o & /*$$scope*/
      64) && Ke(
        s,
        l,
        n,
        /*$$scope*/
        n[6],
        r ? qe(
          l,
          /*$$scope*/
          n[6],
          o,
          null
        ) : Ue(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      r || (O(s, n), r = !0);
    },
    o(n) {
      M(s, n), r = !1;
    },
    d(n) {
      n && I(t), s && s.d(n), e[9](null);
    }
  };
}
function Qe(e) {
  let t, r, l, s, n = (
    /*$$slots*/
    e[4].default && J(e)
  );
  return {
    c() {
      t = se("react-portal-target"), r = He(), n && n.c(), l = H(), this.h();
    },
    l(o) {
      t = oe(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), re(t).forEach(I), r = Me(o), n && n.l(o), l = H(), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(o, i) {
      T(o, t, i), e[8](t), T(o, r, i), n && n.m(o, i), T(o, l, i), s = !0;
    },
    p(o, [i]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, i), i & /*$$slots*/
      16 && O(n, 1)) : (n = J(o), n.c(), O(n, 1), n.m(l.parentNode, l)) : n && (ze(), M(n, 1, 1, () => {
        n = null;
      }), Ae());
    },
    i(o) {
      s || (O(n), s = !0);
    },
    o(o) {
      M(n), s = !1;
    },
    d(o) {
      o && (I(t), I(r), I(l)), e[8](null), n && n.d(o);
    }
  };
}
function X(e) {
  const {
    svelteInit: t,
    ...r
  } = e;
  return r;
}
function $e(e, t, r) {
  let l, s, {
    $$slots: n = {},
    $$scope: o
  } = t;
  const i = De(n);
  let {
    svelteInit: u
  } = t;
  const _ = P(X(t)), h = P();
  G(e, h, (a) => r(0, l = a));
  const c = P();
  G(e, c, (a) => r(1, s = a));
  const w = [], f = Xe("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: v,
    subSlotIndex: m
  } = fe() || {}, p = u({
    parent: f,
    props: _,
    target: h,
    slot: c,
    slotKey: x,
    slotIndex: v,
    subSlotIndex: m,
    onDestroy(a) {
      w.push(a);
    }
  });
  Ze("$$ms-gr-react-wrapper", p), Je(() => {
    _.set(X(t));
  }), Ye(() => {
    w.forEach((a) => a());
  });
  function b(a) {
    B[a ? "unshift" : "push"](() => {
      l = a, h.set(l);
    });
  }
  function S(a) {
    B[a ? "unshift" : "push"](() => {
      s = a, c.set(s);
    });
  }
  return e.$$set = (a) => {
    r(17, t = z(z({}, t), K(a))), "svelteInit" in a && r(5, u = a.svelteInit), "$$scope" in a && r(6, o = a.$$scope);
  }, t = K(t), [l, s, h, c, i, u, o, n, b, S];
}
class et extends We {
  constructor(t) {
    super(), Be(this, t, $e, Qe, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: mt
} = window.__gradio__svelte__internal, Y = window.ms_globals.rerender, j = window.ms_globals.tree;
function tt(e, t = {}) {
  function r(l) {
    const s = P(), n = new et({
      ...l,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const i = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: e,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, u = o.parent ?? j;
          return u.nodes = [...u.nodes, i], Y({
            createPortal: W,
            node: j
          }), o.onDestroy(() => {
            u.nodes = u.nodes.filter((_) => _.svelteInstance !== s), Y({
              createPortal: W,
              node: j
            });
          }), i;
        },
        ...l.props
      }
    });
    return s.set(n), n;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise.then(() => {
      l(r);
    });
  });
}
function nt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function rt(e, t = !1) {
  try {
    if (me(e))
      return e;
    if (t && !nt(e))
      return;
    if (typeof e == "string") {
      let r = e.trim();
      return r.startsWith(";") && (r = r.slice(1)), r.endsWith(";") && (r = r.slice(0, -1)), new Function(`return (...args) => (${r})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function Z(e, t) {
  return ie(() => rt(e, t), [e, t]);
}
function ot({
  value: e,
  onValueChange: t
}) {
  const [r, l] = ee(e), s = F(t);
  s.current = t;
  const n = F(r);
  return n.current = r, N(() => {
    s.current(r);
  }, [r]), N(() => {
    Te(e, n.current) || l(e);
  }, [e]), [r, l];
}
const st = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function lt(e) {
  return e ? Object.keys(e).reduce((t, r) => {
    const l = e[r];
    return t[r] = it(r, l), t;
  }, {}) : {};
}
function it(e, t) {
  return typeof t == "number" && !st.includes(e) ? t + "px" : t;
}
function D(e) {
  const t = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const s = y.Children.toArray(e._reactElement.props.children).map((n) => {
      if (y.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: i
        } = D(n.props.el);
        return y.cloneElement(n, {
          ...n.props,
          el: i,
          children: [...y.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return s.originalChildren = e._reactElement.props.children, t.push(W(y.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: s
    }), r)), {
      clonedElement: r,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((s) => {
    e.getEventListeners(s).forEach(({
      listener: o,
      type: i,
      useCapture: u
    }) => {
      r.addEventListener(i, o, u);
    });
  });
  const l = Array.from(e.childNodes);
  for (let s = 0; s < l.length; s++) {
    const n = l[s];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: i
      } = D(n);
      t.push(...i), r.appendChild(o);
    } else n.nodeType === 3 && r.appendChild(n.cloneNode());
  }
  return {
    clonedElement: r,
    portals: t
  };
}
function ct(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Q = ce(({
  slot: e,
  clone: t,
  className: r,
  style: l,
  observeAttributes: s
}, n) => {
  const o = F(), [i, u] = ee([]), {
    forceClone: _
  } = _e(), h = _ ? !0 : t;
  return N(() => {
    var v;
    if (!o.current || !e)
      return;
    let c = e;
    function w() {
      let m = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (m = c.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), ct(n, m), r && m.classList.add(...r.split(" ")), l) {
        const p = lt(l);
        Object.keys(p).forEach((b) => {
          m.style[b] = p[b];
        });
      }
    }
    let f = null, x = null;
    if (h && window.MutationObserver) {
      let m = function() {
        var a, C, d;
        (a = o.current) != null && a.contains(c) && ((C = o.current) == null || C.removeChild(c));
        const {
          portals: b,
          clonedElement: S
        } = D(e);
        c = S, u(b), c.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          w();
        }, 50), (d = o.current) == null || d.appendChild(c);
      };
      m();
      const p = Pe(() => {
        m(), f == null || f.disconnect(), f == null || f.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: s
        });
      }, 50);
      f = new window.MutationObserver(p), f.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", w(), (v = o.current) == null || v.appendChild(c);
    return () => {
      var m, p;
      c.style.display = "", (m = o.current) != null && m.contains(c) && ((p = o.current) == null || p.removeChild(c)), f == null || f.disconnect();
    };
  }, [e, h, r, l, n, s, _]), y.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...i);
}), at = ({
  children: e,
  ...t
}) => /* @__PURE__ */ g.jsx(g.Fragment, {
  children: e(t)
});
function ut(e) {
  return y.createElement(at, {
    children: e
  });
}
function $(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ut((r) => /* @__PURE__ */ g.jsx(pe, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ g.jsx(Q, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...r
    })
  })) : /* @__PURE__ */ g.jsx(Q, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function dt({
  key: e,
  slots: t,
  targets: r
}, l) {
  return t[e] ? (...s) => r ? r.map((n, o) => /* @__PURE__ */ g.jsx(y.Fragment, {
    children: $(n, {
      clone: !0,
      params: s,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ g.jsx(g.Fragment, {
    children: $(t[e], {
      clone: !0,
      params: s,
      forceClone: !0
    })
  }) : void 0;
}
const _t = tt(({
  formatter: e,
  onValueChange: t,
  onChange: r,
  children: l,
  setSlotParams: s,
  elRef: n,
  slots: o,
  separator: i,
  ...u
}) => {
  const _ = Z(e), h = Z(i, !0), [c, w] = ot({
    onValueChange: t,
    value: u.value
  });
  return /* @__PURE__ */ g.jsxs(g.Fragment, {
    children: [/* @__PURE__ */ g.jsx("div", {
      style: {
        display: "none"
      },
      children: l
    }), /* @__PURE__ */ g.jsx(he.OTP, {
      ...u,
      value: c,
      ref: n,
      formatter: _,
      separator: o.separator ? dt({
        slots: o,
        key: "separator"
      }) : h || i,
      onChange: (f) => {
        r == null || r(f), w(f);
      }
    })]
  });
});
export {
  _t as InputOTP,
  _t as default
};
