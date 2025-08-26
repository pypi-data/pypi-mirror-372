import { m as $, i as ee } from "./Index-CKk_zu_D.js";
const D = window.ms_globals.antd.ConfigProvider, P = window.ms_globals.React;
function j() {
}
function te(t, ...e) {
  if (t == null) {
    for (const n of e) n(void 0);
    return j;
  }
  const o = t.subscribe(...e);
  return o.unsubscribe ? () => o.unsubscribe() : o;
}
function G(t) {
  let e;
  return te(t, (o) => e = o)(), e;
}
const h = [];
function g(t, e = j) {
  let o;
  const n = /* @__PURE__ */ new Set();
  function r(i) {
    if (u = i, ((l = t) != l ? u == u : l !== u || l && typeof l == "object" || typeof l == "function") && (t = i, o)) {
      const p = !h.length;
      for (const f of n) f[1](), h.push(f, t);
      if (p) {
        for (let f = 0; f < h.length; f += 2) h[f][0](h[f + 1]);
        h.length = 0;
      }
    }
    var l, u;
  }
  function s(i) {
    r(i(t));
  }
  return {
    set: r,
    update: s,
    subscribe: function(i, l = j) {
      const u = [i, l];
      return n.add(u), n.size === 1 && (o = e(r, s) || j), i(t), () => {
        n.delete(u), n.size === 0 && o && (o(), o = null);
      };
    }
  };
}
const {
  getContext: ne,
  setContext: se
} = window.__gradio__svelte__internal, oe = "$$ms-gr-config-type-key";
function re(t) {
  se(oe, t);
}
const ie = "$$ms-gr-loading-status-key";
function le() {
  const t = window.ms_globals.loadingKey++, e = ne(ie);
  return (o) => {
    if (!e || !o)
      return;
    const {
      loadingStatusMap: n,
      options: r
    } = e, {
      generating: s,
      error: i
    } = G(r);
    (o == null ? void 0 : o.status) === "pending" || i && (o == null ? void 0 : o.status) === "error" || (s && (o == null ? void 0 : o.status)) === "generating" ? n.update(({
      map: l
    }) => (l.set(t, o), {
      map: l
    })) : n.update(({
      map: l
    }) => (l.delete(t), {
      map: l
    }));
  };
}
const {
  getContext: I,
  setContext: x
} = window.__gradio__svelte__internal, ce = "$$ms-gr-slots-key";
function ae() {
  const t = g({});
  return x(ce, t);
}
const V = "$$ms-gr-slot-params-mapping-fn-key";
function ue() {
  return I(V);
}
function fe(t) {
  return x(V, g(t));
}
const me = "$$ms-gr-slot-params-key";
function _e() {
  const t = x(me, g({}));
  return (e, o) => {
    t.update((n) => typeof o == "function" ? {
      ...n,
      [e]: o(n[e])
    } : {
      ...n,
      [e]: o
    });
  };
}
const Z = "$$ms-gr-sub-index-context-key";
function de() {
  return I(Z) || null;
}
function E(t) {
  return x(Z, t);
}
function pe(t, e, o) {
  if (!Reflect.has(t, "as_item") || !Reflect.has(t, "_internal"))
    throw new Error("`as_item` and `_internal` is required");
  const n = be(), r = ue();
  fe().set(void 0);
  const i = he({
    slot: void 0,
    index: t._internal.index,
    subIndex: t._internal.subIndex
  }), l = de();
  typeof l == "number" && E(void 0);
  const u = le();
  typeof t._internal.subIndex == "number" && E(t._internal.subIndex), n && n.subscribe((a) => {
    i.slotKey.set(a);
  }), ge();
  const p = t.as_item, f = (a, _) => a ? {
    ...$({
      ...a
    }, e),
    __render_slotParamsMappingFn: r ? G(r) : void 0,
    __render_as_item: _,
    __render_restPropsMapping: e
  } : void 0, d = g({
    ...t,
    _internal: {
      ...t._internal,
      index: l ?? t._internal.index
    },
    restProps: f(t.restProps, p),
    originalRestProps: t.restProps
  });
  return r && r.subscribe((a) => {
    d.update((_) => ({
      ..._,
      restProps: {
        ..._.restProps,
        __slotParamsMappingFn: a
      }
    }));
  }), [d, (a) => {
    var _;
    u((_ = a.restProps) == null ? void 0 : _.loading_status), d.set({
      ...a,
      _internal: {
        ...a._internal,
        index: l ?? a._internal.index
      },
      restProps: f(a.restProps, a.as_item),
      originalRestProps: a.restProps
    });
  }];
}
const B = "$$ms-gr-slot-key";
function ge() {
  x(B, g(void 0));
}
function be() {
  return I(B);
}
const H = "$$ms-gr-component-slot-context-key";
function he({
  slot: t,
  index: e,
  subIndex: o
}) {
  return x(H, {
    slotKey: g(t),
    slotIndex: g(e),
    subSlotIndex: g(o)
  });
}
function Qe() {
  return I(H);
}
function T() {
  return T = Object.assign ? Object.assign.bind() : function(t) {
    for (var e = 1; e < arguments.length; e++) {
      var o = arguments[e];
      for (var n in o) ({}).hasOwnProperty.call(o, n) && (t[n] = o[n]);
    }
    return t;
  }, T.apply(null, arguments);
}
var Ue = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {};
function Pe(t) {
  return t && t.__esModule && Object.prototype.hasOwnProperty.call(t, "default") ? t.default : t;
}
var J = {
  exports: {}
};
/*!
	Copyright (c) 2018 Jed Watson.
	Licensed under the MIT License (MIT), see
	http://jedwatson.github.io/classnames
*/
(function(t) {
  (function() {
    var e = {}.hasOwnProperty;
    function o() {
      for (var s = "", i = 0; i < arguments.length; i++) {
        var l = arguments[i];
        l && (s = r(s, n(l)));
      }
      return s;
    }
    function n(s) {
      if (typeof s == "string" || typeof s == "number")
        return s;
      if (typeof s != "object")
        return "";
      if (Array.isArray(s))
        return o.apply(null, s);
      if (s.toString !== Object.prototype.toString && !s.toString.toString().includes("[native code]"))
        return s.toString();
      var i = "";
      for (var l in s)
        e.call(s, l) && s[l] && (i = r(i, l));
      return i;
    }
    function r(s, i) {
      return i ? s ? s + " " + i : s + i : s;
    }
    t.exports ? (o.default = o, t.exports = o) : window.classNames = o;
  })();
})(J);
var ye = J.exports;
const z = /* @__PURE__ */ Pe(ye), xe = /* @__PURE__ */ P.createContext({});
function ve() {
  const {
    getPrefixCls: t,
    direction: e,
    csp: o,
    iconPrefixCls: n,
    theme: r
  } = P.useContext(D.ConfigContext);
  return {
    theme: r,
    getPrefixCls: t,
    direction: e,
    csp: o,
    iconPrefixCls: n
  };
}
const Ce = (t) => {
  const {
    attachments: e,
    bubble: o,
    conversations: n,
    prompts: r,
    sender: s,
    suggestion: i,
    thoughtChain: l,
    welcome: u,
    theme: p,
    ...f
  } = t, {
    theme: d
  } = ve(), a = P.useMemo(() => ({
    attachments: e,
    bubble: o,
    conversations: n,
    prompts: r,
    sender: s,
    suggestion: i,
    thoughtChain: l,
    welcome: u
  }), [e, o, n, r, s, i, l, u]), _ = P.useMemo(() => ({
    ...d,
    ...p
  }), [d, p]);
  return /* @__PURE__ */ P.createElement(xe.Provider, {
    value: a
  }, /* @__PURE__ */ P.createElement(D, T({}, f, {
    // Note:  we can not set `cssVar` by default.
    //        Since when developer not wrap with XProvider,
    //        the generate css is still using css var but no css var injected.
    // Origin comment: antdx enable cssVar by default, and antd v6 will enable cssVar by default
    // theme={{ cssVar: true, ...antdConfProps?.theme }}
    theme: _
  })));
}, {
  SvelteComponent: ke,
  assign: X,
  check_outros: Se,
  claim_component: Me,
  component_subscribe: O,
  compute_rest_props: A,
  create_component: Ke,
  create_slot: Fe,
  destroy_component: je,
  detach: Q,
  empty: w,
  exclude_internal_props: we,
  flush: b,
  get_all_dirty_from_scope: Ie,
  get_slot_changes: Oe,
  get_spread_object: q,
  get_spread_update: Te,
  group_outros: Xe,
  handle_promise: Re,
  init: Ne,
  insert_hydration: U,
  mount_component: Ee,
  noop: m,
  safe_not_equal: ze,
  transition_in: y,
  transition_out: C,
  update_await_block_branch: Ae,
  update_slot_base: qe
} = window.__gradio__svelte__internal;
function L(t) {
  let e, o, n = {
    ctx: t,
    current: null,
    token: null,
    hasCatch: !1,
    pending: Ve,
    then: De,
    catch: Le,
    value: 20,
    blocks: [, , ,]
  };
  return Re(
    /*AwaitedXProvider*/
    t[2],
    n
  ), {
    c() {
      e = w(), n.block.c();
    },
    l(r) {
      e = w(), n.block.l(r);
    },
    m(r, s) {
      U(r, e, s), n.block.m(r, n.anchor = s), n.mount = () => e.parentNode, n.anchor = e, o = !0;
    },
    p(r, s) {
      t = r, Ae(n, t, s);
    },
    i(r) {
      o || (y(n.block), o = !0);
    },
    o(r) {
      for (let s = 0; s < 3; s += 1) {
        const i = n.blocks[s];
        C(i);
      }
      o = !1;
    },
    d(r) {
      r && Q(e), n.block.d(r), n.token = null, n = null;
    }
  };
}
function Le(t) {
  return {
    c: m,
    l: m,
    m,
    p: m,
    i: m,
    o: m,
    d: m
  };
}
function De(t) {
  let e, o;
  const n = [
    {
      className: z(
        "ms-gr-antdx-x-provider",
        /*$mergedProps*/
        t[0].elem_classes
      )
    },
    {
      id: (
        /*$mergedProps*/
        t[0].elem_id
      )
    },
    {
      style: (
        /*$mergedProps*/
        t[0].elem_style
      )
    },
    /*$mergedProps*/
    t[0].restProps,
    /*$mergedProps*/
    t[0].props,
    {
      slots: (
        /*$slots*/
        t[1]
      )
    },
    {
      component: Ce
    },
    {
      themeMode: (
        /*$mergedProps*/
        t[0].gradio.theme
      )
    },
    {
      setSlotParams: (
        /*setSlotParams*/
        t[5]
      )
    }
  ];
  let r = {
    $$slots: {
      default: [Ge]
    },
    $$scope: {
      ctx: t
    }
  };
  for (let s = 0; s < n.length; s += 1)
    r = X(r, n[s]);
  return e = new /*XProvider*/
  t[20]({
    props: r
  }), {
    c() {
      Ke(e.$$.fragment);
    },
    l(s) {
      Me(e.$$.fragment, s);
    },
    m(s, i) {
      Ee(e, s, i), o = !0;
    },
    p(s, i) {
      const l = i & /*$mergedProps, $slots, setSlotParams*/
      35 ? Te(n, [i & /*$mergedProps*/
      1 && {
        className: z(
          "ms-gr-antdx-x-provider",
          /*$mergedProps*/
          s[0].elem_classes
        )
      }, i & /*$mergedProps*/
      1 && {
        id: (
          /*$mergedProps*/
          s[0].elem_id
        )
      }, i & /*$mergedProps*/
      1 && {
        style: (
          /*$mergedProps*/
          s[0].elem_style
        )
      }, i & /*$mergedProps*/
      1 && q(
        /*$mergedProps*/
        s[0].restProps
      ), i & /*$mergedProps*/
      1 && q(
        /*$mergedProps*/
        s[0].props
      ), i & /*$slots*/
      2 && {
        slots: (
          /*$slots*/
          s[1]
        )
      }, n[6], i & /*$mergedProps*/
      1 && {
        themeMode: (
          /*$mergedProps*/
          s[0].gradio.theme
        )
      }, i & /*setSlotParams*/
      32 && {
        setSlotParams: (
          /*setSlotParams*/
          s[5]
        )
      }]) : {};
      i & /*$$scope*/
      131072 && (l.$$scope = {
        dirty: i,
        ctx: s
      }), e.$set(l);
    },
    i(s) {
      o || (y(e.$$.fragment, s), o = !0);
    },
    o(s) {
      C(e.$$.fragment, s), o = !1;
    },
    d(s) {
      je(e, s);
    }
  };
}
function Ge(t) {
  let e;
  const o = (
    /*#slots*/
    t[16].default
  ), n = Fe(
    o,
    t,
    /*$$scope*/
    t[17],
    null
  );
  return {
    c() {
      n && n.c();
    },
    l(r) {
      n && n.l(r);
    },
    m(r, s) {
      n && n.m(r, s), e = !0;
    },
    p(r, s) {
      n && n.p && (!e || s & /*$$scope*/
      131072) && qe(
        n,
        o,
        r,
        /*$$scope*/
        r[17],
        e ? Oe(
          o,
          /*$$scope*/
          r[17],
          s,
          null
        ) : Ie(
          /*$$scope*/
          r[17]
        ),
        null
      );
    },
    i(r) {
      e || (y(n, r), e = !0);
    },
    o(r) {
      C(n, r), e = !1;
    },
    d(r) {
      n && n.d(r);
    }
  };
}
function Ve(t) {
  return {
    c: m,
    l: m,
    m,
    p: m,
    i: m,
    o: m,
    d: m
  };
}
function Ze(t) {
  let e, o, n = (
    /*$mergedProps*/
    t[0].visible && L(t)
  );
  return {
    c() {
      n && n.c(), e = w();
    },
    l(r) {
      n && n.l(r), e = w();
    },
    m(r, s) {
      n && n.m(r, s), U(r, e, s), o = !0;
    },
    p(r, [s]) {
      /*$mergedProps*/
      r[0].visible ? n ? (n.p(r, s), s & /*$mergedProps*/
      1 && y(n, 1)) : (n = L(r), n.c(), y(n, 1), n.m(e.parentNode, e)) : n && (Xe(), C(n, 1, 1, () => {
        n = null;
      }), Se());
    },
    i(r) {
      o || (y(n), o = !0);
    },
    o(r) {
      C(n), o = !1;
    },
    d(r) {
      r && Q(e), n && n.d(r);
    }
  };
}
function Be(t, e, o) {
  const n = ["gradio", "props", "as_item", "visible", "elem_id", "elem_classes", "elem_style", "_internal"];
  let r = A(e, n), s, i, l, {
    $$slots: u = {},
    $$scope: p
  } = e;
  const f = ee(() => import("./config-provider-rXQnJyjg.js").then((c) => c.f));
  let {
    gradio: d
  } = e, {
    props: a = {}
  } = e;
  const _ = g(a);
  O(t, _, (c) => o(15, s = c));
  let {
    as_item: v
  } = e, {
    visible: k = !0
  } = e, {
    elem_id: S = ""
  } = e, {
    elem_classes: M = []
  } = e, {
    elem_style: K = {}
  } = e, {
    _internal: F = {}
  } = e;
  const [R, W] = pe({
    gradio: d,
    props: s,
    visible: k,
    _internal: F,
    elem_id: S,
    elem_classes: M,
    elem_style: K,
    as_item: v,
    restProps: r
  });
  O(t, R, (c) => o(0, i = c));
  const Y = _e(), N = ae();
  return O(t, N, (c) => o(1, l = c)), re("antd"), t.$$set = (c) => {
    e = X(X({}, e), we(c)), o(19, r = A(e, n)), "gradio" in c && o(7, d = c.gradio), "props" in c && o(8, a = c.props), "as_item" in c && o(9, v = c.as_item), "visible" in c && o(10, k = c.visible), "elem_id" in c && o(11, S = c.elem_id), "elem_classes" in c && o(12, M = c.elem_classes), "elem_style" in c && o(13, K = c.elem_style), "_internal" in c && o(14, F = c._internal), "$$scope" in c && o(17, p = c.$$scope);
  }, t.$$.update = () => {
    t.$$.dirty & /*props*/
    256 && _.update((c) => ({
      ...c,
      ...a
    })), W({
      gradio: d,
      props: s,
      visible: k,
      _internal: F,
      elem_id: S,
      elem_classes: M,
      elem_style: K,
      as_item: v,
      restProps: r
    });
  }, [i, l, f, _, R, Y, N, d, a, v, k, S, M, K, F, s, u, p];
}
class He extends ke {
  constructor(e) {
    super(), Ne(this, e, Be, Ze, ze, {
      gradio: 7,
      props: 8,
      as_item: 9,
      visible: 10,
      elem_id: 11,
      elem_classes: 12,
      elem_style: 13,
      _internal: 14
    });
  }
  get gradio() {
    return this.$$.ctx[7];
  }
  set gradio(e) {
    this.$$set({
      gradio: e
    }), b();
  }
  get props() {
    return this.$$.ctx[8];
  }
  set props(e) {
    this.$$set({
      props: e
    }), b();
  }
  get as_item() {
    return this.$$.ctx[9];
  }
  set as_item(e) {
    this.$$set({
      as_item: e
    }), b();
  }
  get visible() {
    return this.$$.ctx[10];
  }
  set visible(e) {
    this.$$set({
      visible: e
    }), b();
  }
  get elem_id() {
    return this.$$.ctx[11];
  }
  set elem_id(e) {
    this.$$set({
      elem_id: e
    }), b();
  }
  get elem_classes() {
    return this.$$.ctx[12];
  }
  set elem_classes(e) {
    this.$$set({
      elem_classes: e
    }), b();
  }
  get elem_style() {
    return this.$$.ctx[13];
  }
  set elem_style(e) {
    this.$$set({
      elem_style: e
    }), b();
  }
  get _internal() {
    return this.$$.ctx[14];
  }
  set _internal(e) {
    this.$$set({
      _internal: e
    }), b();
  }
}
const We = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  default: He
}, Symbol.toStringTag, {
  value: "Module"
}));
export {
  We as X,
  g as Z,
  Pe as a,
  Ue as c,
  Qe as g
};
