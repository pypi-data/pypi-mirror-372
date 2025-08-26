var _t = typeof global == "object" && global && global.Object === Object && global, nn = typeof self == "object" && self && self.Object === Object && self, E = _t || nn || Function("return this")(), A = E.Symbol, bt = Object.prototype, rn = bt.hasOwnProperty, on = bt.toString, z = A ? A.toStringTag : void 0;
function an(e) {
  var t = rn.call(e, z), n = e[z];
  try {
    e[z] = void 0;
    var r = !0;
  } catch {
  }
  var i = on.call(e);
  return r && (t ? e[z] = n : delete e[z]), i;
}
var sn = Object.prototype, un = sn.toString;
function ln(e) {
  return un.call(e);
}
var cn = "[object Null]", fn = "[object Undefined]", Ke = A ? A.toStringTag : void 0;
function D(e) {
  return e == null ? e === void 0 ? fn : cn : Ke && Ke in Object(e) ? an(e) : ln(e);
}
function I(e) {
  return e != null && typeof e == "object";
}
var pn = "[object Symbol]";
function Pe(e) {
  return typeof e == "symbol" || I(e) && D(e) == pn;
}
function ht(e, t) {
  for (var n = -1, r = e == null ? 0 : e.length, i = Array(r); ++n < r; )
    i[n] = t(e[n], n, e);
  return i;
}
var x = Array.isArray, Ue = A ? A.prototype : void 0, Ge = Ue ? Ue.toString : void 0;
function yt(e) {
  if (typeof e == "string")
    return e;
  if (x(e))
    return ht(e, yt) + "";
  if (Pe(e))
    return Ge ? Ge.call(e) : "";
  var t = e + "";
  return t == "0" && 1 / e == -1 / 0 ? "-0" : t;
}
function Z(e) {
  var t = typeof e;
  return e != null && (t == "object" || t == "function");
}
function mt(e) {
  return e;
}
var gn = "[object AsyncFunction]", dn = "[object Function]", _n = "[object GeneratorFunction]", bn = "[object Proxy]";
function vt(e) {
  if (!Z(e))
    return !1;
  var t = D(e);
  return t == dn || t == _n || t == gn || t == bn;
}
var de = E["__core-js_shared__"], Be = function() {
  var e = /[^.]+$/.exec(de && de.keys && de.keys.IE_PROTO || "");
  return e ? "Symbol(src)_1." + e : "";
}();
function hn(e) {
  return !!Be && Be in e;
}
var yn = Function.prototype, mn = yn.toString;
function N(e) {
  if (e != null) {
    try {
      return mn.call(e);
    } catch {
    }
    try {
      return e + "";
    } catch {
    }
  }
  return "";
}
var vn = /[\\^$.*+?()[\]{}|]/g, Tn = /^\[object .+?Constructor\]$/, On = Function.prototype, Pn = Object.prototype, wn = On.toString, An = Pn.hasOwnProperty, Sn = RegExp("^" + wn.call(An).replace(vn, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$");
function $n(e) {
  if (!Z(e) || hn(e))
    return !1;
  var t = vt(e) ? Sn : Tn;
  return t.test(N(e));
}
function xn(e, t) {
  return e == null ? void 0 : e[t];
}
function K(e, t) {
  var n = xn(e, t);
  return $n(n) ? n : void 0;
}
var he = K(E, "WeakMap");
function Cn(e, t, n) {
  switch (n.length) {
    case 0:
      return e.call(t);
    case 1:
      return e.call(t, n[0]);
    case 2:
      return e.call(t, n[0], n[1]);
    case 3:
      return e.call(t, n[0], n[1], n[2]);
  }
  return e.apply(t, n);
}
var jn = 800, En = 16, In = Date.now;
function Mn(e) {
  var t = 0, n = 0;
  return function() {
    var r = In(), i = En - (r - n);
    if (n = r, i > 0) {
      if (++t >= jn)
        return arguments[0];
    } else
      t = 0;
    return e.apply(void 0, arguments);
  };
}
function Fn(e) {
  return function() {
    return e;
  };
}
var oe = function() {
  try {
    var e = K(Object, "defineProperty");
    return e({}, "", {}), e;
  } catch {
  }
}(), Rn = oe ? function(e, t) {
  return oe(e, "toString", {
    configurable: !0,
    enumerable: !1,
    value: Fn(t),
    writable: !0
  });
} : mt, Ln = Mn(Rn);
function Dn(e, t) {
  for (var n = -1, r = e == null ? 0 : e.length; ++n < r && t(e[n], n, e) !== !1; )
    ;
  return e;
}
var Nn = 9007199254740991, Kn = /^(?:0|[1-9]\d*)$/;
function Tt(e, t) {
  var n = typeof e;
  return t = t ?? Nn, !!t && (n == "number" || n != "symbol" && Kn.test(e)) && e > -1 && e % 1 == 0 && e < t;
}
function we(e, t, n) {
  t == "__proto__" && oe ? oe(e, t, {
    configurable: !0,
    enumerable: !0,
    value: n,
    writable: !0
  }) : e[t] = n;
}
function Ae(e, t) {
  return e === t || e !== e && t !== t;
}
var Un = Object.prototype, Gn = Un.hasOwnProperty;
function Ot(e, t, n) {
  var r = e[t];
  (!(Gn.call(e, t) && Ae(r, n)) || n === void 0 && !(t in e)) && we(e, t, n);
}
function Bn(e, t, n, r) {
  var i = !n;
  n || (n = {});
  for (var o = -1, a = t.length; ++o < a; ) {
    var s = t[o], u = void 0;
    u === void 0 && (u = e[s]), i ? we(n, s, u) : Ot(n, s, u);
  }
  return n;
}
var ze = Math.max;
function zn(e, t, n) {
  return t = ze(t === void 0 ? e.length - 1 : t, 0), function() {
    for (var r = arguments, i = -1, o = ze(r.length - t, 0), a = Array(o); ++i < o; )
      a[i] = r[t + i];
    i = -1;
    for (var s = Array(t + 1); ++i < t; )
      s[i] = r[i];
    return s[t] = n(a), Cn(e, this, s);
  };
}
var Hn = 9007199254740991;
function Se(e) {
  return typeof e == "number" && e > -1 && e % 1 == 0 && e <= Hn;
}
function Pt(e) {
  return e != null && Se(e.length) && !vt(e);
}
var Xn = Object.prototype;
function wt(e) {
  var t = e && e.constructor, n = typeof t == "function" && t.prototype || Xn;
  return e === n;
}
function Jn(e, t) {
  for (var n = -1, r = Array(e); ++n < e; )
    r[n] = t(n);
  return r;
}
var qn = "[object Arguments]";
function He(e) {
  return I(e) && D(e) == qn;
}
var At = Object.prototype, Zn = At.hasOwnProperty, Yn = At.propertyIsEnumerable, $e = He(/* @__PURE__ */ function() {
  return arguments;
}()) ? He : function(e) {
  return I(e) && Zn.call(e, "callee") && !Yn.call(e, "callee");
};
function Wn() {
  return !1;
}
var St = typeof exports == "object" && exports && !exports.nodeType && exports, Xe = St && typeof module == "object" && module && !module.nodeType && module, Qn = Xe && Xe.exports === St, Je = Qn ? E.Buffer : void 0, Vn = Je ? Je.isBuffer : void 0, ae = Vn || Wn, kn = "[object Arguments]", er = "[object Array]", tr = "[object Boolean]", nr = "[object Date]", rr = "[object Error]", ir = "[object Function]", or = "[object Map]", ar = "[object Number]", sr = "[object Object]", ur = "[object RegExp]", lr = "[object Set]", cr = "[object String]", fr = "[object WeakMap]", pr = "[object ArrayBuffer]", gr = "[object DataView]", dr = "[object Float32Array]", _r = "[object Float64Array]", br = "[object Int8Array]", hr = "[object Int16Array]", yr = "[object Int32Array]", mr = "[object Uint8Array]", vr = "[object Uint8ClampedArray]", Tr = "[object Uint16Array]", Or = "[object Uint32Array]", m = {};
m[dr] = m[_r] = m[br] = m[hr] = m[yr] = m[mr] = m[vr] = m[Tr] = m[Or] = !0;
m[kn] = m[er] = m[pr] = m[tr] = m[gr] = m[nr] = m[rr] = m[ir] = m[or] = m[ar] = m[sr] = m[ur] = m[lr] = m[cr] = m[fr] = !1;
function Pr(e) {
  return I(e) && Se(e.length) && !!m[D(e)];
}
function xe(e) {
  return function(t) {
    return e(t);
  };
}
var $t = typeof exports == "object" && exports && !exports.nodeType && exports, H = $t && typeof module == "object" && module && !module.nodeType && module, wr = H && H.exports === $t, _e = wr && _t.process, B = function() {
  try {
    var e = H && H.require && H.require("util").types;
    return e || _e && _e.binding && _e.binding("util");
  } catch {
  }
}(), qe = B && B.isTypedArray, xt = qe ? xe(qe) : Pr, Ar = Object.prototype, Sr = Ar.hasOwnProperty;
function Ct(e, t) {
  var n = x(e), r = !n && $e(e), i = !n && !r && ae(e), o = !n && !r && !i && xt(e), a = n || r || i || o, s = a ? Jn(e.length, String) : [], u = s.length;
  for (var l in e)
    (t || Sr.call(e, l)) && !(a && // Safari 9 has enumerable `arguments.length` in strict mode.
    (l == "length" || // Node.js 0.10 has enumerable non-index properties on buffers.
    i && (l == "offset" || l == "parent") || // PhantomJS 2 has enumerable non-index properties on typed arrays.
    o && (l == "buffer" || l == "byteLength" || l == "byteOffset") || // Skip index properties.
    Tt(l, u))) && s.push(l);
  return s;
}
function jt(e, t) {
  return function(n) {
    return e(t(n));
  };
}
var $r = jt(Object.keys, Object), xr = Object.prototype, Cr = xr.hasOwnProperty;
function jr(e) {
  if (!wt(e))
    return $r(e);
  var t = [];
  for (var n in Object(e))
    Cr.call(e, n) && n != "constructor" && t.push(n);
  return t;
}
function Ce(e) {
  return Pt(e) ? Ct(e) : jr(e);
}
function Er(e) {
  var t = [];
  if (e != null)
    for (var n in Object(e))
      t.push(n);
  return t;
}
var Ir = Object.prototype, Mr = Ir.hasOwnProperty;
function Fr(e) {
  if (!Z(e))
    return Er(e);
  var t = wt(e), n = [];
  for (var r in e)
    r == "constructor" && (t || !Mr.call(e, r)) || n.push(r);
  return n;
}
function Rr(e) {
  return Pt(e) ? Ct(e, !0) : Fr(e);
}
var Lr = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/, Dr = /^\w*$/;
function je(e, t) {
  if (x(e))
    return !1;
  var n = typeof e;
  return n == "number" || n == "symbol" || n == "boolean" || e == null || Pe(e) ? !0 : Dr.test(e) || !Lr.test(e) || t != null && e in Object(t);
}
var X = K(Object, "create");
function Nr() {
  this.__data__ = X ? X(null) : {}, this.size = 0;
}
function Kr(e) {
  var t = this.has(e) && delete this.__data__[e];
  return this.size -= t ? 1 : 0, t;
}
var Ur = "__lodash_hash_undefined__", Gr = Object.prototype, Br = Gr.hasOwnProperty;
function zr(e) {
  var t = this.__data__;
  if (X) {
    var n = t[e];
    return n === Ur ? void 0 : n;
  }
  return Br.call(t, e) ? t[e] : void 0;
}
var Hr = Object.prototype, Xr = Hr.hasOwnProperty;
function Jr(e) {
  var t = this.__data__;
  return X ? t[e] !== void 0 : Xr.call(t, e);
}
var qr = "__lodash_hash_undefined__";
function Zr(e, t) {
  var n = this.__data__;
  return this.size += this.has(e) ? 0 : 1, n[e] = X && t === void 0 ? qr : t, this;
}
function L(e) {
  var t = -1, n = e == null ? 0 : e.length;
  for (this.clear(); ++t < n; ) {
    var r = e[t];
    this.set(r[0], r[1]);
  }
}
L.prototype.clear = Nr;
L.prototype.delete = Kr;
L.prototype.get = zr;
L.prototype.has = Jr;
L.prototype.set = Zr;
function Yr() {
  this.__data__ = [], this.size = 0;
}
function ce(e, t) {
  for (var n = e.length; n--; )
    if (Ae(e[n][0], t))
      return n;
  return -1;
}
var Wr = Array.prototype, Qr = Wr.splice;
function Vr(e) {
  var t = this.__data__, n = ce(t, e);
  if (n < 0)
    return !1;
  var r = t.length - 1;
  return n == r ? t.pop() : Qr.call(t, n, 1), --this.size, !0;
}
function kr(e) {
  var t = this.__data__, n = ce(t, e);
  return n < 0 ? void 0 : t[n][1];
}
function ei(e) {
  return ce(this.__data__, e) > -1;
}
function ti(e, t) {
  var n = this.__data__, r = ce(n, e);
  return r < 0 ? (++this.size, n.push([e, t])) : n[r][1] = t, this;
}
function M(e) {
  var t = -1, n = e == null ? 0 : e.length;
  for (this.clear(); ++t < n; ) {
    var r = e[t];
    this.set(r[0], r[1]);
  }
}
M.prototype.clear = Yr;
M.prototype.delete = Vr;
M.prototype.get = kr;
M.prototype.has = ei;
M.prototype.set = ti;
var J = K(E, "Map");
function ni() {
  this.size = 0, this.__data__ = {
    hash: new L(),
    map: new (J || M)(),
    string: new L()
  };
}
function ri(e) {
  var t = typeof e;
  return t == "string" || t == "number" || t == "symbol" || t == "boolean" ? e !== "__proto__" : e === null;
}
function fe(e, t) {
  var n = e.__data__;
  return ri(t) ? n[typeof t == "string" ? "string" : "hash"] : n.map;
}
function ii(e) {
  var t = fe(this, e).delete(e);
  return this.size -= t ? 1 : 0, t;
}
function oi(e) {
  return fe(this, e).get(e);
}
function ai(e) {
  return fe(this, e).has(e);
}
function si(e, t) {
  var n = fe(this, e), r = n.size;
  return n.set(e, t), this.size += n.size == r ? 0 : 1, this;
}
function F(e) {
  var t = -1, n = e == null ? 0 : e.length;
  for (this.clear(); ++t < n; ) {
    var r = e[t];
    this.set(r[0], r[1]);
  }
}
F.prototype.clear = ni;
F.prototype.delete = ii;
F.prototype.get = oi;
F.prototype.has = ai;
F.prototype.set = si;
var ui = "Expected a function";
function Ee(e, t) {
  if (typeof e != "function" || t != null && typeof t != "function")
    throw new TypeError(ui);
  var n = function() {
    var r = arguments, i = t ? t.apply(this, r) : r[0], o = n.cache;
    if (o.has(i))
      return o.get(i);
    var a = e.apply(this, r);
    return n.cache = o.set(i, a) || o, a;
  };
  return n.cache = new (Ee.Cache || F)(), n;
}
Ee.Cache = F;
var li = 500;
function ci(e) {
  var t = Ee(e, function(r) {
    return n.size === li && n.clear(), r;
  }), n = t.cache;
  return t;
}
var fi = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g, pi = /\\(\\)?/g, gi = ci(function(e) {
  var t = [];
  return e.charCodeAt(0) === 46 && t.push(""), e.replace(fi, function(n, r, i, o) {
    t.push(i ? o.replace(pi, "$1") : r || n);
  }), t;
});
function di(e) {
  return e == null ? "" : yt(e);
}
function pe(e, t) {
  return x(e) ? e : je(e, t) ? [e] : gi(di(e));
}
function Y(e) {
  if (typeof e == "string" || Pe(e))
    return e;
  var t = e + "";
  return t == "0" && 1 / e == -1 / 0 ? "-0" : t;
}
function Ie(e, t) {
  t = pe(t, e);
  for (var n = 0, r = t.length; e != null && n < r; )
    e = e[Y(t[n++])];
  return n && n == r ? e : void 0;
}
function _i(e, t, n) {
  var r = e == null ? void 0 : Ie(e, t);
  return r === void 0 ? n : r;
}
function Me(e, t) {
  for (var n = -1, r = t.length, i = e.length; ++n < r; )
    e[i + n] = t[n];
  return e;
}
var Ze = A ? A.isConcatSpreadable : void 0;
function bi(e) {
  return x(e) || $e(e) || !!(Ze && e && e[Ze]);
}
function hi(e, t, n, r, i) {
  var o = -1, a = e.length;
  for (n || (n = bi), i || (i = []); ++o < a; ) {
    var s = e[o];
    n(s) ? Me(i, s) : i[i.length] = s;
  }
  return i;
}
function yi(e) {
  var t = e == null ? 0 : e.length;
  return t ? hi(e) : [];
}
function mi(e) {
  return Ln(zn(e, void 0, yi), e + "");
}
var Et = jt(Object.getPrototypeOf, Object), vi = "[object Object]", Ti = Function.prototype, Oi = Object.prototype, It = Ti.toString, Pi = Oi.hasOwnProperty, wi = It.call(Object);
function ye(e) {
  if (!I(e) || D(e) != vi)
    return !1;
  var t = Et(e);
  if (t === null)
    return !0;
  var n = Pi.call(t, "constructor") && t.constructor;
  return typeof n == "function" && n instanceof n && It.call(n) == wi;
}
function Ai(e, t, n) {
  var r = -1, i = e.length;
  t < 0 && (t = -t > i ? 0 : i + t), n = n > i ? i : n, n < 0 && (n += i), i = t > n ? 0 : n - t >>> 0, t >>>= 0;
  for (var o = Array(i); ++r < i; )
    o[r] = e[r + t];
  return o;
}
function Si() {
  this.__data__ = new M(), this.size = 0;
}
function $i(e) {
  var t = this.__data__, n = t.delete(e);
  return this.size = t.size, n;
}
function xi(e) {
  return this.__data__.get(e);
}
function Ci(e) {
  return this.__data__.has(e);
}
var ji = 200;
function Ei(e, t) {
  var n = this.__data__;
  if (n instanceof M) {
    var r = n.__data__;
    if (!J || r.length < ji - 1)
      return r.push([e, t]), this.size = ++n.size, this;
    n = this.__data__ = new F(r);
  }
  return n.set(e, t), this.size = n.size, this;
}
function j(e) {
  var t = this.__data__ = new M(e);
  this.size = t.size;
}
j.prototype.clear = Si;
j.prototype.delete = $i;
j.prototype.get = xi;
j.prototype.has = Ci;
j.prototype.set = Ei;
var Mt = typeof exports == "object" && exports && !exports.nodeType && exports, Ye = Mt && typeof module == "object" && module && !module.nodeType && module, Ii = Ye && Ye.exports === Mt, We = Ii ? E.Buffer : void 0;
We && We.allocUnsafe;
function Mi(e, t) {
  return e.slice();
}
function Fi(e, t) {
  for (var n = -1, r = e == null ? 0 : e.length, i = 0, o = []; ++n < r; ) {
    var a = e[n];
    t(a, n, e) && (o[i++] = a);
  }
  return o;
}
function Ft() {
  return [];
}
var Ri = Object.prototype, Li = Ri.propertyIsEnumerable, Qe = Object.getOwnPropertySymbols, Rt = Qe ? function(e) {
  return e == null ? [] : (e = Object(e), Fi(Qe(e), function(t) {
    return Li.call(e, t);
  }));
} : Ft, Di = Object.getOwnPropertySymbols, Ni = Di ? function(e) {
  for (var t = []; e; )
    Me(t, Rt(e)), e = Et(e);
  return t;
} : Ft;
function Lt(e, t, n) {
  var r = t(e);
  return x(e) ? r : Me(r, n(e));
}
function Ve(e) {
  return Lt(e, Ce, Rt);
}
function Dt(e) {
  return Lt(e, Rr, Ni);
}
var me = K(E, "DataView"), ve = K(E, "Promise"), Te = K(E, "Set"), ke = "[object Map]", Ki = "[object Object]", et = "[object Promise]", tt = "[object Set]", nt = "[object WeakMap]", rt = "[object DataView]", Ui = N(me), Gi = N(J), Bi = N(ve), zi = N(Te), Hi = N(he), $ = D;
(me && $(new me(new ArrayBuffer(1))) != rt || J && $(new J()) != ke || ve && $(ve.resolve()) != et || Te && $(new Te()) != tt || he && $(new he()) != nt) && ($ = function(e) {
  var t = D(e), n = t == Ki ? e.constructor : void 0, r = n ? N(n) : "";
  if (r)
    switch (r) {
      case Ui:
        return rt;
      case Gi:
        return ke;
      case Bi:
        return et;
      case zi:
        return tt;
      case Hi:
        return nt;
    }
  return t;
});
var Xi = Object.prototype, Ji = Xi.hasOwnProperty;
function qi(e) {
  var t = e.length, n = new e.constructor(t);
  return t && typeof e[0] == "string" && Ji.call(e, "index") && (n.index = e.index, n.input = e.input), n;
}
var se = E.Uint8Array;
function Fe(e) {
  var t = new e.constructor(e.byteLength);
  return new se(t).set(new se(e)), t;
}
function Zi(e, t) {
  var n = Fe(e.buffer);
  return new e.constructor(n, e.byteOffset, e.byteLength);
}
var Yi = /\w*$/;
function Wi(e) {
  var t = new e.constructor(e.source, Yi.exec(e));
  return t.lastIndex = e.lastIndex, t;
}
var it = A ? A.prototype : void 0, ot = it ? it.valueOf : void 0;
function Qi(e) {
  return ot ? Object(ot.call(e)) : {};
}
function Vi(e, t) {
  var n = Fe(e.buffer);
  return new e.constructor(n, e.byteOffset, e.length);
}
var ki = "[object Boolean]", eo = "[object Date]", to = "[object Map]", no = "[object Number]", ro = "[object RegExp]", io = "[object Set]", oo = "[object String]", ao = "[object Symbol]", so = "[object ArrayBuffer]", uo = "[object DataView]", lo = "[object Float32Array]", co = "[object Float64Array]", fo = "[object Int8Array]", po = "[object Int16Array]", go = "[object Int32Array]", _o = "[object Uint8Array]", bo = "[object Uint8ClampedArray]", ho = "[object Uint16Array]", yo = "[object Uint32Array]";
function mo(e, t, n) {
  var r = e.constructor;
  switch (t) {
    case so:
      return Fe(e);
    case ki:
    case eo:
      return new r(+e);
    case uo:
      return Zi(e);
    case lo:
    case co:
    case fo:
    case po:
    case go:
    case _o:
    case bo:
    case ho:
    case yo:
      return Vi(e);
    case to:
      return new r();
    case no:
    case oo:
      return new r(e);
    case ro:
      return Wi(e);
    case io:
      return new r();
    case ao:
      return Qi(e);
  }
}
var vo = "[object Map]";
function To(e) {
  return I(e) && $(e) == vo;
}
var at = B && B.isMap, Oo = at ? xe(at) : To, Po = "[object Set]";
function wo(e) {
  return I(e) && $(e) == Po;
}
var st = B && B.isSet, Ao = st ? xe(st) : wo, Nt = "[object Arguments]", So = "[object Array]", $o = "[object Boolean]", xo = "[object Date]", Co = "[object Error]", Kt = "[object Function]", jo = "[object GeneratorFunction]", Eo = "[object Map]", Io = "[object Number]", Ut = "[object Object]", Mo = "[object RegExp]", Fo = "[object Set]", Ro = "[object String]", Lo = "[object Symbol]", Do = "[object WeakMap]", No = "[object ArrayBuffer]", Ko = "[object DataView]", Uo = "[object Float32Array]", Go = "[object Float64Array]", Bo = "[object Int8Array]", zo = "[object Int16Array]", Ho = "[object Int32Array]", Xo = "[object Uint8Array]", Jo = "[object Uint8ClampedArray]", qo = "[object Uint16Array]", Zo = "[object Uint32Array]", h = {};
h[Nt] = h[So] = h[No] = h[Ko] = h[$o] = h[xo] = h[Uo] = h[Go] = h[Bo] = h[zo] = h[Ho] = h[Eo] = h[Io] = h[Ut] = h[Mo] = h[Fo] = h[Ro] = h[Lo] = h[Xo] = h[Jo] = h[qo] = h[Zo] = !0;
h[Co] = h[Kt] = h[Do] = !1;
function re(e, t, n, r, i, o) {
  var a;
  if (n && (a = i ? n(e, r, i, o) : n(e)), a !== void 0)
    return a;
  if (!Z(e))
    return e;
  var s = x(e);
  if (s)
    a = qi(e);
  else {
    var u = $(e), l = u == Kt || u == jo;
    if (ae(e))
      return Mi(e);
    if (u == Ut || u == Nt || l && !i)
      a = {};
    else {
      if (!h[u])
        return i ? e : {};
      a = mo(e, u);
    }
  }
  o || (o = new j());
  var c = o.get(e);
  if (c)
    return c;
  o.set(e, a), Ao(e) ? e.forEach(function(p) {
    a.add(re(p, t, n, p, e, o));
  }) : Oo(e) && e.forEach(function(p, _) {
    a.set(_, re(p, t, n, _, e, o));
  });
  var b = Dt, f = s ? void 0 : b(e);
  return Dn(f || e, function(p, _) {
    f && (_ = p, p = e[_]), Ot(a, _, re(p, t, n, _, e, o));
  }), a;
}
var Yo = "__lodash_hash_undefined__";
function Wo(e) {
  return this.__data__.set(e, Yo), this;
}
function Qo(e) {
  return this.__data__.has(e);
}
function ue(e) {
  var t = -1, n = e == null ? 0 : e.length;
  for (this.__data__ = new F(); ++t < n; )
    this.add(e[t]);
}
ue.prototype.add = ue.prototype.push = Wo;
ue.prototype.has = Qo;
function Vo(e, t) {
  for (var n = -1, r = e == null ? 0 : e.length; ++n < r; )
    if (t(e[n], n, e))
      return !0;
  return !1;
}
function ko(e, t) {
  return e.has(t);
}
var ea = 1, ta = 2;
function Gt(e, t, n, r, i, o) {
  var a = n & ea, s = e.length, u = t.length;
  if (s != u && !(a && u > s))
    return !1;
  var l = o.get(e), c = o.get(t);
  if (l && c)
    return l == t && c == e;
  var b = -1, f = !0, p = n & ta ? new ue() : void 0;
  for (o.set(e, t), o.set(t, e); ++b < s; ) {
    var _ = e[b], y = t[b];
    if (r)
      var d = a ? r(y, _, b, t, e, o) : r(_, y, b, e, t, o);
    if (d !== void 0) {
      if (d)
        continue;
      f = !1;
      break;
    }
    if (p) {
      if (!Vo(t, function(v, T) {
        if (!ko(p, T) && (_ === v || i(_, v, n, r, o)))
          return p.push(T);
      })) {
        f = !1;
        break;
      }
    } else if (!(_ === y || i(_, y, n, r, o))) {
      f = !1;
      break;
    }
  }
  return o.delete(e), o.delete(t), f;
}
function na(e) {
  var t = -1, n = Array(e.size);
  return e.forEach(function(r, i) {
    n[++t] = [i, r];
  }), n;
}
function ra(e) {
  var t = -1, n = Array(e.size);
  return e.forEach(function(r) {
    n[++t] = r;
  }), n;
}
var ia = 1, oa = 2, aa = "[object Boolean]", sa = "[object Date]", ua = "[object Error]", la = "[object Map]", ca = "[object Number]", fa = "[object RegExp]", pa = "[object Set]", ga = "[object String]", da = "[object Symbol]", _a = "[object ArrayBuffer]", ba = "[object DataView]", ut = A ? A.prototype : void 0, be = ut ? ut.valueOf : void 0;
function ha(e, t, n, r, i, o, a) {
  switch (n) {
    case ba:
      if (e.byteLength != t.byteLength || e.byteOffset != t.byteOffset)
        return !1;
      e = e.buffer, t = t.buffer;
    case _a:
      return !(e.byteLength != t.byteLength || !o(new se(e), new se(t)));
    case aa:
    case sa:
    case ca:
      return Ae(+e, +t);
    case ua:
      return e.name == t.name && e.message == t.message;
    case fa:
    case ga:
      return e == t + "";
    case la:
      var s = na;
    case pa:
      var u = r & ia;
      if (s || (s = ra), e.size != t.size && !u)
        return !1;
      var l = a.get(e);
      if (l)
        return l == t;
      r |= oa, a.set(e, t);
      var c = Gt(s(e), s(t), r, i, o, a);
      return a.delete(e), c;
    case da:
      if (be)
        return be.call(e) == be.call(t);
  }
  return !1;
}
var ya = 1, ma = Object.prototype, va = ma.hasOwnProperty;
function Ta(e, t, n, r, i, o) {
  var a = n & ya, s = Ve(e), u = s.length, l = Ve(t), c = l.length;
  if (u != c && !a)
    return !1;
  for (var b = u; b--; ) {
    var f = s[b];
    if (!(a ? f in t : va.call(t, f)))
      return !1;
  }
  var p = o.get(e), _ = o.get(t);
  if (p && _)
    return p == t && _ == e;
  var y = !0;
  o.set(e, t), o.set(t, e);
  for (var d = a; ++b < u; ) {
    f = s[b];
    var v = e[f], T = t[f];
    if (r)
      var P = a ? r(T, v, f, t, e, o) : r(v, T, f, e, t, o);
    if (!(P === void 0 ? v === T || i(v, T, n, r, o) : P)) {
      y = !1;
      break;
    }
    d || (d = f == "constructor");
  }
  if (y && !d) {
    var C = e.constructor, S = t.constructor;
    C != S && "constructor" in e && "constructor" in t && !(typeof C == "function" && C instanceof C && typeof S == "function" && S instanceof S) && (y = !1);
  }
  return o.delete(e), o.delete(t), y;
}
var Oa = 1, lt = "[object Arguments]", ct = "[object Array]", te = "[object Object]", Pa = Object.prototype, ft = Pa.hasOwnProperty;
function wa(e, t, n, r, i, o) {
  var a = x(e), s = x(t), u = a ? ct : $(e), l = s ? ct : $(t);
  u = u == lt ? te : u, l = l == lt ? te : l;
  var c = u == te, b = l == te, f = u == l;
  if (f && ae(e)) {
    if (!ae(t))
      return !1;
    a = !0, c = !1;
  }
  if (f && !c)
    return o || (o = new j()), a || xt(e) ? Gt(e, t, n, r, i, o) : ha(e, t, u, n, r, i, o);
  if (!(n & Oa)) {
    var p = c && ft.call(e, "__wrapped__"), _ = b && ft.call(t, "__wrapped__");
    if (p || _) {
      var y = p ? e.value() : e, d = _ ? t.value() : t;
      return o || (o = new j()), i(y, d, n, r, o);
    }
  }
  return f ? (o || (o = new j()), Ta(e, t, n, r, i, o)) : !1;
}
function Re(e, t, n, r, i) {
  return e === t ? !0 : e == null || t == null || !I(e) && !I(t) ? e !== e && t !== t : wa(e, t, n, r, Re, i);
}
var Aa = 1, Sa = 2;
function $a(e, t, n, r) {
  var i = n.length, o = i;
  if (e == null)
    return !o;
  for (e = Object(e); i--; ) {
    var a = n[i];
    if (a[2] ? a[1] !== e[a[0]] : !(a[0] in e))
      return !1;
  }
  for (; ++i < o; ) {
    a = n[i];
    var s = a[0], u = e[s], l = a[1];
    if (a[2]) {
      if (u === void 0 && !(s in e))
        return !1;
    } else {
      var c = new j(), b;
      if (!(b === void 0 ? Re(l, u, Aa | Sa, r, c) : b))
        return !1;
    }
  }
  return !0;
}
function Bt(e) {
  return e === e && !Z(e);
}
function xa(e) {
  for (var t = Ce(e), n = t.length; n--; ) {
    var r = t[n], i = e[r];
    t[n] = [r, i, Bt(i)];
  }
  return t;
}
function zt(e, t) {
  return function(n) {
    return n == null ? !1 : n[e] === t && (t !== void 0 || e in Object(n));
  };
}
function Ca(e) {
  var t = xa(e);
  return t.length == 1 && t[0][2] ? zt(t[0][0], t[0][1]) : function(n) {
    return n === e || $a(n, e, t);
  };
}
function ja(e, t) {
  return e != null && t in Object(e);
}
function Ea(e, t, n) {
  t = pe(t, e);
  for (var r = -1, i = t.length, o = !1; ++r < i; ) {
    var a = Y(t[r]);
    if (!(o = e != null && n(e, a)))
      break;
    e = e[a];
  }
  return o || ++r != i ? o : (i = e == null ? 0 : e.length, !!i && Se(i) && Tt(a, i) && (x(e) || $e(e)));
}
function Ia(e, t) {
  return e != null && Ea(e, t, ja);
}
var Ma = 1, Fa = 2;
function Ra(e, t) {
  return je(e) && Bt(t) ? zt(Y(e), t) : function(n) {
    var r = _i(n, e);
    return r === void 0 && r === t ? Ia(n, e) : Re(t, r, Ma | Fa);
  };
}
function La(e) {
  return function(t) {
    return t == null ? void 0 : t[e];
  };
}
function Da(e) {
  return function(t) {
    return Ie(t, e);
  };
}
function Na(e) {
  return je(e) ? La(Y(e)) : Da(e);
}
function Ka(e) {
  return typeof e == "function" ? e : e == null ? mt : typeof e == "object" ? x(e) ? Ra(e[0], e[1]) : Ca(e) : Na(e);
}
function Ua(e) {
  return function(t, n, r) {
    for (var i = -1, o = Object(t), a = r(t), s = a.length; s--; ) {
      var u = a[++i];
      if (n(o[u], u, o) === !1)
        break;
    }
    return t;
  };
}
var Ga = Ua();
function Ba(e, t) {
  return e && Ga(e, t, Ce);
}
function za(e) {
  var t = e == null ? 0 : e.length;
  return t ? e[t - 1] : void 0;
}
function Ha(e, t) {
  return t.length < 2 ? e : Ie(e, Ai(t, 0, -1));
}
function Xa(e, t) {
  var n = {};
  return t = Ka(t), Ba(e, function(r, i, o) {
    we(n, t(r, i, o), r);
  }), n;
}
function Ja(e, t) {
  return t = pe(t, e), e = Ha(e, t), e == null || delete e[Y(za(t))];
}
function qa(e) {
  return ye(e) ? void 0 : e;
}
var Za = 1, Ya = 2, Wa = 4, Ht = mi(function(e, t) {
  var n = {};
  if (e == null)
    return n;
  var r = !1;
  t = ht(t, function(o) {
    return o = pe(o, e), r || (r = o.length > 1), o;
  }), Bn(e, Dt(e), n), r && (n = re(n, Za | Ya | Wa, qa));
  for (var i = t.length; i--; )
    Ja(n, t[i]);
  return n;
});
function Qa(e) {
  return e.replace(/(^|_)(\w)/g, (t, n, r, i) => i === 0 ? r.toLowerCase() : r.toUpperCase());
}
async function Va() {
  window.ms_globals || (window.ms_globals = {}), window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((e) => {
    window.ms_globals.initialize = () => {
      e();
    };
  })), await window.ms_globals.initializePromise;
}
async function ka(e) {
  return await Va(), e().then((t) => t.default);
}
const Xt = [
  "interactive",
  "gradio",
  "server",
  "target",
  "theme_mode",
  "root",
  "name",
  // 'visible',
  // 'elem_id',
  // 'elem_classes',
  // 'elem_style',
  "_internal",
  "props",
  // 'value',
  "_selectable",
  "loading_status",
  "value_is_output"
], es = Xt.concat(["attached_events"]);
function ts(e, t = {}, n = !1) {
  return Xa(Ht(e, n ? [] : Xt), (r, i) => t[i] || Qa(i));
}
function ns(e, t) {
  const {
    gradio: n,
    _internal: r,
    restProps: i,
    originalRestProps: o,
    ...a
  } = e, s = (i == null ? void 0 : i.attachedEvents) || [];
  return {
    ...Array.from(/* @__PURE__ */ new Set([...Object.keys(r).map((u) => {
      const l = u.match(/bind_(.+)_event/);
      return l && l[1] ? l[1] : null;
    }).filter(Boolean), ...s.map((u) => u)])).reduce((u, l) => {
      const c = l.split("_"), b = (...p) => {
        const _ = p.map((d) => p && typeof d == "object" && (d.nativeEvent || d instanceof Event) ? {
          type: d.type,
          detail: d.detail,
          timestamp: d.timeStamp,
          clientX: d.clientX,
          clientY: d.clientY,
          targetId: d.target.id,
          targetClassName: d.target.className,
          altKey: d.altKey,
          ctrlKey: d.ctrlKey,
          shiftKey: d.shiftKey,
          metaKey: d.metaKey
        } : d);
        let y;
        try {
          y = JSON.parse(JSON.stringify(_));
        } catch {
          let d = function(v) {
            try {
              return JSON.stringify(v), v;
            } catch {
              return ye(v) ? Object.fromEntries(Object.entries(v).map(([T, P]) => {
                try {
                  return JSON.stringify(P), [T, P];
                } catch {
                  return ye(P) ? [T, Object.fromEntries(Object.entries(P).filter(([C, S]) => {
                    try {
                      return JSON.stringify(S), !0;
                    } catch {
                      return !1;
                    }
                  }))] : null;
                }
              }).filter(Boolean)) : {};
            }
          };
          y = _.map((v) => d(v));
        }
        return n.dispatch(l.replace(/[A-Z]/g, (d) => "_" + d.toLowerCase()), {
          payload: y,
          component: {
            ...a,
            ...Ht(o, es)
          }
        });
      };
      if (c.length > 1) {
        let p = {
          ...a.props[c[0]] || (i == null ? void 0 : i[c[0]]) || {}
        };
        u[c[0]] = p;
        for (let y = 1; y < c.length - 1; y++) {
          const d = {
            ...a.props[c[y]] || (i == null ? void 0 : i[c[y]]) || {}
          };
          p[c[y]] = d, p = d;
        }
        const _ = c[c.length - 1];
        return p[`on${_.slice(0, 1).toUpperCase()}${_.slice(1)}`] = b, u;
      }
      const f = c[0];
      return u[`on${f.slice(0, 1).toUpperCase()}${f.slice(1)}`] = b, u;
    }, {}),
    __render_eventProps: {
      props: e,
      eventsMapping: t
    }
  };
}
function ie() {
}
function rs(e, ...t) {
  if (e == null) {
    for (const r of t) r(void 0);
    return ie;
  }
  const n = e.subscribe(...t);
  return n.unsubscribe ? () => n.unsubscribe() : n;
}
function Jt(e) {
  let t;
  return rs(e, (n) => t = n)(), t;
}
const U = [];
function R(e, t = ie) {
  let n;
  const r = /* @__PURE__ */ new Set();
  function i(a) {
    if (u = a, ((s = e) != s ? u == u : s !== u || s && typeof s == "object" || typeof s == "function") && (e = a, n)) {
      const l = !U.length;
      for (const c of r) c[1](), U.push(c, e);
      if (l) {
        for (let c = 0; c < U.length; c += 2) U[c][0](U[c + 1]);
        U.length = 0;
      }
    }
    var s, u;
  }
  function o(a) {
    i(a(e));
  }
  return {
    set: i,
    update: o,
    subscribe: function(a, s = ie) {
      const u = [a, s];
      return r.add(u), r.size === 1 && (n = t(i, o) || ie), a(e), () => {
        r.delete(u), r.size === 0 && n && (n(), n = null);
      };
    }
  };
}
const {
  getContext: is,
  setContext: Bs
} = window.__gradio__svelte__internal, os = "$$ms-gr-loading-status-key";
function as() {
  const e = window.ms_globals.loadingKey++, t = is(os);
  return (n) => {
    if (!t || !n)
      return;
    const {
      loadingStatusMap: r,
      options: i
    } = t, {
      generating: o,
      error: a
    } = Jt(i);
    (n == null ? void 0 : n.status) === "pending" || a && (n == null ? void 0 : n.status) === "error" || (o && (n == null ? void 0 : n.status)) === "generating" ? r.update(({
      map: s
    }) => (s.set(e, n), {
      map: s
    })) : r.update(({
      map: s
    }) => (s.delete(e), {
      map: s
    }));
  };
}
const {
  getContext: ge,
  setContext: W
} = window.__gradio__svelte__internal, ss = "$$ms-gr-slots-key";
function us() {
  const e = R({});
  return W(ss, e);
}
const qt = "$$ms-gr-slot-params-mapping-fn-key";
function ls() {
  return ge(qt);
}
function cs(e) {
  return W(qt, R(e));
}
const Zt = "$$ms-gr-sub-index-context-key";
function fs() {
  return ge(Zt) || null;
}
function pt(e) {
  return W(Zt, e);
}
function ps(e, t, n) {
  if (!Reflect.has(e, "as_item") || !Reflect.has(e, "_internal"))
    throw new Error("`as_item` and `_internal` is required");
  const r = Wt(), i = ls();
  cs().set(void 0);
  const a = ds({
    slot: void 0,
    index: e._internal.index,
    subIndex: e._internal.subIndex
  }), s = fs();
  typeof s == "number" && pt(void 0);
  const u = as();
  typeof e._internal.subIndex == "number" && pt(e._internal.subIndex), r && r.subscribe((f) => {
    a.slotKey.set(f);
  }), gs();
  const l = e.as_item, c = (f, p) => f ? {
    ...ts({
      ...f
    }, t),
    __render_slotParamsMappingFn: i ? Jt(i) : void 0,
    __render_as_item: p,
    __render_restPropsMapping: t
  } : void 0, b = R({
    ...e,
    _internal: {
      ...e._internal,
      index: s ?? e._internal.index
    },
    restProps: c(e.restProps, l),
    originalRestProps: e.restProps
  });
  return i && i.subscribe((f) => {
    b.update((p) => ({
      ...p,
      restProps: {
        ...p.restProps,
        __slotParamsMappingFn: f
      }
    }));
  }), [b, (f) => {
    var p;
    u((p = f.restProps) == null ? void 0 : p.loading_status), b.set({
      ...f,
      _internal: {
        ...f._internal,
        index: s ?? f._internal.index
      },
      restProps: c(f.restProps, f.as_item),
      originalRestProps: f.restProps
    });
  }];
}
const Yt = "$$ms-gr-slot-key";
function gs() {
  W(Yt, R(void 0));
}
function Wt() {
  return ge(Yt);
}
const Qt = "$$ms-gr-component-slot-context-key";
function ds({
  slot: e,
  index: t,
  subIndex: n
}) {
  return W(Qt, {
    slotKey: R(e),
    slotIndex: R(t),
    subSlotIndex: R(n)
  });
}
function zs() {
  return ge(Qt);
}
function _s(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e;
}
var Vt = {
  exports: {}
};
/*!
	Copyright (c) 2018 Jed Watson.
	Licensed under the MIT License (MIT), see
	http://jedwatson.github.io/classnames
*/
(function(e) {
  (function() {
    var t = {}.hasOwnProperty;
    function n() {
      for (var o = "", a = 0; a < arguments.length; a++) {
        var s = arguments[a];
        s && (o = i(o, r(s)));
      }
      return o;
    }
    function r(o) {
      if (typeof o == "string" || typeof o == "number")
        return o;
      if (typeof o != "object")
        return "";
      if (Array.isArray(o))
        return n.apply(null, o);
      if (o.toString !== Object.prototype.toString && !o.toString.toString().includes("[native code]"))
        return o.toString();
      var a = "";
      for (var s in o)
        t.call(o, s) && o[s] && (a = i(a, s));
      return a;
    }
    function i(o, a) {
      return a ? o ? o + " " + a : o + a : o;
    }
    e.exports ? (n.default = n, e.exports = n) : window.classNames = n;
  })();
})(Vt);
var bs = Vt.exports;
const hs = /* @__PURE__ */ _s(bs), {
  SvelteComponent: ys,
  assign: Oe,
  check_outros: ms,
  claim_component: vs,
  component_subscribe: ne,
  compute_rest_props: gt,
  create_component: Ts,
  create_slot: Os,
  destroy_component: Ps,
  detach: kt,
  empty: le,
  exclude_internal_props: ws,
  flush: w,
  get_all_dirty_from_scope: As,
  get_slot_changes: Ss,
  get_spread_object: $s,
  get_spread_update: xs,
  group_outros: Cs,
  handle_promise: js,
  init: Es,
  insert_hydration: en,
  mount_component: Is,
  noop: O,
  safe_not_equal: Ms,
  transition_in: G,
  transition_out: q,
  update_await_block_branch: Fs,
  update_slot_base: Rs
} = window.__gradio__svelte__internal;
function Ls(e) {
  return {
    c: O,
    l: O,
    m: O,
    p: O,
    i: O,
    o: O,
    d: O
  };
}
function Ds(e) {
  let t, n;
  const r = [
    /*itemProps*/
    e[1].props,
    {
      slots: (
        /*itemProps*/
        e[1].slots
      )
    },
    {
      itemIndex: (
        /*$mergedProps*/
        e[0]._internal.index || 0
      )
    },
    {
      itemSlotKey: (
        /*$slotKey*/
        e[2]
      )
    }
  ];
  let i = {
    $$slots: {
      default: [Ns]
    },
    $$scope: {
      ctx: e
    }
  };
  for (let o = 0; o < r.length; o += 1)
    i = Oe(i, r[o]);
  return t = new /*MentionsOption*/
  e[26]({
    props: i
  }), {
    c() {
      Ts(t.$$.fragment);
    },
    l(o) {
      vs(t.$$.fragment, o);
    },
    m(o, a) {
      Is(t, o, a), n = !0;
    },
    p(o, a) {
      const s = a & /*itemProps, $mergedProps, $slotKey*/
      7 ? xs(r, [a & /*itemProps*/
      2 && $s(
        /*itemProps*/
        o[1].props
      ), a & /*itemProps*/
      2 && {
        slots: (
          /*itemProps*/
          o[1].slots
        )
      }, a & /*$mergedProps*/
      1 && {
        itemIndex: (
          /*$mergedProps*/
          o[0]._internal.index || 0
        )
      }, a & /*$slotKey*/
      4 && {
        itemSlotKey: (
          /*$slotKey*/
          o[2]
        )
      }]) : {};
      a & /*$$scope, $mergedProps*/
      8388609 && (s.$$scope = {
        dirty: a,
        ctx: o
      }), t.$set(s);
    },
    i(o) {
      n || (G(t.$$.fragment, o), n = !0);
    },
    o(o) {
      q(t.$$.fragment, o), n = !1;
    },
    d(o) {
      Ps(t, o);
    }
  };
}
function dt(e) {
  let t;
  const n = (
    /*#slots*/
    e[22].default
  ), r = Os(
    n,
    e,
    /*$$scope*/
    e[23],
    null
  );
  return {
    c() {
      r && r.c();
    },
    l(i) {
      r && r.l(i);
    },
    m(i, o) {
      r && r.m(i, o), t = !0;
    },
    p(i, o) {
      r && r.p && (!t || o & /*$$scope*/
      8388608) && Rs(
        r,
        n,
        i,
        /*$$scope*/
        i[23],
        t ? Ss(
          n,
          /*$$scope*/
          i[23],
          o,
          null
        ) : As(
          /*$$scope*/
          i[23]
        ),
        null
      );
    },
    i(i) {
      t || (G(r, i), t = !0);
    },
    o(i) {
      q(r, i), t = !1;
    },
    d(i) {
      r && r.d(i);
    }
  };
}
function Ns(e) {
  let t, n, r = (
    /*$mergedProps*/
    e[0].visible && dt(e)
  );
  return {
    c() {
      r && r.c(), t = le();
    },
    l(i) {
      r && r.l(i), t = le();
    },
    m(i, o) {
      r && r.m(i, o), en(i, t, o), n = !0;
    },
    p(i, o) {
      /*$mergedProps*/
      i[0].visible ? r ? (r.p(i, o), o & /*$mergedProps*/
      1 && G(r, 1)) : (r = dt(i), r.c(), G(r, 1), r.m(t.parentNode, t)) : r && (Cs(), q(r, 1, 1, () => {
        r = null;
      }), ms());
    },
    i(i) {
      n || (G(r), n = !0);
    },
    o(i) {
      q(r), n = !1;
    },
    d(i) {
      i && kt(t), r && r.d(i);
    }
  };
}
function Ks(e) {
  return {
    c: O,
    l: O,
    m: O,
    p: O,
    i: O,
    o: O,
    d: O
  };
}
function Us(e) {
  let t, n, r = {
    ctx: e,
    current: null,
    token: null,
    hasCatch: !1,
    pending: Ks,
    then: Ds,
    catch: Ls,
    value: 26,
    blocks: [, , ,]
  };
  return js(
    /*AwaitedMentionsOption*/
    e[3],
    r
  ), {
    c() {
      t = le(), r.block.c();
    },
    l(i) {
      t = le(), r.block.l(i);
    },
    m(i, o) {
      en(i, t, o), r.block.m(i, r.anchor = o), r.mount = () => t.parentNode, r.anchor = t, n = !0;
    },
    p(i, [o]) {
      e = i, Fs(r, e, o);
    },
    i(i) {
      n || (G(r.block), n = !0);
    },
    o(i) {
      for (let o = 0; o < 3; o += 1) {
        const a = r.blocks[o];
        q(a);
      }
      n = !1;
    },
    d(i) {
      i && kt(t), r.block.d(i), r.token = null, r = null;
    }
  };
}
function Gs(e, t, n) {
  let r;
  const i = ["gradio", "props", "_internal", "value", "label", "disabled", "key", "as_item", "visible", "elem_id", "elem_classes", "elem_style"];
  let o = gt(t, i), a, s, u, l, {
    $$slots: c = {},
    $$scope: b
  } = t;
  const f = ka(() => import("./mentions.option-D9zNzHOp.js"));
  let {
    gradio: p
  } = t, {
    props: _ = {}
  } = t;
  const y = R(_);
  ne(e, y, (g) => n(21, u = g));
  let {
    _internal: d = {}
  } = t, {
    value: v
  } = t, {
    label: T
  } = t, {
    disabled: P
  } = t, {
    key: C
  } = t, {
    as_item: S
  } = t, {
    visible: Q = !0
  } = t, {
    elem_id: V = ""
  } = t, {
    elem_classes: k = []
  } = t, {
    elem_style: ee = {}
  } = t;
  const Le = Wt();
  ne(e, Le, (g) => n(2, l = g));
  const [De, tn] = ps({
    gradio: p,
    props: u,
    _internal: d,
    visible: Q,
    elem_id: V,
    elem_classes: k,
    elem_style: ee,
    as_item: S,
    value: v,
    disabled: P,
    key: C,
    label: T,
    restProps: o
  });
  ne(e, De, (g) => n(0, s = g));
  const Ne = us();
  return ne(e, Ne, (g) => n(20, a = g)), e.$$set = (g) => {
    t = Oe(Oe({}, t), ws(g)), n(25, o = gt(t, i)), "gradio" in g && n(8, p = g.gradio), "props" in g && n(9, _ = g.props), "_internal" in g && n(10, d = g._internal), "value" in g && n(11, v = g.value), "label" in g && n(12, T = g.label), "disabled" in g && n(13, P = g.disabled), "key" in g && n(14, C = g.key), "as_item" in g && n(15, S = g.as_item), "visible" in g && n(16, Q = g.visible), "elem_id" in g && n(17, V = g.elem_id), "elem_classes" in g && n(18, k = g.elem_classes), "elem_style" in g && n(19, ee = g.elem_style), "$$scope" in g && n(23, b = g.$$scope);
  }, e.$$.update = () => {
    e.$$.dirty & /*props*/
    512 && y.update((g) => ({
      ...g,
      ..._
    })), tn({
      gradio: p,
      props: u,
      _internal: d,
      visible: Q,
      elem_id: V,
      elem_classes: k,
      elem_style: ee,
      as_item: S,
      value: v,
      disabled: P,
      key: C,
      label: T,
      restProps: o
    }), e.$$.dirty & /*$mergedProps, $slots*/
    1048577 && n(1, r = {
      props: {
        style: s.elem_style,
        className: hs(s.elem_classes, "ms-gr-antd-mentions-option"),
        id: s.elem_id,
        value: s.value,
        label: s.label,
        disabled: s.disabled,
        key: s.key,
        ...s.restProps,
        ...s.props,
        ...ns(s)
      },
      slots: a
    });
  }, [s, r, l, f, y, Le, De, Ne, p, _, d, v, T, P, C, S, Q, V, k, ee, a, u, c, b];
}
class Hs extends ys {
  constructor(t) {
    super(), Es(this, t, Gs, Us, Ms, {
      gradio: 8,
      props: 9,
      _internal: 10,
      value: 11,
      label: 12,
      disabled: 13,
      key: 14,
      as_item: 15,
      visible: 16,
      elem_id: 17,
      elem_classes: 18,
      elem_style: 19
    });
  }
  get gradio() {
    return this.$$.ctx[8];
  }
  set gradio(t) {
    this.$$set({
      gradio: t
    }), w();
  }
  get props() {
    return this.$$.ctx[9];
  }
  set props(t) {
    this.$$set({
      props: t
    }), w();
  }
  get _internal() {
    return this.$$.ctx[10];
  }
  set _internal(t) {
    this.$$set({
      _internal: t
    }), w();
  }
  get value() {
    return this.$$.ctx[11];
  }
  set value(t) {
    this.$$set({
      value: t
    }), w();
  }
  get label() {
    return this.$$.ctx[12];
  }
  set label(t) {
    this.$$set({
      label: t
    }), w();
  }
  get disabled() {
    return this.$$.ctx[13];
  }
  set disabled(t) {
    this.$$set({
      disabled: t
    }), w();
  }
  get key() {
    return this.$$.ctx[14];
  }
  set key(t) {
    this.$$set({
      key: t
    }), w();
  }
  get as_item() {
    return this.$$.ctx[15];
  }
  set as_item(t) {
    this.$$set({
      as_item: t
    }), w();
  }
  get visible() {
    return this.$$.ctx[16];
  }
  set visible(t) {
    this.$$set({
      visible: t
    }), w();
  }
  get elem_id() {
    return this.$$.ctx[17];
  }
  set elem_id(t) {
    this.$$set({
      elem_id: t
    }), w();
  }
  get elem_classes() {
    return this.$$.ctx[18];
  }
  set elem_classes(t) {
    this.$$set({
      elem_classes: t
    }), w();
  }
  get elem_style() {
    return this.$$.ctx[19];
  }
  set elem_style(t) {
    this.$$set({
      elem_style: t
    }), w();
  }
}
export {
  Hs as I,
  R as Z,
  zs as g
};
