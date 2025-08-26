import { Z as p, g as J } from "./Index-G6_2eAiw.js";
const G = window.ms_globals.React, I = window.ms_globals.ReactDOM.createPortal;
var T = {
  exports: {}
}, v = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var M = G, V = Symbol.for("react.element"), Y = Symbol.for("react.fragment"), Z = Object.prototype.hasOwnProperty, H = M.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Q = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function j(r, t, l) {
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
v.Fragment = Y;
v.jsx = j;
v.jsxs = j;
T.exports = v;
var b = T.exports;
const {
  SvelteComponent: X,
  assign: k,
  binding_callbacks: S,
  check_outros: $,
  children: D,
  claim_element: L,
  claim_space: ee,
  component_subscribe: x,
  compute_slots: te,
  create_slot: se,
  detach: c,
  element: A,
  empty: E,
  exclude_internal_props: R,
  get_all_dirty_from_scope: oe,
  get_slot_changes: ne,
  group_outros: re,
  init: le,
  insert_hydration: m,
  safe_not_equal: ie,
  set_custom_element_data: N,
  space: ae,
  transition_in: g,
  transition_out: w,
  update_slot_base: _e
} = window.__gradio__svelte__internal, {
  beforeUpdate: ce,
  getContext: ue,
  onDestroy: fe,
  setContext: de
} = window.__gradio__svelte__internal;
function O(r) {
  let t, l;
  const n = (
    /*#slots*/
    r[7].default
  ), o = se(
    n,
    r,
    /*$$scope*/
    r[6],
    null
  );
  return {
    c() {
      t = A("svelte-slot"), o && o.c(), this.h();
    },
    l(e) {
      t = L(e, "SVELTE-SLOT", {
        class: !0
      });
      var s = D(t);
      o && o.l(s), s.forEach(c), this.h();
    },
    h() {
      N(t, "class", "svelte-1rt0kpf");
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
        l ? ne(
          n,
          /*$$scope*/
          e[6],
          s,
          null
        ) : oe(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      l || (g(o, e), l = !0);
    },
    o(e) {
      w(o, e), l = !1;
    },
    d(e) {
      e && c(t), o && o.d(e), r[9](null);
    }
  };
}
function pe(r) {
  let t, l, n, o, e = (
    /*$$slots*/
    r[4].default && O(r)
  );
  return {
    c() {
      t = A("react-portal-target"), l = ae(), e && e.c(), n = E(), this.h();
    },
    l(s) {
      t = L(s, "REACT-PORTAL-TARGET", {
        class: !0
      }), D(t).forEach(c), l = ee(s), e && e.l(s), n = E(), this.h();
    },
    h() {
      N(t, "class", "svelte-1rt0kpf");
    },
    m(s, a) {
      m(s, t, a), r[8](t), m(s, l, a), e && e.m(s, a), m(s, n, a), o = !0;
    },
    p(s, [a]) {
      /*$$slots*/
      s[4].default ? e ? (e.p(s, a), a & /*$$slots*/
      16 && g(e, 1)) : (e = O(s), e.c(), g(e, 1), e.m(n.parentNode, n)) : e && (re(), w(e, 1, 1, () => {
        e = null;
      }), $());
    },
    i(s) {
      o || (g(e), o = !0);
    },
    o(s) {
      w(e), o = !1;
    },
    d(s) {
      s && (c(t), c(l), c(n)), r[8](null), e && e.d(s);
    }
  };
}
function C(r) {
  const {
    svelteInit: t,
    ...l
  } = r;
  return l;
}
function me(r, t, l) {
  let n, o, {
    $$slots: e = {},
    $$scope: s
  } = t;
  const a = te(e);
  let {
    svelteInit: _
  } = t;
  const u = p(C(t)), f = p();
  x(r, f, (i) => l(0, n = i));
  const d = p();
  x(r, d, (i) => l(1, o = i));
  const y = [], q = ue("$$ms-gr-react-wrapper"), {
    slotKey: F,
    slotIndex: K,
    subSlotIndex: U
  } = J() || {}, W = _({
    parent: q,
    props: u,
    target: f,
    slot: d,
    slotKey: F,
    slotIndex: K,
    subSlotIndex: U,
    onDestroy(i) {
      y.push(i);
    }
  });
  de("$$ms-gr-react-wrapper", W), ce(() => {
    u.set(C(t));
  }), fe(() => {
    y.forEach((i) => i());
  });
  function z(i) {
    S[i ? "unshift" : "push"](() => {
      n = i, f.set(n);
    });
  }
  function B(i) {
    S[i ? "unshift" : "push"](() => {
      o = i, d.set(o);
    });
  }
  return r.$$set = (i) => {
    l(17, t = k(k({}, t), R(i))), "svelteInit" in i && l(5, _ = i.svelteInit), "$$scope" in i && l(6, s = i.$$scope);
  }, t = R(t), [n, o, f, d, a, _, s, e, z, B];
}
class ge extends X {
  constructor(t) {
    super(), le(this, t, me, pe, ie, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: he
} = window.__gradio__svelte__internal, P = window.ms_globals.rerender, h = window.ms_globals.tree;
function ve(r, t = {}) {
  function l(n) {
    const o = p(), e = new ge({
      ...n,
      props: {
        svelteInit(s) {
          window.ms_globals.autokey += 1;
          const a = {
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
          }, _ = s.parent ?? h;
          return _.nodes = [..._.nodes, a], P({
            createPortal: I,
            node: h
          }), s.onDestroy(() => {
            _.nodes = _.nodes.filter((u) => u.svelteInstance !== o), P({
              createPortal: I,
              node: h
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
      n(l);
    });
  });
}
const we = ve(({
  value: r
}) => /* @__PURE__ */ b.jsx(b.Fragment, {
  children: r || /* @__PURE__ */ b.jsx("span", {})
}));
export {
  we as Text,
  we as default
};
