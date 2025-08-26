import { i as ke, a as Z, r as Te, Z as W, g as Oe, b as je } from "./Index-Ce5Tc2nH.js";
const S = window.ms_globals.React, we = window.ms_globals.React.useMemo, Pe = window.ms_globals.React.forwardRef, Ue = window.ms_globals.React.useRef, X = window.ms_globals.React.useState, he = window.ms_globals.React.useEffect, Y = window.ms_globals.ReactDOM.createPortal, De = window.ms_globals.internalContext.useContextPropsContext, Ne = window.ms_globals.internalContext.ContextPropsProvider, We = window.ms_globals.antd.Upload;
var Ae = /\s/;
function Me(e) {
  for (var t = e.length; t-- && Ae.test(e.charAt(t)); )
    ;
  return t;
}
var ze = /^\s+/;
function Be(e) {
  return e && e.slice(0, Me(e) + 1).replace(ze, "");
}
var re = NaN, qe = /^[-+]0x[0-9a-f]+$/i, Ge = /^0b[01]+$/i, He = /^0o[0-7]+$/i, Ke = parseInt;
function oe(e) {
  if (typeof e == "number")
    return e;
  if (ke(e))
    return re;
  if (Z(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = Z(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = Be(e);
  var r = Ge.test(e);
  return r || He.test(e) ? Ke(e.slice(2), r ? 2 : 8) : qe.test(e) ? re : +e;
}
function Je() {
}
var K = function() {
  return Te.Date.now();
}, Xe = "Expected a function", Ye = Math.max, Ze = Math.min;
function Qe(e, t, r) {
  var s, i, n, o, l, f, g = 0, I = !1, c = !1, _ = !0;
  if (typeof e != "function")
    throw new TypeError(Xe);
  t = oe(t) || 0, Z(r) && (I = !!r.leading, c = "maxWait" in r, n = c ? Ye(oe(r.maxWait) || 0, t) : n, _ = "trailing" in r ? !!r.trailing : _);
  function m(u) {
    var E = s, U = i;
    return s = i = void 0, g = u, o = e.apply(U, E), o;
  }
  function b(u) {
    return g = u, l = setTimeout(p, t), I ? m(u) : o;
  }
  function P(u) {
    var E = u - f, U = u - g, D = t - E;
    return c ? Ze(D, n - U) : D;
  }
  function a(u) {
    var E = u - f, U = u - g;
    return f === void 0 || E >= t || E < 0 || c && U >= n;
  }
  function p() {
    var u = K();
    if (a(u))
      return x(u);
    l = setTimeout(p, P(u));
  }
  function x(u) {
    return l = void 0, _ && s ? m(u) : (s = i = void 0, o);
  }
  function w() {
    l !== void 0 && clearTimeout(l), g = 0, s = f = i = l = void 0;
  }
  function d() {
    return l === void 0 ? o : x(K());
  }
  function F() {
    var u = K(), E = a(u);
    if (s = arguments, i = this, f = u, E) {
      if (l === void 0)
        return b(f);
      if (c)
        return clearTimeout(l), l = setTimeout(p, t), m(f);
    }
    return l === void 0 && (l = setTimeout(p, t)), o;
  }
  return F.cancel = w, F.flush = d, F;
}
var _e = {
  exports: {}
}, z = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Ve = S, $e = Symbol.for("react.element"), et = Symbol.for("react.fragment"), tt = Object.prototype.hasOwnProperty, nt = Ve.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, rt = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function ge(e, t, r) {
  var s, i = {}, n = null, o = null;
  r !== void 0 && (n = "" + r), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (s in t) tt.call(t, s) && !rt.hasOwnProperty(s) && (i[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) i[s] === void 0 && (i[s] = t[s]);
  return {
    $$typeof: $e,
    type: e,
    key: n,
    ref: o,
    props: i,
    _owner: nt.current
  };
}
z.Fragment = et;
z.jsx = ge;
z.jsxs = ge;
_e.exports = z;
var R = _e.exports;
const {
  SvelteComponent: ot,
  assign: ie,
  binding_callbacks: se,
  check_outros: it,
  children: ve,
  claim_element: Ie,
  claim_space: st,
  component_subscribe: le,
  compute_slots: lt,
  create_slot: ct,
  detach: O,
  element: ye,
  empty: ce,
  exclude_internal_props: ae,
  get_all_dirty_from_scope: at,
  get_slot_changes: dt,
  group_outros: ut,
  init: ft,
  insert_hydration: A,
  safe_not_equal: mt,
  set_custom_element_data: be,
  space: pt,
  transition_in: M,
  transition_out: Q,
  update_slot_base: wt
} = window.__gradio__svelte__internal, {
  beforeUpdate: ht,
  getContext: _t,
  onDestroy: gt,
  setContext: vt
} = window.__gradio__svelte__internal;
function de(e) {
  let t, r;
  const s = (
    /*#slots*/
    e[7].default
  ), i = ct(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = ye("svelte-slot"), i && i.c(), this.h();
    },
    l(n) {
      t = Ie(n, "SVELTE-SLOT", {
        class: !0
      });
      var o = ve(t);
      i && i.l(o), o.forEach(O), this.h();
    },
    h() {
      be(t, "class", "svelte-1rt0kpf");
    },
    m(n, o) {
      A(n, t, o), i && i.m(t, null), e[9](t), r = !0;
    },
    p(n, o) {
      i && i.p && (!r || o & /*$$scope*/
      64) && wt(
        i,
        s,
        n,
        /*$$scope*/
        n[6],
        r ? dt(
          s,
          /*$$scope*/
          n[6],
          o,
          null
        ) : at(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      r || (M(i, n), r = !0);
    },
    o(n) {
      Q(i, n), r = !1;
    },
    d(n) {
      n && O(t), i && i.d(n), e[9](null);
    }
  };
}
function It(e) {
  let t, r, s, i, n = (
    /*$$slots*/
    e[4].default && de(e)
  );
  return {
    c() {
      t = ye("react-portal-target"), r = pt(), n && n.c(), s = ce(), this.h();
    },
    l(o) {
      t = Ie(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), ve(t).forEach(O), r = st(o), n && n.l(o), s = ce(), this.h();
    },
    h() {
      be(t, "class", "svelte-1rt0kpf");
    },
    m(o, l) {
      A(o, t, l), e[8](t), A(o, r, l), n && n.m(o, l), A(o, s, l), i = !0;
    },
    p(o, [l]) {
      /*$$slots*/
      o[4].default ? n ? (n.p(o, l), l & /*$$slots*/
      16 && M(n, 1)) : (n = de(o), n.c(), M(n, 1), n.m(s.parentNode, s)) : n && (ut(), Q(n, 1, 1, () => {
        n = null;
      }), it());
    },
    i(o) {
      i || (M(n), i = !0);
    },
    o(o) {
      Q(n), i = !1;
    },
    d(o) {
      o && (O(t), O(r), O(s)), e[8](null), n && n.d(o);
    }
  };
}
function ue(e) {
  const {
    svelteInit: t,
    ...r
  } = e;
  return r;
}
function yt(e, t, r) {
  let s, i, {
    $$slots: n = {},
    $$scope: o
  } = t;
  const l = lt(n);
  let {
    svelteInit: f
  } = t;
  const g = W(ue(t)), I = W();
  le(e, I, (d) => r(0, s = d));
  const c = W();
  le(e, c, (d) => r(1, i = d));
  const _ = [], m = _t("$$ms-gr-react-wrapper"), {
    slotKey: b,
    slotIndex: P,
    subSlotIndex: a
  } = Oe() || {}, p = f({
    parent: m,
    props: g,
    target: I,
    slot: c,
    slotKey: b,
    slotIndex: P,
    subSlotIndex: a,
    onDestroy(d) {
      _.push(d);
    }
  });
  vt("$$ms-gr-react-wrapper", p), ht(() => {
    g.set(ue(t));
  }), gt(() => {
    _.forEach((d) => d());
  });
  function x(d) {
    se[d ? "unshift" : "push"](() => {
      s = d, I.set(s);
    });
  }
  function w(d) {
    se[d ? "unshift" : "push"](() => {
      i = d, c.set(i);
    });
  }
  return e.$$set = (d) => {
    r(17, t = ie(ie({}, t), ae(d))), "svelteInit" in d && r(5, f = d.svelteInit), "$$scope" in d && r(6, o = d.$$scope);
  }, t = ae(t), [s, i, I, c, l, f, o, n, x, w];
}
class bt extends ot {
  constructor(t) {
    super(), ft(this, t, yt, It, mt, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: jt
} = window.__gradio__svelte__internal, fe = window.ms_globals.rerender, J = window.ms_globals.tree;
function xt(e, t = {}) {
  function r(s) {
    const i = W(), n = new bt({
      ...s,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: i,
            reactComponent: e,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, f = o.parent ?? J;
          return f.nodes = [...f.nodes, l], fe({
            createPortal: Y,
            node: J
          }), o.onDestroy(() => {
            f.nodes = f.nodes.filter((g) => g.svelteInstance !== i), fe({
              createPortal: Y,
              node: J
            });
          }), l;
        },
        ...s.props
      }
    });
    return i.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise.then(() => {
      s(r);
    });
  });
}
function Et(e) {
  return /^(?:async\s+)?(?:function\s*(?:\w*\s*)?\(|\([\w\s,=]*\)\s*=>|\(\{[\w\s,=]*\}\)\s*=>|function\s*\*\s*\w*\s*\()/i.test(e.trim());
}
function Lt(e, t = !1) {
  try {
    if (je(e))
      return e;
    if (t && !Et(e))
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
function L(e, t) {
  return we(() => Lt(e, t), [e, t]);
}
const St = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function Rt(e) {
  return e ? Object.keys(e).reduce((t, r) => {
    const s = e[r];
    return t[r] = Ft(r, s), t;
  }, {}) : {};
}
function Ft(e, t) {
  return typeof t == "number" && !St.includes(e) ? t + "px" : t;
}
function V(e) {
  const t = [], r = e.cloneNode(!1);
  if (e._reactElement) {
    const i = S.Children.toArray(e._reactElement.props.children).map((n) => {
      if (S.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: l
        } = V(n.props.el);
        return S.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...S.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return i.originalChildren = e._reactElement.props.children, t.push(Y(S.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: i
    }), r)), {
      clonedElement: r,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((i) => {
    e.getEventListeners(i).forEach(({
      listener: o,
      type: l,
      useCapture: f
    }) => {
      r.addEventListener(l, o, f);
    });
  });
  const s = Array.from(e.childNodes);
  for (let i = 0; i < s.length; i++) {
    const n = s[i];
    if (n.nodeType === 1) {
      const {
        clonedElement: o,
        portals: l
      } = V(n);
      t.push(...l), r.appendChild(o);
    } else n.nodeType === 3 && r.appendChild(n.cloneNode());
  }
  return {
    clonedElement: r,
    portals: t
  };
}
function Ct(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const me = Pe(({
  slot: e,
  clone: t,
  className: r,
  style: s,
  observeAttributes: i
}, n) => {
  const o = Ue(), [l, f] = X([]), {
    forceClone: g
  } = De(), I = g ? !0 : t;
  return he(() => {
    var P;
    if (!o.current || !e)
      return;
    let c = e;
    function _() {
      let a = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (a = c.children[0], a.tagName.toLowerCase() === "react-portal-target" && a.children[0] && (a = a.children[0])), Ct(n, a), r && a.classList.add(...r.split(" ")), s) {
        const p = Rt(s);
        Object.keys(p).forEach((x) => {
          a.style[x] = p[x];
        });
      }
    }
    let m = null, b = null;
    if (I && window.MutationObserver) {
      let a = function() {
        var d, F, u;
        (d = o.current) != null && d.contains(c) && ((F = o.current) == null || F.removeChild(c));
        const {
          portals: x,
          clonedElement: w
        } = V(e);
        c = w, f(x), c.style.display = "contents", b && clearTimeout(b), b = setTimeout(() => {
          _();
        }, 50), (u = o.current) == null || u.appendChild(c);
      };
      a();
      const p = Qe(() => {
        a(), m == null || m.disconnect(), m == null || m.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      m = new window.MutationObserver(p), m.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", _(), (P = o.current) == null || P.appendChild(c);
    return () => {
      var a, p;
      c.style.display = "", (a = o.current) != null && a.contains(c) && ((p = o.current) == null || p.removeChild(c)), m == null || m.disconnect();
    };
  }, [e, I, r, s, n, i, g]), S.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...l);
}), Pt = ({
  children: e,
  ...t
}) => /* @__PURE__ */ R.jsx(R.Fragment, {
  children: e(t)
});
function Ut(e) {
  return S.createElement(Pt, {
    children: e
  });
}
function pe(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? Ut((r) => /* @__PURE__ */ R.jsx(Ne, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ R.jsx(me, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...r
    })
  })) : /* @__PURE__ */ R.jsx(me, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function T({
  key: e,
  slots: t,
  targets: r
}, s) {
  return t[e] ? (...i) => r ? r.map((n, o) => /* @__PURE__ */ R.jsx(S.Fragment, {
    children: pe(n, {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ R.jsx(R.Fragment, {
    children: pe(t[e], {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }) : void 0;
}
const kt = (e) => !!e.name;
function Tt(e) {
  return typeof e == "object" && e !== null ? e : {};
}
const Dt = xt(({
  slots: e,
  upload: t,
  showUploadList: r,
  progress: s,
  beforeUpload: i,
  customRequest: n,
  previewFile: o,
  isImageUrl: l,
  itemRender: f,
  iconRender: g,
  data: I,
  onChange: c,
  onValueChange: _,
  onRemove: m,
  fileList: b,
  setSlotParams: P,
  maxCount: a,
  ...p
}) => {
  const x = e["showUploadList.downloadIcon"] || e["showUploadList.removeIcon"] || e["showUploadList.previewIcon"] || e["showUploadList.extra"] || typeof r == "object", w = Tt(r), d = L(w.showPreviewIcon), F = L(w.showRemoveIcon), u = L(w.showDownloadIcon), E = L(i), U = L(n), D = L(s == null ? void 0 : s.format), xe = L(o), Ee = L(l), Le = L(f), Se = L(g), Re = L(I), [Fe, N] = X(!1), [j, B] = X(b);
  he(() => {
    B(b);
  }, [b]);
  const $ = we(() => {
    const k = {};
    return j.map((v) => {
      if (!kt(v)) {
        const C = v.uid || v.url || v.path;
        return k[C] || (k[C] = 0), k[C]++, {
          ...v,
          name: v.orig_name || v.path,
          uid: v.uid || C + "-" + k[C],
          status: "done"
        };
      }
      return v;
    }) || [];
  }, [j]), q = p.disabled || Fe;
  return /* @__PURE__ */ R.jsx(We.Dragger, {
    ...p,
    disabled: q,
    fileList: $,
    data: Re || I,
    previewFile: xe,
    isImageUrl: Ee,
    itemRender: e.itemRender ? T({
      slots: e,
      key: "itemRender"
    }) : Le,
    iconRender: e.iconRender ? T({
      slots: e,
      key: "iconRender"
    }) : Se,
    maxCount: a,
    onChange: async (k) => {
      try {
        const v = k.file, C = k.fileList, ee = $.findIndex((y) => y.uid === v.uid);
        if (ee !== -1) {
          if (q)
            return;
          m == null || m(v);
          const y = j.slice();
          y.splice(ee, 1), _ == null || _(y), c == null || c(y.map((G) => G.path));
        } else {
          if (E && !await E(v, C) || q)
            return;
          N(!0);
          let y = C.filter((h) => h.status !== "done");
          if (a === 1)
            y = y.slice(0, 1);
          else if (y.length === 0) {
            N(!1);
            return;
          } else if (typeof a == "number") {
            const h = a - j.length;
            y = y.slice(0, h < 0 ? 0 : h);
          }
          const G = j, te = y.map((h) => ({
            ...h,
            size: h.size,
            uid: h.uid,
            name: h.name,
            percent: 99,
            status: "uploading"
          }));
          B((h) => [...a === 1 ? [] : h, ...te]);
          const ne = (await t(y.map((h) => h.originFileObj))).filter(Boolean).map((h, Ce) => ({
            ...h,
            uid: te[Ce].uid
          })), H = a === 1 ? ne : [...G, ...ne];
          N(!1), B(H), _ == null || _(H), c == null || c(H.map((h) => h.path));
        }
      } catch (v) {
        console.error(v), N(!1);
      }
    },
    customRequest: U || Je,
    progress: s && {
      ...s,
      format: D
    },
    showUploadList: x ? {
      ...w,
      showDownloadIcon: u || w.showDownloadIcon,
      showRemoveIcon: F || w.showRemoveIcon,
      showPreviewIcon: d || w.showPreviewIcon,
      downloadIcon: e["showUploadList.downloadIcon"] ? T({
        slots: e,
        key: "showUploadList.downloadIcon"
      }) : w.downloadIcon,
      removeIcon: e["showUploadList.removeIcon"] ? T({
        slots: e,
        key: "showUploadList.removeIcon"
      }) : w.removeIcon,
      previewIcon: e["showUploadList.previewIcon"] ? T({
        slots: e,
        key: "showUploadList.previewIcon"
      }) : w.previewIcon,
      extra: e["showUploadList.extra"] ? T({
        slots: e,
        key: "showUploadList.extra"
      }) : w.extra
    } : r
  });
});
export {
  Dt as UploadDragger,
  Dt as default
};
