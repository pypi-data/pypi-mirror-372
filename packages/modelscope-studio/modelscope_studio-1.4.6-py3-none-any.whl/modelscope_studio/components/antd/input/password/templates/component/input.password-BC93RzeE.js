import { i as ue, a as B, r as de, b as fe, Z as O, g as me, c as _e } from "./Index-ZVWoto5l.js";
const b = window.ms_globals.React, ce = window.ms_globals.React.forwardRef, N = window.ms_globals.React.useRef, te = window.ms_globals.React.useState, W = window.ms_globals.React.useEffect, ne = window.ms_globals.React.useMemo, M = window.ms_globals.ReactDOM.createPortal, he = window.ms_globals.internalContext.useContextPropsContext, pe = window.ms_globals.internalContext.ContextPropsProvider, ge = window.ms_globals.antd.Input;
var we = /\s/;
function xe(e) {
  for (var t = e.length; t-- && we.test(e.charAt(t)); )
    ;
  return t;
}
var ye = /^\s+/;
function be(e) {
  return e && e.slice(0, xe(e) + 1).replace(ye, "");
}
var q = NaN, ve = /^[-+]0x[0-9a-f]+$/i, Ee = /^0b[01]+$/i, Ce = /^0o[0-7]+$/i, Ie = parseInt;
function z(e) {
  if (typeof e == "number")
    return e;
  if (ue(e))
    return q;
  if (B(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = B(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = be(e);
  var n = Ee.test(e);
  return n || Ce.test(e) ? Ie(e.slice(2), n ? 2 : 8) : ve.test(e) ? q : +e;
}
var L = function() {
  return de.Date.now();
}, Se = "Expected a function", Re = Math.max, Pe = Math.min;
function Te(e, t, n) {
  var s, i, r, o, l, d, f = 0, g = !1, a = !1, w = !0;
  if (typeof e != "function")
    throw new TypeError(Se);
  t = z(t) || 0, B(n) && (g = !!n.leading, a = "maxWait" in n, r = a ? Re(z(n.maxWait) || 0, t) : r, w = "trailing" in n ? !!n.trailing : w);
  function _(u) {
    var E = s, P = i;
    return s = i = void 0, f = u, o = e.apply(P, E), o;
  }
  function x(u) {
    return f = u, l = setTimeout(h, t), g ? _(u) : o;
  }
  function v(u) {
    var E = u - d, P = u - f, V = t - E;
    return a ? Pe(V, r - P) : V;
  }
  function m(u) {
    var E = u - d, P = u - f;
    return d === void 0 || E >= t || E < 0 || a && P >= r;
  }
  function h() {
    var u = L();
    if (m(u))
      return y(u);
    l = setTimeout(h, v(u));
  }
  function y(u) {
    return l = void 0, w && s ? _(u) : (s = i = void 0, o);
  }
  function R() {
    l !== void 0 && clearTimeout(l), f = 0, s = d = i = l = void 0;
  }
  function c() {
    return l === void 0 ? o : y(L());
  }
  function I() {
    var u = L(), E = m(u);
    if (s = arguments, i = this, d = u, E) {
      if (l === void 0)
        return x(d);
      if (a)
        return clearTimeout(l), l = setTimeout(h, t), _(d);
    }
    return l === void 0 && (l = setTimeout(h, t)), o;
  }
  return I.cancel = R, I.flush = c, I;
}
function Oe(e, t) {
  return fe(e, t);
}
var re = {
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
var je = b, ke = Symbol.for("react.element"), Fe = Symbol.for("react.fragment"), Le = Object.prototype.hasOwnProperty, Ae = je.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ne = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function oe(e, t, n) {
  var s, i = {}, r = null, o = null;
  n !== void 0 && (r = "" + n), t.key !== void 0 && (r = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (s in t) Le.call(t, s) && !Ne.hasOwnProperty(s) && (i[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) i[s] === void 0 && (i[s] = t[s]);
  return {
    $$typeof: ke,
    type: e,
    key: r,
    ref: o,
    props: i,
    _owner: Ae.current
  };
}
F.Fragment = Fe;
F.jsx = oe;
F.jsxs = oe;
re.exports = F;
var p = re.exports;
const {
  SvelteComponent: We,
  assign: G,
  binding_callbacks: H,
  check_outros: Me,
  children: se,
  claim_element: ie,
  claim_space: Be,
  component_subscribe: K,
  compute_slots: De,
  create_slot: Ue,
  detach: S,
  element: le,
  empty: J,
  exclude_internal_props: X,
  get_all_dirty_from_scope: Ve,
  get_slot_changes: qe,
  group_outros: ze,
  init: Ge,
  insert_hydration: j,
  safe_not_equal: He,
  set_custom_element_data: ae,
  space: Ke,
  transition_in: k,
  transition_out: D,
  update_slot_base: Je
} = window.__gradio__svelte__internal, {
  beforeUpdate: Xe,
  getContext: Ye,
  onDestroy: Ze,
  setContext: Qe
} = window.__gradio__svelte__internal;
function Y(e) {
  let t, n;
  const s = (
    /*#slots*/
    e[7].default
  ), i = Ue(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = le("svelte-slot"), i && i.c(), this.h();
    },
    l(r) {
      t = ie(r, "SVELTE-SLOT", {
        class: !0
      });
      var o = se(t);
      i && i.l(o), o.forEach(S), this.h();
    },
    h() {
      ae(t, "class", "svelte-1rt0kpf");
    },
    m(r, o) {
      j(r, t, o), i && i.m(t, null), e[9](t), n = !0;
    },
    p(r, o) {
      i && i.p && (!n || o & /*$$scope*/
      64) && Je(
        i,
        s,
        r,
        /*$$scope*/
        r[6],
        n ? qe(
          s,
          /*$$scope*/
          r[6],
          o,
          null
        ) : Ve(
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
function $e(e) {
  let t, n, s, i, r = (
    /*$$slots*/
    e[4].default && Y(e)
  );
  return {
    c() {
      t = le("react-portal-target"), n = Ke(), r && r.c(), s = J(), this.h();
    },
    l(o) {
      t = ie(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), se(t).forEach(S), n = Be(o), r && r.l(o), s = J(), this.h();
    },
    h() {
      ae(t, "class", "svelte-1rt0kpf");
    },
    m(o, l) {
      j(o, t, l), e[8](t), j(o, n, l), r && r.m(o, l), j(o, s, l), i = !0;
    },
    p(o, [l]) {
      /*$$slots*/
      o[4].default ? r ? (r.p(o, l), l & /*$$slots*/
      16 && k(r, 1)) : (r = Y(o), r.c(), k(r, 1), r.m(s.parentNode, s)) : r && (ze(), D(r, 1, 1, () => {
        r = null;
      }), Me());
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
function et(e, t, n) {
  let s, i, {
    $$slots: r = {},
    $$scope: o
  } = t;
  const l = De(r);
  let {
    svelteInit: d
  } = t;
  const f = O(Z(t)), g = O();
  K(e, g, (c) => n(0, s = c));
  const a = O();
  K(e, a, (c) => n(1, i = c));
  const w = [], _ = Ye("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: v,
    subSlotIndex: m
  } = me() || {}, h = d({
    parent: _,
    props: f,
    target: g,
    slot: a,
    slotKey: x,
    slotIndex: v,
    subSlotIndex: m,
    onDestroy(c) {
      w.push(c);
    }
  });
  Qe("$$ms-gr-react-wrapper", h), Xe(() => {
    f.set(Z(t));
  }), Ze(() => {
    w.forEach((c) => c());
  });
  function y(c) {
    H[c ? "unshift" : "push"](() => {
      s = c, g.set(s);
    });
  }
  function R(c) {
    H[c ? "unshift" : "push"](() => {
      i = c, a.set(i);
    });
  }
  return e.$$set = (c) => {
    n(17, t = G(G({}, t), X(c))), "svelteInit" in c && n(5, d = c.svelteInit), "$$scope" in c && n(6, o = c.$$scope);
  }, t = X(t), [s, i, g, a, l, d, o, r, y, R];
}
class tt extends We {
  constructor(t) {
    super(), Ge(this, t, et, $e, He, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: _t
} = window.__gradio__svelte__internal, Q = window.ms_globals.rerender, A = window.ms_globals.tree;
function nt(e, t = {}) {
  function n(s) {
    const i = O(), r = new tt({
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
          }, d = o.parent ?? A;
          return d.nodes = [...d.nodes, l], Q({
            createPortal: M,
            node: A
          }), o.onDestroy(() => {
            d.nodes = d.nodes.filter((f) => f.svelteInstance !== i), Q({
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
const rt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function ot(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const s = e[n];
    return t[n] = st(n, s), t;
  }, {}) : {};
}
function st(e, t) {
  return typeof t == "number" && !rt.includes(e) ? t + "px" : t;
}
function U(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const i = b.Children.toArray(e._reactElement.props.children).map((r) => {
      if (b.isValidElement(r) && r.props.__slot__) {
        const {
          portals: o,
          clonedElement: l
        } = U(r.props.el);
        return b.cloneElement(r, {
          ...r.props,
          el: l,
          children: [...b.Children.toArray(r.props.children), ...o]
        });
      }
      return null;
    });
    return i.originalChildren = e._reactElement.props.children, t.push(M(b.cloneElement(e._reactElement, {
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
      useCapture: d
    }) => {
      n.addEventListener(l, o, d);
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
function it(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const C = ce(({
  slot: e,
  clone: t,
  className: n,
  style: s,
  observeAttributes: i
}, r) => {
  const o = N(), [l, d] = te([]), {
    forceClone: f
  } = he(), g = f ? !0 : t;
  return W(() => {
    var v;
    if (!o.current || !e)
      return;
    let a = e;
    function w() {
      let m = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (m = a.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), it(r, m), n && m.classList.add(...n.split(" ")), s) {
        const h = ot(s);
        Object.keys(h).forEach((y) => {
          m.style[y] = h[y];
        });
      }
    }
    let _ = null, x = null;
    if (g && window.MutationObserver) {
      let m = function() {
        var c, I, u;
        (c = o.current) != null && c.contains(a) && ((I = o.current) == null || I.removeChild(a));
        const {
          portals: y,
          clonedElement: R
        } = U(e);
        a = R, d(y), a.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          w();
        }, 50), (u = o.current) == null || u.appendChild(a);
      };
      m();
      const h = Te(() => {
        m(), _ == null || _.disconnect(), _ == null || _.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      _ = new window.MutationObserver(h), _.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", w(), (v = o.current) == null || v.appendChild(a);
    return () => {
      var m, h;
      a.style.display = "", (m = o.current) != null && m.contains(a) && ((h = o.current) == null || h.removeChild(a)), _ == null || _.disconnect();
    };
  }, [e, g, n, s, r, i, f]), b.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...l);
});
function lt(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function at(e, t = !1) {
  try {
    if (_e(e))
      return e;
    if (t && !lt(e))
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
  return ne(() => at(e, t), [e, t]);
}
function ct({
  value: e,
  onValueChange: t
}) {
  const [n, s] = te(e), i = N(t);
  i.current = t;
  const r = N(n);
  return r.current = n, W(() => {
    i.current(n);
  }, [n]), W(() => {
    Oe(e, r.current) || s(e);
  }, [e]), [n, s];
}
function ut(e, t) {
  return Object.keys(e).reduce((n, s) => (e[s] !== void 0 && (n[s] = e[s]), n), {});
}
const dt = ({
  children: e,
  ...t
}) => /* @__PURE__ */ p.jsx(p.Fragment, {
  children: e(t)
});
function ft(e) {
  return b.createElement(dt, {
    children: e
  });
}
function $(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ft((n) => /* @__PURE__ */ p.jsx(pe, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ p.jsx(C, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...n
    })
  })) : /* @__PURE__ */ p.jsx(C, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function ee({
  key: e,
  slots: t,
  targets: n
}, s) {
  return t[e] ? (...i) => n ? n.map((r, o) => /* @__PURE__ */ p.jsx(b.Fragment, {
    children: $(r, {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ p.jsx(p.Fragment, {
    children: $(t[e], {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }) : void 0;
}
const ht = nt(({
  slots: e,
  children: t,
  count: n,
  showCount: s,
  onValueChange: i,
  onChange: r,
  iconRender: o,
  elRef: l,
  setSlotParams: d,
  ...f
}) => {
  const g = T(n == null ? void 0 : n.strategy), a = T(n == null ? void 0 : n.exceedFormatter), w = T(n == null ? void 0 : n.show), _ = T(typeof s == "object" ? s.formatter : void 0), x = T(o), [v, m] = ct({
    onValueChange: i,
    value: f.value
  });
  return /* @__PURE__ */ p.jsxs(p.Fragment, {
    children: [/* @__PURE__ */ p.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ p.jsx(ge.Password, {
      ...f,
      value: v,
      ref: l,
      onChange: (h) => {
        r == null || r(h), m(h.target.value);
      },
      iconRender: e.iconRender ? ee({
        slots: e,
        key: "iconRender"
      }) : x,
      showCount: e["showCount.formatter"] ? {
        formatter: ee({
          slots: e,
          key: "showCount.formatter"
        })
      } : typeof s == "object" && _ ? {
        ...s,
        formatter: _
      } : s,
      count: ne(() => ut({
        ...n,
        exceedFormatter: a,
        strategy: g,
        show: w || (n == null ? void 0 : n.show)
      }), [n, a, g, w]),
      addonAfter: e.addonAfter ? /* @__PURE__ */ p.jsx(C, {
        slot: e.addonAfter
      }) : f.addonAfter,
      addonBefore: e.addonBefore ? /* @__PURE__ */ p.jsx(C, {
        slot: e.addonBefore
      }) : f.addonBefore,
      allowClear: e["allowClear.clearIcon"] ? {
        clearIcon: /* @__PURE__ */ p.jsx(C, {
          slot: e["allowClear.clearIcon"]
        })
      } : f.allowClear,
      prefix: e.prefix ? /* @__PURE__ */ p.jsx(C, {
        slot: e.prefix
      }) : f.prefix,
      suffix: e.suffix ? /* @__PURE__ */ p.jsx(C, {
        slot: e.suffix
      }) : f.suffix
    })]
  });
});
export {
  ht as InputPassword,
  ht as default
};
