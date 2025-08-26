import { i as se, a as A, r as ie, Z as T, g as le } from "./Index-B5xEpPw5.js";
const w = window.ms_globals.React, te = window.ms_globals.React.forwardRef, ne = window.ms_globals.React.useRef, re = window.ms_globals.React.useState, oe = window.ms_globals.React.useEffect, N = window.ms_globals.ReactDOM.createPortal, ae = window.ms_globals.internalContext.useContextPropsContext, ce = window.ms_globals.antd.Layout;
var ue = /\s/;
function de(e) {
  for (var t = e.length; t-- && ue.test(e.charAt(t)); )
    ;
  return t;
}
var fe = /^\s+/;
function me(e) {
  return e && e.slice(0, de(e) + 1).replace(fe, "");
}
var M = NaN, _e = /^[-+]0x[0-9a-f]+$/i, pe = /^0b[01]+$/i, ge = /^0o[0-7]+$/i, he = parseInt;
function F(e) {
  if (typeof e == "number")
    return e;
  if (se(e))
    return M;
  if (A(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = A(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = me(e);
  var s = pe.test(e);
  return s || ge.test(e) ? he(e.slice(2), s ? 2 : 8) : _e.test(e) ? M : +e;
}
var L = function() {
  return ie.Date.now();
}, ye = "Expected a function", be = Math.max, Ee = Math.min;
function we(e, t, s) {
  var i, o, n, r, l, d, p = 0, g = !1, a = !1, h = !0;
  if (typeof e != "function")
    throw new TypeError(ye);
  t = F(t) || 0, A(s) && (g = !!s.leading, a = "maxWait" in s, n = a ? be(F(s.maxWait) || 0, t) : n, h = "trailing" in s ? !!s.trailing : h);
  function m(u) {
    var b = i, S = o;
    return i = o = void 0, p = u, r = e.apply(S, b), r;
  }
  function E(u) {
    return p = u, l = setTimeout(_, t), g ? m(u) : r;
  }
  function v(u) {
    var b = u - d, S = u - p, D = t - b;
    return a ? Ee(D, n - S) : D;
  }
  function f(u) {
    var b = u - d, S = u - p;
    return d === void 0 || b >= t || b < 0 || a && S >= n;
  }
  function _() {
    var u = L();
    if (f(u))
      return y(u);
    l = setTimeout(_, v(u));
  }
  function y(u) {
    return l = void 0, h && i ? m(u) : (i = o = void 0, r);
  }
  function I() {
    l !== void 0 && clearTimeout(l), p = 0, i = d = o = l = void 0;
  }
  function c() {
    return l === void 0 ? r : y(L());
  }
  function C() {
    var u = L(), b = f(u);
    if (i = arguments, o = this, d = u, b) {
      if (l === void 0)
        return E(d);
      if (a)
        return clearTimeout(l), l = setTimeout(_, t), m(d);
    }
    return l === void 0 && (l = setTimeout(_, t)), r;
  }
  return C.cancel = I, C.flush = c, C;
}
var X = {
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
var ve = w, Ce = Symbol.for("react.element"), xe = Symbol.for("react.fragment"), Ie = Object.prototype.hasOwnProperty, Se = ve.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Te = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Y(e, t, s) {
  var i, o = {}, n = null, r = null;
  s !== void 0 && (n = "" + s), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (i in t) Ie.call(t, i) && !Te.hasOwnProperty(i) && (o[i] = t[i]);
  if (e && e.defaultProps) for (i in t = e.defaultProps, t) o[i] === void 0 && (o[i] = t[i]);
  return {
    $$typeof: Ce,
    type: e,
    key: n,
    ref: r,
    props: o,
    _owner: Se.current
  };
}
k.Fragment = xe;
k.jsx = Y;
k.jsxs = Y;
X.exports = k;
var U = X.exports;
const {
  SvelteComponent: Re,
  assign: z,
  binding_callbacks: B,
  check_outros: Oe,
  children: Z,
  claim_element: Q,
  claim_space: ke,
  component_subscribe: G,
  compute_slots: Le,
  create_slot: Pe,
  detach: x,
  element: $,
  empty: H,
  exclude_internal_props: K,
  get_all_dirty_from_scope: Ne,
  get_slot_changes: Ae,
  group_outros: We,
  init: je,
  insert_hydration: R,
  safe_not_equal: De,
  set_custom_element_data: ee,
  space: Me,
  transition_in: O,
  transition_out: W,
  update_slot_base: Fe
} = window.__gradio__svelte__internal, {
  beforeUpdate: Ue,
  getContext: ze,
  onDestroy: Be,
  setContext: Ge
} = window.__gradio__svelte__internal;
function q(e) {
  let t, s;
  const i = (
    /*#slots*/
    e[7].default
  ), o = Pe(
    i,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = $("svelte-slot"), o && o.c(), this.h();
    },
    l(n) {
      t = Q(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = Z(t);
      o && o.l(r), r.forEach(x), this.h();
    },
    h() {
      ee(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      R(n, t, r), o && o.m(t, null), e[9](t), s = !0;
    },
    p(n, r) {
      o && o.p && (!s || r & /*$$scope*/
      64) && Fe(
        o,
        i,
        n,
        /*$$scope*/
        n[6],
        s ? Ae(
          i,
          /*$$scope*/
          n[6],
          r,
          null
        ) : Ne(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      s || (O(o, n), s = !0);
    },
    o(n) {
      W(o, n), s = !1;
    },
    d(n) {
      n && x(t), o && o.d(n), e[9](null);
    }
  };
}
function He(e) {
  let t, s, i, o, n = (
    /*$$slots*/
    e[4].default && q(e)
  );
  return {
    c() {
      t = $("react-portal-target"), s = Me(), n && n.c(), i = H(), this.h();
    },
    l(r) {
      t = Q(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), Z(t).forEach(x), s = ke(r), n && n.l(r), i = H(), this.h();
    },
    h() {
      ee(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      R(r, t, l), e[8](t), R(r, s, l), n && n.m(r, l), R(r, i, l), o = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && O(n, 1)) : (n = q(r), n.c(), O(n, 1), n.m(i.parentNode, i)) : n && (We(), W(n, 1, 1, () => {
        n = null;
      }), Oe());
    },
    i(r) {
      o || (O(n), o = !0);
    },
    o(r) {
      W(n), o = !1;
    },
    d(r) {
      r && (x(t), x(s), x(i)), e[8](null), n && n.d(r);
    }
  };
}
function V(e) {
  const {
    svelteInit: t,
    ...s
  } = e;
  return s;
}
function Ke(e, t, s) {
  let i, o, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = Le(n);
  let {
    svelteInit: d
  } = t;
  const p = T(V(t)), g = T();
  G(e, g, (c) => s(0, i = c));
  const a = T();
  G(e, a, (c) => s(1, o = c));
  const h = [], m = ze("$$ms-gr-react-wrapper"), {
    slotKey: E,
    slotIndex: v,
    subSlotIndex: f
  } = le() || {}, _ = d({
    parent: m,
    props: p,
    target: g,
    slot: a,
    slotKey: E,
    slotIndex: v,
    subSlotIndex: f,
    onDestroy(c) {
      h.push(c);
    }
  });
  Ge("$$ms-gr-react-wrapper", _), Ue(() => {
    p.set(V(t));
  }), Be(() => {
    h.forEach((c) => c());
  });
  function y(c) {
    B[c ? "unshift" : "push"](() => {
      i = c, g.set(i);
    });
  }
  function I(c) {
    B[c ? "unshift" : "push"](() => {
      o = c, a.set(o);
    });
  }
  return e.$$set = (c) => {
    s(17, t = z(z({}, t), K(c))), "svelteInit" in c && s(5, d = c.svelteInit), "$$scope" in c && s(6, r = c.$$scope);
  }, t = K(t), [i, o, g, a, l, d, r, n, y, I];
}
class qe extends Re {
  constructor(t) {
    super(), je(this, t, Ke, He, De, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: et
} = window.__gradio__svelte__internal, J = window.ms_globals.rerender, P = window.ms_globals.tree;
function Ve(e, t = {}) {
  function s(i) {
    const o = T(), n = new qe({
      ...i,
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
          }, d = r.parent ?? P;
          return d.nodes = [...d.nodes, l], J({
            createPortal: N,
            node: P
          }), r.onDestroy(() => {
            d.nodes = d.nodes.filter((p) => p.svelteInstance !== o), J({
              createPortal: N,
              node: P
            });
          }), l;
        },
        ...i.props
      }
    });
    return o.set(n), n;
  }
  return new Promise((i) => {
    window.ms_globals.initializePromise.then(() => {
      i(s);
    });
  });
}
const Je = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Xe(e) {
  return e ? Object.keys(e).reduce((t, s) => {
    const i = e[s];
    return t[s] = Ye(s, i), t;
  }, {}) : {};
}
function Ye(e, t) {
  return typeof t == "number" && !Je.includes(e) ? t + "px" : t;
}
function j(e) {
  const t = [], s = e.cloneNode(!1);
  if (e._reactElement) {
    const o = w.Children.toArray(e._reactElement.props.children).map((n) => {
      if (w.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = j(n.props.el);
        return w.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...w.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(N(w.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), s)), {
      clonedElement: s,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: r,
      type: l,
      useCapture: d
    }) => {
      s.addEventListener(l, r, d);
    });
  });
  const i = Array.from(e.childNodes);
  for (let o = 0; o < i.length; o++) {
    const n = i[o];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = j(n);
      t.push(...l), s.appendChild(r);
    } else n.nodeType === 3 && s.appendChild(n.cloneNode());
  }
  return {
    clonedElement: s,
    portals: t
  };
}
function Ze(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Qe = te(({
  slot: e,
  clone: t,
  className: s,
  style: i,
  observeAttributes: o
}, n) => {
  const r = ne(), [l, d] = re([]), {
    forceClone: p
  } = ae(), g = p ? !0 : t;
  return oe(() => {
    var v;
    if (!r.current || !e)
      return;
    let a = e;
    function h() {
      let f = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (f = a.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), Ze(n, f), s && f.classList.add(...s.split(" ")), i) {
        const _ = Xe(i);
        Object.keys(_).forEach((y) => {
          f.style[y] = _[y];
        });
      }
    }
    let m = null, E = null;
    if (g && window.MutationObserver) {
      let f = function() {
        var c, C, u;
        (c = r.current) != null && c.contains(a) && ((C = r.current) == null || C.removeChild(a));
        const {
          portals: y,
          clonedElement: I
        } = j(e);
        a = I, d(y), a.style.display = "contents", E && clearTimeout(E), E = setTimeout(() => {
          h();
        }, 50), (u = r.current) == null || u.appendChild(a);
      };
      f();
      const _ = we(() => {
        f(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      m = new window.MutationObserver(_), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", h(), (v = r.current) == null || v.appendChild(a);
    return () => {
      var f, _;
      a.style.display = "", (f = r.current) != null && f.contains(a) && ((_ = r.current) == null || _.removeChild(a)), m == null || m.disconnect();
    };
  }, [e, g, s, i, n, o, p]), w.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
}), tt = Ve(({
  slots: e,
  ...t
}) => /* @__PURE__ */ U.jsx(ce.Sider, {
  ...t,
  trigger: e.trigger ? /* @__PURE__ */ U.jsx(Qe, {
    slot: e.trigger,
    clone: !0
  }) : t.trigger === void 0 ? null : t.trigger === "default" ? void 0 : t.trigger
}));
export {
  tt as LayoutSider,
  tt as default
};
