import { i as ae, a as M, r as ue, b as de, Z as R, g as fe } from "./Index-0qmCfruT.js";
const y = window.ms_globals.React, ce = window.ms_globals.React.forwardRef, A = window.ms_globals.React.useRef, $ = window.ms_globals.React.useState, F = window.ms_globals.React.useEffect, ie = window.ms_globals.React.useMemo, W = window.ms_globals.ReactDOM.createPortal, me = window.ms_globals.internalContext.useContextPropsContext, B = window.ms_globals.internalContext.ContextPropsProvider, _e = window.ms_globals.antd.Cascader, he = window.ms_globals.createItemsContext.createItemsContext;
var pe = /\s/;
function ge(t) {
  for (var e = t.length; e-- && pe.test(t.charAt(e)); )
    ;
  return e;
}
var be = /^\s+/;
function xe(t) {
  return t && t.slice(0, ge(t) + 1).replace(be, "");
}
var H = NaN, Ce = /^[-+]0x[0-9a-f]+$/i, Ee = /^0b[01]+$/i, we = /^0o[0-7]+$/i, ye = parseInt;
function q(t) {
  if (typeof t == "number")
    return t;
  if (ae(t))
    return H;
  if (M(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = M(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = xe(t);
  var o = Ee.test(t);
  return o || we.test(t) ? ye(t.slice(2), o ? 2 : 8) : Ce.test(t) ? H : +t;
}
var L = function() {
  return ue.Date.now();
}, ve = "Expected a function", Ie = Math.max, Se = Math.min;
function Pe(t, e, o) {
  var s, l, n, r, c, a, h = 0, b = !1, i = !1, p = !0;
  if (typeof t != "function")
    throw new TypeError(ve);
  e = q(e) || 0, M(o) && (b = !!o.leading, i = "maxWait" in o, n = i ? Ie(q(o.maxWait) || 0, e) : n, p = "trailing" in o ? !!o.trailing : p);
  function u(m) {
    var w = s, P = l;
    return s = l = void 0, h = m, r = t.apply(P, w), r;
  }
  function x(m) {
    return h = m, c = setTimeout(_, e), b ? u(m) : r;
  }
  function E(m) {
    var w = m - a, P = m - h, U = e - w;
    return i ? Se(U, n - P) : U;
  }
  function d(m) {
    var w = m - a, P = m - h;
    return a === void 0 || w >= e || w < 0 || i && P >= n;
  }
  function _() {
    var m = L();
    if (d(m))
      return g(m);
    c = setTimeout(_, E(m));
  }
  function g(m) {
    return c = void 0, p && s ? u(m) : (s = l = void 0, r);
  }
  function v() {
    c !== void 0 && clearTimeout(c), h = 0, s = a = l = c = void 0;
  }
  function f() {
    return c === void 0 ? r : g(L());
  }
  function I() {
    var m = L(), w = d(m);
    if (s = arguments, l = this, a = m, w) {
      if (c === void 0)
        return x(a);
      if (i)
        return clearTimeout(c), c = setTimeout(_, e), u(a);
    }
    return c === void 0 && (c = setTimeout(_, e)), r;
  }
  return I.cancel = v, I.flush = f, I;
}
function Re(t, e) {
  return de(t, e);
}
var ee = {
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
var Te = y, ke = Symbol.for("react.element"), Oe = Symbol.for("react.fragment"), je = Object.prototype.hasOwnProperty, Le = Te.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ne = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function te(t, e, o) {
  var s, l = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), e.key !== void 0 && (n = "" + e.key), e.ref !== void 0 && (r = e.ref);
  for (s in e) je.call(e, s) && !Ne.hasOwnProperty(s) && (l[s] = e[s]);
  if (t && t.defaultProps) for (s in e = t.defaultProps, e) l[s] === void 0 && (l[s] = e[s]);
  return {
    $$typeof: ke,
    type: t,
    key: n,
    ref: r,
    props: l,
    _owner: Le.current
  };
}
j.Fragment = Oe;
j.jsx = te;
j.jsxs = te;
ee.exports = j;
var C = ee.exports;
const {
  SvelteComponent: Ae,
  assign: z,
  binding_callbacks: G,
  check_outros: Fe,
  children: ne,
  claim_element: re,
  claim_space: We,
  component_subscribe: J,
  compute_slots: Me,
  create_slot: De,
  detach: S,
  element: le,
  empty: X,
  exclude_internal_props: Y,
  get_all_dirty_from_scope: Ve,
  get_slot_changes: Ue,
  group_outros: Be,
  init: He,
  insert_hydration: T,
  safe_not_equal: qe,
  set_custom_element_data: oe,
  space: ze,
  transition_in: k,
  transition_out: D,
  update_slot_base: Ge
} = window.__gradio__svelte__internal, {
  beforeUpdate: Je,
  getContext: Xe,
  onDestroy: Ye,
  setContext: Ze
} = window.__gradio__svelte__internal;
function Z(t) {
  let e, o;
  const s = (
    /*#slots*/
    t[7].default
  ), l = De(
    s,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = le("svelte-slot"), l && l.c(), this.h();
    },
    l(n) {
      e = re(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = ne(e);
      l && l.l(r), r.forEach(S), this.h();
    },
    h() {
      oe(e, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      T(n, e, r), l && l.m(e, null), t[9](e), o = !0;
    },
    p(n, r) {
      l && l.p && (!o || r & /*$$scope*/
      64) && Ge(
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
        ) : Ve(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (k(l, n), o = !0);
    },
    o(n) {
      D(l, n), o = !1;
    },
    d(n) {
      n && S(e), l && l.d(n), t[9](null);
    }
  };
}
function Ke(t) {
  let e, o, s, l, n = (
    /*$$slots*/
    t[4].default && Z(t)
  );
  return {
    c() {
      e = le("react-portal-target"), o = ze(), n && n.c(), s = X(), this.h();
    },
    l(r) {
      e = re(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), ne(e).forEach(S), o = We(r), n && n.l(r), s = X(), this.h();
    },
    h() {
      oe(e, "class", "svelte-1rt0kpf");
    },
    m(r, c) {
      T(r, e, c), t[8](e), T(r, o, c), n && n.m(r, c), T(r, s, c), l = !0;
    },
    p(r, [c]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, c), c & /*$$slots*/
      16 && k(n, 1)) : (n = Z(r), n.c(), k(n, 1), n.m(s.parentNode, s)) : n && (Be(), D(n, 1, 1, () => {
        n = null;
      }), Fe());
    },
    i(r) {
      l || (k(n), l = !0);
    },
    o(r) {
      D(n), l = !1;
    },
    d(r) {
      r && (S(e), S(o), S(s)), t[8](null), n && n.d(r);
    }
  };
}
function K(t) {
  const {
    svelteInit: e,
    ...o
  } = t;
  return o;
}
function Qe(t, e, o) {
  let s, l, {
    $$slots: n = {},
    $$scope: r
  } = e;
  const c = Me(n);
  let {
    svelteInit: a
  } = e;
  const h = R(K(e)), b = R();
  J(t, b, (f) => o(0, s = f));
  const i = R();
  J(t, i, (f) => o(1, l = f));
  const p = [], u = Xe("$$ms-gr-react-wrapper"), {
    slotKey: x,
    slotIndex: E,
    subSlotIndex: d
  } = fe() || {}, _ = a({
    parent: u,
    props: h,
    target: b,
    slot: i,
    slotKey: x,
    slotIndex: E,
    subSlotIndex: d,
    onDestroy(f) {
      p.push(f);
    }
  });
  Ze("$$ms-gr-react-wrapper", _), Je(() => {
    h.set(K(e));
  }), Ye(() => {
    p.forEach((f) => f());
  });
  function g(f) {
    G[f ? "unshift" : "push"](() => {
      s = f, b.set(s);
    });
  }
  function v(f) {
    G[f ? "unshift" : "push"](() => {
      l = f, i.set(l);
    });
  }
  return t.$$set = (f) => {
    o(17, e = z(z({}, e), Y(f))), "svelteInit" in f && o(5, a = f.svelteInit), "$$scope" in f && o(6, r = f.$$scope);
  }, e = Y(e), [s, l, b, i, c, a, r, n, g, v];
}
class $e extends Ae {
  constructor(e) {
    super(), He(this, e, Qe, Ke, qe, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: dt
} = window.__gradio__svelte__internal, Q = window.ms_globals.rerender, N = window.ms_globals.tree;
function et(t, e = {}) {
  function o(s) {
    const l = R(), n = new $e({
      ...s,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: l,
            reactComponent: t,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: e.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, a = r.parent ?? N;
          return a.nodes = [...a.nodes, c], Q({
            createPortal: W,
            node: N
          }), r.onDestroy(() => {
            a.nodes = a.nodes.filter((h) => h.svelteInstance !== l), Q({
              createPortal: W,
              node: N
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
function nt(t) {
  return t ? Object.keys(t).reduce((e, o) => {
    const s = t[o];
    return e[o] = rt(o, s), e;
  }, {}) : {};
}
function rt(t, e) {
  return typeof e == "number" && !tt.includes(t) ? e + "px" : e;
}
function V(t) {
  const e = [], o = t.cloneNode(!1);
  if (t._reactElement) {
    const l = y.Children.toArray(t._reactElement.props.children).map((n) => {
      if (y.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: c
        } = V(n.props.el);
        return y.cloneElement(n, {
          ...n.props,
          el: c,
          children: [...y.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return l.originalChildren = t._reactElement.props.children, e.push(W(y.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: l
    }), o)), {
      clonedElement: o,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((l) => {
    t.getEventListeners(l).forEach(({
      listener: r,
      type: c,
      useCapture: a
    }) => {
      o.addEventListener(c, r, a);
    });
  });
  const s = Array.from(t.childNodes);
  for (let l = 0; l < s.length; l++) {
    const n = s[l];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: c
      } = V(n);
      e.push(...c), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: e
  };
}
function lt(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const O = ce(({
  slot: t,
  clone: e,
  className: o,
  style: s,
  observeAttributes: l
}, n) => {
  const r = A(), [c, a] = $([]), {
    forceClone: h
  } = me(), b = h ? !0 : e;
  return F(() => {
    var E;
    if (!r.current || !t)
      return;
    let i = t;
    function p() {
      let d = i;
      if (i.tagName.toLowerCase() === "svelte-slot" && i.children.length === 1 && i.children[0] && (d = i.children[0], d.tagName.toLowerCase() === "react-portal-target" && d.children[0] && (d = d.children[0])), lt(n, d), o && d.classList.add(...o.split(" ")), s) {
        const _ = nt(s);
        Object.keys(_).forEach((g) => {
          d.style[g] = _[g];
        });
      }
    }
    let u = null, x = null;
    if (b && window.MutationObserver) {
      let d = function() {
        var f, I, m;
        (f = r.current) != null && f.contains(i) && ((I = r.current) == null || I.removeChild(i));
        const {
          portals: g,
          clonedElement: v
        } = V(t);
        i = v, a(g), i.style.display = "contents", x && clearTimeout(x), x = setTimeout(() => {
          p();
        }, 50), (m = r.current) == null || m.appendChild(i);
      };
      d();
      const _ = Pe(() => {
        d(), u == null || u.disconnect(), u == null || u.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: l
        });
      }, 50);
      u = new window.MutationObserver(_), u.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      i.style.display = "contents", p(), (E = r.current) == null || E.appendChild(i);
    return () => {
      var d, _;
      i.style.display = "", (d = r.current) != null && d.contains(i) && ((_ = r.current) == null || _.removeChild(i)), u == null || u.disconnect();
    };
  }, [t, b, o, s, n, l, h]), y.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...c);
});
function ot({
  value: t,
  onValueChange: e
}) {
  const [o, s] = $(t), l = A(e);
  l.current = e;
  const n = A(o);
  return n.current = o, F(() => {
    l.current(o);
  }, [o]), F(() => {
    Re(t, n.current) || s(t);
  }, [t]), [o, s];
}
const st = ({
  children: t,
  ...e
}) => /* @__PURE__ */ C.jsx(C.Fragment, {
  children: t(e)
});
function ct(t) {
  return y.createElement(st, {
    children: t
  });
}
function se(t, e, o) {
  const s = t.filter(Boolean);
  if (s.length !== 0)
    return s.map((l, n) => {
      var h, b;
      if (typeof l != "object")
        return e != null && e.fallback ? e.fallback(l) : l;
      const r = e != null && e.itemPropsTransformer ? e == null ? void 0 : e.itemPropsTransformer({
        ...l.props,
        key: ((h = l.props) == null ? void 0 : h.key) ?? (o ? `${o}-${n}` : `${n}`)
      }) : {
        ...l.props,
        key: ((b = l.props) == null ? void 0 : b.key) ?? (o ? `${o}-${n}` : `${n}`)
      };
      let c = r;
      Object.keys(l.slots).forEach((i) => {
        if (!l.slots[i] || !(l.slots[i] instanceof Element) && !l.slots[i].el)
          return;
        const p = i.split(".");
        p.forEach((g, v) => {
          c[g] || (c[g] = {}), v !== p.length - 1 && (c = r[g]);
        });
        const u = l.slots[i];
        let x, E, d = (e == null ? void 0 : e.clone) ?? !1, _ = e == null ? void 0 : e.forceClone;
        u instanceof Element ? x = u : (x = u.el, E = u.callback, d = u.clone ?? d, _ = u.forceClone ?? _), _ = _ ?? !!E, c[p[p.length - 1]] = x ? E ? (...g) => (E(p[p.length - 1], g), /* @__PURE__ */ C.jsx(B, {
          ...l.ctx,
          params: g,
          forceClone: _,
          children: /* @__PURE__ */ C.jsx(O, {
            slot: x,
            clone: d
          })
        })) : ct((g) => /* @__PURE__ */ C.jsx(B, {
          ...l.ctx,
          forceClone: _,
          children: /* @__PURE__ */ C.jsx(O, {
            ...g,
            slot: x,
            clone: d
          })
        })) : c[p[p.length - 1]], c = r;
      });
      const a = (e == null ? void 0 : e.children) || "children";
      return l[a] ? r[a] = se(l[a], e, `${n}`) : e != null && e.children && (r[a] = void 0, Reflect.deleteProperty(r, a)), r;
    });
}
const {
  useItems: it,
  withItemsContextProvider: at,
  ItemHandler: ft
} = he("antd-cascader-options"), mt = et(at(["default", "options"], ({
  slots: t,
  children: e,
  onValueChange: o,
  onChange: s,
  onLoadData: l,
  options: n,
  ...r
}) => {
  const [c, a] = ot({
    onValueChange: o,
    value: r.value
  }), {
    items: h
  } = it(), b = h.options.length > 0 ? h.options : h.default;
  return /* @__PURE__ */ C.jsxs(C.Fragment, {
    children: [/* @__PURE__ */ C.jsx("div", {
      style: {
        display: "none"
      },
      children: e
    }), /* @__PURE__ */ C.jsx(_e.Panel, {
      ...r,
      value: c,
      options: ie(() => n || se(b, {
        clone: !0
      }), [n, b]),
      loadData: l,
      onChange: (i, ...p) => {
        s == null || s(i, ...p), a(i);
      },
      expandIcon: t.expandIcon ? /* @__PURE__ */ C.jsx(O, {
        slot: t.expandIcon
      }) : r.expandIcon,
      notFoundContent: t.notFoundContent ? /* @__PURE__ */ C.jsx(O, {
        slot: t.notFoundContent
      }) : r.notFoundContent
    })]
  });
}));
export {
  mt as CascaderPanel,
  mt as default
};
