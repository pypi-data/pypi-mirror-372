import { i as fe, a as B, r as pe, Z as j, g as me, t as _e, s as R, c as ge } from "./Index-D3y_ZTFF.js";
const C = window.ms_globals.React, A = window.ms_globals.React.useMemo, ne = window.ms_globals.React.useState, re = window.ms_globals.React.useEffect, ue = window.ms_globals.React.forwardRef, de = window.ms_globals.React.useRef, U = window.ms_globals.ReactDOM.createPortal, he = window.ms_globals.internalContext.useContextPropsContext, be = window.ms_globals.internalContext.ContextPropsProvider, O = window.ms_globals.antd.Typography;
var ye = /\s/;
function xe(e) {
  for (var t = e.length; t-- && ye.test(e.charAt(t)); )
    ;
  return t;
}
var Ce = /^\s+/;
function we(e) {
  return e && e.slice(0, xe(e) + 1).replace(Ce, "");
}
var K = NaN, Ee = /^[-+]0x[0-9a-f]+$/i, ve = /^0b[01]+$/i, Ie = /^0o[0-7]+$/i, Se = parseInt;
function V(e) {
  if (typeof e == "number")
    return e;
  if (fe(e))
    return K;
  if (B(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = B(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = we(e);
  var r = ve.test(e);
  return r || Ie.test(e) ? Se(e.slice(2), r ? 2 : 8) : Ee.test(e) ? K : +e;
}
var W = function() {
  return pe.Date.now();
}, Te = "Expected a function", Pe = Math.max, Re = Math.min;
function Oe(e, t, r) {
  var l, s, n, o, i, c, g = 0, h = !1, a = !1, y = !0;
  if (typeof e != "function")
    throw new TypeError(Te);
  t = V(t) || 0, B(r) && (h = !!r.leading, a = "maxWait" in r, n = a ? Pe(V(r.maxWait) || 0, t) : n, y = "trailing" in r ? !!r.trailing : y);
  function p(d) {
    var b = l, v = s;
    return l = s = void 0, g = d, o = e.apply(v, b), o;
  }
  function w(d) {
    return g = d, i = setTimeout(m, t), h ? p(d) : o;
  }
  function E(d) {
    var b = d - c, v = d - g, H = t - b;
    return a ? Re(H, n - v) : H;
  }
  function f(d) {
    var b = d - c, v = d - g;
    return c === void 0 || b >= t || b < 0 || a && v >= n;
  }
  function m() {
    var d = W();
    if (f(d))
      return x(d);
    i = setTimeout(m, E(d));
  }
  function x(d) {
    return i = void 0, y && l ? p(d) : (l = s = void 0, o);
  }
  function T() {
    i !== void 0 && clearTimeout(i), g = 0, l = c = s = i = void 0;
  }
  function u() {
    return i === void 0 ? o : x(W());
  }
  function S() {
    var d = W(), b = f(d);
    if (l = arguments, s = this, c = d, b) {
      if (i === void 0)
        return w(c);
      if (a)
        return clearTimeout(i), i = setTimeout(m, t), p(c);
    }
    return i === void 0 && (i = setTimeout(m, t)), o;
  }
  return S.cancel = T, S.flush = u, S;
}
var oe = {
  exports: {}
}, N = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var je = C, ke = Symbol.for("react.element"), Le = Symbol.for("react.fragment"), Ae = Object.prototype.hasOwnProperty, Ne = je.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, We = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function le(e, t, r) {
  var l, s = {}, n = null, o = null;
  r !== void 0 && (n = "" + r), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (l in t) Ae.call(t, l) && !We.hasOwnProperty(l) && (s[l] = t[l]);
  if (e && e.defaultProps) for (l in t = e.defaultProps, t) s[l] === void 0 && (s[l] = t[l]);
  return {
    $$typeof: ke,
    type: e,
    key: n,
    ref: o,
    props: s,
    _owner: Ne.current
  };
}
N.Fragment = Le;
N.jsx = le;
N.jsxs = le;
oe.exports = N;
var _ = oe.exports;
const {
  SvelteComponent: Fe,
  assign: q,
  binding_callbacks: J,
  check_outros: Me,
  children: se,
  claim_element: ie,
  claim_space: De,
  component_subscribe: X,
  compute_slots: Ue,
  create_slot: Be,
  detach: P,
  element: ae,
  empty: Y,
  exclude_internal_props: Z,
  get_all_dirty_from_scope: ze,
  get_slot_changes: Ge,
  group_outros: He,
  init: Ke,
  insert_hydration: k,
  safe_not_equal: Ve,
  set_custom_element_data: ce,
  space: qe,
  transition_in: L,
  transition_out: z,
  update_slot_base: Je
} = window.__gradio__svelte__internal, {
  beforeUpdate: Xe,
  getContext: Ye,
  onDestroy: Ze,
  setContext: Qe
} = window.__gradio__svelte__internal;
function Q(e) {
  let t, r;
  const l = (
    /*#slots*/
    e[7].default
  ), s = Be(
    l,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ae("svelte-slot"), s && s.c(), this.h();
    },
    l(n) {
      t = ie(n, "SVELTE-SLOT", {
        class: !0
      });
      var o = se(t);
      s && s.l(o), o.forEach(P), this.h();
    },
    h() {
      ce(t, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      k(n, t, o), s && s.m(t, null), e[9](t), r = !0;
    },
    p(n, o) {
      s && s.p && (!r || o & /*$$scope*/
      64) && Je(
        s,
        l,
        n,
        /*$$scope*/
        n[6],
        r ? Ge(
          l,
          /*$$scope*/
          n[6],
          o,
          null
        ) : ze(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      r || (L(s, n), r = !0);
    },
    o(n) {
      z(s, n), r = !1;
    },
    d(n) {
      n && P(t), s && s.d(n), e[9](null);
    }
  };
}
function $e(e) {
  let t, r, l, s, n = (
    /*$$slots*/
    e[4].default && Q(e)
  );
  return {
    c() {
      t = ae("react-portal-target"), r = qe(), n && n.c(), l = Y(), this.h();
    },
    l(o) {
      t = ie(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), se(t).forEach(P), r = De(o), n && n.l(o), l = Y(), this.h();
    },
    h() {
      ce(t, "class", "svelte-1rt0kpf");
    },
    m(o, i) {
      k(o, t, i), e[8](t), k(o, r, i), n && n.m(o, i), k(o, l, i), s = !0;
    },
    p(o, [i]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, i), i & /*$$slots*/
      16 && L(n, 1)) : (n = Q(o), n.c(), L(n, 1), n.m(l.parentNode, l)) : n && (He(), z(n, 1, 1, () => {
        n = null;
      }), Me());
    },
    i(o) {
      s || (L(n), s = !0);
    },
    o(o) {
      z(n), s = !1;
    },
    d(o) {
      o && (P(t), P(r), P(l)), e[8](null), n && n.d(o);
    }
  };
}
function $(e) {
  const {
    svelteInit: t,
    ...r
  } = e;
  return r;
}
function et(e, t, r) {
  let l, s, {
    $$slots: n = {},
    $$scope: o
  } = t;
  const i = Ue(n);
  let {
    svelteInit: c
  } = t;
  const g = j($(t)), h = j();
  X(e, h, (u) => r(0, l = u));
  const a = j();
  X(e, a, (u) => r(1, s = u));
  const y = [], p = Ye("$$ms-gr-react-wrapper"), {
    slotKey: w,
    slotIndex: E,
    subSlotIndex: f
  } = me() || {}, m = c({
    parent: p,
    props: g,
    target: h,
    slot: a,
    slotKey: w,
    slotIndex: E,
    subSlotIndex: f,
    onDestroy(u) {
      y.push(u);
    }
  });
  Qe("$$ms-gr-react-wrapper", m), Xe(() => {
    g.set($(t));
  }), Ze(() => {
    y.forEach((u) => u());
  });
  function x(u) {
    J[u ? "unshift" : "push"](() => {
      l = u, h.set(l);
    });
  }
  function T(u) {
    J[u ? "unshift" : "push"](() => {
      s = u, a.set(s);
    });
  }
  return e.$$set = (u) => {
    r(17, t = q(q({}, t), Z(u))), "svelteInit" in u && r(5, c = u.svelteInit), "$$scope" in u && r(6, o = u.$$scope);
  }, t = Z(t), [l, s, h, a, i, c, o, n, x, T];
}
class tt extends Fe {
  constructor(t) {
    super(), Ke(this, t, et, $e, Ve, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: _t
} = window.__gradio__svelte__internal, ee = window.ms_globals.rerender, F = window.ms_globals.tree;
function nt(e, t = {}) {
  function r(l) {
    const s = j(), n = new tt({
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
          }, c = o.parent ?? F;
          return c.nodes = [...c.nodes, i], ee({
            createPortal: U,
            node: F
          }), o.onDestroy(() => {
            c.nodes = c.nodes.filter((g) => g.svelteInstance !== s), ee({
              createPortal: U,
              node: F
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
function rt(e) {
  const [t, r] = ne(() => R(e));
  return re(() => {
    let l = !0;
    return e.subscribe((n) => {
      l && (l = !1, n === t) || r(n);
    });
  }, [e]), t;
}
function ot(e) {
  const t = A(() => _e(e, (r) => r), [e]);
  return rt(t);
}
const lt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function st(e) {
  return e ? Object.keys(e).reduce((t, r) => {
    const l = e[r];
    return t[r] = it(r, l), t;
  }, {}) : {};
}
function it(e, t) {
  return typeof t == "number" && !lt.includes(e) ? t + "px" : t;
}
function G(e) {
  const t = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const s = C.Children.toArray(e._reactElement.props.children).map((n) => {
      if (C.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: i
        } = G(n.props.el);
        return C.cloneElement(n, {
          ...n.props,
          el: i,
          children: [...C.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return s.originalChildren = e._reactElement.props.children, t.push(U(C.cloneElement(e._reactElement, {
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
      useCapture: c
    }) => {
      r.addEventListener(i, o, c);
    });
  });
  const l = Array.from(e.childNodes);
  for (let s = 0; s < l.length; s++) {
    const n = l[s];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: i
      } = G(n);
      t.push(...i), r.appendChild(o);
    } else n.nodeType === 3 && r.appendChild(n.cloneNode());
  }
  return {
    clonedElement: r,
    portals: t
  };
}
function at(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const I = ue(({
  slot: e,
  clone: t,
  className: r,
  style: l,
  observeAttributes: s
}, n) => {
  const o = de(), [i, c] = ne([]), {
    forceClone: g
  } = he(), h = g ? !0 : t;
  return re(() => {
    var E;
    if (!o.current || !e)
      return;
    let a = e;
    function y() {
      let f = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (f = a.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), at(n, f), r && f.classList.add(...r.split(" ")), l) {
        const m = st(l);
        Object.keys(m).forEach((x) => {
          f.style[x] = m[x];
        });
      }
    }
    let p = null, w = null;
    if (h && window.MutationObserver) {
      let f = function() {
        var u, S, d;
        (u = o.current) != null && u.contains(a) && ((S = o.current) == null || S.removeChild(a));
        const {
          portals: x,
          clonedElement: T
        } = G(e);
        a = T, c(x), a.style.display = "contents", w && clearTimeout(w), w = setTimeout(() => {
          y();
        }, 50), (d = o.current) == null || d.appendChild(a);
      };
      f();
      const m = Oe(() => {
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
      a.style.display = "contents", y(), (E = o.current) == null || E.appendChild(a);
    return () => {
      var f, m;
      a.style.display = "", (f = o.current) != null && f.contains(a) && ((m = o.current) == null || m.removeChild(a)), p == null || p.disconnect();
    };
  }, [e, h, r, l, n, s, g]), C.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...i);
});
function ct(e) {
  return A(() => {
    const t = C.Children.toArray(e), r = [], l = [];
    return t.forEach((s) => {
      s.props.node && s.props.nodeSlotKey ? r.push(s) : l.push(s);
    }), [r, l];
  }, [e]);
}
function M(e, t) {
  const r = A(() => C.Children.toArray(e.originalChildren || e).filter((n) => n.props.node && !n.props.node.ignore && (!t && !n.props.nodeSlotKey || t && t === n.props.nodeSlotKey)).sort((n, o) => {
    if (n.props.node.slotIndex && o.props.node.slotIndex) {
      const i = R(n.props.node.slotIndex) || 0, c = R(o.props.node.slotIndex) || 0;
      return i - c === 0 && n.props.node.subSlotIndex && o.props.node.subSlotIndex ? (R(n.props.node.subSlotIndex) || 0) - (R(o.props.node.subSlotIndex) || 0) : i - c;
    }
    return 0;
  }).map((n) => n.props.node.target), [e, t]);
  return ot(r);
}
function ut(e, t) {
  return Object.keys(e).reduce((r, l) => (e[l] !== void 0 && (r[l] = e[l]), r), {});
}
const dt = ({
  children: e,
  ...t
}) => /* @__PURE__ */ _.jsx(_.Fragment, {
  children: e(t)
});
function ft(e) {
  return C.createElement(dt, {
    children: e
  });
}
function te(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ft((r) => /* @__PURE__ */ _.jsx(be, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ _.jsx(I, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...r
    })
  })) : /* @__PURE__ */ _.jsx(I, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function pt({
  key: e,
  slots: t,
  targets: r
}, l) {
  return t[e] ? (...s) => r ? r.map((n, o) => /* @__PURE__ */ _.jsx(C.Fragment, {
    children: te(n, {
      clone: !0,
      params: s,
      forceClone: (l == null ? void 0 : l.forceClone) ?? !0
    })
  }, o)) : /* @__PURE__ */ _.jsx(_.Fragment, {
    children: te(t[e], {
      clone: !0,
      params: s,
      forceClone: (l == null ? void 0 : l.forceClone) ?? !0
    })
  }) : void 0;
}
function D(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const gt = nt(({
  component: e,
  className: t,
  slots: r,
  children: l,
  copyable: s,
  editable: n,
  ellipsis: o,
  setSlotParams: i,
  value: c,
  ...g
}) => {
  var d;
  const h = M(l, "copyable.tooltips"), a = M(l, "copyable.icon"), y = r["copyable.icon"] || h.length > 0 || s, p = r["editable.icon"] || r["editable.tooltip"] || r["editable.enterIcon"] || n, w = r["ellipsis.symbol"] || r["ellipsis.tooltip"] || r["ellipsis.tooltip.title"] || o, E = D(s), f = D(n), m = D(o), x = A(() => {
    switch (e) {
      case "title":
        return O.Title;
      case "paragraph":
        return O.Paragraph;
      case "text":
        return O.Text;
      case "link":
        return O.Link;
    }
  }, [e]), [T, u] = ct(l), S = M(l);
  return /* @__PURE__ */ _.jsxs(_.Fragment, {
    children: [/* @__PURE__ */ _.jsx("div", {
      style: {
        display: "none"
      },
      children: T
    }), /* @__PURE__ */ _.jsx(x, {
      ...g,
      className: ge(t, `ms-gr-antd-typography-${e}`),
      copyable: y ? ut({
        text: c,
        ...E,
        tooltips: h.length > 0 ? h.map((b, v) => /* @__PURE__ */ _.jsx(I, {
          slot: b
        }, v)) : E.tooltips,
        icon: a.length > 0 ? a.map((b, v) => /* @__PURE__ */ _.jsx(I, {
          slot: b,
          clone: !0
        }, v)) : E.icon
      }) : void 0,
      editable: p ? {
        ...f,
        icon: r["editable.icon"] ? /* @__PURE__ */ _.jsx(I, {
          slot: r["editable.icon"],
          clone: !0
        }) : f.icon,
        tooltip: r["editable.tooltip"] ? /* @__PURE__ */ _.jsx(I, {
          slot: r["editable.tooltip"]
        }) : f.tooltip,
        enterIcon: r["editable.enterIcon"] ? /* @__PURE__ */ _.jsx(I, {
          slot: r["editable.enterIcon"]
        }) : f.enterIcon
      } : void 0,
      ellipsis: e === "link" ? !!w : w ? {
        ...m,
        symbol: r["ellipsis.symbol"] ? pt({
          key: "ellipsis.symbol",
          slots: r
        }, {}) : m.symbol,
        tooltip: r["ellipsis.tooltip"] ? /* @__PURE__ */ _.jsx(I, {
          slot: r["ellipsis.tooltip"]
        }) : {
          ...m.tooltip,
          title: r["ellipsis.tooltip.title"] ? /* @__PURE__ */ _.jsx(I, {
            slot: r["ellipsis.tooltip.title"]
          }) : (d = m.tooltip) == null ? void 0 : d.title
        }
      } : void 0,
      children: S.length > 0 ? u : c
    })]
  });
});
export {
  gt as TypographyBase,
  gt as default
};
