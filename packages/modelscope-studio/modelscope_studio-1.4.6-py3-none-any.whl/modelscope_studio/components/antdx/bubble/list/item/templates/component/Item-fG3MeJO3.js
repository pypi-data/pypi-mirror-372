import { i as ae, a as D, r as ue, m as fe, b as de, c as me, d as pe } from "./Index-B1Twn3kd.js";
const w = window.ms_globals.React, _e = window.ms_globals.React.forwardRef, ge = window.ms_globals.React.useRef, be = window.ms_globals.React.useState, he = window.ms_globals.React.useEffect, ye = window.ms_globals.internalContext.useContextPropsContext, xe = window.ms_globals.ReactDOM.createPortal;
var Pe = /\s/;
function Ce(e) {
  for (var t = e.length; t-- && Pe.test(e.charAt(t)); )
    ;
  return t;
}
var ve = /^\s+/;
function Ee(e) {
  return e && e.slice(0, Ce(e) + 1).replace(ve, "");
}
var G = NaN, Se = /^[-+]0x[0-9a-f]+$/i, Re = /^0b[01]+$/i, ke = /^0o[0-7]+$/i, Ie = parseInt;
function V(e) {
  if (typeof e == "number")
    return e;
  if (ae(e))
    return G;
  if (D(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = D(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Ee(e);
  var r = Re.test(e);
  return r || ke.test(e) ? Ie(e.slice(2), r ? 2 : 8) : Se.test(e) ? G : +e;
}
var z = function() {
  return ue.Date.now();
}, we = "Expected a function", Oe = Math.max, Fe = Math.min;
function Te(e, t, r) {
  var s, o, n, i, l, m, b = 0, _ = !1, u = !1, f = !0;
  if (typeof e != "function")
    throw new TypeError(we);
  t = V(t) || 0, D(r) && (_ = !!r.leading, u = "maxWait" in r, n = u ? Oe(V(r.maxWait) || 0, t) : n, f = "trailing" in r ? !!r.trailing : f);
  function a(d) {
    var x = s, P = o;
    return s = o = void 0, b = d, i = e.apply(P, x), i;
  }
  function C(d) {
    return b = d, l = setTimeout(g, t), _ ? a(d) : i;
  }
  function v(d) {
    var x = d - m, P = d - b, M = t - x;
    return u ? Fe(M, n - P) : M;
  }
  function p(d) {
    var x = d - m, P = d - b;
    return m === void 0 || x >= t || x < 0 || u && P >= n;
  }
  function g() {
    var d = z();
    if (p(d))
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
    return l === void 0 ? i : y(z());
  }
  function S() {
    var d = z(), x = p(d);
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
function L() {
}
function Me(e, ...t) {
  if (e == null) {
    for (const s of t) s(void 0);
    return L;
  }
  const r = e.subscribe(...t);
  return r.unsubscribe ? () => r.unsubscribe() : r;
}
function Q(e) {
  let t;
  return Me(e, (r) => t = r)(), t;
}
const O = [];
function R(e, t = L) {
  let r;
  const s = /* @__PURE__ */ new Set();
  function o(i) {
    if (m = i, ((l = e) != l ? m == m : l !== m || l && typeof l == "object" || typeof l == "function") && (e = i, r)) {
      const b = !O.length;
      for (const _ of s) _[1](), O.push(_, e);
      if (b) {
        for (let _ = 0; _ < O.length; _ += 2) O[_][0](O[_ + 1]);
        O.length = 0;
      }
    }
    var l, m;
  }
  function n(i) {
    o(i(e));
  }
  return {
    set: o,
    update: n,
    subscribe: function(i, l = L) {
      const m = [i, l];
      return s.add(m), s.size === 1 && (r = t(o, n) || L), i(e), () => {
        s.delete(m), s.size === 0 && r && (r(), r = null);
      };
    }
  };
}
const {
  getContext: je,
  setContext: Kt
} = window.__gradio__svelte__internal, Ke = "$$ms-gr-loading-status-key";
function Le() {
  const e = window.ms_globals.loadingKey++, t = je(Ke);
  return (r) => {
    if (!t || !r)
      return;
    const {
      loadingStatusMap: s,
      options: o
    } = t, {
      generating: n,
      error: i
    } = Q(o);
    (r == null ? void 0 : r.status) === "pending" || i && (r == null ? void 0 : r.status) === "error" || (n && (r == null ? void 0 : r.status)) === "generating" ? s.update(({
      map: l
    }) => (l.set(e, r), {
      map: l
    })) : s.update(({
      map: l
    }) => (l.delete(e), {
      map: l
    }));
  };
}
const {
  getContext: A,
  setContext: T
} = window.__gradio__svelte__internal, Ne = "$$ms-gr-slots-key";
function Ae() {
  const e = R({});
  return T(Ne, e);
}
const $ = "$$ms-gr-slot-params-mapping-fn-key";
function We() {
  return A($);
}
function ze(e) {
  return T($, R(e));
}
const Be = "$$ms-gr-slot-params-key";
function De() {
  const e = T(Be, R({}));
  return (t, r) => {
    e.update((s) => typeof r == "function" ? {
      ...s,
      [t]: r(s[t])
    } : {
      ...s,
      [t]: r
    });
  };
}
const ee = "$$ms-gr-sub-index-context-key";
function Ue() {
  return A(ee) || null;
}
function X(e) {
  return T(ee, e);
}
function He(e, t, r) {
  if (!Reflect.has(e, "as_item") || !Reflect.has(e, "_internal"))
    throw new Error("`as_item` and `_internal` is required");
  const s = ne(), o = We();
  ze().set(void 0);
  const i = Ge({
    slot: void 0,
    index: e._internal.index,
    subIndex: e._internal.subIndex
  }), l = Ue();
  typeof l == "number" && X(void 0);
  const m = Le();
  typeof e._internal.subIndex == "number" && X(e._internal.subIndex), s && s.subscribe((f) => {
    i.slotKey.set(f);
  }), qe();
  const b = e.as_item, _ = (f, a) => f ? {
    ...fe({
      ...f
    }, t),
    __render_slotParamsMappingFn: o ? Q(o) : void 0,
    __render_as_item: a,
    __render_restPropsMapping: t
  } : void 0, u = R({
    ...e,
    _internal: {
      ...e._internal,
      index: l ?? e._internal.index
    },
    restProps: _(e.restProps, b),
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
      restProps: _(f.restProps, f.as_item),
      originalRestProps: f.restProps
    });
  }];
}
const te = "$$ms-gr-slot-key";
function qe() {
  T(te, R(void 0));
}
function ne() {
  return A(te);
}
const re = "$$ms-gr-component-slot-context-key";
function Ge({
  slot: e,
  index: t,
  subIndex: r
}) {
  return T(re, {
    slotKey: R(e),
    slotIndex: R(t),
    subSlotIndex: R(r)
  });
}
function Lt() {
  return A(re);
}
function Ve(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function J(e, t = !1) {
  try {
    if (de(e))
      return e;
    if (t && !Ve(e))
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
function Xe(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e;
}
var se = {
  exports: {}
}, W = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Je = w, Ye = Symbol.for("react.element"), Ze = Symbol.for("react.fragment"), Qe = Object.prototype.hasOwnProperty, $e = Je.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, et = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function oe(e, t, r) {
  var s, o = {}, n = null, i = null;
  r !== void 0 && (n = "" + r), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (i = t.ref);
  for (s in t) Qe.call(t, s) && !et.hasOwnProperty(s) && (o[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) o[s] === void 0 && (o[s] = t[s]);
  return {
    $$typeof: Ye,
    type: e,
    key: n,
    ref: i,
    props: o,
    _owner: $e.current
  };
}
W.Fragment = Ze;
W.jsx = oe;
W.jsxs = oe;
se.exports = W;
var tt = se.exports;
const nt = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function rt(e) {
  return e ? Object.keys(e).reduce((t, r) => {
    const s = e[r];
    return t[r] = st(r, s), t;
  }, {}) : {};
}
function st(e, t) {
  return typeof t == "number" && !nt.includes(e) ? t + "px" : t;
}
function U(e) {
  const t = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const o = w.Children.toArray(e._reactElement.props.children).map((n) => {
      if (w.isValidElement(n) && n.props.__slot__) {
        const {
          portals: i,
          clonedElement: l
        } = U(n.props.el);
        return w.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...w.Children.toArray(n.props.children), ...i]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(xe(w.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), r)), {
      clonedElement: r,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: i,
      type: l,
      useCapture: m
    }) => {
      r.addEventListener(l, i, m);
    });
  });
  const s = Array.from(e.childNodes);
  for (let o = 0; o < s.length; o++) {
    const n = s[o];
    if (n.nodeType === 1) {
      const {
        clonedElement: i,
        portals: l
      } = U(n);
      t.push(...l), r.appendChild(i);
    } else n.nodeType === 3 && r.appendChild(n.cloneNode());
  }
  return {
    clonedElement: r,
    portals: t
  };
}
function ot(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const it = _e(({
  slot: e,
  clone: t,
  className: r,
  style: s,
  observeAttributes: o
}, n) => {
  const i = ge(), [l, m] = be([]), {
    forceClone: b
  } = ye(), _ = b ? !0 : t;
  return he(() => {
    var v;
    if (!i.current || !e)
      return;
    let u = e;
    function f() {
      let p = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (p = u.children[0], p.tagName.toLowerCase() === "react-portal-target" && p.children[0] && (p = p.children[0])), ot(n, p), r && p.classList.add(...r.split(" ")), s) {
        const g = rt(s);
        Object.keys(g).forEach((y) => {
          p.style[y] = g[y];
        });
      }
    }
    let a = null, C = null;
    if (_ && window.MutationObserver) {
      let p = function() {
        var E, S, d;
        (E = i.current) != null && E.contains(u) && ((S = i.current) == null || S.removeChild(u));
        const {
          portals: y,
          clonedElement: k
        } = U(e);
        u = k, m(y), u.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          f();
        }, 50), (d = i.current) == null || d.appendChild(u);
      };
      p();
      const g = Te(() => {
        p(), a == null || a.disconnect(), a == null || a.observe(e, {
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
      var p, g;
      u.style.display = "", (p = i.current) != null && p.contains(u) && ((g = i.current) == null || g.removeChild(u)), a == null || a.disconnect();
    };
  }, [e, _, r, s, n, o, b]), w.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...l);
});
function B(e, t) {
  return e ? /* @__PURE__ */ tt.jsx(it, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
var ie = {
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
    function r() {
      for (var n = "", i = 0; i < arguments.length; i++) {
        var l = arguments[i];
        l && (n = o(n, s(l)));
      }
      return n;
    }
    function s(n) {
      if (typeof n == "string" || typeof n == "number")
        return n;
      if (typeof n != "object")
        return "";
      if (Array.isArray(n))
        return r.apply(null, n);
      if (n.toString !== Object.prototype.toString && !n.toString.toString().includes("[native code]"))
        return n.toString();
      var i = "";
      for (var l in n)
        t.call(n, l) && n[l] && (i = o(i, l));
      return i;
    }
    function o(n, i) {
      return i ? n ? n + " " + i : n + i : n;
    }
    e.exports ? (r.default = r, e.exports = r) : window.classNames = r;
  })();
})(ie);
var lt = ie.exports;
const ct = /* @__PURE__ */ Xe(lt), {
  SvelteComponent: at,
  assign: H,
  check_outros: ut,
  claim_component: ft,
  component_subscribe: K,
  compute_rest_props: Y,
  create_component: dt,
  create_slot: mt,
  destroy_component: pt,
  detach: le,
  empty: N,
  exclude_internal_props: _t,
  flush: I,
  get_all_dirty_from_scope: gt,
  get_slot_changes: bt,
  get_spread_object: ht,
  get_spread_update: yt,
  group_outros: xt,
  handle_promise: Pt,
  init: Ct,
  insert_hydration: ce,
  mount_component: vt,
  noop: h,
  safe_not_equal: Et,
  transition_in: F,
  transition_out: j,
  update_await_block_branch: St,
  update_slot_base: Rt
} = window.__gradio__svelte__internal;
function kt(e) {
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
function It(e) {
  let t, r;
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
      default: [wt]
    },
    $$scope: {
      ctx: e
    }
  };
  for (let n = 0; n < s.length; n += 1)
    o = H(o, s[n]);
  return t = new /*BubbleListItem*/
  e[23]({
    props: o
  }), {
    c() {
      dt(t.$$.fragment);
    },
    l(n) {
      ft(t.$$.fragment, n);
    },
    m(n, i) {
      vt(t, n, i), r = !0;
    },
    p(n, i) {
      const l = i & /*itemProps, $mergedProps, $slotKey*/
      7 ? yt(s, [i & /*itemProps*/
      2 && ht(
        /*itemProps*/
        n[1].props
      ), i & /*itemProps*/
      2 && {
        slots: (
          /*itemProps*/
          n[1].slots
        )
      }, i & /*$mergedProps*/
      1 && {
        itemIndex: (
          /*$mergedProps*/
          n[0]._internal.index || 0
        )
      }, i & /*$slotKey*/
      4 && {
        itemSlotKey: (
          /*$slotKey*/
          n[2]
        )
      }]) : {};
      i & /*$$scope, $mergedProps*/
      524289 && (l.$$scope = {
        dirty: i,
        ctx: n
      }), t.$set(l);
    },
    i(n) {
      r || (F(t.$$.fragment, n), r = !0);
    },
    o(n) {
      j(t.$$.fragment, n), r = !1;
    },
    d(n) {
      pt(t, n);
    }
  };
}
function Z(e) {
  let t;
  const r = (
    /*#slots*/
    e[18].default
  ), s = mt(
    r,
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
    m(o, n) {
      s && s.m(o, n), t = !0;
    },
    p(o, n) {
      s && s.p && (!t || n & /*$$scope*/
      524288) && Rt(
        s,
        r,
        o,
        /*$$scope*/
        o[19],
        t ? bt(
          r,
          /*$$scope*/
          o[19],
          n,
          null
        ) : gt(
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
      j(s, o), t = !1;
    },
    d(o) {
      s && s.d(o);
    }
  };
}
function wt(e) {
  let t, r, s = (
    /*$mergedProps*/
    e[0].visible && Z(e)
  );
  return {
    c() {
      s && s.c(), t = N();
    },
    l(o) {
      s && s.l(o), t = N();
    },
    m(o, n) {
      s && s.m(o, n), ce(o, t, n), r = !0;
    },
    p(o, n) {
      /*$mergedProps*/
      o[0].visible ? s ? (s.p(o, n), n & /*$mergedProps*/
      1 && F(s, 1)) : (s = Z(o), s.c(), F(s, 1), s.m(t.parentNode, t)) : s && (xt(), j(s, 1, 1, () => {
        s = null;
      }), ut());
    },
    i(o) {
      r || (F(s), r = !0);
    },
    o(o) {
      j(s), r = !1;
    },
    d(o) {
      o && le(t), s && s.d(o);
    }
  };
}
function Ot(e) {
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
function Ft(e) {
  let t, r, s = {
    ctx: e,
    current: null,
    token: null,
    hasCatch: !1,
    pending: Ot,
    then: It,
    catch: kt,
    value: 23,
    blocks: [, , ,]
  };
  return Pt(
    /*AwaitedBubbleListItem*/
    e[3],
    s
  ), {
    c() {
      t = N(), s.block.c();
    },
    l(o) {
      t = N(), s.block.l(o);
    },
    m(o, n) {
      ce(o, t, n), s.block.m(o, s.anchor = n), s.mount = () => t.parentNode, s.anchor = t, r = !0;
    },
    p(o, [n]) {
      e = o, St(s, e, n);
    },
    i(o) {
      r || (F(s.block), r = !0);
    },
    o(o) {
      for (let n = 0; n < 3; n += 1) {
        const i = s.blocks[n];
        j(i);
      }
      r = !1;
    },
    d(o) {
      o && le(t), s.block.d(o), s.token = null, s = null;
    }
  };
}
function Tt(e, t, r) {
  const s = ["gradio", "props", "_internal", "as_item", "visible", "elem_id", "elem_classes", "elem_style"];
  let o = Y(t, s), n, i, l, m, {
    $$slots: b = {},
    $$scope: _
  } = t;
  const u = me(() => import("./bubble.list.item-CKALsN7z.js"));
  let {
    gradio: f
  } = t, {
    props: a = {}
  } = t;
  const C = R(a);
  K(e, C, (c) => r(17, l = c));
  let {
    _internal: v = {}
  } = t, {
    as_item: p
  } = t, {
    visible: g = !0
  } = t, {
    elem_id: y = ""
  } = t, {
    elem_classes: k = []
  } = t, {
    elem_style: E = {}
  } = t;
  const S = ne();
  K(e, S, (c) => r(2, m = c));
  const [d, x] = He({
    gradio: f,
    props: l,
    _internal: v,
    visible: g,
    elem_id: y,
    elem_classes: k,
    elem_style: E,
    as_item: p,
    restProps: o
  });
  K(e, d, (c) => r(0, i = c));
  const P = De(), M = Ae();
  K(e, M, (c) => r(16, n = c));
  let q = {
    props: {},
    slots: {}
  };
  return e.$$set = (c) => {
    t = H(H({}, t), _t(c)), r(22, o = Y(t, s)), "gradio" in c && r(8, f = c.gradio), "props" in c && r(9, a = c.props), "_internal" in c && r(10, v = c._internal), "as_item" in c && r(11, p = c.as_item), "visible" in c && r(12, g = c.visible), "elem_id" in c && r(13, y = c.elem_id), "elem_classes" in c && r(14, k = c.elem_classes), "elem_style" in c && r(15, E = c.elem_style), "$$scope" in c && r(19, _ = c.$$scope);
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
      as_item: p,
      restProps: o
    }), e.$$.dirty & /*$mergedProps, $slots*/
    65537) {
      let c = i.props.avatar || i.restProps.avatar;
      n.avatar ? c = B(n.avatar) : (n["avatar.icon"] || n["avatar.src"]) && (c = {
        ...c || {},
        icon: n["avatar.icon"] ? B(n["avatar.icon"]) : c == null ? void 0 : c.icon,
        src: n["avatar.src"] ? B(n["avatar.src"]) : c == null ? void 0 : c.src
      }), r(1, q = {
        props: {
          style: i.elem_style,
          className: ct(i.elem_classes, "ms-gr-antdx-bubble-list-role"),
          id: i.elem_id,
          ...i.restProps,
          ...i.props,
          ...pe(i, {
            typing_complete: "typingComplete"
          }),
          avatar: c,
          loadingRender: J(i.props.loadingRender || i.restProps.loadingRender),
          messageRender: J(i.props.messageRender || i.restProps.messageRender)
        },
        slots: {
          ...n,
          avatar: void 0,
          "avatar.icon": void 0,
          "avatar.src": void 0,
          header: {
            el: n.header,
            callback: P
          },
          footer: {
            el: n.footer,
            callback: P
          },
          loadingRender: {
            el: n.loadingRender,
            callback: P
          },
          messageRender: {
            el: n.messageRender,
            callback: P
          }
        }
      });
    }
  }, [i, q, m, u, C, S, d, M, f, a, v, p, g, y, k, E, n, l, b, _];
}
class Mt extends at {
  constructor(t) {
    super(), Ct(this, t, Tt, Ft, Et, {
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
    }), I();
  }
  get props() {
    return this.$$.ctx[9];
  }
  set props(t) {
    this.$$set({
      props: t
    }), I();
  }
  get _internal() {
    return this.$$.ctx[10];
  }
  set _internal(t) {
    this.$$set({
      _internal: t
    }), I();
  }
  get as_item() {
    return this.$$.ctx[11];
  }
  set as_item(t) {
    this.$$set({
      as_item: t
    }), I();
  }
  get visible() {
    return this.$$.ctx[12];
  }
  set visible(t) {
    this.$$set({
      visible: t
    }), I();
  }
  get elem_id() {
    return this.$$.ctx[13];
  }
  set elem_id(t) {
    this.$$set({
      elem_id: t
    }), I();
  }
  get elem_classes() {
    return this.$$.ctx[14];
  }
  set elem_classes(t) {
    this.$$set({
      elem_classes: t
    }), I();
  }
  get elem_style() {
    return this.$$.ctx[15];
  }
  set elem_style(t) {
    this.$$set({
      elem_style: t
    }), I();
  }
}
const Nt = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: Mt
}, Symbol.toStringTag, {
  value: "Module"
}));
export {
  Nt as I,
  R as Z,
  Lt as g,
  tt as j
};
