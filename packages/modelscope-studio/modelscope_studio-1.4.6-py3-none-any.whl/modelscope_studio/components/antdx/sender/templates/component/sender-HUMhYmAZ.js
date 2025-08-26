import { i as vr, a as _t, r as yr, b as br, Z as Ke, g as Sr, c as ee, d as xr } from "./Index-WucvfZrK.js";
const m = window.ms_globals.React, b = window.ms_globals.React, ur = window.ms_globals.React.forwardRef, ne = window.ms_globals.React.useRef, Mn = window.ms_globals.React.useState, me = window.ms_globals.React.useEffect, fr = window.ms_globals.React.version, dr = window.ms_globals.React.isValidElement, pr = window.ms_globals.React.useLayoutEffect, hr = window.ms_globals.React.useImperativeHandle, mr = window.ms_globals.React.memo, gr = window.ms_globals.React.useMemo, zt = window.ms_globals.ReactDOM, wt = window.ms_globals.ReactDOM.createPortal, Er = window.ms_globals.internalContext.useContextPropsContext, Cr = window.ms_globals.internalContext.useSuggestionOpenContext, wr = window.ms_globals.antd.ConfigProvider, Tt = window.ms_globals.antd.theme, Pn = window.ms_globals.antd.Button, _r = window.ms_globals.antd.Input, Tr = window.ms_globals.antd.Flex, Rr = window.ms_globals.antdIcons.CloseOutlined, Mr = window.ms_globals.antdIcons.ClearOutlined, Pr = window.ms_globals.antdIcons.ArrowUpOutlined, Or = window.ms_globals.antdIcons.AudioMutedOutlined, Ar = window.ms_globals.antdIcons.AudioOutlined, Rt = window.ms_globals.antdCssinjs.unit, mt = window.ms_globals.antdCssinjs.token2CSSVar, Ut = window.ms_globals.antdCssinjs.useStyleRegister, kr = window.ms_globals.antdCssinjs.useCSSVarRegister, Ir = window.ms_globals.antdCssinjs.createTheme, Lr = window.ms_globals.antdCssinjs.useCacheToken;
var jr = /\s/;
function $r(e) {
  for (var t = e.length; t-- && jr.test(e.charAt(t)); )
    ;
  return t;
}
var Dr = /^\s+/;
function Nr(e) {
  return e && e.slice(0, $r(e) + 1).replace(Dr, "");
}
var Xt = NaN, Br = /^[-+]0x[0-9a-f]+$/i, Hr = /^0b[01]+$/i, Vr = /^0o[0-7]+$/i, Fr = parseInt;
function Wt(e) {
  if (typeof e == "number")
    return e;
  if (vr(e))
    return Xt;
  if (_t(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = _t(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Nr(e);
  var n = Hr.test(e);
  return n || Vr.test(e) ? Fr(e.slice(2), n ? 2 : 8) : Br.test(e) ? Xt : +e;
}
var gt = function() {
  return yr.Date.now();
}, zr = "Expected a function", Ur = Math.max, Xr = Math.min;
function Wr(e, t, n) {
  var o, r, i, s, a, l, c = 0, f = !1, u = !1, d = !0;
  if (typeof e != "function")
    throw new TypeError(zr);
  t = Wt(t) || 0, _t(n) && (f = !!n.leading, u = "maxWait" in n, i = u ? Ur(Wt(n.maxWait) || 0, t) : i, d = "trailing" in n ? !!n.trailing : d);
  function p(S) {
    var R = o, M = r;
    return o = r = void 0, c = S, s = e.apply(M, R), s;
  }
  function v(S) {
    return c = S, a = setTimeout(x, t), f ? p(S) : s;
  }
  function g(S) {
    var R = S - l, M = S - c, k = t - R;
    return u ? Xr(k, i - M) : k;
  }
  function h(S) {
    var R = S - l, M = S - c;
    return l === void 0 || R >= t || R < 0 || u && M >= i;
  }
  function x() {
    var S = gt();
    if (h(S))
      return E(S);
    a = setTimeout(x, g(S));
  }
  function E(S) {
    return a = void 0, d && o ? p(S) : (o = r = void 0, s);
  }
  function _() {
    a !== void 0 && clearTimeout(a), c = 0, o = l = r = a = void 0;
  }
  function y() {
    return a === void 0 ? s : E(gt());
  }
  function T() {
    var S = gt(), R = h(S);
    if (o = arguments, r = this, l = S, R) {
      if (a === void 0)
        return v(l);
      if (u)
        return clearTimeout(a), a = setTimeout(x, t), p(l);
    }
    return a === void 0 && (a = setTimeout(x, t)), s;
  }
  return T.cancel = _, T.flush = y, T;
}
function Kr(e, t) {
  return br(e, t);
}
var On = {
  exports: {}
}, Je = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Gr = b, qr = Symbol.for("react.element"), Qr = Symbol.for("react.fragment"), Zr = Object.prototype.hasOwnProperty, Yr = Gr.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Jr = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function An(e, t, n) {
  var o, r = {}, i = null, s = null;
  n !== void 0 && (i = "" + n), t.key !== void 0 && (i = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (o in t) Zr.call(t, o) && !Jr.hasOwnProperty(o) && (r[o] = t[o]);
  if (e && e.defaultProps) for (o in t = e.defaultProps, t) r[o] === void 0 && (r[o] = t[o]);
  return {
    $$typeof: qr,
    type: e,
    key: i,
    ref: s,
    props: r,
    _owner: Yr.current
  };
}
Je.Fragment = Qr;
Je.jsx = An;
Je.jsxs = An;
On.exports = Je;
var ce = On.exports;
const {
  SvelteComponent: eo,
  assign: Kt,
  binding_callbacks: Gt,
  check_outros: to,
  children: kn,
  claim_element: In,
  claim_space: no,
  component_subscribe: qt,
  compute_slots: ro,
  create_slot: oo,
  detach: Ee,
  element: Ln,
  empty: Qt,
  exclude_internal_props: Zt,
  get_all_dirty_from_scope: io,
  get_slot_changes: so,
  group_outros: ao,
  init: co,
  insert_hydration: Ge,
  safe_not_equal: lo,
  set_custom_element_data: jn,
  space: uo,
  transition_in: qe,
  transition_out: Mt,
  update_slot_base: fo
} = window.__gradio__svelte__internal, {
  beforeUpdate: po,
  getContext: ho,
  onDestroy: mo,
  setContext: go
} = window.__gradio__svelte__internal;
function Yt(e) {
  let t, n;
  const o = (
    /*#slots*/
    e[7].default
  ), r = oo(
    o,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = Ln("svelte-slot"), r && r.c(), this.h();
    },
    l(i) {
      t = In(i, "SVELTE-SLOT", {
        class: !0
      });
      var s = kn(t);
      r && r.l(s), s.forEach(Ee), this.h();
    },
    h() {
      jn(t, "class", "svelte-1rt0kpf");
    },
    m(i, s) {
      Ge(i, t, s), r && r.m(t, null), e[9](t), n = !0;
    },
    p(i, s) {
      r && r.p && (!n || s & /*$$scope*/
      64) && fo(
        r,
        o,
        i,
        /*$$scope*/
        i[6],
        n ? so(
          o,
          /*$$scope*/
          i[6],
          s,
          null
        ) : io(
          /*$$scope*/
          i[6]
        ),
        null
      );
    },
    i(i) {
      n || (qe(r, i), n = !0);
    },
    o(i) {
      Mt(r, i), n = !1;
    },
    d(i) {
      i && Ee(t), r && r.d(i), e[9](null);
    }
  };
}
function vo(e) {
  let t, n, o, r, i = (
    /*$$slots*/
    e[4].default && Yt(e)
  );
  return {
    c() {
      t = Ln("react-portal-target"), n = uo(), i && i.c(), o = Qt(), this.h();
    },
    l(s) {
      t = In(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), kn(t).forEach(Ee), n = no(s), i && i.l(s), o = Qt(), this.h();
    },
    h() {
      jn(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      Ge(s, t, a), e[8](t), Ge(s, n, a), i && i.m(s, a), Ge(s, o, a), r = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? i ? (i.p(s, a), a & /*$$slots*/
      16 && qe(i, 1)) : (i = Yt(s), i.c(), qe(i, 1), i.m(o.parentNode, o)) : i && (ao(), Mt(i, 1, 1, () => {
        i = null;
      }), to());
    },
    i(s) {
      r || (qe(i), r = !0);
    },
    o(s) {
      Mt(i), r = !1;
    },
    d(s) {
      s && (Ee(t), Ee(n), Ee(o)), e[8](null), i && i.d(s);
    }
  };
}
function Jt(e) {
  const {
    svelteInit: t,
    ...n
  } = e;
  return n;
}
function yo(e, t, n) {
  let o, r, {
    $$slots: i = {},
    $$scope: s
  } = t;
  const a = ro(i);
  let {
    svelteInit: l
  } = t;
  const c = Ke(Jt(t)), f = Ke();
  qt(e, f, (y) => n(0, o = y));
  const u = Ke();
  qt(e, u, (y) => n(1, r = y));
  const d = [], p = ho("$$ms-gr-react-wrapper"), {
    slotKey: v,
    slotIndex: g,
    subSlotIndex: h
  } = Sr() || {}, x = l({
    parent: p,
    props: c,
    target: f,
    slot: u,
    slotKey: v,
    slotIndex: g,
    subSlotIndex: h,
    onDestroy(y) {
      d.push(y);
    }
  });
  go("$$ms-gr-react-wrapper", x), po(() => {
    c.set(Jt(t));
  }), mo(() => {
    d.forEach((y) => y());
  });
  function E(y) {
    Gt[y ? "unshift" : "push"](() => {
      o = y, f.set(o);
    });
  }
  function _(y) {
    Gt[y ? "unshift" : "push"](() => {
      r = y, u.set(r);
    });
  }
  return e.$$set = (y) => {
    n(17, t = Kt(Kt({}, t), Zt(y))), "svelteInit" in y && n(5, l = y.svelteInit), "$$scope" in y && n(6, s = y.$$scope);
  }, t = Zt(t), [o, r, f, u, a, l, s, i, E, _];
}
class bo extends eo {
  constructor(t) {
    super(), co(this, t, yo, vo, lo, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: fs
} = window.__gradio__svelte__internal, en = window.ms_globals.rerender, vt = window.ms_globals.tree;
function So(e, t = {}) {
  function n(o) {
    const r = Ke(), i = new bo({
      ...o,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: r,
            reactComponent: e,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, l = s.parent ?? vt;
          return l.nodes = [...l.nodes, a], en({
            createPortal: wt,
            node: vt
          }), s.onDestroy(() => {
            l.nodes = l.nodes.filter((c) => c.svelteInstance !== r), en({
              createPortal: wt,
              node: vt
            });
          }), a;
        },
        ...o.props
      }
    });
    return r.set(i), i;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise.then(() => {
      o(n);
    });
  });
}
const xo = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Eo(e) {
  return e ? Object.keys(e).reduce((t, n) => {
    const o = e[n];
    return t[n] = Co(n, o), t;
  }, {}) : {};
}
function Co(e, t) {
  return typeof t == "number" && !xo.includes(e) ? t + "px" : t;
}
function Pt(e) {
  const t = [], n = e.cloneNode(!1);
  if (e._reactElement) {
    const r = b.Children.toArray(e._reactElement.props.children).map((i) => {
      if (b.isValidElement(i) && i.props.__slot__) {
        const {
          portals: s,
          clonedElement: a
        } = Pt(i.props.el);
        return b.cloneElement(i, {
          ...i.props,
          el: a,
          children: [...b.Children.toArray(i.props.children), ...s]
        });
      }
      return null;
    });
    return r.originalChildren = e._reactElement.props.children, t.push(wt(b.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: r
    }), n)), {
      clonedElement: n,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((r) => {
    e.getEventListeners(r).forEach(({
      listener: s,
      type: a,
      useCapture: l
    }) => {
      n.addEventListener(a, s, l);
    });
  });
  const o = Array.from(e.childNodes);
  for (let r = 0; r < o.length; r++) {
    const i = o[r];
    if (i.nodeType === 1) {
      const {
        clonedElement: s,
        portals: a
      } = Pt(i);
      t.push(...a), n.appendChild(s);
    } else i.nodeType === 3 && n.appendChild(i.cloneNode());
  }
  return {
    clonedElement: n,
    portals: t
  };
}
function wo(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Be = ur(({
  slot: e,
  clone: t,
  className: n,
  style: o,
  observeAttributes: r
}, i) => {
  const s = ne(), [a, l] = Mn([]), {
    forceClone: c
  } = Er(), f = c ? !0 : t;
  return me(() => {
    var g;
    if (!s.current || !e)
      return;
    let u = e;
    function d() {
      let h = u;
      if (u.tagName.toLowerCase() === "svelte-slot" && u.children.length === 1 && u.children[0] && (h = u.children[0], h.tagName.toLowerCase() === "react-portal-target" && h.children[0] && (h = h.children[0])), wo(i, h), n && h.classList.add(...n.split(" ")), o) {
        const x = Eo(o);
        Object.keys(x).forEach((E) => {
          h.style[E] = x[E];
        });
      }
    }
    let p = null, v = null;
    if (f && window.MutationObserver) {
      let h = function() {
        var y, T, S;
        (y = s.current) != null && y.contains(u) && ((T = s.current) == null || T.removeChild(u));
        const {
          portals: E,
          clonedElement: _
        } = Pt(e);
        u = _, l(E), u.style.display = "contents", v && clearTimeout(v), v = setTimeout(() => {
          d();
        }, 50), (S = s.current) == null || S.appendChild(u);
      };
      h();
      const x = Wr(() => {
        h(), p == null || p.disconnect(), p == null || p.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: r
        });
      }, 50);
      p = new window.MutationObserver(x), p.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      u.style.display = "contents", d(), (g = s.current) == null || g.appendChild(u);
    return () => {
      var h, x;
      u.style.display = "", (h = s.current) != null && h.contains(u) && ((x = s.current) == null || x.removeChild(u)), p == null || p.disconnect();
    };
  }, [e, f, n, o, i, r, c]), b.createElement("react-child", {
    ref: s,
    style: {
      display: "contents"
    }
  }, ...a);
}), _o = "1.6.0";
function ae() {
  return ae = Object.assign ? Object.assign.bind() : function(e) {
    for (var t = 1; t < arguments.length; t++) {
      var n = arguments[t];
      for (var o in n) ({}).hasOwnProperty.call(n, o) && (e[o] = n[o]);
    }
    return e;
  }, ae.apply(null, arguments);
}
function V(e) {
  "@babel/helpers - typeof";
  return V = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(t) {
    return typeof t;
  } : function(t) {
    return t && typeof Symbol == "function" && t.constructor === Symbol && t !== Symbol.prototype ? "symbol" : typeof t;
  }, V(e);
}
function To(e, t) {
  if (V(e) != "object" || !e) return e;
  var n = e[Symbol.toPrimitive];
  if (n !== void 0) {
    var o = n.call(e, t);
    if (V(o) != "object") return o;
    throw new TypeError("@@toPrimitive must return a primitive value.");
  }
  return (t === "string" ? String : Number)(e);
}
function $n(e) {
  var t = To(e, "string");
  return V(t) == "symbol" ? t : t + "";
}
function w(e, t, n) {
  return (t = $n(t)) in e ? Object.defineProperty(e, t, {
    value: n,
    enumerable: !0,
    configurable: !0,
    writable: !0
  }) : e[t] = n, e;
}
function tn(e, t) {
  var n = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var o = Object.getOwnPropertySymbols(e);
    t && (o = o.filter(function(r) {
      return Object.getOwnPropertyDescriptor(e, r).enumerable;
    })), n.push.apply(n, o);
  }
  return n;
}
function C(e) {
  for (var t = 1; t < arguments.length; t++) {
    var n = arguments[t] != null ? arguments[t] : {};
    t % 2 ? tn(Object(n), !0).forEach(function(o) {
      w(e, o, n[o]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : tn(Object(n)).forEach(function(o) {
      Object.defineProperty(e, o, Object.getOwnPropertyDescriptor(n, o));
    });
  }
  return e;
}
var Ro = `accept acceptCharset accessKey action allowFullScreen allowTransparency
    alt async autoComplete autoFocus autoPlay capture cellPadding cellSpacing challenge
    charSet checked classID className colSpan cols content contentEditable contextMenu
    controls coords crossOrigin data dateTime default defer dir disabled download draggable
    encType form formAction formEncType formMethod formNoValidate formTarget frameBorder
    headers height hidden high href hrefLang htmlFor httpEquiv icon id inputMode integrity
    is keyParams keyType kind label lang list loop low manifest marginHeight marginWidth max maxLength media
    mediaGroup method min minLength multiple muted name noValidate nonce open
    optimum pattern placeholder poster preload radioGroup readOnly rel required
    reversed role rowSpan rows sandbox scope scoped scrolling seamless selected
    shape size sizes span spellCheck src srcDoc srcLang srcSet start step style
    summary tabIndex target title type useMap value width wmode wrap`, Mo = `onCopy onCut onPaste onCompositionEnd onCompositionStart onCompositionUpdate onKeyDown
    onKeyPress onKeyUp onFocus onBlur onChange onInput onSubmit onClick onContextMenu onDoubleClick
    onDrag onDragEnd onDragEnter onDragExit onDragLeave onDragOver onDragStart onDrop onMouseDown
    onMouseEnter onMouseLeave onMouseMove onMouseOut onMouseOver onMouseUp onSelect onTouchCancel
    onTouchEnd onTouchMove onTouchStart onScroll onWheel onAbort onCanPlay onCanPlayThrough
    onDurationChange onEmptied onEncrypted onEnded onError onLoadedData onLoadedMetadata
    onLoadStart onPause onPlay onPlaying onProgress onRateChange onSeeked onSeeking onStalled onSuspend onTimeUpdate onVolumeChange onWaiting onLoad onError`, Po = "".concat(Ro, " ").concat(Mo).split(/[\s\n]+/), Oo = "aria-", Ao = "data-";
function nn(e, t) {
  return e.indexOf(t) === 0;
}
function ko(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : !1, n;
  t === !1 ? n = {
    aria: !0,
    data: !0,
    attr: !0
  } : t === !0 ? n = {
    aria: !0
  } : n = C({}, t);
  var o = {};
  return Object.keys(e).forEach(function(r) {
    // Aria
    (n.aria && (r === "role" || nn(r, Oo)) || // Data
    n.data && nn(r, Ao) || // Attr
    n.attr && Po.includes(r)) && (o[r] = e[r]);
  }), o;
}
const Io = /* @__PURE__ */ b.createContext({}), Lo = {
  classNames: {},
  styles: {},
  className: "",
  style: {}
}, jo = (e) => {
  const t = b.useContext(Io);
  return b.useMemo(() => ({
    ...Lo,
    ...t[e]
  }), [t[e]]);
};
function Ot() {
  const {
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: o,
    theme: r
  } = b.useContext(wr.ConfigContext);
  return {
    theme: r,
    getPrefixCls: e,
    direction: t,
    csp: n,
    iconPrefixCls: o
  };
}
function $o(e) {
  if (Array.isArray(e)) return e;
}
function Do(e, t) {
  var n = e == null ? null : typeof Symbol < "u" && e[Symbol.iterator] || e["@@iterator"];
  if (n != null) {
    var o, r, i, s, a = [], l = !0, c = !1;
    try {
      if (i = (n = n.call(e)).next, t === 0) {
        if (Object(n) !== n) return;
        l = !1;
      } else for (; !(l = (o = i.call(n)).done) && (a.push(o.value), a.length !== t); l = !0) ;
    } catch (f) {
      c = !0, r = f;
    } finally {
      try {
        if (!l && n.return != null && (s = n.return(), Object(s) !== s)) return;
      } finally {
        if (c) throw r;
      }
    }
    return a;
  }
}
function rn(e, t) {
  (t == null || t > e.length) && (t = e.length);
  for (var n = 0, o = Array(t); n < t; n++) o[n] = e[n];
  return o;
}
function No(e, t) {
  if (e) {
    if (typeof e == "string") return rn(e, t);
    var n = {}.toString.call(e).slice(8, -1);
    return n === "Object" && e.constructor && (n = e.constructor.name), n === "Map" || n === "Set" ? Array.from(e) : n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n) ? rn(e, t) : void 0;
  }
}
function Bo() {
  throw new TypeError(`Invalid attempt to destructure non-iterable instance.
In order to be iterable, non-array objects must have a [Symbol.iterator]() method.`);
}
function W(e, t) {
  return $o(e) || Do(e, t) || No(e, t) || Bo();
}
function _e(e, t) {
  if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
}
function on(e, t) {
  for (var n = 0; n < t.length; n++) {
    var o = t[n];
    o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, $n(o.key), o);
  }
}
function Te(e, t, n) {
  return t && on(e.prototype, t), n && on(e, n), Object.defineProperty(e, "prototype", {
    writable: !1
  }), e;
}
function ge(e) {
  if (e === void 0) throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
  return e;
}
function At(e, t) {
  return At = Object.setPrototypeOf ? Object.setPrototypeOf.bind() : function(n, o) {
    return n.__proto__ = o, n;
  }, At(e, t);
}
function et(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Super expression must either be null or a function");
  e.prototype = Object.create(t && t.prototype, {
    constructor: {
      value: e,
      writable: !0,
      configurable: !0
    }
  }), Object.defineProperty(e, "prototype", {
    writable: !1
  }), t && At(e, t);
}
function Ze(e) {
  return Ze = Object.setPrototypeOf ? Object.getPrototypeOf.bind() : function(t) {
    return t.__proto__ || Object.getPrototypeOf(t);
  }, Ze(e);
}
function Dn() {
  try {
    var e = !Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function() {
    }));
  } catch {
  }
  return (Dn = function() {
    return !!e;
  })();
}
function Ho(e, t) {
  if (t && (V(t) == "object" || typeof t == "function")) return t;
  if (t !== void 0) throw new TypeError("Derived constructors may only return object or undefined");
  return ge(e);
}
function tt(e) {
  var t = Dn();
  return function() {
    var n, o = Ze(e);
    if (t) {
      var r = Ze(this).constructor;
      n = Reflect.construct(o, arguments, r);
    } else n = o.apply(this, arguments);
    return Ho(this, n);
  };
}
var Nn = /* @__PURE__ */ Te(function e() {
  _e(this, e);
}), Bn = "CALC_UNIT", Vo = new RegExp(Bn, "g");
function yt(e) {
  return typeof e == "number" ? "".concat(e).concat(Bn) : e;
}
var Fo = /* @__PURE__ */ function(e) {
  et(n, e);
  var t = tt(n);
  function n(o, r) {
    var i;
    _e(this, n), i = t.call(this), w(ge(i), "result", ""), w(ge(i), "unitlessCssVar", void 0), w(ge(i), "lowPriority", void 0);
    var s = V(o);
    return i.unitlessCssVar = r, o instanceof n ? i.result = "(".concat(o.result, ")") : s === "number" ? i.result = yt(o) : s === "string" && (i.result = o), i;
  }
  return Te(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " + ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " + ").concat(yt(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result = "".concat(this.result, " - ").concat(r.getResult()) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " - ").concat(yt(r))), this.lowPriority = !0, this;
    }
  }, {
    key: "mul",
    value: function(r) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), r instanceof n ? this.result = "".concat(this.result, " * ").concat(r.getResult(!0)) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " * ").concat(r)), this.lowPriority = !1, this;
    }
  }, {
    key: "div",
    value: function(r) {
      return this.lowPriority && (this.result = "(".concat(this.result, ")")), r instanceof n ? this.result = "".concat(this.result, " / ").concat(r.getResult(!0)) : (typeof r == "number" || typeof r == "string") && (this.result = "".concat(this.result, " / ").concat(r)), this.lowPriority = !1, this;
    }
  }, {
    key: "getResult",
    value: function(r) {
      return this.lowPriority || r ? "(".concat(this.result, ")") : this.result;
    }
  }, {
    key: "equal",
    value: function(r) {
      var i = this, s = r || {}, a = s.unit, l = !0;
      return typeof a == "boolean" ? l = a : Array.from(this.unitlessCssVar).some(function(c) {
        return i.result.includes(c);
      }) && (l = !1), this.result = this.result.replace(Vo, l ? "px" : ""), typeof this.lowPriority < "u" ? "calc(".concat(this.result, ")") : this.result;
    }
  }]), n;
}(Nn), zo = /* @__PURE__ */ function(e) {
  et(n, e);
  var t = tt(n);
  function n(o) {
    var r;
    return _e(this, n), r = t.call(this), w(ge(r), "result", 0), o instanceof n ? r.result = o.result : typeof o == "number" && (r.result = o), r;
  }
  return Te(n, [{
    key: "add",
    value: function(r) {
      return r instanceof n ? this.result += r.result : typeof r == "number" && (this.result += r), this;
    }
  }, {
    key: "sub",
    value: function(r) {
      return r instanceof n ? this.result -= r.result : typeof r == "number" && (this.result -= r), this;
    }
  }, {
    key: "mul",
    value: function(r) {
      return r instanceof n ? this.result *= r.result : typeof r == "number" && (this.result *= r), this;
    }
  }, {
    key: "div",
    value: function(r) {
      return r instanceof n ? this.result /= r.result : typeof r == "number" && (this.result /= r), this;
    }
  }, {
    key: "equal",
    value: function() {
      return this.result;
    }
  }]), n;
}(Nn), Uo = function(t, n) {
  var o = t === "css" ? Fo : zo;
  return function(r) {
    return new o(r, n);
  };
}, sn = function(t, n) {
  return "".concat([n, t.replace(/([A-Z]+)([A-Z][a-z]+)/g, "$1-$2").replace(/([a-z])([A-Z])/g, "$1-$2")].filter(Boolean).join("-"));
};
function ve(e) {
  var t = m.useRef();
  t.current = e;
  var n = m.useCallback(function() {
    for (var o, r = arguments.length, i = new Array(r), s = 0; s < r; s++)
      i[s] = arguments[s];
    return (o = t.current) === null || o === void 0 ? void 0 : o.call.apply(o, [t].concat(i));
  }, []);
  return n;
}
function nt() {
  return !!(typeof window < "u" && window.document && window.document.createElement);
}
var an = nt() ? m.useLayoutEffect : m.useEffect, Xo = function(t, n) {
  var o = m.useRef(!0);
  an(function() {
    return t(o.current);
  }, n), an(function() {
    return o.current = !1, function() {
      o.current = !0;
    };
  }, []);
}, cn = function(t, n) {
  Xo(function(o) {
    if (!o)
      return t();
  }, n);
};
function $e(e) {
  var t = m.useRef(!1), n = m.useState(e), o = W(n, 2), r = o[0], i = o[1];
  m.useEffect(function() {
    return t.current = !1, function() {
      t.current = !0;
    };
  }, []);
  function s(a, l) {
    l && t.current || i(a);
  }
  return [r, s];
}
function bt(e) {
  return e !== void 0;
}
function Hn(e, t) {
  var n = t || {}, o = n.defaultValue, r = n.value, i = n.onChange, s = n.postState, a = $e(function() {
    return bt(r) ? r : bt(o) ? typeof o == "function" ? o() : o : typeof e == "function" ? e() : e;
  }), l = W(a, 2), c = l[0], f = l[1], u = r !== void 0 ? r : c, d = s ? s(u) : u, p = ve(i), v = $e([u]), g = W(v, 2), h = g[0], x = g[1];
  cn(function() {
    var _ = h[0];
    c !== _ && p(c, _);
  }, [h]), cn(function() {
    bt(r) || f(r);
  }, [r]);
  var E = ve(function(_, y) {
    f(_, y), x([u], y);
  });
  return [d, E];
}
var Vn = {
  exports: {}
}, O = {};
/**
 * @license React
 * react-is.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Nt = Symbol.for("react.element"), Bt = Symbol.for("react.portal"), rt = Symbol.for("react.fragment"), ot = Symbol.for("react.strict_mode"), it = Symbol.for("react.profiler"), st = Symbol.for("react.provider"), at = Symbol.for("react.context"), Wo = Symbol.for("react.server_context"), ct = Symbol.for("react.forward_ref"), lt = Symbol.for("react.suspense"), ut = Symbol.for("react.suspense_list"), ft = Symbol.for("react.memo"), dt = Symbol.for("react.lazy"), Ko = Symbol.for("react.offscreen"), Fn;
Fn = Symbol.for("react.module.reference");
function Q(e) {
  if (typeof e == "object" && e !== null) {
    var t = e.$$typeof;
    switch (t) {
      case Nt:
        switch (e = e.type, e) {
          case rt:
          case it:
          case ot:
          case lt:
          case ut:
            return e;
          default:
            switch (e = e && e.$$typeof, e) {
              case Wo:
              case at:
              case ct:
              case dt:
              case ft:
              case st:
                return e;
              default:
                return t;
            }
        }
      case Bt:
        return t;
    }
  }
}
O.ContextConsumer = at;
O.ContextProvider = st;
O.Element = Nt;
O.ForwardRef = ct;
O.Fragment = rt;
O.Lazy = dt;
O.Memo = ft;
O.Portal = Bt;
O.Profiler = it;
O.StrictMode = ot;
O.Suspense = lt;
O.SuspenseList = ut;
O.isAsyncMode = function() {
  return !1;
};
O.isConcurrentMode = function() {
  return !1;
};
O.isContextConsumer = function(e) {
  return Q(e) === at;
};
O.isContextProvider = function(e) {
  return Q(e) === st;
};
O.isElement = function(e) {
  return typeof e == "object" && e !== null && e.$$typeof === Nt;
};
O.isForwardRef = function(e) {
  return Q(e) === ct;
};
O.isFragment = function(e) {
  return Q(e) === rt;
};
O.isLazy = function(e) {
  return Q(e) === dt;
};
O.isMemo = function(e) {
  return Q(e) === ft;
};
O.isPortal = function(e) {
  return Q(e) === Bt;
};
O.isProfiler = function(e) {
  return Q(e) === it;
};
O.isStrictMode = function(e) {
  return Q(e) === ot;
};
O.isSuspense = function(e) {
  return Q(e) === lt;
};
O.isSuspenseList = function(e) {
  return Q(e) === ut;
};
O.isValidElementType = function(e) {
  return typeof e == "string" || typeof e == "function" || e === rt || e === it || e === ot || e === lt || e === ut || e === Ko || typeof e == "object" && e !== null && (e.$$typeof === dt || e.$$typeof === ft || e.$$typeof === st || e.$$typeof === at || e.$$typeof === ct || e.$$typeof === Fn || e.getModuleId !== void 0);
};
O.typeOf = Q;
Vn.exports = O;
var St = Vn.exports, Go = Symbol.for("react.element"), qo = Symbol.for("react.transitional.element"), Qo = Symbol.for("react.fragment");
function Zo(e) {
  return (
    // Base object type
    e && V(e) === "object" && // React Element type
    (e.$$typeof === Go || e.$$typeof === qo) && // React Fragment type
    e.type === Qo
  );
}
var Yo = Number(fr.split(".")[0]), Jo = function(t, n) {
  typeof t == "function" ? t(n) : V(t) === "object" && t && "current" in t && (t.current = n);
}, ei = function(t) {
  var n, o;
  if (!t)
    return !1;
  if (zn(t) && Yo >= 19)
    return !0;
  var r = St.isMemo(t) ? t.type.type : t.type;
  return !(typeof r == "function" && !((n = r.prototype) !== null && n !== void 0 && n.render) && r.$$typeof !== St.ForwardRef || typeof t == "function" && !((o = t.prototype) !== null && o !== void 0 && o.render) && t.$$typeof !== St.ForwardRef);
};
function zn(e) {
  return /* @__PURE__ */ dr(e) && !Zo(e);
}
var ti = function(t) {
  if (t && zn(t)) {
    var n = t;
    return n.props.propertyIsEnumerable("ref") ? n.props.ref : n.ref;
  }
  return null;
};
function ni(e, t) {
  for (var n = e, o = 0; o < t.length; o += 1) {
    if (n == null)
      return;
    n = n[t[o]];
  }
  return n;
}
function ln(e, t, n, o) {
  var r = C({}, t[e]);
  if (o != null && o.deprecatedTokens) {
    var i = o.deprecatedTokens;
    i.forEach(function(a) {
      var l = W(a, 2), c = l[0], f = l[1];
      if (r != null && r[c] || r != null && r[f]) {
        var u;
        (u = r[f]) !== null && u !== void 0 || (r[f] = r == null ? void 0 : r[c]);
      }
    });
  }
  var s = C(C({}, n), r);
  return Object.keys(s).forEach(function(a) {
    s[a] === t[a] && delete s[a];
  }), s;
}
var Un = typeof CSSINJS_STATISTIC < "u", kt = !0;
function Ht() {
  for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++)
    t[n] = arguments[n];
  if (!Un)
    return Object.assign.apply(Object, [{}].concat(t));
  kt = !1;
  var o = {};
  return t.forEach(function(r) {
    if (V(r) === "object") {
      var i = Object.keys(r);
      i.forEach(function(s) {
        Object.defineProperty(o, s, {
          configurable: !0,
          enumerable: !0,
          get: function() {
            return r[s];
          }
        });
      });
    }
  }), kt = !0, o;
}
var un = {};
function ri() {
}
var oi = function(t) {
  var n, o = t, r = ri;
  return Un && typeof Proxy < "u" && (n = /* @__PURE__ */ new Set(), o = new Proxy(t, {
    get: function(s, a) {
      if (kt) {
        var l;
        (l = n) === null || l === void 0 || l.add(a);
      }
      return s[a];
    }
  }), r = function(s, a) {
    var l;
    un[s] = {
      global: Array.from(n),
      component: C(C({}, (l = un[s]) === null || l === void 0 ? void 0 : l.component), a)
    };
  }), {
    token: o,
    keys: n,
    flush: r
  };
};
function fn(e, t, n) {
  if (typeof n == "function") {
    var o;
    return n(Ht(t, (o = t[e]) !== null && o !== void 0 ? o : {}));
  }
  return n ?? {};
}
function ii(e) {
  return e === "js" ? {
    max: Math.max,
    min: Math.min
  } : {
    max: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "max(".concat(o.map(function(i) {
        return Rt(i);
      }).join(","), ")");
    },
    min: function() {
      for (var n = arguments.length, o = new Array(n), r = 0; r < n; r++)
        o[r] = arguments[r];
      return "min(".concat(o.map(function(i) {
        return Rt(i);
      }).join(","), ")");
    }
  };
}
var si = 1e3 * 60 * 10, ai = /* @__PURE__ */ function() {
  function e() {
    _e(this, e), w(this, "map", /* @__PURE__ */ new Map()), w(this, "objectIDMap", /* @__PURE__ */ new WeakMap()), w(this, "nextID", 0), w(this, "lastAccessBeat", /* @__PURE__ */ new Map()), w(this, "accessBeat", 0);
  }
  return Te(e, [{
    key: "set",
    value: function(n, o) {
      this.clear();
      var r = this.getCompositeKey(n);
      this.map.set(r, o), this.lastAccessBeat.set(r, Date.now());
    }
  }, {
    key: "get",
    value: function(n) {
      var o = this.getCompositeKey(n), r = this.map.get(o);
      return this.lastAccessBeat.set(o, Date.now()), this.accessBeat += 1, r;
    }
  }, {
    key: "getCompositeKey",
    value: function(n) {
      var o = this, r = n.map(function(i) {
        return i && V(i) === "object" ? "obj_".concat(o.getObjectID(i)) : "".concat(V(i), "_").concat(i);
      });
      return r.join("|");
    }
  }, {
    key: "getObjectID",
    value: function(n) {
      if (this.objectIDMap.has(n))
        return this.objectIDMap.get(n);
      var o = this.nextID;
      return this.objectIDMap.set(n, o), this.nextID += 1, o;
    }
  }, {
    key: "clear",
    value: function() {
      var n = this;
      if (this.accessBeat > 1e4) {
        var o = Date.now();
        this.lastAccessBeat.forEach(function(r, i) {
          o - r > si && (n.map.delete(i), n.lastAccessBeat.delete(i));
        }), this.accessBeat = 0;
      }
    }
  }]), e;
}(), dn = new ai();
function ci(e, t) {
  return b.useMemo(function() {
    var n = dn.get(t);
    if (n)
      return n;
    var o = e();
    return dn.set(t, o), o;
  }, t);
}
var li = function() {
  return {};
};
function ui(e) {
  var t = e.useCSP, n = t === void 0 ? li : t, o = e.useToken, r = e.usePrefix, i = e.getResetStyles, s = e.getCommonStyle, a = e.getCompUnitless;
  function l(d, p, v, g) {
    var h = Array.isArray(d) ? d[0] : d;
    function x(M) {
      return "".concat(String(h)).concat(M.slice(0, 1).toUpperCase()).concat(M.slice(1));
    }
    var E = (g == null ? void 0 : g.unitless) || {}, _ = typeof a == "function" ? a(d) : {}, y = C(C({}, _), {}, w({}, x("zIndexPopup"), !0));
    Object.keys(E).forEach(function(M) {
      y[x(M)] = E[M];
    });
    var T = C(C({}, g), {}, {
      unitless: y,
      prefixToken: x
    }), S = f(d, p, v, T), R = c(h, v, T);
    return function(M) {
      var k = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : M, $ = S(M, k), D = W($, 2), A = D[1], I = R(k), j = W(I, 2), P = j[0], F = j[1];
      return [P, A, F];
    };
  }
  function c(d, p, v) {
    var g = v.unitless, h = v.injectStyle, x = h === void 0 ? !0 : h, E = v.prefixToken, _ = v.ignore, y = function(R) {
      var M = R.rootCls, k = R.cssVar, $ = k === void 0 ? {} : k, D = o(), A = D.realToken;
      return kr({
        path: [d],
        prefix: $.prefix,
        key: $.key,
        unitless: g,
        ignore: _,
        token: A,
        scope: M
      }, function() {
        var I = fn(d, A, p), j = ln(d, A, I, {
          deprecatedTokens: v == null ? void 0 : v.deprecatedTokens
        });
        return Object.keys(I).forEach(function(P) {
          j[E(P)] = j[P], delete j[P];
        }), j;
      }), null;
    }, T = function(R) {
      var M = o(), k = M.cssVar;
      return [function($) {
        return x && k ? /* @__PURE__ */ b.createElement(b.Fragment, null, /* @__PURE__ */ b.createElement(y, {
          rootCls: R,
          cssVar: k,
          component: d
        }), $) : $;
      }, k == null ? void 0 : k.key];
    };
    return T;
  }
  function f(d, p, v) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = Array.isArray(d) ? d : [d, d], x = W(h, 1), E = x[0], _ = h.join("-"), y = e.layer || {
      name: "antd"
    };
    return function(T) {
      var S = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : T, R = o(), M = R.theme, k = R.realToken, $ = R.hashId, D = R.token, A = R.cssVar, I = r(), j = I.rootPrefixCls, P = I.iconPrefixCls, F = n(), q = A ? "css" : "js", N = ci(function() {
        var G = /* @__PURE__ */ new Set();
        return A && Object.keys(g.unitless || {}).forEach(function(te) {
          G.add(mt(te, A.prefix)), G.add(mt(te, sn(E, A.prefix)));
        }), Uo(q, G);
      }, [q, E, A == null ? void 0 : A.prefix]), ue = ii(q), ye = ue.max, K = ue.min, re = {
        theme: M,
        token: D,
        hashId: $,
        nonce: function() {
          return F.nonce;
        },
        clientOnly: g.clientOnly,
        layer: y,
        // antd is always at top of styles
        order: g.order || -999
      };
      typeof i == "function" && Ut(C(C({}, re), {}, {
        clientOnly: !1,
        path: ["Shared", j]
      }), function() {
        return i(D, {
          prefix: {
            rootPrefixCls: j,
            iconPrefixCls: P
          },
          csp: F
        });
      });
      var fe = Ut(C(C({}, re), {}, {
        path: [_, T, P]
      }), function() {
        if (g.injectStyle === !1)
          return [];
        var G = oi(D), te = G.token, Z = G.flush, Y = fn(E, k, v), de = ".".concat(T), be = ln(E, k, Y, {
          deprecatedTokens: g.deprecatedTokens
        });
        A && Y && V(Y) === "object" && Object.keys(Y).forEach(function(Re) {
          Y[Re] = "var(".concat(mt(Re, sn(E, A.prefix)), ")");
        });
        var pe = Ht(te, {
          componentCls: de,
          prefixCls: T,
          iconCls: ".".concat(P),
          antCls: ".".concat(j),
          calc: N,
          // @ts-ignore
          max: ye,
          // @ts-ignore
          min: K
        }, A ? Y : be), Se = p(pe, {
          hashId: $,
          prefixCls: T,
          rootPrefixCls: j,
          iconPrefixCls: P
        });
        Z(E, be);
        var oe = typeof s == "function" ? s(pe, T, S, g.resetFont) : null;
        return [g.resetStyle === !1 ? null : oe, Se];
      });
      return [fe, $];
    };
  }
  function u(d, p, v) {
    var g = arguments.length > 3 && arguments[3] !== void 0 ? arguments[3] : {}, h = f(d, p, v, C({
      resetStyle: !1,
      // Sub Style should default after root one
      order: -998
    }, g)), x = function(_) {
      var y = _.prefixCls, T = _.rootCls, S = T === void 0 ? y : T;
      return h(y, S), null;
    };
    return x;
  }
  return {
    genStyleHooks: l,
    genSubStyleComponent: u,
    genComponentStyleHook: f
  };
}
const fi = {
  blue: "#1677FF",
  purple: "#722ED1",
  cyan: "#13C2C2",
  green: "#52C41A",
  magenta: "#EB2F96",
  /**
   * @deprecated Use magenta instead
   */
  pink: "#EB2F96",
  red: "#F5222D",
  orange: "#FA8C16",
  yellow: "#FADB14",
  volcano: "#FA541C",
  geekblue: "#2F54EB",
  gold: "#FAAD14",
  lime: "#A0D911"
}, di = Object.assign(Object.assign({}, fi), {
  // Color
  colorPrimary: "#1677ff",
  colorSuccess: "#52c41a",
  colorWarning: "#faad14",
  colorError: "#ff4d4f",
  colorInfo: "#1677ff",
  colorLink: "",
  colorTextBase: "",
  colorBgBase: "",
  // Font
  fontFamily: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
'Noto Color Emoji'`,
  fontFamilyCode: "'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace",
  fontSize: 14,
  // Line
  lineWidth: 1,
  lineType: "solid",
  // Motion
  motionUnit: 0.1,
  motionBase: 0,
  motionEaseOutCirc: "cubic-bezier(0.08, 0.82, 0.17, 1)",
  motionEaseInOutCirc: "cubic-bezier(0.78, 0.14, 0.15, 0.86)",
  motionEaseOut: "cubic-bezier(0.215, 0.61, 0.355, 1)",
  motionEaseInOut: "cubic-bezier(0.645, 0.045, 0.355, 1)",
  motionEaseOutBack: "cubic-bezier(0.12, 0.4, 0.29, 1.46)",
  motionEaseInBack: "cubic-bezier(0.71, -0.46, 0.88, 0.6)",
  motionEaseInQuint: "cubic-bezier(0.755, 0.05, 0.855, 0.06)",
  motionEaseOutQuint: "cubic-bezier(0.23, 1, 0.32, 1)",
  // Radius
  borderRadius: 6,
  // Size
  sizeUnit: 4,
  sizeStep: 4,
  sizePopupArrow: 16,
  // Control Base
  controlHeight: 32,
  // zIndex
  zIndexBase: 0,
  zIndexPopupBase: 1e3,
  // Image
  opacityImage: 1,
  // Wireframe
  wireframe: !1,
  // Motion
  motion: !0
}), H = Math.round;
function xt(e, t) {
  const n = e.replace(/^[^(]*\((.*)/, "$1").replace(/\).*/, "").match(/\d*\.?\d+%?/g) || [], o = n.map((r) => parseFloat(r));
  for (let r = 0; r < 3; r += 1)
    o[r] = t(o[r] || 0, n[r] || "", r);
  return n[3] ? o[3] = n[3].includes("%") ? o[3] / 100 : o[3] : o[3] = 1, o;
}
const pn = (e, t, n) => n === 0 ? e : e / 100;
function Ie(e, t) {
  const n = t || 255;
  return e > n ? n : e < 0 ? 0 : e;
}
class se {
  constructor(t) {
    w(this, "isValid", !0), w(this, "r", 0), w(this, "g", 0), w(this, "b", 0), w(this, "a", 1), w(this, "_h", void 0), w(this, "_s", void 0), w(this, "_l", void 0), w(this, "_v", void 0), w(this, "_max", void 0), w(this, "_min", void 0), w(this, "_brightness", void 0);
    function n(o) {
      return o[0] in t && o[1] in t && o[2] in t;
    }
    if (t) if (typeof t == "string") {
      let r = function(i) {
        return o.startsWith(i);
      };
      const o = t.trim();
      /^#?[A-F\d]{3,8}$/i.test(o) ? this.fromHexString(o) : r("rgb") ? this.fromRgbString(o) : r("hsl") ? this.fromHslString(o) : (r("hsv") || r("hsb")) && this.fromHsvString(o);
    } else if (t instanceof se)
      this.r = t.r, this.g = t.g, this.b = t.b, this.a = t.a, this._h = t._h, this._s = t._s, this._l = t._l, this._v = t._v;
    else if (n("rgb"))
      this.r = Ie(t.r), this.g = Ie(t.g), this.b = Ie(t.b), this.a = typeof t.a == "number" ? Ie(t.a, 1) : 1;
    else if (n("hsl"))
      this.fromHsl(t);
    else if (n("hsv"))
      this.fromHsv(t);
    else
      throw new Error("@ant-design/fast-color: unsupported input " + JSON.stringify(t));
  }
  // ======================= Setter =======================
  setR(t) {
    return this._sc("r", t);
  }
  setG(t) {
    return this._sc("g", t);
  }
  setB(t) {
    return this._sc("b", t);
  }
  setA(t) {
    return this._sc("a", t, 1);
  }
  setHue(t) {
    const n = this.toHsv();
    return n.h = t, this._c(n);
  }
  // ======================= Getter =======================
  /**
   * Returns the perceived luminance of a color, from 0-1.
   * @see http://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
   */
  getLuminance() {
    function t(i) {
      const s = i / 255;
      return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
    }
    const n = t(this.r), o = t(this.g), r = t(this.b);
    return 0.2126 * n + 0.7152 * o + 0.0722 * r;
  }
  getHue() {
    if (typeof this._h > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._h = 0 : this._h = H(60 * (this.r === this.getMax() ? (this.g - this.b) / t + (this.g < this.b ? 6 : 0) : this.g === this.getMax() ? (this.b - this.r) / t + 2 : (this.r - this.g) / t + 4));
    }
    return this._h;
  }
  getSaturation() {
    if (typeof this._s > "u") {
      const t = this.getMax() - this.getMin();
      t === 0 ? this._s = 0 : this._s = t / this.getMax();
    }
    return this._s;
  }
  getLightness() {
    return typeof this._l > "u" && (this._l = (this.getMax() + this.getMin()) / 510), this._l;
  }
  getValue() {
    return typeof this._v > "u" && (this._v = this.getMax() / 255), this._v;
  }
  /**
   * Returns the perceived brightness of the color, from 0-255.
   * Note: this is not the b of HSB
   * @see http://www.w3.org/TR/AERT#color-contrast
   */
  getBrightness() {
    return typeof this._brightness > "u" && (this._brightness = (this.r * 299 + this.g * 587 + this.b * 114) / 1e3), this._brightness;
  }
  // ======================== Func ========================
  darken(t = 10) {
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() - t / 100;
    return r < 0 && (r = 0), this._c({
      h: n,
      s: o,
      l: r,
      a: this.a
    });
  }
  lighten(t = 10) {
    const n = this.getHue(), o = this.getSaturation();
    let r = this.getLightness() + t / 100;
    return r > 1 && (r = 1), this._c({
      h: n,
      s: o,
      l: r,
      a: this.a
    });
  }
  /**
   * Mix the current color a given amount with another color, from 0 to 100.
   * 0 means no mixing (return current color).
   */
  mix(t, n = 50) {
    const o = this._c(t), r = n / 100, i = (a) => (o[a] - this[a]) * r + this[a], s = {
      r: H(i("r")),
      g: H(i("g")),
      b: H(i("b")),
      a: H(i("a") * 100) / 100
    };
    return this._c(s);
  }
  /**
   * Mix the color with pure white, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return white.
   */
  tint(t = 10) {
    return this.mix({
      r: 255,
      g: 255,
      b: 255,
      a: 1
    }, t);
  }
  /**
   * Mix the color with pure black, from 0 to 100.
   * Providing 0 will do nothing, providing 100 will always return black.
   */
  shade(t = 10) {
    return this.mix({
      r: 0,
      g: 0,
      b: 0,
      a: 1
    }, t);
  }
  onBackground(t) {
    const n = this._c(t), o = this.a + n.a * (1 - this.a), r = (i) => H((this[i] * this.a + n[i] * n.a * (1 - this.a)) / o);
    return this._c({
      r: r("r"),
      g: r("g"),
      b: r("b"),
      a: o
    });
  }
  // ======================= Status =======================
  isDark() {
    return this.getBrightness() < 128;
  }
  isLight() {
    return this.getBrightness() >= 128;
  }
  // ======================== MISC ========================
  equals(t) {
    return this.r === t.r && this.g === t.g && this.b === t.b && this.a === t.a;
  }
  clone() {
    return this._c(this);
  }
  // ======================= Format =======================
  toHexString() {
    let t = "#";
    const n = (this.r || 0).toString(16);
    t += n.length === 2 ? n : "0" + n;
    const o = (this.g || 0).toString(16);
    t += o.length === 2 ? o : "0" + o;
    const r = (this.b || 0).toString(16);
    if (t += r.length === 2 ? r : "0" + r, typeof this.a == "number" && this.a >= 0 && this.a < 1) {
      const i = H(this.a * 255).toString(16);
      t += i.length === 2 ? i : "0" + i;
    }
    return t;
  }
  /** CSS support color pattern */
  toHsl() {
    return {
      h: this.getHue(),
      s: this.getSaturation(),
      l: this.getLightness(),
      a: this.a
    };
  }
  /** CSS support color pattern */
  toHslString() {
    const t = this.getHue(), n = H(this.getSaturation() * 100), o = H(this.getLightness() * 100);
    return this.a !== 1 ? `hsla(${t},${n}%,${o}%,${this.a})` : `hsl(${t},${n}%,${o}%)`;
  }
  /** Same as toHsb */
  toHsv() {
    return {
      h: this.getHue(),
      s: this.getSaturation(),
      v: this.getValue(),
      a: this.a
    };
  }
  toRgb() {
    return {
      r: this.r,
      g: this.g,
      b: this.b,
      a: this.a
    };
  }
  toRgbString() {
    return this.a !== 1 ? `rgba(${this.r},${this.g},${this.b},${this.a})` : `rgb(${this.r},${this.g},${this.b})`;
  }
  toString() {
    return this.toRgbString();
  }
  // ====================== Privates ======================
  /** Return a new FastColor object with one channel changed */
  _sc(t, n, o) {
    const r = this.clone();
    return r[t] = Ie(n, o), r;
  }
  _c(t) {
    return new this.constructor(t);
  }
  getMax() {
    return typeof this._max > "u" && (this._max = Math.max(this.r, this.g, this.b)), this._max;
  }
  getMin() {
    return typeof this._min > "u" && (this._min = Math.min(this.r, this.g, this.b)), this._min;
  }
  fromHexString(t) {
    const n = t.replace("#", "");
    function o(r, i) {
      return parseInt(n[r] + n[i || r], 16);
    }
    n.length < 6 ? (this.r = o(0), this.g = o(1), this.b = o(2), this.a = n[3] ? o(3) / 255 : 1) : (this.r = o(0, 1), this.g = o(2, 3), this.b = o(4, 5), this.a = n[6] ? o(6, 7) / 255 : 1);
  }
  fromHsl({
    h: t,
    s: n,
    l: o,
    a: r
  }) {
    if (this._h = t % 360, this._s = n, this._l = o, this.a = typeof r == "number" ? r : 1, n <= 0) {
      const d = H(o * 255);
      this.r = d, this.g = d, this.b = d;
    }
    let i = 0, s = 0, a = 0;
    const l = t / 60, c = (1 - Math.abs(2 * o - 1)) * n, f = c * (1 - Math.abs(l % 2 - 1));
    l >= 0 && l < 1 ? (i = c, s = f) : l >= 1 && l < 2 ? (i = f, s = c) : l >= 2 && l < 3 ? (s = c, a = f) : l >= 3 && l < 4 ? (s = f, a = c) : l >= 4 && l < 5 ? (i = f, a = c) : l >= 5 && l < 6 && (i = c, a = f);
    const u = o - c / 2;
    this.r = H((i + u) * 255), this.g = H((s + u) * 255), this.b = H((a + u) * 255);
  }
  fromHsv({
    h: t,
    s: n,
    v: o,
    a: r
  }) {
    this._h = t % 360, this._s = n, this._v = o, this.a = typeof r == "number" ? r : 1;
    const i = H(o * 255);
    if (this.r = i, this.g = i, this.b = i, n <= 0)
      return;
    const s = t / 60, a = Math.floor(s), l = s - a, c = H(o * (1 - n) * 255), f = H(o * (1 - n * l) * 255), u = H(o * (1 - n * (1 - l)) * 255);
    switch (a) {
      case 0:
        this.g = u, this.b = c;
        break;
      case 1:
        this.r = f, this.b = c;
        break;
      case 2:
        this.r = c, this.b = u;
        break;
      case 3:
        this.r = c, this.g = f;
        break;
      case 4:
        this.r = u, this.g = c;
        break;
      case 5:
      default:
        this.g = c, this.b = f;
        break;
    }
  }
  fromHsvString(t) {
    const n = xt(t, pn);
    this.fromHsv({
      h: n[0],
      s: n[1],
      v: n[2],
      a: n[3]
    });
  }
  fromHslString(t) {
    const n = xt(t, pn);
    this.fromHsl({
      h: n[0],
      s: n[1],
      l: n[2],
      a: n[3]
    });
  }
  fromRgbString(t) {
    const n = xt(t, (o, r) => (
      // Convert percentage to number. e.g. 50% -> 128
      r.includes("%") ? H(o / 100 * 255) : o
    ));
    this.r = n[0], this.g = n[1], this.b = n[2], this.a = n[3];
  }
}
function Et(e) {
  return e >= 0 && e <= 255;
}
function He(e, t) {
  const {
    r: n,
    g: o,
    b: r,
    a: i
  } = new se(e).toRgb();
  if (i < 1)
    return e;
  const {
    r: s,
    g: a,
    b: l
  } = new se(t).toRgb();
  for (let c = 0.01; c <= 1; c += 0.01) {
    const f = Math.round((n - s * (1 - c)) / c), u = Math.round((o - a * (1 - c)) / c), d = Math.round((r - l * (1 - c)) / c);
    if (Et(f) && Et(u) && Et(d))
      return new se({
        r: f,
        g: u,
        b: d,
        a: Math.round(c * 100) / 100
      }).toRgbString();
  }
  return new se({
    r: n,
    g: o,
    b: r,
    a: 1
  }).toRgbString();
}
var pi = function(e, t) {
  var n = {};
  for (var o in e) Object.prototype.hasOwnProperty.call(e, o) && t.indexOf(o) < 0 && (n[o] = e[o]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var r = 0, o = Object.getOwnPropertySymbols(e); r < o.length; r++)
    t.indexOf(o[r]) < 0 && Object.prototype.propertyIsEnumerable.call(e, o[r]) && (n[o[r]] = e[o[r]]);
  return n;
};
function hi(e) {
  const {
    override: t
  } = e, n = pi(e, ["override"]), o = Object.assign({}, t);
  Object.keys(di).forEach((d) => {
    delete o[d];
  });
  const r = Object.assign(Object.assign({}, n), o), i = 480, s = 576, a = 768, l = 992, c = 1200, f = 1600;
  if (r.motion === !1) {
    const d = "0s";
    r.motionDurationFast = d, r.motionDurationMid = d, r.motionDurationSlow = d;
  }
  return Object.assign(Object.assign(Object.assign({}, r), {
    // ============== Background ============== //
    colorFillContent: r.colorFillSecondary,
    colorFillContentHover: r.colorFill,
    colorFillAlter: r.colorFillQuaternary,
    colorBgContainerDisabled: r.colorFillTertiary,
    // ============== Split ============== //
    colorBorderBg: r.colorBgContainer,
    colorSplit: He(r.colorBorderSecondary, r.colorBgContainer),
    // ============== Text ============== //
    colorTextPlaceholder: r.colorTextQuaternary,
    colorTextDisabled: r.colorTextQuaternary,
    colorTextHeading: r.colorText,
    colorTextLabel: r.colorTextSecondary,
    colorTextDescription: r.colorTextTertiary,
    colorTextLightSolid: r.colorWhite,
    colorHighlight: r.colorError,
    colorBgTextHover: r.colorFillSecondary,
    colorBgTextActive: r.colorFill,
    colorIcon: r.colorTextTertiary,
    colorIconHover: r.colorText,
    colorErrorOutline: He(r.colorErrorBg, r.colorBgContainer),
    colorWarningOutline: He(r.colorWarningBg, r.colorBgContainer),
    // Font
    fontSizeIcon: r.fontSizeSM,
    // Line
    lineWidthFocus: r.lineWidth * 3,
    // Control
    lineWidth: r.lineWidth,
    controlOutlineWidth: r.lineWidth * 2,
    // Checkbox size and expand icon size
    controlInteractiveSize: r.controlHeight / 2,
    controlItemBgHover: r.colorFillTertiary,
    controlItemBgActive: r.colorPrimaryBg,
    controlItemBgActiveHover: r.colorPrimaryBgHover,
    controlItemBgActiveDisabled: r.colorFill,
    controlTmpOutline: r.colorFillQuaternary,
    controlOutline: He(r.colorPrimaryBg, r.colorBgContainer),
    lineType: r.lineType,
    borderRadius: r.borderRadius,
    borderRadiusXS: r.borderRadiusXS,
    borderRadiusSM: r.borderRadiusSM,
    borderRadiusLG: r.borderRadiusLG,
    fontWeightStrong: 600,
    opacityLoading: 0.65,
    linkDecoration: "none",
    linkHoverDecoration: "none",
    linkFocusDecoration: "none",
    controlPaddingHorizontal: 12,
    controlPaddingHorizontalSM: 8,
    paddingXXS: r.sizeXXS,
    paddingXS: r.sizeXS,
    paddingSM: r.sizeSM,
    padding: r.size,
    paddingMD: r.sizeMD,
    paddingLG: r.sizeLG,
    paddingXL: r.sizeXL,
    paddingContentHorizontalLG: r.sizeLG,
    paddingContentVerticalLG: r.sizeMS,
    paddingContentHorizontal: r.sizeMS,
    paddingContentVertical: r.sizeSM,
    paddingContentHorizontalSM: r.size,
    paddingContentVerticalSM: r.sizeXS,
    marginXXS: r.sizeXXS,
    marginXS: r.sizeXS,
    marginSM: r.sizeSM,
    margin: r.size,
    marginMD: r.sizeMD,
    marginLG: r.sizeLG,
    marginXL: r.sizeXL,
    marginXXL: r.sizeXXL,
    boxShadow: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowSecondary: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowTertiary: `
      0 1px 2px 0 rgba(0, 0, 0, 0.03),
      0 1px 6px -1px rgba(0, 0, 0, 0.02),
      0 2px 4px 0 rgba(0, 0, 0, 0.02)
    `,
    screenXS: i,
    screenXSMin: i,
    screenXSMax: s - 1,
    screenSM: s,
    screenSMMin: s,
    screenSMMax: a - 1,
    screenMD: a,
    screenMDMin: a,
    screenMDMax: l - 1,
    screenLG: l,
    screenLGMin: l,
    screenLGMax: c - 1,
    screenXL: c,
    screenXLMin: c,
    screenXLMax: f - 1,
    screenXXL: f,
    screenXXLMin: f,
    boxShadowPopoverArrow: "2px 2px 5px rgba(0, 0, 0, 0.05)",
    boxShadowCard: `
      0 1px 2px -2px ${new se("rgba(0, 0, 0, 0.16)").toRgbString()},
      0 3px 6px 0 ${new se("rgba(0, 0, 0, 0.12)").toRgbString()},
      0 5px 12px 4px ${new se("rgba(0, 0, 0, 0.09)").toRgbString()}
    `,
    boxShadowDrawerRight: `
      -6px 0 16px 0 rgba(0, 0, 0, 0.08),
      -3px 0 6px -4px rgba(0, 0, 0, 0.12),
      -9px 0 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerLeft: `
      6px 0 16px 0 rgba(0, 0, 0, 0.08),
      3px 0 6px -4px rgba(0, 0, 0, 0.12),
      9px 0 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerUp: `
      0 6px 16px 0 rgba(0, 0, 0, 0.08),
      0 3px 6px -4px rgba(0, 0, 0, 0.12),
      0 9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowDrawerDown: `
      0 -6px 16px 0 rgba(0, 0, 0, 0.08),
      0 -3px 6px -4px rgba(0, 0, 0, 0.12),
      0 -9px 28px 8px rgba(0, 0, 0, 0.05)
    `,
    boxShadowTabsOverflowLeft: "inset 10px 0 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowRight: "inset -10px 0 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowTop: "inset 0 10px 8px -8px rgba(0, 0, 0, 0.08)",
    boxShadowTabsOverflowBottom: "inset 0 -10px 8px -8px rgba(0, 0, 0, 0.08)"
  }), o);
}
const mi = {
  lineHeight: !0,
  lineHeightSM: !0,
  lineHeightLG: !0,
  lineHeightHeading1: !0,
  lineHeightHeading2: !0,
  lineHeightHeading3: !0,
  lineHeightHeading4: !0,
  lineHeightHeading5: !0,
  opacityLoading: !0,
  fontWeightStrong: !0,
  zIndexPopupBase: !0,
  zIndexBase: !0,
  opacityImage: !0
}, gi = {
  motionBase: !0,
  motionUnit: !0
}, vi = Ir(Tt.defaultAlgorithm), yi = {
  screenXS: !0,
  screenXSMin: !0,
  screenXSMax: !0,
  screenSM: !0,
  screenSMMin: !0,
  screenSMMax: !0,
  screenMD: !0,
  screenMDMin: !0,
  screenMDMax: !0,
  screenLG: !0,
  screenLGMin: !0,
  screenLGMax: !0,
  screenXL: !0,
  screenXLMin: !0,
  screenXLMax: !0,
  screenXXL: !0,
  screenXXLMin: !0
}, Xn = (e, t, n) => {
  const o = n.getDerivativeToken(e), {
    override: r,
    ...i
  } = t;
  let s = {
    ...o,
    override: r
  };
  return s = hi(s), i && Object.entries(i).forEach(([a, l]) => {
    const {
      theme: c,
      ...f
    } = l;
    let u = f;
    c && (u = Xn({
      ...s,
      ...f
    }, {
      override: f
    }, c)), s[a] = u;
  }), s;
};
function bi() {
  const {
    token: e,
    hashed: t,
    theme: n = vi,
    override: o,
    cssVar: r
  } = b.useContext(Tt._internalContext), [i, s, a] = Lr(n, [Tt.defaultSeed, e], {
    salt: `${_o}-${t || ""}`,
    override: o,
    getComputedToken: Xn,
    cssVar: r && {
      prefix: r.prefix,
      key: r.key,
      unitless: mi,
      ignore: gi,
      preserve: yi
    }
  });
  return [n, a, t ? s : "", i, r];
}
const {
  genStyleHooks: Si
} = ui({
  usePrefix: () => {
    const {
      getPrefixCls: e,
      iconPrefixCls: t
    } = Ot();
    return {
      iconPrefixCls: t,
      rootPrefixCls: e()
    };
  },
  useToken: () => {
    const [e, t, n, o, r] = bi();
    return {
      theme: e,
      realToken: t,
      hashId: n,
      token: o,
      cssVar: r
    };
  },
  useCSP: () => {
    const {
      csp: e
    } = Ot();
    return e ?? {};
  },
  layer: {
    name: "antdx",
    dependencies: ["antd"]
  }
});
function hn(e) {
  return e instanceof HTMLElement || e instanceof SVGElement;
}
function xi(e) {
  return e && V(e) === "object" && hn(e.nativeElement) ? e.nativeElement : hn(e) ? e : null;
}
function Ei(e) {
  var t = xi(e);
  if (t)
    return t;
  if (e instanceof b.Component) {
    var n;
    return (n = zt.findDOMNode) === null || n === void 0 ? void 0 : n.call(zt, e);
  }
  return null;
}
function Ci(e, t) {
  if (e == null) return {};
  var n = {};
  for (var o in e) if ({}.hasOwnProperty.call(e, o)) {
    if (t.indexOf(o) !== -1) continue;
    n[o] = e[o];
  }
  return n;
}
function mn(e, t) {
  if (e == null) return {};
  var n, o, r = Ci(e, t);
  if (Object.getOwnPropertySymbols) {
    var i = Object.getOwnPropertySymbols(e);
    for (o = 0; o < i.length; o++) n = i[o], t.indexOf(n) === -1 && {}.propertyIsEnumerable.call(e, n) && (r[n] = e[n]);
  }
  return r;
}
var wi = /* @__PURE__ */ m.createContext({}), _i = /* @__PURE__ */ function(e) {
  et(n, e);
  var t = tt(n);
  function n() {
    return _e(this, n), t.apply(this, arguments);
  }
  return Te(n, [{
    key: "render",
    value: function() {
      return this.props.children;
    }
  }]), n;
}(m.Component);
function Ti(e) {
  var t = m.useReducer(function(a) {
    return a + 1;
  }, 0), n = W(t, 2), o = n[1], r = m.useRef(e), i = ve(function() {
    return r.current;
  }), s = ve(function(a) {
    r.current = typeof a == "function" ? a(r.current) : a, o();
  });
  return [i, s];
}
var le = "none", Ve = "appear", Fe = "enter", ze = "leave", gn = "none", J = "prepare", Ce = "start", we = "active", Vt = "end", Wn = "prepared";
function vn(e, t) {
  var n = {};
  return n[e.toLowerCase()] = t.toLowerCase(), n["Webkit".concat(e)] = "webkit".concat(t), n["Moz".concat(e)] = "moz".concat(t), n["ms".concat(e)] = "MS".concat(t), n["O".concat(e)] = "o".concat(t.toLowerCase()), n;
}
function Ri(e, t) {
  var n = {
    animationend: vn("Animation", "AnimationEnd"),
    transitionend: vn("Transition", "TransitionEnd")
  };
  return e && ("AnimationEvent" in t || delete n.animationend.animation, "TransitionEvent" in t || delete n.transitionend.transition), n;
}
var Mi = Ri(nt(), typeof window < "u" ? window : {}), Kn = {};
if (nt()) {
  var Pi = document.createElement("div");
  Kn = Pi.style;
}
var Ue = {};
function Gn(e) {
  if (Ue[e])
    return Ue[e];
  var t = Mi[e];
  if (t)
    for (var n = Object.keys(t), o = n.length, r = 0; r < o; r += 1) {
      var i = n[r];
      if (Object.prototype.hasOwnProperty.call(t, i) && i in Kn)
        return Ue[e] = t[i], Ue[e];
    }
  return "";
}
var qn = Gn("animationend"), Qn = Gn("transitionend"), Zn = !!(qn && Qn), yn = qn || "animationend", bn = Qn || "transitionend";
function Sn(e, t) {
  if (!e) return null;
  if (V(e) === "object") {
    var n = t.replace(/-\w/g, function(o) {
      return o[1].toUpperCase();
    });
    return e[n];
  }
  return "".concat(e, "-").concat(t);
}
const Oi = function(e) {
  var t = ne();
  function n(r) {
    r && (r.removeEventListener(bn, e), r.removeEventListener(yn, e));
  }
  function o(r) {
    t.current && t.current !== r && n(t.current), r && r !== t.current && (r.addEventListener(bn, e), r.addEventListener(yn, e), t.current = r);
  }
  return m.useEffect(function() {
    return function() {
      n(t.current);
    };
  }, []), [o, n];
};
var Yn = nt() ? pr : me, Jn = function(t) {
  return +setTimeout(t, 16);
}, er = function(t) {
  return clearTimeout(t);
};
typeof window < "u" && "requestAnimationFrame" in window && (Jn = function(t) {
  return window.requestAnimationFrame(t);
}, er = function(t) {
  return window.cancelAnimationFrame(t);
});
var xn = 0, Ft = /* @__PURE__ */ new Map();
function tr(e) {
  Ft.delete(e);
}
var It = function(t) {
  var n = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 1;
  xn += 1;
  var o = xn;
  function r(i) {
    if (i === 0)
      tr(o), t();
    else {
      var s = Jn(function() {
        r(i - 1);
      });
      Ft.set(o, s);
    }
  }
  return r(n), o;
};
It.cancel = function(e) {
  var t = Ft.get(e);
  return tr(e), er(t);
};
const Ai = function() {
  var e = m.useRef(null);
  function t() {
    It.cancel(e.current);
  }
  function n(o) {
    var r = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : 2;
    t();
    var i = It(function() {
      r <= 1 ? o({
        isCanceled: function() {
          return i !== e.current;
        }
      }) : n(o, r - 1);
    });
    e.current = i;
  }
  return m.useEffect(function() {
    return function() {
      t();
    };
  }, []), [n, t];
};
var ki = [J, Ce, we, Vt], Ii = [J, Wn], nr = !1, Li = !0;
function rr(e) {
  return e === we || e === Vt;
}
const ji = function(e, t, n) {
  var o = $e(gn), r = W(o, 2), i = r[0], s = r[1], a = Ai(), l = W(a, 2), c = l[0], f = l[1];
  function u() {
    s(J, !0);
  }
  var d = t ? Ii : ki;
  return Yn(function() {
    if (i !== gn && i !== Vt) {
      var p = d.indexOf(i), v = d[p + 1], g = n(i);
      g === nr ? s(v, !0) : v && c(function(h) {
        function x() {
          h.isCanceled() || s(v, !0);
        }
        g === !0 ? x() : Promise.resolve(g).then(x);
      });
    }
  }, [e, i]), m.useEffect(function() {
    return function() {
      f();
    };
  }, []), [u, i];
};
function $i(e, t, n, o) {
  var r = o.motionEnter, i = r === void 0 ? !0 : r, s = o.motionAppear, a = s === void 0 ? !0 : s, l = o.motionLeave, c = l === void 0 ? !0 : l, f = o.motionDeadline, u = o.motionLeaveImmediately, d = o.onAppearPrepare, p = o.onEnterPrepare, v = o.onLeavePrepare, g = o.onAppearStart, h = o.onEnterStart, x = o.onLeaveStart, E = o.onAppearActive, _ = o.onEnterActive, y = o.onLeaveActive, T = o.onAppearEnd, S = o.onEnterEnd, R = o.onLeaveEnd, M = o.onVisibleChanged, k = $e(), $ = W(k, 2), D = $[0], A = $[1], I = Ti(le), j = W(I, 2), P = j[0], F = j[1], q = $e(null), N = W(q, 2), ue = N[0], ye = N[1], K = P(), re = ne(!1), fe = ne(null);
  function G() {
    return n();
  }
  var te = ne(!1);
  function Z() {
    F(le), ye(null, !0);
  }
  var Y = ve(function(z) {
    var B = P();
    if (B !== le) {
      var U = G();
      if (!(z && !z.deadline && z.target !== U)) {
        var xe = te.current, he;
        B === Ve && xe ? he = T == null ? void 0 : T(U, z) : B === Fe && xe ? he = S == null ? void 0 : S(U, z) : B === ze && xe && (he = R == null ? void 0 : R(U, z)), xe && he !== !1 && Z();
      }
    }
  }), de = Oi(Y), be = W(de, 1), pe = be[0], Se = function(B) {
    switch (B) {
      case Ve:
        return w(w(w({}, J, d), Ce, g), we, E);
      case Fe:
        return w(w(w({}, J, p), Ce, h), we, _);
      case ze:
        return w(w(w({}, J, v), Ce, x), we, y);
      default:
        return {};
    }
  }, oe = m.useMemo(function() {
    return Se(K);
  }, [K]), Re = ji(K, !e, function(z) {
    if (z === J) {
      var B = oe[J];
      return B ? B(G()) : nr;
    }
    if (ie in oe) {
      var U;
      ye(((U = oe[ie]) === null || U === void 0 ? void 0 : U.call(oe, G(), null)) || null);
    }
    return ie === we && K !== le && (pe(G()), f > 0 && (clearTimeout(fe.current), fe.current = setTimeout(function() {
      Y({
        deadline: !0
      });
    }, f))), ie === Wn && Z(), Li;
  }), De = W(Re, 2), Me = De[0], ie = De[1], Pe = rr(ie);
  te.current = Pe;
  var Ne = ne(null);
  Yn(function() {
    if (!(re.current && Ne.current === t)) {
      A(t);
      var z = re.current;
      re.current = !0;
      var B;
      !z && t && a && (B = Ve), z && t && i && (B = Fe), (z && !t && c || !z && u && !t && c) && (B = ze);
      var U = Se(B);
      B && (e || U[J]) ? (F(B), Me()) : F(le), Ne.current = t;
    }
  }, [t]), me(function() {
    // Cancel appear
    (K === Ve && !a || // Cancel enter
    K === Fe && !i || // Cancel leave
    K === ze && !c) && F(le);
  }, [a, i, c]), me(function() {
    return function() {
      re.current = !1, clearTimeout(fe.current);
    };
  }, []);
  var Oe = m.useRef(!1);
  me(function() {
    D && (Oe.current = !0), D !== void 0 && K === le && ((Oe.current || D) && (M == null || M(D)), Oe.current = !0);
  }, [D, K]);
  var Ae = ue;
  return oe[J] && ie === Ce && (Ae = C({
    transition: "none"
  }, Ae)), [K, ie, Ae, D ?? t];
}
function Di(e) {
  var t = e;
  V(e) === "object" && (t = e.transitionSupport);
  function n(r, i) {
    return !!(r.motionName && t && i !== !1);
  }
  var o = /* @__PURE__ */ m.forwardRef(function(r, i) {
    var s = r.visible, a = s === void 0 ? !0 : s, l = r.removeOnLeave, c = l === void 0 ? !0 : l, f = r.forceRender, u = r.children, d = r.motionName, p = r.leavedClassName, v = r.eventProps, g = m.useContext(wi), h = g.motion, x = n(r, h), E = ne(), _ = ne();
    function y() {
      try {
        return E.current instanceof HTMLElement ? E.current : Ei(_.current);
      } catch {
        return null;
      }
    }
    var T = $i(x, a, y, r), S = W(T, 4), R = S[0], M = S[1], k = S[2], $ = S[3], D = m.useRef($);
    $ && (D.current = !0);
    var A = m.useCallback(function(N) {
      E.current = N, Jo(i, N);
    }, [i]), I, j = C(C({}, v), {}, {
      visible: a
    });
    if (!u)
      I = null;
    else if (R === le)
      $ ? I = u(C({}, j), A) : !c && D.current && p ? I = u(C(C({}, j), {}, {
        className: p
      }), A) : f || !c && !p ? I = u(C(C({}, j), {}, {
        style: {
          display: "none"
        }
      }), A) : I = null;
    else {
      var P;
      M === J ? P = "prepare" : rr(M) ? P = "active" : M === Ce && (P = "start");
      var F = Sn(d, "".concat(R, "-").concat(P));
      I = u(C(C({}, j), {}, {
        className: ee(Sn(d, R), w(w({}, F, F && P), d, typeof d == "string")),
        style: k
      }), A);
    }
    if (/* @__PURE__ */ m.isValidElement(I) && ei(I)) {
      var q = ti(I);
      q || (I = /* @__PURE__ */ m.cloneElement(I, {
        ref: A
      }));
    }
    return /* @__PURE__ */ m.createElement(_i, {
      ref: _
    }, I);
  });
  return o.displayName = "CSSMotion", o;
}
const or = Di(Zn);
var Lt = "add", jt = "keep", $t = "remove", Ct = "removed";
function Ni(e) {
  var t;
  return e && V(e) === "object" && "key" in e ? t = e : t = {
    key: e
  }, C(C({}, t), {}, {
    key: String(t.key)
  });
}
function Dt() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
  return e.map(Ni);
}
function Bi() {
  var e = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [], t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : [], n = [], o = 0, r = t.length, i = Dt(e), s = Dt(t);
  i.forEach(function(c) {
    for (var f = !1, u = o; u < r; u += 1) {
      var d = s[u];
      if (d.key === c.key) {
        o < u && (n = n.concat(s.slice(o, u).map(function(p) {
          return C(C({}, p), {}, {
            status: Lt
          });
        })), o = u), n.push(C(C({}, d), {}, {
          status: jt
        })), o += 1, f = !0;
        break;
      }
    }
    f || n.push(C(C({}, c), {}, {
      status: $t
    }));
  }), o < r && (n = n.concat(s.slice(o).map(function(c) {
    return C(C({}, c), {}, {
      status: Lt
    });
  })));
  var a = {};
  n.forEach(function(c) {
    var f = c.key;
    a[f] = (a[f] || 0) + 1;
  });
  var l = Object.keys(a).filter(function(c) {
    return a[c] > 1;
  });
  return l.forEach(function(c) {
    n = n.filter(function(f) {
      var u = f.key, d = f.status;
      return u !== c || d !== $t;
    }), n.forEach(function(f) {
      f.key === c && (f.status = jt);
    });
  }), n;
}
var Hi = ["component", "children", "onVisibleChanged", "onAllRemoved"], Vi = ["status"], Fi = ["eventProps", "visible", "children", "motionName", "motionAppear", "motionEnter", "motionLeave", "motionLeaveImmediately", "motionDeadline", "removeOnLeave", "leavedClassName", "onAppearPrepare", "onAppearStart", "onAppearActive", "onAppearEnd", "onEnterStart", "onEnterActive", "onEnterEnd", "onLeaveStart", "onLeaveActive", "onLeaveEnd"];
function zi(e) {
  var t = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : or, n = /* @__PURE__ */ function(o) {
    et(i, o);
    var r = tt(i);
    function i() {
      var s;
      _e(this, i);
      for (var a = arguments.length, l = new Array(a), c = 0; c < a; c++)
        l[c] = arguments[c];
      return s = r.call.apply(r, [this].concat(l)), w(ge(s), "state", {
        keyEntities: []
      }), w(ge(s), "removeKey", function(f) {
        s.setState(function(u) {
          var d = u.keyEntities.map(function(p) {
            return p.key !== f ? p : C(C({}, p), {}, {
              status: Ct
            });
          });
          return {
            keyEntities: d
          };
        }, function() {
          var u = s.state.keyEntities, d = u.filter(function(p) {
            var v = p.status;
            return v !== Ct;
          }).length;
          d === 0 && s.props.onAllRemoved && s.props.onAllRemoved();
        });
      }), s;
    }
    return Te(i, [{
      key: "render",
      value: function() {
        var a = this, l = this.state.keyEntities, c = this.props, f = c.component, u = c.children, d = c.onVisibleChanged;
        c.onAllRemoved;
        var p = mn(c, Hi), v = f || m.Fragment, g = {};
        return Fi.forEach(function(h) {
          g[h] = p[h], delete p[h];
        }), delete p.keys, /* @__PURE__ */ m.createElement(v, p, l.map(function(h, x) {
          var E = h.status, _ = mn(h, Vi), y = E === Lt || E === jt;
          return /* @__PURE__ */ m.createElement(t, ae({}, g, {
            key: _.key,
            visible: y,
            eventProps: _,
            onVisibleChanged: function(S) {
              d == null || d(S, {
                key: _.key
              }), S || a.removeKey(_.key);
            }
          }), function(T, S) {
            return u(C(C({}, T), {}, {
              index: x
            }), S);
          });
        }));
      }
    }], [{
      key: "getDerivedStateFromProps",
      value: function(a, l) {
        var c = a.keys, f = l.keyEntities, u = Dt(c), d = Bi(f, u);
        return {
          keyEntities: d.filter(function(p) {
            var v = f.find(function(g) {
              var h = g.key;
              return p.key === h;
            });
            return !(v && v.status === Ct && p.status === $t);
          })
        };
      }
    }]), i;
  }(m.Component);
  return w(n, "defaultProps", {
    component: "div"
  }), n;
}
zi(Zn);
function Ui(e, t) {
  return hr(e, () => {
    const n = t(), {
      nativeElement: o
    } = n;
    return new Proxy(o, {
      get(r, i) {
        return n[i] ? n[i] : Reflect.get(r, i);
      }
    });
  });
}
const ir = /* @__PURE__ */ m.createContext({}), En = () => ({
  height: 0
}), Cn = (e) => ({
  height: e.scrollHeight
});
function Xi(e) {
  const {
    title: t,
    onOpenChange: n,
    open: o,
    children: r,
    className: i,
    style: s,
    classNames: a = {},
    styles: l = {},
    closable: c,
    forceRender: f
  } = e, {
    prefixCls: u
  } = m.useContext(ir), d = `${u}-header`;
  return /* @__PURE__ */ m.createElement(or, {
    motionEnter: !0,
    motionLeave: !0,
    motionName: `${d}-motion`,
    leavedClassName: `${d}-motion-hidden`,
    onEnterStart: En,
    onEnterActive: Cn,
    onLeaveStart: Cn,
    onLeaveActive: En,
    visible: o,
    forceRender: f
  }, ({
    className: p,
    style: v
  }) => /* @__PURE__ */ m.createElement("div", {
    className: ee(d, p, i),
    style: {
      ...v,
      ...s
    }
  }, (c !== !1 || t) && /* @__PURE__ */ m.createElement("div", {
    className: (
      // We follow antd naming standard here.
      // So the header part is use `-header` suffix.
      // Though its little bit weird for double `-header`.
      ee(`${d}-header`, a.header)
    ),
    style: {
      ...l.header
    }
  }, /* @__PURE__ */ m.createElement("div", {
    className: `${d}-title`
  }, t), c !== !1 && /* @__PURE__ */ m.createElement("div", {
    className: `${d}-close`
  }, /* @__PURE__ */ m.createElement(Pn, {
    type: "text",
    icon: /* @__PURE__ */ m.createElement(Rr, null),
    size: "small",
    onClick: () => {
      n == null || n(!o);
    }
  }))), r && /* @__PURE__ */ m.createElement("div", {
    className: ee(`${d}-content`, a.content),
    style: {
      ...l.content
    }
  }, r)));
}
const pt = /* @__PURE__ */ m.createContext(null);
function Wi(e, t) {
  const {
    className: n,
    action: o,
    onClick: r,
    ...i
  } = e, s = m.useContext(pt), {
    prefixCls: a,
    disabled: l
  } = s, c = i.disabled ?? l ?? s[`${o}Disabled`];
  return /* @__PURE__ */ m.createElement(Pn, ae({
    type: "text"
  }, i, {
    ref: t,
    onClick: (f) => {
      var u;
      c || ((u = s[o]) == null || u.call(s), r == null || r(f));
    },
    className: ee(a, n, {
      [`${a}-disabled`]: c
    })
  }));
}
const ht = /* @__PURE__ */ m.forwardRef(Wi);
function Ki(e, t) {
  return /* @__PURE__ */ m.createElement(ht, ae({
    icon: /* @__PURE__ */ m.createElement(Mr, null)
  }, e, {
    action: "onClear",
    ref: t
  }));
}
const Gi = /* @__PURE__ */ m.forwardRef(Ki), qi = /* @__PURE__ */ mr((e) => {
  const {
    className: t
  } = e;
  return /* @__PURE__ */ b.createElement("svg", {
    color: "currentColor",
    viewBox: "0 0 1000 1000",
    xmlns: "http://www.w3.org/2000/svg",
    className: t
  }, /* @__PURE__ */ b.createElement("title", null, "Stop Loading"), /* @__PURE__ */ b.createElement("rect", {
    fill: "currentColor",
    height: "250",
    rx: "24",
    ry: "24",
    width: "250",
    x: "375",
    y: "375"
  }), /* @__PURE__ */ b.createElement("circle", {
    cx: "500",
    cy: "500",
    fill: "none",
    r: "450",
    stroke: "currentColor",
    strokeWidth: "100",
    opacity: "0.45"
  }), /* @__PURE__ */ b.createElement("circle", {
    cx: "500",
    cy: "500",
    fill: "none",
    r: "450",
    stroke: "currentColor",
    strokeWidth: "100",
    strokeDasharray: "600 9999999"
  }, /* @__PURE__ */ b.createElement("animateTransform", {
    attributeName: "transform",
    dur: "1s",
    from: "0 500 500",
    repeatCount: "indefinite",
    to: "360 500 500",
    type: "rotate"
  })));
});
function Qi(e, t) {
  const {
    prefixCls: n
  } = m.useContext(pt), {
    className: o
  } = e;
  return /* @__PURE__ */ m.createElement(ht, ae({
    icon: null,
    color: "primary",
    variant: "text",
    shape: "circle"
  }, e, {
    className: ee(o, `${n}-loading-button`),
    action: "onCancel",
    ref: t
  }), /* @__PURE__ */ m.createElement(qi, {
    className: `${n}-loading-icon`
  }));
}
const sr = /* @__PURE__ */ m.forwardRef(Qi);
function Zi(e, t) {
  return /* @__PURE__ */ m.createElement(ht, ae({
    icon: /* @__PURE__ */ m.createElement(Pr, null),
    type: "primary",
    shape: "circle"
  }, e, {
    action: "onSend",
    ref: t
  }));
}
const ar = /* @__PURE__ */ m.forwardRef(Zi), Le = 1e3, je = 4, Qe = 140, wn = Qe / 2, Xe = 250, _n = 500, We = 0.8;
function Yi({
  className: e
}) {
  return /* @__PURE__ */ b.createElement("svg", {
    color: "currentColor",
    viewBox: `0 0 ${Le} ${Le}`,
    xmlns: "http://www.w3.org/2000/svg",
    className: e
  }, /* @__PURE__ */ b.createElement("title", null, "Speech Recording"), Array.from({
    length: je
  }).map((t, n) => {
    const o = (Le - Qe * je) / (je - 1), r = n * (o + Qe), i = Le / 2 - Xe / 2, s = Le / 2 - _n / 2;
    return /* @__PURE__ */ b.createElement("rect", {
      fill: "currentColor",
      rx: wn,
      ry: wn,
      height: Xe,
      width: Qe,
      x: r,
      y: i,
      key: n
    }, /* @__PURE__ */ b.createElement("animate", {
      attributeName: "height",
      values: `${Xe}; ${_n}; ${Xe}`,
      keyTimes: "0; 0.5; 1",
      dur: `${We}s`,
      begin: `${We / je * n}s`,
      repeatCount: "indefinite"
    }), /* @__PURE__ */ b.createElement("animate", {
      attributeName: "y",
      values: `${i}; ${s}; ${i}`,
      keyTimes: "0; 0.5; 1",
      dur: `${We}s`,
      begin: `${We / je * n}s`,
      repeatCount: "indefinite"
    }));
  }));
}
function Ji(e, t) {
  const {
    speechRecording: n,
    onSpeechDisabled: o,
    prefixCls: r
  } = m.useContext(pt);
  let i = null;
  return n ? i = /* @__PURE__ */ m.createElement(Yi, {
    className: `${r}-recording-icon`
  }) : o ? i = /* @__PURE__ */ m.createElement(Or, null) : i = /* @__PURE__ */ m.createElement(Ar, null), /* @__PURE__ */ m.createElement(ht, ae({
    icon: i,
    color: "primary",
    variant: "text"
  }, e, {
    action: "onSpeech",
    ref: t
  }));
}
const cr = /* @__PURE__ */ m.forwardRef(Ji), es = (e) => {
  const {
    componentCls: t,
    calc: n
  } = e, o = `${t}-header`;
  return {
    [t]: {
      [o]: {
        borderBottomWidth: e.lineWidth,
        borderBottomStyle: "solid",
        borderBottomColor: e.colorBorder,
        // ======================== Header ========================
        "&-header": {
          background: e.colorFillAlter,
          fontSize: e.fontSize,
          lineHeight: e.lineHeight,
          paddingBlock: n(e.paddingSM).sub(e.lineWidthBold).equal(),
          paddingInlineStart: e.padding,
          paddingInlineEnd: e.paddingXS,
          display: "flex",
          borderRadius: {
            _skip_check_: !0,
            value: n(e.borderRadius).mul(2).equal()
          },
          borderEndStartRadius: 0,
          borderEndEndRadius: 0,
          [`${o}-title`]: {
            flex: "auto"
          }
        },
        // ======================= Content ========================
        "&-content": {
          padding: e.padding
        },
        // ======================== Motion ========================
        "&-motion": {
          transition: ["height", "border"].map((r) => `${r} ${e.motionDurationSlow}`).join(","),
          overflow: "hidden",
          "&-enter-start, &-leave-active": {
            borderBottomColor: "transparent"
          },
          "&-hidden": {
            display: "none"
          }
        }
      }
    }
  };
}, ts = (e) => {
  const {
    componentCls: t,
    padding: n,
    paddingSM: o,
    paddingXS: r,
    paddingXXS: i,
    lineWidth: s,
    lineWidthBold: a,
    calc: l
  } = e;
  return {
    [t]: {
      position: "relative",
      width: "100%",
      boxSizing: "border-box",
      boxShadow: `${e.boxShadowTertiary}`,
      transition: `background ${e.motionDurationSlow}`,
      // Border
      borderRadius: {
        _skip_check_: !0,
        value: l(e.borderRadius).mul(2).equal()
      },
      borderColor: e.colorBorder,
      borderWidth: 0,
      borderStyle: "solid",
      // Border
      "&:after": {
        content: '""',
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
        transition: `border-color ${e.motionDurationSlow}`,
        borderRadius: {
          _skip_check_: !0,
          value: "inherit"
        },
        borderStyle: "inherit",
        borderColor: "inherit",
        borderWidth: s
      },
      // Focus
      "&:focus-within": {
        boxShadow: `${e.boxShadowSecondary}`,
        borderColor: e.colorPrimary,
        "&:after": {
          borderWidth: a
        }
      },
      "&-disabled": {
        background: e.colorBgContainerDisabled
      },
      // ============================== RTL ==============================
      [`&${t}-rtl`]: {
        direction: "rtl"
      },
      // ============================ Content ============================
      [`${t}-content`]: {
        display: "flex",
        gap: r,
        width: "100%",
        paddingBlock: o,
        paddingInlineStart: n,
        paddingInlineEnd: o,
        boxSizing: "border-box",
        alignItems: "flex-end"
      },
      // ============================ Prefix =============================
      [`${t}-prefix`]: {
        flex: "none"
      },
      // ============================= Input =============================
      [`${t}-input`]: {
        padding: 0,
        borderRadius: 0,
        flex: "auto",
        alignSelf: "center",
        minHeight: "auto"
      },
      // ============================ Actions ============================
      [`${t}-actions-list`]: {
        flex: "none",
        display: "flex",
        "&-presets": {
          gap: e.paddingXS
        }
      },
      [`${t}-actions-btn`]: {
        "&-disabled": {
          opacity: 0.45
        },
        "&-loading-button": {
          padding: 0,
          border: 0
        },
        "&-loading-icon": {
          height: e.controlHeight,
          width: e.controlHeight,
          verticalAlign: "top"
        },
        "&-recording-icon": {
          height: "1.2em",
          width: "1.2em",
          verticalAlign: "top"
        }
      },
      // ============================ Footer =============================
      [`${t}-footer`]: {
        paddingInlineStart: n,
        paddingInlineEnd: o,
        paddingBlockEnd: o,
        paddingBlockStart: i,
        boxSizing: "border-box"
      }
    }
  };
}, ns = () => ({}), rs = Si("Sender", (e) => {
  const {
    paddingXS: t,
    calc: n
  } = e, o = Ht(e, {
    SenderContentMaxWidth: `calc(100% - ${Rt(n(t).add(32).equal())})`
  });
  return [ts(o), es(o)];
}, ns);
let Ye;
!Ye && typeof window < "u" && (Ye = window.SpeechRecognition || window.webkitSpeechRecognition);
function os(e, t) {
  const n = ve(e), [o, r, i] = b.useMemo(() => typeof t == "object" ? [t.recording, t.onRecordingChange, typeof t.recording == "boolean"] : [void 0, void 0, !1], [t]), [s, a] = b.useState(null);
  b.useEffect(() => {
    if (typeof navigator < "u" && "permissions" in navigator) {
      let g = null;
      return navigator.permissions.query({
        name: "microphone"
      }).then((h) => {
        a(h.state), h.onchange = function() {
          a(this.state);
        }, g = h;
      }), () => {
        g && (g.onchange = null);
      };
    }
  }, []);
  const l = Ye && s !== "denied", c = b.useRef(null), [f, u] = Hn(!1, {
    value: o
  }), d = b.useRef(!1), p = () => {
    if (l && !c.current) {
      const g = new Ye();
      g.onstart = () => {
        u(!0);
      }, g.onend = () => {
        u(!1);
      }, g.onresult = (h) => {
        var x, E, _;
        if (!d.current) {
          const y = (_ = (E = (x = h.results) == null ? void 0 : x[0]) == null ? void 0 : E[0]) == null ? void 0 : _.transcript;
          n(y);
        }
        d.current = !1;
      }, c.current = g;
    }
  }, v = ve((g) => {
    g && !f || (d.current = g, i ? r == null || r(!f) : (p(), c.current && (f ? (c.current.stop(), r == null || r(!1)) : (c.current.start(), r == null || r(!0)))));
  });
  return [l, v, f];
}
function is(e, t, n) {
  return ni(e, t) || n;
}
const Tn = {
  SendButton: ar,
  ClearButton: Gi,
  LoadingButton: sr,
  SpeechButton: cr
}, ss = /* @__PURE__ */ b.forwardRef((e, t) => {
  const {
    prefixCls: n,
    styles: o = {},
    classNames: r = {},
    className: i,
    rootClassName: s,
    style: a,
    defaultValue: l,
    value: c,
    readOnly: f,
    submitType: u = "enter",
    onSubmit: d,
    loading: p,
    components: v,
    onCancel: g,
    onChange: h,
    actions: x,
    onKeyPress: E,
    onKeyDown: _,
    disabled: y,
    allowSpeech: T,
    prefix: S,
    footer: R,
    header: M,
    onPaste: k,
    onPasteFile: $,
    autoSize: D = {
      maxRows: 8
    },
    ...A
  } = e, {
    direction: I,
    getPrefixCls: j
  } = Ot(), P = j("sender", n), F = b.useRef(null), q = b.useRef(null);
  Ui(t, () => {
    var L, X;
    return {
      nativeElement: F.current,
      focus: (L = q.current) == null ? void 0 : L.focus,
      blur: (X = q.current) == null ? void 0 : X.blur
    };
  });
  const N = jo("sender"), ue = `${P}-input`, [ye, K, re] = rs(P), fe = ee(P, N.className, i, s, K, re, {
    [`${P}-rtl`]: I === "rtl",
    [`${P}-disabled`]: y
  }), G = `${P}-actions-btn`, te = `${P}-actions-list`, [Z, Y] = Hn(l || "", {
    value: c
  }), de = (L, X) => {
    Y(L), h && h(L, X);
  }, [be, pe, Se] = os((L) => {
    de(`${Z} ${L}`);
  }, T), oe = is(v, ["input"], _r.TextArea), De = {
    ...ko(A, {
      attr: !0,
      aria: !0,
      data: !0
    }),
    ref: q
  }, Me = () => {
    Z && d && !p && d(Z);
  }, ie = () => {
    de("");
  }, Pe = b.useRef(!1), Ne = () => {
    Pe.current = !0;
  }, Oe = () => {
    Pe.current = !1;
  }, Ae = (L) => {
    const X = L.key === "Enter" && !Pe.current;
    switch (u) {
      case "enter":
        X && !L.shiftKey && (L.preventDefault(), Me());
        break;
      case "shiftEnter":
        X && L.shiftKey && (L.preventDefault(), Me());
        break;
    }
    E == null || E(L);
  }, z = (L) => {
    var ke;
    const X = (ke = L.clipboardData) == null ? void 0 : ke.files;
    X != null && X.length && $ && ($(X[0], X), L.preventDefault()), k == null || k(L);
  }, B = (L) => {
    var X, ke;
    L.target !== ((X = F.current) == null ? void 0 : X.querySelector(`.${ue}`)) && L.preventDefault(), (ke = q.current) == null || ke.focus();
  };
  let U = /* @__PURE__ */ b.createElement(Tr, {
    className: `${te}-presets`
  }, T && /* @__PURE__ */ b.createElement(cr, null), p ? /* @__PURE__ */ b.createElement(sr, null) : /* @__PURE__ */ b.createElement(ar, null));
  typeof x == "function" ? U = x(U, {
    components: Tn
  }) : (x || x === !1) && (U = x);
  const xe = {
    prefixCls: G,
    onSend: Me,
    onSendDisabled: !Z,
    onClear: ie,
    onClearDisabled: !Z,
    onCancel: g,
    onCancelDisabled: !p,
    onSpeech: () => pe(!1),
    onSpeechDisabled: !be,
    speechRecording: Se,
    disabled: y
  }, he = typeof R == "function" ? R({
    components: Tn
  }) : R || null;
  return ye(/* @__PURE__ */ b.createElement("div", {
    ref: F,
    className: fe,
    style: {
      ...N.style,
      ...a
    }
  }, M && /* @__PURE__ */ b.createElement(ir.Provider, {
    value: {
      prefixCls: P
    }
  }, M), /* @__PURE__ */ b.createElement(pt.Provider, {
    value: xe
  }, /* @__PURE__ */ b.createElement("div", {
    className: `${P}-content`,
    onMouseDown: B
  }, S && /* @__PURE__ */ b.createElement("div", {
    className: ee(`${P}-prefix`, N.classNames.prefix, r.prefix),
    style: {
      ...N.styles.prefix,
      ...o.prefix
    }
  }, S), /* @__PURE__ */ b.createElement(oe, ae({}, De, {
    disabled: y,
    style: {
      ...N.styles.input,
      ...o.input
    },
    className: ee(ue, N.classNames.input, r.input),
    autoSize: D,
    value: Z,
    onChange: (L) => {
      de(L.target.value, L), pe(!0);
    },
    onPressEnter: Ae,
    onCompositionStart: Ne,
    onCompositionEnd: Oe,
    onKeyDown: _,
    onPaste: z,
    variant: "borderless",
    readOnly: f
  })), U && /* @__PURE__ */ b.createElement("div", {
    className: ee(te, N.classNames.actions, r.actions),
    style: {
      ...N.styles.actions,
      ...o.actions
    }
  }, U)), he && /* @__PURE__ */ b.createElement("div", {
    className: ee(`${P}-footer`, N.classNames.footer, r.footer),
    style: {
      ...N.styles.footer,
      ...o.footer
    }
  }, he))));
}), lr = ss;
lr.Header = Xi;
function as(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function cs(e, t = !1) {
  try {
    if (xr(e))
      return e;
    if (t && !as(e))
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
function Rn(e, t) {
  return gr(() => cs(e, t), [e, t]);
}
function ls({
  value: e,
  onValueChange: t
}) {
  const [n, o] = Mn(e), r = ne(t);
  r.current = t;
  const i = ne(n);
  return i.current = n, me(() => {
    r.current(n);
  }, [n]), me(() => {
    Kr(e, i.current) || o(e);
  }, [e]), [n, o];
}
const ds = So(({
  slots: e,
  children: t,
  onValueChange: n,
  onChange: o,
  onPasteFile: r,
  upload: i,
  elRef: s,
  ...a
}) => {
  const l = Rn(a.actions, !0), c = Rn(a.footer, !0), [f, u] = ls({
    onValueChange: n,
    value: a.value
  }), d = Cr();
  return /* @__PURE__ */ ce.jsxs(ce.Fragment, {
    children: [/* @__PURE__ */ ce.jsx("div", {
      style: {
        display: "none"
      },
      children: t
    }), /* @__PURE__ */ ce.jsx(lr, {
      ...a,
      value: f,
      ref: s,
      onSubmit: (...p) => {
        var v;
        d || (v = a.onSubmit) == null || v.call(a, ...p);
      },
      onChange: (p) => {
        o == null || o(p), u(p);
      },
      onPasteFile: async (p, v) => {
        const g = await i(Array.from(v));
        r == null || r(g.map((h) => h.path));
      },
      header: e.header ? /* @__PURE__ */ ce.jsx(Be, {
        slot: e.header
      }) : a.header,
      prefix: e.prefix ? /* @__PURE__ */ ce.jsx(Be, {
        slot: e.prefix
      }) : a.prefix,
      actions: e.actions ? /* @__PURE__ */ ce.jsx(Be, {
        slot: e.actions
      }) : l || a.actions,
      footer: e.footer ? /* @__PURE__ */ ce.jsx(Be, {
        slot: e.footer
      }) : c || a.footer
    })]
  });
});
export {
  ds as Sender,
  ds as default
};
