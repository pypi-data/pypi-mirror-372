import { i as be, a as B, r as Ie, b as ve, Z as F, g as Ee, c as Re } from "./Index-DumzMspW.js";
const S = window.ms_globals.React, ye = window.ms_globals.React.forwardRef, D = window.ms_globals.React.useRef, le = window.ms_globals.React.useState, V = window.ms_globals.React.useEffect, ce = window.ms_globals.React.useMemo, U = window.ms_globals.ReactDOM.createPortal, Se = window.ms_globals.internalContext.useContextPropsContext, H = window.ms_globals.internalContext.ContextPropsProvider, Pe = window.ms_globals.antd.Cascader, ke = window.ms_globals.createItemsContext.createItemsContext;
var Te = /\s/;
function je(e) {
  for (var n = e.length; n-- && Te.test(e.charAt(n)); )
    ;
  return n;
}
var Fe = /^\s+/;
function Oe(e) {
  return e && e.slice(0, je(e) + 1).replace(Fe, "");
}
var X = NaN, Le = /^[-+]0x[0-9a-f]+$/i, Ne = /^0b[01]+$/i, We = /^0o[0-7]+$/i, Ae = parseInt;
function Y(e) {
  if (typeof e == "number")
    return e;
  if (be(e))
    return X;
  if (B(e)) {
    var n = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = B(n) ? n + "" : n;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Oe(e);
  var r = Ne.test(e);
  return r || We.test(e) ? Ae(e.slice(2), r ? 2 : 8) : Le.test(e) ? X : +e;
}
var A = function() {
  return Ie.Date.now();
}, Me = "Expected a function", De = Math.max, Ve = Math.min;
function Ue(e, n, r) {
  var c, o, t, l, s, u, x = 0, w = !1, a = !1, _ = !0;
  if (typeof e != "function")
    throw new TypeError(Me);
  n = Y(n) || 0, B(r) && (w = !!r.leading, a = "maxWait" in r, t = a ? De(Y(r.maxWait) || 0, n) : t, _ = "trailing" in r ? !!r.trailing : _);
  function d(m) {
    var b = c, k = o;
    return c = o = void 0, x = m, l = e.apply(k, b), l;
  }
  function C(m) {
    return x = m, s = setTimeout(h, n), w ? d(m) : l;
  }
  function y(m) {
    var b = m - u, k = m - x, I = n - b;
    return a ? Ve(I, t - k) : I;
  }
  function i(m) {
    var b = m - u, k = m - x;
    return u === void 0 || b >= n || b < 0 || a && k >= t;
  }
  function h() {
    var m = A();
    if (i(m))
      return p(m);
    s = setTimeout(h, y(m));
  }
  function p(m) {
    return s = void 0, _ && c ? d(m) : (c = o = void 0, l);
  }
  function R() {
    s !== void 0 && clearTimeout(s), x = 0, c = u = o = s = void 0;
  }
  function f() {
    return s === void 0 ? l : p(A());
  }
  function P() {
    var m = A(), b = i(m);
    if (c = arguments, o = this, u = m, b) {
      if (s === void 0)
        return C(u);
      if (a)
        return clearTimeout(s), s = setTimeout(h, n), d(u);
    }
    return s === void 0 && (s = setTimeout(h, n)), l;
  }
  return P.cancel = R, P.flush = f, P;
}
function Be(e, n) {
  return ve(e, n);
}
var se = {
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
var He = S, qe = Symbol.for("react.element"), ze = Symbol.for("react.fragment"), Ge = Object.prototype.hasOwnProperty, Je = He.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Xe = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ae(e, n, r) {
  var c, o = {}, t = null, l = null;
  r !== void 0 && (t = "" + r), n.key !== void 0 && (t = "" + n.key), n.ref !== void 0 && (l = n.ref);
  for (c in n) Ge.call(n, c) && !Xe.hasOwnProperty(c) && (o[c] = n[c]);
  if (e && e.defaultProps) for (c in n = e.defaultProps, n) o[c] === void 0 && (o[c] = n[c]);
  return {
    $$typeof: qe,
    type: e,
    key: t,
    ref: l,
    props: o,
    _owner: Je.current
  };
}
N.Fragment = ze;
N.jsx = ae;
N.jsxs = ae;
se.exports = N;
var g = se.exports;
const {
  SvelteComponent: Ye,
  assign: Z,
  binding_callbacks: K,
  check_outros: Ze,
  children: ie,
  claim_element: ue,
  claim_space: Ke,
  component_subscribe: Q,
  compute_slots: Qe,
  create_slot: $e,
  detach: j,
  element: de,
  empty: $,
  exclude_internal_props: ee,
  get_all_dirty_from_scope: en,
  get_slot_changes: nn,
  group_outros: tn,
  init: rn,
  insert_hydration: O,
  safe_not_equal: on,
  set_custom_element_data: fe,
  space: ln,
  transition_in: L,
  transition_out: q,
  update_slot_base: cn
} = window.__gradio__svelte__internal, {
  beforeUpdate: sn,
  getContext: an,
  onDestroy: un,
  setContext: dn
} = window.__gradio__svelte__internal;
function ne(e) {
  let n, r;
  const c = (
    /*#slots*/
    e[7].default
  ), o = $e(
    c,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      n = de("svelte-slot"), o && o.c(), this.h();
    },
    l(t) {
      n = ue(t, "SVELTE-SLOT", {
        class: !0
      });
      var l = ie(n);
      o && o.l(l), l.forEach(j), this.h();
    },
    h() {
      fe(n, "class", "svelte-1rt0kpf");
    },
    m(t, l) {
      O(t, n, l), o && o.m(n, null), e[9](n), r = !0;
    },
    p(t, l) {
      o && o.p && (!r || l & /*$$scope*/
      64) && cn(
        o,
        c,
        t,
        /*$$scope*/
        t[6],
        r ? nn(
          c,
          /*$$scope*/
          t[6],
          l,
          null
        ) : en(
          /*$$scope*/
          t[6]
        ),
        null
      );
    },
    i(t) {
      r || (L(o, t), r = !0);
    },
    o(t) {
      q(o, t), r = !1;
    },
    d(t) {
      t && j(n), o && o.d(t), e[9](null);
    }
  };
}
function fn(e) {
  let n, r, c, o, t = (
    /*$$slots*/
    e[4].default && ne(e)
  );
  return {
    c() {
      n = de("react-portal-target"), r = ln(), t && t.c(), c = $(), this.h();
    },
    l(l) {
      n = ue(l, "REACT-PORTAL-TARGET", {
        class: !0
      }), ie(n).forEach(j), r = Ke(l), t && t.l(l), c = $(), this.h();
    },
    h() {
      fe(n, "class", "svelte-1rt0kpf");
    },
    m(l, s) {
      O(l, n, s), e[8](n), O(l, r, s), t && t.m(l, s), O(l, c, s), o = !0;
    },
    p(l, [s]) {
      /*$$slots*/
      l[4].default ? t ? (t.p(l, s), s & /*$$slots*/
      16 && L(t, 1)) : (t = ne(l), t.c(), L(t, 1), t.m(c.parentNode, c)) : t && (tn(), q(t, 1, 1, () => {
        t = null;
      }), Ze());
    },
    i(l) {
      o || (L(t), o = !0);
    },
    o(l) {
      q(t), o = !1;
    },
    d(l) {
      l && (j(n), j(r), j(c)), e[8](null), t && t.d(l);
    }
  };
}
function te(e) {
  const {
    svelteInit: n,
    ...r
  } = e;
  return r;
}
function mn(e, n, r) {
  let c, o, {
    $$slots: t = {},
    $$scope: l
  } = n;
  const s = Qe(t);
  let {
    svelteInit: u
  } = n;
  const x = F(te(n)), w = F();
  Q(e, w, (f) => r(0, c = f));
  const a = F();
  Q(e, a, (f) => r(1, o = f));
  const _ = [], d = an("$$ms-gr-react-wrapper"), {
    slotKey: C,
    slotIndex: y,
    subSlotIndex: i
  } = Ee() || {}, h = u({
    parent: d,
    props: x,
    target: w,
    slot: a,
    slotKey: C,
    slotIndex: y,
    subSlotIndex: i,
    onDestroy(f) {
      _.push(f);
    }
  });
  dn("$$ms-gr-react-wrapper", h), sn(() => {
    x.set(te(n));
  }), un(() => {
    _.forEach((f) => f());
  });
  function p(f) {
    K[f ? "unshift" : "push"](() => {
      c = f, w.set(c);
    });
  }
  function R(f) {
    K[f ? "unshift" : "push"](() => {
      o = f, a.set(o);
    });
  }
  return e.$$set = (f) => {
    r(17, n = Z(Z({}, n), ee(f))), "svelteInit" in f && r(5, u = f.svelteInit), "$$scope" in f && r(6, l = f.$$scope);
  }, n = ee(n), [c, o, w, a, s, u, l, t, p, R];
}
class hn extends Ye {
  constructor(n) {
    super(), rn(this, n, mn, fn, on, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Pn
} = window.__gradio__svelte__internal, re = window.ms_globals.rerender, M = window.ms_globals.tree;
function _n(e, n = {}) {
  function r(c) {
    const o = F(), t = new hn({
      ...c,
      props: {
        svelteInit(l) {
          window.ms_globals.autokey += 1;
          const s = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: e,
            props: l.props,
            slot: l.slot,
            target: l.target,
            slotIndex: l.slotIndex,
            subSlotIndex: l.subSlotIndex,
            ignore: n.ignore,
            slotKey: l.slotKey,
            nodes: []
          }, u = l.parent ?? M;
          return u.nodes = [...u.nodes, s], re({
            createPortal: U,
            node: M
          }), l.onDestroy(() => {
            u.nodes = u.nodes.filter((x) => x.svelteInstance !== o), re({
              createPortal: U,
              node: M
            });
          }), s;
        },
        ...c.props
      }
    });
    return o.set(t), t;
  }
  return new Promise((c) => {
    window.ms_globals.initializePromise.then(() => {
      c(r);
    });
  });
}
const gn = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function pn(e) {
  return e ? Object.keys(e).reduce((n, r) => {
    const c = e[r];
    return n[r] = xn(r, c), n;
  }, {}) : {};
}
function xn(e, n) {
  return typeof n == "number" && !gn.includes(e) ? n + "px" : n;
}
function z(e) {
  const n = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const o = S.Children.toArray(e._reactElement.props.children).map((t) => {
      if (S.isValidElement(t) && t.props.__slot__) {
        const {
          portals: l,
          clonedElement: s
        } = z(t.props.el);
        return S.cloneElement(t, {
          ...t.props,
          el: s,
          children: [...S.Children.toArray(t.props.children), ...l]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, n.push(U(S.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), r)), {
      clonedElement: r,
      portals: n
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: l,
      type: s,
      useCapture: u
    }) => {
      r.addEventListener(s, l, u);
    });
  });
  const c = Array.from(e.childNodes);
  for (let o = 0; o < c.length; o++) {
    const t = c[o];
    if (t.nodeType === 1) {
      const {
        clonedElement: l,
        portals: s
      } = z(t);
      n.push(...s), r.appendChild(l);
    } else t.nodeType === 3 && r.appendChild(t.cloneNode());
  }
  return {
    clonedElement: r,
    portals: n
  };
}
function wn(e, n) {
  e && (typeof e == "function" ? e(n) : e.current = n);
}
const E = ye(({
  slot: e,
  clone: n,
  className: r,
  style: c,
  observeAttributes: o
}, t) => {
  const l = D(), [s, u] = le([]), {
    forceClone: x
  } = Se(), w = x ? !0 : n;
  return V(() => {
    var y;
    if (!l.current || !e)
      return;
    let a = e;
    function _() {
      let i = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (i = a.children[0], i.tagName.toLowerCase() === "react-portal-target" && i.children[0] && (i = i.children[0])), wn(t, i), r && i.classList.add(...r.split(" ")), c) {
        const h = pn(c);
        Object.keys(h).forEach((p) => {
          i.style[p] = h[p];
        });
      }
    }
    let d = null, C = null;
    if (w && window.MutationObserver) {
      let i = function() {
        var f, P, m;
        (f = l.current) != null && f.contains(a) && ((P = l.current) == null || P.removeChild(a));
        const {
          portals: p,
          clonedElement: R
        } = z(e);
        a = R, u(p), a.style.display = "contents", C && clearTimeout(C), C = setTimeout(() => {
          _();
        }, 50), (m = l.current) == null || m.appendChild(a);
      };
      i();
      const h = Ue(() => {
        i(), d == null || d.disconnect(), d == null || d.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      d = new window.MutationObserver(h), d.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", _(), (y = l.current) == null || y.appendChild(a);
    return () => {
      var i, h;
      a.style.display = "", (i = l.current) != null && i.contains(a) && ((h = l.current) == null || h.removeChild(a)), d == null || d.disconnect();
    };
  }, [e, w, r, c, t, o, x]), S.createElement("react-child", {
    ref: l,
    style: {
      display: "contents"
    }
  }, ...s);
});
function Cn(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function yn(e, n = !1) {
  try {
    if (Re(e))
      return e;
    if (n && !Cn(e))
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
function v(e, n) {
  return ce(() => yn(e, n), [e, n]);
}
function bn({
  value: e,
  onValueChange: n
}) {
  const [r, c] = le(e), o = D(n);
  o.current = n;
  const t = D(r);
  return t.current = r, V(() => {
    o.current(r);
  }, [r]), V(() => {
    Be(e, t.current) || c(e);
  }, [e]), [r, c];
}
const In = ({
  children: e,
  ...n
}) => /* @__PURE__ */ g.jsx(g.Fragment, {
  children: e(n)
});
function me(e) {
  return S.createElement(In, {
    children: e
  });
}
function he(e, n, r) {
  const c = e.filter(Boolean);
  if (c.length !== 0)
    return c.map((o, t) => {
      var x, w;
      if (typeof o != "object")
        return n != null && n.fallback ? n.fallback(o) : o;
      const l = n != null && n.itemPropsTransformer ? n == null ? void 0 : n.itemPropsTransformer({
        ...o.props,
        key: ((x = o.props) == null ? void 0 : x.key) ?? (r ? `${r}-${t}` : `${t}`)
      }) : {
        ...o.props,
        key: ((w = o.props) == null ? void 0 : w.key) ?? (r ? `${r}-${t}` : `${t}`)
      };
      let s = l;
      Object.keys(o.slots).forEach((a) => {
        if (!o.slots[a] || !(o.slots[a] instanceof Element) && !o.slots[a].el)
          return;
        const _ = a.split(".");
        _.forEach((p, R) => {
          s[p] || (s[p] = {}), R !== _.length - 1 && (s = l[p]);
        });
        const d = o.slots[a];
        let C, y, i = (n == null ? void 0 : n.clone) ?? !1, h = n == null ? void 0 : n.forceClone;
        d instanceof Element ? C = d : (C = d.el, y = d.callback, i = d.clone ?? i, h = d.forceClone ?? h), h = h ?? !!y, s[_[_.length - 1]] = C ? y ? (...p) => (y(_[_.length - 1], p), /* @__PURE__ */ g.jsx(H, {
          ...o.ctx,
          params: p,
          forceClone: h,
          children: /* @__PURE__ */ g.jsx(E, {
            slot: C,
            clone: i
          })
        })) : me((p) => /* @__PURE__ */ g.jsx(H, {
          ...o.ctx,
          forceClone: h,
          children: /* @__PURE__ */ g.jsx(E, {
            ...p,
            slot: C,
            clone: i
          })
        })) : s[_[_.length - 1]], s = l;
      });
      const u = (n == null ? void 0 : n.children) || "children";
      return o[u] ? l[u] = he(o[u], n, `${t}`) : n != null && n.children && (l[u] = void 0, Reflect.deleteProperty(l, u)), l;
    });
}
function oe(e, n) {
  return e ? n != null && n.forceClone || n != null && n.params ? me((r) => /* @__PURE__ */ g.jsx(H, {
    forceClone: n == null ? void 0 : n.forceClone,
    params: n == null ? void 0 : n.params,
    children: /* @__PURE__ */ g.jsx(E, {
      slot: e,
      clone: n == null ? void 0 : n.clone,
      ...r
    })
  })) : /* @__PURE__ */ g.jsx(E, {
    slot: e,
    clone: n == null ? void 0 : n.clone
  }) : null;
}
function T({
  key: e,
  slots: n,
  targets: r
}, c) {
  return n[e] ? (...o) => r ? r.map((t, l) => /* @__PURE__ */ g.jsx(S.Fragment, {
    children: oe(t, {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }, l)) : /* @__PURE__ */ g.jsx(g.Fragment, {
    children: oe(n[e], {
      clone: !0,
      params: o,
      forceClone: !0
    })
  }) : void 0;
}
const {
  useItems: vn,
  withItemsContextProvider: En,
  ItemHandler: kn
} = ke("antd-cascader-options");
function Rn(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const Tn = _n(En(["default", "options"], ({
  slots: e,
  children: n,
  onValueChange: r,
  onChange: c,
  displayRender: o,
  elRef: t,
  getPopupContainer: l,
  tagRender: s,
  maxTagPlaceholder: u,
  dropdownRender: x,
  popupRender: w,
  optionRender: a,
  showSearch: _,
  options: d,
  setSlotParams: C,
  onLoadData: y,
  ...i
}) => {
  const h = v(l), p = v(o), R = v(s), f = v(a), P = v(x), m = v(w), b = v(u), k = typeof _ == "object" || e["showSearch.render"], I = Rn(_), _e = v(I.filter), ge = v(I.render), pe = v(I.sort), [xe, we] = bn({
    onValueChange: r,
    value: i.value
  }), {
    items: W
  } = vn(), G = W.options.length > 0 ? W.options : W.default;
  return /* @__PURE__ */ g.jsxs(g.Fragment, {
    children: [/* @__PURE__ */ g.jsx("div", {
      style: {
        display: "none"
      },
      children: n
    }), /* @__PURE__ */ g.jsx(Pe, {
      ...i,
      ref: t,
      value: xe,
      options: ce(() => d || he(G, {
        clone: !0
      }), [d, G]),
      showSearch: k ? {
        ...I,
        filter: _e || I.filter,
        render: e["showSearch.render"] ? T({
          slots: e,
          key: "showSearch.render"
        }) : ge || I.render,
        sort: pe || I.sort
      } : _,
      loadData: y,
      optionRender: f,
      getPopupContainer: h,
      prefix: e.prefix ? /* @__PURE__ */ g.jsx(E, {
        slot: e.prefix
      }) : i.prefix,
      dropdownRender: e.dropdownRender ? T({
        slots: e,
        key: "dropdownRender"
      }) : P,
      popupRender: e.popupRender ? T({
        slots: e,
        key: "popupRender"
      }) : m,
      displayRender: e.displayRender ? T({
        slots: e,
        key: "displayRender"
      }) : p,
      tagRender: e.tagRender ? T({
        slots: e,
        key: "tagRender"
      }) : R,
      onChange: (J, ...Ce) => {
        c == null || c(J, ...Ce), we(J);
      },
      suffixIcon: e.suffixIcon ? /* @__PURE__ */ g.jsx(E, {
        slot: e.suffixIcon
      }) : i.suffixIcon,
      expandIcon: e.expandIcon ? /* @__PURE__ */ g.jsx(E, {
        slot: e.expandIcon
      }) : i.expandIcon,
      removeIcon: e.removeIcon ? /* @__PURE__ */ g.jsx(E, {
        slot: e.removeIcon
      }) : i.removeIcon,
      notFoundContent: e.notFoundContent ? /* @__PURE__ */ g.jsx(E, {
        slot: e.notFoundContent
      }) : i.notFoundContent,
      maxTagPlaceholder: e.maxTagPlaceholder ? T({
        slots: e,
        key: "maxTagPlaceholder"
      }) : b || u,
      allowClear: e["allowClear.clearIcon"] ? {
        clearIcon: /* @__PURE__ */ g.jsx(E, {
          slot: e["allowClear.clearIcon"]
        })
      } : i.allowClear
    })]
  });
}));
export {
  Tn as Cascader,
  Tn as default
};
