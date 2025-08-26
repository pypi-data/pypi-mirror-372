import { aQ as Ge, aR as Mn, aS as Qe, aT as Je, aU as Ke, aV as re, aW as Sn, _ as h, g as Fn, s as Un, q as En, p as In, a as An, b as Ln, c as _t, d as qt, e as Wn, l as Qt, k as Yn, j as On, y as Nn, u as Hn } from "./mermaid.core-BbULqNNQ.js";
import { e as Vn, g as Pn, H as tt, I as Rn, J as zn } from "./Index-tGU7TQVz.js";
import { b as Bn, t as Ae, c as qn, a as Zn, l as Xn } from "./linear-CH5XRYVR.js";
import { i as jn } from "./init-DjUOC4st.js";
function Gn(t, e) {
  let n;
  if (e === void 0)
    for (const r of t)
      r != null && (n < r || n === void 0 && r >= r) && (n = r);
  else {
    let r = -1;
    for (let i of t)
      (i = e(i, ++r, t)) != null && (n < i || n === void 0 && i >= i) && (n = i);
  }
  return n;
}
function Qn(t, e) {
  let n;
  if (e === void 0)
    for (const r of t)
      r != null && (n > r || n === void 0 && r >= r) && (n = r);
  else {
    let r = -1;
    for (let i of t)
      (i = e(i, ++r, t)) != null && (n > i || n === void 0 && i >= i) && (n = i);
  }
  return n;
}
function Jn(t) {
  return t;
}
var Xt = 1, ie = 2, me = 3, Zt = 4, Le = 1e-6;
function Kn(t) {
  return "translate(" + t + ",0)";
}
function $n(t) {
  return "translate(0," + t + ")";
}
function tr(t) {
  return (e) => +t(e);
}
function er(t, e) {
  return e = Math.max(0, t.bandwidth() - e * 2) / 2, t.round() && (e = Math.round(e)), (n) => +t(n) + e;
}
function nr() {
  return !this.__axis;
}
function $e(t, e) {
  var n = [], r = null, i = null, a = 6, s = 6, C = 3, M = typeof window < "u" && window.devicePixelRatio > 1 ? 0 : 0.5, T = t === Xt || t === Zt ? -1 : 1, v = t === Zt || t === ie ? "x" : "y", A = t === Xt || t === me ? Kn : $n;
  function b(p) {
    var R = r ?? (e.ticks ? e.ticks.apply(e, n) : e.domain()), I = i ?? (e.tickFormat ? e.tickFormat.apply(e, n) : Jn), et = Math.max(a, 0) + C, rt = e.range(), nt = +rt[0] + M, Z = +rt[rt.length - 1] + M, X = (e.bandwidth ? er : tr)(e.copy(), M), $ = p.selection ? p.selection() : p, x = $.selectAll(".domain").data([null]), H = $.selectAll(".tick").data(R, e).order(), w = H.exit(), F = H.enter().append("g").attr("class", "tick"), D = H.select("line"), _ = H.select("text");
    x = x.merge(x.enter().insert("path", ".tick").attr("class", "domain").attr("stroke", "currentColor")), H = H.merge(F), D = D.merge(F.append("line").attr("stroke", "currentColor").attr(v + "2", T * a)), _ = _.merge(F.append("text").attr("fill", "currentColor").attr(v, T * et).attr("dy", t === Xt ? "0em" : t === me ? "0.71em" : "0.32em")), p !== $ && (x = x.transition(p), H = H.transition(p), D = D.transition(p), _ = _.transition(p), w = w.transition(p).attr("opacity", Le).attr("transform", function(k) {
      return isFinite(k = X(k)) ? A(k + M) : this.getAttribute("transform");
    }), F.attr("opacity", Le).attr("transform", function(k) {
      var L = this.parentNode.__axis;
      return A((L && isFinite(L = L(k)) ? L : X(k)) + M);
    })), w.remove(), x.attr("d", t === Zt || t === ie ? s ? "M" + T * s + "," + nt + "H" + M + "V" + Z + "H" + T * s : "M" + M + "," + nt + "V" + Z : s ? "M" + nt + "," + T * s + "V" + M + "H" + Z + "V" + T * s : "M" + nt + "," + M + "H" + Z), H.attr("opacity", 1).attr("transform", function(k) {
      return A(X(k) + M);
    }), D.attr(v + "2", T * a), _.attr(v, T * et).text(I), $.filter(nr).attr("fill", "none").attr("font-size", 10).attr("font-family", "sans-serif").attr("text-anchor", t === ie ? "start" : t === Zt ? "end" : "middle"), $.each(function() {
      this.__axis = X;
    });
  }
  return b.scale = function(p) {
    return arguments.length ? (e = p, b) : e;
  }, b.ticks = function() {
    return n = Array.from(arguments), b;
  }, b.tickArguments = function(p) {
    return arguments.length ? (n = p == null ? [] : Array.from(p), b) : n.slice();
  }, b.tickValues = function(p) {
    return arguments.length ? (r = p == null ? null : Array.from(p), b) : r && r.slice();
  }, b.tickFormat = function(p) {
    return arguments.length ? (i = p, b) : i;
  }, b.tickSize = function(p) {
    return arguments.length ? (a = s = +p, b) : a;
  }, b.tickSizeInner = function(p) {
    return arguments.length ? (a = +p, b) : a;
  }, b.tickSizeOuter = function(p) {
    return arguments.length ? (s = +p, b) : s;
  }, b.tickPadding = function(p) {
    return arguments.length ? (C = +p, b) : C;
  }, b.offset = function(p) {
    return arguments.length ? (M = +p, b) : M;
  }, b;
}
function rr(t) {
  return $e(Xt, t);
}
function ir(t) {
  return $e(me, t);
}
const ar = Math.PI / 180, sr = 180 / Math.PI, Jt = 18, tn = 0.96422, en = 1, nn = 0.82521, rn = 4 / 29, Mt = 6 / 29, an = 3 * Mt * Mt, or = Mt * Mt * Mt;
function sn(t) {
  if (t instanceof lt) return new lt(t.l, t.a, t.b, t.opacity);
  if (t instanceof dt) return on(t);
  t instanceof Ge || (t = Mn(t));
  var e = ce(t.r), n = ce(t.g), r = ce(t.b), i = ae((0.2225045 * e + 0.7168786 * n + 0.0606169 * r) / en), a, s;
  return e === n && n === r ? a = s = i : (a = ae((0.4360747 * e + 0.3850649 * n + 0.1430804 * r) / tn), s = ae((0.0139322 * e + 0.0971045 * n + 0.7141733 * r) / nn)), new lt(116 * i - 16, 500 * (a - i), 200 * (i - s), t.opacity);
}
function cr(t, e, n, r) {
  return arguments.length === 1 ? sn(t) : new lt(t, e, n, r ?? 1);
}
function lt(t, e, n, r) {
  this.l = +t, this.a = +e, this.b = +n, this.opacity = +r;
}
Qe(lt, cr, Je(Ke, {
  brighter(t) {
    return new lt(this.l + Jt * (t ?? 1), this.a, this.b, this.opacity);
  },
  darker(t) {
    return new lt(this.l - Jt * (t ?? 1), this.a, this.b, this.opacity);
  },
  rgb() {
    var t = (this.l + 16) / 116, e = isNaN(this.a) ? t : t + this.a / 500, n = isNaN(this.b) ? t : t - this.b / 200;
    return e = tn * se(e), t = en * se(t), n = nn * se(n), new Ge(oe(3.1338561 * e - 1.6168667 * t - 0.4906146 * n), oe(-0.9787684 * e + 1.9161415 * t + 0.033454 * n), oe(0.0719453 * e - 0.2289914 * t + 1.4052427 * n), this.opacity);
  }
}));
function ae(t) {
  return t > or ? Math.pow(t, 1 / 3) : t / an + rn;
}
function se(t) {
  return t > Mt ? t * t * t : an * (t - rn);
}
function oe(t) {
  return 255 * (t <= 31308e-7 ? 12.92 * t : 1.055 * Math.pow(t, 1 / 2.4) - 0.055);
}
function ce(t) {
  return (t /= 255) <= 0.04045 ? t / 12.92 : Math.pow((t + 0.055) / 1.055, 2.4);
}
function lr(t) {
  if (t instanceof dt) return new dt(t.h, t.c, t.l, t.opacity);
  if (t instanceof lt || (t = sn(t)), t.a === 0 && t.b === 0) return new dt(NaN, 0 < t.l && t.l < 100 ? 0 : NaN, t.l, t.opacity);
  var e = Math.atan2(t.b, t.a) * sr;
  return new dt(e < 0 ? e + 360 : e, Math.sqrt(t.a * t.a + t.b * t.b), t.l, t.opacity);
}
function ge(t, e, n, r) {
  return arguments.length === 1 ? lr(t) : new dt(t, e, n, r ?? 1);
}
function dt(t, e, n, r) {
  this.h = +t, this.c = +e, this.l = +n, this.opacity = +r;
}
function on(t) {
  if (isNaN(t.h)) return new lt(t.l, 0, 0, t.opacity);
  var e = t.h * ar;
  return new lt(t.l, Math.cos(e) * t.c, Math.sin(e) * t.c, t.opacity);
}
Qe(dt, ge, Je(Ke, {
  brighter(t) {
    return new dt(this.h, this.c, this.l + Jt * (t ?? 1), this.opacity);
  },
  darker(t) {
    return new dt(this.h, this.c, this.l - Jt * (t ?? 1), this.opacity);
  },
  rgb() {
    return on(this).rgb();
  }
}));
function ur(t) {
  return function(e, n) {
    var r = t((e = ge(e)).h, (n = ge(n)).h), i = re(e.c, n.c), a = re(e.l, n.l), s = re(e.opacity, n.opacity);
    return function(C) {
      return e.h = r(C), e.c = i(C), e.l = a(C), e.opacity = s(C), e + "";
    };
  };
}
const fr = ur(Sn);
function hr(t, e) {
  t = t.slice();
  var n = 0, r = t.length - 1, i = t[n], a = t[r], s;
  return a < i && (s = n, n = r, r = s, s = i, i = a, a = s), t[n] = e.floor(i), t[r] = e.ceil(a), t;
}
const le = /* @__PURE__ */ new Date(), ue = /* @__PURE__ */ new Date();
function G(t, e, n, r) {
  function i(a) {
    return t(a = arguments.length === 0 ? /* @__PURE__ */ new Date() : /* @__PURE__ */ new Date(+a)), a;
  }
  return i.floor = (a) => (t(a = /* @__PURE__ */ new Date(+a)), a), i.ceil = (a) => (t(a = new Date(a - 1)), e(a, 1), t(a), a), i.round = (a) => {
    const s = i(a), C = i.ceil(a);
    return a - s < C - a ? s : C;
  }, i.offset = (a, s) => (e(a = /* @__PURE__ */ new Date(+a), s == null ? 1 : Math.floor(s)), a), i.range = (a, s, C) => {
    const M = [];
    if (a = i.ceil(a), C = C == null ? 1 : Math.floor(C), !(a < s) || !(C > 0)) return M;
    let T;
    do
      M.push(T = /* @__PURE__ */ new Date(+a)), e(a, C), t(a);
    while (T < a && a < s);
    return M;
  }, i.filter = (a) => G((s) => {
    if (s >= s) for (; t(s), !a(s); ) s.setTime(s - 1);
  }, (s, C) => {
    if (s >= s)
      if (C < 0) for (; ++C <= 0; )
        for (; e(s, -1), !a(s); )
          ;
      else for (; --C >= 0; )
        for (; e(s, 1), !a(s); )
          ;
  }), n && (i.count = (a, s) => (le.setTime(+a), ue.setTime(+s), t(le), t(ue), Math.floor(n(le, ue))), i.every = (a) => (a = Math.floor(a), !isFinite(a) || !(a > 0) ? null : a > 1 ? i.filter(r ? (s) => r(s) % a === 0 : (s) => i.count(0, s) % a === 0) : i)), i;
}
const Ft = G(() => {
}, (t, e) => {
  t.setTime(+t + e);
}, (t, e) => e - t);
Ft.every = (t) => (t = Math.floor(t), !isFinite(t) || !(t > 0) ? null : t > 1 ? G((e) => {
  e.setTime(Math.floor(e / t) * t);
}, (e, n) => {
  e.setTime(+e + n * t);
}, (e, n) => (n - e) / t) : Ft);
Ft.range;
const mt = 1e3, at = mt * 60, gt = at * 60, yt = gt * 24, ve = yt * 7, We = yt * 30, fe = yt * 365, pt = G((t) => {
  t.setTime(t - t.getMilliseconds());
}, (t, e) => {
  t.setTime(+t + e * mt);
}, (t, e) => (e - t) / mt, (t) => t.getUTCSeconds());
pt.range;
const Wt = G((t) => {
  t.setTime(t - t.getMilliseconds() - t.getSeconds() * mt);
}, (t, e) => {
  t.setTime(+t + e * at);
}, (t, e) => (e - t) / at, (t) => t.getMinutes());
Wt.range;
const dr = G((t) => {
  t.setUTCSeconds(0, 0);
}, (t, e) => {
  t.setTime(+t + e * at);
}, (t, e) => (e - t) / at, (t) => t.getUTCMinutes());
dr.range;
const Yt = G((t) => {
  t.setTime(t - t.getMilliseconds() - t.getSeconds() * mt - t.getMinutes() * at);
}, (t, e) => {
  t.setTime(+t + e * gt);
}, (t, e) => (e - t) / gt, (t) => t.getHours());
Yt.range;
const mr = G((t) => {
  t.setUTCMinutes(0, 0, 0);
}, (t, e) => {
  t.setTime(+t + e * gt);
}, (t, e) => (e - t) / gt, (t) => t.getUTCHours());
mr.range;
const Tt = G((t) => t.setHours(0, 0, 0, 0), (t, e) => t.setDate(t.getDate() + e), (t, e) => (e - t - (e.getTimezoneOffset() - t.getTimezoneOffset()) * at) / yt, (t) => t.getDate() - 1);
Tt.range;
const be = G((t) => {
  t.setUTCHours(0, 0, 0, 0);
}, (t, e) => {
  t.setUTCDate(t.getUTCDate() + e);
}, (t, e) => (e - t) / yt, (t) => t.getUTCDate() - 1);
be.range;
const gr = G((t) => {
  t.setUTCHours(0, 0, 0, 0);
}, (t, e) => {
  t.setUTCDate(t.getUTCDate() + e);
}, (t, e) => (e - t) / yt, (t) => Math.floor(t / yt));
gr.range;
function xt(t) {
  return G((e) => {
    e.setDate(e.getDate() - (e.getDay() + 7 - t) % 7), e.setHours(0, 0, 0, 0);
  }, (e, n) => {
    e.setDate(e.getDate() + n * 7);
  }, (e, n) => (n - e - (n.getTimezoneOffset() - e.getTimezoneOffset()) * at) / ve);
}
const Ht = xt(0), Ot = xt(1), cn = xt(2), ln = xt(3), vt = xt(4), un = xt(5), fn = xt(6);
Ht.range;
Ot.range;
cn.range;
ln.range;
vt.range;
un.range;
fn.range;
function wt(t) {
  return G((e) => {
    e.setUTCDate(e.getUTCDate() - (e.getUTCDay() + 7 - t) % 7), e.setUTCHours(0, 0, 0, 0);
  }, (e, n) => {
    e.setUTCDate(e.getUTCDate() + n * 7);
  }, (e, n) => (n - e) / ve);
}
const hn = wt(0), Kt = wt(1), yr = wt(2), kr = wt(3), Ut = wt(4), pr = wt(5), Tr = wt(6);
hn.range;
Kt.range;
yr.range;
kr.range;
Ut.range;
pr.range;
Tr.range;
const Nt = G((t) => {
  t.setDate(1), t.setHours(0, 0, 0, 0);
}, (t, e) => {
  t.setMonth(t.getMonth() + e);
}, (t, e) => e.getMonth() - t.getMonth() + (e.getFullYear() - t.getFullYear()) * 12, (t) => t.getMonth());
Nt.range;
const vr = G((t) => {
  t.setUTCDate(1), t.setUTCHours(0, 0, 0, 0);
}, (t, e) => {
  t.setUTCMonth(t.getUTCMonth() + e);
}, (t, e) => e.getUTCMonth() - t.getUTCMonth() + (e.getUTCFullYear() - t.getUTCFullYear()) * 12, (t) => t.getUTCMonth());
vr.range;
const kt = G((t) => {
  t.setMonth(0, 1), t.setHours(0, 0, 0, 0);
}, (t, e) => {
  t.setFullYear(t.getFullYear() + e);
}, (t, e) => e.getFullYear() - t.getFullYear(), (t) => t.getFullYear());
kt.every = (t) => !isFinite(t = Math.floor(t)) || !(t > 0) ? null : G((e) => {
  e.setFullYear(Math.floor(e.getFullYear() / t) * t), e.setMonth(0, 1), e.setHours(0, 0, 0, 0);
}, (e, n) => {
  e.setFullYear(e.getFullYear() + n * t);
});
kt.range;
const bt = G((t) => {
  t.setUTCMonth(0, 1), t.setUTCHours(0, 0, 0, 0);
}, (t, e) => {
  t.setUTCFullYear(t.getUTCFullYear() + e);
}, (t, e) => e.getUTCFullYear() - t.getUTCFullYear(), (t) => t.getUTCFullYear());
bt.every = (t) => !isFinite(t = Math.floor(t)) || !(t > 0) ? null : G((e) => {
  e.setUTCFullYear(Math.floor(e.getUTCFullYear() / t) * t), e.setUTCMonth(0, 1), e.setUTCHours(0, 0, 0, 0);
}, (e, n) => {
  e.setUTCFullYear(e.getUTCFullYear() + n * t);
});
bt.range;
function br(t, e, n, r, i, a) {
  const s = [[pt, 1, mt], [pt, 5, 5 * mt], [pt, 15, 15 * mt], [pt, 30, 30 * mt], [a, 1, at], [a, 5, 5 * at], [a, 15, 15 * at], [a, 30, 30 * at], [i, 1, gt], [i, 3, 3 * gt], [i, 6, 6 * gt], [i, 12, 12 * gt], [r, 1, yt], [r, 2, 2 * yt], [n, 1, ve], [e, 1, We], [e, 3, 3 * We], [t, 1, fe]];
  function C(T, v, A) {
    const b = v < T;
    b && ([T, v] = [v, T]);
    const p = A && typeof A.range == "function" ? A : M(T, v, A), R = p ? p.range(T, +v + 1) : [];
    return b ? R.reverse() : R;
  }
  function M(T, v, A) {
    const b = Math.abs(v - T) / A, p = Bn(([, , et]) => et).right(s, b);
    if (p === s.length) return t.every(Ae(T / fe, v / fe, A));
    if (p === 0) return Ft.every(Math.max(Ae(T, v, A), 1));
    const [R, I] = s[b / s[p - 1][2] < s[p][2] / b ? p - 1 : p];
    return R.every(I);
  }
  return [C, M];
}
const [xr, wr] = br(kt, Nt, Ht, Tt, Yt, Wt);
function he(t) {
  if (0 <= t.y && t.y < 100) {
    var e = new Date(-1, t.m, t.d, t.H, t.M, t.S, t.L);
    return e.setFullYear(t.y), e;
  }
  return new Date(t.y, t.m, t.d, t.H, t.M, t.S, t.L);
}
function de(t) {
  if (0 <= t.y && t.y < 100) {
    var e = new Date(Date.UTC(-1, t.m, t.d, t.H, t.M, t.S, t.L));
    return e.setUTCFullYear(t.y), e;
  }
  return new Date(Date.UTC(t.y, t.m, t.d, t.H, t.M, t.S, t.L));
}
function It(t, e, n) {
  return {
    y: t,
    m: e,
    d: n,
    H: 0,
    M: 0,
    S: 0,
    L: 0
  };
}
function Cr(t) {
  var e = t.dateTime, n = t.date, r = t.time, i = t.periods, a = t.days, s = t.shortDays, C = t.months, M = t.shortMonths, T = At(i), v = Lt(i), A = At(a), b = Lt(a), p = At(s), R = Lt(s), I = At(C), et = Lt(C), rt = At(M), nt = Lt(M), Z = {
    a: m,
    A: U,
    b: c,
    B: l,
    c: null,
    d: Pe,
    e: Pe,
    f: Xr,
    g: ri,
    G: ai,
    H: Br,
    I: qr,
    j: Zr,
    L: dn,
    m: jr,
    M: Gr,
    p: o,
    q: V,
    Q: Be,
    s: qe,
    S: Qr,
    u: Jr,
    U: Kr,
    V: $r,
    w: ti,
    W: ei,
    x: null,
    X: null,
    y: ni,
    Y: ii,
    Z: si,
    "%": ze
  }, X = {
    a: Y,
    A: O,
    b: Q,
    B: z,
    c: null,
    d: Re,
    e: Re,
    f: ui,
    g: vi,
    G: xi,
    H: oi,
    I: ci,
    j: li,
    L: gn,
    m: fi,
    M: hi,
    p: B,
    q: st,
    Q: Be,
    s: qe,
    S: di,
    u: mi,
    U: gi,
    V: yi,
    w: ki,
    W: pi,
    x: null,
    X: null,
    y: Ti,
    Y: bi,
    Z: wi,
    "%": ze
  }, $ = {
    a: D,
    A: _,
    b: k,
    B: L,
    c: f,
    d: He,
    e: He,
    f: Vr,
    g: Ne,
    G: Oe,
    H: Ve,
    I: Ve,
    j: Yr,
    L: Hr,
    m: Wr,
    M: Or,
    p: F,
    q: Lr,
    Q: Rr,
    s: zr,
    S: Nr,
    u: Fr,
    U: Ur,
    V: Er,
    w: Sr,
    W: Ir,
    x: d,
    X: y,
    y: Ne,
    Y: Oe,
    Z: Ar,
    "%": Pr
  };
  Z.x = x(n, Z), Z.X = x(r, Z), Z.c = x(e, Z), X.x = x(n, X), X.X = x(r, X), X.c = x(e, X);
  function x(g, E) {
    return function(W) {
      var u = [], K = -1, S = 0, q = g.length, P, ot, ut;
      for (W instanceof Date || (W = /* @__PURE__ */ new Date(+W)); ++K < q; )
        g.charCodeAt(K) === 37 && (u.push(g.slice(S, K)), (ot = Ye[P = g.charAt(++K)]) != null ? P = g.charAt(++K) : ot = P === "e" ? " " : "0", (ut = E[P]) && (P = ut(W, ot)), u.push(P), S = K + 1);
      return u.push(g.slice(S, K)), u.join("");
    };
  }
  function H(g, E) {
    return function(W) {
      var u = It(1900, void 0, 1), K = w(u, g, W += "", 0), S, q;
      if (K != W.length) return null;
      if ("Q" in u) return new Date(u.Q);
      if ("s" in u) return new Date(u.s * 1e3 + ("L" in u ? u.L : 0));
      if (E && !("Z" in u) && (u.Z = 0), "p" in u && (u.H = u.H % 12 + u.p * 12), u.m === void 0 && (u.m = "q" in u ? u.q : 0), "V" in u) {
        if (u.V < 1 || u.V > 53) return null;
        "w" in u || (u.w = 1), "Z" in u ? (S = de(It(u.y, 0, 1)), q = S.getUTCDay(), S = q > 4 || q === 0 ? Kt.ceil(S) : Kt(S), S = be.offset(S, (u.V - 1) * 7), u.y = S.getUTCFullYear(), u.m = S.getUTCMonth(), u.d = S.getUTCDate() + (u.w + 6) % 7) : (S = he(It(u.y, 0, 1)), q = S.getDay(), S = q > 4 || q === 0 ? Ot.ceil(S) : Ot(S), S = Tt.offset(S, (u.V - 1) * 7), u.y = S.getFullYear(), u.m = S.getMonth(), u.d = S.getDate() + (u.w + 6) % 7);
      } else ("W" in u || "U" in u) && ("w" in u || (u.w = "u" in u ? u.u % 7 : "W" in u ? 1 : 0), q = "Z" in u ? de(It(u.y, 0, 1)).getUTCDay() : he(It(u.y, 0, 1)).getDay(), u.m = 0, u.d = "W" in u ? (u.w + 6) % 7 + u.W * 7 - (q + 5) % 7 : u.w + u.U * 7 - (q + 6) % 7);
      return "Z" in u ? (u.H += u.Z / 100 | 0, u.M += u.Z % 100, de(u)) : he(u);
    };
  }
  function w(g, E, W, u) {
    for (var K = 0, S = E.length, q = W.length, P, ot; K < S; ) {
      if (u >= q) return -1;
      if (P = E.charCodeAt(K++), P === 37) {
        if (P = E.charAt(K++), ot = $[P in Ye ? E.charAt(K++) : P], !ot || (u = ot(g, W, u)) < 0) return -1;
      } else if (P != W.charCodeAt(u++))
        return -1;
    }
    return u;
  }
  function F(g, E, W) {
    var u = T.exec(E.slice(W));
    return u ? (g.p = v.get(u[0].toLowerCase()), W + u[0].length) : -1;
  }
  function D(g, E, W) {
    var u = p.exec(E.slice(W));
    return u ? (g.w = R.get(u[0].toLowerCase()), W + u[0].length) : -1;
  }
  function _(g, E, W) {
    var u = A.exec(E.slice(W));
    return u ? (g.w = b.get(u[0].toLowerCase()), W + u[0].length) : -1;
  }
  function k(g, E, W) {
    var u = rt.exec(E.slice(W));
    return u ? (g.m = nt.get(u[0].toLowerCase()), W + u[0].length) : -1;
  }
  function L(g, E, W) {
    var u = I.exec(E.slice(W));
    return u ? (g.m = et.get(u[0].toLowerCase()), W + u[0].length) : -1;
  }
  function f(g, E, W) {
    return w(g, e, E, W);
  }
  function d(g, E, W) {
    return w(g, n, E, W);
  }
  function y(g, E, W) {
    return w(g, r, E, W);
  }
  function m(g) {
    return s[g.getDay()];
  }
  function U(g) {
    return a[g.getDay()];
  }
  function c(g) {
    return M[g.getMonth()];
  }
  function l(g) {
    return C[g.getMonth()];
  }
  function o(g) {
    return i[+(g.getHours() >= 12)];
  }
  function V(g) {
    return 1 + ~~(g.getMonth() / 3);
  }
  function Y(g) {
    return s[g.getUTCDay()];
  }
  function O(g) {
    return a[g.getUTCDay()];
  }
  function Q(g) {
    return M[g.getUTCMonth()];
  }
  function z(g) {
    return C[g.getUTCMonth()];
  }
  function B(g) {
    return i[+(g.getUTCHours() >= 12)];
  }
  function st(g) {
    return 1 + ~~(g.getUTCMonth() / 3);
  }
  return {
    format: function(g) {
      var E = x(g += "", Z);
      return E.toString = function() {
        return g;
      }, E;
    },
    parse: function(g) {
      var E = H(g += "", !1);
      return E.toString = function() {
        return g;
      }, E;
    },
    utcFormat: function(g) {
      var E = x(g += "", X);
      return E.toString = function() {
        return g;
      }, E;
    },
    utcParse: function(g) {
      var E = H(g += "", !0);
      return E.toString = function() {
        return g;
      }, E;
    }
  };
}
var Ye = {
  "-": "",
  _: " ",
  0: "0"
}, J = /^\s*\d+/, Dr = /^%/, _r = /[\\^$*+?|[\]().{}]/g;
function N(t, e, n) {
  var r = t < 0 ? "-" : "", i = (r ? -t : t) + "", a = i.length;
  return r + (a < n ? new Array(n - a + 1).join(e) + i : i);
}
function Mr(t) {
  return t.replace(_r, "\\$&");
}
function At(t) {
  return new RegExp("^(?:" + t.map(Mr).join("|") + ")", "i");
}
function Lt(t) {
  return new Map(t.map((e, n) => [e.toLowerCase(), n]));
}
function Sr(t, e, n) {
  var r = J.exec(e.slice(n, n + 1));
  return r ? (t.w = +r[0], n + r[0].length) : -1;
}
function Fr(t, e, n) {
  var r = J.exec(e.slice(n, n + 1));
  return r ? (t.u = +r[0], n + r[0].length) : -1;
}
function Ur(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.U = +r[0], n + r[0].length) : -1;
}
function Er(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.V = +r[0], n + r[0].length) : -1;
}
function Ir(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.W = +r[0], n + r[0].length) : -1;
}
function Oe(t, e, n) {
  var r = J.exec(e.slice(n, n + 4));
  return r ? (t.y = +r[0], n + r[0].length) : -1;
}
function Ne(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.y = +r[0] + (+r[0] > 68 ? 1900 : 2e3), n + r[0].length) : -1;
}
function Ar(t, e, n) {
  var r = /^(Z)|([+-]\d\d)(?::?(\d\d))?/.exec(e.slice(n, n + 6));
  return r ? (t.Z = r[1] ? 0 : -(r[2] + (r[3] || "00")), n + r[0].length) : -1;
}
function Lr(t, e, n) {
  var r = J.exec(e.slice(n, n + 1));
  return r ? (t.q = r[0] * 3 - 3, n + r[0].length) : -1;
}
function Wr(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.m = r[0] - 1, n + r[0].length) : -1;
}
function He(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.d = +r[0], n + r[0].length) : -1;
}
function Yr(t, e, n) {
  var r = J.exec(e.slice(n, n + 3));
  return r ? (t.m = 0, t.d = +r[0], n + r[0].length) : -1;
}
function Ve(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.H = +r[0], n + r[0].length) : -1;
}
function Or(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.M = +r[0], n + r[0].length) : -1;
}
function Nr(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.S = +r[0], n + r[0].length) : -1;
}
function Hr(t, e, n) {
  var r = J.exec(e.slice(n, n + 3));
  return r ? (t.L = +r[0], n + r[0].length) : -1;
}
function Vr(t, e, n) {
  var r = J.exec(e.slice(n, n + 6));
  return r ? (t.L = Math.floor(r[0] / 1e3), n + r[0].length) : -1;
}
function Pr(t, e, n) {
  var r = Dr.exec(e.slice(n, n + 1));
  return r ? n + r[0].length : -1;
}
function Rr(t, e, n) {
  var r = J.exec(e.slice(n));
  return r ? (t.Q = +r[0], n + r[0].length) : -1;
}
function zr(t, e, n) {
  var r = J.exec(e.slice(n));
  return r ? (t.s = +r[0], n + r[0].length) : -1;
}
function Pe(t, e) {
  return N(t.getDate(), e, 2);
}
function Br(t, e) {
  return N(t.getHours(), e, 2);
}
function qr(t, e) {
  return N(t.getHours() % 12 || 12, e, 2);
}
function Zr(t, e) {
  return N(1 + Tt.count(kt(t), t), e, 3);
}
function dn(t, e) {
  return N(t.getMilliseconds(), e, 3);
}
function Xr(t, e) {
  return dn(t, e) + "000";
}
function jr(t, e) {
  return N(t.getMonth() + 1, e, 2);
}
function Gr(t, e) {
  return N(t.getMinutes(), e, 2);
}
function Qr(t, e) {
  return N(t.getSeconds(), e, 2);
}
function Jr(t) {
  var e = t.getDay();
  return e === 0 ? 7 : e;
}
function Kr(t, e) {
  return N(Ht.count(kt(t) - 1, t), e, 2);
}
function mn(t) {
  var e = t.getDay();
  return e >= 4 || e === 0 ? vt(t) : vt.ceil(t);
}
function $r(t, e) {
  return t = mn(t), N(vt.count(kt(t), t) + (kt(t).getDay() === 4), e, 2);
}
function ti(t) {
  return t.getDay();
}
function ei(t, e) {
  return N(Ot.count(kt(t) - 1, t), e, 2);
}
function ni(t, e) {
  return N(t.getFullYear() % 100, e, 2);
}
function ri(t, e) {
  return t = mn(t), N(t.getFullYear() % 100, e, 2);
}
function ii(t, e) {
  return N(t.getFullYear() % 1e4, e, 4);
}
function ai(t, e) {
  var n = t.getDay();
  return t = n >= 4 || n === 0 ? vt(t) : vt.ceil(t), N(t.getFullYear() % 1e4, e, 4);
}
function si(t) {
  var e = t.getTimezoneOffset();
  return (e > 0 ? "-" : (e *= -1, "+")) + N(e / 60 | 0, "0", 2) + N(e % 60, "0", 2);
}
function Re(t, e) {
  return N(t.getUTCDate(), e, 2);
}
function oi(t, e) {
  return N(t.getUTCHours(), e, 2);
}
function ci(t, e) {
  return N(t.getUTCHours() % 12 || 12, e, 2);
}
function li(t, e) {
  return N(1 + be.count(bt(t), t), e, 3);
}
function gn(t, e) {
  return N(t.getUTCMilliseconds(), e, 3);
}
function ui(t, e) {
  return gn(t, e) + "000";
}
function fi(t, e) {
  return N(t.getUTCMonth() + 1, e, 2);
}
function hi(t, e) {
  return N(t.getUTCMinutes(), e, 2);
}
function di(t, e) {
  return N(t.getUTCSeconds(), e, 2);
}
function mi(t) {
  var e = t.getUTCDay();
  return e === 0 ? 7 : e;
}
function gi(t, e) {
  return N(hn.count(bt(t) - 1, t), e, 2);
}
function yn(t) {
  var e = t.getUTCDay();
  return e >= 4 || e === 0 ? Ut(t) : Ut.ceil(t);
}
function yi(t, e) {
  return t = yn(t), N(Ut.count(bt(t), t) + (bt(t).getUTCDay() === 4), e, 2);
}
function ki(t) {
  return t.getUTCDay();
}
function pi(t, e) {
  return N(Kt.count(bt(t) - 1, t), e, 2);
}
function Ti(t, e) {
  return N(t.getUTCFullYear() % 100, e, 2);
}
function vi(t, e) {
  return t = yn(t), N(t.getUTCFullYear() % 100, e, 2);
}
function bi(t, e) {
  return N(t.getUTCFullYear() % 1e4, e, 4);
}
function xi(t, e) {
  var n = t.getUTCDay();
  return t = n >= 4 || n === 0 ? Ut(t) : Ut.ceil(t), N(t.getUTCFullYear() % 1e4, e, 4);
}
function wi() {
  return "+0000";
}
function ze() {
  return "%";
}
function Be(t) {
  return +t;
}
function qe(t) {
  return Math.floor(+t / 1e3);
}
var Dt, $t;
Ci({
  dateTime: "%x, %X",
  date: "%-m/%-d/%Y",
  time: "%-I:%M:%S %p",
  periods: ["AM", "PM"],
  days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
  shortDays: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
  months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
  shortMonths: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
});
function Ci(t) {
  return Dt = Cr(t), $t = Dt.format, Dt.parse, Dt.utcFormat, Dt.utcParse, Dt;
}
function Di(t) {
  return new Date(t);
}
function _i(t) {
  return t instanceof Date ? +t : +/* @__PURE__ */ new Date(+t);
}
function kn(t, e, n, r, i, a, s, C, M, T) {
  var v = qn(), A = v.invert, b = v.domain, p = T(".%L"), R = T(":%S"), I = T("%I:%M"), et = T("%I %p"), rt = T("%a %d"), nt = T("%b %d"), Z = T("%B"), X = T("%Y");
  function $(x) {
    return (M(x) < x ? p : C(x) < x ? R : s(x) < x ? I : a(x) < x ? et : r(x) < x ? i(x) < x ? rt : nt : n(x) < x ? Z : X)(x);
  }
  return v.invert = function(x) {
    return new Date(A(x));
  }, v.domain = function(x) {
    return arguments.length ? b(Array.from(x, _i)) : b().map(Di);
  }, v.ticks = function(x) {
    var H = b();
    return t(H[0], H[H.length - 1], x ?? 10);
  }, v.tickFormat = function(x, H) {
    return H == null ? $ : T(H);
  }, v.nice = function(x) {
    var H = b();
    return (!x || typeof x.range != "function") && (x = e(H[0], H[H.length - 1], x ?? 10)), x ? b(hr(H, x)) : v;
  }, v.copy = function() {
    return Zn(v, kn(t, e, n, r, i, a, s, C, M, T));
  }, v;
}
function Mi() {
  return jn.apply(kn(xr, wr, kt, Nt, Ht, Tt, Yt, Wt, pt, $t).domain([new Date(2e3, 0, 1), new Date(2e3, 0, 2)]), arguments);
}
var pn = {
  exports: {}
};
(function(t, e) {
  (function(n, r) {
    t.exports = r();
  })(Vn, function() {
    var n = "day";
    return function(r, i, a) {
      var s = function(T) {
        return T.add(4 - T.isoWeekday(), n);
      }, C = i.prototype;
      C.isoWeekYear = function() {
        return s(this).year();
      }, C.isoWeek = function(T) {
        if (!this.$utils().u(T)) return this.add(7 * (T - this.isoWeek()), n);
        var v, A, b, p, R = s(this), I = (v = this.isoWeekYear(), A = this.$u, b = (A ? a.utc : a)().year(v).startOf("year"), p = 4 - b.isoWeekday(), b.isoWeekday() > 4 && (p += 7), b.add(p, n));
        return R.diff(I, "week") + 1;
      }, C.isoWeekday = function(T) {
        return this.$utils().u(T) ? this.day() || 7 : this.day(this.day() % 7 ? T : T - 7);
      };
      var M = C.startOf;
      C.startOf = function(T, v) {
        var A = this.$utils(), b = !!A.u(v) || v;
        return A.p(T) === "isoweek" ? b ? this.date(this.date() - (this.isoWeekday() - 1)).startOf("day") : this.date(this.date() - 1 - (this.isoWeekday() - 1) + 7).endOf("day") : M.bind(this)(T, v);
      };
    };
  });
})(pn);
var Si = pn.exports;
const Fi = /* @__PURE__ */ Pn(Si);
var ye = function() {
  var t = /* @__PURE__ */ h(function(L, f, d, y) {
    for (d = d || {}, y = L.length; y--; d[L[y]] = f) ;
    return d;
  }, "o"), e = [6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 35, 36, 38, 40], n = [1, 26], r = [1, 27], i = [1, 28], a = [1, 29], s = [1, 30], C = [1, 31], M = [1, 32], T = [1, 33], v = [1, 34], A = [1, 9], b = [1, 10], p = [1, 11], R = [1, 12], I = [1, 13], et = [1, 14], rt = [1, 15], nt = [1, 16], Z = [1, 19], X = [1, 20], $ = [1, 21], x = [1, 22], H = [1, 23], w = [1, 25], F = [1, 35], D = {
    trace: /* @__PURE__ */ h(function() {
    }, "trace"),
    yy: {},
    symbols_: {
      error: 2,
      start: 3,
      gantt: 4,
      document: 5,
      EOF: 6,
      line: 7,
      SPACE: 8,
      statement: 9,
      NL: 10,
      weekday: 11,
      weekday_monday: 12,
      weekday_tuesday: 13,
      weekday_wednesday: 14,
      weekday_thursday: 15,
      weekday_friday: 16,
      weekday_saturday: 17,
      weekday_sunday: 18,
      weekend: 19,
      weekend_friday: 20,
      weekend_saturday: 21,
      dateFormat: 22,
      inclusiveEndDates: 23,
      topAxis: 24,
      axisFormat: 25,
      tickInterval: 26,
      excludes: 27,
      includes: 28,
      todayMarker: 29,
      title: 30,
      acc_title: 31,
      acc_title_value: 32,
      acc_descr: 33,
      acc_descr_value: 34,
      acc_descr_multiline_value: 35,
      section: 36,
      clickStatement: 37,
      taskTxt: 38,
      taskData: 39,
      click: 40,
      callbackname: 41,
      callbackargs: 42,
      href: 43,
      clickStatementDebug: 44,
      $accept: 0,
      $end: 1
    },
    terminals_: {
      2: "error",
      4: "gantt",
      6: "EOF",
      8: "SPACE",
      10: "NL",
      12: "weekday_monday",
      13: "weekday_tuesday",
      14: "weekday_wednesday",
      15: "weekday_thursday",
      16: "weekday_friday",
      17: "weekday_saturday",
      18: "weekday_sunday",
      20: "weekend_friday",
      21: "weekend_saturday",
      22: "dateFormat",
      23: "inclusiveEndDates",
      24: "topAxis",
      25: "axisFormat",
      26: "tickInterval",
      27: "excludes",
      28: "includes",
      29: "todayMarker",
      30: "title",
      31: "acc_title",
      32: "acc_title_value",
      33: "acc_descr",
      34: "acc_descr_value",
      35: "acc_descr_multiline_value",
      36: "section",
      38: "taskTxt",
      39: "taskData",
      40: "click",
      41: "callbackname",
      42: "callbackargs",
      43: "href"
    },
    productions_: [0, [3, 3], [5, 0], [5, 2], [7, 2], [7, 1], [7, 1], [7, 1], [11, 1], [11, 1], [11, 1], [11, 1], [11, 1], [11, 1], [11, 1], [19, 1], [19, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 2], [9, 2], [9, 1], [9, 1], [9, 1], [9, 2], [37, 2], [37, 3], [37, 3], [37, 4], [37, 3], [37, 4], [37, 2], [44, 2], [44, 3], [44, 3], [44, 4], [44, 3], [44, 4], [44, 2]],
    performAction: /* @__PURE__ */ h(function(f, d, y, m, U, c, l) {
      var o = c.length - 1;
      switch (U) {
        case 1:
          return c[o - 1];
        case 2:
          this.$ = [];
          break;
        case 3:
          c[o - 1].push(c[o]), this.$ = c[o - 1];
          break;
        case 4:
        case 5:
          this.$ = c[o];
          break;
        case 6:
        case 7:
          this.$ = [];
          break;
        case 8:
          m.setWeekday("monday");
          break;
        case 9:
          m.setWeekday("tuesday");
          break;
        case 10:
          m.setWeekday("wednesday");
          break;
        case 11:
          m.setWeekday("thursday");
          break;
        case 12:
          m.setWeekday("friday");
          break;
        case 13:
          m.setWeekday("saturday");
          break;
        case 14:
          m.setWeekday("sunday");
          break;
        case 15:
          m.setWeekend("friday");
          break;
        case 16:
          m.setWeekend("saturday");
          break;
        case 17:
          m.setDateFormat(c[o].substr(11)), this.$ = c[o].substr(11);
          break;
        case 18:
          m.enableInclusiveEndDates(), this.$ = c[o].substr(18);
          break;
        case 19:
          m.TopAxis(), this.$ = c[o].substr(8);
          break;
        case 20:
          m.setAxisFormat(c[o].substr(11)), this.$ = c[o].substr(11);
          break;
        case 21:
          m.setTickInterval(c[o].substr(13)), this.$ = c[o].substr(13);
          break;
        case 22:
          m.setExcludes(c[o].substr(9)), this.$ = c[o].substr(9);
          break;
        case 23:
          m.setIncludes(c[o].substr(9)), this.$ = c[o].substr(9);
          break;
        case 24:
          m.setTodayMarker(c[o].substr(12)), this.$ = c[o].substr(12);
          break;
        case 27:
          m.setDiagramTitle(c[o].substr(6)), this.$ = c[o].substr(6);
          break;
        case 28:
          this.$ = c[o].trim(), m.setAccTitle(this.$);
          break;
        case 29:
        case 30:
          this.$ = c[o].trim(), m.setAccDescription(this.$);
          break;
        case 31:
          m.addSection(c[o].substr(8)), this.$ = c[o].substr(8);
          break;
        case 33:
          m.addTask(c[o - 1], c[o]), this.$ = "task";
          break;
        case 34:
          this.$ = c[o - 1], m.setClickEvent(c[o - 1], c[o], null);
          break;
        case 35:
          this.$ = c[o - 2], m.setClickEvent(c[o - 2], c[o - 1], c[o]);
          break;
        case 36:
          this.$ = c[o - 2], m.setClickEvent(c[o - 2], c[o - 1], null), m.setLink(c[o - 2], c[o]);
          break;
        case 37:
          this.$ = c[o - 3], m.setClickEvent(c[o - 3], c[o - 2], c[o - 1]), m.setLink(c[o - 3], c[o]);
          break;
        case 38:
          this.$ = c[o - 2], m.setClickEvent(c[o - 2], c[o], null), m.setLink(c[o - 2], c[o - 1]);
          break;
        case 39:
          this.$ = c[o - 3], m.setClickEvent(c[o - 3], c[o - 1], c[o]), m.setLink(c[o - 3], c[o - 2]);
          break;
        case 40:
          this.$ = c[o - 1], m.setLink(c[o - 1], c[o]);
          break;
        case 41:
        case 47:
          this.$ = c[o - 1] + " " + c[o];
          break;
        case 42:
        case 43:
        case 45:
          this.$ = c[o - 2] + " " + c[o - 1] + " " + c[o];
          break;
        case 44:
        case 46:
          this.$ = c[o - 3] + " " + c[o - 2] + " " + c[o - 1] + " " + c[o];
          break;
      }
    }, "anonymous"),
    table: [{
      3: 1,
      4: [1, 2]
    }, {
      1: [3]
    }, t(e, [2, 2], {
      5: 3
    }), {
      6: [1, 4],
      7: 5,
      8: [1, 6],
      9: 7,
      10: [1, 8],
      11: 17,
      12: n,
      13: r,
      14: i,
      15: a,
      16: s,
      17: C,
      18: M,
      19: 18,
      20: T,
      21: v,
      22: A,
      23: b,
      24: p,
      25: R,
      26: I,
      27: et,
      28: rt,
      29: nt,
      30: Z,
      31: X,
      33: $,
      35: x,
      36: H,
      37: 24,
      38: w,
      40: F
    }, t(e, [2, 7], {
      1: [2, 1]
    }), t(e, [2, 3]), {
      9: 36,
      11: 17,
      12: n,
      13: r,
      14: i,
      15: a,
      16: s,
      17: C,
      18: M,
      19: 18,
      20: T,
      21: v,
      22: A,
      23: b,
      24: p,
      25: R,
      26: I,
      27: et,
      28: rt,
      29: nt,
      30: Z,
      31: X,
      33: $,
      35: x,
      36: H,
      37: 24,
      38: w,
      40: F
    }, t(e, [2, 5]), t(e, [2, 6]), t(e, [2, 17]), t(e, [2, 18]), t(e, [2, 19]), t(e, [2, 20]), t(e, [2, 21]), t(e, [2, 22]), t(e, [2, 23]), t(e, [2, 24]), t(e, [2, 25]), t(e, [2, 26]), t(e, [2, 27]), {
      32: [1, 37]
    }, {
      34: [1, 38]
    }, t(e, [2, 30]), t(e, [2, 31]), t(e, [2, 32]), {
      39: [1, 39]
    }, t(e, [2, 8]), t(e, [2, 9]), t(e, [2, 10]), t(e, [2, 11]), t(e, [2, 12]), t(e, [2, 13]), t(e, [2, 14]), t(e, [2, 15]), t(e, [2, 16]), {
      41: [1, 40],
      43: [1, 41]
    }, t(e, [2, 4]), t(e, [2, 28]), t(e, [2, 29]), t(e, [2, 33]), t(e, [2, 34], {
      42: [1, 42],
      43: [1, 43]
    }), t(e, [2, 40], {
      41: [1, 44]
    }), t(e, [2, 35], {
      43: [1, 45]
    }), t(e, [2, 36]), t(e, [2, 38], {
      42: [1, 46]
    }), t(e, [2, 37]), t(e, [2, 39])],
    defaultActions: {},
    parseError: /* @__PURE__ */ h(function(f, d) {
      if (d.recoverable)
        this.trace(f);
      else {
        var y = new Error(f);
        throw y.hash = d, y;
      }
    }, "parseError"),
    parse: /* @__PURE__ */ h(function(f) {
      var d = this, y = [0], m = [], U = [null], c = [], l = this.table, o = "", V = 0, Y = 0, O = 2, Q = 1, z = c.slice.call(arguments, 1), B = Object.create(this.lexer), st = {
        yy: {}
      };
      for (var g in this.yy)
        Object.prototype.hasOwnProperty.call(this.yy, g) && (st.yy[g] = this.yy[g]);
      B.setInput(f, st.yy), st.yy.lexer = B, st.yy.parser = this, typeof B.yylloc > "u" && (B.yylloc = {});
      var E = B.yylloc;
      c.push(E);
      var W = B.options && B.options.ranges;
      typeof st.yy.parseError == "function" ? this.parseError = st.yy.parseError : this.parseError = Object.getPrototypeOf(this).parseError;
      function u(it) {
        y.length = y.length - 2 * it, U.length = U.length - it, c.length = c.length - it;
      }
      h(u, "popStack");
      function K() {
        var it;
        return it = m.pop() || B.lex() || Q, typeof it != "number" && (it instanceof Array && (m = it, it = m.pop()), it = d.symbols_[it] || it), it;
      }
      h(K, "lex");
      for (var S, q, P, ot, ut = {}, zt, ft, Ie, Bt; ; ) {
        if (q = y[y.length - 1], this.defaultActions[q] ? P = this.defaultActions[q] : ((S === null || typeof S > "u") && (S = K()), P = l[q] && l[q][S]), typeof P > "u" || !P.length || !P[0]) {
          var ne = "";
          Bt = [];
          for (zt in l[q])
            this.terminals_[zt] && zt > O && Bt.push("'" + this.terminals_[zt] + "'");
          B.showPosition ? ne = "Parse error on line " + (V + 1) + `:
` + B.showPosition() + `
Expecting ` + Bt.join(", ") + ", got '" + (this.terminals_[S] || S) + "'" : ne = "Parse error on line " + (V + 1) + ": Unexpected " + (S == Q ? "end of input" : "'" + (this.terminals_[S] || S) + "'"), this.parseError(ne, {
            text: B.match,
            token: this.terminals_[S] || S,
            line: B.yylineno,
            loc: E,
            expected: Bt
          });
        }
        if (P[0] instanceof Array && P.length > 1)
          throw new Error("Parse Error: multiple actions possible at state: " + q + ", token: " + S);
        switch (P[0]) {
          case 1:
            y.push(S), U.push(B.yytext), c.push(B.yylloc), y.push(P[1]), S = null, Y = B.yyleng, o = B.yytext, V = B.yylineno, E = B.yylloc;
            break;
          case 2:
            if (ft = this.productions_[P[1]][1], ut.$ = U[U.length - ft], ut._$ = {
              first_line: c[c.length - (ft || 1)].first_line,
              last_line: c[c.length - 1].last_line,
              first_column: c[c.length - (ft || 1)].first_column,
              last_column: c[c.length - 1].last_column
            }, W && (ut._$.range = [c[c.length - (ft || 1)].range[0], c[c.length - 1].range[1]]), ot = this.performAction.apply(ut, [o, Y, V, st.yy, P[1], U, c].concat(z)), typeof ot < "u")
              return ot;
            ft && (y = y.slice(0, -1 * ft * 2), U = U.slice(0, -1 * ft), c = c.slice(0, -1 * ft)), y.push(this.productions_[P[1]][0]), U.push(ut.$), c.push(ut._$), Ie = l[y[y.length - 2]][y[y.length - 1]], y.push(Ie);
            break;
          case 3:
            return !0;
        }
      }
      return !0;
    }, "parse")
  }, _ = /* @__PURE__ */ function() {
    var L = {
      EOF: 1,
      parseError: /* @__PURE__ */ h(function(d, y) {
        if (this.yy.parser)
          this.yy.parser.parseError(d, y);
        else
          throw new Error(d);
      }, "parseError"),
      // resets the lexer, sets new input
      setInput: /* @__PURE__ */ h(function(f, d) {
        return this.yy = d || this.yy || {}, this._input = f, this._more = this._backtrack = this.done = !1, this.yylineno = this.yyleng = 0, this.yytext = this.matched = this.match = "", this.conditionStack = ["INITIAL"], this.yylloc = {
          first_line: 1,
          first_column: 0,
          last_line: 1,
          last_column: 0
        }, this.options.ranges && (this.yylloc.range = [0, 0]), this.offset = 0, this;
      }, "setInput"),
      // consumes and returns one char from the input
      input: /* @__PURE__ */ h(function() {
        var f = this._input[0];
        this.yytext += f, this.yyleng++, this.offset++, this.match += f, this.matched += f;
        var d = f.match(/(?:\r\n?|\n).*/g);
        return d ? (this.yylineno++, this.yylloc.last_line++) : this.yylloc.last_column++, this.options.ranges && this.yylloc.range[1]++, this._input = this._input.slice(1), f;
      }, "input"),
      // unshifts one char (or a string) into the input
      unput: /* @__PURE__ */ h(function(f) {
        var d = f.length, y = f.split(/(?:\r\n?|\n)/g);
        this._input = f + this._input, this.yytext = this.yytext.substr(0, this.yytext.length - d), this.offset -= d;
        var m = this.match.split(/(?:\r\n?|\n)/g);
        this.match = this.match.substr(0, this.match.length - 1), this.matched = this.matched.substr(0, this.matched.length - 1), y.length - 1 && (this.yylineno -= y.length - 1);
        var U = this.yylloc.range;
        return this.yylloc = {
          first_line: this.yylloc.first_line,
          last_line: this.yylineno + 1,
          first_column: this.yylloc.first_column,
          last_column: y ? (y.length === m.length ? this.yylloc.first_column : 0) + m[m.length - y.length].length - y[0].length : this.yylloc.first_column - d
        }, this.options.ranges && (this.yylloc.range = [U[0], U[0] + this.yyleng - d]), this.yyleng = this.yytext.length, this;
      }, "unput"),
      // When called from action, caches matched text and appends it on next action
      more: /* @__PURE__ */ h(function() {
        return this._more = !0, this;
      }, "more"),
      // When called from action, signals the lexer that this rule fails to match the input, so the next matching rule (regex) should be tested instead.
      reject: /* @__PURE__ */ h(function() {
        if (this.options.backtrack_lexer)
          this._backtrack = !0;
        else
          return this.parseError("Lexical error on line " + (this.yylineno + 1) + `. You can only invoke reject() in the lexer when the lexer is of the backtracking persuasion (options.backtrack_lexer = true).
` + this.showPosition(), {
            text: "",
            token: null,
            line: this.yylineno
          });
        return this;
      }, "reject"),
      // retain first n characters of the match
      less: /* @__PURE__ */ h(function(f) {
        this.unput(this.match.slice(f));
      }, "less"),
      // displays already matched input, i.e. for error messages
      pastInput: /* @__PURE__ */ h(function() {
        var f = this.matched.substr(0, this.matched.length - this.match.length);
        return (f.length > 20 ? "..." : "") + f.substr(-20).replace(/\n/g, "");
      }, "pastInput"),
      // displays upcoming input, i.e. for error messages
      upcomingInput: /* @__PURE__ */ h(function() {
        var f = this.match;
        return f.length < 20 && (f += this._input.substr(0, 20 - f.length)), (f.substr(0, 20) + (f.length > 20 ? "..." : "")).replace(/\n/g, "");
      }, "upcomingInput"),
      // displays the character position where the lexing error occurred, i.e. for error messages
      showPosition: /* @__PURE__ */ h(function() {
        var f = this.pastInput(), d = new Array(f.length + 1).join("-");
        return f + this.upcomingInput() + `
` + d + "^";
      }, "showPosition"),
      // test the lexed token: return FALSE when not a match, otherwise return token
      test_match: /* @__PURE__ */ h(function(f, d) {
        var y, m, U;
        if (this.options.backtrack_lexer && (U = {
          yylineno: this.yylineno,
          yylloc: {
            first_line: this.yylloc.first_line,
            last_line: this.last_line,
            first_column: this.yylloc.first_column,
            last_column: this.yylloc.last_column
          },
          yytext: this.yytext,
          match: this.match,
          matches: this.matches,
          matched: this.matched,
          yyleng: this.yyleng,
          offset: this.offset,
          _more: this._more,
          _input: this._input,
          yy: this.yy,
          conditionStack: this.conditionStack.slice(0),
          done: this.done
        }, this.options.ranges && (U.yylloc.range = this.yylloc.range.slice(0))), m = f[0].match(/(?:\r\n?|\n).*/g), m && (this.yylineno += m.length), this.yylloc = {
          first_line: this.yylloc.last_line,
          last_line: this.yylineno + 1,
          first_column: this.yylloc.last_column,
          last_column: m ? m[m.length - 1].length - m[m.length - 1].match(/\r?\n?/)[0].length : this.yylloc.last_column + f[0].length
        }, this.yytext += f[0], this.match += f[0], this.matches = f, this.yyleng = this.yytext.length, this.options.ranges && (this.yylloc.range = [this.offset, this.offset += this.yyleng]), this._more = !1, this._backtrack = !1, this._input = this._input.slice(f[0].length), this.matched += f[0], y = this.performAction.call(this, this.yy, this, d, this.conditionStack[this.conditionStack.length - 1]), this.done && this._input && (this.done = !1), y)
          return y;
        if (this._backtrack) {
          for (var c in U)
            this[c] = U[c];
          return !1;
        }
        return !1;
      }, "test_match"),
      // return next match in input
      next: /* @__PURE__ */ h(function() {
        if (this.done)
          return this.EOF;
        this._input || (this.done = !0);
        var f, d, y, m;
        this._more || (this.yytext = "", this.match = "");
        for (var U = this._currentRules(), c = 0; c < U.length; c++)
          if (y = this._input.match(this.rules[U[c]]), y && (!d || y[0].length > d[0].length)) {
            if (d = y, m = c, this.options.backtrack_lexer) {
              if (f = this.test_match(y, U[c]), f !== !1)
                return f;
              if (this._backtrack) {
                d = !1;
                continue;
              } else
                return !1;
            } else if (!this.options.flex)
              break;
          }
        return d ? (f = this.test_match(d, U[m]), f !== !1 ? f : !1) : this._input === "" ? this.EOF : this.parseError("Lexical error on line " + (this.yylineno + 1) + `. Unrecognized text.
` + this.showPosition(), {
          text: "",
          token: null,
          line: this.yylineno
        });
      }, "next"),
      // return next match that has a token
      lex: /* @__PURE__ */ h(function() {
        var d = this.next();
        return d || this.lex();
      }, "lex"),
      // activates a new lexer condition state (pushes the new lexer condition state onto the condition stack)
      begin: /* @__PURE__ */ h(function(d) {
        this.conditionStack.push(d);
      }, "begin"),
      // pop the previously active lexer condition state off the condition stack
      popState: /* @__PURE__ */ h(function() {
        var d = this.conditionStack.length - 1;
        return d > 0 ? this.conditionStack.pop() : this.conditionStack[0];
      }, "popState"),
      // produce the lexer rule set which is active for the currently active lexer condition state
      _currentRules: /* @__PURE__ */ h(function() {
        return this.conditionStack.length && this.conditionStack[this.conditionStack.length - 1] ? this.conditions[this.conditionStack[this.conditionStack.length - 1]].rules : this.conditions.INITIAL.rules;
      }, "_currentRules"),
      // return the currently active lexer condition state; when an index argument is provided it produces the N-th previous condition state, if available
      topState: /* @__PURE__ */ h(function(d) {
        return d = this.conditionStack.length - 1 - Math.abs(d || 0), d >= 0 ? this.conditionStack[d] : "INITIAL";
      }, "topState"),
      // alias for begin(condition)
      pushState: /* @__PURE__ */ h(function(d) {
        this.begin(d);
      }, "pushState"),
      // return the number of states currently on the stack
      stateStackSize: /* @__PURE__ */ h(function() {
        return this.conditionStack.length;
      }, "stateStackSize"),
      options: {
        "case-insensitive": !0
      },
      performAction: /* @__PURE__ */ h(function(d, y, m, U) {
        switch (m) {
          case 0:
            return this.begin("open_directive"), "open_directive";
          case 1:
            return this.begin("acc_title"), 31;
          case 2:
            return this.popState(), "acc_title_value";
          case 3:
            return this.begin("acc_descr"), 33;
          case 4:
            return this.popState(), "acc_descr_value";
          case 5:
            this.begin("acc_descr_multiline");
            break;
          case 6:
            this.popState();
            break;
          case 7:
            return "acc_descr_multiline_value";
          case 8:
            break;
          case 9:
            break;
          case 10:
            break;
          case 11:
            return 10;
          case 12:
            break;
          case 13:
            break;
          case 14:
            this.begin("href");
            break;
          case 15:
            this.popState();
            break;
          case 16:
            return 43;
          case 17:
            this.begin("callbackname");
            break;
          case 18:
            this.popState();
            break;
          case 19:
            this.popState(), this.begin("callbackargs");
            break;
          case 20:
            return 41;
          case 21:
            this.popState();
            break;
          case 22:
            return 42;
          case 23:
            this.begin("click");
            break;
          case 24:
            this.popState();
            break;
          case 25:
            return 40;
          case 26:
            return 4;
          case 27:
            return 22;
          case 28:
            return 23;
          case 29:
            return 24;
          case 30:
            return 25;
          case 31:
            return 26;
          case 32:
            return 28;
          case 33:
            return 27;
          case 34:
            return 29;
          case 35:
            return 12;
          case 36:
            return 13;
          case 37:
            return 14;
          case 38:
            return 15;
          case 39:
            return 16;
          case 40:
            return 17;
          case 41:
            return 18;
          case 42:
            return 20;
          case 43:
            return 21;
          case 44:
            return "date";
          case 45:
            return 30;
          case 46:
            return "accDescription";
          case 47:
            return 36;
          case 48:
            return 38;
          case 49:
            return 39;
          case 50:
            return ":";
          case 51:
            return 6;
          case 52:
            return "INVALID";
        }
      }, "anonymous"),
      rules: [/^(?:%%\{)/i, /^(?:accTitle\s*:\s*)/i, /^(?:(?!\n||)*[^\n]*)/i, /^(?:accDescr\s*:\s*)/i, /^(?:(?!\n||)*[^\n]*)/i, /^(?:accDescr\s*\{\s*)/i, /^(?:[\}])/i, /^(?:[^\}]*)/i, /^(?:%%(?!\{)*[^\n]*)/i, /^(?:[^\}]%%*[^\n]*)/i, /^(?:%%*[^\n]*[\n]*)/i, /^(?:[\n]+)/i, /^(?:\s+)/i, /^(?:%[^\n]*)/i, /^(?:href[\s]+["])/i, /^(?:["])/i, /^(?:[^"]*)/i, /^(?:call[\s]+)/i, /^(?:\([\s]*\))/i, /^(?:\()/i, /^(?:[^(]*)/i, /^(?:\))/i, /^(?:[^)]*)/i, /^(?:click[\s]+)/i, /^(?:[\s\n])/i, /^(?:[^\s\n]*)/i, /^(?:gantt\b)/i, /^(?:dateFormat\s[^#\n;]+)/i, /^(?:inclusiveEndDates\b)/i, /^(?:topAxis\b)/i, /^(?:axisFormat\s[^#\n;]+)/i, /^(?:tickInterval\s[^#\n;]+)/i, /^(?:includes\s[^#\n;]+)/i, /^(?:excludes\s[^#\n;]+)/i, /^(?:todayMarker\s[^\n;]+)/i, /^(?:weekday\s+monday\b)/i, /^(?:weekday\s+tuesday\b)/i, /^(?:weekday\s+wednesday\b)/i, /^(?:weekday\s+thursday\b)/i, /^(?:weekday\s+friday\b)/i, /^(?:weekday\s+saturday\b)/i, /^(?:weekday\s+sunday\b)/i, /^(?:weekend\s+friday\b)/i, /^(?:weekend\s+saturday\b)/i, /^(?:\d\d\d\d-\d\d-\d\d\b)/i, /^(?:title\s[^\n]+)/i, /^(?:accDescription\s[^#\n;]+)/i, /^(?:section\s[^\n]+)/i, /^(?:[^:\n]+)/i, /^(?::[^#\n;]+)/i, /^(?::)/i, /^(?:$)/i, /^(?:.)/i],
      conditions: {
        acc_descr_multiline: {
          rules: [6, 7],
          inclusive: !1
        },
        acc_descr: {
          rules: [4],
          inclusive: !1
        },
        acc_title: {
          rules: [2],
          inclusive: !1
        },
        callbackargs: {
          rules: [21, 22],
          inclusive: !1
        },
        callbackname: {
          rules: [18, 19, 20],
          inclusive: !1
        },
        href: {
          rules: [15, 16],
          inclusive: !1
        },
        click: {
          rules: [24, 25],
          inclusive: !1
        },
        INITIAL: {
          rules: [0, 1, 3, 5, 8, 9, 10, 11, 12, 13, 14, 17, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52],
          inclusive: !0
        }
      }
    };
    return L;
  }();
  D.lexer = _;
  function k() {
    this.yy = {};
  }
  return h(k, "Parser"), k.prototype = D, D.Parser = k, new k();
}();
ye.parser = ye;
var Ui = ye;
tt.extend(Fi);
tt.extend(Rn);
tt.extend(zn);
var Ze = {
  friday: 5,
  saturday: 6
}, ct = "", xe = "", we = void 0, Ce = "", Vt = [], Pt = [], De = /* @__PURE__ */ new Map(), _e = [], te = [], Et = "", Me = "", Tn = ["active", "done", "crit", "milestone", "vert"], Se = [], Rt = !1, Fe = !1, Ue = "sunday", ee = "saturday", ke = 0, Ei = /* @__PURE__ */ h(function() {
  _e = [], te = [], Et = "", Se = [], jt = 0, Te = void 0, Gt = void 0, j = [], ct = "", xe = "", Me = "", we = void 0, Ce = "", Vt = [], Pt = [], Rt = !1, Fe = !1, ke = 0, De = /* @__PURE__ */ new Map(), Nn(), Ue = "sunday", ee = "saturday";
}, "clear"), Ii = /* @__PURE__ */ h(function(t) {
  xe = t;
}, "setAxisFormat"), Ai = /* @__PURE__ */ h(function() {
  return xe;
}, "getAxisFormat"), Li = /* @__PURE__ */ h(function(t) {
  we = t;
}, "setTickInterval"), Wi = /* @__PURE__ */ h(function() {
  return we;
}, "getTickInterval"), Yi = /* @__PURE__ */ h(function(t) {
  Ce = t;
}, "setTodayMarker"), Oi = /* @__PURE__ */ h(function() {
  return Ce;
}, "getTodayMarker"), Ni = /* @__PURE__ */ h(function(t) {
  ct = t;
}, "setDateFormat"), Hi = /* @__PURE__ */ h(function() {
  Rt = !0;
}, "enableInclusiveEndDates"), Vi = /* @__PURE__ */ h(function() {
  return Rt;
}, "endDatesAreInclusive"), Pi = /* @__PURE__ */ h(function() {
  Fe = !0;
}, "enableTopAxis"), Ri = /* @__PURE__ */ h(function() {
  return Fe;
}, "topAxisEnabled"), zi = /* @__PURE__ */ h(function(t) {
  Me = t;
}, "setDisplayMode"), Bi = /* @__PURE__ */ h(function() {
  return Me;
}, "getDisplayMode"), qi = /* @__PURE__ */ h(function() {
  return ct;
}, "getDateFormat"), Zi = /* @__PURE__ */ h(function(t) {
  Vt = t.toLowerCase().split(/[\s,]+/);
}, "setIncludes"), Xi = /* @__PURE__ */ h(function() {
  return Vt;
}, "getIncludes"), ji = /* @__PURE__ */ h(function(t) {
  Pt = t.toLowerCase().split(/[\s,]+/);
}, "setExcludes"), Gi = /* @__PURE__ */ h(function() {
  return Pt;
}, "getExcludes"), Qi = /* @__PURE__ */ h(function() {
  return De;
}, "getLinks"), Ji = /* @__PURE__ */ h(function(t) {
  Et = t, _e.push(t);
}, "addSection"), Ki = /* @__PURE__ */ h(function() {
  return _e;
}, "getSections"), $i = /* @__PURE__ */ h(function() {
  let t = Xe();
  const e = 10;
  let n = 0;
  for (; !t && n < e; )
    t = Xe(), n++;
  return te = j, te;
}, "getTasks"), vn = /* @__PURE__ */ h(function(t, e, n, r) {
  return r.includes(t.format(e.trim())) ? !1 : n.includes("weekends") && (t.isoWeekday() === Ze[ee] || t.isoWeekday() === Ze[ee] + 1) || n.includes(t.format("dddd").toLowerCase()) ? !0 : n.includes(t.format(e.trim()));
}, "isInvalidDate"), ta = /* @__PURE__ */ h(function(t) {
  Ue = t;
}, "setWeekday"), ea = /* @__PURE__ */ h(function() {
  return Ue;
}, "getWeekday"), na = /* @__PURE__ */ h(function(t) {
  ee = t;
}, "setWeekend"), bn = /* @__PURE__ */ h(function(t, e, n, r) {
  if (!n.length || t.manualEndTime)
    return;
  let i;
  t.startTime instanceof Date ? i = tt(t.startTime) : i = tt(t.startTime, e, !0), i = i.add(1, "d");
  let a;
  t.endTime instanceof Date ? a = tt(t.endTime) : a = tt(t.endTime, e, !0);
  const [s, C] = ra(i, a, e, n, r);
  t.endTime = s.toDate(), t.renderEndTime = C;
}, "checkTaskDates"), ra = /* @__PURE__ */ h(function(t, e, n, r, i) {
  let a = !1, s = null;
  for (; t <= e; )
    a || (s = e.toDate()), a = vn(t, n, r, i), a && (e = e.add(1, "d")), t = t.add(1, "d");
  return [e, s];
}, "fixTaskDates"), pe = /* @__PURE__ */ h(function(t, e, n) {
  n = n.trim();
  const i = /^after\s+(?<ids>[\d\w- ]+)/.exec(n);
  if (i !== null) {
    let s = null;
    for (const M of i.groups.ids.split(" ")) {
      let T = Ct(M);
      T !== void 0 && (!s || T.endTime > s.endTime) && (s = T);
    }
    if (s)
      return s.endTime;
    const C = /* @__PURE__ */ new Date();
    return C.setHours(0, 0, 0, 0), C;
  }
  let a = tt(n, e.trim(), !0);
  if (a.isValid())
    return a.toDate();
  {
    Qt.debug("Invalid date:" + n), Qt.debug("With date format:" + e.trim());
    const s = new Date(n);
    if (s === void 0 || isNaN(s.getTime()) || // WebKit browsers can mis-parse invalid dates to be ridiculously
    // huge numbers, e.g. new Date('202304') gets parsed as January 1, 202304.
    // This can cause virtually infinite loops while rendering, so for the
    // purposes of Gantt charts we'll just treat any date beyond 10,000 AD/BC as
    // invalid.
    s.getFullYear() < -1e4 || s.getFullYear() > 1e4)
      throw new Error("Invalid date:" + n);
    return s;
  }
}, "getStartDate"), xn = /* @__PURE__ */ h(function(t) {
  const e = /^(\d+(?:\.\d+)?)([Mdhmswy]|ms)$/.exec(t.trim());
  return e !== null ? [Number.parseFloat(e[1]), e[2]] : [NaN, "ms"];
}, "parseDuration"), wn = /* @__PURE__ */ h(function(t, e, n, r = !1) {
  n = n.trim();
  const a = /^until\s+(?<ids>[\d\w- ]+)/.exec(n);
  if (a !== null) {
    let v = null;
    for (const b of a.groups.ids.split(" ")) {
      let p = Ct(b);
      p !== void 0 && (!v || p.startTime < v.startTime) && (v = p);
    }
    if (v)
      return v.startTime;
    const A = /* @__PURE__ */ new Date();
    return A.setHours(0, 0, 0, 0), A;
  }
  let s = tt(n, e.trim(), !0);
  if (s.isValid())
    return r && (s = s.add(1, "d")), s.toDate();
  let C = tt(t);
  const [M, T] = xn(n);
  if (!Number.isNaN(M)) {
    const v = C.add(M, T);
    v.isValid() && (C = v);
  }
  return C.toDate();
}, "getEndDate"), jt = 0, St = /* @__PURE__ */ h(function(t) {
  return t === void 0 ? (jt = jt + 1, "task" + jt) : t;
}, "parseId"), ia = /* @__PURE__ */ h(function(t, e) {
  let n;
  e.substr(0, 1) === ":" ? n = e.substr(1, e.length) : n = e;
  const r = n.split(","), i = {};
  Ee(r, i, Tn);
  for (let s = 0; s < r.length; s++)
    r[s] = r[s].trim();
  let a = "";
  switch (r.length) {
    case 1:
      i.id = St(), i.startTime = t.endTime, a = r[0];
      break;
    case 2:
      i.id = St(), i.startTime = pe(void 0, ct, r[0]), a = r[1];
      break;
    case 3:
      i.id = St(r[0]), i.startTime = pe(void 0, ct, r[1]), a = r[2];
      break;
  }
  return a && (i.endTime = wn(i.startTime, ct, a, Rt), i.manualEndTime = tt(a, "YYYY-MM-DD", !0).isValid(), bn(i, ct, Pt, Vt)), i;
}, "compileData"), aa = /* @__PURE__ */ h(function(t, e) {
  let n;
  e.substr(0, 1) === ":" ? n = e.substr(1, e.length) : n = e;
  const r = n.split(","), i = {};
  Ee(r, i, Tn);
  for (let a = 0; a < r.length; a++)
    r[a] = r[a].trim();
  switch (r.length) {
    case 1:
      i.id = St(), i.startTime = {
        type: "prevTaskEnd",
        id: t
      }, i.endTime = {
        data: r[0]
      };
      break;
    case 2:
      i.id = St(), i.startTime = {
        type: "getStartDate",
        startData: r[0]
      }, i.endTime = {
        data: r[1]
      };
      break;
    case 3:
      i.id = St(r[0]), i.startTime = {
        type: "getStartDate",
        startData: r[1]
      }, i.endTime = {
        data: r[2]
      };
      break;
  }
  return i;
}, "parseData"), Te, Gt, j = [], Cn = {}, sa = /* @__PURE__ */ h(function(t, e) {
  const n = {
    section: Et,
    type: Et,
    processed: !1,
    manualEndTime: !1,
    renderEndTime: null,
    raw: {
      data: e
    },
    task: t,
    classes: []
  }, r = aa(Gt, e);
  n.raw.startTime = r.startTime, n.raw.endTime = r.endTime, n.id = r.id, n.prevTaskId = Gt, n.active = r.active, n.done = r.done, n.crit = r.crit, n.milestone = r.milestone, n.vert = r.vert, n.order = ke, ke++;
  const i = j.push(n);
  Gt = n.id, Cn[n.id] = i - 1;
}, "addTask"), Ct = /* @__PURE__ */ h(function(t) {
  const e = Cn[t];
  return j[e];
}, "findTaskById"), oa = /* @__PURE__ */ h(function(t, e) {
  const n = {
    section: Et,
    type: Et,
    description: t,
    task: t,
    classes: []
  }, r = ia(Te, e);
  n.startTime = r.startTime, n.endTime = r.endTime, n.id = r.id, n.active = r.active, n.done = r.done, n.crit = r.crit, n.milestone = r.milestone, n.vert = r.vert, Te = n, te.push(n);
}, "addTaskOrg"), Xe = /* @__PURE__ */ h(function() {
  const t = /* @__PURE__ */ h(function(n) {
    const r = j[n];
    let i = "";
    switch (j[n].raw.startTime.type) {
      case "prevTaskEnd": {
        const a = Ct(r.prevTaskId);
        r.startTime = a.endTime;
        break;
      }
      case "getStartDate":
        i = pe(void 0, ct, j[n].raw.startTime.startData), i && (j[n].startTime = i);
        break;
    }
    return j[n].startTime && (j[n].endTime = wn(j[n].startTime, ct, j[n].raw.endTime.data, Rt), j[n].endTime && (j[n].processed = !0, j[n].manualEndTime = tt(j[n].raw.endTime.data, "YYYY-MM-DD", !0).isValid(), bn(j[n], ct, Pt, Vt))), j[n].processed;
  }, "compileTask");
  let e = !0;
  for (const [n, r] of j.entries())
    t(n), e = e && r.processed;
  return e;
}, "compileTasks"), ca = /* @__PURE__ */ h(function(t, e) {
  let n = e;
  _t().securityLevel !== "loose" && (n = On(e)), t.split(",").forEach(function(r) {
    Ct(r) !== void 0 && (_n(r, () => {
      window.open(n, "_self");
    }), De.set(r, n));
  }), Dn(t, "clickable");
}, "setLink"), Dn = /* @__PURE__ */ h(function(t, e) {
  t.split(",").forEach(function(n) {
    let r = Ct(n);
    r !== void 0 && r.classes.push(e);
  });
}, "setClass"), la = /* @__PURE__ */ h(function(t, e, n) {
  if (_t().securityLevel !== "loose" || e === void 0)
    return;
  let r = [];
  if (typeof n == "string") {
    r = n.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);
    for (let a = 0; a < r.length; a++) {
      let s = r[a].trim();
      s.startsWith('"') && s.endsWith('"') && (s = s.substr(1, s.length - 2)), r[a] = s;
    }
  }
  r.length === 0 && r.push(t), Ct(t) !== void 0 && _n(t, () => {
    Hn.runFunc(e, ...r);
  });
}, "setClickFun"), _n = /* @__PURE__ */ h(function(t, e) {
  Se.push(function() {
    const n = document.querySelector(`[id="${t}"]`);
    n !== null && n.addEventListener("click", function() {
      e();
    });
  }, function() {
    const n = document.querySelector(`[id="${t}-text"]`);
    n !== null && n.addEventListener("click", function() {
      e();
    });
  });
}, "pushFun"), ua = /* @__PURE__ */ h(function(t, e, n) {
  t.split(",").forEach(function(r) {
    la(r, e, n);
  }), Dn(t, "clickable");
}, "setClickEvent"), fa = /* @__PURE__ */ h(function(t) {
  Se.forEach(function(e) {
    e(t);
  });
}, "bindFunctions"), ha = {
  getConfig: /* @__PURE__ */ h(() => _t().gantt, "getConfig"),
  clear: Ei,
  setDateFormat: Ni,
  getDateFormat: qi,
  enableInclusiveEndDates: Hi,
  endDatesAreInclusive: Vi,
  enableTopAxis: Pi,
  topAxisEnabled: Ri,
  setAxisFormat: Ii,
  getAxisFormat: Ai,
  setTickInterval: Li,
  getTickInterval: Wi,
  setTodayMarker: Yi,
  getTodayMarker: Oi,
  setAccTitle: Ln,
  getAccTitle: An,
  setDiagramTitle: In,
  getDiagramTitle: En,
  setDisplayMode: zi,
  getDisplayMode: Bi,
  setAccDescription: Un,
  getAccDescription: Fn,
  addSection: Ji,
  getSections: Ki,
  getTasks: $i,
  addTask: sa,
  findTaskById: Ct,
  addTaskOrg: oa,
  setIncludes: Zi,
  getIncludes: Xi,
  setExcludes: ji,
  getExcludes: Gi,
  setClickEvent: ua,
  setLink: ca,
  getLinks: Qi,
  bindFunctions: fa,
  parseDuration: xn,
  isInvalidDate: vn,
  setWeekday: ta,
  getWeekday: ea,
  setWeekend: na
};
function Ee(t, e, n) {
  let r = !0;
  for (; r; )
    r = !1, n.forEach(function(i) {
      const a = "^\\s*" + i + "\\s*$", s = new RegExp(a);
      t[0].match(s) && (e[i] = !0, t.shift(1), r = !0);
    });
}
h(Ee, "getTaskTags");
var da = /* @__PURE__ */ h(function() {
  Qt.debug("Something is calling, setConf, remove the call");
}, "setConf"), je = {
  monday: Ot,
  tuesday: cn,
  wednesday: ln,
  thursday: vt,
  friday: un,
  saturday: fn,
  sunday: Ht
}, ma = /* @__PURE__ */ h((t, e) => {
  let n = [...t].map(() => -1 / 0), r = [...t].sort((a, s) => a.startTime - s.startTime || a.order - s.order), i = 0;
  for (const a of r)
    for (let s = 0; s < n.length; s++)
      if (a.startTime >= n[s]) {
        n[s] = a.endTime, a.order = s + e, s > i && (i = s);
        break;
      }
  return i;
}, "getMaxIntersections"), ht, ga = /* @__PURE__ */ h(function(t, e, n, r) {
  const i = _t().gantt, a = _t().securityLevel;
  let s;
  a === "sandbox" && (s = qt("#i" + e));
  const C = a === "sandbox" ? qt(s.nodes()[0].contentDocument.body) : qt("body"), M = a === "sandbox" ? s.nodes()[0].contentDocument : document, T = M.getElementById(e);
  ht = T.parentElement.offsetWidth, ht === void 0 && (ht = 1200), i.useWidth !== void 0 && (ht = i.useWidth);
  const v = r.db.getTasks();
  let A = [];
  for (const w of v)
    A.push(w.type);
  A = H(A);
  const b = {};
  let p = 2 * i.topPadding;
  if (r.db.getDisplayMode() === "compact" || i.displayMode === "compact") {
    const w = {};
    for (const D of v)
      w[D.section] === void 0 ? w[D.section] = [D] : w[D.section].push(D);
    let F = 0;
    for (const D of Object.keys(w)) {
      const _ = ma(w[D], F) + 1;
      F += _, p += _ * (i.barHeight + i.barGap), b[D] = _;
    }
  } else {
    p += v.length * (i.barHeight + i.barGap);
    for (const w of A)
      b[w] = v.filter((F) => F.type === w).length;
  }
  T.setAttribute("viewBox", "0 0 " + ht + " " + p);
  const R = C.select(`[id="${e}"]`), I = Mi().domain([Qn(v, function(w) {
    return w.startTime;
  }), Gn(v, function(w) {
    return w.endTime;
  })]).rangeRound([0, ht - i.leftPadding - i.rightPadding]);
  function et(w, F) {
    const D = w.startTime, _ = F.startTime;
    let k = 0;
    return D > _ ? k = 1 : D < _ && (k = -1), k;
  }
  h(et, "taskCompare"), v.sort(et), rt(v, ht, p), Wn(R, p, ht, i.useMaxWidth), R.append("text").text(r.db.getDiagramTitle()).attr("x", ht / 2).attr("y", i.titleTopMargin).attr("class", "titleText");
  function rt(w, F, D) {
    const _ = i.barHeight, k = _ + i.barGap, L = i.topPadding, f = i.leftPadding, d = Xn().domain([0, A.length]).range(["#00B9FA", "#F95002"]).interpolate(fr);
    Z(k, L, f, F, D, w, r.db.getExcludes(), r.db.getIncludes()), X(f, L, F, D), nt(w, k, L, f, _, d, F), $(k, L), x(f, L, F, D);
  }
  h(rt, "makeGantt");
  function nt(w, F, D, _, k, L, f) {
    w.sort((l, o) => l.vert === o.vert ? 0 : l.vert ? 1 : -1);
    const y = [...new Set(w.map((l) => l.order))].map((l) => w.find((o) => o.order === l));
    R.append("g").selectAll("rect").data(y).enter().append("rect").attr("x", 0).attr("y", function(l, o) {
      return o = l.order, o * F + D - 2;
    }).attr("width", function() {
      return f - i.rightPadding / 2;
    }).attr("height", F).attr("class", function(l) {
      for (const [o, V] of A.entries())
        if (l.type === V)
          return "section section" + o % i.numberSectionStyles;
      return "section section0";
    }).enter();
    const m = R.append("g").selectAll("rect").data(w).enter(), U = r.db.getLinks();
    if (m.append("rect").attr("id", function(l) {
      return l.id;
    }).attr("rx", 3).attr("ry", 3).attr("x", function(l) {
      return l.milestone ? I(l.startTime) + _ + 0.5 * (I(l.endTime) - I(l.startTime)) - 0.5 * k : I(l.startTime) + _;
    }).attr("y", function(l, o) {
      return o = l.order, l.vert ? i.gridLineStartPadding : o * F + D;
    }).attr("width", function(l) {
      return l.milestone ? k : l.vert ? 0.08 * k : I(l.renderEndTime || l.endTime) - I(l.startTime);
    }).attr("height", function(l) {
      return l.vert ? v.length * (i.barHeight + i.barGap) + i.barHeight * 2 : k;
    }).attr("transform-origin", function(l, o) {
      return o = l.order, (I(l.startTime) + _ + 0.5 * (I(l.endTime) - I(l.startTime))).toString() + "px " + (o * F + D + 0.5 * k).toString() + "px";
    }).attr("class", function(l) {
      const o = "task";
      let V = "";
      l.classes.length > 0 && (V = l.classes.join(" "));
      let Y = 0;
      for (const [Q, z] of A.entries())
        l.type === z && (Y = Q % i.numberSectionStyles);
      let O = "";
      return l.active ? l.crit ? O += " activeCrit" : O = " active" : l.done ? l.crit ? O = " doneCrit" : O = " done" : l.crit && (O += " crit"), O.length === 0 && (O = " task"), l.milestone && (O = " milestone " + O), l.vert && (O = " vert " + O), O += Y, O += " " + V, o + O;
    }), m.append("text").attr("id", function(l) {
      return l.id + "-text";
    }).text(function(l) {
      return l.task;
    }).attr("font-size", i.fontSize).attr("x", function(l) {
      let o = I(l.startTime), V = I(l.renderEndTime || l.endTime);
      if (l.milestone && (o += 0.5 * (I(l.endTime) - I(l.startTime)) - 0.5 * k, V = o + k), l.vert)
        return I(l.startTime) + _;
      const Y = this.getBBox().width;
      return Y > V - o ? V + Y + 1.5 * i.leftPadding > f ? o + _ - 5 : V + _ + 5 : (V - o) / 2 + o + _;
    }).attr("y", function(l, o) {
      return l.vert ? i.gridLineStartPadding + v.length * (i.barHeight + i.barGap) + 60 : (o = l.order, o * F + i.barHeight / 2 + (i.fontSize / 2 - 2) + D);
    }).attr("text-height", k).attr("class", function(l) {
      const o = I(l.startTime);
      let V = I(l.endTime);
      l.milestone && (V = o + k);
      const Y = this.getBBox().width;
      let O = "";
      l.classes.length > 0 && (O = l.classes.join(" "));
      let Q = 0;
      for (const [B, st] of A.entries())
        l.type === st && (Q = B % i.numberSectionStyles);
      let z = "";
      return l.active && (l.crit ? z = "activeCritText" + Q : z = "activeText" + Q), l.done ? l.crit ? z = z + " doneCritText" + Q : z = z + " doneText" + Q : l.crit && (z = z + " critText" + Q), l.milestone && (z += " milestoneText"), l.vert && (z += " vertText"), Y > V - o ? V + Y + 1.5 * i.leftPadding > f ? O + " taskTextOutsideLeft taskTextOutside" + Q + " " + z : O + " taskTextOutsideRight taskTextOutside" + Q + " " + z + " width-" + Y : O + " taskText taskText" + Q + " " + z + " width-" + Y;
    }), _t().securityLevel === "sandbox") {
      let l;
      l = qt("#i" + e);
      const o = l.nodes()[0].contentDocument;
      m.filter(function(V) {
        return U.has(V.id);
      }).each(function(V) {
        var Y = o.querySelector("#" + V.id), O = o.querySelector("#" + V.id + "-text");
        const Q = Y.parentNode;
        var z = o.createElement("a");
        z.setAttribute("xlink:href", U.get(V.id)), z.setAttribute("target", "_top"), Q.appendChild(z), z.appendChild(Y), z.appendChild(O);
      });
    }
  }
  h(nt, "drawRects");
  function Z(w, F, D, _, k, L, f, d) {
    if (f.length === 0 && d.length === 0)
      return;
    let y, m;
    for (const {
      startTime: Y,
      endTime: O
    } of L)
      (y === void 0 || Y < y) && (y = Y), (m === void 0 || O > m) && (m = O);
    if (!y || !m)
      return;
    if (tt(m).diff(tt(y), "year") > 5) {
      Qt.warn("The difference between the min and max time is more than 5 years. This will cause performance issues. Skipping drawing exclude days.");
      return;
    }
    const U = r.db.getDateFormat(), c = [];
    let l = null, o = tt(y);
    for (; o.valueOf() <= m; )
      r.db.isInvalidDate(o, U, f, d) ? l ? l.end = o : l = {
        start: o,
        end: o
      } : l && (c.push(l), l = null), o = o.add(1, "d");
    R.append("g").selectAll("rect").data(c).enter().append("rect").attr("id", function(Y) {
      return "exclude-" + Y.start.format("YYYY-MM-DD");
    }).attr("x", function(Y) {
      return I(Y.start) + D;
    }).attr("y", i.gridLineStartPadding).attr("width", function(Y) {
      const O = Y.end.add(1, "day");
      return I(O) - I(Y.start);
    }).attr("height", k - F - i.gridLineStartPadding).attr("transform-origin", function(Y, O) {
      return (I(Y.start) + D + 0.5 * (I(Y.end) - I(Y.start))).toString() + "px " + (O * w + 0.5 * k).toString() + "px";
    }).attr("class", "exclude-range");
  }
  h(Z, "drawExcludeDays");
  function X(w, F, D, _) {
    let k = ir(I).tickSize(-_ + F + i.gridLineStartPadding).tickFormat($t(r.db.getAxisFormat() || i.axisFormat || "%Y-%m-%d"));
    const f = /^([1-9]\d*)(millisecond|second|minute|hour|day|week|month)$/.exec(r.db.getTickInterval() || i.tickInterval);
    if (f !== null) {
      const d = f[1], y = f[2], m = r.db.getWeekday() || i.weekday;
      switch (y) {
        case "millisecond":
          k.ticks(Ft.every(d));
          break;
        case "second":
          k.ticks(pt.every(d));
          break;
        case "minute":
          k.ticks(Wt.every(d));
          break;
        case "hour":
          k.ticks(Yt.every(d));
          break;
        case "day":
          k.ticks(Tt.every(d));
          break;
        case "week":
          k.ticks(je[m].every(d));
          break;
        case "month":
          k.ticks(Nt.every(d));
          break;
      }
    }
    if (R.append("g").attr("class", "grid").attr("transform", "translate(" + w + ", " + (_ - 50) + ")").call(k).selectAll("text").style("text-anchor", "middle").attr("fill", "#000").attr("stroke", "none").attr("font-size", 10).attr("dy", "1em"), r.db.topAxisEnabled() || i.topAxis) {
      let d = rr(I).tickSize(-_ + F + i.gridLineStartPadding).tickFormat($t(r.db.getAxisFormat() || i.axisFormat || "%Y-%m-%d"));
      if (f !== null) {
        const y = f[1], m = f[2], U = r.db.getWeekday() || i.weekday;
        switch (m) {
          case "millisecond":
            d.ticks(Ft.every(y));
            break;
          case "second":
            d.ticks(pt.every(y));
            break;
          case "minute":
            d.ticks(Wt.every(y));
            break;
          case "hour":
            d.ticks(Yt.every(y));
            break;
          case "day":
            d.ticks(Tt.every(y));
            break;
          case "week":
            d.ticks(je[U].every(y));
            break;
          case "month":
            d.ticks(Nt.every(y));
            break;
        }
      }
      R.append("g").attr("class", "grid").attr("transform", "translate(" + w + ", " + F + ")").call(d).selectAll("text").style("text-anchor", "middle").attr("fill", "#000").attr("stroke", "none").attr("font-size", 10);
    }
  }
  h(X, "makeGrid");
  function $(w, F) {
    let D = 0;
    const _ = Object.keys(b).map((k) => [k, b[k]]);
    R.append("g").selectAll("text").data(_).enter().append(function(k) {
      const L = k[0].split(Yn.lineBreakRegex), f = -(L.length - 1) / 2, d = M.createElementNS("http://www.w3.org/2000/svg", "text");
      d.setAttribute("dy", f + "em");
      for (const [y, m] of L.entries()) {
        const U = M.createElementNS("http://www.w3.org/2000/svg", "tspan");
        U.setAttribute("alignment-baseline", "central"), U.setAttribute("x", "10"), y > 0 && U.setAttribute("dy", "1em"), U.textContent = m, d.appendChild(U);
      }
      return d;
    }).attr("x", 10).attr("y", function(k, L) {
      if (L > 0)
        for (let f = 0; f < L; f++)
          return D += _[L - 1][1], k[1] * w / 2 + D * w + F;
      else
        return k[1] * w / 2 + F;
    }).attr("font-size", i.sectionFontSize).attr("class", function(k) {
      for (const [L, f] of A.entries())
        if (k[0] === f)
          return "sectionTitle sectionTitle" + L % i.numberSectionStyles;
      return "sectionTitle";
    });
  }
  h($, "vertLabels");
  function x(w, F, D, _) {
    const k = r.db.getTodayMarker();
    if (k === "off")
      return;
    const L = R.append("g").attr("class", "today"), f = /* @__PURE__ */ new Date(), d = L.append("line");
    d.attr("x1", I(f) + w).attr("x2", I(f) + w).attr("y1", i.titleTopMargin).attr("y2", _ - i.titleTopMargin).attr("class", "today"), k !== "" && d.attr("style", k.replace(/,/g, ";"));
  }
  h(x, "drawToday");
  function H(w) {
    const F = {}, D = [];
    for (let _ = 0, k = w.length; _ < k; ++_)
      Object.prototype.hasOwnProperty.call(F, w[_]) || (F[w[_]] = !0, D.push(w[_]));
    return D;
  }
  h(H, "checkUnique");
}, "draw"), ya = {
  setConf: da,
  draw: ga
}, ka = /* @__PURE__ */ h((t) => `
  .mermaid-main-font {
        font-family: ${t.fontFamily};
  }

  .exclude-range {
    fill: ${t.excludeBkgColor};
  }

  .section {
    stroke: none;
    opacity: 0.2;
  }

  .section0 {
    fill: ${t.sectionBkgColor};
  }

  .section2 {
    fill: ${t.sectionBkgColor2};
  }

  .section1,
  .section3 {
    fill: ${t.altSectionBkgColor};
    opacity: 0.2;
  }

  .sectionTitle0 {
    fill: ${t.titleColor};
  }

  .sectionTitle1 {
    fill: ${t.titleColor};
  }

  .sectionTitle2 {
    fill: ${t.titleColor};
  }

  .sectionTitle3 {
    fill: ${t.titleColor};
  }

  .sectionTitle {
    text-anchor: start;
    font-family: ${t.fontFamily};
  }


  /* Grid and axis */

  .grid .tick {
    stroke: ${t.gridColor};
    opacity: 0.8;
    shape-rendering: crispEdges;
  }

  .grid .tick text {
    font-family: ${t.fontFamily};
    fill: ${t.textColor};
  }

  .grid path {
    stroke-width: 0;
  }


  /* Today line */

  .today {
    fill: none;
    stroke: ${t.todayLineColor};
    stroke-width: 2px;
  }


  /* Task styling */

  /* Default task */

  .task {
    stroke-width: 2;
  }

  .taskText {
    text-anchor: middle;
    font-family: ${t.fontFamily};
  }

  .taskTextOutsideRight {
    fill: ${t.taskTextDarkColor};
    text-anchor: start;
    font-family: ${t.fontFamily};
  }

  .taskTextOutsideLeft {
    fill: ${t.taskTextDarkColor};
    text-anchor: end;
  }


  /* Special case clickable */

  .task.clickable {
    cursor: pointer;
  }

  .taskText.clickable {
    cursor: pointer;
    fill: ${t.taskTextClickableColor} !important;
    font-weight: bold;
  }

  .taskTextOutsideLeft.clickable {
    cursor: pointer;
    fill: ${t.taskTextClickableColor} !important;
    font-weight: bold;
  }

  .taskTextOutsideRight.clickable {
    cursor: pointer;
    fill: ${t.taskTextClickableColor} !important;
    font-weight: bold;
  }


  /* Specific task settings for the sections*/

  .taskText0,
  .taskText1,
  .taskText2,
  .taskText3 {
    fill: ${t.taskTextColor};
  }

  .task0,
  .task1,
  .task2,
  .task3 {
    fill: ${t.taskBkgColor};
    stroke: ${t.taskBorderColor};
  }

  .taskTextOutside0,
  .taskTextOutside2
  {
    fill: ${t.taskTextOutsideColor};
  }

  .taskTextOutside1,
  .taskTextOutside3 {
    fill: ${t.taskTextOutsideColor};
  }


  /* Active task */

  .active0,
  .active1,
  .active2,
  .active3 {
    fill: ${t.activeTaskBkgColor};
    stroke: ${t.activeTaskBorderColor};
  }

  .activeText0,
  .activeText1,
  .activeText2,
  .activeText3 {
    fill: ${t.taskTextDarkColor} !important;
  }


  /* Completed task */

  .done0,
  .done1,
  .done2,
  .done3 {
    stroke: ${t.doneTaskBorderColor};
    fill: ${t.doneTaskBkgColor};
    stroke-width: 2;
  }

  .doneText0,
  .doneText1,
  .doneText2,
  .doneText3 {
    fill: ${t.taskTextDarkColor} !important;
  }


  /* Tasks on the critical line */

  .crit0,
  .crit1,
  .crit2,
  .crit3 {
    stroke: ${t.critBorderColor};
    fill: ${t.critBkgColor};
    stroke-width: 2;
  }

  .activeCrit0,
  .activeCrit1,
  .activeCrit2,
  .activeCrit3 {
    stroke: ${t.critBorderColor};
    fill: ${t.activeTaskBkgColor};
    stroke-width: 2;
  }

  .doneCrit0,
  .doneCrit1,
  .doneCrit2,
  .doneCrit3 {
    stroke: ${t.critBorderColor};
    fill: ${t.doneTaskBkgColor};
    stroke-width: 2;
    cursor: pointer;
    shape-rendering: crispEdges;
  }

  .milestone {
    transform: rotate(45deg) scale(0.8,0.8);
  }

  .milestoneText {
    font-style: italic;
  }
  .doneCritText0,
  .doneCritText1,
  .doneCritText2,
  .doneCritText3 {
    fill: ${t.taskTextDarkColor} !important;
  }

  .vert {
    stroke: ${t.vertLineColor};
  }

  .vertText {
    font-size: 15px;
    text-anchor: middle;
    fill: ${t.vertLineColor} !important;
  }

  .activeCritText0,
  .activeCritText1,
  .activeCritText2,
  .activeCritText3 {
    fill: ${t.taskTextDarkColor} !important;
  }

  .titleText {
    text-anchor: middle;
    font-size: 18px;
    fill: ${t.titleColor || t.textColor};
    font-family: ${t.fontFamily};
  }
`, "getStyles"), pa = ka, wa = {
  parser: Ui,
  db: ha,
  renderer: ya,
  styles: pa
};
export {
  wa as diagram
};
