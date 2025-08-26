var cn = Object.defineProperty;
var Ne = (e) => {
  throw TypeError(e);
};
var fn = (e, t, n) => t in e ? cn(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n;
var $ = (e, t, n) => fn(e, typeof t != "symbol" ? t + "" : t, n), Ke = (e, t, n) => t.has(e) || Ne("Cannot " + n);
var z = (e, t, n) => (Ke(e, t, "read from private field"), n ? n.call(e) : t.get(e)), Ue = (e, t, n) => t.has(e) ? Ne("Cannot add the same private member more than once") : t instanceof WeakSet ? t.add(e) : t.set(e, n), Ge = (e, t, n, r) => (Ke(e, t, "write to private field"), r ? r.call(e, n) : t.set(e, n), n);
var vt = typeof global == "object" && global && global.Object === Object && global, pn = typeof self == "object" && self && self.Object === Object && self, I = vt || pn || Function("return this")(), O = I.Symbol, Tt = Object.prototype, gn = Tt.hasOwnProperty, dn = Tt.toString, J = O ? O.toStringTag : void 0;
function _n(e) {
  var t = gn.call(e, J), n = e[J];
  try {
    e[J] = void 0;
    var r = !0;
  } catch {
  }
  var o = dn.call(e);
  return r && (t ? e[J] = n : delete e[J]), o;
}
var hn = Object.prototype, yn = hn.toString;
function bn(e) {
  return yn.call(e);
}
var mn = "[object Null]", vn = "[object Undefined]", ze = O ? O.toStringTag : void 0;
function K(e) {
  return e == null ? e === void 0 ? vn : mn : ze && ze in Object(e) ? _n(e) : bn(e);
}
function R(e) {
  return e != null && typeof e == "object";
}
var Tn = "[object Symbol]";
function Pe(e) {
  return typeof e == "symbol" || R(e) && K(e) == Tn;
}
function wt(e, t) {
  for (var n = -1, r = e == null ? 0 : e.length, o = Array(r); ++n < r; )
    o[n] = t(e[n], n, e);
  return o;
}
var x = Array.isArray, Be = O ? O.prototype : void 0, He = Be ? Be.toString : void 0;
function Pt(e) {
  if (typeof e == "string")
    return e;
  if (x(e))
    return wt(e, Pt) + "";
  if (Pe(e))
    return He ? He.call(e) : "";
  var t = e + "";
  return t == "0" && 1 / e == -1 / 0 ? "-0" : t;
}
function V(e) {
  var t = typeof e;
  return e != null && (t == "object" || t == "function");
}
function Ot(e) {
  return e;
}
var wn = "[object AsyncFunction]", Pn = "[object Function]", On = "[object GeneratorFunction]", An = "[object Proxy]";
function At(e) {
  if (!V(e))
    return !1;
  var t = K(e);
  return t == Pn || t == On || t == wn || t == An;
}
var pe = I["__core-js_shared__"], qe = function() {
  var e = /[^.]+$/.exec(pe && pe.keys && pe.keys.IE_PROTO || "");
  return e ? "Symbol(src)_1." + e : "";
}();
function $n(e) {
  return !!qe && qe in e;
}
var Sn = Function.prototype, xn = Sn.toString;
function U(e) {
  if (e != null) {
    try {
      return xn.call(e);
    } catch {
    }
    try {
      return e + "";
    } catch {
    }
  }
  return "";
}
var Cn = /[\\^$.*+?()[\]{}|]/g, jn = /^\[object .+?Constructor\]$/, En = Function.prototype, In = Object.prototype, Fn = En.toString, Mn = In.hasOwnProperty, Rn = RegExp("^" + Fn.call(Mn).replace(Cn, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$");
function Ln(e) {
  if (!V(e) || $n(e))
    return !1;
  var t = At(e) ? Rn : jn;
  return t.test(U(e));
}
function Dn(e, t) {
  return e == null ? void 0 : e[t];
}
function G(e, t) {
  var n = Dn(e, t);
  return Ln(n) ? n : void 0;
}
var ye = G(I, "WeakMap");
function Nn(e, t, n) {
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
var Kn = 800, Un = 16, Gn = Date.now;
function zn(e) {
  var t = 0, n = 0;
  return function() {
    var r = Gn(), o = Un - (r - n);
    if (n = r, o > 0) {
      if (++t >= Kn)
        return arguments[0];
    } else
      t = 0;
    return e.apply(void 0, arguments);
  };
}
function Bn(e) {
  return function() {
    return e;
  };
}
var re = function() {
  try {
    var e = G(Object, "defineProperty");
    return e({}, "", {}), e;
  } catch {
  }
}(), Hn = re ? function(e, t) {
  return re(e, "toString", {
    configurable: !0,
    enumerable: !1,
    value: Bn(t),
    writable: !0
  });
} : Ot, qn = zn(Hn);
function Xn(e, t) {
  for (var n = -1, r = e == null ? 0 : e.length; ++n < r && t(e[n], n, e) !== !1; )
    ;
  return e;
}
var Jn = 9007199254740991, Zn = /^(?:0|[1-9]\d*)$/;
function $t(e, t) {
  var n = typeof e;
  return t = t ?? Jn, !!t && (n == "number" || n != "symbol" && Zn.test(e)) && e > -1 && e % 1 == 0 && e < t;
}
function Oe(e, t, n) {
  t == "__proto__" && re ? re(e, t, {
    configurable: !0,
    enumerable: !0,
    value: n,
    writable: !0
  }) : e[t] = n;
}
function Ae(e, t) {
  return e === t || e !== e && t !== t;
}
var Wn = Object.prototype, Yn = Wn.hasOwnProperty;
function St(e, t, n) {
  var r = e[t];
  (!(Yn.call(e, t) && Ae(r, n)) || n === void 0 && !(t in e)) && Oe(e, t, n);
}
function Qn(e, t, n, r) {
  var o = !n;
  n || (n = {});
  for (var i = -1, a = t.length; ++i < a; ) {
    var s = t[i], u = void 0;
    u === void 0 && (u = e[s]), o ? Oe(n, s, u) : St(n, s, u);
  }
  return n;
}
var Xe = Math.max;
function Vn(e, t, n) {
  return t = Xe(t === void 0 ? e.length - 1 : t, 0), function() {
    for (var r = arguments, o = -1, i = Xe(r.length - t, 0), a = Array(i); ++o < i; )
      a[o] = r[t + o];
    o = -1;
    for (var s = Array(t + 1); ++o < t; )
      s[o] = r[o];
    return s[t] = n(a), Nn(e, this, s);
  };
}
var kn = 9007199254740991;
function $e(e) {
  return typeof e == "number" && e > -1 && e % 1 == 0 && e <= kn;
}
function xt(e) {
  return e != null && $e(e.length) && !At(e);
}
var er = Object.prototype;
function Ct(e) {
  var t = e && e.constructor, n = typeof t == "function" && t.prototype || er;
  return e === n;
}
function tr(e, t) {
  for (var n = -1, r = Array(e); ++n < e; )
    r[n] = t(n);
  return r;
}
var nr = "[object Arguments]";
function Je(e) {
  return R(e) && K(e) == nr;
}
var jt = Object.prototype, rr = jt.hasOwnProperty, ir = jt.propertyIsEnumerable, Se = Je(/* @__PURE__ */ function() {
  return arguments;
}()) ? Je : function(e) {
  return R(e) && rr.call(e, "callee") && !ir.call(e, "callee");
};
function or() {
  return !1;
}
var Et = typeof exports == "object" && exports && !exports.nodeType && exports, Ze = Et && typeof module == "object" && module && !module.nodeType && module, ar = Ze && Ze.exports === Et, We = ar ? I.Buffer : void 0, sr = We ? We.isBuffer : void 0, ie = sr || or, ur = "[object Arguments]", lr = "[object Array]", cr = "[object Boolean]", fr = "[object Date]", pr = "[object Error]", gr = "[object Function]", dr = "[object Map]", _r = "[object Number]", hr = "[object Object]", yr = "[object RegExp]", br = "[object Set]", mr = "[object String]", vr = "[object WeakMap]", Tr = "[object ArrayBuffer]", wr = "[object DataView]", Pr = "[object Float32Array]", Or = "[object Float64Array]", Ar = "[object Int8Array]", $r = "[object Int16Array]", Sr = "[object Int32Array]", xr = "[object Uint8Array]", Cr = "[object Uint8ClampedArray]", jr = "[object Uint16Array]", Er = "[object Uint32Array]", m = {};
m[Pr] = m[Or] = m[Ar] = m[$r] = m[Sr] = m[xr] = m[Cr] = m[jr] = m[Er] = !0;
m[ur] = m[lr] = m[Tr] = m[cr] = m[wr] = m[fr] = m[pr] = m[gr] = m[dr] = m[_r] = m[hr] = m[yr] = m[br] = m[mr] = m[vr] = !1;
function Ir(e) {
  return R(e) && $e(e.length) && !!m[K(e)];
}
function xe(e) {
  return function(t) {
    return e(t);
  };
}
var It = typeof exports == "object" && exports && !exports.nodeType && exports, Z = It && typeof module == "object" && module && !module.nodeType && module, Fr = Z && Z.exports === It, ge = Fr && vt.process, q = function() {
  try {
    var e = Z && Z.require && Z.require("util").types;
    return e || ge && ge.binding && ge.binding("util");
  } catch {
  }
}(), Ye = q && q.isTypedArray, Ft = Ye ? xe(Ye) : Ir, Mr = Object.prototype, Rr = Mr.hasOwnProperty;
function Mt(e, t) {
  var n = x(e), r = !n && Se(e), o = !n && !r && ie(e), i = !n && !r && !o && Ft(e), a = n || r || o || i, s = a ? tr(e.length, String) : [], u = s.length;
  for (var l in e)
    (t || Rr.call(e, l)) && !(a && // Safari 9 has enumerable `arguments.length` in strict mode.
    (l == "length" || // Node.js 0.10 has enumerable non-index properties on buffers.
    o && (l == "offset" || l == "parent") || // PhantomJS 2 has enumerable non-index properties on typed arrays.
    i && (l == "buffer" || l == "byteLength" || l == "byteOffset") || // Skip index properties.
    $t(l, u))) && s.push(l);
  return s;
}
function Rt(e, t) {
  return function(n) {
    return e(t(n));
  };
}
var Lr = Rt(Object.keys, Object), Dr = Object.prototype, Nr = Dr.hasOwnProperty;
function Kr(e) {
  if (!Ct(e))
    return Lr(e);
  var t = [];
  for (var n in Object(e))
    Nr.call(e, n) && n != "constructor" && t.push(n);
  return t;
}
function Ce(e) {
  return xt(e) ? Mt(e) : Kr(e);
}
function Ur(e) {
  var t = [];
  if (e != null)
    for (var n in Object(e))
      t.push(n);
  return t;
}
var Gr = Object.prototype, zr = Gr.hasOwnProperty;
function Br(e) {
  if (!V(e))
    return Ur(e);
  var t = Ct(e), n = [];
  for (var r in e)
    r == "constructor" && (t || !zr.call(e, r)) || n.push(r);
  return n;
}
function Hr(e) {
  return xt(e) ? Mt(e, !0) : Br(e);
}
var qr = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/, Xr = /^\w*$/;
function je(e, t) {
  if (x(e))
    return !1;
  var n = typeof e;
  return n == "number" || n == "symbol" || n == "boolean" || e == null || Pe(e) ? !0 : Xr.test(e) || !qr.test(e) || t != null && e in Object(t);
}
var W = G(Object, "create");
function Jr() {
  this.__data__ = W ? W(null) : {}, this.size = 0;
}
function Zr(e) {
  var t = this.has(e) && delete this.__data__[e];
  return this.size -= t ? 1 : 0, t;
}
var Wr = "__lodash_hash_undefined__", Yr = Object.prototype, Qr = Yr.hasOwnProperty;
function Vr(e) {
  var t = this.__data__;
  if (W) {
    var n = t[e];
    return n === Wr ? void 0 : n;
  }
  return Qr.call(t, e) ? t[e] : void 0;
}
var kr = Object.prototype, ei = kr.hasOwnProperty;
function ti(e) {
  var t = this.__data__;
  return W ? t[e] !== void 0 : ei.call(t, e);
}
var ni = "__lodash_hash_undefined__";
function ri(e, t) {
  var n = this.__data__;
  return this.size += this.has(e) ? 0 : 1, n[e] = W && t === void 0 ? ni : t, this;
}
function N(e) {
  var t = -1, n = e == null ? 0 : e.length;
  for (this.clear(); ++t < n; ) {
    var r = e[t];
    this.set(r[0], r[1]);
  }
}
N.prototype.clear = Jr;
N.prototype.delete = Zr;
N.prototype.get = Vr;
N.prototype.has = ti;
N.prototype.set = ri;
function ii() {
  this.__data__ = [], this.size = 0;
}
function ue(e, t) {
  for (var n = e.length; n--; )
    if (Ae(e[n][0], t))
      return n;
  return -1;
}
var oi = Array.prototype, ai = oi.splice;
function si(e) {
  var t = this.__data__, n = ue(t, e);
  if (n < 0)
    return !1;
  var r = t.length - 1;
  return n == r ? t.pop() : ai.call(t, n, 1), --this.size, !0;
}
function ui(e) {
  var t = this.__data__, n = ue(t, e);
  return n < 0 ? void 0 : t[n][1];
}
function li(e) {
  return ue(this.__data__, e) > -1;
}
function ci(e, t) {
  var n = this.__data__, r = ue(n, e);
  return r < 0 ? (++this.size, n.push([e, t])) : n[r][1] = t, this;
}
function L(e) {
  var t = -1, n = e == null ? 0 : e.length;
  for (this.clear(); ++t < n; ) {
    var r = e[t];
    this.set(r[0], r[1]);
  }
}
L.prototype.clear = ii;
L.prototype.delete = si;
L.prototype.get = ui;
L.prototype.has = li;
L.prototype.set = ci;
var Y = G(I, "Map");
function fi() {
  this.size = 0, this.__data__ = {
    hash: new N(),
    map: new (Y || L)(),
    string: new N()
  };
}
function pi(e) {
  var t = typeof e;
  return t == "string" || t == "number" || t == "symbol" || t == "boolean" ? e !== "__proto__" : e === null;
}
function le(e, t) {
  var n = e.__data__;
  return pi(t) ? n[typeof t == "string" ? "string" : "hash"] : n.map;
}
function gi(e) {
  var t = le(this, e).delete(e);
  return this.size -= t ? 1 : 0, t;
}
function di(e) {
  return le(this, e).get(e);
}
function _i(e) {
  return le(this, e).has(e);
}
function hi(e, t) {
  var n = le(this, e), r = n.size;
  return n.set(e, t), this.size += n.size == r ? 0 : 1, this;
}
function D(e) {
  var t = -1, n = e == null ? 0 : e.length;
  for (this.clear(); ++t < n; ) {
    var r = e[t];
    this.set(r[0], r[1]);
  }
}
D.prototype.clear = fi;
D.prototype.delete = gi;
D.prototype.get = di;
D.prototype.has = _i;
D.prototype.set = hi;
var yi = "Expected a function";
function Ee(e, t) {
  if (typeof e != "function" || t != null && typeof t != "function")
    throw new TypeError(yi);
  var n = function() {
    var r = arguments, o = t ? t.apply(this, r) : r[0], i = n.cache;
    if (i.has(o))
      return i.get(o);
    var a = e.apply(this, r);
    return n.cache = i.set(o, a) || i, a;
  };
  return n.cache = new (Ee.Cache || D)(), n;
}
Ee.Cache = D;
var bi = 500;
function mi(e) {
  var t = Ee(e, function(r) {
    return n.size === bi && n.clear(), r;
  }), n = t.cache;
  return t;
}
var vi = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g, Ti = /\\(\\)?/g, wi = mi(function(e) {
  var t = [];
  return e.charCodeAt(0) === 46 && t.push(""), e.replace(vi, function(n, r, o, i) {
    t.push(o ? i.replace(Ti, "$1") : r || n);
  }), t;
});
function Pi(e) {
  return e == null ? "" : Pt(e);
}
function ce(e, t) {
  return x(e) ? e : je(e, t) ? [e] : wi(Pi(e));
}
function k(e) {
  if (typeof e == "string" || Pe(e))
    return e;
  var t = e + "";
  return t == "0" && 1 / e == -1 / 0 ? "-0" : t;
}
function Ie(e, t) {
  t = ce(t, e);
  for (var n = 0, r = t.length; e != null && n < r; )
    e = e[k(t[n++])];
  return n && n == r ? e : void 0;
}
function Oi(e, t, n) {
  var r = e == null ? void 0 : Ie(e, t);
  return r === void 0 ? n : r;
}
function Fe(e, t) {
  for (var n = -1, r = t.length, o = e.length; ++n < r; )
    e[o + n] = t[n];
  return e;
}
var Qe = O ? O.isConcatSpreadable : void 0;
function Ai(e) {
  return x(e) || Se(e) || !!(Qe && e && e[Qe]);
}
function $i(e, t, n, r, o) {
  var i = -1, a = e.length;
  for (n || (n = Ai), o || (o = []); ++i < a; ) {
    var s = e[i];
    n(s) ? Fe(o, s) : o[o.length] = s;
  }
  return o;
}
function Si(e) {
  var t = e == null ? 0 : e.length;
  return t ? $i(e) : [];
}
function xi(e) {
  return qn(Vn(e, void 0, Si), e + "");
}
var Lt = Rt(Object.getPrototypeOf, Object), Ci = "[object Object]", ji = Function.prototype, Ei = Object.prototype, Dt = ji.toString, Ii = Ei.hasOwnProperty, Fi = Dt.call(Object);
function be(e) {
  if (!R(e) || K(e) != Ci)
    return !1;
  var t = Lt(e);
  if (t === null)
    return !0;
  var n = Ii.call(t, "constructor") && t.constructor;
  return typeof n == "function" && n instanceof n && Dt.call(n) == Fi;
}
function Mi(e, t, n) {
  var r = -1, o = e.length;
  t < 0 && (t = -t > o ? 0 : o + t), n = n > o ? o : n, n < 0 && (n += o), o = t > n ? 0 : n - t >>> 0, t >>>= 0;
  for (var i = Array(o); ++r < o; )
    i[r] = e[r + t];
  return i;
}
function Ri() {
  this.__data__ = new L(), this.size = 0;
}
function Li(e) {
  var t = this.__data__, n = t.delete(e);
  return this.size = t.size, n;
}
function Di(e) {
  return this.__data__.get(e);
}
function Ni(e) {
  return this.__data__.has(e);
}
var Ki = 200;
function Ui(e, t) {
  var n = this.__data__;
  if (n instanceof L) {
    var r = n.__data__;
    if (!Y || r.length < Ki - 1)
      return r.push([e, t]), this.size = ++n.size, this;
    n = this.__data__ = new D(r);
  }
  return n.set(e, t), this.size = n.size, this;
}
function E(e) {
  var t = this.__data__ = new L(e);
  this.size = t.size;
}
E.prototype.clear = Ri;
E.prototype.delete = Li;
E.prototype.get = Di;
E.prototype.has = Ni;
E.prototype.set = Ui;
var Nt = typeof exports == "object" && exports && !exports.nodeType && exports, Ve = Nt && typeof module == "object" && module && !module.nodeType && module, Gi = Ve && Ve.exports === Nt, ke = Gi ? I.Buffer : void 0;
ke && ke.allocUnsafe;
function zi(e, t) {
  return e.slice();
}
function Bi(e, t) {
  for (var n = -1, r = e == null ? 0 : e.length, o = 0, i = []; ++n < r; ) {
    var a = e[n];
    t(a, n, e) && (i[o++] = a);
  }
  return i;
}
function Kt() {
  return [];
}
var Hi = Object.prototype, qi = Hi.propertyIsEnumerable, et = Object.getOwnPropertySymbols, Ut = et ? function(e) {
  return e == null ? [] : (e = Object(e), Bi(et(e), function(t) {
    return qi.call(e, t);
  }));
} : Kt, Xi = Object.getOwnPropertySymbols, Ji = Xi ? function(e) {
  for (var t = []; e; )
    Fe(t, Ut(e)), e = Lt(e);
  return t;
} : Kt;
function Gt(e, t, n) {
  var r = t(e);
  return x(e) ? r : Fe(r, n(e));
}
function tt(e) {
  return Gt(e, Ce, Ut);
}
function zt(e) {
  return Gt(e, Hr, Ji);
}
var me = G(I, "DataView"), ve = G(I, "Promise"), Te = G(I, "Set"), nt = "[object Map]", Zi = "[object Object]", rt = "[object Promise]", it = "[object Set]", ot = "[object WeakMap]", at = "[object DataView]", Wi = U(me), Yi = U(Y), Qi = U(ve), Vi = U(Te), ki = U(ye), S = K;
(me && S(new me(new ArrayBuffer(1))) != at || Y && S(new Y()) != nt || ve && S(ve.resolve()) != rt || Te && S(new Te()) != it || ye && S(new ye()) != ot) && (S = function(e) {
  var t = K(e), n = t == Zi ? e.constructor : void 0, r = n ? U(n) : "";
  if (r)
    switch (r) {
      case Wi:
        return at;
      case Yi:
        return nt;
      case Qi:
        return rt;
      case Vi:
        return it;
      case ki:
        return ot;
    }
  return t;
});
var eo = Object.prototype, to = eo.hasOwnProperty;
function no(e) {
  var t = e.length, n = new e.constructor(t);
  return t && typeof e[0] == "string" && to.call(e, "index") && (n.index = e.index, n.input = e.input), n;
}
var oe = I.Uint8Array;
function Me(e) {
  var t = new e.constructor(e.byteLength);
  return new oe(t).set(new oe(e)), t;
}
function ro(e, t) {
  var n = Me(e.buffer);
  return new e.constructor(n, e.byteOffset, e.byteLength);
}
var io = /\w*$/;
function oo(e) {
  var t = new e.constructor(e.source, io.exec(e));
  return t.lastIndex = e.lastIndex, t;
}
var st = O ? O.prototype : void 0, ut = st ? st.valueOf : void 0;
function ao(e) {
  return ut ? Object(ut.call(e)) : {};
}
function so(e, t) {
  var n = Me(e.buffer);
  return new e.constructor(n, e.byteOffset, e.length);
}
var uo = "[object Boolean]", lo = "[object Date]", co = "[object Map]", fo = "[object Number]", po = "[object RegExp]", go = "[object Set]", _o = "[object String]", ho = "[object Symbol]", yo = "[object ArrayBuffer]", bo = "[object DataView]", mo = "[object Float32Array]", vo = "[object Float64Array]", To = "[object Int8Array]", wo = "[object Int16Array]", Po = "[object Int32Array]", Oo = "[object Uint8Array]", Ao = "[object Uint8ClampedArray]", $o = "[object Uint16Array]", So = "[object Uint32Array]";
function xo(e, t, n) {
  var r = e.constructor;
  switch (t) {
    case yo:
      return Me(e);
    case uo:
    case lo:
      return new r(+e);
    case bo:
      return ro(e);
    case mo:
    case vo:
    case To:
    case wo:
    case Po:
    case Oo:
    case Ao:
    case $o:
    case So:
      return so(e);
    case co:
      return new r();
    case fo:
    case _o:
      return new r(e);
    case po:
      return oo(e);
    case go:
      return new r();
    case ho:
      return ao(e);
  }
}
var Co = "[object Map]";
function jo(e) {
  return R(e) && S(e) == Co;
}
var lt = q && q.isMap, Eo = lt ? xe(lt) : jo, Io = "[object Set]";
function Fo(e) {
  return R(e) && S(e) == Io;
}
var ct = q && q.isSet, Mo = ct ? xe(ct) : Fo, Bt = "[object Arguments]", Ro = "[object Array]", Lo = "[object Boolean]", Do = "[object Date]", No = "[object Error]", Ht = "[object Function]", Ko = "[object GeneratorFunction]", Uo = "[object Map]", Go = "[object Number]", qt = "[object Object]", zo = "[object RegExp]", Bo = "[object Set]", Ho = "[object String]", qo = "[object Symbol]", Xo = "[object WeakMap]", Jo = "[object ArrayBuffer]", Zo = "[object DataView]", Wo = "[object Float32Array]", Yo = "[object Float64Array]", Qo = "[object Int8Array]", Vo = "[object Int16Array]", ko = "[object Int32Array]", ea = "[object Uint8Array]", ta = "[object Uint8ClampedArray]", na = "[object Uint16Array]", ra = "[object Uint32Array]", y = {};
y[Bt] = y[Ro] = y[Jo] = y[Zo] = y[Lo] = y[Do] = y[Wo] = y[Yo] = y[Qo] = y[Vo] = y[ko] = y[Uo] = y[Go] = y[qt] = y[zo] = y[Bo] = y[Ho] = y[qo] = y[ea] = y[ta] = y[na] = y[ra] = !0;
y[No] = y[Ht] = y[Xo] = !1;
function te(e, t, n, r, o, i) {
  var a;
  if (n && (a = o ? n(e, r, o, i) : n(e)), a !== void 0)
    return a;
  if (!V(e))
    return e;
  var s = x(e);
  if (s)
    a = no(e);
  else {
    var u = S(e), l = u == Ht || u == Ko;
    if (ie(e))
      return zi(e);
    if (u == qt || u == Bt || l && !o)
      a = {};
    else {
      if (!y[u])
        return o ? e : {};
      a = xo(e, u);
    }
  }
  i || (i = new E());
  var f = i.get(e);
  if (f)
    return f;
  i.set(e, a), Mo(e) ? e.forEach(function(p) {
    a.add(te(p, t, n, p, e, i));
  }) : Eo(e) && e.forEach(function(p, _) {
    a.set(_, te(p, t, n, _, e, i));
  });
  var h = zt, c = s ? void 0 : h(e);
  return Xn(c || e, function(p, _) {
    c && (_ = p, p = e[_]), St(a, _, te(p, t, n, _, e, i));
  }), a;
}
var ia = "__lodash_hash_undefined__";
function oa(e) {
  return this.__data__.set(e, ia), this;
}
function aa(e) {
  return this.__data__.has(e);
}
function ae(e) {
  var t = -1, n = e == null ? 0 : e.length;
  for (this.__data__ = new D(); ++t < n; )
    this.add(e[t]);
}
ae.prototype.add = ae.prototype.push = oa;
ae.prototype.has = aa;
function sa(e, t) {
  for (var n = -1, r = e == null ? 0 : e.length; ++n < r; )
    if (t(e[n], n, e))
      return !0;
  return !1;
}
function ua(e, t) {
  return e.has(t);
}
var la = 1, ca = 2;
function Xt(e, t, n, r, o, i) {
  var a = n & la, s = e.length, u = t.length;
  if (s != u && !(a && u > s))
    return !1;
  var l = i.get(e), f = i.get(t);
  if (l && f)
    return l == t && f == e;
  var h = -1, c = !0, p = n & ca ? new ae() : void 0;
  for (i.set(e, t), i.set(t, e); ++h < s; ) {
    var _ = e[h], b = t[h];
    if (r)
      var g = a ? r(b, _, h, t, e, i) : r(_, b, h, e, t, i);
    if (g !== void 0) {
      if (g)
        continue;
      c = !1;
      break;
    }
    if (p) {
      if (!sa(t, function(v, T) {
        if (!ua(p, T) && (_ === v || o(_, v, n, r, i)))
          return p.push(T);
      })) {
        c = !1;
        break;
      }
    } else if (!(_ === b || o(_, b, n, r, i))) {
      c = !1;
      break;
    }
  }
  return i.delete(e), i.delete(t), c;
}
function fa(e) {
  var t = -1, n = Array(e.size);
  return e.forEach(function(r, o) {
    n[++t] = [o, r];
  }), n;
}
function pa(e) {
  var t = -1, n = Array(e.size);
  return e.forEach(function(r) {
    n[++t] = r;
  }), n;
}
var ga = 1, da = 2, _a = "[object Boolean]", ha = "[object Date]", ya = "[object Error]", ba = "[object Map]", ma = "[object Number]", va = "[object RegExp]", Ta = "[object Set]", wa = "[object String]", Pa = "[object Symbol]", Oa = "[object ArrayBuffer]", Aa = "[object DataView]", ft = O ? O.prototype : void 0, de = ft ? ft.valueOf : void 0;
function $a(e, t, n, r, o, i, a) {
  switch (n) {
    case Aa:
      if (e.byteLength != t.byteLength || e.byteOffset != t.byteOffset)
        return !1;
      e = e.buffer, t = t.buffer;
    case Oa:
      return !(e.byteLength != t.byteLength || !i(new oe(e), new oe(t)));
    case _a:
    case ha:
    case ma:
      return Ae(+e, +t);
    case ya:
      return e.name == t.name && e.message == t.message;
    case va:
    case wa:
      return e == t + "";
    case ba:
      var s = fa;
    case Ta:
      var u = r & ga;
      if (s || (s = pa), e.size != t.size && !u)
        return !1;
      var l = a.get(e);
      if (l)
        return l == t;
      r |= da, a.set(e, t);
      var f = Xt(s(e), s(t), r, o, i, a);
      return a.delete(e), f;
    case Pa:
      if (de)
        return de.call(e) == de.call(t);
  }
  return !1;
}
var Sa = 1, xa = Object.prototype, Ca = xa.hasOwnProperty;
function ja(e, t, n, r, o, i) {
  var a = n & Sa, s = tt(e), u = s.length, l = tt(t), f = l.length;
  if (u != f && !a)
    return !1;
  for (var h = u; h--; ) {
    var c = s[h];
    if (!(a ? c in t : Ca.call(t, c)))
      return !1;
  }
  var p = i.get(e), _ = i.get(t);
  if (p && _)
    return p == t && _ == e;
  var b = !0;
  i.set(e, t), i.set(t, e);
  for (var g = a; ++h < u; ) {
    c = s[h];
    var v = e[c], T = t[c];
    if (r)
      var P = a ? r(T, v, c, t, e, i) : r(v, T, c, e, t, i);
    if (!(P === void 0 ? v === T || o(v, T, n, r, i) : P)) {
      b = !1;
      break;
    }
    g || (g = c == "constructor");
  }
  if (b && !g) {
    var C = e.constructor, A = t.constructor;
    C != A && "constructor" in e && "constructor" in t && !(typeof C == "function" && C instanceof C && typeof A == "function" && A instanceof A) && (b = !1);
  }
  return i.delete(e), i.delete(t), b;
}
var Ea = 1, pt = "[object Arguments]", gt = "[object Array]", ee = "[object Object]", Ia = Object.prototype, dt = Ia.hasOwnProperty;
function Fa(e, t, n, r, o, i) {
  var a = x(e), s = x(t), u = a ? gt : S(e), l = s ? gt : S(t);
  u = u == pt ? ee : u, l = l == pt ? ee : l;
  var f = u == ee, h = l == ee, c = u == l;
  if (c && ie(e)) {
    if (!ie(t))
      return !1;
    a = !0, f = !1;
  }
  if (c && !f)
    return i || (i = new E()), a || Ft(e) ? Xt(e, t, n, r, o, i) : $a(e, t, u, n, r, o, i);
  if (!(n & Ea)) {
    var p = f && dt.call(e, "__wrapped__"), _ = h && dt.call(t, "__wrapped__");
    if (p || _) {
      var b = p ? e.value() : e, g = _ ? t.value() : t;
      return i || (i = new E()), o(b, g, n, r, i);
    }
  }
  return c ? (i || (i = new E()), ja(e, t, n, r, o, i)) : !1;
}
function Re(e, t, n, r, o) {
  return e === t ? !0 : e == null || t == null || !R(e) && !R(t) ? e !== e && t !== t : Fa(e, t, n, r, Re, o);
}
var Ma = 1, Ra = 2;
function La(e, t, n, r) {
  var o = n.length, i = o;
  if (e == null)
    return !i;
  for (e = Object(e); o--; ) {
    var a = n[o];
    if (a[2] ? a[1] !== e[a[0]] : !(a[0] in e))
      return !1;
  }
  for (; ++o < i; ) {
    a = n[o];
    var s = a[0], u = e[s], l = a[1];
    if (a[2]) {
      if (u === void 0 && !(s in e))
        return !1;
    } else {
      var f = new E(), h;
      if (!(h === void 0 ? Re(l, u, Ma | Ra, r, f) : h))
        return !1;
    }
  }
  return !0;
}
function Jt(e) {
  return e === e && !V(e);
}
function Da(e) {
  for (var t = Ce(e), n = t.length; n--; ) {
    var r = t[n], o = e[r];
    t[n] = [r, o, Jt(o)];
  }
  return t;
}
function Zt(e, t) {
  return function(n) {
    return n == null ? !1 : n[e] === t && (t !== void 0 || e in Object(n));
  };
}
function Na(e) {
  var t = Da(e);
  return t.length == 1 && t[0][2] ? Zt(t[0][0], t[0][1]) : function(n) {
    return n === e || La(n, e, t);
  };
}
function Ka(e, t) {
  return e != null && t in Object(e);
}
function Ua(e, t, n) {
  t = ce(t, e);
  for (var r = -1, o = t.length, i = !1; ++r < o; ) {
    var a = k(t[r]);
    if (!(i = e != null && n(e, a)))
      break;
    e = e[a];
  }
  return i || ++r != o ? i : (o = e == null ? 0 : e.length, !!o && $e(o) && $t(a, o) && (x(e) || Se(e)));
}
function Ga(e, t) {
  return e != null && Ua(e, t, Ka);
}
var za = 1, Ba = 2;
function Ha(e, t) {
  return je(e) && Jt(t) ? Zt(k(e), t) : function(n) {
    var r = Oi(n, e);
    return r === void 0 && r === t ? Ga(n, e) : Re(t, r, za | Ba);
  };
}
function qa(e) {
  return function(t) {
    return t == null ? void 0 : t[e];
  };
}
function Xa(e) {
  return function(t) {
    return Ie(t, e);
  };
}
function Ja(e) {
  return je(e) ? qa(k(e)) : Xa(e);
}
function Za(e) {
  return typeof e == "function" ? e : e == null ? Ot : typeof e == "object" ? x(e) ? Ha(e[0], e[1]) : Na(e) : Ja(e);
}
function Wa(e) {
  return function(t, n, r) {
    for (var o = -1, i = Object(t), a = r(t), s = a.length; s--; ) {
      var u = a[++o];
      if (n(i[u], u, i) === !1)
        break;
    }
    return t;
  };
}
var Ya = Wa();
function Qa(e, t) {
  return e && Ya(e, t, Ce);
}
function Va(e) {
  var t = e == null ? 0 : e.length;
  return t ? e[t - 1] : void 0;
}
function ka(e, t) {
  return t.length < 2 ? e : Ie(e, Mi(t, 0, -1));
}
function es(e, t) {
  var n = {};
  return t = Za(t), Qa(e, function(r, o, i) {
    Oe(n, t(r, o, i), r);
  }), n;
}
function ts(e, t) {
  return t = ce(t, e), e = ka(e, t), e == null || delete e[k(Va(t))];
}
function ns(e) {
  return be(e) ? void 0 : e;
}
var rs = 1, is = 2, os = 4, Wt = xi(function(e, t) {
  var n = {};
  if (e == null)
    return n;
  var r = !1;
  t = wt(t, function(i) {
    return i = ce(i, e), r || (r = i.length > 1), i;
  }), Qn(e, zt(e), n), r && (n = te(n, rs | is | os, ns));
  for (var o = t.length; o--; )
    ts(n, t[o]);
  return n;
});
function as(e) {
  return e.replace(/(^|_)(\w)/g, (t, n, r, o) => o === 0 ? r.toLowerCase() : r.toUpperCase());
}
async function ss() {
  window.ms_globals || (window.ms_globals = {}), window.ms_globals.initializePromise || (window.ms_globals.initializePromise = new Promise((e) => {
    window.ms_globals.initialize = () => {
      e();
    };
  })), await window.ms_globals.initializePromise;
}
async function us(e) {
  return await ss(), e().then((t) => t.default);
}
const Yt = [
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
], ls = Yt.concat(["attached_events"]);
function cs(e, t = {}, n = !1) {
  return es(Wt(e, n ? [] : Yt), (r, o) => t[o] || as(o));
}
function _t(e, t) {
  const {
    gradio: n,
    _internal: r,
    restProps: o,
    originalRestProps: i,
    ...a
  } = e, s = (o == null ? void 0 : o.attachedEvents) || [];
  return {
    ...Array.from(/* @__PURE__ */ new Set([...Object.keys(r).map((u) => {
      const l = u.match(/bind_(.+)_event/);
      return l && l[1] ? l[1] : null;
    }).filter(Boolean), ...s.map((u) => t && t[u] ? t[u] : u)])).reduce((u, l) => {
      const f = l.split("_"), h = (...p) => {
        const _ = p.map((g) => p && typeof g == "object" && (g.nativeEvent || g instanceof Event) ? {
          type: g.type,
          detail: g.detail,
          timestamp: g.timeStamp,
          clientX: g.clientX,
          clientY: g.clientY,
          targetId: g.target.id,
          targetClassName: g.target.className,
          altKey: g.altKey,
          ctrlKey: g.ctrlKey,
          shiftKey: g.shiftKey,
          metaKey: g.metaKey
        } : g);
        let b;
        try {
          b = JSON.parse(JSON.stringify(_));
        } catch {
          let g = function(v) {
            try {
              return JSON.stringify(v), v;
            } catch {
              return be(v) ? Object.fromEntries(Object.entries(v).map(([T, P]) => {
                try {
                  return JSON.stringify(P), [T, P];
                } catch {
                  return be(P) ? [T, Object.fromEntries(Object.entries(P).filter(([C, A]) => {
                    try {
                      return JSON.stringify(A), !0;
                    } catch {
                      return !1;
                    }
                  }))] : null;
                }
              }).filter(Boolean)) : {};
            }
          };
          b = _.map((v) => g(v));
        }
        return n.dispatch(l.replace(/[A-Z]/g, (g) => "_" + g.toLowerCase()), {
          payload: b,
          component: {
            ...a,
            ...Wt(i, ls)
          }
        });
      };
      if (f.length > 1) {
        let p = {
          ...a.props[f[0]] || (o == null ? void 0 : o[f[0]]) || {}
        };
        u[f[0]] = p;
        for (let b = 1; b < f.length - 1; b++) {
          const g = {
            ...a.props[f[b]] || (o == null ? void 0 : o[f[b]]) || {}
          };
          p[f[b]] = g, p = g;
        }
        const _ = f[f.length - 1];
        return p[`on${_.slice(0, 1).toUpperCase()}${_.slice(1)}`] = h, u;
      }
      const c = f[0];
      return u[`on${c.slice(0, 1).toUpperCase()}${c.slice(1)}`] = h, u;
    }, {}),
    __render_eventProps: {
      props: e,
      eventsMapping: t
    }
  };
}
function ne() {
}
function fs(e, ...t) {
  if (e == null) {
    for (const r of t) r(void 0);
    return ne;
  }
  const n = e.subscribe(...t);
  return n.unsubscribe ? () => n.unsubscribe() : n;
}
function Qt(e) {
  let t;
  return fs(e, (n) => t = n)(), t;
}
const B = [];
function M(e, t = ne) {
  let n;
  const r = /* @__PURE__ */ new Set();
  function o(a) {
    if (u = a, ((s = e) != s ? u == u : s !== u || s && typeof s == "object" || typeof s == "function") && (e = a, n)) {
      const l = !B.length;
      for (const f of r) f[1](), B.push(f, e);
      if (l) {
        for (let f = 0; f < B.length; f += 2) B[f][0](B[f + 1]);
        B.length = 0;
      }
    }
    var s, u;
  }
  function i(a) {
    o(a(e));
  }
  return {
    set: o,
    update: i,
    subscribe: function(a, s = ne) {
      const u = [a, s];
      return r.add(u), r.size === 1 && (n = t(o, i) || ne), a(e), () => {
        r.delete(u), r.size === 0 && n && (n(), n = null);
      };
    }
  };
}
const {
  getContext: ps,
  setContext: eu
} = window.__gradio__svelte__internal, gs = "$$ms-gr-loading-status-key";
function ds() {
  const e = window.ms_globals.loadingKey++, t = ps(gs);
  return (n) => {
    if (!t || !n)
      return;
    const {
      loadingStatusMap: r,
      options: o
    } = t, {
      generating: i,
      error: a
    } = Qt(o);
    (n == null ? void 0 : n.status) === "pending" || a && (n == null ? void 0 : n.status) === "error" || (i && (n == null ? void 0 : n.status)) === "generating" ? r.update(({
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
  getContext: fe,
  setContext: X
} = window.__gradio__svelte__internal, _s = "$$ms-gr-slots-key";
function hs() {
  const e = M({});
  return X(_s, e);
}
const Vt = "$$ms-gr-slot-params-mapping-fn-key";
function ys() {
  return fe(Vt);
}
function bs(e) {
  return X(Vt, M(e));
}
const ms = "$$ms-gr-slot-params-key";
function vs() {
  const e = X(ms, M({}));
  return (t, n) => {
    e.update((r) => typeof n == "function" ? {
      ...r,
      [t]: n(r[t])
    } : {
      ...r,
      [t]: n
    });
  };
}
const kt = "$$ms-gr-sub-index-context-key";
function Ts() {
  return fe(kt) || null;
}
function ht(e) {
  return X(kt, e);
}
function ws(e, t, n) {
  if (!Reflect.has(e, "as_item") || !Reflect.has(e, "_internal"))
    throw new Error("`as_item` and `_internal` is required");
  const r = Os(), o = ys();
  bs().set(void 0);
  const a = As({
    slot: void 0,
    index: e._internal.index,
    subIndex: e._internal.subIndex
  }), s = Ts();
  typeof s == "number" && ht(void 0);
  const u = ds();
  typeof e._internal.subIndex == "number" && ht(e._internal.subIndex), r && r.subscribe((c) => {
    a.slotKey.set(c);
  }), Ps();
  const l = e.as_item, f = (c, p) => c ? {
    ...cs({
      ...c
    }, t),
    __render_slotParamsMappingFn: o ? Qt(o) : void 0,
    __render_as_item: p,
    __render_restPropsMapping: t
  } : void 0, h = M({
    ...e,
    _internal: {
      ...e._internal,
      index: s ?? e._internal.index
    },
    restProps: f(e.restProps, l),
    originalRestProps: e.restProps
  });
  return o && o.subscribe((c) => {
    h.update((p) => ({
      ...p,
      restProps: {
        ...p.restProps,
        __slotParamsMappingFn: c
      }
    }));
  }), [h, (c) => {
    var p;
    u((p = c.restProps) == null ? void 0 : p.loading_status), h.set({
      ...c,
      _internal: {
        ...c._internal,
        index: s ?? c._internal.index
      },
      restProps: f(c.restProps, c.as_item),
      originalRestProps: c.restProps
    });
  }];
}
const en = "$$ms-gr-slot-key";
function Ps() {
  X(en, M(void 0));
}
function Os() {
  return fe(en);
}
const tn = "$$ms-gr-component-slot-context-key";
function As({
  slot: e,
  index: t,
  subIndex: n
}) {
  return X(tn, {
    slotKey: M(e),
    slotIndex: M(t),
    subSlotIndex: M(n)
  });
}
function tu() {
  return fe(tn);
}
new Intl.Collator(0, {
  numeric: 1
}).compare;
async function $s(e, t) {
  return e.map((n) => new Ss({
    path: n.name,
    orig_name: n.name,
    blob: n,
    size: n.size,
    mime_type: n.type,
    is_stream: t
  }));
}
class Ss {
  constructor({
    path: t,
    url: n,
    orig_name: r,
    size: o,
    blob: i,
    is_stream: a,
    mime_type: s,
    alt_text: u,
    b64: l
  }) {
    $(this, "path");
    $(this, "url");
    $(this, "orig_name");
    $(this, "size");
    $(this, "blob");
    $(this, "is_stream");
    $(this, "mime_type");
    $(this, "alt_text");
    $(this, "b64");
    $(this, "meta", {
      _type: "gradio.FileData"
    });
    this.path = t, this.url = n, this.orig_name = r, this.size = o, this.blob = n ? void 0 : i, this.is_stream = a, this.mime_type = s, this.alt_text = u, this.b64 = l;
  }
}
typeof process < "u" && process.versions && process.versions.node;
var F;
class nu extends TransformStream {
  /** Constructs a new instance. */
  constructor(n = {
    allowCR: !1
  }) {
    super({
      transform: (r, o) => {
        for (r = z(this, F) + r; ; ) {
          const i = r.indexOf(`
`), a = n.allowCR ? r.indexOf("\r") : -1;
          if (a !== -1 && a !== r.length - 1 && (i === -1 || i - 1 > a)) {
            o.enqueue(r.slice(0, a)), r = r.slice(a + 1);
            continue;
          }
          if (i === -1) break;
          const s = r[i - 1] === "\r" ? i - 1 : i;
          o.enqueue(r.slice(0, s)), r = r.slice(i + 1);
        }
        Ge(this, F, r);
      },
      flush: (r) => {
        if (z(this, F) === "") return;
        const o = n.allowCR && z(this, F).endsWith("\r") ? z(this, F).slice(0, -1) : z(this, F);
        r.enqueue(o);
      }
    });
    Ue(this, F, "");
  }
}
F = new WeakMap();
function xs(e) {
  return e && e.__esModule && Object.prototype.hasOwnProperty.call(e, "default") ? e.default : e;
}
var nn = {
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
      for (var i = "", a = 0; a < arguments.length; a++) {
        var s = arguments[a];
        s && (i = o(i, r(s)));
      }
      return i;
    }
    function r(i) {
      if (typeof i == "string" || typeof i == "number")
        return i;
      if (typeof i != "object")
        return "";
      if (Array.isArray(i))
        return n.apply(null, i);
      if (i.toString !== Object.prototype.toString && !i.toString.toString().includes("[native code]"))
        return i.toString();
      var a = "";
      for (var s in i)
        t.call(i, s) && i[s] && (a = o(a, s));
      return a;
    }
    function o(i, a) {
      return a ? i ? i + " " + a : i + a : i;
    }
    e.exports ? (n.default = n, e.exports = n) : window.classNames = n;
  })();
})(nn);
var Cs = nn.exports;
const yt = /* @__PURE__ */ xs(Cs), {
  SvelteComponent: js,
  assign: we,
  check_outros: Es,
  claim_component: Is,
  component_subscribe: _e,
  compute_rest_props: bt,
  create_component: Fs,
  create_slot: Ms,
  destroy_component: Rs,
  detach: rn,
  empty: se,
  exclude_internal_props: Ls,
  flush: j,
  get_all_dirty_from_scope: Ds,
  get_slot_changes: Ns,
  get_spread_object: he,
  get_spread_update: Ks,
  group_outros: Us,
  handle_promise: Gs,
  init: zs,
  insert_hydration: on,
  mount_component: Bs,
  noop: w,
  safe_not_equal: Hs,
  transition_in: H,
  transition_out: Q,
  update_await_block_branch: qs,
  update_slot_base: Xs
} = window.__gradio__svelte__internal;
function mt(e) {
  let t, n, r = {
    ctx: e,
    current: null,
    token: null,
    hasCatch: !1,
    pending: Ys,
    then: Zs,
    catch: Js,
    value: 24,
    blocks: [, , ,]
  };
  return Gs(
    /*AwaitedSender*/
    e[3],
    r
  ), {
    c() {
      t = se(), r.block.c();
    },
    l(o) {
      t = se(), r.block.l(o);
    },
    m(o, i) {
      on(o, t, i), r.block.m(o, r.anchor = i), r.mount = () => t.parentNode, r.anchor = t, n = !0;
    },
    p(o, i) {
      e = o, qs(r, e, i);
    },
    i(o) {
      n || (H(r.block), n = !0);
    },
    o(o) {
      for (let i = 0; i < 3; i += 1) {
        const a = r.blocks[i];
        Q(a);
      }
      n = !1;
    },
    d(o) {
      o && rn(t), r.block.d(o), r.token = null, r = null;
    }
  };
}
function Js(e) {
  return {
    c: w,
    l: w,
    m: w,
    p: w,
    i: w,
    o: w,
    d: w
  };
}
function Zs(e) {
  let t, n;
  const r = [
    {
      style: (
        /*$mergedProps*/
        e[1].elem_style
      )
    },
    {
      className: yt(
        /*$mergedProps*/
        e[1].elem_classes,
        "ms-gr-antdx-sender"
      )
    },
    {
      id: (
        /*$mergedProps*/
        e[1].elem_id
      )
    },
    /*$mergedProps*/
    e[1].restProps,
    /*$mergedProps*/
    e[1].props,
    _t(
      /*$mergedProps*/
      e[1],
      {
        key_press: "keyPress",
        paste_file: "pasteFile",
        key_down: "keyDown",
        allow_speech_recording_change: "allowSpeech_recordingChange"
      }
    ),
    {
      slots: (
        /*$slots*/
        e[2]
      )
    },
    {
      value: (
        /*$mergedProps*/
        e[1].props.value ?? /*$mergedProps*/
        e[1].value
      )
    },
    {
      setSlotParams: (
        /*setSlotParams*/
        e[6]
      )
    },
    {
      onValueChange: (
        /*func*/
        e[20]
      )
    },
    {
      upload: (
        /*upload*/
        e[8]
      )
    }
  ];
  let o = {
    $$slots: {
      default: [Ws]
    },
    $$scope: {
      ctx: e
    }
  };
  for (let i = 0; i < r.length; i += 1)
    o = we(o, r[i]);
  return t = new /*Sender*/
  e[24]({
    props: o
  }), {
    c() {
      Fs(t.$$.fragment);
    },
    l(i) {
      Is(t.$$.fragment, i);
    },
    m(i, a) {
      Bs(t, i, a), n = !0;
    },
    p(i, a) {
      const s = a & /*$mergedProps, $slots, setSlotParams, value, upload*/
      327 ? Ks(r, [a & /*$mergedProps*/
      2 && {
        style: (
          /*$mergedProps*/
          i[1].elem_style
        )
      }, a & /*$mergedProps*/
      2 && {
        className: yt(
          /*$mergedProps*/
          i[1].elem_classes,
          "ms-gr-antdx-sender"
        )
      }, a & /*$mergedProps*/
      2 && {
        id: (
          /*$mergedProps*/
          i[1].elem_id
        )
      }, a & /*$mergedProps*/
      2 && he(
        /*$mergedProps*/
        i[1].restProps
      ), a & /*$mergedProps*/
      2 && he(
        /*$mergedProps*/
        i[1].props
      ), a & /*$mergedProps*/
      2 && he(_t(
        /*$mergedProps*/
        i[1],
        {
          key_press: "keyPress",
          paste_file: "pasteFile",
          key_down: "keyDown",
          allow_speech_recording_change: "allowSpeech_recordingChange"
        }
      )), a & /*$slots*/
      4 && {
        slots: (
          /*$slots*/
          i[2]
        )
      }, a & /*$mergedProps*/
      2 && {
        value: (
          /*$mergedProps*/
          i[1].props.value ?? /*$mergedProps*/
          i[1].value
        )
      }, a & /*setSlotParams*/
      64 && {
        setSlotParams: (
          /*setSlotParams*/
          i[6]
        )
      }, a & /*value*/
      1 && {
        onValueChange: (
          /*func*/
          i[20]
        )
      }, a & /*upload*/
      256 && {
        upload: (
          /*upload*/
          i[8]
        )
      }]) : {};
      a & /*$$scope*/
      2097152 && (s.$$scope = {
        dirty: a,
        ctx: i
      }), t.$set(s);
    },
    i(i) {
      n || (H(t.$$.fragment, i), n = !0);
    },
    o(i) {
      Q(t.$$.fragment, i), n = !1;
    },
    d(i) {
      Rs(t, i);
    }
  };
}
function Ws(e) {
  let t;
  const n = (
    /*#slots*/
    e[19].default
  ), r = Ms(
    n,
    e,
    /*$$scope*/
    e[21],
    null
  );
  return {
    c() {
      r && r.c();
    },
    l(o) {
      r && r.l(o);
    },
    m(o, i) {
      r && r.m(o, i), t = !0;
    },
    p(o, i) {
      r && r.p && (!t || i & /*$$scope*/
      2097152) && Xs(
        r,
        n,
        o,
        /*$$scope*/
        o[21],
        t ? Ns(
          n,
          /*$$scope*/
          o[21],
          i,
          null
        ) : Ds(
          /*$$scope*/
          o[21]
        ),
        null
      );
    },
    i(o) {
      t || (H(r, o), t = !0);
    },
    o(o) {
      Q(r, o), t = !1;
    },
    d(o) {
      r && r.d(o);
    }
  };
}
function Ys(e) {
  return {
    c: w,
    l: w,
    m: w,
    p: w,
    i: w,
    o: w,
    d: w
  };
}
function Qs(e) {
  let t, n, r = (
    /*$mergedProps*/
    e[1].visible && mt(e)
  );
  return {
    c() {
      r && r.c(), t = se();
    },
    l(o) {
      r && r.l(o), t = se();
    },
    m(o, i) {
      r && r.m(o, i), on(o, t, i), n = !0;
    },
    p(o, [i]) {
      /*$mergedProps*/
      o[1].visible ? r ? (r.p(o, i), i & /*$mergedProps*/
      2 && H(r, 1)) : (r = mt(o), r.c(), H(r, 1), r.m(t.parentNode, t)) : r && (Us(), Q(r, 1, 1, () => {
        r = null;
      }), Es());
    },
    i(o) {
      n || (H(r), n = !0);
    },
    o(o) {
      Q(r), n = !1;
    },
    d(o) {
      o && rn(t), r && r.d(o);
    }
  };
}
function Vs(e, t, n) {
  const r = ["gradio", "props", "_internal", "root", "value", "as_item", "visible", "elem_id", "elem_classes", "elem_style"];
  let o = bt(t, r), i, a, s, {
    $$slots: u = {},
    $$scope: l
  } = t;
  const f = us(() => import("./sender-HUMhYmAZ.js"));
  let {
    gradio: h
  } = t, {
    props: c = {}
  } = t;
  const p = M(c);
  _e(e, p, (d) => n(18, i = d));
  let {
    _internal: _ = {}
  } = t, {
    root: b
  } = t, {
    value: g = ""
  } = t, {
    as_item: v
  } = t, {
    visible: T = !0
  } = t, {
    elem_id: P = ""
  } = t, {
    elem_classes: C = []
  } = t, {
    elem_style: A = {}
  } = t;
  const [Le, an] = ws({
    gradio: h,
    props: i,
    _internal: _,
    visible: T,
    elem_id: P,
    elem_classes: C,
    elem_style: A,
    as_item: v,
    value: g,
    restProps: o
  });
  _e(e, Le, (d) => n(1, a = d));
  const sn = vs(), De = hs();
  _e(e, De, (d) => n(2, s = d));
  const un = async (d) => await h.client.upload(await $s(d), b) || [], ln = (d) => {
    n(0, g = d);
  };
  return e.$$set = (d) => {
    t = we(we({}, t), Ls(d)), n(23, o = bt(t, r)), "gradio" in d && n(9, h = d.gradio), "props" in d && n(10, c = d.props), "_internal" in d && n(11, _ = d._internal), "root" in d && n(12, b = d.root), "value" in d && n(0, g = d.value), "as_item" in d && n(13, v = d.as_item), "visible" in d && n(14, T = d.visible), "elem_id" in d && n(15, P = d.elem_id), "elem_classes" in d && n(16, C = d.elem_classes), "elem_style" in d && n(17, A = d.elem_style), "$$scope" in d && n(21, l = d.$$scope);
  }, e.$$.update = () => {
    e.$$.dirty & /*props*/
    1024 && p.update((d) => ({
      ...d,
      ...c
    })), an({
      gradio: h,
      props: i,
      _internal: _,
      visible: T,
      elem_id: P,
      elem_classes: C,
      elem_style: A,
      as_item: v,
      value: g,
      restProps: o
    });
  }, [g, a, s, f, p, Le, sn, De, un, h, c, _, b, v, T, P, C, A, i, u, ln, l];
}
class ru extends js {
  constructor(t) {
    super(), zs(this, t, Vs, Qs, Hs, {
      gradio: 9,
      props: 10,
      _internal: 11,
      root: 12,
      value: 0,
      as_item: 13,
      visible: 14,
      elem_id: 15,
      elem_classes: 16,
      elem_style: 17
    });
  }
  get gradio() {
    return this.$$.ctx[9];
  }
  set gradio(t) {
    this.$$set({
      gradio: t
    }), j();
  }
  get props() {
    return this.$$.ctx[10];
  }
  set props(t) {
    this.$$set({
      props: t
    }), j();
  }
  get _internal() {
    return this.$$.ctx[11];
  }
  set _internal(t) {
    this.$$set({
      _internal: t
    }), j();
  }
  get root() {
    return this.$$.ctx[12];
  }
  set root(t) {
    this.$$set({
      root: t
    }), j();
  }
  get value() {
    return this.$$.ctx[0];
  }
  set value(t) {
    this.$$set({
      value: t
    }), j();
  }
  get as_item() {
    return this.$$.ctx[13];
  }
  set as_item(t) {
    this.$$set({
      as_item: t
    }), j();
  }
  get visible() {
    return this.$$.ctx[14];
  }
  set visible(t) {
    this.$$set({
      visible: t
    }), j();
  }
  get elem_id() {
    return this.$$.ctx[15];
  }
  set elem_id(t) {
    this.$$set({
      elem_id: t
    }), j();
  }
  get elem_classes() {
    return this.$$.ctx[16];
  }
  set elem_classes(t) {
    this.$$set({
      elem_classes: t
    }), j();
  }
  get elem_style() {
    return this.$$.ctx[17];
  }
  set elem_style(t) {
    this.$$set({
      elem_style: t
    }), j();
  }
}
export {
  ru as I,
  M as Z,
  V as a,
  Re as b,
  yt as c,
  At as d,
  tu as g,
  Pe as i,
  I as r
};
