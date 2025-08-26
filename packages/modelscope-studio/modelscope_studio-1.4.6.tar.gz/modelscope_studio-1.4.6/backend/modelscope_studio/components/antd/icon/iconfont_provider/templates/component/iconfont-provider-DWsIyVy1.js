import { b as V, Z as m, g as Y } from "./Index-DppExZu6.js";
const G = window.ms_globals.React, J = window.ms_globals.React.useRef, U = window.ms_globals.React.useMemo, h = window.ms_globals.ReactDOM.createPortal, Z = window.ms_globals.internalContext.IconFontContext, H = window.ms_globals.antdIcons.createFromIconfontCN;
function y(l, e) {
  return V(l, e);
}
var T = {
  exports: {}
}, w = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Q = G, X = Symbol.for("react.element"), $ = Symbol.for("react.fragment"), ee = Object.prototype.hasOwnProperty, te = Q.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, ne = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function F(l, e, r) {
  var o, s = {}, t = null, n = null;
  r !== void 0 && (t = "" + r), e.key !== void 0 && (t = "" + e.key), e.ref !== void 0 && (n = e.ref);
  for (o in e) ee.call(e, o) && !ne.hasOwnProperty(o) && (s[o] = e[o]);
  if (l && l.defaultProps) for (o in e = l.defaultProps, e) s[o] === void 0 && (s[o] = e[o]);
  return {
    $$typeof: X,
    type: l,
    key: t,
    ref: n,
    props: s,
    _owner: te.current
  };
}
w.Fragment = $;
w.jsx = F;
w.jsxs = F;
T.exports = w;
var oe = T.exports;
const {
  SvelteComponent: se,
  assign: R,
  binding_callbacks: E,
  check_outros: re,
  children: j,
  claim_element: D,
  claim_space: le,
  component_subscribe: k,
  compute_slots: ce,
  create_slot: ae,
  detach: u,
  element: L,
  empty: S,
  exclude_internal_props: x,
  get_all_dirty_from_scope: ie,
  get_slot_changes: ue,
  group_outros: _e,
  init: fe,
  insert_hydration: p,
  safe_not_equal: de,
  set_custom_element_data: N,
  space: me,
  transition_in: g,
  transition_out: v,
  update_slot_base: pe
} = window.__gradio__svelte__internal, {
  beforeUpdate: ge,
  getContext: we,
  onDestroy: be,
  setContext: ve
} = window.__gradio__svelte__internal;
function C(l) {
  let e, r;
  const o = (
    /*#slots*/
    l[7].default
  ), s = ae(
    o,
    l,
    /*$$scope*/
    l[6],
    null
  );
  return {
    c() {
      e = L("svelte-slot"), s && s.c(), this.h();
    },
    l(t) {
      e = D(t, "SVELTE-SLOT", {
        class: !0
      });
      var n = j(e);
      s && s.l(n), n.forEach(u), this.h();
    },
    h() {
      N(e, "class", "svelte-1rt0kpf");
    },
    m(t, n) {
      p(t, e, n), s && s.m(e, null), l[9](e), r = !0;
    },
    p(t, n) {
      s && s.p && (!r || n & /*$$scope*/
      64) && pe(
        s,
        o,
        t,
        /*$$scope*/
        t[6],
        r ? ue(
          o,
          /*$$scope*/
          t[6],
          n,
          null
        ) : ie(
          /*$$scope*/
          t[6]
        ),
        null
      );
    },
    i(t) {
      r || (g(s, t), r = !0);
    },
    o(t) {
      v(s, t), r = !1;
    },
    d(t) {
      t && u(e), s && s.d(t), l[9](null);
    }
  };
}
function Ie(l) {
  let e, r, o, s, t = (
    /*$$slots*/
    l[4].default && C(l)
  );
  return {
    c() {
      e = L("react-portal-target"), r = me(), t && t.c(), o = S(), this.h();
    },
    l(n) {
      e = D(n, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(e).forEach(u), r = le(n), t && t.l(n), o = S(), this.h();
    },
    h() {
      N(e, "class", "svelte-1rt0kpf");
    },
    m(n, a) {
      p(n, e, a), l[8](e), p(n, r, a), t && t.m(n, a), p(n, o, a), s = !0;
    },
    p(n, [a]) {
      /*$$slots*/
      n[4].default ? t ? (t.p(n, a), a & /*$$slots*/
      16 && g(t, 1)) : (t = C(n), t.c(), g(t, 1), t.m(o.parentNode, o)) : t && (_e(), v(t, 1, 1, () => {
        t = null;
      }), re());
    },
    i(n) {
      s || (g(t), s = !0);
    },
    o(n) {
      v(t), s = !1;
    },
    d(n) {
      n && (u(e), u(r), u(o)), l[8](null), t && t.d(n);
    }
  };
}
function O(l) {
  const {
    svelteInit: e,
    ...r
  } = l;
  return r;
}
function he(l, e, r) {
  let o, s, {
    $$slots: t = {},
    $$scope: n
  } = e;
  const a = ce(t);
  let {
    svelteInit: i
  } = e;
  const _ = m(O(e)), f = m();
  k(l, f, (c) => r(0, o = c));
  const d = m();
  k(l, d, (c) => r(1, s = c));
  const I = [], q = we("$$ms-gr-react-wrapper"), {
    slotKey: A,
    slotIndex: K,
    subSlotIndex: M
  } = Y() || {}, W = i({
    parent: q,
    props: _,
    target: f,
    slot: d,
    slotKey: A,
    slotIndex: K,
    subSlotIndex: M,
    onDestroy(c) {
      I.push(c);
    }
  });
  ve("$$ms-gr-react-wrapper", W), ge(() => {
    _.set(O(e));
  }), be(() => {
    I.forEach((c) => c());
  });
  function z(c) {
    E[c ? "unshift" : "push"](() => {
      o = c, f.set(o);
    });
  }
  function B(c) {
    E[c ? "unshift" : "push"](() => {
      s = c, d.set(s);
    });
  }
  return l.$$set = (c) => {
    r(17, e = R(R({}, e), x(c))), "svelteInit" in c && r(5, i = c.svelteInit), "$$scope" in c && r(6, n = c.$$scope);
  }, e = x(e), [o, s, f, d, a, i, n, t, z, B];
}
class ye extends se {
  constructor(e) {
    super(), fe(this, e, he, Ie, de, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ke
} = window.__gradio__svelte__internal, P = window.ms_globals.rerender, b = window.ms_globals.tree;
function Re(l, e = {}) {
  function r(o) {
    const s = m(), t = new ye({
      ...o,
      props: {
        svelteInit(n) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: l,
            props: n.props,
            slot: n.slot,
            target: n.target,
            slotIndex: n.slotIndex,
            subSlotIndex: n.subSlotIndex,
            ignore: e.ignore,
            slotKey: n.slotKey,
            nodes: []
          }, i = n.parent ?? b;
          return i.nodes = [...i.nodes, a], P({
            createPortal: h,
            node: b
          }), n.onDestroy(() => {
            i.nodes = i.nodes.filter((_) => _.svelteInstance !== s), P({
              createPortal: h,
              node: b
            });
          }), a;
        },
        ...o.props
      }
    });
    return s.set(t), t;
  }
  return new Promise((o) => {
    window.ms_globals.initializePromise.then(() => {
      o(r);
    });
  });
}
const Se = Re(({
  children: l,
  extraCommonProps: e,
  scriptUrl: r
}) => {
  const o = J({}), s = U(() => (o.current.iconfont && y(o.current.scriptUrl, r) && y(o.current.extraCommonProps, e) || (o.current = {
    scriptUrl: r,
    extraCommonProps: e,
    iconfont: H({
      scriptUrl: r,
      extraCommonProps: e
    })
  }), o.current.iconfont), [e, r]);
  return /* @__PURE__ */ oe.jsx(Z.Provider, {
    value: s || null,
    children: l
  });
});
export {
  Se as Icon,
  Se as default
};
