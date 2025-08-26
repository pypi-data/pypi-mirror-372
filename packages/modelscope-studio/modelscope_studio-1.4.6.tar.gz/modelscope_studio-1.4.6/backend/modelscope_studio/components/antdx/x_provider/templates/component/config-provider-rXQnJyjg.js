import { Z as L, g as vt, a as Be, c as xt } from "./XProvider-Cvj7sJYT.js";
import { a as Ct, b as de, r as kt, c as Et } from "./Index-CKk_zu_D.js";
const k = window.ms_globals.React, gt = window.ms_globals.React.forwardRef, wt = window.ms_globals.React.useRef, Ye = window.ms_globals.React.useState, qe = window.ms_globals.React.useEffect, bt = window.ms_globals.React.useMemo, ue = window.ms_globals.ReactDOM.createPortal, St = window.ms_globals.internalContext.useContextPropsContext, jt = window.ms_globals.internalContext.ContextPropsProvider, Ot = window.ms_globals.antdCssinjs.StyleProvider, Tt = window.ms_globals.antd.ConfigProvider, Se = window.ms_globals.antd.theme, Ge = window.ms_globals.dayjs;
function He(t, e) {
  for (var r = 0; r < e.length; r++) {
    const n = e[r];
    if (typeof n != "string" && !Array.isArray(n)) {
      for (const a in n)
        if (a !== "default" && !(a in t)) {
          const o = Object.getOwnPropertyDescriptor(n, a);
          o && Object.defineProperty(t, a, o.get ? o : {
            enumerable: !0,
            get: () => n[a]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(t, Symbol.toStringTag, {
    value: "Module"
  }));
}
var Rt = /\s/;
function It(t) {
  for (var e = t.length; e-- && Rt.test(t.charAt(e)); )
    ;
  return e;
}
var Ft = /^\s+/;
function zt(t) {
  return t && t.slice(0, It(t) + 1).replace(Ft, "");
}
var je = NaN, Dt = /^[-+]0x[0-9a-f]+$/i, Mt = /^0b[01]+$/i, At = /^0o[0-7]+$/i, Nt = parseInt;
function Ce(t) {
  if (typeof t == "number")
    return t;
  if (Ct(t))
    return je;
  if (de(t)) {
    var e = typeof t.valueOf == "function" ? t.valueOf() : t;
    t = de(e) ? e + "" : e;
  }
  if (typeof t != "string")
    return t === 0 ? t : +t;
  t = zt(t);
  var r = Mt.test(t);
  return r || At.test(t) ? Nt(t.slice(2), r ? 2 : 8) : Dt.test(t) ? je : +t;
}
var oe = function() {
  return kt.Date.now();
}, $t = "Expected a function", Ut = Math.max, Lt = Math.min;
function Kt(t, e, r) {
  var n, a, o, i, s, l, p = 0, y = !1, c = !1, h = !0;
  if (typeof t != "function")
    throw new TypeError($t);
  e = Ce(e) || 0, de(r) && (y = !!r.leading, c = "maxWait" in r, o = c ? Ut(Ce(r.maxWait) || 0, e) : o, h = "trailing" in r ? !!r.trailing : h);
  function m(d) {
    var E = n, M = a;
    return n = a = void 0, p = d, i = t.apply(M, E), i;
  }
  function C(d) {
    return p = d, s = setTimeout(_, e), y ? m(d) : i;
  }
  function j(d) {
    var E = d - l, M = d - p, xe = e - E;
    return c ? Lt(xe, o - M) : xe;
  }
  function f(d) {
    var E = d - l, M = d - p;
    return l === void 0 || E >= e || E < 0 || c && M >= o;
  }
  function _() {
    var d = oe();
    if (f(d))
      return x(d);
    s = setTimeout(_, j(d));
  }
  function x(d) {
    return s = void 0, h && n ? m(d) : (n = a = void 0, i);
  }
  function O() {
    s !== void 0 && clearTimeout(s), p = 0, n = l = a = s = void 0;
  }
  function u() {
    return s === void 0 ? i : x(oe());
  }
  function b() {
    var d = oe(), E = f(d);
    if (n = arguments, a = this, l = d, E) {
      if (s === void 0)
        return C(l);
      if (c)
        return clearTimeout(s), s = setTimeout(_, e), m(l);
    }
    return s === void 0 && (s = setTimeout(_, e)), i;
  }
  return b.cancel = O, b.flush = u, b;
}
var Je = {
  exports: {}
}, G = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Wt = k, Yt = Symbol.for("react.element"), qt = Symbol.for("react.fragment"), Bt = Object.prototype.hasOwnProperty, Gt = Wt.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Ht = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Qe(t, e, r) {
  var n, a = {}, o = null, i = null;
  r !== void 0 && (o = "" + r), e.key !== void 0 && (o = "" + e.key), e.ref !== void 0 && (i = e.ref);
  for (n in e) Bt.call(e, n) && !Ht.hasOwnProperty(n) && (a[n] = e[n]);
  if (t && t.defaultProps) for (n in e = t.defaultProps, e) a[n] === void 0 && (a[n] = e[n]);
  return {
    $$typeof: Yt,
    type: t,
    key: o,
    ref: i,
    props: a,
    _owner: Gt.current
  };
}
G.Fragment = qt;
G.jsx = Qe;
G.jsxs = Qe;
Je.exports = G;
var v = Je.exports;
const {
  SvelteComponent: Jt,
  assign: ke,
  binding_callbacks: Ee,
  check_outros: Qt,
  children: Ze,
  claim_element: Xe,
  claim_space: Zt,
  component_subscribe: Oe,
  compute_slots: Xt,
  create_slot: Vt,
  detach: F,
  element: Ve,
  empty: Te,
  exclude_internal_props: Re,
  get_all_dirty_from_scope: er,
  get_slot_changes: tr,
  group_outros: rr,
  init: nr,
  insert_hydration: K,
  safe_not_equal: ar,
  set_custom_element_data: et,
  space: or,
  transition_in: W,
  transition_out: fe,
  update_slot_base: ir
} = window.__gradio__svelte__internal, {
  beforeUpdate: sr,
  getContext: lr,
  onDestroy: cr,
  setContext: ur
} = window.__gradio__svelte__internal;
function Ie(t) {
  let e, r;
  const n = (
    /*#slots*/
    t[7].default
  ), a = Vt(
    n,
    t,
    /*$$scope*/
    t[6],
    null
  );
  return {
    c() {
      e = Ve("svelte-slot"), a && a.c(), this.h();
    },
    l(o) {
      e = Xe(o, "SVELTE-SLOT", {
        class: !0
      });
      var i = Ze(e);
      a && a.l(i), i.forEach(F), this.h();
    },
    h() {
      et(e, "class", "svelte-1rt0kpf");
    },
    m(o, i) {
      K(o, e, i), a && a.m(e, null), t[9](e), r = !0;
    },
    p(o, i) {
      a && a.p && (!r || i & /*$$scope*/
      64) && ir(
        a,
        n,
        o,
        /*$$scope*/
        o[6],
        r ? tr(
          n,
          /*$$scope*/
          o[6],
          i,
          null
        ) : er(
          /*$$scope*/
          o[6]
        ),
        null
      );
    },
    i(o) {
      r || (W(a, o), r = !0);
    },
    o(o) {
      fe(a, o), r = !1;
    },
    d(o) {
      o && F(e), a && a.d(o), t[9](null);
    }
  };
}
function dr(t) {
  let e, r, n, a, o = (
    /*$$slots*/
    t[4].default && Ie(t)
  );
  return {
    c() {
      e = Ve("react-portal-target"), r = or(), o && o.c(), n = Te(), this.h();
    },
    l(i) {
      e = Xe(i, "REACT-PORTAL-TARGET", {
        class: !0
      }), Ze(e).forEach(F), r = Zt(i), o && o.l(i), n = Te(), this.h();
    },
    h() {
      et(e, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      K(i, e, s), t[8](e), K(i, r, s), o && o.m(i, s), K(i, n, s), a = !0;
    },
    p(i, [s]) {
      /*$$slots*/
      i[4].default ? o ? (o.p(i, s), s & /*$$slots*/
      16 && W(o, 1)) : (o = Ie(i), o.c(), W(o, 1), o.m(n.parentNode, n)) : o && (rr(), fe(o, 1, 1, () => {
        o = null;
      }), Qt());
    },
    i(i) {
      a || (W(o), a = !0);
    },
    o(i) {
      fe(o), a = !1;
    },
    d(i) {
      i && (F(e), F(r), F(n)), t[8](null), o && o.d(i);
    }
  };
}
function Fe(t) {
  const {
    svelteInit: e,
    ...r
  } = t;
  return r;
}
function fr(t, e, r) {
  let n, a, {
    $$slots: o = {},
    $$scope: i
  } = e;
  const s = Xt(o);
  let {
    svelteInit: l
  } = e;
  const p = L(Fe(e)), y = L();
  Oe(t, y, (u) => r(0, n = u));
  const c = L();
  Oe(t, c, (u) => r(1, a = u));
  const h = [], m = lr("$$ms-gr-react-wrapper"), {
    slotKey: C,
    slotIndex: j,
    subSlotIndex: f
  } = vt() || {}, _ = l({
    parent: m,
    props: p,
    target: y,
    slot: c,
    slotKey: C,
    slotIndex: j,
    subSlotIndex: f,
    onDestroy(u) {
      h.push(u);
    }
  });
  ur("$$ms-gr-react-wrapper", _), sr(() => {
    p.set(Fe(e));
  }), cr(() => {
    h.forEach((u) => u());
  });
  function x(u) {
    Ee[u ? "unshift" : "push"](() => {
      n = u, y.set(n);
    });
  }
  function O(u) {
    Ee[u ? "unshift" : "push"](() => {
      a = u, c.set(a);
    });
  }
  return t.$$set = (u) => {
    r(17, e = ke(ke({}, e), Re(u))), "svelteInit" in u && r(5, l = u.svelteInit), "$$scope" in u && r(6, i = u.$$scope);
  }, e = Re(e), [n, a, y, c, s, l, i, o, x, O];
}
class mr extends Jt {
  constructor(e) {
    super(), nr(this, e, fr, dr, ar, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ln
} = window.__gradio__svelte__internal, ze = window.ms_globals.rerender, ie = window.ms_globals.tree;
function pr(t, e = {}) {
  function r(n) {
    const a = L(), o = new mr({
      ...n,
      props: {
        svelteInit(i) {
          window.ms_globals.autokey += 1;
          const s = {
            key: window.ms_globals.autokey,
            svelteInstance: a,
            reactComponent: t,
            props: i.props,
            slot: i.slot,
            target: i.target,
            slotIndex: i.slotIndex,
            subSlotIndex: i.subSlotIndex,
            ignore: e.ignore,
            slotKey: i.slotKey,
            nodes: []
          }, l = i.parent ?? ie;
          return l.nodes = [...l.nodes, s], ze({
            createPortal: ue,
            node: ie
          }), i.onDestroy(() => {
            l.nodes = l.nodes.filter((p) => p.svelteInstance !== a), ze({
              createPortal: ue,
              node: ie
            });
          }), s;
        },
        ...n.props
      }
    });
    return a.set(o), o;
  }
  return new Promise((n) => {
    window.ms_globals.initializePromise.then(() => {
      n(r);
    });
  });
}
const _r = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function yr(t) {
  return t ? Object.keys(t).reduce((e, r) => {
    const n = t[r];
    return e[r] = hr(r, n), e;
  }, {}) : {};
}
function hr(t, e) {
  return typeof e == "number" && !_r.includes(t) ? e + "px" : e;
}
function me(t) {
  const e = [], r = t.cloneNode(!1);
  if (t._reactElement) {
    const a = k.Children.toArray(t._reactElement.props.children).map((o) => {
      if (k.isValidElement(o) && o.props.__slot__) {
        const {
          portals: i,
          clonedElement: s
        } = me(o.props.el);
        return k.cloneElement(o, {
          ...o.props,
          el: s,
          children: [...k.Children.toArray(o.props.children), ...i]
        });
      }
      return null;
    });
    return a.originalChildren = t._reactElement.props.children, e.push(ue(k.cloneElement(t._reactElement, {
      ...t._reactElement.props,
      children: a
    }), r)), {
      clonedElement: r,
      portals: e
    };
  }
  Object.keys(t.getEventListeners()).forEach((a) => {
    t.getEventListeners(a).forEach(({
      listener: i,
      type: s,
      useCapture: l
    }) => {
      r.addEventListener(s, i, l);
    });
  });
  const n = Array.from(t.childNodes);
  for (let a = 0; a < n.length; a++) {
    const o = n[a];
    if (o.nodeType === 1) {
      const {
        clonedElement: i,
        portals: s
      } = me(o);
      e.push(...s), r.appendChild(i);
    } else o.nodeType === 3 && r.appendChild(o.cloneNode());
  }
  return {
    clonedElement: r,
    portals: e
  };
}
function Pr(t, e) {
  t && (typeof t == "function" ? t(e) : t.current = e);
}
const pe = gt(({
  slot: t,
  clone: e,
  className: r,
  style: n,
  observeAttributes: a
}, o) => {
  const i = wt(), [s, l] = Ye([]), {
    forceClone: p
  } = St(), y = p ? !0 : e;
  return qe(() => {
    var j;
    if (!i.current || !t)
      return;
    let c = t;
    function h() {
      let f = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (f = c.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), Pr(o, f), r && f.classList.add(...r.split(" ")), n) {
        const _ = yr(n);
        Object.keys(_).forEach((x) => {
          f.style[x] = _[x];
        });
      }
    }
    let m = null, C = null;
    if (y && window.MutationObserver) {
      let f = function() {
        var u, b, d;
        (u = i.current) != null && u.contains(c) && ((b = i.current) == null || b.removeChild(c));
        const {
          portals: x,
          clonedElement: O
        } = me(t);
        c = O, l(x), c.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          h();
        }, 50), (d = i.current) == null || d.appendChild(c);
      };
      f();
      const _ = Kt(() => {
        f(), m == null || m.disconnect(), m == null || m.observe(t, {
          childList: !0,
          subtree: !0,
          attributes: a
        });
      }, 50);
      m = new window.MutationObserver(_), m.observe(t, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", h(), (j = i.current) == null || j.appendChild(c);
    return () => {
      var f, _;
      c.style.display = "", (f = i.current) != null && f.contains(c) && ((_ = i.current) == null || _.removeChild(c)), m == null || m.disconnect();
    };
  }, [t, y, r, n, o, a, p]), k.createElement("react-child", {
    ref: i,
    style: {
      display: "contents"
    }
  }, ...s);
});
function gr(t) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(t.trim());
}
function wr(t, e = !1) {
  try {
    if (Et(t))
      return t;
    if (e && !gr(t))
      return;
    if (typeof t == "string") {
      let r = t.trim();
      return r.startsWith(";") && (r = r.slice(1)), r.endsWith(";") && (r = r.slice(0, -1)), new Function(`return (...args) => (${r})(...args)`)();
    }
    return;
  } catch {
    return;
  }
}
function se(t, e) {
  return bt(() => wr(t, e), [t, e]);
}
const br = ({
  children: t,
  ...e
}) => /* @__PURE__ */ v.jsx(v.Fragment, {
  children: t(e)
});
function vr(t) {
  return k.createElement(br, {
    children: t
  });
}
function De(t, e) {
  return t ? e != null && e.forceClone || e != null && e.params ? vr((r) => /* @__PURE__ */ v.jsx(jt, {
    forceClone: e == null ? void 0 : e.forceClone,
    params: e == null ? void 0 : e.params,
    children: /* @__PURE__ */ v.jsx(pe, {
      slot: t,
      clone: e == null ? void 0 : e.clone,
      ...r
    })
  })) : /* @__PURE__ */ v.jsx(pe, {
    slot: t,
    clone: e == null ? void 0 : e.clone
  }) : null;
}
function xr({
  key: t,
  slots: e,
  targets: r
}, n) {
  return e[t] ? (...a) => r ? r.map((o, i) => /* @__PURE__ */ v.jsx(k.Fragment, {
    children: De(o, {
      clone: !0,
      params: a,
      forceClone: !0
    })
  }, i)) : /* @__PURE__ */ v.jsx(v.Fragment, {
    children: De(e[t], {
      clone: !0,
      params: a,
      forceClone: !0
    })
  }) : void 0;
}
var tt = Symbol.for("immer-nothing"), Me = Symbol.for("immer-draftable"), g = Symbol.for("immer-state");
function S(t, ...e) {
  throw new Error(`[Immer] minified error nr: ${t}. Full error at: https://bit.ly/3cXEKWf`);
}
var z = Object.getPrototypeOf;
function D(t) {
  return !!t && !!t[g];
}
function R(t) {
  var e;
  return t ? rt(t) || Array.isArray(t) || !!t[Me] || !!((e = t.constructor) != null && e[Me]) || J(t) || Q(t) : !1;
}
var Sr = Object.prototype.constructor.toString();
function rt(t) {
  if (!t || typeof t != "object") return !1;
  const e = z(t);
  if (e === null)
    return !0;
  const r = Object.hasOwnProperty.call(e, "constructor") && e.constructor;
  return r === Object ? !0 : typeof r == "function" && Function.toString.call(r) === Sr;
}
function Y(t, e) {
  H(t) === 0 ? Reflect.ownKeys(t).forEach((r) => {
    e(r, t[r], t);
  }) : t.forEach((r, n) => e(n, r, t));
}
function H(t) {
  const e = t[g];
  return e ? e.type_ : Array.isArray(t) ? 1 : J(t) ? 2 : Q(t) ? 3 : 0;
}
function _e(t, e) {
  return H(t) === 2 ? t.has(e) : Object.prototype.hasOwnProperty.call(t, e);
}
function nt(t, e, r) {
  const n = H(t);
  n === 2 ? t.set(e, r) : n === 3 ? t.add(r) : t[e] = r;
}
function jr(t, e) {
  return t === e ? t !== 0 || 1 / t === 1 / e : t !== t && e !== e;
}
function J(t) {
  return t instanceof Map;
}
function Q(t) {
  return t instanceof Set;
}
function T(t) {
  return t.copy_ || t.base_;
}
function ye(t, e) {
  if (J(t))
    return new Map(t);
  if (Q(t))
    return new Set(t);
  if (Array.isArray(t)) return Array.prototype.slice.call(t);
  const r = rt(t);
  if (e === !0 || e === "class_only" && !r) {
    const n = Object.getOwnPropertyDescriptors(t);
    delete n[g];
    let a = Reflect.ownKeys(n);
    for (let o = 0; o < a.length; o++) {
      const i = a[o], s = n[i];
      s.writable === !1 && (s.writable = !0, s.configurable = !0), (s.get || s.set) && (n[i] = {
        configurable: !0,
        writable: !0,
        // could live with !!desc.set as well here...
        enumerable: s.enumerable,
        value: t[i]
      });
    }
    return Object.create(z(t), n);
  } else {
    const n = z(t);
    if (n !== null && r)
      return {
        ...t
      };
    const a = Object.create(n);
    return Object.assign(a, t);
  }
}
function be(t, e = !1) {
  return Z(t) || D(t) || !R(t) || (H(t) > 1 && (t.set = t.add = t.clear = t.delete = Cr), Object.freeze(t), e && Object.entries(t).forEach(([r, n]) => be(n, !0))), t;
}
function Cr() {
  S(2);
}
function Z(t) {
  return Object.isFrozen(t);
}
var kr = {};
function I(t) {
  const e = kr[t];
  return e || S(0, t), e;
}
var A;
function at() {
  return A;
}
function Er(t, e) {
  return {
    drafts_: [],
    parent_: t,
    immer_: e,
    // Whenever the modified draft contains a draft from another scope, we
    // need to prevent auto-freezing so the unowned draft can be finalized.
    canAutoFreeze_: !0,
    unfinalizedDrafts_: 0
  };
}
function Ae(t, e) {
  e && (I("Patches"), t.patches_ = [], t.inversePatches_ = [], t.patchListener_ = e);
}
function he(t) {
  Pe(t), t.drafts_.forEach(Or), t.drafts_ = null;
}
function Pe(t) {
  t === A && (A = t.parent_);
}
function Ne(t) {
  return A = Er(A, t);
}
function Or(t) {
  const e = t[g];
  e.type_ === 0 || e.type_ === 1 ? e.revoke_() : e.revoked_ = !0;
}
function $e(t, e) {
  e.unfinalizedDrafts_ = e.drafts_.length;
  const r = e.drafts_[0];
  return t !== void 0 && t !== r ? (r[g].modified_ && (he(e), S(4)), R(t) && (t = q(e, t), e.parent_ || B(e, t)), e.patches_ && I("Patches").generateReplacementPatches_(r[g].base_, t, e.patches_, e.inversePatches_)) : t = q(e, r, []), he(e), e.patches_ && e.patchListener_(e.patches_, e.inversePatches_), t !== tt ? t : void 0;
}
function q(t, e, r) {
  if (Z(e)) return e;
  const n = e[g];
  if (!n)
    return Y(e, (a, o) => Ue(t, n, e, a, o, r)), e;
  if (n.scope_ !== t) return e;
  if (!n.modified_)
    return B(t, n.base_, !0), n.base_;
  if (!n.finalized_) {
    n.finalized_ = !0, n.scope_.unfinalizedDrafts_--;
    const a = n.copy_;
    let o = a, i = !1;
    n.type_ === 3 && (o = new Set(a), a.clear(), i = !0), Y(o, (s, l) => Ue(t, n, a, s, l, r, i)), B(t, a, !1), r && t.patches_ && I("Patches").generatePatches_(n, r, t.patches_, t.inversePatches_);
  }
  return n.copy_;
}
function Ue(t, e, r, n, a, o, i) {
  if (D(a)) {
    const s = o && e && e.type_ !== 3 && // Set objects are atomic since they have no keys.
    !_e(e.assigned_, n) ? o.concat(n) : void 0, l = q(t, a, s);
    if (nt(r, n, l), D(l))
      t.canAutoFreeze_ = !1;
    else return;
  } else i && r.add(a);
  if (R(a) && !Z(a)) {
    if (!t.immer_.autoFreeze_ && t.unfinalizedDrafts_ < 1)
      return;
    q(t, a), (!e || !e.scope_.parent_) && typeof n != "symbol" && Object.prototype.propertyIsEnumerable.call(r, n) && B(t, a);
  }
}
function B(t, e, r = !1) {
  !t.parent_ && t.immer_.autoFreeze_ && t.canAutoFreeze_ && be(e, r);
}
function Tr(t, e) {
  const r = Array.isArray(t), n = {
    type_: r ? 1 : 0,
    // Track which produce call this is associated with.
    scope_: e ? e.scope_ : at(),
    // True for both shallow and deep changes.
    modified_: !1,
    // Used during finalization.
    finalized_: !1,
    // Track which properties have been assigned (true) or deleted (false).
    assigned_: {},
    // The parent draft state.
    parent_: e,
    // The base state.
    base_: t,
    // The base proxy.
    draft_: null,
    // set below
    // The base copy with any updated values.
    copy_: null,
    // Called by the `produce` function.
    revoke_: null,
    isManual_: !1
  };
  let a = n, o = ve;
  r && (a = [n], o = N);
  const {
    revoke: i,
    proxy: s
  } = Proxy.revocable(a, o);
  return n.draft_ = s, n.revoke_ = i, s;
}
var ve = {
  get(t, e) {
    if (e === g) return t;
    const r = T(t);
    if (!_e(r, e))
      return Rr(t, r, e);
    const n = r[e];
    return t.finalized_ || !R(n) ? n : n === le(t.base_, e) ? (ce(t), t.copy_[e] = we(n, t)) : n;
  },
  has(t, e) {
    return e in T(t);
  },
  ownKeys(t) {
    return Reflect.ownKeys(T(t));
  },
  set(t, e, r) {
    const n = ot(T(t), e);
    if (n != null && n.set)
      return n.set.call(t.draft_, r), !0;
    if (!t.modified_) {
      const a = le(T(t), e), o = a == null ? void 0 : a[g];
      if (o && o.base_ === r)
        return t.copy_[e] = r, t.assigned_[e] = !1, !0;
      if (jr(r, a) && (r !== void 0 || _e(t.base_, e))) return !0;
      ce(t), ge(t);
    }
    return t.copy_[e] === r && // special case: handle new props with value 'undefined'
    (r !== void 0 || e in t.copy_) || // special case: NaN
    Number.isNaN(r) && Number.isNaN(t.copy_[e]) || (t.copy_[e] = r, t.assigned_[e] = !0), !0;
  },
  deleteProperty(t, e) {
    return le(t.base_, e) !== void 0 || e in t.base_ ? (t.assigned_[e] = !1, ce(t), ge(t)) : delete t.assigned_[e], t.copy_ && delete t.copy_[e], !0;
  },
  // Note: We never coerce `desc.value` into an Immer draft, because we can't make
  // the same guarantee in ES5 mode.
  getOwnPropertyDescriptor(t, e) {
    const r = T(t), n = Reflect.getOwnPropertyDescriptor(r, e);
    return n && {
      writable: !0,
      configurable: t.type_ !== 1 || e !== "length",
      enumerable: n.enumerable,
      value: r[e]
    };
  },
  defineProperty() {
    S(11);
  },
  getPrototypeOf(t) {
    return z(t.base_);
  },
  setPrototypeOf() {
    S(12);
  }
}, N = {};
Y(ve, (t, e) => {
  N[t] = function() {
    return arguments[0] = arguments[0][0], e.apply(this, arguments);
  };
});
N.deleteProperty = function(t, e) {
  return N.set.call(this, t, e, void 0);
};
N.set = function(t, e, r) {
  return ve.set.call(this, t[0], e, r, t[0]);
};
function le(t, e) {
  const r = t[g];
  return (r ? T(r) : t)[e];
}
function Rr(t, e, r) {
  var a;
  const n = ot(e, r);
  return n ? "value" in n ? n.value : (
    // This is a very special case, if the prop is a getter defined by the
    // prototype, we should invoke it with the draft as context!
    (a = n.get) == null ? void 0 : a.call(t.draft_)
  ) : void 0;
}
function ot(t, e) {
  if (!(e in t)) return;
  let r = z(t);
  for (; r; ) {
    const n = Object.getOwnPropertyDescriptor(r, e);
    if (n) return n;
    r = z(r);
  }
}
function ge(t) {
  t.modified_ || (t.modified_ = !0, t.parent_ && ge(t.parent_));
}
function ce(t) {
  t.copy_ || (t.copy_ = ye(t.base_, t.scope_.immer_.useStrictShallowCopy_));
}
var Ir = class {
  constructor(t) {
    this.autoFreeze_ = !0, this.useStrictShallowCopy_ = !1, this.produce = (e, r, n) => {
      if (typeof e == "function" && typeof r != "function") {
        const o = r;
        r = e;
        const i = this;
        return function(l = o, ...p) {
          return i.produce(l, (y) => r.call(this, y, ...p));
        };
      }
      typeof r != "function" && S(6), n !== void 0 && typeof n != "function" && S(7);
      let a;
      if (R(e)) {
        const o = Ne(this), i = we(e, void 0);
        let s = !0;
        try {
          a = r(i), s = !1;
        } finally {
          s ? he(o) : Pe(o);
        }
        return Ae(o, n), $e(a, o);
      } else if (!e || typeof e != "object") {
        if (a = r(e), a === void 0 && (a = e), a === tt && (a = void 0), this.autoFreeze_ && be(a, !0), n) {
          const o = [], i = [];
          I("Patches").generateReplacementPatches_(e, a, o, i), n(o, i);
        }
        return a;
      } else S(1, e);
    }, this.produceWithPatches = (e, r) => {
      if (typeof e == "function")
        return (i, ...s) => this.produceWithPatches(i, (l) => e(l, ...s));
      let n, a;
      return [this.produce(e, r, (i, s) => {
        n = i, a = s;
      }), n, a];
    }, typeof (t == null ? void 0 : t.autoFreeze) == "boolean" && this.setAutoFreeze(t.autoFreeze), typeof (t == null ? void 0 : t.useStrictShallowCopy) == "boolean" && this.setUseStrictShallowCopy(t.useStrictShallowCopy);
  }
  createDraft(t) {
    R(t) || S(8), D(t) && (t = Fr(t));
    const e = Ne(this), r = we(t, void 0);
    return r[g].isManual_ = !0, Pe(e), r;
  }
  finishDraft(t, e) {
    const r = t && t[g];
    (!r || !r.isManual_) && S(9);
    const {
      scope_: n
    } = r;
    return Ae(n, e), $e(void 0, n);
  }
  /**
   * Pass true to automatically freeze all copies created by Immer.
   *
   * By default, auto-freezing is enabled.
   */
  setAutoFreeze(t) {
    this.autoFreeze_ = t;
  }
  /**
   * Pass true to enable strict shallow copy.
   *
   * By default, immer does not copy the object descriptors such as getter, setter and non-enumrable properties.
   */
  setUseStrictShallowCopy(t) {
    this.useStrictShallowCopy_ = t;
  }
  applyPatches(t, e) {
    let r;
    for (r = e.length - 1; r >= 0; r--) {
      const a = e[r];
      if (a.path.length === 0 && a.op === "replace") {
        t = a.value;
        break;
      }
    }
    r > -1 && (e = e.slice(r + 1));
    const n = I("Patches").applyPatches_;
    return D(t) ? n(t, e) : this.produce(t, (a) => n(a, e));
  }
};
function we(t, e) {
  const r = J(t) ? I("MapSet").proxyMap_(t, e) : Q(t) ? I("MapSet").proxySet_(t, e) : Tr(t, e);
  return (e ? e.scope_ : at()).drafts_.push(r), r;
}
function Fr(t) {
  return D(t) || S(10, t), it(t);
}
function it(t) {
  if (!R(t) || Z(t)) return t;
  const e = t[g];
  let r;
  if (e) {
    if (!e.modified_) return e.base_;
    e.finalized_ = !0, r = ye(t, e.scope_.immer_.useStrictShallowCopy_);
  } else
    r = ye(t, !0);
  return Y(r, (n, a) => {
    nt(r, n, it(a));
  }), e && (e.finalized_ = !1), r;
}
var w = new Ir(), zr = w.produce;
w.produceWithPatches.bind(w);
w.setAutoFreeze.bind(w);
w.setUseStrictShallowCopy.bind(w);
w.applyPatches.bind(w);
w.createDraft.bind(w);
w.finishDraft.bind(w);
var X = {}, st = {
  exports: {}
};
(function(t) {
  function e(r) {
    return r && r.__esModule ? r : {
      default: r
    };
  }
  t.exports = e, t.exports.__esModule = !0, t.exports.default = t.exports;
})(st);
var V = st.exports, ee = {};
Object.defineProperty(ee, "__esModule", {
  value: !0
});
ee.default = void 0;
var Dr = {
  // Options
  items_per_page: "/ page",
  jump_to: "Go to",
  jump_to_confirm: "confirm",
  page: "Page",
  // Pagination
  prev_page: "Previous Page",
  next_page: "Next Page",
  prev_5: "Previous 5 Pages",
  next_5: "Next 5 Pages",
  prev_3: "Previous 3 Pages",
  next_3: "Next 3 Pages",
  page_size: "Page Size"
};
ee.default = Dr;
var te = {}, $ = {}, re = {}, lt = {
  exports: {}
}, ct = {
  exports: {}
}, ut = {
  exports: {}
}, dt = {
  exports: {}
};
(function(t) {
  function e(r) {
    "@babel/helpers - typeof";
    return t.exports = e = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(n) {
      return typeof n;
    } : function(n) {
      return n && typeof Symbol == "function" && n.constructor === Symbol && n !== Symbol.prototype ? "symbol" : typeof n;
    }, t.exports.__esModule = !0, t.exports.default = t.exports, e(r);
  }
  t.exports = e, t.exports.__esModule = !0, t.exports.default = t.exports;
})(dt);
var ft = dt.exports, mt = {
  exports: {}
};
(function(t) {
  var e = ft.default;
  function r(n, a) {
    if (e(n) != "object" || !n) return n;
    var o = n[Symbol.toPrimitive];
    if (o !== void 0) {
      var i = o.call(n, a || "default");
      if (e(i) != "object") return i;
      throw new TypeError("@@toPrimitive must return a primitive value.");
    }
    return (a === "string" ? String : Number)(n);
  }
  t.exports = r, t.exports.__esModule = !0, t.exports.default = t.exports;
})(mt);
var Mr = mt.exports;
(function(t) {
  var e = ft.default, r = Mr;
  function n(a) {
    var o = r(a, "string");
    return e(o) == "symbol" ? o : o + "";
  }
  t.exports = n, t.exports.__esModule = !0, t.exports.default = t.exports;
})(ut);
var Ar = ut.exports;
(function(t) {
  var e = Ar;
  function r(n, a, o) {
    return (a = e(a)) in n ? Object.defineProperty(n, a, {
      value: o,
      enumerable: !0,
      configurable: !0,
      writable: !0
    }) : n[a] = o, n;
  }
  t.exports = r, t.exports.__esModule = !0, t.exports.default = t.exports;
})(ct);
var Nr = ct.exports;
(function(t) {
  var e = Nr;
  function r(a, o) {
    var i = Object.keys(a);
    if (Object.getOwnPropertySymbols) {
      var s = Object.getOwnPropertySymbols(a);
      o && (s = s.filter(function(l) {
        return Object.getOwnPropertyDescriptor(a, l).enumerable;
      })), i.push.apply(i, s);
    }
    return i;
  }
  function n(a) {
    for (var o = 1; o < arguments.length; o++) {
      var i = arguments[o] != null ? arguments[o] : {};
      o % 2 ? r(Object(i), !0).forEach(function(s) {
        e(a, s, i[s]);
      }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(a, Object.getOwnPropertyDescriptors(i)) : r(Object(i)).forEach(function(s) {
        Object.defineProperty(a, s, Object.getOwnPropertyDescriptor(i, s));
      });
    }
    return a;
  }
  t.exports = n, t.exports.__esModule = !0, t.exports.default = t.exports;
})(lt);
var $r = lt.exports, ne = {};
Object.defineProperty(ne, "__esModule", {
  value: !0
});
ne.commonLocale = void 0;
ne.commonLocale = {
  yearFormat: "YYYY",
  dayFormat: "D",
  cellMeridiemFormat: "A",
  monthBeforeYear: !0
};
var Ur = V.default;
Object.defineProperty(re, "__esModule", {
  value: !0
});
re.default = void 0;
var Le = Ur($r), Lr = ne, Kr = (0, Le.default)((0, Le.default)({}, Lr.commonLocale), {}, {
  locale: "en_US",
  today: "Today",
  now: "Now",
  backToToday: "Back to today",
  ok: "OK",
  clear: "Clear",
  week: "Week",
  month: "Month",
  year: "Year",
  timeSelect: "select time",
  dateSelect: "select date",
  weekSelect: "Choose a week",
  monthSelect: "Choose a month",
  yearSelect: "Choose a year",
  decadeSelect: "Choose a decade",
  dateFormat: "M/D/YYYY",
  dateTimeFormat: "M/D/YYYY HH:mm:ss",
  previousMonth: "Previous month (PageUp)",
  nextMonth: "Next month (PageDown)",
  previousYear: "Last year (Control + left)",
  nextYear: "Next year (Control + right)",
  previousDecade: "Last decade",
  nextDecade: "Next decade",
  previousCentury: "Last century",
  nextCentury: "Next century"
});
re.default = Kr;
var U = {};
Object.defineProperty(U, "__esModule", {
  value: !0
});
U.default = void 0;
const Wr = {
  placeholder: "Select time",
  rangePlaceholder: ["Start time", "End time"]
};
U.default = Wr;
var pt = V.default;
Object.defineProperty($, "__esModule", {
  value: !0
});
$.default = void 0;
var Yr = pt(re), qr = pt(U);
const Br = {
  lang: Object.assign({
    placeholder: "Select date",
    yearPlaceholder: "Select year",
    quarterPlaceholder: "Select quarter",
    monthPlaceholder: "Select month",
    weekPlaceholder: "Select week",
    rangePlaceholder: ["Start date", "End date"],
    rangeYearPlaceholder: ["Start year", "End year"],
    rangeQuarterPlaceholder: ["Start quarter", "End quarter"],
    rangeMonthPlaceholder: ["Start month", "End month"],
    rangeWeekPlaceholder: ["Start week", "End week"]
  }, Yr.default),
  timePickerLocale: Object.assign({}, qr.default)
};
$.default = Br;
var Gr = V.default;
Object.defineProperty(te, "__esModule", {
  value: !0
});
te.default = void 0;
var Hr = Gr($);
te.default = Hr.default;
var ae = V.default;
Object.defineProperty(X, "__esModule", {
  value: !0
});
X.default = void 0;
var Jr = ae(ee), Qr = ae(te), Zr = ae($), Xr = ae(U);
const P = "${label} is not a valid ${type}", Vr = {
  locale: "en",
  Pagination: Jr.default,
  DatePicker: Zr.default,
  TimePicker: Xr.default,
  Calendar: Qr.default,
  global: {
    placeholder: "Please select",
    close: "Close"
  },
  Table: {
    filterTitle: "Filter menu",
    filterConfirm: "OK",
    filterReset: "Reset",
    filterEmptyText: "No filters",
    filterCheckAll: "Select all items",
    filterSearchPlaceholder: "Search in filters",
    emptyText: "No data",
    selectAll: "Select current page",
    selectInvert: "Invert current page",
    selectNone: "Clear all data",
    selectionAll: "Select all data",
    sortTitle: "Sort",
    expand: "Expand row",
    collapse: "Collapse row",
    triggerDesc: "Click to sort descending",
    triggerAsc: "Click to sort ascending",
    cancelSort: "Click to cancel sorting"
  },
  Tour: {
    Next: "Next",
    Previous: "Previous",
    Finish: "Finish"
  },
  Modal: {
    okText: "OK",
    cancelText: "Cancel",
    justOkText: "OK"
  },
  Popconfirm: {
    okText: "OK",
    cancelText: "Cancel"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Search here",
    itemUnit: "item",
    itemsUnit: "items",
    remove: "Remove",
    selectCurrent: "Select current page",
    removeCurrent: "Remove current page",
    selectAll: "Select all data",
    deselectAll: "Deselect all data",
    removeAll: "Remove all data",
    selectInvert: "Invert current page"
  },
  Upload: {
    uploading: "Uploading...",
    removeFile: "Remove file",
    uploadError: "Upload error",
    previewFile: "Preview file",
    downloadFile: "Download file"
  },
  Empty: {
    description: "No data"
  },
  Icon: {
    icon: "icon"
  },
  Text: {
    edit: "Edit",
    copy: "Copy",
    copied: "Copied",
    expand: "Expand",
    collapse: "Collapse"
  },
  Form: {
    optional: "(optional)",
    defaultValidateMessages: {
      default: "Field validation error for ${label}",
      required: "Please enter ${label}",
      enum: "${label} must be one of [${enum}]",
      whitespace: "${label} cannot be a blank character",
      date: {
        format: "${label} date format is invalid",
        parse: "${label} cannot be converted to a date",
        invalid: "${label} is an invalid date"
      },
      types: {
        string: P,
        method: P,
        array: P,
        object: P,
        number: P,
        date: P,
        boolean: P,
        integer: P,
        float: P,
        regexp: P,
        email: P,
        url: P,
        hex: P
      },
      string: {
        len: "${label} must be ${len} characters",
        min: "${label} must be at least ${min} characters",
        max: "${label} must be up to ${max} characters",
        range: "${label} must be between ${min}-${max} characters"
      },
      number: {
        len: "${label} must be equal to ${len}",
        min: "${label} must be minimum ${min}",
        max: "${label} must be maximum ${max}",
        range: "${label} must be between ${min}-${max}"
      },
      array: {
        len: "Must be ${len} ${label}",
        min: "At least ${min} ${label}",
        max: "At most ${max} ${label}",
        range: "The amount of ${label} must be between ${min}-${max}"
      },
      pattern: {
        mismatch: "${label} does not match the pattern ${pattern}"
      }
    }
  },
  Image: {
    preview: "Preview"
  },
  QRCode: {
    expired: "QR code expired",
    refresh: "Refresh",
    scanned: "Scanned"
  },
  ColorPicker: {
    presetEmpty: "Empty",
    transparent: "Transparent",
    singleColor: "Single",
    gradientColor: "Gradient"
  }
};
X.default = Vr;
var _t = X;
const yt = /* @__PURE__ */ Be(_t), en = /* @__PURE__ */ He({
  __proto__: null,
  default: yt
}, [_t]);
var ht = {
  exports: {}
};
(function(t, e) {
  (function(r, n) {
    t.exports = n();
  })(xt, function() {
    return {
      name: "en",
      weekdays: "Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday".split("_"),
      months: "January_February_March_April_May_June_July_August_September_October_November_December".split("_"),
      ordinal: function(r) {
        var n = ["th", "st", "nd", "rd"], a = r % 100;
        return "[" + r + (n[(a - 20) % 10] || n[a] || n[0]) + "]";
      }
    };
  });
})(ht);
var Pt = ht.exports;
const tn = /* @__PURE__ */ Be(Pt), rn = /* @__PURE__ */ He({
  __proto__: null,
  default: tn
}, [Pt]), nn = () => (Ge.locale("en"), yt), Ke = {
  ar_EG: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./ar_EG-CF_1nBQm.js").then((e) => e.a), import("./ar-BJfSbh2B.js").then((e) => e.a)]);
    return {
      antd: t,
      dayjs: "ar"
    };
  },
  az_AZ: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./az_AZ-DuBzNNjd.js").then((e) => e.a), import("./az-D4LkDUiA.js").then((e) => e.a)]);
    return {
      antd: t,
      dayjs: "az"
    };
  },
  bg_BG: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./bg_BG-BDp5oejz.js").then((e) => e.b), import("./bg-DNJlgddO.js").then((e) => e.b)]);
    return {
      antd: t,
      dayjs: "bg"
    };
  },
  bn_BD: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./bn_BD-D2k0aJj3.js").then((e) => e.b), import("./bn-LM73tIZB.js").then((e) => e.b)]);
    return {
      antd: t,
      dayjs: "bn"
    };
  },
  by_BY: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./by_BY-CsI1YXua.js").then((e) => e.b),
      import("./be-QlIBKv-f.js").then((e) => e.b)
      // Belarusian (Belarus)
    ]);
    return {
      antd: t,
      dayjs: "be"
    };
  },
  ca_ES: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./ca_ES-hv6FEbOa.js").then((e) => e.c), import("./ca-BVHMbDpG.js").then((e) => e.c)]);
    return {
      antd: t,
      dayjs: "ca"
    };
  },
  cs_CZ: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./cs_CZ-DL_huktX.js").then((e) => e.c), import("./cs-BV-bbnt3.js").then((e) => e.c)]);
    return {
      antd: t,
      dayjs: "cs"
    };
  },
  da_DK: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./da_DK-DO5-bbyb.js").then((e) => e.d), import("./da-mxiceUVT.js").then((e) => e.d)]);
    return {
      antd: t,
      dayjs: "da"
    };
  },
  de_DE: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./de_DE-NMKGfKro.js").then((e) => e.d), import("./de-C7q9uekq.js").then((e) => e.d)]);
    return {
      antd: t,
      dayjs: "de"
    };
  },
  el_GR: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./el_GR-C8qz2ilR.js").then((e) => e.e), import("./el-BjC5yNDJ.js").then((e) => e.e)]);
    return {
      antd: t,
      dayjs: "el"
    };
  },
  en_GB: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./en_GB-DN4iBy4o.js").then((e) => e.e), import("./en-gb-DUlaTlx2.js").then((e) => e.e)]);
    return {
      antd: t,
      dayjs: "en-gb"
    };
  },
  en_US: async () => {
    const [{
      default: t
    }] = await Promise.all([Promise.resolve().then(() => en), Promise.resolve().then(() => rn)]);
    return {
      antd: t,
      dayjs: "en"
    };
  },
  es_ES: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./es_ES-DbF-sVyk.js").then((e) => e.e), import("./es-BHSBQJFE.js").then((e) => e.e)]);
    return {
      antd: t,
      dayjs: "es"
    };
  },
  et_EE: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./et_EE-CNhpcsCD.js").then((e) => e.e), import("./et-Zbq1qYeG.js").then((e) => e.e)]);
    return {
      antd: t,
      dayjs: "et"
    };
  },
  eu_ES: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./eu_ES-C_Ghs_YJ.js").then((e) => e.e),
      import("./eu-DkwEHmv2.js").then((e) => e.e)
      // Basque
    ]);
    return {
      antd: t,
      dayjs: "eu"
    };
  },
  fa_IR: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./fa_IR-WY4IJlLb.js").then((e) => e.f), import("./fa-m9Yz51MJ.js").then((e) => e.f)]);
    return {
      antd: t,
      dayjs: "fa"
    };
  },
  fi_FI: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./fi_FI-CLfZOxiY.js").then((e) => e.f), import("./fi-DB3CbdaA.js").then((e) => e.f)]);
    return {
      antd: t,
      dayjs: "fi"
    };
  },
  fr_BE: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./fr_BE-DjcWKZ9g.js").then((e) => e.f), import("./fr-DtBCR8cS.js").then((e) => e.f)]);
    return {
      antd: t,
      dayjs: "fr"
    };
  },
  fr_CA: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./fr_CA-D542dCED.js").then((e) => e.f), import("./fr-ca-kHLeAmWY.js").then((e) => e.f)]);
    return {
      antd: t,
      dayjs: "fr-ca"
    };
  },
  fr_FR: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./fr_FR-C1UbpGpQ.js").then((e) => e.f), import("./fr-DtBCR8cS.js").then((e) => e.f)]);
    return {
      antd: t,
      dayjs: "fr"
    };
  },
  ga_IE: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./ga_IE-BdGyeSzC.js").then((e) => e.g),
      import("./ga-BwMM7U46.js").then((e) => e.g)
      // Irish
    ]);
    return {
      antd: t,
      dayjs: "ga"
    };
  },
  gl_ES: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./gl_ES-DLGVzoH7.js").then((e) => e.g),
      import("./gl-CmPHYxkI.js").then((e) => e.g)
      // Galician
    ]);
    return {
      antd: t,
      dayjs: "gl"
    };
  },
  he_IL: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./he_IL-DuPk-wd4.js").then((e) => e.h), import("./he-BHHJC_77.js").then((e) => e.h)]);
    return {
      antd: t,
      dayjs: "he"
    };
  },
  hi_IN: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./hi_IN-DYkeijFt.js").then((e) => e.h), import("./hi-CbudUafL.js").then((e) => e.h)]);
    return {
      antd: t,
      dayjs: "hi"
    };
  },
  hr_HR: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./hr_HR-B-5ARnS2.js").then((e) => e.h), import("./hr-BL6A_ONm.js").then((e) => e.h)]);
    return {
      antd: t,
      dayjs: "hr"
    };
  },
  hu_HU: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./hu_HU-DIlkPXE-.js").then((e) => e.h), import("./hu-DZ_-pDFx.js").then((e) => e.h)]);
    return {
      antd: t,
      dayjs: "hu"
    };
  },
  hy_AM: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./hy_AM-D5AG4_Hd.js").then((e) => e.h),
      import("./am-DnS-kXAW.js").then((e) => e.a)
      // Armenian
    ]);
    return {
      antd: t,
      dayjs: "am"
    };
  },
  id_ID: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./id_ID-ChOlIu3l.js").then((e) => e.i), import("./id-DcV88clW.js").then((e) => e.i)]);
    return {
      antd: t,
      dayjs: "id"
    };
  },
  is_IS: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./is_IS-D3IRqxT7.js").then((e) => e.i), import("./is-CBpMm0pC.js").then((e) => e.i)]);
    return {
      antd: t,
      dayjs: "is"
    };
  },
  it_IT: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./it_IT-BMd_84uX.js").then((e) => e.i), import("./it-BfnhV_OI.js").then((e) => e.i)]);
    return {
      antd: t,
      dayjs: "it"
    };
  },
  ja_JP: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./ja_JP-COt1L50w.js").then((e) => e.j), import("./ja-CHCPMcyt.js").then((e) => e.j)]);
    return {
      antd: t,
      dayjs: "ja"
    };
  },
  ka_GE: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./ka_GE-CzsFAD-i.js").then((e) => e.k),
      import("./ka-DrNLPKEq.js").then((e) => e.k)
      // Georgian
    ]);
    return {
      antd: t,
      dayjs: "ka"
    };
  },
  kk_KZ: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./kk_KZ-TlbaHIvf.js").then((e) => e.k),
      import("./kk-Bl3MaxQ4.js").then((e) => e.k)
      // Kazakh
    ]);
    return {
      antd: t,
      dayjs: "kk"
    };
  },
  km_KH: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./km_KH-CCemei-q.js").then((e) => e.k),
      import("./km-CSoKDhHx.js").then((e) => e.k)
      // Khmer
    ]);
    return {
      antd: t,
      dayjs: "km"
    };
  },
  kmr_IQ: async () => {
    const [t] = await Promise.all([
      import("./kmr_IQ-BjfTOUOy.js").then((e) => e.k)
      // Not available in Day.js, so no need to load a locale file.
    ]);
    return {
      antd: t.default,
      dayjs: ""
    };
  },
  kn_IN: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./kn_IN-Dov09sF_.js").then((e) => e.k),
      import("./kn-D4s7r3uC.js").then((e) => e.k)
      // Kannada
    ]);
    return {
      antd: t,
      dayjs: "kn"
    };
  },
  ko_KR: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./ko_KR-CN5Ezw63.js").then((e) => e.k), import("./ko-CsgNMhIk.js").then((e) => e.k)]);
    return {
      antd: t,
      dayjs: "ko"
    };
  },
  ku_IQ: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./ku_IQ-DOxk8d3o.js").then((e) => e.k),
      import("./ku-B7ShDwzV.js").then((e) => e.k)
      // Kurdish (Central)
    ]);
    return {
      antd: t,
      dayjs: "ku"
    };
  },
  lt_LT: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./lt_LT-DCU3OkAK.js").then((e) => e.l), import("./lt-DJKZ9dUL.js").then((e) => e.l)]);
    return {
      antd: t,
      dayjs: "lt"
    };
  },
  lv_LV: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./lv_LV-oPXrXTry.js").then((e) => e.l), import("./lv-U9GkSyTv.js").then((e) => e.l)]);
    return {
      antd: t,
      dayjs: "lv"
    };
  },
  mk_MK: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./mk_MK-COzZbf7n.js").then((e) => e.m),
      import("./mk-f70DkBOB.js").then((e) => e.m)
      // Macedonian
    ]);
    return {
      antd: t,
      dayjs: "mk"
    };
  },
  ml_IN: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./ml_IN-yVQgjkz5.js").then((e) => e.m),
      import("./ml-D55Tc7kq.js").then((e) => e.m)
      // Malayalam
    ]);
    return {
      antd: t,
      dayjs: "ml"
    };
  },
  mn_MN: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./mn_MN-DOsZvCHS.js").then((e) => e.m),
      import("./mn-eNrTouQy.js").then((e) => e.m)
      // Mongolian
    ]);
    return {
      antd: t,
      dayjs: "mn"
    };
  },
  ms_MY: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./ms_MY-06fpN9td.js").then((e) => e.m), import("./ms-B7afcbDz.js").then((e) => e.m)]);
    return {
      antd: t,
      dayjs: "ms"
    };
  },
  my_MM: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./my_MM-BAiCz-ma.js").then((e) => e.m),
      import("./my-CvR37khL.js").then((e) => e.m)
      // Burmese
    ]);
    return {
      antd: t,
      dayjs: "my"
    };
  },
  nb_NO: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./nb_NO-xi21xDPo.js").then((e) => e.n),
      import("./nb-Cn3kxr46.js").then((e) => e.n)
      // Norwegian Bokmål
    ]);
    return {
      antd: t,
      dayjs: "nb"
    };
  },
  ne_NP: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./ne_NP-CD2e0Aap.js").then((e) => e.n),
      import("./ne-CTuNWvKZ.js").then((e) => e.n)
      // Nepali
    ]);
    return {
      antd: t,
      dayjs: "ne"
    };
  },
  nl_BE: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./nl_BE-D2Kz10YC.js").then((e) => e.n),
      import("./nl-be-CN8nCNmA.js").then((e) => e.n)
      // Dutch (Belgium)
    ]);
    return {
      antd: t,
      dayjs: "nl-be"
    };
  },
  nl_NL: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./nl_NL-BA4-0_UN.js").then((e) => e.n),
      import("./nl-CKTWqLH8.js").then((e) => e.n)
      // Dutch (Netherlands)
    ]);
    return {
      antd: t,
      dayjs: "nl"
    };
  },
  pl_PL: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./pl_PL-DgLGoIcH.js").then((e) => e.p), import("./pl-CCOUxw7V.js").then((e) => e.p)]);
    return {
      antd: t,
      dayjs: "pl"
    };
  },
  pt_BR: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./pt_BR-8iWXZV-p.js").then((e) => e.p),
      import("./pt-br-Cx2vWoDE.js").then((e) => e.p)
      // Portuguese (Brazil)
    ]);
    return {
      antd: t,
      dayjs: "pt-br"
    };
  },
  pt_PT: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./pt_PT-BN9Momfr.js").then((e) => e.p),
      import("./pt-kNsi4HRN.js").then((e) => e.p)
      // Portuguese (Portugal)
    ]);
    return {
      antd: t,
      dayjs: "pt"
    };
  },
  ro_RO: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./ro_RO-DMNk7bCw.js").then((e) => e.r), import("./ro-NhE2fVMC.js").then((e) => e.r)]);
    return {
      antd: t,
      dayjs: "ro"
    };
  },
  ru_RU: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./ru_RU-DdacOO__.js").then((e) => e.r), import("./ru-3fFkRZW9.js").then((e) => e.r)]);
    return {
      antd: t,
      dayjs: "ru"
    };
  },
  si_LK: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./si_LK-WQths1bw.js").then((e) => e.s),
      import("./si-BArqPnmm.js").then((e) => e.s)
      // Sinhala
    ]);
    return {
      antd: t,
      dayjs: "si"
    };
  },
  sk_SK: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./sk_SK-Dvt2EoDi.js").then((e) => e.s), import("./sk-Cey6m0kd.js").then((e) => e.s)]);
    return {
      antd: t,
      dayjs: "sk"
    };
  },
  sl_SI: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./sl_SI-Dwsvn-n2.js").then((e) => e.s), import("./sl-s969Y8Zt.js").then((e) => e.s)]);
    return {
      antd: t,
      dayjs: "sl"
    };
  },
  sr_RS: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./sr_RS-Lzi0821B.js").then((e) => e.s),
      import("./sr-E_k64rwJ.js").then((e) => e.s)
      // Serbian
    ]);
    return {
      antd: t,
      dayjs: "sr"
    };
  },
  sv_SE: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./sv_SE-wn7olaiw.js").then((e) => e.s), import("./sv-Dwot-I-f.js").then((e) => e.s)]);
    return {
      antd: t,
      dayjs: "sv"
    };
  },
  ta_IN: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./ta_IN-DmKxquv8.js").then((e) => e.t),
      import("./ta-CJIIxViT.js").then((e) => e.t)
      // Tamil
    ]);
    return {
      antd: t,
      dayjs: "ta"
    };
  },
  th_TH: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./th_TH-CfSTonL-.js").then((e) => e.t), import("./th-BULz_vvL.js").then((e) => e.t)]);
    return {
      antd: t,
      dayjs: "th"
    };
  },
  tk_TK: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./tk_TK-BhhPxM84.js").then((e) => e.t),
      import("./tk-CafwHzmT.js").then((e) => e.t)
      // Turkmen
    ]);
    return {
      antd: t,
      dayjs: "tk"
    };
  },
  tr_TR: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./tr_TR-BtEr3_lH.js").then((e) => e.t), import("./tr-Dc0kUncI.js").then((e) => e.t)]);
    return {
      antd: t,
      dayjs: "tr"
    };
  },
  uk_UA: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./uk_UA-4Tamvge-.js").then((e) => e.u),
      import("./uk-CtkAVArm.js").then((e) => e.u)
      // Ukrainian
    ]);
    return {
      antd: t,
      dayjs: "uk"
    };
  },
  ur_PK: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./ur_PK-C3mu3TjP.js").then((e) => e.u),
      import("./ur-Bn0ArWUq.js").then((e) => e.u)
      // Urdu
    ]);
    return {
      antd: t,
      dayjs: "ur"
    };
  },
  uz_UZ: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./uz_UZ-CMgAGePX.js").then((e) => e.u),
      import("./uz-VjdiggAe.js").then((e) => e.u)
      // Uzbek
    ]);
    return {
      antd: t,
      dayjs: "uz"
    };
  },
  vi_VN: async () => {
    const [{
      default: t
    }] = await Promise.all([import("./vi_VN-QiOU3IR8.js").then((e) => e.v), import("./vi-BRW4MhWN.js").then((e) => e.v)]);
    return {
      antd: t,
      dayjs: "vi"
    };
  },
  zh_CN: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./zh_CN-BNmzRyEe.js").then((e) => e.z),
      import("./zh-cn-gu0VsMuJ.js").then((e) => e.z)
      // Chinese (Simplified)
    ]);
    return {
      antd: t,
      dayjs: "zh-cn"
    };
  },
  zh_HK: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./zh_HK-C4MX0S84.js").then((e) => e.z),
      import("./zh-hk-6DpJBbKK.js").then((e) => e.z)
      // Chinese (Hong Kong)
    ]);
    return {
      antd: t,
      dayjs: "zh-hk"
    };
  },
  zh_TW: async () => {
    const [{
      default: t
    }] = await Promise.all([
      import("./zh_TW-DEtoo_bf.js").then((e) => e.z),
      import("./zh-tw-CoE4d8zy.js").then((e) => e.z)
      // Chinese (Taiwan)
    ]);
    return {
      antd: t,
      dayjs: "zh-tw"
    };
  }
}, an = (t, e) => zr(t, (r) => {
  Object.keys(e).forEach((n) => {
    const a = n.split(".");
    let o = r;
    for (let i = 0; i < a.length - 1; i++) {
      const s = a[i];
      o[s] || (o[s] = {}), o = o[s];
    }
    o[a[a.length - 1]] = /* @__PURE__ */ v.jsx(pe, {
      slot: e[n],
      clone: !0
    });
  });
}), We = pr(({
  slots: t,
  themeMode: e,
  id: r,
  className: n,
  style: a,
  locale: o = "en_US",
  getTargetContainer: i,
  getPopupContainer: s,
  renderEmpty: l,
  setSlotParams: p,
  children: y,
  component: c,
  ...h
}) => {
  var u;
  const [m, C] = Ye(() => nn()), j = {
    dark: e === "dark",
    ...((u = h.theme) == null ? void 0 : u.algorithm) || {}
  }, f = se(s), _ = se(i), x = se(l);
  qe(() => {
    o && Ke[o] && Ke[o]().then(({
      antd: b,
      dayjs: d
    }) => {
      C(b), Ge.locale(d);
    });
  }, [o]);
  const O = c || Tt;
  return /* @__PURE__ */ v.jsx("div", {
    id: r,
    className: n,
    style: a,
    children: /* @__PURE__ */ v.jsx(Ot, {
      hashPriority: "high",
      container: document.body,
      children: /* @__PURE__ */ v.jsx(O, {
        prefixCls: "ms-gr-ant",
        ...an(h, t),
        locale: m,
        getPopupContainer: f,
        getTargetContainer: _,
        renderEmpty: t.renderEmpty ? xr({
          slots: t,
          key: "renderEmpty"
        }) : x,
        theme: {
          cssVar: !0,
          ...h.theme,
          algorithm: Object.keys(j).map((b) => {
            switch (b) {
              case "dark":
                return j[b] ? Se.darkAlgorithm : null;
              case "compact":
                return j[b] ? Se.compactAlgorithm : null;
              default:
                return null;
            }
          }).filter(Boolean)
        },
        children: y
      })
    })
  });
}), cn = /* @__PURE__ */ Object.freeze(/* @__PURE__ */ Object.defineProperty({
  __proto__: null,
  ConfigProvider: We,
  default: We
}, Symbol.toStringTag, {
  value: "Module"
}));
export {
  te as a,
  $ as b,
  ne as c,
  U as d,
  ee as e,
  cn as f,
  V as i,
  $r as o
};
