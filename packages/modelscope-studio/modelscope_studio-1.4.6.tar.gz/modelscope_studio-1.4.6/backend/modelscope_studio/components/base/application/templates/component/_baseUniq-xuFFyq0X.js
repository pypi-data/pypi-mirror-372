import { m as o, x as v, r as A, y as R, p as c, z as p, n as x, o as E, k as F, A as S, S as b, B as I, C as k, D as N } from "./Index-tGU7TQVz.js";
function O(n, e, r, s) {
  for (var t = n.length, i = r + -1; ++i < t; )
    if (e(n[i], i, n))
      return i;
  return -1;
}
function C(n) {
  return n !== n;
}
function B(n, e, r) {
  for (var s = r - 1, t = n.length; ++s < t; )
    if (n[s] === e)
      return s;
  return -1;
}
function L(n, e, r) {
  return e === e ? B(n, e, r) : O(n, C, r);
}
function T(n, e) {
  var r = n == null ? 0 : n.length;
  return !!r && L(n, e, 0) > -1;
}
function Y(n, e, r, s) {
  var t = -1, i = n == null ? 0 : n.length;
  for (s && i && (r = n[++t]); ++t < i; )
    r = e(r, n[t], t, n);
  return r;
}
function _(n, e) {
  return function(r, s) {
    if (r == null)
      return r;
    if (!o(r))
      return n(r, s);
    for (var t = r.length, i = -1, a = Object(r); ++i < t && s(a[i], i, a) !== !1; )
      ;
    return r;
  };
}
var l = _(v);
function q(n) {
  return typeof n == "function" ? n : A;
}
function Z(n, e) {
  var r = c(n) ? R : l;
  return r(n, q(e));
}
function z(n, e) {
  var r = [];
  return l(n, function(s, t, i) {
    e(s, t, i) && r.push(s);
  }), r;
}
function y(n, e) {
  var r = c(n) ? p : z;
  return r(n, x(e));
}
function D(n, e) {
  return E(e, function(r) {
    return n[r];
  });
}
function J(n) {
  return n == null ? [] : D(n, F(n));
}
function G(n, e, r, s, t) {
  return t(n, function(i, a, f) {
    r = s ? (s = !1, i) : e(r, i, a, f);
  }), r;
}
function K(n, e, r) {
  var s = c(n) ? Y : G, t = arguments.length < 3;
  return s(n, x(e), r, t, l);
}
var H = 1 / 0, M = b && 1 / I(new b([, -0]))[1] == H ? function(n) {
  return new b(n);
} : S, U = 200;
function P(n, e, r) {
  var s = -1, t = T, i = n.length, a = !0, f = [], u = f;
  if (i >= U) {
    var w = e ? null : M(n);
    if (w)
      return I(w);
    a = !1, t = N, u = new k();
  } else
    u = e ? [] : f;
  n: for (; ++s < i; ) {
    var h = n[s], g = e ? e(h) : h;
    if (h = h !== 0 ? h : 0, a && g === g) {
      for (var d = u.length; d--; )
        if (u[d] === g)
          continue n;
      e && u.push(g), f.push(h);
    } else t(u, g, r) || (u !== f && u.push(g), f.push(h));
  }
  return f;
}
export {
  Z as a,
  P as b,
  O as c,
  l as d,
  q as e,
  y as f,
  T as g,
  L as h,
  z as i,
  K as r,
  J as v
};
