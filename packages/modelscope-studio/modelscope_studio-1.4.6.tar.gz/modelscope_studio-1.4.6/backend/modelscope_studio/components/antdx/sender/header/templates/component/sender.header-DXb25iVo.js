import { i as gn, a as Ne, r as hn, Z as ce, g as bn, c as le } from "./Index-GV9lDdRT.js";
const p = window.ms_globals.React, F = window.ms_globals.React, vn = window.ms_globals.React.forwardRef, K = window.ms_globals.React.useRef, mn = window.ms_globals.React.useState, ee = window.ms_globals.React.useEffect, pn = window.ms_globals.React.isValidElement, yn = window.ms_globals.React.version, En = window.ms_globals.React.useLayoutEffect, at = window.ms_globals.ReactDOM, Ie = window.ms_globals.ReactDOM.createPortal, _n = window.ms_globals.internalContext.useContextPropsContext, Sn = window.ms_globals.antdIcons.CloseOutlined, wn = window.ms_globals.antd.Button, Cn = window.ms_globals.antd.ConfigProvider;
var Rn = /\s/;
function Pn(e) {
  for (var t = e.length; t-- && Rn.test(e.charAt(t)); )
    ;
  return t;
}
var Tn = /^\s+/;
function xn(e) {
  return e && e.slice(0, Pn(e) + 1).replace(Tn, "");
}
var st = NaN, On = /^[-+]0x[0-9a-f]+$/i, An = /^0b[01]+$/i, Ln = /^0o[0-7]+$/i, kn = parseInt;
function ut(e) {
  if (typeof e == "number")
    return e;
  if (gn(e))
    return st;
  if (Ne(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = Ne(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = xn(e);
  var n = An.test(e);
  return n || Ln.test(e) ? kn(e.slice(2), n ? 2 : 8) : On.test(e) ? st : +e;
}
var Oe = function() {
  return hn.Date.now();
}, jn = "Expected a function", In = Math.max, Nn = Math.min;
function Mn(e, t, n) {
  var r, o, i, a, s, l, c = 0, v = !1, u = !1, d = !0;
  if (typeof e != "function")
    throw new TypeError(jn);
  t = ut(t) || 0, Ne(n) && (v = !!n.leading, u = "maxWait" in n, i = u ? In(ut(n.maxWait) || 0, t) : i, d = "trailing" in n ? !!n.trailing : d);
  function f(m) {
    var C = r, L = o;
    return r = o = void 0, c = m, a = e.apply(L, C), a;
  }
  function h(m) {
    return c = m, s = setTimeout(_, t), v ? f(m) : a;
  }
  function S(m) {
    var C = m - l, L = m - c, Q = t - C;
    return u ? Nn(Q, i - L) : Q;
  }
  function y(m) {
    var C = m - l, L = m - c;
    return l === void 0 || C >= t || C < 0 || u && L >= i;
  }
  function _() {
    var m = Oe();
    if (y(m))
      return w(m);
    s = setTimeout(_, S(m));
  }
  function w(m) {
    return s = void 0, d && r ? f(m) : (r = o = void 0, a);
  }
  function P() {
    s !== void 0 && clearTimeout(s), c = 0, r = l = o = s = void 0;
  }
  function E() {
    return s === void 0 ? a : w(Oe());
  }
  function T() {
    var m = Oe(), C = y(m);
    if (r = arguments, o = this, l = m, C) {
      if (s === void 0)
        return h(l);
      if (u)
        return clearTimeout(s), s = setTimeout(_, t), f(l);
    }
    return s === void 0 && (s = setTimeout(_, t)), a;
  }
  return T.cancel = P, T.flush = E, T;
}
var At = {
  exports: {}
}, me = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var $n = F, Dn = Symbol.for("react.element"), Fn = Symbol.for("react.fragment"), Vn = Object.prototype.hasOwnProperty, Un = $n.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Kn = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function Lt(e, t, n) {
  var r, o = {}, i = null, a = null;
  n !== void 0 && (i = "" + n), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (a = t.ref);
  for (r in t) Vn.call(t, r) && !Kn.hasOwnProperty(r) && (o[r] = t[r]);
  if (e && e.defaultProps) for (r in t = e.defaultProps, t) o[r] === void 0 && (o[r] = t[r]);
  return {
    $$typeof: Dn,
    type: e,
    key: i,
    ref: a,
    props: o,
    _owner: Un.current
  };
}
me.Fragment = Fn;
me.jsx = Lt;
me.jsxs = Lt;
At.exports = me;
var Ae = At.exports;
const {
  SvelteComponent: Wn,
  assign: ct,
  binding_callbacks: lt,
  check_outros: Hn,
  children: kt,
  claim_element: jt,
  claim_space: zn,
  component_subscribe: ft,
  compute_slots: Bn,
  create_slot: Qn,
  detach: Y,
  element: It,
  empty: dt,
  exclude_internal_props: vt,
  get_all_dirty_from_scope: Gn,
  get_slot_changes: qn,
  group_outros: Yn,
  init: Jn,
  insert_hydration: fe,
  safe_not_equal: Xn,
  set_custom_element_data: Nt,
  space: Zn,
  transition_in: de,
  transition_out: Me,
  update_slot_base: er
} = window.__gradio__svelte__internal, {
  beforeUpdate: tr,
  getContext: nr,
  onDestroy: rr,
  setContext: or
} = window.__gradio__svelte__internal;
function mt(e) {
  let t, n;
  const r = (
    /*#slots*/
    e[7].default
  ), o = Qn(
    r,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = It("svelte-slot"), o && o.c(), this.h();
    },
    l(i) {
      t = jt(i, "SVELTE-SLOT", {
        class: !0
      });
      var a = kt(t);
      o && o.l(a), a.forEach(Y), this.h();
    },
    h() {
      Nt(t, "class", "svelte-1rt0kpf");
    },
    m(i, a) {
      fe(i, t, a), o && o.m(t, null), e[9](t), n = !0;
    },
    p(i, a) {
      o && o.p && (!n || a & /*$$scope*/
      64) && er(
        o,
        r,
        i,
        /*$$scope*/
        i[6],
        n ? qn(
          r,
          /*$$scope*/
          i[6],
          a,
          null
        ) : Gn(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      n || (de(o, i), n = !0);
    },
    o(i) {
      Me(o, i), n = !1;
    },
    d(i) {
      i && Y(t), o && o.d(i), e[9](null);
    }
  };
}
function ir(e) {
  let t, n, r, o, i = (
    /*$$slots*/
    e[4].default && mt(e)
  );
  return {
    c() {
      t = It("react-portal-target"), n = Zn(), i && i.c(), r = dt(), this.h();
    },
    l(a) {
      t = jt(a, "REACT-PORTAL-TARGET", {
        class: !0
      }), kt(t).forEach(Y), n = zn(a), i && i.l(a), r = dt(), this.h();
    },
    h() {
      Nt(t, "class", "svelte-1rt0kpf");
    },
    m(a, s) {
      fe(a, t, s), e[8](t), fe(a, n, s), i && i.m(a, s), fe(a, r, s), o = !0;
    },
    p(a, [s]) {
      /*$$slots*/
      a[4].default ? i ? (i.p(a, s), s & /*$$slots*/
      16 && de(i, 1)) : (i = mt(a), i.c(), de(i, 1), i.m(r.parentNode, r)) : i && (Yn(), Me(i, 1, 1, () => {
        i = null;
      }), Hn());
    },
    i(a) {
      o || (de(i), o = !0);
    },
    o(a) {
      Me(i), o = !1;
    },
    d(a) {
      a && (Y(t), Y(n), Y(r)), e[8](null), i && i.d(a);
    }
  };
}
function pt(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function ar(e, t, n) {
  let r, o, {
    $$slots: i = {},
    $$scope: a
  } = t;
  const s = Bn(i);
  let {
    svelteInit: l
  } = t;
  const c = ce(pt(t)), v = ce();
  ft(e, v, (E) => n(0, r = E));
  const u = ce();
  ft(e, u, (E) => n(1, o = E));
  const d = [], f = nr("$$ms-gr-react-wrapper"), {
    slotKey: h,
    slotIndex: S,
    subSlotIndex: y
  } = bn() || {}, _ = l({
    parent: f,
    props: c,
    target: v,
    slot: u,
    slotKey: h,
    slotIndex: S,
    subSlotIndex: y,
    onDestroy(E) {
      d.push(E);
    }
  });
  or("$$ms-gr-react-wrapper", _), tr(() => {
    c.set(pt(t));
  }), rr(() => {
    d.forEach((E) => E());
  });
  function w(E) {
    lt[E ? "unshift" : "push"](() => {
      r = E, v.set(r);
    });
  }
  function P(E) {
    lt[E ? "unshift" : "push"](() => {
      o = E, u.set(o);
    });
  }
  return e.$$set = (E) => {
    n(17, t = ct(ct({}, t), vt(E))), "svelteInit" in E && n(5, l = E.svelteInit), "$$scope" in E && n(6, a = E.$$scope);
  }, t = vt(t), [r, o, v, u, s, l, a, i, w, P];
}
class sr extends Wn {
  constructor(t) {
    super(), Jn(this, t, ar, ir, Xn, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: to
} = window.__gradio__svelte__internal, yt = window.ms_globals.rerender, Le = window.ms_globals.tree;
function ur(e, t = {}) {
  function n(r) {
    const o = ce(), i = new sr({
      ...r,
      props: {
        svelteInit(a) {
          window.ms_globals.autokey += 1;
          const s = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: e,
            props: a.props,
            slot: a.slot,
            target: a.target,
            slotIndex: a.slotIndex,
            subSlotIndex: a.subSlotIndex,
            ignore: t.ignore,
            slotKey: a.slotKey,
            nodes: []
          }, l = a.parent ?? Le;
          return l.nodes = [...l.nodes, s], yt({
            createPortal: Ie,
            node: Le
          }), a.onDestroy(() => {
            l.nodes = l.nodes.filter((c) => c.svelteInstance !== o), yt({
              createPortal: Ie,
              node: Le
            });
          }), s;
        },
        ...r.props
      }
    });
    return o.set(i), i;
  }
  return new Promise((r) => {
    window.ms_globals.initializePromise.then(() => {
      r(n);
    });
  });
}
const cr = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function lr(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const r = e[n];
    return t[n] = fr(n, r), t;
  }, {}) : {};
}
function fr(e, t) {
  return typeof t == "number" && !cr.includes(e) ? t + "px" : t;
}
function $e(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const o = F.Children.toArray(e._reactElement.props.children).map((i) => {
      if (F.isValidElement(i) && i.props.__slot__) {
        const {
          portals: a,
          clonedElement: s
        } = $e(i.props.el);
        return F.cloneElement(i, {
          ...i.props,
          el: s,
          children: [...F.Children.toArray(i.props.children), ...a]
        });
      }
      return null;
    });
    return o.originalChildren = e._reactElement.props.children, t.push(Ie(F.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: o
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((o) => {
    e.getEventListeners(o).forEach(({
      listener: a,
      type: s,
      useCapture: l
    }) => {
      n.addEventListener(s, a, l);
    });
  });
  const r = Array.from(e.childNodes);
  for (let o = 0; o < r.length; o++) {
    const i = r[o];
    if (i.nodeType === 1) {
      const {
        clonedElement: a,
        portals: s
      } = $e(i);
      t.push(...s), n.appendChild(a);
    } else i.nodeType === 3 && n.appendChild(i.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function dr(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const vr = vn(({
  slot: e,
  clone: t,
  className: n,
  style: r,
  observeAttributes: o
}, i) => {
  const a = K(), [s, l] = mn([]), {
    forceClone: c
  } = _n(), v = c ? !0 : t;
  return ee(() => {
    var S;
    if (!a.current || !e)
      return;
    let u = e;
    function d() {
      let y = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (y = u.children[0], y.tagName.toLowerCase() === "react-portal-target" && y.children[0] && (y = y.children[0])), dr(i, y), n && y.classList.add(...n.split(" ")), r) {
        const _ = lr(r);
        Object.keys(_).forEach((w) => {
          y.style[w] = _[w];
        });
      }
    }
    let f = null, h = null;
    if (v && window.MutationObserver) {
      let y = function() {
        var E, T, m;
        (E = a.current) != null && E.contains(u) && ((T = a.current) == null || T.removeChild(u));
        const {
          portals: w,
          clonedElement: P
        } = $e(e);
        u = P, l(w), u.style.display = "contents", h && clearTimeout(h), h = setTimeout(() => {
          d();
        }, 50), (m = a.current) == null || m.appendChild(u);
      };
      y();
      const _ = Mn(() => {
        y(), f == null || f.disconnect(), f == null || f.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: o
        });
      }, 50);
      f = new window.MutationObserver(_), f.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", d(), (S = a.current) == null || S.appendChild(u);
    return () => {
      var y, _;
      u.style.display = "", (y = a.current) != null && y.contains(u) && ((_ = a.current) == null || _.removeChild(u)), f == null || f.disconnect();
    };
  }, [e, v, n, r, i, o, c]), F.createElement("react-child", {
    ref: a,
    style: {
      display: "contents"
    }
  }, ...s);
});
function k(e) {
  "@babel/helpers - typeof";
  return k = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, k(e);
}
function mr(e, t) {
  if (k(e) != "object" || !e) return e;
  var n = e[Symbol.toPrimitive];
  if (n !== void 0) {
    var r = n.call(e, t);
    if (k(r) != "object") return r;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function Mt(e) {
  var t = mr(e, "string");
  return k(t) == "symbol" ? t : t + "";
}
function x(e, t, n) {
  return (t = Mt(t)) in e ? Object.defineProperty(e, t, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = n, e;
}
function Et(e, t) {
  var n = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var r = Object.getOwnPropertySymbols(e);
    t && (r = r.filter(function(o) {
      return Object.getOwnPropertyDescriptor(e, o).enumerable;
    })), n.push.apply(n, r);
  }
  return n;
}
function b(e) {
  for (var t = 1; t < arguments.length; t++) {
    var n = arguments[t] != null ? arguments[t] : {};
    t % 2 ? Et(Object(n), !0).forEach(function(r) {
      x(e, r, n[r]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : Et(Object(n)).forEach(function(r) {
      Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(n, r));
    });
  }
  return e;
}
function pr(e) {
  if (Array.isArray(e)) return e;
}
function yr(e, t) {
  var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (n != null) {
    var r, o, i, a, s = [], l = !0, c = !1;
    try {
      if (i = (n = n.call(e)).next, t === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (r = i.call(n)).done) && (s.push(r.value), s.length !== t); l = !0) ;
    } catch (v) {
      c = !0, o = v;
    } finally {
      try {
        if (!l && n.return != null && (a = n.return(), Object(a) !== a)) return;
      } finally {
        if (c) throw o;
      }
    }
    return s;
  }
}
function gt(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var n = 0, r = Array(t); n < t; n++) r[n] = e[n];
  return r;
}
function Er(e, t) {
  if (e) {
    if (typeof e == "string") return gt(e, t);
    var n = {}.toString.call(e).slice(8, -1);
    return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? gt(e, t) : void 0;
  }
}
function gr() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function D(e, t) {
  return pr(e) || yr(e, t) || Er(e, t) || gr();
}
function ht(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function hr(e) {
  return e && k(e) === "object" && ht(e.nativeElement) ? e.nativeElement : ht(e) ? e : null;
}
function br(e) {
  var t = hr(e);
  if (t)
    return t;
  if (e instanceof F.Component) {
    var n;
    return (n = at.findDOMNode) === null || n === void 0 ? void 0 : n.call(at, e);
  }
  return null;
}
var $t = {
  exports: {}
}, g = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ge = Symbol.for("react.element"), qe = Symbol.for("react.portal"), pe = Symbol.for("react.fragment"), ye = Symbol.for("react.strict_mode"), Ee = Symbol.for("react.profiler"), ge = Symbol.for("react.provider"), he = Symbol.for("react.context"), _r = Symbol.for("react.server_context"), be = Symbol.for("react.forward_ref"), _e = Symbol.for("react.suspense"), Se = Symbol.for("react.suspense_list"), we = Symbol.for("react.memo"), Ce = Symbol.for("react.lazy"), Sr = Symbol.for("react.offscreen"), Dt;
Dt = Symbol.for("react.module.reference");
function j(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case Ge:
        switch (e = e.type, e) {
          case pe:
          case Ee:
          case ye:
          case _e:
          case Se:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case _r:
              case he:
              case be:
              case Ce:
              case we:
              case ge:
                return e;
              default:
                return t;
            }
        }
      case qe:
        return t;
    }
  }
}
g.ContextConsumer = he;
g.ContextProvider = ge;
g.Element = Ge;
g.ForwardRef = be;
g.Fragment = pe;
g.Lazy = Ce;
g.Memo = we;
g.Portal = qe;
g.Profiler = Ee;
g.StrictMode = ye;
g.Suspense = _e;
g.SuspenseList = Se;
g.isAsyncMode = function() {
  return !1;
};
g.isConcurrentMode = function() {
  return !1;
};
g.isContextConsumer = function(e) {
  return j(e) === he;
};
g.isContextProvider = function(e) {
  return j(e) === ge;
};
g.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === Ge;
};
g.isForwardRef = function(e) {
  return j(e) === be;
};
g.isFragment = function(e) {
  return j(e) === pe;
};
g.isLazy = function(e) {
  return j(e) === Ce;
};
g.isMemo = function(e) {
  return j(e) === we;
};
g.isPortal = function(e) {
  return j(e) === qe;
};
g.isProfiler = function(e) {
  return j(e) === Ee;
};
g.isStrictMode = function(e) {
  return j(e) === ye;
};
g.isSuspense = function(e) {
  return j(e) === _e;
};
g.isSuspenseList = function(e) {
  return j(e) === Se;
};
g.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === pe || e === Ee || e === ye || e === _e || e === Se || e === Sr || typeof e == "object" && e !== null && (e.$$typeof === Ce || e.$$typeof === we || e.$$typeof === ge || e.$$typeof === he || e.$$typeof === be || e.$$typeof === Dt || e.getModuleId !== void 0);
};
g.typeOf = j;
$t.exports = g;
var ke = $t.exports, wr = Symbol.for("react.element"), Cr = Symbol.for("react.transitional.element"), Rr = Symbol.for("react.fragment");
function Pr(e) {
  return (
    // Base object type
    e && k(e) === "object" && // React Element type
    (e.$$typeof === wr || e.$$typeof === Cr) && // React Fragment type
    e.type === Rr
  );
}
var Tr = Number(yn.split(".")[0]), xr = function(t, n) {
  typeof t == "function" ? t(n) : k(t) === "object" && t && "current" in t && (t.current = n);
}, Or = function(t) {
  var n, r;
  if (!t)
    return !1;
  if (Ft(t) && Tr >= 19)
    return !0;
  var o = ke.isMemo(t) ? t.type.type : t.type;
  return !(typeof o == "function" && !((n = o.prototype) !== null && n !== void 0 && n.render) && o.$$typeof !== ke.ForwardRef || typeof t == "function" && !((r = t.prototype) !== null && r !== void 0 && r.render) && t.$$typeof !== ke.ForwardRef);
};
function Ft(e) {
  return /* @__PURE__ */ pn(e) && !Pr(e);
}
var Ar = function(t) {
  if (t && Ft(t)) {
    var n = t;
    return n.props.propertyIsEnumerable("ref") ? n.props.ref : n.ref;
  }
  return null;
};
function Lr(e, t) {
  if (e == null) return {};
  var n = {};
  for (var r in e) if ({}.hasOwnProperty.call(e, r)) {
    if (t.indexOf(r) !== -1) continue;
    n[r] = e[r];
  }
  return n;
}
function bt(e, t) {
  if (e == null) return {};
  var n, r, o = Lr(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (r = 0; r < i.length; r++) n = i[r], t.indexOf(n) === -1 && {}.propertyIsEnumerable.call(e, n) && (o[n] = e[n]);
  }
  return o;
}
var kr = /* @__PURE__ */ p.createContext({});
function Vt(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function _t(e, t) {
  for (var n = 0; n < t.length; n++) {
    var r = t[n];
    r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, Mt(r.key), r);
  }
}
function Ut(e, t, n) {
  return t && _t(e.prototype, t), n && _t(e, n), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function De(e, t) {
  return De = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, r) {
    return n.__proto__ = r, n;
  }, De(e, t);
}
function Kt(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && De(e, t);
}
function ve(e) {
  return ve = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, ve(e);
}
function Wt() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Wt = function() {
    return !!e;
  })();
}
function Fe(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function jr(e, t) {
  if (t && (k(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return Fe(e);
}
function Ht(e) {
  var t = Wt();
  return function() {
    var n, r = ve(e);
    if (t) {
      var o = ve(this).constructor;
      n = Reflect.construct(r, arguments, o);
    } else n = r.apply(this, arguments);
    return jr(this, n);
  };
}
var Ir = /* @__PURE__ */ function(e) {
  Kt(n, e);
  var t = Ht(n);
  function n() {
    return Vt(this, n), t.apply(this, arguments);
  }
  return Ut(n, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), n;
}(p.Component);
function Ve(e) {
  var t = p.useRef();
  t.current = e;
  var n = p.useCallback(function() {
    for (var r, o = arguments.length, i = new Array(o), a = 0; a < o; a++)
      i[a] = arguments[a];
    return (r = t.current) === null || r === void 0 ? void 0 : r.call.apply(r, [t].concat(i));
  }, []);
  return n;
}
function Ye() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
function Ue(e) {
  var t = p.useRef(!1), n = p.useState(e), r = D(n, 2), o = r[0], i = r[1];
  p.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function a(s, l) {
    l && t.current || i(s);
  }
  return [o, a];
}
function Nr(e) {
  var t = p.useReducer(function(s) {
    return s + 1;
  }, 0), n = D(t, 2), r = n[1], o = p.useRef(e), i = Ve(function() {
    return o.current;
  }), a = Ve(function(s) {
    o.current = typeof s == "function" ? s(o.current) : s, r();
  });
  return [i, a];
}
var U = "none", ie = "appear", ae = "enter", se = "leave", St = "none", N = "prepare", J = "start", X = "active", Je = "end", zt = "prepared";
function wt(e, t) {
  var n = {};
  return n[e.toLowerCase()] = t.toLowerCase(), n["Webkit".concat(e)] = "webkit".concat(t), n["Moz".concat(e)] = "moz".concat(t), n["ms".concat(e)] = "MS".concat(t), n["O".concat(e)] = "o".concat(t.toLowerCase()), n;
}
function Mr(e, t) {
  var n = {
    animationend: wt("Animation", "AnimationEnd"),
    transitionend: wt("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete n.animationend.animation, "TransitionEvent" in t || delete n.transitionend.transition), n;
}
var $r = Mr(Ye(), typeof window < "u" ? window : {}), Bt = {};
if (Ye()) {
  var Dr = document.createElement("div");
  Bt = Dr.style;
}
var ue = {};
function Qt(e) {
  if (ue[e])
    return ue[e];
  var t = $r[e];
  if (t)
    for (var n = Object.keys(t), r = n.length, o = 0; o < r; o += 1) {
      var i = n[o];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in Bt)
        return ue[e] = t[i], ue[e];
    }
  return "";
}
var Gt = Qt("animationend"), qt = Qt("transitionend"), Yt = !!(Gt && qt), Ct = Gt || "animationend", Rt = qt || "transitionend";
function Pt(e, t) {
  if (!e) return null;
  if (k(e) === "object") {
    var n = t.replace(/-\w/g, function(r) {
      return r[1].toUpperCase();
    });
    return e[n];
  }
  return "".concat(e, "-").concat(t);
}
const Fr = function(e) {
  var t = K();
  function n(o) {
    o && (o.removeEventListener(Rt, e), o.removeEventListener(Ct, e));
  }
  function r(o) {
    t.current && t.current !== o && n(t.current), o && o !== t.current && (o.addEventListener(Rt, e), o.addEventListener(Ct, e), t.current = o);
  }
  return p.useEffect(function() {
    return function() {
      n(t.current);
    };
  }, []), [r, n];
};
var Jt = Ye() ? En : ee, Xt = function(t) {
  return +setTimeout(t, 16);
}, Zt = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (Xt = function(t) {
  return window.requestAnimationFrame(t);
}, Zt = function(t) {
  return window.cancelAnimationFrame(t);
});
var Tt = 0, Xe = /* @__PURE__ */ new Map();
function en(e) {
  Xe.delete(e);
}
var Ke = function(t) {
  var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  Tt += 1;
  var r = Tt;
  function o(i) {
    if (i === 0)
      en(r), t();
    else {
      var a = Xt(function() {
        o(i - 1);
      });
      Xe.set(r, a);
    }
  }
  return o(n), r;
};
Ke.cancel = function(e) {
  var t = Xe.get(e);
  return en(e), Zt(t);
};
const Vr = function() {
  var e = p.useRef(null);
  function t() {
    Ke.cancel(e.current);
  }
  function n(r) {
    var o = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = Ke(function() {
      o <= 1 ? r({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : n(r, o - 1);
    });
    e.current = i;
  }
  return p.useEffect(function() {
    return function() {
      t();
    };
  }, []), [n, t];
};
var Ur = [N, J, X, Je], Kr = [N, zt], tn = !1, Wr = !0;
function nn(e) {
  return e === X || e === Je;
}
const Hr = function(e, t, n) {
  var r = Ue(St), o = D(r, 2), i = o[0], a = o[1], s = Vr(), l = D(s, 2), c = l[0], v = l[1];
  function u() {
    a(N, !0);
  }
  var d = t ? Kr : Ur;
  return Jt(function() {
    if (i !== St && i !== Je) {
      var f = d.indexOf(i), h = d[f + 1], S = n(i);
      S === tn ? a(h, !0) : h && c(function(y) {
        function _() {
          y.isCanceled() || a(h, !0);
        }
        S === !0 ? _() : Promise.resolve(S).then(_);
      });
    }
  }, [e, i]), p.useEffect(function() {
    return function() {
      v();
    };
  }, []), [u, i];
};
function zr(e, t, n, r) {
  var o = r.motionEnter, i = o === void 0 ? !0 : o, a = r.motionAppear, s = a === void 0 ? !0 : a, l = r.motionLeave, c = l === void 0 ? !0 : l, v = r.motionDeadline, u = r.motionLeaveImmediately, d = r.onAppearPrepare, f = r.onEnterPrepare, h = r.onLeavePrepare, S = r.onAppearStart, y = r.onEnterStart, _ = r.onLeaveStart, w = r.onAppearActive, P = r.onEnterActive, E = r.onLeaveActive, T = r.onAppearEnd, m = r.onEnterEnd, C = r.onLeaveEnd, L = r.onVisibleChanged, Q = Ue(), G = D(Q, 2), I = G[0], W = G[1], O = Nr(U), H = D(O, 2), V = H[0], z = H[1], Re = Ue(null), q = D(Re, 2), an = q[0], Ze = q[1], M = V(), te = K(!1), Pe = K(null);
  function ne() {
    return n();
  }
  var et = K(!1);
  function tt() {
    z(U), Ze(null, !0);
  }
  var nt = Ve(function(A) {
    var R = V();
    if (R !== U) {
      var $ = ne();
      if (!(A && !A.deadline && A.target !== $)) {
        var re = et.current, oe;
        R === ie && re ? oe = T == null ? void 0 : T($, A) : R === ae && re ? oe = m == null ? void 0 : m($, A) : R === se && re && (oe = C == null ? void 0 : C($, A)), re && oe !== !1 && tt();
      }
    }
  }), sn = Fr(nt), un = D(sn, 1), cn = un[0], rt = function(R) {
    switch (R) {
      case ie:
        return x(x(x({}, N, d), J, S), X, w);
      case ae:
        return x(x(x({}, N, f), J, y), X, P);
      case se:
        return x(x(x({}, N, h), J, _), X, E);
      default:
        return {};
    }
  }, Z = p.useMemo(function() {
    return rt(M);
  }, [M]), ln = Hr(M, !e, function(A) {
    if (A === N) {
      var R = Z[N];
      return R ? R(ne()) : tn;
    }
    if (B in Z) {
      var $;
      Ze((($ = Z[B]) === null || $ === void 0 ? void 0 : $.call(Z, ne(), null)) || null);
    }
    return B === X && M !== U && (cn(ne()), v > 0 && (clearTimeout(Pe.current), Pe.current = setTimeout(function() {
      nt({
        deadline: !0
      });
    }, v))), B === zt && tt(), Wr;
  }), ot = D(ln, 2), fn = ot[0], B = ot[1], dn = nn(B);
  et.current = dn;
  var it = K(null);
  Jt(function() {
    if (!(te.current && it.current === t)) {
      W(t);
      var A = te.current;
      te.current = !0;
      var R;
      !A && t && s && (R = ie), A && t && i && (R = ae), (A && !t && c || !A && u && !t && c) && (R = se);
      var $ = rt(R);
      R && (e || $[N]) ? (z(R), fn()) : z(U), it.current = t;
    }
  }, [t]), ee(function() {
    // Cancel appear
    (M === ie && !s || // Cancel enter
    M === ae && !i || // Cancel leave
    M === se && !c) && z(U);
  }, [s, i, c]), ee(function() {
    return function() {
      te.current = !1, clearTimeout(Pe.current);
    };
  }, []);
  var Te = p.useRef(!1);
  ee(function() {
    I && (Te.current = !0), I !== void 0 && M === U && ((Te.current || I) && (L == null || L(I)), Te.current = !0);
  }, [I, M]);
  var xe = an;
  return Z[N] && B === J && (xe = b({
    transition: "none"
  }, xe)), [M, B, xe, I ?? t];
}
function Br(e) {
  var t = e;
  k(e) === "object" && (t = e.transitionSupport);
  function n(o, i) {
    return !!(o.motionName && t && i !== !1);
  }
  var r = /* @__PURE__ */ p.forwardRef(function(o, i) {
    var a = o.visible, s = a === void 0 ? !0 : a, l = o.removeOnLeave, c = l === void 0 ? !0 : l, v = o.forceRender, u = o.children, d = o.motionName, f = o.leavedClassName, h = o.eventProps, S = p.useContext(kr), y = S.motion, _ = n(o, y), w = K(), P = K();
    function E() {
      try {
        return w.current instanceof HTMLElement ? w.current : br(P.current);
      } catch {
        return null;
      }
    }
    var T = zr(_, s, E, o), m = D(T, 4), C = m[0], L = m[1], Q = m[2], G = m[3], I = p.useRef(G);
    G && (I.current = !0);
    var W = p.useCallback(function(q) {
      w.current = q, xr(i, q);
    }, [i]), O, H = b(b({}, h), {}, {
      visible: s
    });
    if (!u)
      O = null;
    else if (C === U)
      G ? O = u(b({}, H), W) : !c && I.current && f ? O = u(b(b({}, H), {}, {
        className: f
      }), W) : v || !c && !f ? O = u(b(b({}, H), {}, {
        style: {
          display: "none"
        }
      }), W) : O = null;
    else {
      var V;
      L === N ? V = "prepare" : nn(L) ? V = "active" : L === J && (V = "start");
      var z = Pt(d, "".concat(C, "-").concat(V));
      O = u(b(b({}, H), {}, {
        className: le(Pt(d, C), x(x({}, z, z && V), d, typeof d == "string")),
        style: Q
      }), W);
    }
    if (/* @__PURE__ */ p.isValidElement(O) && Or(O)) {
      var Re = Ar(O);
      Re || (O = /* @__PURE__ */ p.cloneElement(O, {
        ref: W
      }));
    }
    return /* @__PURE__ */ p.createElement(Ir, {
      ref: P
    }, O);
  });
  return r.displayName = "CSSMotion", r;
}
const rn = Br(Yt);
function We() {
  return We = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var n = arguments[t];
      for (var r in n) ({}).hasOwnProperty.call(n, r) && (e[r] = n[r]);
    }
    return e;
  }, We.apply(null, arguments);
}
var He = "add", ze = "keep", Be = "remove", je = "removed";
function Qr(e) {
  var t;
  return e && k(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, b(b({}, t), {}, {
    key: String(t.key)
  });
}
function Qe() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(Qr);
}
function Gr() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], n = [], r = 0, o = t.length, i = Qe(e), a = Qe(t);
  i.forEach(function(c) {
    for (var v = !1, u = r; u < o; u += 1) {
      var d = a[u];
      if (d.key === c.key) {
        r < u && (n = n.concat(a.slice(r, u).map(function(f) {
          return b(b({}, f), {}, {
            status: He
          });
        })), r = u), n.push(b(b({}, d), {}, {
          status: ze
        })), r += 1, v = !0;
        break;
      }
    }
    v || n.push(b(b({}, c), {}, {
      status: Be
    }));
  }), r < o && (n = n.concat(a.slice(r).map(function(c) {
    return b(b({}, c), {}, {
      status: He
    });
  })));
  var s = {};
  n.forEach(function(c) {
    var v = c.key;
    s[v] = (s[v] || 0) + 1;
  });
  var l = Object.keys(s).filter(function(c) {
    return s[c] > 1;
  });
  return l.forEach(function(c) {
    n = n.filter(function(v) {
      var u = v.key, d = v.status;
      return u !== c || d !== Be;
    }), n.forEach(function(v) {
      v.key === c && (v.status = ze);
    });
  }), n;
}
var qr = ["component", "children", "onVisibleChanged", "onAllRemoved"], Yr = ["status"], Jr = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function Xr(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : rn, n = /* @__PURE__ */ function(r) {
    Kt(i, r);
    var o = Ht(i);
    function i() {
      var a;
      Vt(this, i);
      for (var s = arguments.length, l = new Array(s), c = 0; c < s; c++)
        l[c] = arguments[c];
      return a = o.call.apply(o, [this].concat(l)), x(Fe(a), "state", {
        keyEntities: []
      }), x(Fe(a), "removeKey", function(v) {
        a.setState(function(u) {
          var d = u.keyEntities.map(function(f) {
            return f.key !== v ? f : b(b({}, f), {}, {
              status: je
            });
          });
          return {
            keyEntities: d
          };
        }, function() {
          var u = a.state.keyEntities, d = u.filter(function(f) {
            var h = f.status;
            return h !== je;
          }).length;
          d === 0 && a.props.onAllRemoved && a.props.onAllRemoved();
        });
      }), a;
    }
    return Ut(i, [{
      key: "render",
      value: function() {
        var s = this, l = this.state.keyEntities, c = this.props, v = c.component, u = c.children, d = c.onVisibleChanged;
        c.onAllRemoved;
        var f = bt(c, qr), h = v || p.Fragment, S = {};
        return Jr.forEach(function(y) {
          S[y] = f[y], delete f[y];
        }), delete f.keys, /* @__PURE__ */ p.createElement(h, f, l.map(function(y, _) {
          var w = y.status, P = bt(y, Yr), E = w === He || w === ze;
          return /* @__PURE__ */ p.createElement(t, We({}, S, {
            key: P.key,
            visible: E,
            eventProps: P,
            onVisibleChanged: function(m) {
              d == null || d(m, {
                key: P.key
              }), m || s.removeKey(P.key);
            }
          }), function(T, m) {
            return u(b(b({}, T), {}, {
              index: _
            }), m);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(s, l) {
        var c = s.keys, v = l.keyEntities, u = Qe(c), d = Gr(v, u);
        return {
          keyEntities: d.filter(function(f) {
            var h = v.find(function(S) {
              var y = S.key;
              return f.key === y;
            });
            return !(h && h.status === je && f.status === Be);
          })
        };
      }
    }]), i;
  }(p.Component);
  return x(n, "defaultProps", {
    component: "div"
  }), n;
}
Xr(Yt);
const on = /* @__PURE__ */ p.createContext({}), xt = () => ({
  height: 0
}), Ot = (e) => ({
  height: e.scrollHeight
});
function Zr(e) {
  const {
    title: t,
    onOpenChange: n,
    open: r,
    children: o,
    className: i,
    style: a,
    classNames: s = {},
    styles: l = {},
    closable: c,
    forceRender: v
  } = e, {
    prefixCls: u
  } = p.useContext(on), d = `${u}-header`;
  return /* @__PURE__ */ p.createElement(rn, {
    motionEnter: !0,
    motionLeave: !0,
    motionName: `${d}-motion`,
    leavedClassName: `${d}-motion-hidden`,
    onEnterStart: xt,
    onEnterActive: Ot,
    onLeaveStart: Ot,
    onLeaveActive: xt,
    visible: r,
    forceRender: v
  }, ({
    className: f,
    style: h
  }) => /* @__PURE__ */ p.createElement("div", {
    className: le(d, f, i),
    style: {
      ...h,
      ...a
    }
  }, (c !== !1 || t) && /* @__PURE__ */ p.createElement("div", {
    className: (
      // We follow antd naming standard here.
      // So the header part is use `-header` suffix.
      // Though its little bit weird for double `-header`.
      le(`${d}-header`, s.header)
    ),
    style: {
      ...l.header
    }
  }, /* @__PURE__ */ p.createElement("div", {
    className: `${d}-title`
  }, t), c !== !1 && /* @__PURE__ */ p.createElement("div", {
    className: `${d}-close`
  }, /* @__PURE__ */ p.createElement(wn, {
    type: "text",
    icon: /* @__PURE__ */ p.createElement(Sn, null),
    size: "small",
    onClick: () => {
      n == null || n(!r);
    }
  }))), o && /* @__PURE__ */ p.createElement("div", {
    className: le(`${d}-content`, s.content),
    style: {
      ...l.content
    }
  }, o)));
}
const no = ur(({
  slots: e,
  ...t
}) => {
  const {
    getPrefixCls: n
  } = F.useContext(Cn.ConfigContext);
  return /* @__PURE__ */ Ae.jsx(on.Provider, {
    value: {
      prefixCls: n("sender")
    },
    children: /* @__PURE__ */ Ae.jsx(Zr, {
      ...t,
      title: e.title ? /* @__PURE__ */ Ae.jsx(vr, {
        slot: e.title
      }) : t.title
    })
  });
});
export {
  no as SenderHeader,
  no as default
};
