import { i as ke, a as Z, r as Te, Z as D, g as Oe, b as je } from "./Index-RjYm-RR-.js";
const R = window.ms_globals.React, we = window.ms_globals.React.useMemo, Pe = window.ms_globals.React.forwardRef, Ue = window.ms_globals.React.useRef, X = window.ms_globals.React.useState, he = window.ms_globals.React.useEffect, Y = window.ms_globals.ReactDOM.createPortal, Ne = window.ms_globals.internalContext.useContextPropsContext, We = window.ms_globals.internalContext.ContextPropsProvider, De = window.ms_globals.antd.Upload;
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
  var s, i, n, o, l, u, g = 0, y = !1, c = !1, _ = !0;
  if (typeof e != "function")
    throw new TypeError(Xe);
  t = oe(t) || 0, Z(r) && (y = !!r.leading, c = "maxWait" in r, n = c ? Ye(oe(r.maxWait) || 0, t) : n, _ = "trailing" in r ? !!r.trailing : _);
  function f(d) {
    var E = s, U = i;
    return s = i = void 0, g = d, o = e.apply(U, E), o;
  }
  function I(d) {
    return g = d, l = setTimeout(p, t), y ? f(d) : o;
  }
  function S(d) {
    var E = d - u, U = d - g, N = t - E;
    return c ? Ze(N, n - U) : N;
  }
  function m(d) {
    var E = d - u, U = d - g;
    return u === void 0 || E >= t || E < 0 || c && U >= n;
  }
  function p() {
    var d = K();
    if (m(d))
      return x(d);
    l = setTimeout(p, S(d));
  }
  function x(d) {
    return l = void 0, _ && s ? f(d) : (s = i = void 0, o);
  }
  function w() {
    l !== void 0 && clearTimeout(l), g = 0, s = u = i = l = void 0;
  }
  function a() {
    return l === void 0 ? o : x(K());
  }
  function C() {
    var d = K(), E = m(d);
    if (s = arguments, i = this, u = d, E) {
      if (l === void 0)
        return I(u);
      if (c)
        return clearTimeout(l), l = setTimeout(p, t), f(u);
    }
    return l === void 0 && (l = setTimeout(p, t)), o;
  }
  return C.cancel = w, C.flush = a, C;
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
var Ve = R, $e = Symbol.for("react.element"), et = Symbol.for("react.fragment"), tt = Object.prototype.hasOwnProperty, nt = Ve.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, rt = {
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
var F = _e.exports;
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
    svelteInit: u
  } = t;
  const g = D(ue(t)), y = D();
  le(e, y, (a) => r(0, s = a));
  const c = D();
  le(e, c, (a) => r(1, i = a));
  const _ = [], f = _t("$$ms-gr-react-wrapper"), {
    slotKey: I,
    slotIndex: S,
    subSlotIndex: m
  } = Oe() || {}, p = u({
    parent: f,
    props: g,
    target: y,
    slot: c,
    slotKey: I,
    slotIndex: S,
    subSlotIndex: m,
    onDestroy(a) {
      _.push(a);
    }
  });
  vt("$$ms-gr-react-wrapper", p), ht(() => {
    g.set(ue(t));
  }), gt(() => {
    _.forEach((a) => a());
  });
  function x(a) {
    se[a ? "unshift" : "push"](() => {
      s = a, y.set(s);
    });
  }
  function w(a) {
    se[a ? "unshift" : "push"](() => {
      i = a, c.set(i);
    });
  }
  return e.$$set = (a) => {
    r(17, t = ie(ie({}, t), ae(a))), "svelteInit" in a && r(5, u = a.svelteInit), "$$scope" in a && r(6, o = a.$$scope);
  }, t = ae(t), [s, i, y, c, l, u, o, n, x, w];
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
    const i = D(), n = new bt({
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
          }, u = o.parent ?? J;
          return u.nodes = [...u.nodes, l], fe({
            createPortal: Y,
            node: J
          }), o.onDestroy(() => {
            u.nodes = u.nodes.filter((g) => g.svelteInstance !== i), fe({
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
    const i = R.Children.toArray(e._reactElement.props.children).map((n) => {
      if (R.isValidElement(n) && n.props.__slot__) {
        const {
          portals: o,
          clonedElement: l
        } = V(n.props.el);
        return R.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...R.Children.toArray(n.props.children), ...o]
        });
      }
      return null;
    });
    return i.originalChildren = e._reactElement.props.children, t.push(Y(R.cloneElement(e._reactElement, {
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
      useCapture: u
    }) => {
      r.addEventListener(l, o, u);
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
  const o = Ue(), [l, u] = X([]), {
    forceClone: g
  } = Ne(), y = g ? !0 : t;
  return he(() => {
    var S;
    if (!o.current || !e)
      return;
    let c = e;
    function _() {
      let m = c;
      if (c.tagName.toLowerCase() === "svelte-slot" && c.children.length === 1 && c.children[0] && (m = c.children[0], m.tagName.toLowerCase() === "react-portal-target" && m.children[0] && (m = m.children[0])), Ct(n, m), r && m.classList.add(...r.split(" ")), s) {
        const p = Rt(s);
        Object.keys(p).forEach((x) => {
          m.style[x] = p[x];
        });
      }
    }
    let f = null, I = null;
    if (y && window.MutationObserver) {
      let m = function() {
        var a, C, d;
        (a = o.current) != null && a.contains(c) && ((C = o.current) == null || C.removeChild(c));
        const {
          portals: x,
          clonedElement: w
        } = V(e);
        c = w, u(x), c.style.display = "contents", I && clearTimeout(I), I = setTimeout(() => {
          _();
        }, 50), (d = o.current) == null || d.appendChild(c);
      };
      m();
      const p = Qe(() => {
        m(), f == null || f.disconnect(), f == null || f.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      f = new window.MutationObserver(p), f.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      c.style.display = "contents", _(), (S = o.current) == null || S.appendChild(c);
    return () => {
      var m, p;
      c.style.display = "", (m = o.current) != null && m.contains(c) && ((p = o.current) == null || p.removeChild(c)), f == null || f.disconnect();
    };
  }, [e, y, r, s, n, i, g]), R.createElement("react-child", {
    ref: o,
    style: {
      display: "contents"
    }
  }, ...l);
}), Pt = ({
  children: e,
  ...t
}) => /* @__PURE__ */ F.jsx(F.Fragment, {
  children: e(t)
});
function Ut(e) {
  return R.createElement(Pt, {
    children: e
  });
}
function pe(e, t) {
  return e ? t != null && t.forceClone || t != null && t.params ? Ut((r) => /* @__PURE__ */ F.jsx(We, {
    forceClone: t == null ? void 0 : t.forceClone,
    params: t == null ? void 0 : t.params,
    children: /* @__PURE__ */ F.jsx(me, {
      slot: e,
      clone: t == null ? void 0 : t.clone,
      ...r
    })
  })) : /* @__PURE__ */ F.jsx(me, {
    slot: e,
    clone: t == null ? void 0 : t.clone
  }) : null;
}
function T({
  key: e,
  slots: t,
  targets: r
}, s) {
  return t[e] ? (...i) => r ? r.map((n, o) => /* @__PURE__ */ F.jsx(R.Fragment, {
    children: pe(n, {
      clone: !0,
      params: i,
      forceClone: !0
    })
  }, o)) : /* @__PURE__ */ F.jsx(F.Fragment, {
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
const Nt = xt(({
  slots: e,
  upload: t,
  showUploadList: r,
  progress: s,
  beforeUpload: i,
  customRequest: n,
  previewFile: o,
  isImageUrl: l,
  itemRender: u,
  iconRender: g,
  data: y,
  onChange: c,
  onValueChange: _,
  onRemove: f,
  maxCount: I,
  fileList: S,
  setSlotParams: m,
  ...p
}) => {
  const x = e["showUploadList.downloadIcon"] || e["showUploadList.removeIcon"] || e["showUploadList.previewIcon"] || e["showUploadList.extra"] || typeof r == "object", w = Tt(r), a = L(w.showPreviewIcon), C = L(w.showRemoveIcon), d = L(w.showDownloadIcon), E = L(i), U = L(n), N = L(s == null ? void 0 : s.format), xe = L(o), Ee = L(l), Le = L(u), Se = L(g), Re = L(y), [Fe, W] = X(!1), [j, B] = X(S);
  he(() => {
    B(S);
  }, [S]);
  const $ = we(() => {
    const k = {};
    return j.map((v) => {
      if (!kt(v)) {
        const P = v.uid || v.url || v.path;
        return k[P] || (k[P] = 0), k[P]++, {
          ...v,
          name: v.orig_name || v.path,
          uid: v.uid || P + "-" + k[P],
          status: "done"
        };
      }
      return v;
    }) || [];
  }, [j]), q = p.disabled || Fe;
  return /* @__PURE__ */ F.jsx(De, {
    ...p,
    disabled: q,
    fileList: $,
    data: Re || y,
    previewFile: xe,
    isImageUrl: Ee,
    maxCount: I,
    itemRender: e.itemRender ? T({
      slots: e,
      key: "itemRender"
    }) : Le,
    iconRender: e.iconRender ? T({
      slots: e,
      key: "iconRender"
    }) : Se,
    customRequest: U || Je,
    onChange: async (k) => {
      try {
        const v = k.file, P = k.fileList, ee = $.findIndex((b) => b.uid === v.uid);
        if (ee !== -1) {
          if (q)
            return;
          f == null || f(v);
          const b = j.slice();
          b.splice(ee, 1), _ == null || _(b), c == null || c(b.map((G) => G.path));
        } else {
          if (E && !await E(v, P) || q)
            return;
          W(!0);
          let b = P.filter((h) => h.status !== "done");
          if (I === 1)
            b = b.slice(0, 1);
          else if (b.length === 0) {
            W(!1);
            return;
          } else if (typeof I == "number") {
            const h = I - j.length;
            b = b.slice(0, h < 0 ? 0 : h);
          }
          const G = j, te = b.map((h) => ({
            ...h,
            size: h.size,
            uid: h.uid,
            name: h.name,
            percent: 99,
            status: "uploading"
          }));
          B((h) => [...I === 1 ? [] : h, ...te]);
          const ne = (await t(b.map((h) => h.originFileObj))).filter(Boolean).map((h, Ce) => ({
            ...h,
            uid: te[Ce].uid
          })), H = I === 1 ? ne : [...G, ...ne];
          W(!1), B(H), _ == null || _(H), c == null || c(H.map((h) => h.path));
        }
      } catch (v) {
        console.error(v), W(!1);
      }
    },
    progress: s && {
      ...s,
      format: N
    },
    showUploadList: x ? {
      ...w,
      showDownloadIcon: d || w.showDownloadIcon,
      showRemoveIcon: C || w.showRemoveIcon,
      showPreviewIcon: a || w.showPreviewIcon,
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
  Nt as Upload,
  Nt as default
};
