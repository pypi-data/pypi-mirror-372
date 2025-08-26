import { Z as p, g as G } from "./Index-Lm8czM4o.js";
const B = window.ms_globals.React, y = window.ms_globals.ReactDOM.createPortal, J = window.ms_globals.antd.Flex;
var P = {
  exports: {}
}, b = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var M = B, V = Symbol.for("react.element"), Y = Symbol.for("react.fragment"), Z = Object.prototype.hasOwnProperty, H = M.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Q = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function T(l, t, r) {
  var n, o = {}, e = null, s = null;
  r !== void 0 && (e = "" + r), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (n in t) Z.call(t, n) && !Q.hasOwnProperty(n) && (o[n] = t[n]);
  if (l && l.defaultProps) for (n in t = l.defaultProps, t) o[n] === void 0 && (o[n] = t[n]);
  return {
    $$typeof: V,
    type: l,
    key: e,
    ref: s,
    props: o,
    _owner: H.current
  };
}
b.Fragment = Y;
b.jsx = T;
b.jsxs = T;
P.exports = b;
var X = P.exports;
const {
  SvelteComponent: $,
  assign: I,
  binding_callbacks: k,
  check_outros: ee,
  children: j,
  claim_element: D,
  claim_space: te,
  component_subscribe: x,
  compute_slots: se,
  create_slot: oe,
  detach: c,
  element: L,
  empty: S,
  exclude_internal_props: E,
  get_all_dirty_from_scope: ne,
  get_slot_changes: le,
  group_outros: re,
  init: ie,
  insert_hydration: m,
  safe_not_equal: ae,
  set_custom_element_data: F,
  space: _e,
  transition_in: g,
  transition_out: w,
  update_slot_base: ce
} = window.__gradio__svelte__internal, {
  beforeUpdate: ue,
  getContext: fe,
  onDestroy: de,
  setContext: pe
} = window.__gradio__svelte__internal;
function R(l) {
  let t, r;
  const n = (
    /*#slots*/
    l[7].default
  ), o = oe(
    n,
    l,
    /*$$scope*/
    l[6],
    null
  );
  return {
    c() {
      t = L("svelte-slot"), o && o.c(), this.h();
    },
    l(e) {
      t = D(e, "SVELTE-SLOT", {
        class: !0
      });
      var s = j(t);
      o && o.l(s), s.forEach(c), this.h();
    },
    h() {
      F(t, "class", "svelte-1rt0kpf");
    },
    m(e, s) {
      m(e, t, s), o && o.m(t, null), l[9](t), r = !0;
    },
    p(e, s) {
      o && o.p && (!r || s & /*$$scope*/
      64) && ce(
        o,
        n,
        e,
        /*$$scope*/
        e[6],
        r ? le(
          n,
          /*$$scope*/
          e[6],
          s,
          null
        ) : ne(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      r || (g(o, e), r = !0);
    },
    o(e) {
      w(o, e), r = !1;
    },
    d(e) {
      e && c(t), o && o.d(e), l[9](null);
    }
  };
}
function me(l) {
  let t, r, n, o, e = (
    /*$$slots*/
    l[4].default && R(l)
  );
  return {
    c() {
      t = L("react-portal-target"), r = _e(), e && e.c(), n = S(), this.h();
    },
    l(s) {
      t = D(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(t).forEach(c), r = te(s), e && e.l(s), n = S(), this.h();
    },
    h() {
      F(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      m(s, t, a), l[8](t), m(s, r, a), e && e.m(s, a), m(s, n, a), o = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? e ? (e.p(s, a), a & /*$$slots*/
      16 && g(e, 1)) : (e = R(s), e.c(), g(e, 1), e.m(n.parentNode, n)) : e && (re(), w(e, 1, 1, () => {
        e = null;
      }), ee());
    },
    i(s) {
      o || (g(e), o = !0);
    },
    o(s) {
      w(e), o = !1;
    },
    d(s) {
      s && (c(t), c(r), c(n)), l[8](null), e && e.d(s);
    }
  };
}
function O(l) {
  const {
    svelteInit: t,
    ...r
  } = l;
  return r;
}
function ge(l, t, r) {
  let n, o, {
    $$slots: e = {},
    $$scope: s
  } = t;
  const a = se(e);
  let {
    svelteInit: _
  } = t;
  const u = p(O(t)), f = p();
  x(l, f, (i) => r(0, n = i));
  const d = p();
  x(l, d, (i) => r(1, o = i));
  const h = [], A = fe("$$ms-gr-react-wrapper"), {
    slotKey: N,
    slotIndex: q,
    subSlotIndex: K
  } = G() || {}, U = _({
    parent: A,
    props: u,
    target: f,
    slot: d,
    slotKey: N,
    slotIndex: q,
    subSlotIndex: K,
    onDestroy(i) {
      h.push(i);
    }
  });
  pe("$$ms-gr-react-wrapper", U), ue(() => {
    u.set(O(t));
  }), de(() => {
    h.forEach((i) => i());
  });
  function W(i) {
    k[i ? "unshift" : "push"](() => {
      n = i, f.set(n);
    });
  }
  function z(i) {
    k[i ? "unshift" : "push"](() => {
      o = i, d.set(o);
    });
  }
  return l.$$set = (i) => {
    r(17, t = I(I({}, t), E(i))), "svelteInit" in i && r(5, _ = i.svelteInit), "$$scope" in i && r(6, s = i.$$scope);
  }, t = E(t), [n, o, f, d, a, _, s, e, W, z];
}
class be extends $ {
  constructor(t) {
    super(), ie(this, t, ge, me, ae, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: he
} = window.__gradio__svelte__internal, C = window.ms_globals.rerender, v = window.ms_globals.tree;
function ve(l, t = {}) {
  function r(n) {
    const o = p(), e = new be({
      ...n,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: l,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, _ = s.parent ?? v;
          return _.nodes = [..._.nodes, a], C({
            createPortal: y,
            node: v
          }), s.onDestroy(() => {
            _.nodes = _.nodes.filter((u) => u.svelteInstance !== o), C({
              createPortal: y,
              node: v
            });
          }), a;
        },
        ...n.props
      }
    });
    return o.set(e), e;
  }
  return new Promise((n) => {
    window.ms_globals.initializePromise.then(() => {
      n(r);
    });
  });
}
const ye = ve(({
  children: l,
  ...t
}) => /* @__PURE__ */ X.jsx(J, {
  ...t,
  children: l
}));
export {
  ye as Flex,
  ye as default
};
