import { Z as f, g as G } from "./Index-T4cAoDix.js";
const B = window.ms_globals.React, x = window.ms_globals.ReactDOM.createPortal, w = window.ms_globals.createItemsContext.createItemsContext;
var T = {
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
var J = B, M = Symbol.for("react.element"), V = Symbol.for("react.fragment"), Y = Object.prototype.hasOwnProperty, Z = J.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Q = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function H(l, t, r) {
  var s, n = {}, e = null, o = null;
  r !== void 0 && (e = "" + r), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (s in t) Y.call(t, s) && !Q.hasOwnProperty(s) && (n[s] = t[s]);
  if (l && l.defaultProps) for (s in t = l.defaultProps, t) n[s] === void 0 && (n[s] = t[s]);
  return {
    $$typeof: M,
    type: l,
    key: e,
    ref: o,
    props: n,
    _owner: Z.current
  };
}
b.Fragment = V;
b.jsx = H;
b.jsxs = H;
T.exports = b;
var X = T.exports;
const {
  SvelteComponent: $,
  assign: C,
  binding_callbacks: S,
  check_outros: ee,
  children: j,
  claim_element: D,
  claim_space: te,
  component_subscribe: y,
  compute_slots: oe,
  create_slot: ne,
  detach: u,
  element: L,
  empty: P,
  exclude_internal_props: R,
  get_all_dirty_from_scope: se,
  get_slot_changes: le,
  group_outros: re,
  init: ie,
  insert_hydration: p,
  safe_not_equal: ae,
  set_custom_element_data: A,
  space: ce,
  transition_in: I,
  transition_out: h,
  update_slot_base: ue
} = window.__gradio__svelte__internal, {
  beforeUpdate: _e,
  getContext: de,
  onDestroy: me,
  setContext: fe
} = window.__gradio__svelte__internal;
function E(l) {
  let t, r;
  const s = (
    /*#slots*/
    l[7].default
  ), n = ne(
    s,
    l,
    /*$$scope*/
    l[6],
    null
  );
  return {
    c() {
      t = L("svelte-slot"), n && n.c(), this.h();
    },
    l(e) {
      t = D(e, "SVELTE-SLOT", {
        class: !0
      });
      var o = j(t);
      n && n.l(o), o.forEach(u), this.h();
    },
    h() {
      A(t, "class", "svelte-1rt0kpf");
    },
    m(e, o) {
      p(e, t, o), n && n.m(t, null), l[9](t), r = !0;
    },
    p(e, o) {
      n && n.p && (!r || o & /*$$scope*/
      64) && ue(
        n,
        s,
        e,
        /*$$scope*/
        e[6],
        r ? le(
          s,
          /*$$scope*/
          e[6],
          o,
          null
        ) : se(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      r || (I(n, e), r = !0);
    },
    o(e) {
      h(n, e), r = !1;
    },
    d(e) {
      e && u(t), n && n.d(e), l[9](null);
    }
  };
}
function pe(l) {
  let t, r, s, n, e = (
    /*$$slots*/
    l[4].default && E(l)
  );
  return {
    c() {
      t = L("react-portal-target"), r = ce(), e && e.c(), s = P(), this.h();
    },
    l(o) {
      t = D(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(t).forEach(u), r = te(o), e && e.l(o), s = P(), this.h();
    },
    h() {
      A(t, "class", "svelte-1rt0kpf");
    },
    m(o, a) {
      p(o, t, a), l[8](t), p(o, r, a), e && e.m(o, a), p(o, s, a), n = !0;
    },
    p(o, [a]) {
      /*$$slots*/
      o[4].default ? e ? (e.p(o, a), a & /*$$slots*/
      16 && I(e, 1)) : (e = E(o), e.c(), I(e, 1), e.m(s.parentNode, s)) : e && (re(), h(e, 1, 1, () => {
        e = null;
      }), ee());
    },
    i(o) {
      n || (I(e), n = !0);
    },
    o(o) {
      h(e), n = !1;
    },
    d(o) {
      o && (u(t), u(r), u(s)), l[8](null), e && e.d(o);
    }
  };
}
function k(l) {
  const {
    svelteInit: t,
    ...r
  } = l;
  return r;
}
function Ie(l, t, r) {
  let s, n, {
    $$slots: e = {},
    $$scope: o
  } = t;
  const a = oe(e);
  let {
    svelteInit: c
  } = t;
  const _ = f(k(t)), d = f();
  y(l, d, (i) => r(0, s = i));
  const m = f();
  y(l, m, (i) => r(1, n = i));
  const g = [], N = de("$$ms-gr-react-wrapper"), {
    slotKey: q,
    slotIndex: K,
    subSlotIndex: U
  } = G() || {}, F = c({
    parent: N,
    props: _,
    target: d,
    slot: m,
    slotKey: q,
    slotIndex: K,
    subSlotIndex: U,
    onDestroy(i) {
      g.push(i);
    }
  });
  fe("$$ms-gr-react-wrapper", F), _e(() => {
    _.set(k(t));
  }), me(() => {
    g.forEach((i) => i());
  });
  function W(i) {
    S[i ? "unshift" : "push"](() => {
      s = i, d.set(s);
    });
  }
  function z(i) {
    S[i ? "unshift" : "push"](() => {
      n = i, m.set(n);
    });
  }
  return l.$$set = (i) => {
    r(17, t = C(C({}, t), R(i))), "svelteInit" in i && r(5, c = i.svelteInit), "$$scope" in i && r(6, o = i.$$scope);
  }, t = R(t), [s, n, d, m, a, c, o, e, W, z];
}
class we extends $ {
  constructor(t) {
    super(), ie(this, t, Ie, pe, ae, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ge
} = window.__gradio__svelte__internal, O = window.ms_globals.rerender, v = window.ms_globals.tree;
function be(l, t = {}) {
  function r(s) {
    const n = f(), e = new we({
      ...s,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: n,
            reactComponent: l,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, c = o.parent ?? v;
          return c.nodes = [...c.nodes, a], O({
            createPortal: x,
            node: v
          }), o.onDestroy(() => {
            c.nodes = c.nodes.filter((_) => _.svelteInstance !== n), O({
              createPortal: x,
              node: v
            });
          }), a;
        },
        ...s.props
      }
    });
    return n.set(e), e;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise.then(() => {
      s(r);
    });
  });
}
const {
  useItems: xe,
  withItemsContextProvider: Ce,
  ItemHandler: Se
} = w("antd-table-columns"), {
  useItems: ye,
  withItemsContextProvider: Pe,
  ItemHandler: ve
} = w("antd-table-row-selection-selections"), {
  useItems: Re,
  withItemsContextProvider: Ee,
  ItemHandler: ke
} = w("antd-table-row-selection"), {
  useItems: Oe,
  withItemsContextProvider: Te,
  ItemHandler: He
} = w("antd-table-expandable"), je = be((l) => /* @__PURE__ */ X.jsx(ve, {
  ...l
}));
export {
  je as TableRowSelectionSelection,
  je as default
};
