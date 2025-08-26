import { Z as m, g as N } from "./Index-C2Ztdipe.js";
const v = window.ms_globals.ReactDOM.createPortal, U = window.ms_globals.antd.Skeleton, {
  SvelteComponent: V,
  assign: I,
  binding_callbacks: k,
  check_outros: W,
  children: A,
  claim_element: R,
  claim_space: Z,
  component_subscribe: S,
  compute_slots: j,
  create_slot: B,
  detach: _,
  element: D,
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
  setContext: oe
} = window.__gradio__svelte__internal;
function E(r) {
  let s, n;
  const l = (
    /*#slots*/
    r[7].default
  ), o = B(
    l,
    r,
    /*$$scope*/
    r[6],
    null
  );
  return {
    c() {
      s = D("svelte-slot"), o && o.c(), this.h();
    },
    l(e) {
      s = R(e, "SVELTE-SLOT", {
        class: !0
      });
      var t = A(s);
      o && o.l(t), t.forEach(_), this.h();
    },
    h() {
      K(s, "class", "svelte-1rt0kpf");
    },
    m(e, t) {
      p(e, s, t), o && o.m(s, null), r[9](s), n = !0;
    },
    p(e, t) {
      o && o.p && (!n || t & /*$$scope*/
      64) && $(
        o,
        l,
        e,
        /*$$scope*/
        e[6],
        n ? H(
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
      n || (g(o, e), n = !0);
    },
    o(e) {
      h(o, e), n = !1;
    },
    d(e) {
      e && _(s), o && o.d(e), r[9](null);
    }
  };
}
function ne(r) {
  let s, n, l, o, e = (
    /*$$slots*/
    r[4].default && E(r)
  );
  return {
    c() {
      s = D("react-portal-target"), n = Y(), e && e.c(), l = y(), this.h();
    },
    l(t) {
      s = R(t, "REACT-PORTAL-TARGET", {
        class: !0
      }), A(s).forEach(_), n = Z(t), e && e.l(t), l = y(), this.h();
    },
    h() {
      K(s, "class", "svelte-1rt0kpf");
    },
    m(t, c) {
      p(t, s, c), r[8](s), p(t, n, c), e && e.m(t, c), p(t, l, c), o = !0;
    },
    p(t, [c]) {
      /*$$slots*/
      t[4].default ? e ? (e.p(t, c), c & /*$$slots*/
      16 && g(e, 1)) : (e = E(t), e.c(), g(e, 1), e.m(l.parentNode, l)) : e && (J(), h(e, 1, 1, () => {
        e = null;
      }), W());
    },
    i(t) {
      o || (g(e), o = !0);
    },
    o(t) {
      h(e), o = !1;
    },
    d(t) {
      t && (_(s), _(n), _(l)), r[8](null), e && e.d(t);
    }
  };
}
function P(r) {
  const {
    svelteInit: s,
    ...n
  } = r;
  return n;
}
function le(r, s, n) {
  let l, o, {
    $$slots: e = {},
    $$scope: t
  } = s;
  const c = j(e);
  let {
    svelteInit: i
  } = s;
  const u = m(P(s)), f = m();
  S(r, f, (a) => n(0, l = a));
  const d = m();
  S(r, d, (a) => n(1, o = a));
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
  oe("$$ms-gr-react-wrapper", z), ee(() => {
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
      o = a, d.set(o);
    });
  }
  return r.$$set = (a) => {
    n(17, s = I(I({}, s), C(a))), "svelteInit" in a && n(5, i = a.svelteInit), "$$scope" in a && n(6, t = a.$$scope);
  }, s = C(s), [l, o, f, d, c, i, t, e, G, M];
}
class re extends V {
  constructor(s) {
    super(), Q(this, s, le, ne, X, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ie
} = window.__gradio__svelte__internal, T = window.ms_globals.rerender, b = window.ms_globals.tree;
function ae(r, s = {}) {
  function n(l) {
    const o = m(), e = new re({
      ...l,
      props: {
        svelteInit(t) {
          window.ms_globals.autokey += 1;
          const c = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
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
            i.nodes = i.nodes.filter((u) => u.svelteInstance !== o), T({
              createPortal: v,
              node: b
            });
          }), c;
        },
        ...l.props
      }
    });
    return o.set(e), e;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise.then(() => {
      l(n);
    });
  });
}
const _e = ae(U.Avatar);
export {
  _e as SkeletonAvatar,
  _e as default
};
