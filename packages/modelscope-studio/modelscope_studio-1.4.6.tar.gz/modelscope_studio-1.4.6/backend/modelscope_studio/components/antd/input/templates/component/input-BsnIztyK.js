import { i as ce, a as B, r as ue, b as fe, Z as O, g as de, c as me } from "./Index-CfRG6VMP.js";
const v = window.ms_globals.React, ae = window.ms_globals.React.forwardRef, N = window.ms_globals.React.useRef, ee = window.ms_globals.React.useState, W = window.ms_globals.React.useEffect, te = window.ms_globals.React.useMemo, M = window.ms_globals.ReactDOM.createPortal, _e = window.ms_globals.internalContext.useContextPropsContext, he = window.ms_globals.internalContext.ContextPropsProvider, pe = window.ms_globals.antd.Input;
var ge = /\s/;
function xe(e) {
  for (var t = e.length; t-- && ge.test(e.charAt(t)); )
    ;
  return t;
}
var we = /^\s+/;
function ye(e) {
  return e && e.slice(0, xe(e) + 1).replace(we, "");
}
var q = NaN, be = /^[-+]0x[0-9a-f]+$/i, ve = /^0b[01]+$/i, Ee = /^0o[0-7]+$/i, Ce = parseInt;
function z(e) {
  if (typeof e == "number")
    return e;
  if (ce(e))
    return q;
  if (B(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = B(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = ye(e);
  var n = ve.test(e);
  return n || Ee.test(e) ? Ce(e.slice(2), n ? 2 : 8) : be.test(e) ? q : +e;
}
var L = function() {
  return ue.Date.now();
}, Ie = "Expected a function", Se = Math.max, Re = Math.min;
function Pe(e, t, n) {
  var s, i, r, o, l, c, h = 0, g = !1, a = !1, x = !0;
  if (typeof e != "function")
    throw new TypeError(Ie);
  t = z(t) || 0, B(n) && (g = !!n.leading, a = "maxWait" in n, r = a ? Se(z(n.maxWait) || 0, t) : r, x = "trailing" in n ? !!n.trailing : x);
  function d(f) {
    var E = s, P = i;
    return s = i = void 0, h = f, o = e.apply(P, E), o;
  }
  function w(f) {
    return h = f, l = setTimeout(p, t), g ? d(f) : o;
  }
  function y(f) {
    var E = f - c, P = f - h, V = t - E;
    return a ? Re(V, r - P) : V;
  }
  function m(f) {
    var E = f - c, P = f - h;
    return c === void 0 || E >= t || E < 0 || a && P >= r;
  }
  function p() {
    var f = L();
    if (m(f))
      return b(f);
    l = setTimeout(p, y(f));
  }
  function b(f) {
    return l = void 0, x && s ? d(f) : (s = i = void 0, o);
  }
  function R() {
    l !== void 0 && clearTimeout(l), h = 0, s = c = i = l = void 0;
  }
  function u() {
    return l === void 0 ? o : b(L());
  }
  function I() {
    var f = L(), E = m(f);
    if (s = arguments, i = this, c = f, E) {
      if (l === void 0)
        return w(c);
      if (a)
        return clearTimeout(l), l = setTimeout(p, t), d(c);
    }
    return l === void 0 && (l = setTimeout(p, t)), o;
  }
  return I.cancel = R, I.flush = u, I;
}
function Te(e, t) {
  return fe(e, t);
}
var ne = {
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
var Oe = v, je = Symbol.for("react.element"), ke = Symbol.for("react.fragment"), Fe = Object.prototype.hasOwnProperty, Le = Oe.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ae = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function re(e, t, n) {
  var s, i = {}, r = null, o = null;
  n !== void 0 && (r = "" + n), t.key !== void 0 && (r = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (s in t) Fe.call(t, s) && !Ae.hasOwnProperty(s) && (i[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) i[s] === void 0 && (i[s] = t[s]);
  return {
    $$typeof: je,
    type: e,
    key: r,
    ref: o,
    props: i,
    _owner: Le.current
  };
}
F.Fragment = ke;
F.jsx = re;
F.jsxs = re;
ne.exports = F;
var _ = ne.exports;
const {
  SvelteComponent: Ne,
  assign: G,
  binding_callbacks: H,
  check_outros: We,
  children: oe,
  claim_element: se,
  claim_space: Me,
  component_subscribe: K,
  compute_slots: Be,
  create_slot: De,
  detach: S,
  element: ie,
  empty: J,
  exclude_internal_props: X,
  get_all_dirty_from_scope: Ue,
  get_slot_changes: Ve,
  group_outros: qe,
  init: ze,
  insert_hydration: j,
  safe_not_equal: Ge,
  set_custom_element_data: le,
  space: He,
  transition_in: k,
  transition_out: D,
  update_slot_base: Ke
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Ze
} = window.__gradio__svelte__internal;
function Y(e) {
  let t, n;
  const s = (
    /*#slots*/
    e[7].default
  ), i = De(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ie("svelte-slot"), i && i.c(), this.h();
    },
    l(r) {
      t = se(r, "SVELTE-SLOT", {
        class: !0
      });
      var o = oe(t);
      i && i.l(o), o.forEach(S), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(r, o) {
      j(r, t, o), i && i.m(t, null), e[9](t), n = !0;
    },
    p(r, o) {
      i && i.p && (!n || o & /*$$scope*/
      64) && Ke(
        i,
        s,
        r,
        /*$$scope*/
        r[6],
        n ? Ve(
          s,
          /*$$scope*/
          r[6],
          o,
          null
        ) : Ue(
          /*$$scope*/
          r[6]
        ),
        null
      );
    },
    i(r) {
      n || (k(i, r), n = !0);
    },
    o(r) {
      D(i, r), n = !1;
    },
    d(r) {
      r && S(t), i && i.d(r), e[9](null);
    }
  };
}
function Qe(e) {
  let t, n, s, i, r = (
    /*$$slots*/
    e[4].default && Y(e)
  );
  return {
    c() {
      t = ie("react-portal-target"), n = He(), r && r.c(), s = J(), this.h();
    },
    l(o) {
      t = se(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), oe(t).forEach(S), n = Me(o), r && r.l(o), s = J(), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(o, l) {
      j(o, t, l), e[8](t), j(o, n, l), r && r.m(o, l), j(o, s, l), i = !0;
    },
    p(o, [l]) {
      /*$$slots*/
      o[4].default ? r ? (r.p(o, l), l & /*$$slots*/
      16 && k(r, 1)) : (r = Y(o), r.c(), k(r, 1), r.m(s.parentNode, s)) : r && (qe(), D(r, 1, 1, () => {
        r = null;
      }), We());
    },
    i(o) {
      i || (k(r), i = !0);
    },
    o(o) {
      D(r), i = !1;
    },
    d(o) {
      o && (S(t), S(n), S(s)), e[8](null), r && r.d(o);
    }
  };
}
function Z(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function $e(e, t, n) {
  let s, i, {
    $$slots: r = {},
    $$scope: o
  } = t;
  const l = Be(r);
  let {
    svelteInit: c
  } = t;
  const h = O(Z(t)), g = O();
  K(e, g, (u) => n(0, s = u));
  const a = O();
  K(e, a, (u) => n(1, i = u));
  const x = [], d = Xe("$$ms-gr-react-wrapper"), {
    slotKey: w,
    slotIndex: y,
    subSlotIndex: m
  } = de() || {}, p = c({
    parent: d,
    props: h,
    target: g,
    slot: a,
    slotKey: w,
    slotIndex: y,
    subSlotIndex: m,
    onDestroy(u) {
      x.push(u);
    }
  });
  Ze("$$ms-gr-react-wrapper", p), Je(() => {
    h.set(Z(t));
  }), Ye(() => {
    x.forEach((u) => u());
  });
  function b(u) {
    H[u ? "unshift" : "push"](() => {
      s = u, g.set(s);
    });
  }
  function R(u) {
    H[u ? "unshift" : "push"](() => {
      i = u, a.set(i);
    });
  }
  return e.$$set = (u) => {
    n(17, t = G(G({}, t), X(u))), "svelteInit" in u && n(5, c = u.svelteInit), "$$scope" in u && n(6, o = u.$$scope);
  }, t = X(t), [s, i, g, a, l, c, o, r, b, R];
}
class et extends Ne {
  constructor(t) {
    super(), ze(this, t, $e, Qe, Ge, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: _t
} = window.__gradio__svelte__internal, Q = window.ms_globals.rerender, A = window.ms_globals.tree;
function tt(e, t = {}) {
  function n(s) {
    const i = O(), r = new et({
      ...s,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: i,
            reactComponent: e,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, c = o.parent ?? A;
          return c.nodes = [...c.nodes, l], Q({
            createPortal: M,
            node: A
          }), o.onDestroy(() => {
            c.nodes = c.nodes.filter((h) => h.svelteInstance !== i), Q({
              createPortal: M,
              node: A
            });
          }), l;
        },
        ...s.props
      }
    });
    return i.set(r), r;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise.then(() => {
      s(n);
    });
  });
}
const nt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function rt(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const s = e[n];
    return t[n] = ot(n, s), t;
  }, {}) : {};
}
function ot(e, t) {
  return typeof t == "number" && !nt.includes(e) ? t + "px" : t;
}
function U(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const i = v.Children.toArray(e._reactElement.props.children).map((r) => {
      if (v.isValidElement(r) && r.props.__slot__) {
        const {
          portals: o,
          clonedElement: l
        } = U(r.props.el);
        return v.cloneElement(r, {
          ...r.props,
          el: l,
          children: [...v.Children.toArray(r.props.children), ...o]
        });
      }
      return null;
    });
    return i.originalChildren = e._reactElement.props.children, t.push(M(v.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: i
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((i) => {
    e.getEventListeners(i).forEach(({
      listener: o,
      type: l,
      useCapture: c
    }) => {
      n.addEventListener(l, o, c);
    });
  });
  const s = Array.from(e.childNodes);
  for (let i = 0; i < s.length; i++) {
    const r = s[i];
    if (r.nodeType === 1) {
      const {
        clonedElement: o,
        portals: l
      } = U(r);
      t.push(...l), n.appendChild(o);
    } else r.nodeType === 3 && n.appendChild(r.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function st(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const C = ae(({
  slot: e,
  clone: t,
  className: n,
  style: s,
  observeAttributes: i
}, r) => {
  const o = N(), [l, c] = ee([]), {
    forceClone: h
  } = _e(), g = h ? !0 : t;
  return W(() => {
    var y;
    if (!o.current || !e)
      return;
    let a = e;
    function x() {
      let m = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (m = a.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), st(r, m), n && m.classList.add(...n.split(" ")), s) {
        const p = rt(s);
        Object.keys(p).forEach((b) => {
          m.style[b] = p[b];
        });
      }
    }
    let d = null, w = null;
    if (g && window.MutationObserver) {
      let m = function() {
        var u, I, f;
        (u = o.current) != null && u.contains(a) && ((I = o.current) == null || I.removeChild(a));
        const {
          portals: b,
          clonedElement: R
        } = U(e);
        a = R, c(b), a.style.display = "contents", w && clearTimeout(w), w = setTimeout(() => {
          x();
        }, 50), (f = o.current) == null || f.appendChild(a);
      };
      m();
      const p = Pe(() => {
        m(), d == null || d.disconnect(), d == null || d.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      d = new window.MutationObserver(p), d.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", x(), (y = o.current) == null || y.appendChild(a);
    return () => {
      var m, p;
      a.style.display = "", (m = o.current) != null && m.contains(a) && ((p = o.current) == null || p.removeChild(a)), d == null || d.disconnect();
    };
  }, [e, g, n, s, r, i, h]), v.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...l);
});
function it(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function lt(e, t = !1) {
  try {
    if (me(e))
      return e;
    if (t && !it(e))
      return;
    if (typeof e == "string") {
      let n = e.trim();
      return n.startsWith(";") && (n = n.slice(1)), n.endsWith(";") && (n = n.slice(0, -1)), new Function(`return (...args) => (${n})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function T(e, t) {
  return te(() => lt(e, t), [e, t]);
}
function at({
  value: e,
  onValueChange: t
}) {
  const [n, s] = ee(e), i = N(t);
  i.current = t;
  const r = N(n);
  return r.current = n, W(() => {
    i.current(n);
  }, [n]), W(() => {
    Te(e, r.current) || s(e);
  }, [e]), [n, s];
}
function ct(e, t) {
  return Object.keys(e).reduce((n, s) => (e[s] !== void 0 && (n[s] = e[s]), n), {});
}
const ut = ({
  children: e,
  ...t
}) => /* @__PURE__ */ _.jsx(_.Fragment, {
  children: e(t)
});
function ft(e) {
  return v.createElement(ut, {
    children: e
  });
}
function $(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ft((n) => /* @__PURE__ */ _.jsx(he, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ _.jsx(C, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...n
    })
  })) : /* @__PURE__ */ _.jsx(C, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function dt({
  key: e,
  slots: t,
  targets: n
}, s) {
  return t[e] ? (...i) => n ? n.map((r, o) => /* @__PURE__ */ _.jsx(v.Fragment, {
    children: $(r, {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ _.jsx(_.Fragment, {
    children: $(t[e], {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }) : void 0;
}
const ht = tt(({
  slots: e,
  children: t,
  count: n,
  showCount: s,
  onValueChange: i,
  onChange: r,
  setSlotParams: o,
  elRef: l,
  ...c
}) => {
  const h = T(n == null ? void 0 : n.strategy), g = T(n == null ? void 0 : n.exceedFormatter), a = T(n == null ? void 0 : n.show), x = T(typeof s == "object" ? s.formatter : void 0), [d, w] = at({
    onValueChange: i,
    value: c.value
  });
  return /* @__PURE__ */ _.jsxs(_.Fragment, {
    children: [/* @__PURE__ */ _.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ _.jsx(pe, {
      ...c,
      value: d,
      ref: l,
      onChange: (y) => {
        r == null || r(y), w(y.target.value);
      },
      showCount: e["showCount.formatter"] ? {
        formatter: dt({
          slots: e,
          key: "showCount.formatter"
        })
      } : typeof s == "object" && x ? {
        ...s,
        formatter: x
      } : s,
      count: te(() => ct({
        ...n,
        exceedFormatter: g,
        strategy: h,
        show: a || (n == null ? void 0 : n.show)
      }), [n, g, h, a]),
      addonAfter: e.addonAfter ? /* @__PURE__ */ _.jsx(C, {
        slot: e.addonAfter
      }) : c.addonAfter,
      addonBefore: e.addonBefore ? /* @__PURE__ */ _.jsx(C, {
        slot: e.addonBefore
      }) : c.addonBefore,
      allowClear: e["allowClear.clearIcon"] ? {
        clearIcon: /* @__PURE__ */ _.jsx(C, {
          slot: e["allowClear.clearIcon"]
        })
      } : c.allowClear,
      prefix: e.prefix ? /* @__PURE__ */ _.jsx(C, {
        slot: e.prefix
      }) : c.prefix,
      suffix: e.suffix ? /* @__PURE__ */ _.jsx(C, {
        slot: e.suffix
      }) : c.suffix
    })]
  });
});
export {
  ht as Input,
  ht as default
};
