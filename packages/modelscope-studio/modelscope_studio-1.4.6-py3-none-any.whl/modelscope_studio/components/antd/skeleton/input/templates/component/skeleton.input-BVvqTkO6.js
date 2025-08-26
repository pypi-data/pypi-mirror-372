import { Z as m, g as N } from "./Index-CaYUepxN.js";
const v = window.ms_globals.ReactDOM.createPortal, U = window.ms_globals.antd.Skeleton, {
  SvelteComponent: V,
  assign: I,
  binding_callbacks: k,
  check_outros: W,
  children: R,
  claim_element: D,
  claim_space: Z,
  component_subscribe: S,
  compute_slots: j,
  create_slot: B,
  detach: _,
  element: A,
  empty: y,
  exclude_internal_props: C,
  get_all_dirty_from_scope: F,
  get_slot_changes: H,
  group_outros: J,
  init: Q,
  insert_hydration: p,
  safe_not_equal: X,
  set_custom_element_data: K,
  space: Y,
  transition_in: g,
  transition_out: h,
  update_slot_base: $
} = window.__gradio__svelte__internal, {
  beforeUpdate: ee,
  getContext: te,
  onDestroy: se,
  setContext: ne
} = window.__gradio__svelte__internal;
function E(r) {
  let s, o;
  const l = (
    /*#slots*/
    r[7].default
  ), n = B(
    l,
    r,
    /*$$scope*/
    r[6],
    null
  );
  return {
    c() {
      s = A("svelte-slot"), n && n.c(), this.h();
    },
    l(e) {
      s = D(e, "SVELTE-SLOT", {
        class: !0
      });
      var t = R(s);
      n && n.l(t), t.forEach(_), this.h();
    },
    h() {
      K(s, "class", "svelte-1rt0kpf");
    },
    m(e, t) {
      p(e, s, t), n && n.m(s, null), r[9](s), o = !0;
    },
    p(e, t) {
      n && n.p && (!o || t & /*$$scope*/
      64) && $(
        n,
        l,
        e,
        /*$$scope*/
        e[6],
        o ? H(
          l,
          /*$$scope*/
          e[6],
          t,
          null
        ) : F(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      o || (g(n, e), o = !0);
    },
    o(e) {
      h(n, e), o = !1;
    },
    d(e) {
      e && _(s), n && n.d(e), r[9](null);
    }
  };
}
function oe(r) {
  let s, o, l, n, e = (
    /*$$slots*/
    r[4].default && E(r)
  );
  return {
    c() {
      s = A("react-portal-target"), o = Y(), e && e.c(), l = y(), this.h();
    },
    l(t) {
      s = D(t, "REACT-PORTAL-TARGET", {
        class: !0
      }), R(s).forEach(_), o = Z(t), e && e.l(t), l = y(), this.h();
    },
    h() {
      K(s, "class", "svelte-1rt0kpf");
    },
    m(t, c) {
      p(t, s, c), r[8](s), p(t, o, c), e && e.m(t, c), p(t, l, c), n = !0;
    },
    p(t, [c]) {
      /*$$slots*/
      t[4].default ? e ? (e.p(t, c), c & /*$$slots*/
      16 && g(e, 1)) : (e = E(t), e.c(), g(e, 1), e.m(l.parentNode, l)) : e && (J(), h(e, 1, 1, () => {
        e = null;
      }), W());
    },
    i(t) {
      n || (g(e), n = !0);
    },
    o(t) {
      h(e), n = !1;
    },
    d(t) {
      t && (_(s), _(o), _(l)), r[8](null), e && e.d(t);
    }
  };
}
function P(r) {
  const {
    svelteInit: s,
    ...o
  } = r;
  return o;
}
function le(r, s, o) {
  let l, n, {
    $$slots: e = {},
    $$scope: t
  } = s;
  const c = j(e);
  let {
    svelteInit: i
  } = s;
  const u = m(P(s)), f = m();
  S(r, f, (a) => o(0, l = a));
  const d = m();
  S(r, d, (a) => o(1, n = a));
  const w = [], L = te("$$ms-gr-react-wrapper"), {
    slotKey: O,
    slotIndex: x,
    subSlotIndex: q
  } = N() || {}, z = i({
    parent: L,
    props: u,
    target: f,
    slot: d,
    slotKey: O,
    slotIndex: x,
    subSlotIndex: q,
    onDestroy(a) {
      w.push(a);
    }
  });
  ne("$$ms-gr-react-wrapper", z), ee(() => {
    u.set(P(s));
  }), se(() => {
    w.forEach((a) => a());
  });
  function G(a) {
    k[a ? "unshift" : "push"](() => {
      l = a, f.set(l);
    });
  }
  function M(a) {
    k[a ? "unshift" : "push"](() => {
      n = a, d.set(n);
    });
  }
  return r.$$set = (a) => {
    o(17, s = I(I({}, s), C(a))), "svelteInit" in a && o(5, i = a.svelteInit), "$$scope" in a && o(6, t = a.$$scope);
  }, s = C(s), [l, n, f, d, c, i, t, e, G, M];
}
class re extends V {
  constructor(s) {
    super(), Q(this, s, le, oe, X, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ie
} = window.__gradio__svelte__internal, T = window.ms_globals.rerender, b = window.ms_globals.tree;
function ae(r, s = {}) {
  function o(l) {
    const n = m(), e = new re({
      ...l,
      props: {
        svelteInit(t) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: n,
            reactComponent: r,
            props: t.props,
            slot: t.slot,
            target: t.target,
            slotIndex: t.slotIndex,
            subSlotIndex: t.subSlotIndex,
            ignore: s.ignore,
            slotKey: t.slotKey,
            nodes: []
          }, i = t.parent ?? b;
          return i.nodes = [...i.nodes, c], T({
            createPortal: v,
            node: b
          }), t.onDestroy(() => {
            i.nodes = i.nodes.filter((u) => u.svelteInstance !== n), T({
              createPortal: v,
              node: b
            });
          }), c;
        },
        ...l.props
      }
    });
    return n.set(e), e;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise.then(() => {
      l(o);
    });
  });
}
const _e = ae(U.Input);
export {
  _e as SkeletonInput,
  _e as default
};
