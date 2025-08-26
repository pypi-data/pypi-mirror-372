import { Z as p, g as G } from "./Index-CGY9mONI.js";
const B = window.ms_globals.React, y = window.ms_globals.ReactDOM.createPortal, J = window.ms_globals.antd.Checkbox;
var P = {
  exports: {}
}, g = {};
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
function T(r, t, l) {
  var n, o = {}, e = null, s = null;
  l !== void 0 && (e = "" + l), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (s = t.ref);
  for (n in t) Z.call(t, n) && !Q.hasOwnProperty(n) && (o[n] = t[n]);
  if (r && r.defaultProps) for (n in t = r.defaultProps, t) o[n] === void 0 && (o[n] = t[n]);
  return {
    $$typeof: V,
    type: r,
    key: e,
    ref: s,
    props: o,
    _owner: H.current
  };
}
g.Fragment = Y;
g.jsx = T;
g.jsxs = T;
P.exports = g;
var X = P.exports;
const {
  SvelteComponent: $,
  assign: k,
  binding_callbacks: I,
  check_outros: ee,
  children: j,
  claim_element: D,
  claim_space: te,
  component_subscribe: x,
  compute_slots: se,
  create_slot: oe,
  detach: _,
  element: L,
  empty: S,
  exclude_internal_props: E,
  get_all_dirty_from_scope: ne,
  get_slot_changes: re,
  group_outros: le,
  init: ie,
  insert_hydration: m,
  safe_not_equal: ce,
  set_custom_element_data: A,
  space: ae,
  transition_in: b,
  transition_out: w,
  update_slot_base: _e
} = window.__gradio__svelte__internal, {
  beforeUpdate: ue,
  getContext: fe,
  onDestroy: de,
  setContext: pe
} = window.__gradio__svelte__internal;
function R(r) {
  let t, l;
  const n = (
    /*#slots*/
    r[7].default
  ), o = oe(
    n,
    r,
    /*$$scope*/
    r[6],
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
      o && o.l(s), s.forEach(_), this.h();
    },
    h() {
      A(t, "class", "svelte-1rt0kpf");
    },
    m(e, s) {
      m(e, t, s), o && o.m(t, null), r[9](t), l = !0;
    },
    p(e, s) {
      o && o.p && (!l || s & /*$$scope*/
      64) && _e(
        o,
        n,
        e,
        /*$$scope*/
        e[6],
        l ? re(
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
      l || (b(o, e), l = !0);
    },
    o(e) {
      w(o, e), l = !1;
    },
    d(e) {
      e && _(t), o && o.d(e), r[9](null);
    }
  };
}
function me(r) {
  let t, l, n, o, e = (
    /*$$slots*/
    r[4].default && R(r)
  );
  return {
    c() {
      t = L("react-portal-target"), l = ae(), e && e.c(), n = S(), this.h();
    },
    l(s) {
      t = D(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(t).forEach(_), l = te(s), e && e.l(s), n = S(), this.h();
    },
    h() {
      A(t, "class", "svelte-1rt0kpf");
    },
    m(s, c) {
      m(s, t, c), r[8](t), m(s, l, c), e && e.m(s, c), m(s, n, c), o = !0;
    },
    p(s, [c]) {
      /*$$slots*/
      s[4].default ? e ? (e.p(s, c), c & /*$$slots*/
      16 && b(e, 1)) : (e = R(s), e.c(), b(e, 1), e.m(n.parentNode, n)) : e && (le(), w(e, 1, 1, () => {
        e = null;
      }), ee());
    },
    i(s) {
      o || (b(e), o = !0);
    },
    o(s) {
      w(e), o = !1;
    },
    d(s) {
      s && (_(t), _(l), _(n)), r[8](null), e && e.d(s);
    }
  };
}
function O(r) {
  const {
    svelteInit: t,
    ...l
  } = r;
  return l;
}
function be(r, t, l) {
  let n, o, {
    $$slots: e = {},
    $$scope: s
  } = t;
  const c = se(e);
  let {
    svelteInit: a
  } = t;
  const u = p(O(t)), f = p();
  x(r, f, (i) => l(0, n = i));
  const d = p();
  x(r, d, (i) => l(1, o = i));
  const h = [], N = fe("$$ms-gr-react-wrapper"), {
    slotKey: q,
    slotIndex: K,
    subSlotIndex: U
  } = G() || {}, F = a({
    parent: N,
    props: u,
    target: f,
    slot: d,
    slotKey: q,
    slotIndex: K,
    subSlotIndex: U,
    onDestroy(i) {
      h.push(i);
    }
  });
  pe("$$ms-gr-react-wrapper", F), ue(() => {
    u.set(O(t));
  }), de(() => {
    h.forEach((i) => i());
  });
  function W(i) {
    I[i ? "unshift" : "push"](() => {
      n = i, f.set(n);
    });
  }
  function z(i) {
    I[i ? "unshift" : "push"](() => {
      o = i, d.set(o);
    });
  }
  return r.$$set = (i) => {
    l(17, t = k(k({}, t), E(i))), "svelteInit" in i && l(5, a = i.svelteInit), "$$scope" in i && l(6, s = i.$$scope);
  }, t = E(t), [n, o, f, d, c, a, s, e, W, z];
}
class ge extends $ {
  constructor(t) {
    super(), ie(this, t, be, me, ce, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: he
} = window.__gradio__svelte__internal, C = window.ms_globals.rerender, v = window.ms_globals.tree;
function ve(r, t = {}) {
  function l(n) {
    const o = p(), e = new ge({
      ...n,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: r,
            props: s.props,
            slot: s.slot,
            target: s.target,
            slotIndex: s.slotIndex,
            subSlotIndex: s.subSlotIndex,
            ignore: t.ignore,
            slotKey: s.slotKey,
            nodes: []
          }, a = s.parent ?? v;
          return a.nodes = [...a.nodes, c], C({
            createPortal: y,
            node: v
          }), s.onDestroy(() => {
            a.nodes = a.nodes.filter((u) => u.svelteInstance !== o), C({
              createPortal: y,
              node: v
            });
          }), c;
        },
        ...n.props
      }
    });
    return o.set(e), e;
  }
  return new Promise((n) => {
    window.ms_globals.initializePromise.then(() => {
      n(l);
    });
  });
}
const ye = ve(({
  onValueChange: r,
  onChange: t,
  elRef: l,
  ...n
}) => /* @__PURE__ */ X.jsx(J, {
  ...n,
  ref: l,
  onChange: (o) => {
    t == null || t(o), r(o.target.checked);
  }
}));
export {
  ye as Checkbox,
  ye as default
};
