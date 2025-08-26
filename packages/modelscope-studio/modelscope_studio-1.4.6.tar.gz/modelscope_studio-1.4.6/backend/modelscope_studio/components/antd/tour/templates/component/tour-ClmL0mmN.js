import { i as me, a as A, r as _e, Z as T, g as he, b as pe } from "./Index-DkoVcS8X.js";
const v = window.ms_globals.React, ae = window.ms_globals.React.forwardRef, ue = window.ms_globals.React.useRef, de = window.ms_globals.React.useState, fe = window.ms_globals.React.useEffect, ee = window.ms_globals.React.useMemo, W = window.ms_globals.ReactDOM.createPortal, ge = window.ms_globals.internalContext.useContextPropsContext, M = window.ms_globals.internalContext.ContextPropsProvider, xe = window.ms_globals.antd.Tour, we = window.ms_globals.createItemsContext.createItemsContext;
var be = /\s/;
function ye(e) {
  for (var t = e.length; t-- && be.test(e.charAt(t)); )
    ;
  return t;
}
var ve = /^\s+/;
function Ee(e) {
  return e && e.slice(0, ye(e) + 1).replace(ve, "");
}
var H = NaN, Ce = /^[-+]0x[0-9a-f]+$/i, Ie = /^0b[01]+$/i, Se = /^0o[0-7]+$/i, Re = parseInt;
function z(e) {
  if (typeof e == "number")
    return e;
  if (me(e))
    return H;
  if (A(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = A(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Ee(e);
  var s = Ie.test(e);
  return s || Se.test(e) ? Re(e.slice(2), s ? 2 : 8) : Ce.test(e) ? H : +e;
}
var F = function() {
  return _e.Date.now();
}, Pe = "Expected a function", Te = Math.max, ke = Math.min;
function Oe(e, t, s) {
  var l, r, n, o, i, d, h = 0, p = !1, c = !1, g = !0;
  if (typeof e != "function")
    throw new TypeError(Pe);
  t = z(t) || 0, A(s) && (p = !!s.leading, c = "maxWait" in s, n = c ? Te(z(s.maxWait) || 0, t) : n, g = "trailing" in s ? !!s.trailing : g);
  function u(_) {
    var E = l, R = r;
    return l = r = void 0, h = _, o = e.apply(R, E), o;
  }
  function w(_) {
    return h = _, i = setTimeout(m, t), p ? u(_) : o;
  }
  function b(_) {
    var E = _ - d, R = _ - h, B = t - E;
    return c ? ke(B, n - R) : B;
  }
  function a(_) {
    var E = _ - d, R = _ - h;
    return d === void 0 || E >= t || E < 0 || c && R >= n;
  }
  function m() {
    var _ = F();
    if (a(_))
      return y(_);
    i = setTimeout(m, b(_));
  }
  function y(_) {
    return i = void 0, g && l ? u(_) : (l = r = void 0, o);
  }
  function S() {
    i !== void 0 && clearTimeout(i), h = 0, l = d = r = i = void 0;
  }
  function f() {
    return i === void 0 ? o : y(F());
  }
  function C() {
    var _ = F(), E = a(_);
    if (l = arguments, r = this, d = _, E) {
      if (i === void 0)
        return w(d);
      if (c)
        return clearTimeout(i), i = setTimeout(m, t), u(d);
    }
    return i === void 0 && (i = setTimeout(m, t)), o;
  }
  return C.cancel = S, C.flush = f, C;
}
var te = {
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
var je = v, Fe = Symbol.for("react.element"), Le = Symbol.for("react.fragment"), Ne = Object.prototype.hasOwnProperty, We = je.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ae = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ne(e, t, s) {
  var l, r = {}, n = null, o = null;
  s !== void 0 && (n = "" + s), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (l in t) Ne.call(t, l) && !Ae.hasOwnProperty(l) && (r[l] = t[l]);
  if (e && e.defaultProps) for (l in t = e.defaultProps, t) r[l] === void 0 && (r[l] = t[l]);
  return {
    $$typeof: Fe,
    type: e,
    key: n,
    ref: o,
    props: r,
    _owner: We.current
  };
}
j.Fragment = Le;
j.jsx = ne;
j.jsxs = ne;
te.exports = j;
var x = te.exports;
const {
  SvelteComponent: Me,
  assign: G,
  binding_callbacks: q,
  check_outros: De,
  children: re,
  claim_element: oe,
  claim_space: Ue,
  component_subscribe: V,
  compute_slots: Be,
  create_slot: He,
  detach: I,
  element: se,
  empty: J,
  exclude_internal_props: X,
  get_all_dirty_from_scope: ze,
  get_slot_changes: Ge,
  group_outros: qe,
  init: Ve,
  insert_hydration: k,
  safe_not_equal: Je,
  set_custom_element_data: le,
  space: Xe,
  transition_in: O,
  transition_out: D,
  update_slot_base: Ye
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ze,
  getContext: Ke,
  onDestroy: Qe,
  setContext: $e
} = window.__gradio__svelte__internal;
function Y(e) {
  let t, s;
  const l = (
    /*#slots*/
    e[7].default
  ), r = He(
    l,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = se("svelte-slot"), r && r.c(), this.h();
    },
    l(n) {
      t = oe(n, "SVELTE-SLOT", {
        class: !0
      });
      var o = re(t);
      r && r.l(o), o.forEach(I), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      k(n, t, o), r && r.m(t, null), e[9](t), s = !0;
    },
    p(n, o) {
      r && r.p && (!s || o & /*$$scope*/
      64) && Ye(
        r,
        l,
        n,
        /*$$scope*/
        n[6],
        s ? Ge(
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
      s || (O(r, n), s = !0);
    },
    o(n) {
      D(r, n), s = !1;
    },
    d(n) {
      n && I(t), r && r.d(n), e[9](null);
    }
  };
}
function et(e) {
  let t, s, l, r, n = (
    /*$$slots*/
    e[4].default && Y(e)
  );
  return {
    c() {
      t = se("react-portal-target"), s = Xe(), n && n.c(), l = J(), this.h();
    },
    l(o) {
      t = oe(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), re(t).forEach(I), s = Ue(o), n && n.l(o), l = J(), this.h();
    },
    h() {
      le(t, "class", "svelte-1rt0kpf");
    },
    m(o, i) {
      k(o, t, i), e[8](t), k(o, s, i), n && n.m(o, i), k(o, l, i), r = !0;
    },
    p(o, [i]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, i), i & /*$$slots*/
      16 && O(n, 1)) : (n = Y(o), n.c(), O(n, 1), n.m(l.parentNode, l)) : n && (qe(), D(n, 1, 1, () => {
        n = null;
      }), De());
    },
    i(o) {
      r || (O(n), r = !0);
    },
    o(o) {
      D(n), r = !1;
    },
    d(o) {
      o && (I(t), I(s), I(l)), e[8](null), n && n.d(o);
    }
  };
}
function Z(e) {
  const {
    svelteInit: t,
    ...s
  } = e;
  return s;
}
function tt(e, t, s) {
  let l, r, {
    $$slots: n = {},
    $$scope: o
  } = t;
  const i = Be(n);
  let {
    svelteInit: d
  } = t;
  const h = T(Z(t)), p = T();
  V(e, p, (f) => s(0, l = f));
  const c = T();
  V(e, c, (f) => s(1, r = f));
  const g = [], u = Ke("$$ms-gr-react-wrapper"), {
    slotKey: w,
    slotIndex: b,
    subSlotIndex: a
  } = he() || {}, m = d({
    parent: u,
    props: h,
    target: p,
    slot: c,
    slotKey: w,
    slotIndex: b,
    subSlotIndex: a,
    onDestroy(f) {
      g.push(f);
    }
  });
  $e("$$ms-gr-react-wrapper", m), Ze(() => {
    h.set(Z(t));
  }), Qe(() => {
    g.forEach((f) => f());
  });
  function y(f) {
    q[f ? "unshift" : "push"](() => {
      l = f, p.set(l);
    });
  }
  function S(f) {
    q[f ? "unshift" : "push"](() => {
      r = f, c.set(r);
    });
  }
  return e.$$set = (f) => {
    s(17, t = G(G({}, t), X(f))), "svelteInit" in f && s(5, d = f.svelteInit), "$$scope" in f && s(6, o = f.$$scope);
  }, t = X(t), [l, r, p, c, i, d, o, n, y, S];
}
class nt extends Me {
  constructor(t) {
    super(), Ve(this, t, tt, et, Je, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: _t
} = window.__gradio__svelte__internal, K = window.ms_globals.rerender, L = window.ms_globals.tree;
function rt(e, t = {}) {
  function s(l) {
    const r = T(), n = new nt({
      ...l,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const i = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: e,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, d = o.parent ?? L;
          return d.nodes = [...d.nodes, i], K({
            createPortal: W,
            node: L
          }), o.onDestroy(() => {
            d.nodes = d.nodes.filter((h) => h.svelteInstance !== r), K({
              createPortal: W,
              node: L
            });
          }), i;
        },
        ...l.props
      }
    });
    return r.set(n), n;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise.then(() => {
      l(s);
    });
  });
}
const ot = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function st(e) {
  return e ? Object.keys(e).reduce((t, s) => {
    const l = e[s];
    return t[s] = lt(s, l), t;
  }, {}) : {};
}
function lt(e, t) {
  return typeof t == "number" && !ot.includes(e) ? t + "px" : t;
}
function U(e) {
  const t = [], s = e.cloneNode(!1);
  if (e._reactElement) {
    const r = v.Children.toArray(e._reactElement.props.children).map((n) => {
      if (v.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: i
        } = U(n.props.el);
        return v.cloneElement(n, {
          ...n.props,
          el: i,
          children: [...v.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return r.originalChildren = e._reactElement.props.children, t.push(W(v.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: r
    }), s)), {
      clonedElement: s,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((r) => {
    e.getEventListeners(r).forEach(({
      listener: o,
      type: i,
      useCapture: d
    }) => {
      s.addEventListener(i, o, d);
    });
  });
  const l = Array.from(e.childNodes);
  for (let r = 0; r < l.length; r++) {
    const n = l[r];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: i
      } = U(n);
      t.push(...i), s.appendChild(o);
    } else n.nodeType === 3 && s.appendChild(n.cloneNode());
  }
  return {
    clonedElement: s,
    portals: t
  };
}
function it(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const P = ae(({
  slot: e,
  clone: t,
  className: s,
  style: l,
  observeAttributes: r
}, n) => {
  const o = ue(), [i, d] = de([]), {
    forceClone: h
  } = ge(), p = h ? !0 : t;
  return fe(() => {
    var b;
    if (!o.current || !e)
      return;
    let c = e;
    function g() {
      let a = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (a = c.children[0], a.tagName.toLowerCase() === "react-portal-target" && a.children[0] && (a = a.children[0])), it(n, a), s && a.classList.add(...s.split(" ")), l) {
        const m = st(l);
        Object.keys(m).forEach((y) => {
          a.style[y] = m[y];
        });
      }
    }
    let u = null, w = null;
    if (p && window.MutationObserver) {
      let a = function() {
        var f, C, _;
        (f = o.current) != null && f.contains(c) && ((C = o.current) == null || C.removeChild(c));
        const {
          portals: y,
          clonedElement: S
        } = U(e);
        c = S, d(y), c.style.display = "contents", w && clearTimeout(w), w = setTimeout(() => {
          g();
        }, 50), (_ = o.current) == null || _.appendChild(c);
      };
      a();
      const m = Oe(() => {
        a(), u == null || u.disconnect(), u == null || u.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      u = new window.MutationObserver(m), u.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", g(), (b = o.current) == null || b.appendChild(c);
    return () => {
      var a, m;
      c.style.display = "", (a = o.current) != null && a.contains(c) && ((m = o.current) == null || m.removeChild(c)), u == null || u.disconnect();
    };
  }, [e, p, s, l, n, r, h]), v.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...i);
});
function ct(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function at(e, t = !1) {
  try {
    if (pe(e))
      return e;
    if (t && !ct(e))
      return;
    if (typeof e == "string") {
      let s = e.trim();
      return s.startsWith(";") && (s = s.slice(1)), s.endsWith(";") && (s = s.slice(0, -1)), new Function(`return (...args) => (${s})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function N(e, t) {
  return ee(() => at(e, t), [e, t]);
}
const ut = ({
  children: e,
  ...t
}) => /* @__PURE__ */ x.jsx(x.Fragment, {
  children: e(t)
});
function ie(e) {
  return v.createElement(ut, {
    children: e
  });
}
function ce(e, t, s) {
  const l = e.filter(Boolean);
  if (l.length !== 0)
    return l.map((r, n) => {
      var h;
      if (typeof r != "object")
        return r;
      const o = {
        ...r.props,
        key: ((h = r.props) == null ? void 0 : h.key) ?? (s ? `${s}-${n}` : `${n}`)
      };
      let i = o;
      Object.keys(r.slots).forEach((p) => {
        if (!r.slots[p] || !(r.slots[p] instanceof Element) && !r.slots[p].el)
          return;
        const c = p.split(".");
        c.forEach((m, y) => {
          i[m] || (i[m] = {}), y !== c.length - 1 && (i = o[m]);
        });
        const g = r.slots[p];
        let u, w, b = !1, a = t == null ? void 0 : t.forceClone;
        g instanceof Element ? u = g : (u = g.el, w = g.callback, b = g.clone ?? b, a = g.forceClone ?? a), a = a ?? !!w, i[c[c.length - 1]] = u ? w ? (...m) => (w(c[c.length - 1], m), /* @__PURE__ */ x.jsx(M, {
          ...r.ctx,
          params: m,
          forceClone: a,
          children: /* @__PURE__ */ x.jsx(P, {
            slot: u,
            clone: b
          })
        })) : ie((m) => /* @__PURE__ */ x.jsx(M, {
          ...r.ctx,
          forceClone: a,
          children: /* @__PURE__ */ x.jsx(P, {
            ...m,
            slot: u,
            clone: b
          })
        })) : i[c[c.length - 1]], i = o;
      });
      const d = "children";
      return r[d] && (o[d] = ce(r[d], t, `${n}`)), o;
    });
}
function Q(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ie((s) => /* @__PURE__ */ x.jsx(M, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ x.jsx(P, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...s
    })
  })) : /* @__PURE__ */ x.jsx(P, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function $({
  key: e,
  slots: t,
  targets: s
}, l) {
  return t[e] ? (...r) => s ? s.map((n, o) => /* @__PURE__ */ x.jsx(v.Fragment, {
    children: Q(n, {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ x.jsx(x.Fragment, {
    children: Q(t[e], {
      clone: !0,
      params: r,
      forceClone: !0
    })
  }) : void 0;
}
const {
  withItemsContextProvider: dt,
  useItems: ft,
  ItemHandler: ht
} = we("antd-tour-items"), pt = rt(dt(["steps", "default"], ({
  slots: e,
  steps: t,
  children: s,
  onChange: l,
  onClose: r,
  getPopupContainer: n,
  setSlotParams: o,
  indicatorsRender: i,
  actionsRender: d,
  ...h
}) => {
  const p = N(n), c = N(i), g = N(d), {
    items: u
  } = ft(), w = u.steps.length > 0 ? u.steps : u.default;
  return /* @__PURE__ */ x.jsxs(x.Fragment, {
    children: [/* @__PURE__ */ x.jsx("div", {
      style: {
        display: "none"
      },
      children: s
    }), /* @__PURE__ */ x.jsx(xe, {
      ...h,
      steps: ee(() => t || ce(w), [t, w]),
      onChange: (b) => {
        l == null || l(b);
      },
      closeIcon: e.closeIcon ? /* @__PURE__ */ x.jsx(P, {
        slot: e.closeIcon
      }) : h.closeIcon,
      actionsRender: e.actionsRender ? $({
        slots: e,
        key: "actionsRender"
      }) : g,
      indicatorsRender: e.indicatorsRender ? $({
        slots: e,
        key: "indicatorsRender"
      }) : c,
      getPopupContainer: p,
      onClose: (b, ...a) => {
        r == null || r(b, ...a);
      }
    })]
  });
}));
export {
  pt as Tour,
  pt as default
};
