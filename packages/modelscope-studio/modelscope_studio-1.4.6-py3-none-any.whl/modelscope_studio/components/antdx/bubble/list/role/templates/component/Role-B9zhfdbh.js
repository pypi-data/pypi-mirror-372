import { i as de, a as H, r as me, m as _e, b as pe, c as ge, d as be } from "./Index-CGIRsUMG.js";
const I = window.ms_globals.React, he = window.ms_globals.React.forwardRef, ye = window.ms_globals.React.useRef, xe = window.ms_globals.React.useState, Pe = window.ms_globals.React.useEffect, Ce = window.ms_globals.internalContext.useContextPropsContext, ve = window.ms_globals.internalContext.ContextPropsProvider, Ee = window.ms_globals.ReactDOM.createPortal;
var Se = /\s/;
function Re(e) {
  for (var t = e.length; t-- && Se.test(e.charAt(t)); )
    ;
  return t;
}
var ke = /^\s+/;
function we(e) {
  return e && e.slice(0, Re(e) + 1).replace(ke, "");
}
var X = NaN, Ie = /^[-+]0x[0-9a-f]+$/i, Oe = /^0b[01]+$/i, Fe = /^0o[0-7]+$/i, Te = parseInt;
function J(e) {
  if (typeof e == "number")
    return e;
  if (de(e))
    return X;
  if (H(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = H(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = we(e);
  var n = Oe.test(e);
  return n || Fe.test(e) ? Te(e.slice(2), n ? 2 : 8) : Ie.test(e) ? X : +e;
}
var D = function() {
  return me.Date.now();
}, je = "Expected a function", Me = Math.max, Ke = Math.min;
function Le(e, t, n) {
  var s, o, r, i, l, m, b = 0, p = !1, u = !1, f = !0;
  if (typeof e != "function")
    throw new TypeError(je);
  t = J(t) || 0, H(n) && (p = !!n.leading, u = "maxWait" in n, r = u ? Me(J(n.maxWait) || 0, t) : r, f = "trailing" in n ? !!n.trailing : f);
  function a(d) {
    var x = s, P = o;
    return s = o = void 0, b = d, i = e.apply(P, x), i;
  }
  function C(d) {
    return b = d, l = setTimeout(g, t), p ? a(d) : i;
  }
  function v(d) {
    var x = d - m, P = d - b, j = t - x;
    return u ? Ke(j, r - P) : j;
  }
  function _(d) {
    var x = d - m, P = d - b;
    return m === void 0 || x >= t || x < 0 || u && P >= r;
  }
  function g() {
    var d = D();
    if (_(d))
      return y(d);
    l = setTimeout(g, v(d));
  }
  function y(d) {
    return l = void 0, f && s ? a(d) : (s = o = void 0, i);
  }
  function k() {
    l !== void 0 && clearTimeout(l), b = 0, s = m = o = l = void 0;
  }
  function E() {
    return l === void 0 ? i : y(D());
  }
  function S() {
    var d = D(), x = _(d);
    if (s = arguments, o = this, m = d, x) {
      if (l === void 0)
        return C(m);
      if (u)
        return clearTimeout(l), l = setTimeout(g, t), a(m);
    }
    return l === void 0 && (l = setTimeout(g, t)), i;
  }
  return S.cancel = k, S.flush = E, S;
}
function W() {
}
function Ne(e, ...t) {
  if (e == null) {
    for (const s of t) s(void 0);
    return W;
  }
  const n = e.subscribe(...t);
  return n.unsubscribe ? () => n.unsubscribe() : n;
}
function te(e) {
  let t;
  return Ne(e, (n) => t = n)(), t;
}
const O = [];
function R(e, t = W) {
  let n;
  const s = /* @__PURE__ */ new Set();
  function o(i) {
    if (m = i, ((l = e) != l ? m == m : l !== m || l && typeof l == "object" || typeof l == "function") && (e = i, n)) {
      const b = !O.length;
      for (const p of s) p[1](), O.push(p, e);
      if (b) {
        for (let p = 0; p < O.length; p += 2) O[p][0](O[p + 1]);
        O.length = 0;
      }
    }
    var l, m;
  }
  function r(i) {
    o(i(e));
  }
  return {
    set: o,
    update: r,
    subscribe: function(i, l = W) {
      const m = [i, l];
      return s.add(m), s.size === 1 && (n = t(o, r) || W), i(e), () => {
        s.delete(m), s.size === 0 && n && (n(), n = null);
      };
    }
  };
}
const {
  getContext: We,
  setContext: At
} = window.__gradio__svelte__internal, Ae = "$$ms-gr-loading-status-key";
function ze() {
  const e = window.ms_globals.loadingKey++, t = We(Ae);
  return (n) => {
    if (!t || !n)
      return;
    const {
      loadingStatusMap: s,
      options: o
    } = t, {
      generating: r,
      error: i
    } = te(o);
    (n == null ? void 0 : n.status) === "pending" || i && (n == null ? void 0 : n.status) === "error" || (r && (n == null ? void 0 : n.status)) === "generating" ? s.update(({
      map: l
    }) => (l.set(e, n), {
      map: l
    })) : s.update(({
      map: l
    }) => (l.delete(e), {
      map: l
    }));
  };
}
const {
  getContext: z,
  setContext: T
} = window.__gradio__svelte__internal, Be = "$$ms-gr-slots-key";
function De() {
  const e = R({});
  return T(Be, e);
}
const ne = "$$ms-gr-slot-params-mapping-fn-key";
function Ue() {
  return z(ne);
}
function He(e) {
  return T(ne, R(e));
}
const qe = "$$ms-gr-slot-params-key";
function Ge() {
  const e = T(qe, R({}));
  return (t, n) => {
    e.update((s) => typeof n == "function" ? {
      ...s,
      [t]: n(s[t])
    } : {
      ...s,
      [t]: n
    });
  };
}
const re = "$$ms-gr-sub-index-context-key";
function Ve() {
  return z(re) || null;
}
function Y(e) {
  return T(re, e);
}
function Xe(e, t, n) {
  if (!Reflect.has(e, "as_item") || !Reflect.has(e, "_internal"))
    throw new Error("`as_item` and `_internal` is required");
  const s = oe(), o = Ue();
  He().set(void 0);
  const i = Ye({
    slot: void 0,
    index: e._internal.index,
    subIndex: e._internal.subIndex
  }), l = Ve();
  typeof l == "number" && Y(void 0);
  const m = ze();
  typeof e._internal.subIndex == "number" && Y(e._internal.subIndex), s && s.subscribe((f) => {
    i.slotKey.set(f);
  }), Je();
  const b = e.as_item, p = (f, a) => f ? {
    ..._e({
      ...f
    }, t),
    __render_slotParamsMappingFn: o ? te(o) : void 0,
    __render_as_item: a,
    __render_restPropsMapping: t
  } : void 0, u = R({
    ...e,
    _internal: {
      ...e._internal,
      index: l ?? e._internal.index
    },
    restProps: p(e.restProps, b),
    originalRestProps: e.restProps
  });
  return o && o.subscribe((f) => {
    u.update((a) => ({
      ...a,
      restProps: {
        ...a.restProps,
        __slotParamsMappingFn: f
      }
    }));
  }), [u, (f) => {
    var a;
    m((a = f.restProps) == null ? void 0 : a.loading_status), u.set({
      ...f,
      _internal: {
        ...f._internal,
        index: l ?? f._internal.index
      },
      restProps: p(f.restProps, f.as_item),
      originalRestProps: f.restProps
    });
  }];
}
const se = "$$ms-gr-slot-key";
function Je() {
  T(se, R(void 0));
}
function oe() {
  return z(se);
}
const ie = "$$ms-gr-component-slot-context-key";
function Ye({
  slot: e,
  index: t,
  subIndex: n
}) {
  return T(ie, {
    slotKey: R(e),
    slotIndex: R(t),
    subSlotIndex: R(n)
  });
}
function zt() {
  return z(ie);
}
function Ze(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function Z(e, t = !1) {
  try {
    if (pe(e))
      return e;
    if (t && !Ze(e))
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
function Qe(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e;
}
var le = {
  exports: {}
}, B = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var $e = I, et = Symbol.for("react.element"), tt = Symbol.for("react.fragment"), nt = Object.prototype.hasOwnProperty, rt = $e.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, st = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ce(e, t, n) {
  var s, o = {}, r = null, i = null;
  n !== void 0 && (r = "" + n), t.key !== void 0 && (r = "" + t.key), t.ref !== void 0 && (i = t.ref);
  for (s in t) nt.call(t, s) && !st.hasOwnProperty(s) && (o[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) o[s] === void 0 && (o[s] = t[s]);
  return {
    $$typeof: et,
    type: e,
    key: r,
    ref: i,
    props: o,
    _owner: rt.current
  };
}
B.Fragment = tt;
B.jsx = ce;
B.jsxs = ce;
le.exports = B;
var K = le.exports;
const ot = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function it(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const s = e[n];
    return t[n] = lt(n, s), t;
  }, {}) : {};
}
function lt(e, t) {
  return typeof t == "number" && !ot.includes(e) ? t + "px" : t;
}
function q(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const o = I.Children.toArray(e._reactElement.props.children).map((r) => {
      if (I.isValidElement(r) && r.props.__slot__) {
        const {
          portals: i,
          clonedElement: l
        } = q(r.props.el);
        return I.cloneElement(r, {
          ...r.props,
          el: l,
          children: [...I.Children.toArray(r.props.children), ...i]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(Ee(I.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: i,
      type: l,
      useCapture: m
    }) => {
      n.addEventListener(l, i, m);
    });
  });
  const s = Array.from(e.childNodes);
  for (let o = 0; o < s.length; o++) {
    const r = s[o];
    if (r.nodeType === 1) {
      const {
        clonedElement: i,
        portals: l
      } = q(r);
      t.push(...l), n.appendChild(i);
    } else r.nodeType === 3 && n.appendChild(r.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function ct(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Q = he(({
  slot: e,
  clone: t,
  className: n,
  style: s,
  observeAttributes: o
}, r) => {
  const i = ye(), [l, m] = xe([]), {
    forceClone: b
  } = Ce(), p = b ? !0 : t;
  return Pe(() => {
    var v;
    if (!i.current || !e)
      return;
    let u = e;
    function f() {
      let _ = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (_ = u.children[0], _.tagName.toLowerCase() === "react-portal-target" && _.children[0] && (_ = _.children[0])), ct(r, _), n && _.classList.add(...n.split(" ")), s) {
        const g = it(s);
        Object.keys(g).forEach((y) => {
          _.style[y] = g[y];
        });
      }
    }
    let a = null, C = null;
    if (p && window.MutationObserver) {
      let _ = function() {
        var E, S, d;
        (E = i.current) != null && E.contains(u) && ((S = i.current) == null || S.removeChild(u));
        const {
          portals: y,
          clonedElement: k
        } = q(e);
        u = k, m(y), u.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          f();
        }, 50), (d = i.current) == null || d.appendChild(u);
      };
      _();
      const g = Le(() => {
        _(), a == null || a.disconnect(), a == null || a.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      a = new window.MutationObserver(g), a.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", f(), (v = i.current) == null || v.appendChild(u);
    return () => {
      var _, g;
      u.style.display = "", (_ = i.current) != null && _.contains(u) && ((g = i.current) == null || g.removeChild(u)), a == null || a.disconnect();
    };
  }, [e, p, n, s, r, o, b]), I.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...l);
}), at = ({
  children: e,
  ...t
}) => /* @__PURE__ */ K.jsx(K.Fragment, {
  children: e(t)
});
function ut(e) {
  return I.createElement(at, {
    children: e
  });
}
function U(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? ut((n) => /* @__PURE__ */ K.jsx(ve, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ K.jsx(Q, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...n
    })
  })) : /* @__PURE__ */ K.jsx(Q, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
var ae = {
  exports: {}
};
/*!
	Copyright (c) 2018 Jed Watson.
	Licensed under the MIT License (MIT), see
	http://jedwatson.github.io/classnames
*/
(function(e) {
  (function() {
    var t = {}.hasOwnProperty;
    function n() {
      for (var r = "", i = 0; i < arguments.length; i++) {
        var l = arguments[i];
        l && (r = o(r, s(l)));
      }
      return r;
    }
    function s(r) {
      if (typeof r == "string" || typeof r == "number")
        return r;
      if (typeof r != "object")
        return "";
      if (Array.isArray(r))
        return n.apply(null, r);
      if (r.toString !== Object.prototype.toString && !r.toString.toString().includes("[native code]"))
        return r.toString();
      var i = "";
      for (var l in r)
        t.call(r, l) && r[l] && (i = o(i, l));
      return i;
    }
    function o(r, i) {
      return i ? r ? r + " " + i : r + i : r;
    }
    e.exports ? (n.default = n, e.exports = n) : window.classNames = n;
  })();
})(ae);
var ft = ae.exports;
const dt = /* @__PURE__ */ Qe(ft), {
  SvelteComponent: mt,
  assign: G,
  check_outros: _t,
  claim_component: pt,
  component_subscribe: N,
  compute_rest_props: $,
  create_component: gt,
  create_slot: bt,
  destroy_component: ht,
  detach: ue,
  empty: A,
  exclude_internal_props: yt,
  flush: w,
  get_all_dirty_from_scope: xt,
  get_slot_changes: Pt,
  get_spread_object: Ct,
  get_spread_update: vt,
  group_outros: Et,
  handle_promise: St,
  init: Rt,
  insert_hydration: fe,
  mount_component: kt,
  noop: h,
  safe_not_equal: wt,
  transition_in: F,
  transition_out: L,
  update_await_block_branch: It,
  update_slot_base: Ot
} = window.__gradio__svelte__internal;
function Ft(e) {
  return {
    c: h,
    l: h,
    m: h,
    p: h,
    i: h,
    o: h,
    d: h
  };
}
function Tt(e) {
  let t, n;
  const s = [
    /*itemProps*/
    e[1].props,
    {
      slots: (
        /*itemProps*/
        e[1].slots
      )
    },
    {
      itemIndex: (
        /*$mergedProps*/
        e[0]._internal.index || 0
      )
    },
    {
      itemSlotKey: (
        /*$slotKey*/
        e[2]
      )
    }
  ];
  let o = {
    $$slots: {
      default: [jt]
    },
    $$scope: {
      ctx: e
    }
  };
  for (let r = 0; r < s.length; r += 1)
    o = G(o, s[r]);
  return t = new /*BubbleListRole*/
  e[23]({
    props: o
  }), {
    c() {
      gt(t.$$.fragment);
    },
    l(r) {
      pt(t.$$.fragment, r);
    },
    m(r, i) {
      kt(t, r, i), n = !0;
    },
    p(r, i) {
      const l = i & /*itemProps, $mergedProps, $slotKey*/
      7 ? vt(s, [i & /*itemProps*/
      2 && Ct(
        /*itemProps*/
        r[1].props
      ), i & /*itemProps*/
      2 && {
        slots: (
          /*itemProps*/
          r[1].slots
        )
      }, i & /*$mergedProps*/
      1 && {
        itemIndex: (
          /*$mergedProps*/
          r[0]._internal.index || 0
        )
      }, i & /*$slotKey*/
      4 && {
        itemSlotKey: (
          /*$slotKey*/
          r[2]
        )
      }]) : {};
      i & /*$$scope, $mergedProps*/
      524289 && (l.$$scope = {
        dirty: i,
        ctx: r
      }), t.$set(l);
    },
    i(r) {
      n || (F(t.$$.fragment, r), n = !0);
    },
    o(r) {
      L(t.$$.fragment, r), n = !1;
    },
    d(r) {
      ht(t, r);
    }
  };
}
function ee(e) {
  let t;
  const n = (
    /*#slots*/
    e[18].default
  ), s = bt(
    n,
    e,
    /*$$scope*/
    e[19],
    null
  );
  return {
    c() {
      s && s.c();
    },
    l(o) {
      s && s.l(o);
    },
    m(o, r) {
      s && s.m(o, r), t = !0;
    },
    p(o, r) {
      s && s.p && (!t || r & /*$$scope*/
      524288) && Ot(
        s,
        n,
        o,
        /*$$scope*/
        o[19],
        t ? Pt(
          n,
          /*$$scope*/
          o[19],
          r,
          null
        ) : xt(
          /*$$scope*/
          o[19]
        ),
        null
      );
    },
    i(o) {
      t || (F(s, o), t = !0);
    },
    o(o) {
      L(s, o), t = !1;
    },
    d(o) {
      s && s.d(o);
    }
  };
}
function jt(e) {
  let t, n, s = (
    /*$mergedProps*/
    e[0].visible && ee(e)
  );
  return {
    c() {
      s && s.c(), t = A();
    },
    l(o) {
      s && s.l(o), t = A();
    },
    m(o, r) {
      s && s.m(o, r), fe(o, t, r), n = !0;
    },
    p(o, r) {
      /*$mergedProps*/
      o[0].visible ? s ? (s.p(o, r), r & /*$mergedProps*/
      1 && F(s, 1)) : (s = ee(o), s.c(), F(s, 1), s.m(t.parentNode, t)) : s && (Et(), L(s, 1, 1, () => {
        s = null;
      }), _t());
    },
    i(o) {
      n || (F(s), n = !0);
    },
    o(o) {
      L(s), n = !1;
    },
    d(o) {
      o && ue(t), s && s.d(o);
    }
  };
}
function Mt(e) {
  return {
    c: h,
    l: h,
    m: h,
    p: h,
    i: h,
    o: h,
    d: h
  };
}
function Kt(e) {
  let t, n, s = {
    ctx: e,
    current: null,
    token: null,
    hasCatch: !1,
    pending: Mt,
    then: Tt,
    catch: Ft,
    value: 23,
    blocks: [, , ,]
  };
  return St(
    /*AwaitedBubbleListRole*/
    e[3],
    s
  ), {
    c() {
      t = A(), s.block.c();
    },
    l(o) {
      t = A(), s.block.l(o);
    },
    m(o, r) {
      fe(o, t, r), s.block.m(o, s.anchor = r), s.mount = () => t.parentNode, s.anchor = t, n = !0;
    },
    p(o, [r]) {
      e = o, It(s, e, r);
    },
    i(o) {
      n || (F(s.block), n = !0);
    },
    o(o) {
      for (let r = 0; r < 3; r += 1) {
        const i = s.blocks[r];
        L(i);
      }
      n = !1;
    },
    d(o) {
      o && ue(t), s.block.d(o), s.token = null, s = null;
    }
  };
}
function Lt(e, t, n) {
  const s = ["gradio", "props", "_internal", "as_item", "visible", "elem_id", "elem_classes", "elem_style"];
  let o = $(t, s), r, i, l, m, {
    $$slots: b = {},
    $$scope: p
  } = t;
  const u = ge(() => import("./bubble.list.role-BD18BpTN.js"));
  let {
    gradio: f
  } = t, {
    props: a = {}
  } = t;
  const C = R(a);
  N(e, C, (c) => n(17, l = c));
  let {
    _internal: v = {}
  } = t, {
    as_item: _
  } = t, {
    visible: g = !0
  } = t, {
    elem_id: y = ""
  } = t, {
    elem_classes: k = []
  } = t, {
    elem_style: E = {}
  } = t;
  const S = oe();
  N(e, S, (c) => n(2, m = c));
  const [d, x] = Xe({
    gradio: f,
    props: l,
    _internal: v,
    visible: g,
    elem_id: y,
    elem_classes: k,
    elem_style: E,
    as_item: _,
    restProps: o
  });
  N(e, d, (c) => n(0, i = c));
  const P = Ge(), j = De();
  N(e, j, (c) => n(16, r = c));
  let V = {
    props: {},
    slots: {}
  };
  return e.$$set = (c) => {
    t = G(G({}, t), yt(c)), n(22, o = $(t, s)), "gradio" in c && n(8, f = c.gradio), "props" in c && n(9, a = c.props), "_internal" in c && n(10, v = c._internal), "as_item" in c && n(11, _ = c.as_item), "visible" in c && n(12, g = c.visible), "elem_id" in c && n(13, y = c.elem_id), "elem_classes" in c && n(14, k = c.elem_classes), "elem_style" in c && n(15, E = c.elem_style), "$$scope" in c && n(19, p = c.$$scope);
  }, e.$$.update = () => {
    if (e.$$.dirty & /*props*/
    512 && C.update((c) => ({
      ...c,
      ...a
    })), x({
      gradio: f,
      props: l,
      _internal: v,
      visible: g,
      elem_id: y,
      elem_classes: k,
      elem_style: E,
      as_item: _,
      restProps: o
    }), e.$$.dirty & /*$mergedProps, $slots*/
    65537) {
      let c = i.props.avatar || i.restProps.avatar;
      r.avatar ? c = (...M) => U(r.avatar, {
        clone: !0,
        forceClone: !0,
        params: M
      }) : (r["avatar.icon"] || r["avatar.src"]) && (c = {
        ...c || {},
        icon: r["avatar.icon"] ? (...M) => U(r["avatar.icon"], {
          clone: !0,
          forceClone: !0,
          params: M
        }) : c == null ? void 0 : c.icon,
        src: r["avatar.src"] ? (...M) => U(r["avatar.src"], {
          clone: !0,
          forceClone: !0,
          params: M
        }) : c == null ? void 0 : c.src
      }), n(1, V = {
        props: {
          style: i.elem_style,
          className: dt(i.elem_classes, "ms-gr-antdx-bubble-list-role"),
          id: i.elem_id,
          ...i.restProps,
          ...i.props,
          ...be(i, {
            typing_complete: "typingComplete"
          }),
          avatar: c,
          loadingRender: Z(i.props.loadingRender || i.restProps.loadingRender),
          messageRender: Z(i.props.messageRender || i.restProps.messageRender)
        },
        slots: {
          ...r,
          "avatar.icon": void 0,
          "avatar.src": void 0,
          avatar: void 0,
          loadingRender: {
            el: r.loadingRender,
            clone: !0,
            callback: P
          },
          header: {
            el: r.header,
            clone: !0,
            callback: P
          },
          footer: {
            el: r.footer,
            clone: !0,
            callback: P
          },
          messageRender: {
            el: r.messageRender,
            clone: !0,
            callback: P
          }
        }
      });
    }
  }, [i, V, m, u, C, S, d, j, f, a, v, _, g, y, k, E, r, l, b, p];
}
class Nt extends mt {
  constructor(t) {
    super(), Rt(this, t, Lt, Kt, wt, {
      gradio: 8,
      props: 9,
      _internal: 10,
      as_item: 11,
      visible: 12,
      elem_id: 13,
      elem_classes: 14,
      elem_style: 15
    });
  }
  get gradio() {
    return this.$$.ctx[8];
  }
  set gradio(t) {
    this.$$set({
      gradio: t
    }), w();
  }
  get props() {
    return this.$$.ctx[9];
  }
  set props(t) {
    this.$$set({
      props: t
    }), w();
  }
  get _internal() {
    return this.$$.ctx[10];
  }
  set _internal(t) {
    this.$$set({
      _internal: t
    }), w();
  }
  get as_item() {
    return this.$$.ctx[11];
  }
  set as_item(t) {
    this.$$set({
      as_item: t
    }), w();
  }
  get visible() {
    return this.$$.ctx[12];
  }
  set visible(t) {
    this.$$set({
      visible: t
    }), w();
  }
  get elem_id() {
    return this.$$.ctx[13];
  }
  set elem_id(t) {
    this.$$set({
      elem_id: t
    }), w();
  }
  get elem_classes() {
    return this.$$.ctx[14];
  }
  set elem_classes(t) {
    this.$$set({
      elem_classes: t
    }), w();
  }
  get elem_style() {
    return this.$$.ctx[15];
  }
  set elem_style(t) {
    this.$$set({
      elem_style: t
    }), w();
  }
}
const Bt = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: Nt
}, Symbol.toStringTag, {
  value: "Module"
}));
export {
  Bt as R,
  R as Z,
  zt as g,
  K as j
};
