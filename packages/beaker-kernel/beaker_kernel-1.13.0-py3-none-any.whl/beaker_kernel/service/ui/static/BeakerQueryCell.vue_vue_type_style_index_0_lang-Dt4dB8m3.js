import { k as bt, l as Et, B as kt, __tla as __tla_0 } from "./DebugPanel.vue_vue_type_style_index_0_lang-PW_f_WLw.js";
import { d as le, n as ye, i as J, r as j, p as Xe, f as ue, y as z, o as M, R as ie, J as ge, K, B as T, E as F, u as h, L as X, z as Ee, g as Ue, af as Bt, M as ne, I as ee, a1 as Me, a0 as Ct, $ as it, Q as Oe, aj as Ae, ak as Fe, ac as It, al as _t, am as At, U as ot, j as se, a9 as Ft, an as $t, a as me, ao as lt, ap as Je, N as St, _ as ae, w as fe, a8 as Ut, G as Te, A as Re, S as Tt, ag as Rt, V as Dt, W as Nt, X as Qe, Y as Mt, Z as Ze, aq as Ot, ar as Pt } from "./primevue-1TEWPnDt.js";
import { _ as Be } from "./_plugin-vue_export-helper-DlAUqK2U.js";
import { r as Lt, g as qt, l as ke } from "./jupyterlab-C2EV-Dpr.js";
import { f as zt, d as st, u as Vt, i as Ye, e as $e, __tla as __tla_1 } from "./BeakerRawCell.vue_vue_type_style_index_0_lang-DHQ28atJ.js";
import { d as De, g as Ne, __tla as __tla_2 } from "./index-D-jLGYR3.js";
let Y0, nn, rn, K0, en, tn;
let __tla = Promise.all([
    (()=>{
        try {
            return __tla_0;
        } catch  {}
    })(),
    (()=>{
        try {
            return __tla_1;
        } catch  {}
    })(),
    (()=>{
        try {
            return __tla_2;
        } catch  {}
    })()
]).then(async ()=>{
    const jt = le({
        props: [
            "cellMap",
            "noEmptyStartingCell"
        ],
        setup (p) {
            const a = J("session"), f = J("beakerSession"), c = j(a.notebook), g = j(null);
            Xe("cell-component-mapping", p.cellMap);
            const b = ue(()=>a?.notebook?.cells?.length || 0);
            return {
                session: a,
                beakerSession: f,
                notebook: c,
                selectedCellId: g,
                cellCount: b
            };
        },
        methods: {
            selectCell (p, a = !1, f = void 0) {
                if (p === void 0) return "";
                let c;
                return typeof p == "string" ? c = p : Object.hasOwn(p, "cell") ? c = p.cell.id : c = p.id, this.selectedCellId !== c && (this.selectedCellId = c), ye(()=>{
                    this.scrollCellIntoView(this.selectedCell()), a && this.selectedCell().enter(f);
                }), this.selectedCellId;
            },
            scrollCellIntoView (p) {
                const a = p?.$?.vnode?.el;
                if (!a) return;
                const f = a.closest(".beaker-cell") ?? a;
                Et(f, {
                    scrollMode: "if-needed",
                    block: "nearest",
                    inline: "nearest"
                });
            },
            selectedCell () {
                const p = this.beakerSession.findNotebookCellById(this.selectedCellId);
                if (p) return p;
                if (this.notebook.cells.length > 0) return this.selectedCellId = this.notebook.cells[0].id, this.beakerSession.findNotebookCellById(this.selectedCellId);
            },
            nextCell (p) {
                let a;
                if (p === void 0 ? a = this.notebook.cells.indexOf(this.selectedCell().cell) : a = this.notebook.cells.indexOf(p), a >= 0 && a < this.cellCount - 1) {
                    const c = this.notebook.cells[a + 1].id;
                    return this.beakerSession.findNotebookCellById(c);
                }
                return null;
            },
            prevCell (p) {
                let a;
                if (p === void 0 ? a = this.notebook.cells.indexOf(this.selectedCell().cell) : a = this.notebook.cells.indexOf(p), a > 0) {
                    const c = this.notebook.cells[a - 1].id;
                    return this.beakerSession.findNotebookCellById(c);
                }
                return null;
            },
            selectNextCell (p, a = !1) {
                const f = this.nextCell(p);
                if (f) return this.selectCell(f, a);
                for (const c of this.notebook.cells)if (c.children) {
                    const g = c.children.indexOf(p);
                    if (g === -1) continue;
                    return g <= c.children.length - 1 ? this.selectNextCell(c) : this.selectCell(c.children[g + 1], a);
                }
                return null;
            },
            selectPrevCell (p, a = !1) {
                const f = this.prevCell(p);
                return f ? this.selectCell(f, a) : null;
            },
            insertCellBefore (p, a, f = !1) {
                p === void 0 && (p = this.selectedCell()), a === void 0 && (a = new this.defaultCellModel({
                    source: ""
                }));
                const c = p === void 0 ? this.notebook.cells.length - 1 : this.notebook.cells.findIndex((g)=>g === p.cell);
                return this.notebook.cells.splice(c, 0, a), ye(()=>this.selectCell(a, f)), a;
            },
            insertCellAfter (p, a, f = !1) {
                p === void 0 && (p = this.selectedCell()), a === void 0 && (a = new this.defaultCellModel({
                    source: ""
                }));
                const c = p === void 0 ? this.notebook.cells.length - 1 : this.notebook.cells.findIndex((g)=>g === p.cell);
                return this.notebook.cells.splice(c + 1, 0, a), ye(()=>this.selectCell(a, f)), a;
            },
            removeCell (p) {
                p === void 0 && (p = this.selectedCell());
                const a = this.notebook.cells.findIndex((f)=>f === p.cell);
                if (a > -1) return p.cell.id === this.selectedCellId && (this.selectNextCell() || this.selectPrevCell()), this.notebook.cutCell(a);
            },
            convertCellType (p, a) {
                const f = this.notebook.cells.indexOf(p);
                if (f === -1) {
                    console.warn("attempted to convert cell not found in parent cell in place; cell not found");
                    return;
                }
                if (!Object.keys(this.cellMap).includes(a)) {
                    console.warn("invalid cell type provided for conversion target");
                    return;
                }
                const c = new this.cellMap[a].modelClass({
                    ...p
                });
                c.cell_type = a, this.notebook.cells.splice(f, 1, c);
            }
        },
        computed: {
            defaultCellModel () {
                return this.cellMap && this.cellMap.length > 0 ? Object.values(this.cellMap)[0].modelClass : bt;
            }
        },
        beforeMount () {
            if (Xe("notebook", this), this.beakerSession.notebookComponent = this, this.cellCount === 0) {
                if (this.noEmptyStartingCell) return;
                this.session.addCodeCell("");
            }
        },
        mounted () {
            this.noEmptyStartingCell || this.selectedCell() || ye(()=>{
                this.notebook.cells.length > 0 && this.selectCell(this.notebook.cells[0].id);
            });
        }
    }), Gt = {
        class: "beaker-notebook"
    };
    function Ht(p, a, f, c, g, b) {
        return M(), z("div", Gt, [
            ie(p.$slots, "default")
        ]);
    }
    Y0 = Be(jt, [
        [
            "render",
            Ht
        ]
    ]);
    var we = {
        exports: {}
    }, xe = {
        exports: {}
    }, Se = {}, he = {}, We;
    function Xt() {
        if (We) return he;
        We = 1, he.byteLength = o, he.toByteArray = m, he.fromByteArray = L;
        for(var p = [], a = [], f = typeof Uint8Array < "u" ? Uint8Array : Array, c = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/", g = 0, b = c.length; g < b; ++g)p[g] = c[g], a[c.charCodeAt(g)] = g;
        a[45] = 62, a[95] = 63;
        function d(y) {
            var I = y.length;
            if (I % 4 > 0) throw new Error("Invalid string. Length must be a multiple of 4");
            var S = y.indexOf("=");
            S === -1 && (S = I);
            var O = S === I ? 0 : 4 - S % 4;
            return [
                S,
                O
            ];
        }
        function o(y) {
            var I = d(y), S = I[0], O = I[1];
            return (S + O) * 3 / 4 - O;
        }
        function k(y, I, S) {
            return (I + S) * 3 / 4 - S;
        }
        function m(y) {
            var I, S = d(y), O = S[0], P = S[1], B = new f(k(y, O, P)), w = 0, A = P > 0 ? O - 4 : O, _;
            for(_ = 0; _ < A; _ += 4)I = a[y.charCodeAt(_)] << 18 | a[y.charCodeAt(_ + 1)] << 12 | a[y.charCodeAt(_ + 2)] << 6 | a[y.charCodeAt(_ + 3)], B[w++] = I >> 16 & 255, B[w++] = I >> 8 & 255, B[w++] = I & 255;
            return P === 2 && (I = a[y.charCodeAt(_)] << 2 | a[y.charCodeAt(_ + 1)] >> 4, B[w++] = I & 255), P === 1 && (I = a[y.charCodeAt(_)] << 10 | a[y.charCodeAt(_ + 1)] << 4 | a[y.charCodeAt(_ + 2)] >> 2, B[w++] = I >> 8 & 255, B[w++] = I & 255), B;
        }
        function x(y) {
            return p[y >> 18 & 63] + p[y >> 12 & 63] + p[y >> 6 & 63] + p[y & 63];
        }
        function v(y, I, S) {
            for(var O, P = [], B = I; B < S; B += 3)O = (y[B] << 16 & 16711680) + (y[B + 1] << 8 & 65280) + (y[B + 2] & 255), P.push(x(O));
            return P.join("");
        }
        function L(y) {
            for(var I, S = y.length, O = S % 3, P = [], B = 16383, w = 0, A = S - O; w < A; w += B)P.push(v(y, w, w + B > A ? A : w + B));
            return O === 1 ? (I = y[S - 1], P.push(p[I >> 2] + p[I << 4 & 63] + "==")) : O === 2 && (I = (y[S - 2] << 8) + y[S - 1], P.push(p[I >> 10] + p[I >> 4 & 63] + p[I << 2 & 63] + "=")), P.join("");
        }
        return he;
    }
    var be = {};
    var Ke;
    function Jt() {
        return Ke || (Ke = 1, be.read = function(p, a, f, c, g) {
            var b, d, o = g * 8 - c - 1, k = (1 << o) - 1, m = k >> 1, x = -7, v = f ? g - 1 : 0, L = f ? -1 : 1, y = p[a + v];
            for(v += L, b = y & (1 << -x) - 1, y >>= -x, x += o; x > 0; b = b * 256 + p[a + v], v += L, x -= 8);
            for(d = b & (1 << -x) - 1, b >>= -x, x += c; x > 0; d = d * 256 + p[a + v], v += L, x -= 8);
            if (b === 0) b = 1 - m;
            else {
                if (b === k) return d ? NaN : (y ? -1 : 1) * (1 / 0);
                d = d + Math.pow(2, c), b = b - m;
            }
            return (y ? -1 : 1) * d * Math.pow(2, b - c);
        }, be.write = function(p, a, f, c, g, b) {
            var d, o, k, m = b * 8 - g - 1, x = (1 << m) - 1, v = x >> 1, L = g === 23 ? Math.pow(2, -24) - Math.pow(2, -77) : 0, y = c ? 0 : b - 1, I = c ? 1 : -1, S = a < 0 || a === 0 && 1 / a < 0 ? 1 : 0;
            for(a = Math.abs(a), isNaN(a) || a === 1 / 0 ? (o = isNaN(a) ? 1 : 0, d = x) : (d = Math.floor(Math.log(a) / Math.LN2), a * (k = Math.pow(2, -d)) < 1 && (d--, k *= 2), d + v >= 1 ? a += L / k : a += L * Math.pow(2, 1 - v), a * k >= 2 && (d++, k /= 2), d + v >= x ? (o = 0, d = x) : d + v >= 1 ? (o = (a * k - 1) * Math.pow(2, g), d = d + v) : (o = a * Math.pow(2, v - 1) * Math.pow(2, g), d = 0)); g >= 8; p[f + y] = o & 255, y += I, o /= 256, g -= 8);
            for(d = d << g | o, m += g; m > 0; p[f + y] = d & 255, y += I, d /= 256, m -= 8);
            p[f + y - I] |= S * 128;
        }), be;
    }
    var et;
    function Qt() {
        return et || (et = 1, function(p) {
            const a = Xt(), f = Jt(), c = typeof Symbol == "function" && typeof Symbol.for == "function" ? Symbol.for("nodejs.util.inspect.custom") : null;
            p.Buffer = o, p.SlowBuffer = B, p.INSPECT_MAX_BYTES = 50;
            const g = 2147483647;
            p.kMaxLength = g, o.TYPED_ARRAY_SUPPORT = b(), !o.TYPED_ARRAY_SUPPORT && typeof console < "u" && typeof console.error == "function" && console.error("This browser lacks typed array (Uint8Array) support which is required by `buffer` v5.x. Use `buffer` v4.x if you require old browser support.");
            function b() {
                try {
                    const n = new Uint8Array(1), e = {
                        foo: function() {
                            return 42;
                        }
                    };
                    return Object.setPrototypeOf(e, Uint8Array.prototype), Object.setPrototypeOf(n, e), n.foo() === 42;
                } catch  {
                    return !1;
                }
            }
            Object.defineProperty(o.prototype, "parent", {
                enumerable: !0,
                get: function() {
                    if (o.isBuffer(this)) return this.buffer;
                }
            }), Object.defineProperty(o.prototype, "offset", {
                enumerable: !0,
                get: function() {
                    if (o.isBuffer(this)) return this.byteOffset;
                }
            });
            function d(n) {
                if (n > g) throw new RangeError('The value "' + n + '" is invalid for option "size"');
                const e = new Uint8Array(n);
                return Object.setPrototypeOf(e, o.prototype), e;
            }
            function o(n, e, t) {
                if (typeof n == "number") {
                    if (typeof e == "string") throw new TypeError('The "string" argument must be of type string. Received type number');
                    return v(n);
                }
                return k(n, e, t);
            }
            o.poolSize = 8192;
            function k(n, e, t) {
                if (typeof n == "string") return L(n, e);
                if (ArrayBuffer.isView(n)) return I(n);
                if (n == null) throw new TypeError("The first argument must be one of type string, Buffer, ArrayBuffer, Array, or Array-like Object. Received type " + typeof n);
                if (re(n, ArrayBuffer) || n && re(n.buffer, ArrayBuffer) || typeof SharedArrayBuffer < "u" && (re(n, SharedArrayBuffer) || n && re(n.buffer, SharedArrayBuffer))) return S(n, e, t);
                if (typeof n == "number") throw new TypeError('The "value" argument must not be of type number. Received type number');
                const r = n.valueOf && n.valueOf();
                if (r != null && r !== n) return o.from(r, e, t);
                const i = O(n);
                if (i) return i;
                if (typeof Symbol < "u" && Symbol.toPrimitive != null && typeof n[Symbol.toPrimitive] == "function") return o.from(n[Symbol.toPrimitive]("string"), e, t);
                throw new TypeError("The first argument must be one of type string, Buffer, ArrayBuffer, Array, or Array-like Object. Received type " + typeof n);
            }
            o.from = function(n, e, t) {
                return k(n, e, t);
            }, Object.setPrototypeOf(o.prototype, Uint8Array.prototype), Object.setPrototypeOf(o, Uint8Array);
            function m(n) {
                if (typeof n != "number") throw new TypeError('"size" argument must be of type number');
                if (n < 0) throw new RangeError('The value "' + n + '" is invalid for option "size"');
            }
            function x(n, e, t) {
                return m(n), n <= 0 ? d(n) : e !== void 0 ? typeof t == "string" ? d(n).fill(e, t) : d(n).fill(e) : d(n);
            }
            o.alloc = function(n, e, t) {
                return x(n, e, t);
            };
            function v(n) {
                return m(n), d(n < 0 ? 0 : P(n) | 0);
            }
            o.allocUnsafe = function(n) {
                return v(n);
            }, o.allocUnsafeSlow = function(n) {
                return v(n);
            };
            function L(n, e) {
                if ((typeof e != "string" || e === "") && (e = "utf8"), !o.isEncoding(e)) throw new TypeError("Unknown encoding: " + e);
                const t = w(n, e) | 0;
                let r = d(t);
                const i = r.write(n, e);
                return i !== t && (r = r.slice(0, i)), r;
            }
            function y(n) {
                const e = n.length < 0 ? 0 : P(n.length) | 0, t = d(e);
                for(let r = 0; r < e; r += 1)t[r] = n[r] & 255;
                return t;
            }
            function I(n) {
                if (re(n, Uint8Array)) {
                    const e = new Uint8Array(n);
                    return S(e.buffer, e.byteOffset, e.byteLength);
                }
                return y(n);
            }
            function S(n, e, t) {
                if (e < 0 || n.byteLength < e) throw new RangeError('"offset" is outside of buffer bounds');
                if (n.byteLength < e + (t || 0)) throw new RangeError('"length" is outside of buffer bounds');
                let r;
                return e === void 0 && t === void 0 ? r = new Uint8Array(n) : t === void 0 ? r = new Uint8Array(n, e) : r = new Uint8Array(n, e, t), Object.setPrototypeOf(r, o.prototype), r;
            }
            function O(n) {
                if (o.isBuffer(n)) {
                    const e = P(n.length) | 0, t = d(e);
                    return t.length === 0 || n.copy(t, 0, 0, e), t;
                }
                if (n.length !== void 0) return typeof n.length != "number" || _e(n.length) ? d(0) : y(n);
                if (n.type === "Buffer" && Array.isArray(n.data)) return y(n.data);
            }
            function P(n) {
                if (n >= g) throw new RangeError("Attempt to allocate Buffer larger than maximum size: 0x" + g.toString(16) + " bytes");
                return n | 0;
            }
            function B(n) {
                return +n != n && (n = 0), o.alloc(+n);
            }
            o.isBuffer = function(e) {
                return e != null && e._isBuffer === !0 && e !== o.prototype;
            }, o.compare = function(e, t) {
                if (re(e, Uint8Array) && (e = o.from(e, e.offset, e.byteLength)), re(t, Uint8Array) && (t = o.from(t, t.offset, t.byteLength)), !o.isBuffer(e) || !o.isBuffer(t)) throw new TypeError('The "buf1", "buf2" arguments must be one of type Buffer or Uint8Array');
                if (e === t) return 0;
                let r = e.length, i = t.length;
                for(let l = 0, s = Math.min(r, i); l < s; ++l)if (e[l] !== t[l]) {
                    r = e[l], i = t[l];
                    break;
                }
                return r < i ? -1 : i < r ? 1 : 0;
            }, o.isEncoding = function(e) {
                switch(String(e).toLowerCase()){
                    case "hex":
                    case "utf8":
                    case "utf-8":
                    case "ascii":
                    case "latin1":
                    case "binary":
                    case "base64":
                    case "ucs2":
                    case "ucs-2":
                    case "utf16le":
                    case "utf-16le":
                        return !0;
                    default:
                        return !1;
                }
            }, o.concat = function(e, t) {
                if (!Array.isArray(e)) throw new TypeError('"list" argument must be an Array of Buffers');
                if (e.length === 0) return o.alloc(0);
                let r;
                if (t === void 0) for(t = 0, r = 0; r < e.length; ++r)t += e[r].length;
                const i = o.allocUnsafe(t);
                let l = 0;
                for(r = 0; r < e.length; ++r){
                    let s = e[r];
                    if (re(s, Uint8Array)) l + s.length > i.length ? (o.isBuffer(s) || (s = o.from(s)), s.copy(i, l)) : Uint8Array.prototype.set.call(i, s, l);
                    else if (o.isBuffer(s)) s.copy(i, l);
                    else throw new TypeError('"list" argument must be an Array of Buffers');
                    l += s.length;
                }
                return i;
            };
            function w(n, e) {
                if (o.isBuffer(n)) return n.length;
                if (ArrayBuffer.isView(n) || re(n, ArrayBuffer)) return n.byteLength;
                if (typeof n != "string") throw new TypeError('The "string" argument must be one of type string, Buffer, or ArrayBuffer. Received type ' + typeof n);
                const t = n.length, r = arguments.length > 2 && arguments[2] === !0;
                if (!r && t === 0) return 0;
                let i = !1;
                for(;;)switch(e){
                    case "ascii":
                    case "latin1":
                    case "binary":
                        return t;
                    case "utf8":
                    case "utf-8":
                        return Ie(n).length;
                    case "ucs2":
                    case "ucs-2":
                    case "utf16le":
                    case "utf-16le":
                        return t * 2;
                    case "hex":
                        return t >>> 1;
                    case "base64":
                        return He(n).length;
                    default:
                        if (i) return r ? -1 : Ie(n).length;
                        e = ("" + e).toLowerCase(), i = !0;
                }
            }
            o.byteLength = w;
            function A(n, e, t) {
                let r = !1;
                if ((e === void 0 || e < 0) && (e = 0), e > this.length || ((t === void 0 || t > this.length) && (t = this.length), t <= 0) || (t >>>= 0, e >>>= 0, t <= e)) return "";
                for(n || (n = "utf8");;)switch(n){
                    case "hex":
                        return ft(this, e, t);
                    case "utf8":
                    case "utf-8":
                        return Y(this, e, t);
                    case "ascii":
                        return ct(this, e, t);
                    case "latin1":
                    case "binary":
                        return pt(this, e, t);
                    case "base64":
                        return Z(this, e, t);
                    case "ucs2":
                    case "ucs-2":
                    case "utf16le":
                    case "utf-16le":
                        return dt(this, e, t);
                    default:
                        if (r) throw new TypeError("Unknown encoding: " + n);
                        n = (n + "").toLowerCase(), r = !0;
                }
            }
            o.prototype._isBuffer = !0;
            function _(n, e, t) {
                const r = n[e];
                n[e] = n[t], n[t] = r;
            }
            o.prototype.swap16 = function() {
                const e = this.length;
                if (e % 2 !== 0) throw new RangeError("Buffer size must be a multiple of 16-bits");
                for(let t = 0; t < e; t += 2)_(this, t, t + 1);
                return this;
            }, o.prototype.swap32 = function() {
                const e = this.length;
                if (e % 4 !== 0) throw new RangeError("Buffer size must be a multiple of 32-bits");
                for(let t = 0; t < e; t += 4)_(this, t, t + 3), _(this, t + 1, t + 2);
                return this;
            }, o.prototype.swap64 = function() {
                const e = this.length;
                if (e % 8 !== 0) throw new RangeError("Buffer size must be a multiple of 64-bits");
                for(let t = 0; t < e; t += 8)_(this, t, t + 7), _(this, t + 1, t + 6), _(this, t + 2, t + 5), _(this, t + 3, t + 4);
                return this;
            }, o.prototype.toString = function() {
                const e = this.length;
                return e === 0 ? "" : arguments.length === 0 ? Y(this, 0, e) : A.apply(this, arguments);
            }, o.prototype.toLocaleString = o.prototype.toString, o.prototype.equals = function(e) {
                if (!o.isBuffer(e)) throw new TypeError("Argument must be a Buffer");
                return this === e ? !0 : o.compare(this, e) === 0;
            }, o.prototype.inspect = function() {
                let e = "";
                const t = p.INSPECT_MAX_BYTES;
                return e = this.toString("hex", 0, t).replace(/(.{2})/g, "$1 ").trim(), this.length > t && (e += " ... "), "<Buffer " + e + ">";
            }, c && (o.prototype[c] = o.prototype.inspect), o.prototype.compare = function(e, t, r, i, l) {
                if (re(e, Uint8Array) && (e = o.from(e, e.offset, e.byteLength)), !o.isBuffer(e)) throw new TypeError('The "target" argument must be one of type Buffer or Uint8Array. Received type ' + typeof e);
                if (t === void 0 && (t = 0), r === void 0 && (r = e ? e.length : 0), i === void 0 && (i = 0), l === void 0 && (l = this.length), t < 0 || r > e.length || i < 0 || l > this.length) throw new RangeError("out of range index");
                if (i >= l && t >= r) return 0;
                if (i >= l) return -1;
                if (t >= r) return 1;
                if (t >>>= 0, r >>>= 0, i >>>= 0, l >>>= 0, this === e) return 0;
                let s = l - i, D = r - t;
                const G = Math.min(s, D), V = this.slice(i, l), H = e.slice(t, r);
                for(let q = 0; q < G; ++q)if (V[q] !== H[q]) {
                    s = V[q], D = H[q];
                    break;
                }
                return s < D ? -1 : D < s ? 1 : 0;
            };
            function $(n, e, t, r, i) {
                if (n.length === 0) return -1;
                if (typeof t == "string" ? (r = t, t = 0) : t > 2147483647 ? t = 2147483647 : t < -2147483648 && (t = -2147483648), t = +t, _e(t) && (t = i ? 0 : n.length - 1), t < 0 && (t = n.length + t), t >= n.length) {
                    if (i) return -1;
                    t = n.length - 1;
                } else if (t < 0) if (i) t = 0;
                else return -1;
                if (typeof e == "string" && (e = o.from(e, r)), o.isBuffer(e)) return e.length === 0 ? -1 : R(n, e, t, r, i);
                if (typeof e == "number") return e = e & 255, typeof Uint8Array.prototype.indexOf == "function" ? i ? Uint8Array.prototype.indexOf.call(n, e, t) : Uint8Array.prototype.lastIndexOf.call(n, e, t) : R(n, [
                    e
                ], t, r, i);
                throw new TypeError("val must be string, number or Buffer");
            }
            function R(n, e, t, r, i) {
                let l = 1, s = n.length, D = e.length;
                if (r !== void 0 && (r = String(r).toLowerCase(), r === "ucs2" || r === "ucs-2" || r === "utf16le" || r === "utf-16le")) {
                    if (n.length < 2 || e.length < 2) return -1;
                    l = 2, s /= 2, D /= 2, t /= 2;
                }
                function G(H, q) {
                    return l === 1 ? H[q] : H.readUInt16BE(q * l);
                }
                let V;
                if (i) {
                    let H = -1;
                    for(V = t; V < s; V++)if (G(n, V) === G(e, H === -1 ? 0 : V - H)) {
                        if (H === -1 && (H = V), V - H + 1 === D) return H * l;
                    } else H !== -1 && (V -= V - H), H = -1;
                } else for(t + D > s && (t = s - D), V = t; V >= 0; V--){
                    let H = !0;
                    for(let q = 0; q < D; q++)if (G(n, V + q) !== G(e, q)) {
                        H = !1;
                        break;
                    }
                    if (H) return V;
                }
                return -1;
            }
            o.prototype.includes = function(e, t, r) {
                return this.indexOf(e, t, r) !== -1;
            }, o.prototype.indexOf = function(e, t, r) {
                return $(this, e, t, r, !0);
            }, o.prototype.lastIndexOf = function(e, t, r) {
                return $(this, e, t, r, !1);
            };
            function E(n, e, t, r) {
                t = Number(t) || 0;
                const i = n.length - t;
                r ? (r = Number(r), r > i && (r = i)) : r = i;
                const l = e.length;
                r > l / 2 && (r = l / 2);
                let s;
                for(s = 0; s < r; ++s){
                    const D = parseInt(e.substr(s * 2, 2), 16);
                    if (_e(D)) return s;
                    n[t + s] = D;
                }
                return s;
            }
            function u(n, e, t, r) {
                return ve(Ie(e, n.length - t), n, t, r);
            }
            function C(n, e, t, r) {
                return ve(gt(e), n, t, r);
            }
            function U(n, e, t, r) {
                return ve(He(e), n, t, r);
            }
            function N(n, e, t, r) {
                return ve(vt(e, n.length - t), n, t, r);
            }
            o.prototype.write = function(e, t, r, i) {
                if (t === void 0) i = "utf8", r = this.length, t = 0;
                else if (r === void 0 && typeof t == "string") i = t, r = this.length, t = 0;
                else if (isFinite(t)) t = t >>> 0, isFinite(r) ? (r = r >>> 0, i === void 0 && (i = "utf8")) : (i = r, r = void 0);
                else throw new Error("Buffer.write(string, encoding, offset[, length]) is no longer supported");
                const l = this.length - t;
                if ((r === void 0 || r > l) && (r = l), e.length > 0 && (r < 0 || t < 0) || t > this.length) throw new RangeError("Attempt to write outside buffer bounds");
                i || (i = "utf8");
                let s = !1;
                for(;;)switch(i){
                    case "hex":
                        return E(this, e, t, r);
                    case "utf8":
                    case "utf-8":
                        return u(this, e, t, r);
                    case "ascii":
                    case "latin1":
                    case "binary":
                        return C(this, e, t, r);
                    case "base64":
                        return U(this, e, t, r);
                    case "ucs2":
                    case "ucs-2":
                    case "utf16le":
                    case "utf-16le":
                        return N(this, e, t, r);
                    default:
                        if (s) throw new TypeError("Unknown encoding: " + i);
                        i = ("" + i).toLowerCase(), s = !0;
                }
            }, o.prototype.toJSON = function() {
                return {
                    type: "Buffer",
                    data: Array.prototype.slice.call(this._arr || this, 0)
                };
            };
            function Z(n, e, t) {
                return e === 0 && t === n.length ? a.fromByteArray(n) : a.fromByteArray(n.slice(e, t));
            }
            function Y(n, e, t) {
                t = Math.min(n.length, t);
                const r = [];
                let i = e;
                for(; i < t;){
                    const l = n[i];
                    let s = null, D = l > 239 ? 4 : l > 223 ? 3 : l > 191 ? 2 : 1;
                    if (i + D <= t) {
                        let G, V, H, q;
                        switch(D){
                            case 1:
                                l < 128 && (s = l);
                                break;
                            case 2:
                                G = n[i + 1], (G & 192) === 128 && (q = (l & 31) << 6 | G & 63, q > 127 && (s = q));
                                break;
                            case 3:
                                G = n[i + 1], V = n[i + 2], (G & 192) === 128 && (V & 192) === 128 && (q = (l & 15) << 12 | (G & 63) << 6 | V & 63, q > 2047 && (q < 55296 || q > 57343) && (s = q));
                                break;
                            case 4:
                                G = n[i + 1], V = n[i + 2], H = n[i + 3], (G & 192) === 128 && (V & 192) === 128 && (H & 192) === 128 && (q = (l & 15) << 18 | (G & 63) << 12 | (V & 63) << 6 | H & 63, q > 65535 && q < 1114112 && (s = q));
                        }
                    }
                    s === null ? (s = 65533, D = 1) : s > 65535 && (s -= 65536, r.push(s >>> 10 & 1023 | 55296), s = 56320 | s & 1023), r.push(s), i += D;
                }
                return ut(r);
            }
            const W = 4096;
            function ut(n) {
                const e = n.length;
                if (e <= W) return String.fromCharCode.apply(String, n);
                let t = "", r = 0;
                for(; r < e;)t += String.fromCharCode.apply(String, n.slice(r, r += W));
                return t;
            }
            function ct(n, e, t) {
                let r = "";
                t = Math.min(n.length, t);
                for(let i = e; i < t; ++i)r += String.fromCharCode(n[i] & 127);
                return r;
            }
            function pt(n, e, t) {
                let r = "";
                t = Math.min(n.length, t);
                for(let i = e; i < t; ++i)r += String.fromCharCode(n[i]);
                return r;
            }
            function ft(n, e, t) {
                const r = n.length;
                (!e || e < 0) && (e = 0), (!t || t < 0 || t > r) && (t = r);
                let i = "";
                for(let l = e; l < t; ++l)i += wt[n[l]];
                return i;
            }
            function dt(n, e, t) {
                const r = n.slice(e, t);
                let i = "";
                for(let l = 0; l < r.length - 1; l += 2)i += String.fromCharCode(r[l] + r[l + 1] * 256);
                return i;
            }
            o.prototype.slice = function(e, t) {
                const r = this.length;
                e = ~~e, t = t === void 0 ? r : ~~t, e < 0 ? (e += r, e < 0 && (e = 0)) : e > r && (e = r), t < 0 ? (t += r, t < 0 && (t = 0)) : t > r && (t = r), t < e && (t = e);
                const i = this.subarray(e, t);
                return Object.setPrototypeOf(i, o.prototype), i;
            };
            function Q(n, e, t) {
                if (n % 1 !== 0 || n < 0) throw new RangeError("offset is not uint");
                if (n + e > t) throw new RangeError("Trying to access beyond buffer length");
            }
            o.prototype.readUintLE = o.prototype.readUIntLE = function(e, t, r) {
                e = e >>> 0, t = t >>> 0, r || Q(e, t, this.length);
                let i = this[e], l = 1, s = 0;
                for(; ++s < t && (l *= 256);)i += this[e + s] * l;
                return i;
            }, o.prototype.readUintBE = o.prototype.readUIntBE = function(e, t, r) {
                e = e >>> 0, t = t >>> 0, r || Q(e, t, this.length);
                let i = this[e + --t], l = 1;
                for(; t > 0 && (l *= 256);)i += this[e + --t] * l;
                return i;
            }, o.prototype.readUint8 = o.prototype.readUInt8 = function(e, t) {
                return e = e >>> 0, t || Q(e, 1, this.length), this[e];
            }, o.prototype.readUint16LE = o.prototype.readUInt16LE = function(e, t) {
                return e = e >>> 0, t || Q(e, 2, this.length), this[e] | this[e + 1] << 8;
            }, o.prototype.readUint16BE = o.prototype.readUInt16BE = function(e, t) {
                return e = e >>> 0, t || Q(e, 2, this.length), this[e] << 8 | this[e + 1];
            }, o.prototype.readUint32LE = o.prototype.readUInt32LE = function(e, t) {
                return e = e >>> 0, t || Q(e, 4, this.length), (this[e] | this[e + 1] << 8 | this[e + 2] << 16) + this[e + 3] * 16777216;
            }, o.prototype.readUint32BE = o.prototype.readUInt32BE = function(e, t) {
                return e = e >>> 0, t || Q(e, 4, this.length), this[e] * 16777216 + (this[e + 1] << 16 | this[e + 2] << 8 | this[e + 3]);
            }, o.prototype.readBigUInt64LE = oe(function(e) {
                e = e >>> 0, pe(e, "offset");
                const t = this[e], r = this[e + 7];
                (t === void 0 || r === void 0) && de(e, this.length - 8);
                const i = t + this[++e] * 2 ** 8 + this[++e] * 2 ** 16 + this[++e] * 2 ** 24, l = this[++e] + this[++e] * 2 ** 8 + this[++e] * 2 ** 16 + r * 2 ** 24;
                return BigInt(i) + (BigInt(l) << BigInt(32));
            }), o.prototype.readBigUInt64BE = oe(function(e) {
                e = e >>> 0, pe(e, "offset");
                const t = this[e], r = this[e + 7];
                (t === void 0 || r === void 0) && de(e, this.length - 8);
                const i = t * 2 ** 24 + this[++e] * 2 ** 16 + this[++e] * 2 ** 8 + this[++e], l = this[++e] * 2 ** 24 + this[++e] * 2 ** 16 + this[++e] * 2 ** 8 + r;
                return (BigInt(i) << BigInt(32)) + BigInt(l);
            }), o.prototype.readIntLE = function(e, t, r) {
                e = e >>> 0, t = t >>> 0, r || Q(e, t, this.length);
                let i = this[e], l = 1, s = 0;
                for(; ++s < t && (l *= 256);)i += this[e + s] * l;
                return l *= 128, i >= l && (i -= Math.pow(2, 8 * t)), i;
            }, o.prototype.readIntBE = function(e, t, r) {
                e = e >>> 0, t = t >>> 0, r || Q(e, t, this.length);
                let i = t, l = 1, s = this[e + --i];
                for(; i > 0 && (l *= 256);)s += this[e + --i] * l;
                return l *= 128, s >= l && (s -= Math.pow(2, 8 * t)), s;
            }, o.prototype.readInt8 = function(e, t) {
                return e = e >>> 0, t || Q(e, 1, this.length), this[e] & 128 ? (255 - this[e] + 1) * -1 : this[e];
            }, o.prototype.readInt16LE = function(e, t) {
                e = e >>> 0, t || Q(e, 2, this.length);
                const r = this[e] | this[e + 1] << 8;
                return r & 32768 ? r | 4294901760 : r;
            }, o.prototype.readInt16BE = function(e, t) {
                e = e >>> 0, t || Q(e, 2, this.length);
                const r = this[e + 1] | this[e] << 8;
                return r & 32768 ? r | 4294901760 : r;
            }, o.prototype.readInt32LE = function(e, t) {
                return e = e >>> 0, t || Q(e, 4, this.length), this[e] | this[e + 1] << 8 | this[e + 2] << 16 | this[e + 3] << 24;
            }, o.prototype.readInt32BE = function(e, t) {
                return e = e >>> 0, t || Q(e, 4, this.length), this[e] << 24 | this[e + 1] << 16 | this[e + 2] << 8 | this[e + 3];
            }, o.prototype.readBigInt64LE = oe(function(e) {
                e = e >>> 0, pe(e, "offset");
                const t = this[e], r = this[e + 7];
                (t === void 0 || r === void 0) && de(e, this.length - 8);
                const i = this[e + 4] + this[e + 5] * 2 ** 8 + this[e + 6] * 2 ** 16 + (r << 24);
                return (BigInt(i) << BigInt(32)) + BigInt(t + this[++e] * 2 ** 8 + this[++e] * 2 ** 16 + this[++e] * 2 ** 24);
            }), o.prototype.readBigInt64BE = oe(function(e) {
                e = e >>> 0, pe(e, "offset");
                const t = this[e], r = this[e + 7];
                (t === void 0 || r === void 0) && de(e, this.length - 8);
                const i = (t << 24) + this[++e] * 2 ** 16 + this[++e] * 2 ** 8 + this[++e];
                return (BigInt(i) << BigInt(32)) + BigInt(this[++e] * 2 ** 24 + this[++e] * 2 ** 16 + this[++e] * 2 ** 8 + r);
            }), o.prototype.readFloatLE = function(e, t) {
                return e = e >>> 0, t || Q(e, 4, this.length), f.read(this, e, !0, 23, 4);
            }, o.prototype.readFloatBE = function(e, t) {
                return e = e >>> 0, t || Q(e, 4, this.length), f.read(this, e, !1, 23, 4);
            }, o.prototype.readDoubleLE = function(e, t) {
                return e = e >>> 0, t || Q(e, 8, this.length), f.read(this, e, !0, 52, 8);
            }, o.prototype.readDoubleBE = function(e, t) {
                return e = e >>> 0, t || Q(e, 8, this.length), f.read(this, e, !1, 52, 8);
            };
            function te(n, e, t, r, i, l) {
                if (!o.isBuffer(n)) throw new TypeError('"buffer" argument must be a Buffer instance');
                if (e > i || e < l) throw new RangeError('"value" argument is out of bounds');
                if (t + r > n.length) throw new RangeError("Index out of range");
            }
            o.prototype.writeUintLE = o.prototype.writeUIntLE = function(e, t, r, i) {
                if (e = +e, t = t >>> 0, r = r >>> 0, !i) {
                    const D = Math.pow(2, 8 * r) - 1;
                    te(this, e, t, r, D, 0);
                }
                let l = 1, s = 0;
                for(this[t] = e & 255; ++s < r && (l *= 256);)this[t + s] = e / l & 255;
                return t + r;
            }, o.prototype.writeUintBE = o.prototype.writeUIntBE = function(e, t, r, i) {
                if (e = +e, t = t >>> 0, r = r >>> 0, !i) {
                    const D = Math.pow(2, 8 * r) - 1;
                    te(this, e, t, r, D, 0);
                }
                let l = r - 1, s = 1;
                for(this[t + l] = e & 255; --l >= 0 && (s *= 256);)this[t + l] = e / s & 255;
                return t + r;
            }, o.prototype.writeUint8 = o.prototype.writeUInt8 = function(e, t, r) {
                return e = +e, t = t >>> 0, r || te(this, e, t, 1, 255, 0), this[t] = e & 255, t + 1;
            }, o.prototype.writeUint16LE = o.prototype.writeUInt16LE = function(e, t, r) {
                return e = +e, t = t >>> 0, r || te(this, e, t, 2, 65535, 0), this[t] = e & 255, this[t + 1] = e >>> 8, t + 2;
            }, o.prototype.writeUint16BE = o.prototype.writeUInt16BE = function(e, t, r) {
                return e = +e, t = t >>> 0, r || te(this, e, t, 2, 65535, 0), this[t] = e >>> 8, this[t + 1] = e & 255, t + 2;
            }, o.prototype.writeUint32LE = o.prototype.writeUInt32LE = function(e, t, r) {
                return e = +e, t = t >>> 0, r || te(this, e, t, 4, 4294967295, 0), this[t + 3] = e >>> 24, this[t + 2] = e >>> 16, this[t + 1] = e >>> 8, this[t] = e & 255, t + 4;
            }, o.prototype.writeUint32BE = o.prototype.writeUInt32BE = function(e, t, r) {
                return e = +e, t = t >>> 0, r || te(this, e, t, 4, 4294967295, 0), this[t] = e >>> 24, this[t + 1] = e >>> 16, this[t + 2] = e >>> 8, this[t + 3] = e & 255, t + 4;
            };
            function Pe(n, e, t, r, i) {
                Ge(e, r, i, n, t, 7);
                let l = Number(e & BigInt(4294967295));
                n[t++] = l, l = l >> 8, n[t++] = l, l = l >> 8, n[t++] = l, l = l >> 8, n[t++] = l;
                let s = Number(e >> BigInt(32) & BigInt(4294967295));
                return n[t++] = s, s = s >> 8, n[t++] = s, s = s >> 8, n[t++] = s, s = s >> 8, n[t++] = s, t;
            }
            function Le(n, e, t, r, i) {
                Ge(e, r, i, n, t, 7);
                let l = Number(e & BigInt(4294967295));
                n[t + 7] = l, l = l >> 8, n[t + 6] = l, l = l >> 8, n[t + 5] = l, l = l >> 8, n[t + 4] = l;
                let s = Number(e >> BigInt(32) & BigInt(4294967295));
                return n[t + 3] = s, s = s >> 8, n[t + 2] = s, s = s >> 8, n[t + 1] = s, s = s >> 8, n[t] = s, t + 8;
            }
            o.prototype.writeBigUInt64LE = oe(function(e, t = 0) {
                return Pe(this, e, t, BigInt(0), BigInt("0xffffffffffffffff"));
            }), o.prototype.writeBigUInt64BE = oe(function(e, t = 0) {
                return Le(this, e, t, BigInt(0), BigInt("0xffffffffffffffff"));
            }), o.prototype.writeIntLE = function(e, t, r, i) {
                if (e = +e, t = t >>> 0, !i) {
                    const G = Math.pow(2, 8 * r - 1);
                    te(this, e, t, r, G - 1, -G);
                }
                let l = 0, s = 1, D = 0;
                for(this[t] = e & 255; ++l < r && (s *= 256);)e < 0 && D === 0 && this[t + l - 1] !== 0 && (D = 1), this[t + l] = (e / s >> 0) - D & 255;
                return t + r;
            }, o.prototype.writeIntBE = function(e, t, r, i) {
                if (e = +e, t = t >>> 0, !i) {
                    const G = Math.pow(2, 8 * r - 1);
                    te(this, e, t, r, G - 1, -G);
                }
                let l = r - 1, s = 1, D = 0;
                for(this[t + l] = e & 255; --l >= 0 && (s *= 256);)e < 0 && D === 0 && this[t + l + 1] !== 0 && (D = 1), this[t + l] = (e / s >> 0) - D & 255;
                return t + r;
            }, o.prototype.writeInt8 = function(e, t, r) {
                return e = +e, t = t >>> 0, r || te(this, e, t, 1, 127, -128), e < 0 && (e = 255 + e + 1), this[t] = e & 255, t + 1;
            }, o.prototype.writeInt16LE = function(e, t, r) {
                return e = +e, t = t >>> 0, r || te(this, e, t, 2, 32767, -32768), this[t] = e & 255, this[t + 1] = e >>> 8, t + 2;
            }, o.prototype.writeInt16BE = function(e, t, r) {
                return e = +e, t = t >>> 0, r || te(this, e, t, 2, 32767, -32768), this[t] = e >>> 8, this[t + 1] = e & 255, t + 2;
            }, o.prototype.writeInt32LE = function(e, t, r) {
                return e = +e, t = t >>> 0, r || te(this, e, t, 4, 2147483647, -2147483648), this[t] = e & 255, this[t + 1] = e >>> 8, this[t + 2] = e >>> 16, this[t + 3] = e >>> 24, t + 4;
            }, o.prototype.writeInt32BE = function(e, t, r) {
                return e = +e, t = t >>> 0, r || te(this, e, t, 4, 2147483647, -2147483648), e < 0 && (e = 4294967295 + e + 1), this[t] = e >>> 24, this[t + 1] = e >>> 16, this[t + 2] = e >>> 8, this[t + 3] = e & 255, t + 4;
            }, o.prototype.writeBigInt64LE = oe(function(e, t = 0) {
                return Pe(this, e, t, -BigInt("0x8000000000000000"), BigInt("0x7fffffffffffffff"));
            }), o.prototype.writeBigInt64BE = oe(function(e, t = 0) {
                return Le(this, e, t, -BigInt("0x8000000000000000"), BigInt("0x7fffffffffffffff"));
            });
            function qe(n, e, t, r, i, l) {
                if (t + r > n.length) throw new RangeError("Index out of range");
                if (t < 0) throw new RangeError("Index out of range");
            }
            function ze(n, e, t, r, i) {
                return e = +e, t = t >>> 0, i || qe(n, e, t, 4), f.write(n, e, t, r, 23, 4), t + 4;
            }
            o.prototype.writeFloatLE = function(e, t, r) {
                return ze(this, e, t, !0, r);
            }, o.prototype.writeFloatBE = function(e, t, r) {
                return ze(this, e, t, !1, r);
            };
            function Ve(n, e, t, r, i) {
                return e = +e, t = t >>> 0, i || qe(n, e, t, 8), f.write(n, e, t, r, 52, 8), t + 8;
            }
            o.prototype.writeDoubleLE = function(e, t, r) {
                return Ve(this, e, t, !0, r);
            }, o.prototype.writeDoubleBE = function(e, t, r) {
                return Ve(this, e, t, !1, r);
            }, o.prototype.copy = function(e, t, r, i) {
                if (!o.isBuffer(e)) throw new TypeError("argument should be a Buffer");
                if (r || (r = 0), !i && i !== 0 && (i = this.length), t >= e.length && (t = e.length), t || (t = 0), i > 0 && i < r && (i = r), i === r || e.length === 0 || this.length === 0) return 0;
                if (t < 0) throw new RangeError("targetStart out of bounds");
                if (r < 0 || r >= this.length) throw new RangeError("Index out of range");
                if (i < 0) throw new RangeError("sourceEnd out of bounds");
                i > this.length && (i = this.length), e.length - t < i - r && (i = e.length - t + r);
                const l = i - r;
                return this === e && typeof Uint8Array.prototype.copyWithin == "function" ? this.copyWithin(t, r, i) : Uint8Array.prototype.set.call(e, this.subarray(r, i), t), l;
            }, o.prototype.fill = function(e, t, r, i) {
                if (typeof e == "string") {
                    if (typeof t == "string" ? (i = t, t = 0, r = this.length) : typeof r == "string" && (i = r, r = this.length), i !== void 0 && typeof i != "string") throw new TypeError("encoding must be a string");
                    if (typeof i == "string" && !o.isEncoding(i)) throw new TypeError("Unknown encoding: " + i);
                    if (e.length === 1) {
                        const s = e.charCodeAt(0);
                        (i === "utf8" && s < 128 || i === "latin1") && (e = s);
                    }
                } else typeof e == "number" ? e = e & 255 : typeof e == "boolean" && (e = Number(e));
                if (t < 0 || this.length < t || this.length < r) throw new RangeError("Out of range index");
                if (r <= t) return this;
                t = t >>> 0, r = r === void 0 ? this.length : r >>> 0, e || (e = 0);
                let l;
                if (typeof e == "number") for(l = t; l < r; ++l)this[l] = e;
                else {
                    const s = o.isBuffer(e) ? e : o.from(e, i), D = s.length;
                    if (D === 0) throw new TypeError('The value "' + e + '" is invalid for argument "value"');
                    for(l = 0; l < r - t; ++l)this[l + t] = s[l % D];
                }
                return this;
            };
            const ce = {};
            function Ce(n, e, t) {
                ce[n] = class extends t {
                    constructor(){
                        super(), Object.defineProperty(this, "message", {
                            value: e.apply(this, arguments),
                            writable: !0,
                            configurable: !0
                        }), this.name = `${this.name} [${n}]`, this.stack, delete this.name;
                    }
                    get code() {
                        return n;
                    }
                    set code(i) {
                        Object.defineProperty(this, "code", {
                            configurable: !0,
                            enumerable: !0,
                            value: i,
                            writable: !0
                        });
                    }
                    toString() {
                        return `${this.name} [${n}]: ${this.message}`;
                    }
                };
            }
            Ce("ERR_BUFFER_OUT_OF_BOUNDS", function(n) {
                return n ? `${n} is outside of buffer bounds` : "Attempt to access memory outside buffer bounds";
            }, RangeError), Ce("ERR_INVALID_ARG_TYPE", function(n, e) {
                return `The "${n}" argument must be of type number. Received type ${typeof e}`;
            }, TypeError), Ce("ERR_OUT_OF_RANGE", function(n, e, t) {
                let r = `The value of "${n}" is out of range.`, i = t;
                return Number.isInteger(t) && Math.abs(t) > 2 ** 32 ? i = je(String(t)) : typeof t == "bigint" && (i = String(t), (t > BigInt(2) ** BigInt(32) || t < -(BigInt(2) ** BigInt(32))) && (i = je(i)), i += "n"), r += ` It must be ${e}. Received ${i}`, r;
            }, RangeError);
            function je(n) {
                let e = "", t = n.length;
                const r = n[0] === "-" ? 1 : 0;
                for(; t >= r + 4; t -= 3)e = `_${n.slice(t - 3, t)}${e}`;
                return `${n.slice(0, t)}${e}`;
            }
            function ht(n, e, t) {
                pe(e, "offset"), (n[e] === void 0 || n[e + t] === void 0) && de(e, n.length - (t + 1));
            }
            function Ge(n, e, t, r, i, l) {
                if (n > t || n < e) {
                    const s = typeof e == "bigint" ? "n" : "";
                    let D;
                    throw e === 0 || e === BigInt(0) ? D = `>= 0${s} and < 2${s} ** ${(l + 1) * 8}${s}` : D = `>= -(2${s} ** ${(l + 1) * 8 - 1}${s}) and < 2 ** ${(l + 1) * 8 - 1}${s}`, new ce.ERR_OUT_OF_RANGE("value", D, n);
                }
                ht(r, i, l);
            }
            function pe(n, e) {
                if (typeof n != "number") throw new ce.ERR_INVALID_ARG_TYPE(e, "number", n);
            }
            function de(n, e, t) {
                throw Math.floor(n) !== n ? (pe(n, t), new ce.ERR_OUT_OF_RANGE("offset", "an integer", n)) : e < 0 ? new ce.ERR_BUFFER_OUT_OF_BOUNDS : new ce.ERR_OUT_OF_RANGE("offset", `>= 0 and <= ${e}`, n);
            }
            const yt = /[^+/0-9A-Za-z-_]/g;
            function mt(n) {
                if (n = n.split("=")[0], n = n.trim().replace(yt, ""), n.length < 2) return "";
                for(; n.length % 4 !== 0;)n = n + "=";
                return n;
            }
            function Ie(n, e) {
                e = e || 1 / 0;
                let t;
                const r = n.length;
                let i = null;
                const l = [];
                for(let s = 0; s < r; ++s){
                    if (t = n.charCodeAt(s), t > 55295 && t < 57344) {
                        if (!i) {
                            if (t > 56319) {
                                (e -= 3) > -1 && l.push(239, 191, 189);
                                continue;
                            } else if (s + 1 === r) {
                                (e -= 3) > -1 && l.push(239, 191, 189);
                                continue;
                            }
                            i = t;
                            continue;
                        }
                        if (t < 56320) {
                            (e -= 3) > -1 && l.push(239, 191, 189), i = t;
                            continue;
                        }
                        t = (i - 55296 << 10 | t - 56320) + 65536;
                    } else i && (e -= 3) > -1 && l.push(239, 191, 189);
                    if (i = null, t < 128) {
                        if ((e -= 1) < 0) break;
                        l.push(t);
                    } else if (t < 2048) {
                        if ((e -= 2) < 0) break;
                        l.push(t >> 6 | 192, t & 63 | 128);
                    } else if (t < 65536) {
                        if ((e -= 3) < 0) break;
                        l.push(t >> 12 | 224, t >> 6 & 63 | 128, t & 63 | 128);
                    } else if (t < 1114112) {
                        if ((e -= 4) < 0) break;
                        l.push(t >> 18 | 240, t >> 12 & 63 | 128, t >> 6 & 63 | 128, t & 63 | 128);
                    } else throw new Error("Invalid code point");
                }
                return l;
            }
            function gt(n) {
                const e = [];
                for(let t = 0; t < n.length; ++t)e.push(n.charCodeAt(t) & 255);
                return e;
            }
            function vt(n, e) {
                let t, r, i;
                const l = [];
                for(let s = 0; s < n.length && !((e -= 2) < 0); ++s)t = n.charCodeAt(s), r = t >> 8, i = t % 256, l.push(i), l.push(r);
                return l;
            }
            function He(n) {
                return a.toByteArray(mt(n));
            }
            function ve(n, e, t, r) {
                let i;
                for(i = 0; i < r && !(i + t >= e.length || i >= n.length); ++i)e[i + t] = n[i];
                return i;
            }
            function re(n, e) {
                return n instanceof e || n != null && n.constructor != null && n.constructor.name != null && n.constructor.name === e.name;
            }
            function _e(n) {
                return n !== n;
            }
            const wt = function() {
                const n = "0123456789abcdef", e = new Array(256);
                for(let t = 0; t < 16; ++t){
                    const r = t * 16;
                    for(let i = 0; i < 16; ++i)e[r + i] = n[t] + n[i];
                }
                return e;
            }();
            function oe(n) {
                return typeof BigInt > "u" ? xt : n;
            }
            function xt() {
                throw new Error("BigInt not supported");
            }
        }(Se)), Se;
    }
    var tt;
    function Zt() {
        return tt || (tt = 1, function(p, a) {
            var f = Qt(), c = f.Buffer;
            function g(d, o) {
                for(var k in d)o[k] = d[k];
            }
            c.from && c.alloc && c.allocUnsafe && c.allocUnsafeSlow ? p.exports = f : (g(f, a), a.Buffer = b);
            function b(d, o, k) {
                return c(d, o, k);
            }
            b.prototype = Object.create(c.prototype), g(c, b), b.from = function(d, o, k) {
                if (typeof d == "number") throw new TypeError("Argument must not be a number");
                return c(d, o, k);
            }, b.alloc = function(d, o, k) {
                if (typeof d != "number") throw new TypeError("Argument must be a number");
                var m = c(d);
                return o !== void 0 ? typeof k == "string" ? m.fill(o, k) : m.fill(o) : m.fill(0), m;
            }, b.allocUnsafe = function(d) {
                if (typeof d != "number") throw new TypeError("Argument must be a number");
                return c(d);
            }, b.allocUnsafeSlow = function(d) {
                if (typeof d != "number") throw new TypeError("Argument must be a number");
                return f.SlowBuffer(d);
            };
        }(xe, xe.exports)), xe.exports;
    }
    var nt;
    function Yt() {
        if (nt) return we.exports;
        nt = 1, we.exports = y, we.exports.parse = B;
        var p = Lt().basename, a = Zt().Buffer, f = /[\x00-\x20"'()*,/:;<=>?@[\\\]{}\x7f]/g, c = /%[0-9A-Fa-f]{2}/, g = /%([0-9A-Fa-f]{2})/g, b = /[^\x20-\x7e\xa0-\xff]/g, d = /\\([\u0000-\u007f])/g, o = /([\\"])/g, k = /;[\x09\x20]*([!#$%&'*+.0-9A-Z^_`a-z|~-]+)[\x09\x20]*=[\x09\x20]*("(?:[\x20!\x23-\x5b\x5d-\x7e\x80-\xff]|\\[\x20-\x7e])*"|[!#$%&'*+.0-9A-Z^_`a-z|~-]+)[\x09\x20]*/g, m = /^[\x20-\x7e\x80-\xff]+$/, x = /^[!#$%&'*+.0-9A-Z^_`a-z|~-]+$/, v = /^([A-Za-z0-9!#$%&+\-^_`{}~]+)'(?:[A-Za-z]{2,3}(?:-[A-Za-z]{3}){0,3}|[A-Za-z]{4,8}|)'((?:%[0-9A-Fa-f]{2}|[A-Za-z0-9!#$&+.^_`|~-])+)$/, L = /^([!#$%&'*+.0-9A-Z^_`a-z|~-]+)[\x09\x20]*(?:$|;)/;
        function y(E, u) {
            var C = u || {}, U = C.type || "attachment", N = I(E, C.fallback);
            return S(new R(U, N));
        }
        function I(E, u) {
            if (E !== void 0) {
                var C = {};
                if (typeof E != "string") throw new TypeError("filename must be a string");
                if (u === void 0 && (u = !0), typeof u != "string" && typeof u != "boolean") throw new TypeError("fallback must be a string or boolean");
                if (typeof u == "string" && b.test(u)) throw new TypeError("fallback must be ISO-8859-1 string");
                var U = p(E), N = m.test(U), Z = typeof u != "string" ? u && P(U) : p(u), Y = typeof Z == "string" && Z !== U;
                return (Y || !N || c.test(U)) && (C["filename*"] = U), (N || Y) && (C.filename = Y ? Z : U), C;
            }
        }
        function S(E) {
            var u = E.parameters, C = E.type;
            if (!C || typeof C != "string" || !x.test(C)) throw new TypeError("invalid type");
            var U = String(C).toLowerCase();
            if (u && typeof u == "object") for(var N, Z = Object.keys(u).sort(), Y = 0; Y < Z.length; Y++){
                N = Z[Y];
                var W = N.substr(-1) === "*" ? $(u[N]) : _(u[N]);
                U += "; " + N + "=" + W;
            }
            return U;
        }
        function O(E) {
            var u = v.exec(E);
            if (!u) throw new TypeError("invalid extended field value");
            var C = u[1].toLowerCase(), U = u[2], N, Z = U.replace(g, w);
            switch(C){
                case "iso-8859-1":
                    N = P(Z);
                    break;
                case "utf-8":
                    N = a.from(Z, "binary").toString("utf8");
                    break;
                default:
                    throw new TypeError("unsupported charset in extended field");
            }
            return N;
        }
        function P(E) {
            return String(E).replace(b, "?");
        }
        function B(E) {
            if (!E || typeof E != "string") throw new TypeError("argument string is required");
            var u = L.exec(E);
            if (!u) throw new TypeError("invalid type format");
            var C = u[0].length, U = u[1].toLowerCase(), N, Z = [], Y = {}, W;
            for(C = k.lastIndex = u[0].substr(-1) === ";" ? C - 1 : C; u = k.exec(E);){
                if (u.index !== C) throw new TypeError("invalid parameter format");
                if (C += u[0].length, N = u[1].toLowerCase(), W = u[2], Z.indexOf(N) !== -1) throw new TypeError("invalid duplicate parameter");
                if (Z.push(N), N.indexOf("*") + 1 === N.length) {
                    N = N.slice(0, -1), W = O(W), Y[N] = W;
                    continue;
                }
                typeof Y[N] != "string" && (W[0] === '"' && (W = W.substr(1, W.length - 2).replace(d, "$1")), Y[N] = W);
            }
            if (C !== -1 && C !== E.length) throw new TypeError("invalid parameter format");
            return new R(U, Y);
        }
        function w(E, u) {
            return String.fromCharCode(parseInt(u, 16));
        }
        function A(E) {
            return "%" + String(E).charCodeAt(0).toString(16).toUpperCase();
        }
        function _(E) {
            var u = String(E);
            return '"' + u.replace(o, "\\$1") + '"';
        }
        function $(E) {
            var u = String(E), C = encodeURIComponent(u).replace(f, A);
            return "UTF-8''" + C;
        }
        function R(E, u) {
            this.type = E, this.parameters = u;
        }
        return we.exports;
    }
    var Wt = Yt();
    let at, Kt, e0, t0, n0, r0, i0, o0, l0, s0, a0, u0, c0;
    at = qt(Wt);
    Kt = le({
        __name: "OpenNotebookButton",
        props: {
            severity: {
                default: "info"
            }
        },
        emits: [
            "open-file"
        ],
        setup (p, { emit: a }) {
            const f = p, c = a, g = J("show_toast"), b = j(null), d = j(null), o = ()=>{
                b.value.click();
            }, k = async (m)=>{
                const x = m.target.files[0];
                if (x.size) /\.ipynb$/.test(x.name) || g({
                    title: "File not ipynb.",
                    detail: "Beaker will try to load as json.",
                    severity: "warn",
                    life: 4e3
                });
                else {
                    g({
                        title: "Error",
                        detail: "File looks empty. Check file.",
                        severity: "error",
                        life: 1e4
                    });
                    return;
                }
                const v = await x.arrayBuffer(), L = new TextDecoder().decode(v);
                try {
                    const y = JSON.parse(L);
                    c("open-file", y, x.name);
                } catch (y) {
                    console.error(y), g({
                        title: "Invalid File",
                        detail: "Unable to load. Please check file contains valid ipynb json data.",
                        severity: "error",
                        life: 1e4
                    });
                }
                d.value.reset();
            };
            return (m, x)=>{
                const v = ge("tooltip");
                return M(), z(Ee, null, [
                    K(F(h(X), {
                        onClick: o,
                        icon: "pi pi-folder-open",
                        size: "small",
                        severity: f.severity,
                        text: ""
                    }, null, 8, [
                        "severity"
                    ]), [
                        [
                            v,
                            {
                                value: "Open ipynb file",
                                showDelay: 300
                            },
                            void 0,
                            {
                                bottom: !0
                            }
                        ]
                    ]),
                    T("form", {
                        id: "open-file-form",
                        ref_key: "fileForm",
                        ref: d
                    }, [
                        T("input", {
                            onChange: k,
                            ref_key: "fileInput",
                            ref: b,
                            type: "file",
                            style: {
                                display: "none"
                            }
                        }, null, 544)
                    ], 512)
                ], 64);
            };
        }
    });
    e0 = {
        class: "streamline-dialog"
    };
    t0 = {
        class: "streamline-name"
    };
    n0 = {
        class: "streamline-options"
    };
    r0 = {
        key: 0,
        class: "indented-option"
    };
    i0 = {
        key: 1,
        class: "indented-option"
    };
    o0 = {
        key: 0
    };
    l0 = {
        class: "streamline-buttons"
    };
    s0 = le({
        __name: "StreamlineExportDialog",
        setup (p) {
            const a = J("show_overlay"), f = J("dialogRef"), c = j(!1);
            Ue(c, (x)=>{
                x || f.value.close();
            });
            const g = j(!1);
            Ue(g, (x)=>{
                x || (b.value = {
                    collapseCodeCells: !1,
                    collapseOutputs: !1
                });
            });
            const b = j({
                collapseCodeCells: !1,
                collapseOutputs: !1
            }), d = j(""), o = j();
            Bt(()=>{
                d.value = f.value.data.saveAsFilename, o.value = f.value.data.notebook;
            });
            const k = ()=>{
                d.value = `Beaker-Notebook_${Ne()}.ipynb`;
            }, m = (x, v, L)=>{
                c.value = !0;
                const y = ke.URLExt.join(ke.PageConfig.getBaseUrl(), "export", x);
                d.value || k(), fetch(y, {
                    method: "POST",
                    body: JSON.stringify({
                        name: d.value,
                        content: o.value,
                        options: L ?? {}
                    }),
                    headers: {
                        "Content-Type": "application/json;charset=UTF-8"
                    }
                }).then(async (I)=>{
                    if (I.status === 200) {
                        const S = await I.text(), O = I.headers.get("content-disposition"), B = at.parse(O).parameters.filename;
                        De(S, B, v);
                    } else {
                        const S = await I.json();
                        a(S, "Error converting notebook");
                    }
                }).catch((I)=>console.error(I)).finally(()=>{
                    c.value = !1, f.value.close();
                });
            };
            return (x, v)=>{
                const L = ge("tooltip");
                return M(), z("div", e0, [
                    v[12] || (v[12] = T("p", null, " Streamline uses an AI agent to do a pass over the notebook for clarity, making agent interactions feel more like a comprehensive and cohesive notebook. This may take up to several minutes for longer notebooks. ", -1)),
                    T("div", t0, [
                        v[7] || (v[7] = T("label", {
                            for: "notebookname"
                        }, "Notebook Name", -1)),
                        F(h(Oe), null, {
                            default: ee(()=>[
                                    F(h(Me), {
                                        id: "notebookname",
                                        style: {
                                            display: "flex",
                                            margin: "auto"
                                        },
                                        autocomplete: "off",
                                        modelValue: d.value,
                                        "onUpdate:modelValue": v[0] || (v[0] = (y)=>d.value = y)
                                    }, null, 8, [
                                        "modelValue"
                                    ]),
                                    F(h(Ct), null, {
                                        default: ee(()=>v[6] || (v[6] = [
                                                it(".ipynb")
                                            ])),
                                        _: 1
                                    })
                                ]),
                            _: 1
                        })
                    ]),
                    F(h(Ae)),
                    T("div", n0, [
                        K((M(), z("div", null, [
                            v[8] || (v[8] = T("label", {
                                for: "additionalStreamlineOptions"
                            }, "Additional Options", -1)),
                            F(h(Fe), {
                                inputId: "additionalStreamlineOptions",
                                modelValue: g.value,
                                "onUpdate:modelValue": v[1] || (v[1] = (y)=>g.value = y)
                            }, null, 8, [
                                "modelValue"
                            ])
                        ])), [
                            [
                                L,
                                "Enable additional options for streamlining, like collapsing outputs and code cells by default."
                            ]
                        ]),
                        g.value ? K((M(), z("div", r0, [
                            v[9] || (v[9] = T("label", {
                                for: "hidecode"
                            }, "Collapse Code Cells", -1)),
                            F(h(Fe), {
                                inputId: "hidecode",
                                modelValue: b.value.collapseCodeCells,
                                "onUpdate:modelValue": v[2] || (v[2] = (y)=>b.value.collapseCodeCells = y)
                            }, null, 8, [
                                "modelValue"
                            ])
                        ])), [
                            [
                                L,
                                "Collapse code cells by default, which may be expanded using the toggle button on the left-hand side of the Jupyter pane."
                            ]
                        ]) : ne("", !0),
                        g.value ? K((M(), z("div", i0, [
                            v[10] || (v[10] = T("label", {
                                for: "hidecharts"
                            }, "Collapse Outputs", -1)),
                            F(h(Fe), {
                                inputId: "hidecharts",
                                modelValue: b.value.collapseOutputs,
                                "onUpdate:modelValue": v[3] || (v[3] = (y)=>b.value.collapseOutputs = y)
                            }, null, 8, [
                                "modelValue"
                            ])
                        ])), [
                            [
                                L,
                                "Collapse outputs by default (excluding plots and figures), which may be expanded using the toggle button on the left-hand side of the Jupyter pane."
                            ]
                        ]) : ne("", !0)
                    ]),
                    F(h(Ae)),
                    c.value ? (M(), z("div", o0, [
                        F(h(It)),
                        v[11] || (v[11] = T("span", null, "Exporting...", -1)),
                        F(h(Ae))
                    ])) : ne("", !0),
                    T("div", l0, [
                        F(h(X), {
                            type: "button",
                            label: "Cancel",
                            severity: "secondary",
                            onClick: v[4] || (v[4] = (y)=>h(f).close())
                        }),
                        F(h(X), {
                            type: "button",
                            label: "Export Notebook",
                            onClick: v[5] || (v[5] = (y)=>{
                                c.value = !0, m("streamline", "application/json", b.value);
                            })
                        })
                    ])
                ]);
            };
        }
    });
    a0 = {
        key: 0,
        class: "p-splitbutton toolbar-splitbutton"
    };
    K0 = le({
        __name: "BeakerNotebookToolbar",
        props: {
            defaultSeverity: {
                default: "info"
            },
            saveAvailable: {
                type: Boolean,
                default: !1
            },
            saveAsFilename: {}
        },
        emits: [
            "notebook-saved",
            "open-file"
        ],
        setup (p, { emit: a }) {
            const f = J("session"), c = J("notebook"), g = J("cell-component-mapping"), b = J("show_overlay"), d = _t(), o = ue(()=>Object.entries(g).map(([E, u])=>({
                        label: `${At(E)} Cell`,
                        icon: u.icon,
                        command: ()=>{
                            const C = new u.modelClass({
                                source: ""
                            });
                            c.insertCellAfter(c.selectedCell(), C, !0);
                        }
                    }))), k = a, m = p, x = j(m.saveAsFilename), v = j(), L = j(), y = j([
                {
                    label: "Loading...",
                    disabled: !0
                }
            ]), I = (E, u)=>{
                const C = ke.URLExt.join(ke.PageConfig.getBaseUrl(), "export", E);
                fetch(C, {
                    method: "POST",
                    body: JSON.stringify({
                        name: x.value,
                        content: c.notebook.toIPynb()
                    }),
                    headers: {
                        "Content-Type": "application/json;charset=UTF-8"
                    }
                }).then(async (U)=>{
                    if (U.status === 200) {
                        const N = await U.text(), Z = U.headers.get("content-disposition"), W = at.parse(Z).parameters.filename;
                        De(N, W, u);
                    } else {
                        const N = await U.json();
                        b(N, "Error converting notebook");
                    }
                }).catch((U)=>console.error(U));
            }, S = (E, u)=>{
                x.value || P(), E === "streamline" ? d.open(s0, {
                    data: {
                        saveAsFilename: x.value,
                        notebook: c.notebook.toIPynb()
                    },
                    props: {
                        modal: !0,
                        header: "AI-Streamlined Notebook Export"
                    }
                }) : I(E, u);
            }, O = async ()=>{
                const E = new Set([
                    "custom",
                    "qtpdf",
                    "qtpng",
                    "webpdf"
                ]), u = await f.services.nbconvert.getExportFormats();
                y.value = Object.entries(u).filter(([C])=>!E.has(C)).map(([C, U])=>{
                    const N = U.output_mimetype;
                    return {
                        label: C === "streamline" ? "notebook (AI ✨)" : C,
                        tooltip: N,
                        command: ()=>{
                            S(C, N);
                        }
                    };
                }).sort((C, U)=>C.label.localeCompare(U.label));
            };
            ot(async ()=>{
                O();
            }), Ue(m, (E, u)=>{
                x.value !== u.saveAsFilename && (x.value = u.saveAsFilename);
            });
            const P = ()=>{
                x.value = `Beaker-Notebook_${Ne()}.ipynb`;
            }, B = async ()=>{
                const E = {
                    notebook_id: c.id,
                    cells: c.notebook.cells.map((C)=>({
                            cell_id: C.id,
                            content: C.source
                        }))
                };
                await f.executeAction("lint_code", E).done;
            }, w = async ()=>{
                window.confirm("This will reset your entire session, clearing the notebook and removing any updates to the environment. Proceed?") && (St(f).reset(), x.value = void 0, k("notebook-saved", void 0), c.cellCount <= 0 && c.selectCell(f.addCodeCell("")));
            };
            function A(E, u) {
                k("open-file", E, u);
            }
            async function _() {
                const E = f.notebook.toIPynb(), u = f.services.contents;
                x.value || P();
                const C = `./${x.value}`, U = await u.save(C, {
                    type: "notebook",
                    content: E,
                    format: "text"
                });
                k("notebook-saved", U.path), x.value = U.path;
            }
            async function $() {
                await _(), v.value.hide();
            }
            function R() {
                const E = JSON.stringify(f.notebook.toIPynb(), null, 2), u = `Beaker-Notebook_${Ne()}.ipynb`;
                De(E, u, "application/x-ipynb+json");
            }
            return (E, u)=>{
                const C = ge("tooltip");
                return M(), se(h(Ft), {
                    class: "notebook-toolbar"
                }, {
                    start: ee(()=>[
                            ie(E.$slots, "start", {}, ()=>[
                                    F(h(Je), {
                                        onClick: u[0] || (u[0] = (U)=>h(c).insertCellAfter()),
                                        class: "toolbar-splitbutton add-cell-button",
                                        icon: "pi pi-plus",
                                        size: "small",
                                        severity: m.defaultSeverity,
                                        model: o.value,
                                        text: ""
                                    }, null, 8, [
                                        "severity",
                                        "model"
                                    ]),
                                    F(h(X), {
                                        onClick: u[1] || (u[1] = (U)=>h(c).removeCell()),
                                        icon: "pi pi-minus",
                                        size: "small",
                                        severity: m.defaultSeverity,
                                        text: ""
                                    }, null, 8, [
                                        "severity"
                                    ]),
                                    F(h(X), {
                                        onClick: u[2] || (u[2] = (U)=>h(c).selectedCell().execute()),
                                        icon: "pi pi-play",
                                        size: "small",
                                        severity: m.defaultSeverity,
                                        text: ""
                                    }, null, 8, [
                                        "severity"
                                    ]),
                                    F(h(X), {
                                        onClick: u[3] || (u[3] = (U)=>h(f).interrupt()),
                                        icon: "pi pi-stop",
                                        size: "small",
                                        severity: m.defaultSeverity,
                                        text: ""
                                    }, null, 8, [
                                        "severity"
                                    ]),
                                    ie(E.$slots, "start-extra")
                                ])
                        ]),
                    end: ee(()=>[
                            ie(E.$slots, "end", {}, ()=>[
                                    K(F(zt, {
                                        action: B,
                                        size: "small",
                                        severity: m.defaultSeverity,
                                        text: ""
                                    }, null, 8, [
                                        "severity"
                                    ]), [
                                        [
                                            C,
                                            {
                                                value: "Analyze Codecells",
                                                showDelay: 300
                                            },
                                            void 0,
                                            {
                                                bottom: !0
                                            }
                                        ]
                                    ]),
                                    K(F(h(X), {
                                        onClick: w,
                                        icon: "pi pi-refresh",
                                        size: "small",
                                        severity: m.defaultSeverity,
                                        text: ""
                                    }, null, 8, [
                                        "severity"
                                    ]), [
                                        [
                                            C,
                                            {
                                                value: "Reset notebook",
                                                showDelay: 300
                                            },
                                            void 0,
                                            {
                                                bottom: !0
                                            }
                                        ]
                                    ]),
                                    m.saveAvailable ? (M(), z("div", a0, [
                                        K(F(h(X), {
                                            class: "p-splitbutton-defaultbutton",
                                            onClick: _,
                                            icon: "pi pi-save",
                                            size: "small",
                                            severity: m.defaultSeverity,
                                            text: ""
                                        }, null, 8, [
                                            "severity"
                                        ]), [
                                            [
                                                C,
                                                {
                                                    value: "Save locally as " + (x.value ? x.value : "a .ipynb file"),
                                                    showDelay: 300
                                                },
                                                void 0,
                                                {
                                                    bottom: !0
                                                }
                                            ]
                                        ]),
                                        F(h(X), {
                                            class: "p-splitbutton-menubutton",
                                            size: "small",
                                            severity: m.defaultSeverity,
                                            text: "",
                                            onClick: u[4] || (u[4] = (U)=>{
                                                v.value.toggle(U);
                                            })
                                        }, {
                                            default: ee(()=>[
                                                    F(h($t))
                                                ]),
                                            _: 1
                                        }, 8, [
                                            "severity"
                                        ]),
                                        F(h(lt), {
                                            class: "saveas-overlay",
                                            ref_key: "saveAsHoverMenuRef",
                                            ref: v,
                                            popup: !0,
                                            onShow: u[8] || (u[8] = (U)=>{
                                                x.value || P();
                                            })
                                        }, {
                                            default: ee(()=>[
                                                    u[9] || (u[9] = T("div", null, "Save as:", -1)),
                                                    F(h(Oe), null, {
                                                        default: ee(()=>[
                                                                F(h(Me), {
                                                                    class: "saveas-input",
                                                                    ref_key: "saveAsInputRef",
                                                                    ref: L,
                                                                    modelValue: x.value,
                                                                    "onUpdate:modelValue": u[5] || (u[5] = (U)=>x.value = U),
                                                                    onKeydown: u[6] || (u[6] = me((U)=>$(), [
                                                                        "enter"
                                                                    ])),
                                                                    autofocus: ""
                                                                }, null, 8, [
                                                                    "modelValue"
                                                                ]),
                                                                F(h(X), {
                                                                    label: "Save",
                                                                    onClick: u[7] || (u[7] = (U)=>$())
                                                                })
                                                            ]),
                                                        _: 1
                                                    })
                                                ]),
                                            _: 1
                                        }, 512)
                                    ])) : ne("", !0),
                                    K(F(h(Je), {
                                        onClick: R,
                                        class: "toolbar-splitbutton",
                                        icon: "pi pi-download",
                                        size: "small",
                                        model: y.value,
                                        severity: m.defaultSeverity,
                                        text: ""
                                    }, null, 8, [
                                        "model",
                                        "severity"
                                    ]), [
                                        [
                                            C,
                                            {
                                                value: "Export (download) as .ipynb",
                                                showDelay: 300
                                            },
                                            void 0,
                                            {
                                                bottom: !0
                                            }
                                        ]
                                    ]),
                                    F(Kt, {
                                        severity: E.$props.defaultSeverity,
                                        onOpenFile: A
                                    }, null, 8, [
                                        "severity"
                                    ]),
                                    ie(E.$slots, "end-extra")
                                ])
                        ]),
                    _: 3
                });
            };
        }
    });
    u0 = {};
    c0 = {
        class: "draggable-wrapper"
    };
    function p0(p, a) {
        return M(), z("div", c0);
    }
    let f0, d0, h0, y0, m0, g0, v0, w0, x0, b0, E0, k0, B0;
    f0 = Be(u0, [
        [
            "render",
            p0
        ],
        [
            "__scopeId",
            "data-v-6b2da513"
        ]
    ]);
    d0 = [
        "cell-id"
    ];
    h0 = {
        class: "drag-handle"
    };
    y0 = {
        class: "cell-contents"
    };
    m0 = {
        class: "menu-area",
        ref: "menuAreaRef"
    };
    g0 = {
        class: "cell-type-dropdown-item"
    };
    v0 = {
        class: "extra-area"
    };
    w0 = le({
        __name: "BeakerCell",
        props: {
            cell: {},
            index: {},
            dragEnabled: {
                type: Boolean
            }
        },
        emits: [
            "move-cell"
        ],
        setup (p, { emit: a }) {
            const f = p, c = a, g = J("beakerSession"), b = J("notebook"), d = J("cell-component-mapping"), o = (w)=>{
                w.defaultPrevented || b.selectCell(f.cell);
            }, k = j(null), m = j(null), x = j(null), v = j(f.cell.metadata), L = ue(()=>v.value?.collapsed || !1), y = {
                code: "pi pi-code",
                markdown: "pi pi-pencil",
                query: "pi pi-sparkles",
                raw: "pi pi-question-circle"
            }, I = ue(()=>y[f.cell.cell_type]);
            j("pending");
            const S = (w)=>{
                v.value && (v.value.collapsed = !L.value);
            }, O = ()=>{
                f.index > 0 && c("move-cell", f.index, f.index - 1);
            }, P = ()=>{
                f.index < b.cellCount - 1 && c("move-cell", f.index, f.index + 1);
            }, B = (w)=>{
                if (!(w?.target instanceof HTMLElement && w?.relatedTarget instanceof HTMLElement)) return;
                const _ = [
                    `[cell-id="${f.cell.id}"] .menu-area`,
                    `[cell-id="${f.cell.id}"] .hover-menu`,
                    `.menu-overlay[cell-id="${f.cell.id}"]`
                ].join(", ");
                w.relatedTarget.closest(_) !== null || (w.type.toLowerCase().includes("enter") ? m.value.show(w, x.value.$el) : w.type.toLowerCase().includes("leave") && m.value.hide());
            };
            return (w, A)=>{
                const _ = ge("tooltip");
                return M(), z("div", {
                    class: ae([
                        "beaker-cell",
                        {
                            collapsed: L.value
                        }
                    ]),
                    tabindex: "0",
                    onClick: o,
                    ref_key: "beakerCellRef",
                    ref: k,
                    "cell-id": w.cell.id
                }, [
                    T("div", {
                        class: "collapse-box",
                        onClick: fe(S, [
                            "prevent"
                        ])
                    }),
                    T("div", h0, [
                        F(f0, {
                            draggable: f.dragEnabled
                        }, null, 8, [
                            "draggable"
                        ])
                    ]),
                    T("div", y0, [
                        ie(w.$slots, "default"),
                        ie(w.$slots, "child-cells")
                    ]),
                    T("div", m0, [
                        ie(w.$slots, "hover-menu", {}, ()=>[
                                T("div", {
                                    class: "hover-menu",
                                    onPointerenter: B,
                                    onPointerleave: B
                                }, [
                                    F(h(X), {
                                        ref_key: "cellMenuButton",
                                        ref: x,
                                        class: "cell-menu-button",
                                        text: "",
                                        small: "",
                                        icon: "pi pi-ellipsis-v",
                                        onClick: A[0] || (A[0] = fe(($)=>{
                                            m.value.show($);
                                        }, [
                                            "prevent"
                                        ]))
                                    }, null, 512),
                                    F(h(lt), {
                                        class: "menu-overlay",
                                        ref_key: "hoverMenuRef",
                                        ref: m,
                                        "cell-id": w.cell.id,
                                        onPointerenter: B,
                                        onPointerleave: B
                                    }, {
                                        default: ee(()=>[
                                                K((M(), z("div", null, [
                                                    F(h(Ut), {
                                                        name: `${w.cell.id}-celltype`,
                                                        class: "cell-type-selector overlay-menu-button",
                                                        "model-value": w.cell.cell_type,
                                                        "onUpdate:modelValue": A[1] || (A[1] = ($)=>{
                                                            h(b).convertCellType(w.cell, $), m.value.hide();
                                                        }),
                                                        options: Object.keys(h(d) || {}),
                                                        "dropdown-icon": I.value,
                                                        "label-style": {
                                                            display: "none"
                                                        },
                                                        "append-to": "self"
                                                    }, {
                                                        value: ee(($)=>[
                                                                T("span", {
                                                                    class: ae(y[$.value])
                                                                }, null, 2)
                                                            ]),
                                                        option: ee(($)=>[
                                                                T("div", g0, [
                                                                    T("span", {
                                                                        class: ae(y[$.option])
                                                                    }, null, 2),
                                                                    T("span", null, Te($.option), 1)
                                                                ])
                                                            ]),
                                                        _: 1
                                                    }, 8, [
                                                        "name",
                                                        "model-value",
                                                        "options",
                                                        "dropdown-icon"
                                                    ])
                                                ])), [
                                                    [
                                                        _,
                                                        "Change Cell Type",
                                                        void 0,
                                                        {
                                                            left: !0
                                                        }
                                                    ]
                                                ]),
                                                K(F(h(X), {
                                                    onClick: A[2] || (A[2] = ($)=>{
                                                        h(g).findNotebookCellById(w.cell.id).execute(), m.value.hide();
                                                    }),
                                                    icon: "pi pi-play",
                                                    size: "small",
                                                    text: ""
                                                }, null, 512), [
                                                    [
                                                        _,
                                                        "Execute cell",
                                                        void 0,
                                                        {
                                                            left: !0
                                                        }
                                                    ]
                                                ]),
                                                K(F(h(X), {
                                                    onClick: A[3] || (A[3] = ($)=>{
                                                        h(b).removeCell(h(g).findNotebookCellById(w.cell.id)), m.value.hide();
                                                    }),
                                                    icon: "pi pi-minus",
                                                    size: "small",
                                                    text: ""
                                                }, null, 512), [
                                                    [
                                                        _,
                                                        "Remove cell",
                                                        void 0,
                                                        {
                                                            left: !0
                                                        }
                                                    ]
                                                ]),
                                                K(F(h(X), {
                                                    onClick: A[4] || (A[4] = ($)=>{
                                                        O(), m.value.hide();
                                                    }),
                                                    icon: "pi pi-chevron-up",
                                                    size: "small",
                                                    text: ""
                                                }, null, 512), [
                                                    [
                                                        _,
                                                        "Move cell up",
                                                        void 0,
                                                        {
                                                            left: !0
                                                        }
                                                    ]
                                                ]),
                                                K(F(h(X), {
                                                    onClick: A[5] || (A[5] = ($)=>{
                                                        P(), m.value.hide();
                                                    }),
                                                    icon: "pi pi-chevron-down",
                                                    size: "small",
                                                    text: ""
                                                }, null, 512), [
                                                    [
                                                        _,
                                                        "Move cell down",
                                                        void 0,
                                                        {
                                                            left: !0
                                                        }
                                                    ]
                                                ])
                                            ]),
                                        _: 1
                                    }, 8, [
                                        "cell-id"
                                    ])
                                ], 32)
                            ])
                    ], 512),
                    T("div", v0, [
                        ie(w.$slots, "extra")
                    ])
                ], 10, d0);
            };
        }
    });
    en = le({
        __name: "BeakerNotebookPanel",
        emits: [],
        setup (p, { expose: a, emit: f }) {
            const c = J("session"), g = J("cell-component-mapping"), b = J("notebook"), d = j(null), o = j(!1), k = j(-1), m = j(-1), x = ue(()=>c.notebook?.cells.length > 1);
            function v(B, w, A) {
                B.splice(A, 0, B.splice(w, 1)[0]);
            }
            function L(B, w) {
                v(c.notebook.cells, B, w);
            }
            function y(B, w, A) {
                if (B.target instanceof HTMLElement && B.dataTransfer !== null && B.target.matches(".drag-handle *")) {
                    const _ = B.target.closest(".beaker-cell");
                    B.dataTransfer.dropEffect = "move", B.dataTransfer.effectAllowed = "move", B.dataTransfer.setData("x-beaker/cell", JSON.stringify({
                        id: w.id,
                        index: A
                    })), _ !== null && B.dataTransfer.setDragImage(_, 0, 0), o.value = !0, k.value = A;
                }
            }
            function I(B, w, A) {
                B?.dataTransfer?.types.includes("x-beaker/cell") && (m.value = A, B.preventDefault());
            }
            function S(B, w) {
                if (!B.target.closest(".drag-sort-enable")) return;
                const $ = JSON.parse(B.dataTransfer?.getData("x-beaker/cell") || "null"), R = $.id, E = $.index, u = c.notebook.cells[w].id;
                R !== u && v(c.notebook.cells, E, w);
            }
            function O() {
                o.value = !1, m.value = -1, k.value = -1;
            }
            function P(B) {
                d.value && (d.value.scrollTop = d.value.scrollHeight);
            }
            return a({
                scrollBottomCellContainer: P
            }), (B, w)=>(M(), z("div", {
                    class: "cell-container drag-sort-enable",
                    ref_key: "cellsContainerRef",
                    ref: d
                }, [
                    (M(!0), z(Ee, null, Re(h(c).notebook.cells, (A, _)=>(M(), se(w0, {
                            cell: A,
                            selected: A.id === h(b).selectedCellId,
                            index: _,
                            key: `outercell-${A.id}`,
                            class: ae([
                                "beaker-cell",
                                {
                                    selected: A.id === h(b).selectedCellId,
                                    "drag-source": _ == k.value,
                                    "drag-above": _ === m.value && _ < k.value,
                                    "drag-below": _ === m.value && _ > k.value,
                                    "drag-itself": _ === m.value && _ === k.value,
                                    "drag-active": o.value
                                }
                            ]),
                            "drag-enabled": x.value,
                            onMoveCell: L,
                            onDragstart: ($)=>y($, A, _),
                            onDrop: ($)=>S($, _),
                            onDragover: ($)=>I($, A, _),
                            onDragend: O
                        }, {
                            default: ee(()=>[
                                    (M(), se(Tt(h(g)[A.cell_type]), {
                                        cell: A
                                    }, null, 8, [
                                        "cell"
                                    ]))
                                ]),
                            _: 2
                        }, 1032, [
                            "cell",
                            "selected",
                            "index",
                            "class",
                            "drag-enabled",
                            "onDragstart",
                            "onDrop",
                            "onDragover"
                        ]))), 128)),
                    T("div", {
                        class: "drop-overflow-catcher",
                        onDragover: w[0] || (w[0] = (A)=>{
                            m.value = h(c).notebook.cells.length - 1, A.preventDefault();
                        }),
                        onDrop: w[1] || (w[1] = (A)=>S(A, h(c).notebook.cells.length - 1))
                    }, [
                        ie(B.$slots, "notebook-background")
                    ], 32)
                ], 512));
        }
    });
    x0 = {
        id: "agent-input"
    };
    b0 = {
        id: "agent-inner-input"
    };
    E0 = {
        class: "query-input-container"
    };
    tn = le({
        __name: "BeakerAgentQuery",
        props: [
            "runCellCallback"
        ],
        emits: [
            "select-cell",
            "run-cell"
        ],
        setup (p, { emit: a }) {
            const f = J("beakerSession"), c = J("notebook"), g = j(""), b = J("session"), d = (o)=>{
                if (!g.value.trim()) return;
                if (c.notebook.cells.length === 1) {
                    const m = c.notebook.cells[0];
                    m.cell_type === "code" && m.source === "" && m.execution_count === null && m.outputs.length === 0 && c.notebook.removeCell(0);
                }
                const k = b.addQueryCell(g.value);
                g.value = "", ye(()=>{
                    c.selectCell(k.id), f.findNotebookCellById(k.id).execute();
                });
            };
            return (o, k)=>(M(), z("div", x0, [
                    k[1] || (k[1] = T("div", {
                        id: "agent-prompt"
                    }, " How can the agent help? ", -1)),
                    T("div", b0, [
                        T("div", E0, [
                            F(st, {
                                onSubmit: d,
                                modelValue: g.value,
                                "onUpdate:modelValue": k[0] || (k[0] = (m)=>g.value = m),
                                style: {
                                    flex: "1",
                                    "margin-right": "0.75rem"
                                },
                                placeholder: "Ask the AI or request an operation."
                            }, null, 8, [
                                "modelValue"
                            ]),
                            F(h(X), {
                                onClick: d,
                                class: "agent-submit-button",
                                icon: "pi pi-send",
                                label: o.$tmpl._("agent_submit_button_label", "Submit"),
                                foo: o.$tmpl
                            }, null, 8, [
                                "label",
                                "foo"
                            ])
                        ])
                    ])
                ]));
        }
    });
    k0 = {};
    B0 = {
        class: "container",
        "xmlns:svg": "http://www.w3.org/2000/svg",
        xmlns: "http://www.w3.org/2000/svg",
        id: "svg8",
        version: "1.1",
        viewBox: "0 0 270.93333 270.93334",
        height: "1024",
        width: "1024"
    };
    function C0(p, a) {
        return M(), z("svg", B0, a[0] || (a[0] = [
            Rt('<defs id="defs2" data-v-a53841f6></defs><g transform="translate(0,-26.06665)" id="layer1" data-v-a53841f6><g transform="translate(34.695708,15.784521)" id="g6228" data-v-a53841f6><path id="beaker-body" d="m 73.909237,73.439453 c 0.659166,-9.27e-4 1.318331,-0.0019 1.997472,-0.0028 2.170595,-0.0023 4.341168,-7.89e-4 6.511763,10e-4 1.511508,-3.56e-4 3.023015,-8.7e-4 4.534522,-0.0015 3.163727,-7.79e-4 6.327446,3.52e-4 9.491172,0.0028 4.056474,0.003 8.112934,0.0013 12.169404,-0.0019 3.11935,-0.0019 6.23869,-0.0013 9.35804,6.7e-5 1.49596,3.54e-4 2.99192,-8e-5 4.48788,-0.0013 2.08869,-0.0013 4.17735,7.03e-4 6.26604,0.0037 0.61871,-0.0011 1.23743,-0.0021 1.87489,-0.0032 0.57003,0.0015 1.14006,0.003 1.72736,0.0045 l 1.49473,6.04e-4 c 2.79572,0.1322 5.1993,0.789731 7.75824,1.918675 2.18232,1.482857 3.91718,3.210953 4.97748,5.423958 1.06004,2.212468 1.50756,4.855503 1.10794,7.276041 -0.43693,2.646505 -1.86345,4.848272 -3.70417,7.14375 -1.58497,1.432987 -2.75492,2.018161 -4.7625,2.910417 -0.0245,6.129325 -0.0433,12.258635 -0.0548,18.388005 -0.006,2.84611 -0.013,5.69217 -0.025,8.53826 -0.0115,2.74656 -0.0178,5.49309 -0.0206,8.23968 -0.002,1.04793 -0.006,2.09585 -0.0115,3.14377 -0.008,1.46764 -0.009,2.93514 -0.008,4.40279 -0.002,0.83548 -0.005,1.67096 -0.007,2.53175 0.11527,1.91673 0.33954,3.07212 1.1856,4.76199 0.28616,0.62176 0.57231,1.24352 0.86713,1.88413 0.32504,0.68792 0.65007,1.37585 0.98496,2.08462 0.3223,0.6852 0.64461,1.3704 0.97668,2.07636 0.33799,0.71726 0.67599,1.43452 1.02423,2.17351 1.36139,2.8914 2.71844,5.78469 4.06797,8.68164 1.37381,2.94813 2.75953,5.89048 4.15065,8.83047 1.54244,3.26042 3.06609,6.52882 4.57233,9.80612 0.97379,2.10496 1.96242,4.2027 2.95176,6.30039 0.70027,1.48817 1.40033,2.97645 2.10013,4.46485 0.42616,0.90399 0.42616,0.90399 0.86092,1.82624 3.13618,7.02675 3.64956,7.75363 4.62446,11.89429 0.43513,1.84812 0.56285,3.77386 0.52135,5.67206 -0.0396,1.81231 -0.28552,3.63208 -0.73396,5.38847 -0.59366,2.32517 -1.43685,4.60909 -2.56696,6.72609 -1.60118,2.99943 -3.44065,5.97096 -5.89425,8.32472 -3.33218,3.19659 -6.63154,5.52987 -11.62823,7.52854 -5.13859,1.79602 -10.12058,1.96812 -15.5048,1.95899 -0.75087,0.002 -1.50173,0.004 -2.27534,0.006 -2.47555,0.005 -4.95104,0.004 -7.42659,0.002 -1.72491,0.001 -3.44982,0.003 -5.17473,0.004 -3.61303,0.003 -7.22605,0.002 -10.83908,-7.9e-4 -4.16659,-0.003 -8.333127,7.9e-4 -12.499705,0.008 -4.020415,0.007 -8.04081,0.007 -12.06123,0.006 -1.705197,-4e-5 -3.410394,0.002 -5.115588,0.005 -2.386009,0.004 -4.77192,0.001 -7.157926,-0.003 -1.051919,0.004 -1.051919,0.004 -2.125089,0.008 -6.3713,-0.0253 -11.895032,-1.02644 -17.566926,-4.09271 -4.778803,-2.82542 -8.727683,-6.47947 -11.790494,-11.12904 -2.835958,-5.26096 -4.055181,-10.04022 -4.025596,-15.99385 0.378251,-11.5332 8.519115,-23.77256 13.366626,-34.05064 1.184513,-2.51802 2.354694,-5.04253 3.524334,-7.56749 1.386342,-2.97968 2.789469,-5.95141 4.191992,-8.92349 0.76429,-1.62919 1.514021,-3.26319 2.257226,-4.90202 0.386681,-0.8381 0.773975,-1.67592 1.161687,-2.51355 0.209413,-0.45259 0.418827,-0.90518 0.634586,-1.37149 0.437964,-0.94614 0.876184,-1.89216 1.314649,-2.83807 1.568765,-3.39213 1.948791,-5.12906 1.946199,-8.87562 l 1.17e-4,-1.41579 c -1.85e-4,-1.55045 -0.0022,-3.1009 -0.0043,-4.65135 -5.02e-4,-1.07256 -8.73e-4,-2.14512 -0.0011,-3.21768 -0.001,-2.82775 -0.0036,-5.6555 -0.0065,-8.48325 -0.0027,-2.8836 -0.0039,-5.7672 -0.0052,-8.65079 -0.0028,-5.6615 -0.0074,-11.323 -0.01292,-16.984497 l -1.237133,-0.45992 C 58.542804,96.737662 57.153007,95.252318 55.624745,93.502212 54.496853,91.855489 53.865366,90.2781 53.475006,88.3263 c -0.121283,-2.716738 0.05868,-4.870756 1.058333,-7.408333 1.562053,-2.454655 3.087425,-4.260082 5.55625,-5.820833 4.331446,-1.954638 9.167107,-1.664261 13.820136,-1.65617 z M 64.55452,83.870968 c -0.425233,0.224411 -0.816314,0.581284 -1.025851,1.014039 -0.348042,0.718807 -0.426568,1.599215 -0.264583,2.38125 0.14422,0.696267 0.497178,1.4154 1.058333,1.852084 1.300285,1.011866 3.368645,0.444405 4.7625,1.322916 1.018681,0.642049 1.852083,1.5875 2.373741,2.723013 0.69781,2.30781 0.675865,4.503298 0.656823,6.89003 l 4.69e-4,1.54185 c -7.36e-4,1.67643 -0.009,3.35273 -0.01726,5.02913 -0.002,1.16445 -0.0035,2.3289 -0.0045,3.49335 -0.004,3.06089 -0.01443,6.12172 -0.02614,9.18259 -0.01084,3.12496 -0.01566,6.24994 -0.02099,9.37491 -0.03396,18.34919 -0.03396,18.34919 -0.769422,19.87533 l -0.940422,1.95215 c -0.307797,0.63883 -0.615595,1.27767 -0.932719,1.93586 -2.26936,4.72317 -4.447892,9.48324 -6.527937,14.29274 -0.474515,1.0587 -0.800989,1.77791 -1.414759,3.17061 -0.61377,1.3927 -1.056464,2.41802 -1.726145,4.48354 0.61729,-0.0425 0.716746,-0.0682 1.147228,-0.0722 1.3724,0.0289 2.744979,0.0492 4.117578,0.0662 0.764325,0.0123 1.528651,0.0245 2.316137,0.0372 4.011808,-0.18046 6.963259,-1.46773 10.499618,-3.27835 2.93718,-1.1455 5.375697,-1.37498 8.516276,-1.20716 3.699054,0.65586 6.631311,2.3481 9.739973,4.38216 2.557679,1.3867 4.766382,1.92622 7.672922,1.91823 0.74488,0.002 0.74488,0.002 1.50481,0.004 3.12547,-0.15627 5.67446,-1.5122 8.36745,-2.9807 2.85096,-1.51352 5.52986,-2.58694 8.78086,-2.71197 3.43485,0.11449 6.147,1.13989 9.25938,2.48046 3.00087,1.24928 5.57152,1.38595 8.81143,1.30757 0.49791,-0.0204 1.13285,0.0476 1.50175,0.0153 -1.12627,-2.70734 -1.89767,-4.24673 -2.96996,-6.3169 -6.48154,-13.0358 -8.70491,-17.19142 -8.97577,-20.10689 -0.18894,-10.40418 -0.57361,-35.06513 -0.57361,-54.251389 -0.01,-1.551357 1.40047,-2.497347 2.571,-3.21188 1.1618,-0.709211 2.77471,-0.223603 4.00182,-0.812649 0.62098,-0.298088 1.26737,-0.713009 1.5875,-1.322917 0.45274,-0.86254 0.56082,-1.982408 0.26459,-2.910416 -0.24726,-0.774606 -0.86387,-1.481253 -1.5875,-1.852083 -1.04859,-0.537362 -2.34489,-0.248794 -3.52204,-0.299962 -0.59003,-0.02565 -1.16936,-0.0022 -1.77176,-0.0034 -0.64574,1.19e-4 -1.29149,2.39e-4 -1.9568,3.7e-4 -0.67669,-9e-4 -1.35339,-0.0018 -2.05059,-0.0027 -2.24846,-0.0025 -4.49692,-0.003 -6.74538,-0.0033 -1.55582,-8.46e-4 -3.11164,-0.0017 -4.66746,-0.0027 -3.26567,-0.0016 -6.53135,-0.0021 -9.79703,-0.0019 -4.19406,2.7e-5 -8.388098,-0.0036 -12.582149,-0.0081 -3.214389,-0.0029 -6.428775,-0.0035 -9.643165,-0.0033 -1.546751,-3.17e-4 -3.093501,-0.0015 -4.640251,-0.0035 -2.159087,-0.0026 -4.318147,-0.0018 -6.477234,-2.36e-4 -0.967007,-0.0022 -0.967007,-0.0022 -1.953551,-0.0045 -0.586173,0.0011 -1.172347,0.0022 -1.776284,0.0034 -0.510896,-1.45e-4 -0.636509,0.0026 -0.95424,0.01879 -1.100249,0.05597 -2.236743,0.113404 -3.196686,0.620002 z m 55.3304,94.676542 c -0.79978,0.22937 -1.64358,0.63847 -2.11667,1.32291 -0.7671,1.10981 -1.12579,2.66113 -0.79375,3.96875 0.33906,1.33527 1.3662,2.66468 2.64584,3.175 1.40225,0.55922 3.23,0.29024 4.49791,-0.52916 0.86383,-0.55826 1.31295,-1.65464 1.5875,-2.64584 0.18834,-0.67995 0.25578,-1.4591 0,-2.11666 -0.52047,-1.33804 -1.59624,-2.5969 -2.91041,-3.175 -0.88802,-0.39064 -1.97787,-0.26745 -2.91042,0 z m -39.422918,2.38125 c -0.908385,0.55017 -1.810571,1.36432 -2.116666,2.38125 -0.539236,1.79149 -0.203755,3.97347 0.79375,5.55625 0.678173,1.07608 1.921705,1.89957 3.175,2.11666 1.791498,0.31031 3.873413,-0.18523 5.291666,-1.32291 0.922987,-0.74039 1.430443,-2.00222 1.5875,-3.175 0.179072,-1.33718 -0.06122,-2.83583 -0.79375,-3.96875 -0.82388,-1.2742 -2.213444,-2.3628 -3.704167,-2.64584 -1.429011,-0.27132 -2.989189,0.30482 -4.233333,1.05834 z m -24.870833,1.85208 c -1.057671,1.69227 -1.842609,3.21808 -2.645833,5.02708 -0.521992,1.1027 -1.044109,2.20533 -1.568057,3.3071 -2.018585,4.24721 -3.993042,8.50726 -5.840276,12.83249 -0.311052,0.72578 -0.622101,1.45157 -0.942578,2.19935 -1.188333,3.26029 -1.292669,6.24432 -1.174088,9.7069 0.676905,4.20393 2.166241,7.21437 4.762499,10.58333 2.241042,2.54208 4.931013,4.35342 7.987109,5.8043 3.300827,1.17126 6.416857,1.63658 9.911839,1.63941 0.62981,0.001 1.25962,0.002 1.908515,0.003 0.689201,-1.2e-4 1.378402,-2.4e-4 2.088487,-2.6e-4 0.727259,7.9e-4 1.454517,0.002 2.203814,0.003 2.410209,0.003 4.820413,0.003 7.230623,0.003 1.672796,8e-4 3.345591,0.002 5.018387,0.003 3.509361,0.002 7.018719,0.002 10.52808,0.002 4.05248,-1.6e-4 8.10495,0.003 12.15743,0.007 3.90188,0.004 7.80377,0.005 11.70565,0.005 1.65851,2.7e-4 3.31702,0.002 4.97552,0.004 2.3194,0.003 4.63878,0.002 6.95818,2.4e-4 0.68599,0.002 1.37198,0.003 2.07875,0.005 5.45617,-0.01 9.85474,-0.50821 14.79709,-3.02881 3.74039,-2.48004 6.49011,-5.58144 8.66511,-9.47539 1.32955,-3.59262 1.85764,-7.13647 1.5875,-10.31875 -0.27014,-3.18228 -1.1231,-4.67715 -2.18281,-6.99492 -0.28275,-0.61937 -0.56549,-1.23875 -0.8568,-1.87689 -1.27768,-2.71739 -2.58424,-5.42 -3.90157,-8.11836 -1.27493,-2.63584 -2.50059,-5.29304 -3.71967,-7.95508 -0.72992,-1.59218 -0.72992,-1.59218 -1.77457,-3.36516 h -8.73125 c -0.35671,-2.4e-4 -0.95375,-0.007 -0.95375,-0.007 0,0 0.49601,0.96177 0.68917,1.33027 0.44047,0.92628 0.88157,1.85226 1.32292,2.77813 0.24556,0.51569 0.49113,1.03137 0.74414,1.56269 0.96791,2.00227 1.96433,3.98933 2.96002,5.97793 0.80951,1.63481 1.61285,3.27257 2.41433,4.91133 0.20429,0.41456 0.40859,0.82913 0.61908,1.25626 2.31976,4.74819 4.13827,9.12914 3.84576,13.94075 -0.0984,1.61844 -1.06978,3.07768 -1.85208,4.49791 -0.27144,0.49279 -0.62081,0.94067 -0.97566,1.37726 -0.5159,0.63473 -1.13043,1.07808 -1.67018,1.79774 -2.44551,1.74679 -4.77025,2.71392 -7.67291,3.43959 -0.97843,0.0493 -1.95844,0.0702 -2.9381,0.0725 -0.59788,0.003 -1.19576,0.005 -1.81175,0.008 -0.65373,1.8e-4 -1.30747,2.7e-4 -1.98101,5.3e-4 -0.69028,0.002 -1.38056,0.004 -2.09176,0.007 -2.28741,0.006 -4.5748,0.009 -6.86221,0.0105 -1.58849,0.002 -3.17697,0.005 -4.76544,0.007 -3.33276,0.004 -6.66551,0.006 -9.99826,0.007 -4.26939,0.001 -8.538708,0.0114 -12.808074,0.0235 -3.282143,0.008 -6.56427,0.01 -9.846421,0.0101 -1.573887,10e-4 -3.147774,0.004 -4.721652,0.01 -2.202745,0.007 -4.405336,0.006 -6.608087,0.003 -0.974172,0.006 -0.974172,0.006 -1.968024,0.0119 -3.970033,-0.017 -7.408697,-0.92517 -10.80794,-2.35329 -0.407344,-0.17114 -0.759342,-0.45614 -1.107943,-0.72761 -0.7911,-0.61605 -1.53253,-1.30701 -2.216892,-2.03314 -1.865004,-1.97882 -2.559035,-4.11941 -3.074774,-6.69811 -0.227243,-3.52227 0.666995,-6.24645 2.133203,-9.43508 0.95145,-1.97697 1.920673,-3.94441 2.89388,-5.91075 0.498116,-1.03532 0.994382,-2.07152 1.488281,-3.10885 1.045683,-2.18911 2.092843,-4.3775 3.141927,-6.56498 0.259209,-0.54059 0.518418,-1.08117 0.785482,-1.63814 0.480328,-0.9955 1.21632,-2.48121 1.463476,-2.97553 0.247156,-0.49431 0.826865,-1.5705 0.826865,-1.5705 0,0 -0.592218,-0.0125 -0.826865,-0.017 -0.234647,-0.004 -8.995833,0 -8.995833,0 z m 57.679171,7.40833 c -0.62182,0.13346 -1.25985,0.51326 -1.5875,1.05834 -0.45664,0.75966 -0.56257,1.81108 -0.26459,2.64583 0.20966,0.58733 0.88195,0.88195 1.32292,1.32292 0.0882,0.0882 0.14935,0.21685 0.26458,0.26458 0.48889,0.2025 1.07753,0.14125 1.5875,0 0.4956,-0.13727 0.97351,-0.41643 1.32292,-0.79375 0.26799,-0.28939 0.46599,-0.66901 0.52917,-1.05833 0.0999,-0.61558 0.0143,-1.2943 -0.26459,-1.85209 -0.27889,-0.55779 -0.7684,-1.03755 -1.32291,-1.32291 -0.47701,-0.24548 -1.06298,-0.37717 -1.5875,-0.26459 z m -15.610421,2.38125 c -1.200047,0.36207 -2.445062,1.21735 -2.910417,2.38125 -0.527954,1.32046 -0.144198,2.98077 0.529167,4.23334 0.38501,0.71618 1.10848,1.25855 1.852083,1.5875 0.650262,0.28766 1.413283,0.36868 2.116667,0.26458 0.859251,-0.12717 1.827121,-0.38943 2.381251,-1.05833 0.9826,-1.18611 1.44068,-3.00588 1.05833,-4.49792 -0.29455,-1.14939 -1.32274,-2.10971 -2.38125,-2.64583 -0.790706,-0.40048 -1.79727,-0.52061 -2.645831,-0.26459 z m 27.781251,4.23334 c -0.68722,0.1825 -1.34398,0.56092 -1.85208,1.05833 -0.36748,0.35975 -0.65648,0.82732 -0.79375,1.32292 -0.25896,0.93494 -0.37125,2.01412 0,2.91041 0.4773,1.15232 1.49351,2.16853 2.64583,2.64584 0.81481,0.33751 1.83102,0.33751 2.64583,0 1.15232,-0.47731 2.2844,-1.4521 2.64584,-2.64584 0.39095,-1.29123 -0.0612,-2.83583 -0.79375,-3.96875 -0.41194,-0.6371 -1.1296,-1.09138 -1.85209,-1.32291 -0.83987,-0.26915 -1.79343,-0.22637 -2.64583,0 z m -55.827084,7.67291 c -1.224554,0.76995 -2.118475,2.09265 -2.645834,3.43959 -0.355147,0.90709 -0.485663,1.96169 -0.264583,2.91041 0.422232,1.81192 1.411082,3.66099 2.910417,4.7625 1.172204,0.86118 2.782131,1.15683 4.233333,1.05834 1.421555,-0.0965 2.878823,-0.66979 3.96875,-1.5875 1.029807,-0.86709 1.873379,-2.11552 2.116667,-3.43959 0.340722,-1.85434 0.0066,-4.0004 -1.058334,-5.55625 -0.93988,-1.3732 -2.59486,-2.3552 -4.233333,-2.64583 -1.686107,-0.29908 -3.577404,0.14683 -5.027083,1.05833 z m 39.158334,2.91042 c -1.30496,0.96235 -1.91128,2.87757 -1.85208,4.49792 0.0504,1.37954 0.764,2.85461 1.85208,3.70416 1.2818,1.0008 3.18358,1.44773 4.7625,1.05834 1.45821,-0.35962 2.75584,-1.57319 3.43958,-2.91042 0.5235,-1.02384 0.59282,-2.3375 0.26459,-3.43958 -0.41288,-1.38632 -1.32051,-2.86006 -2.64584,-3.43959 -1.78508,-0.78057 -4.25282,-0.62717 -5.82083,0.52917 z" class="main-fill" data-v-551ff1c2="" style="stroke-width:0.26458332;" data-v-a53841f6></path><path id="dot-inside-big" d="m 103.74534,108.96209 c 1.94939,0.29834 3.81324,1.3407 5.29167,2.64583 1.66873,1.47312 3.01091,3.44103 3.70416,5.55625 0.60491,1.84568 0.71616,3.93178 0.26459,5.82084 -0.57272,2.39589 -1.86262,4.72498 -3.63802,6.43268 -1.45695,1.4014 -3.42217,2.31903 -5.39089,2.77812 -1.82545,0.42568 -3.83342,0.4603 -5.622395,-0.0992 -2.492143,-0.77942 -4.892855,-2.30317 -6.515365,-4.34908 -1.404669,-1.77122 -2.267682,-4.09225 -2.38125,-6.35 -0.121441,-2.41426 0.630547,-4.92549 1.852083,-7.01146 0.992805,-1.69538 2.477017,-3.22052 4.233334,-4.10104 2.475663,-1.24115 5.464593,-1.7419 8.202083,-1.32294 z m -6.085417,6.61458 c -0.96026,0.4536 -1.658661,1.42309 -2.116666,2.38125 -0.462719,0.96803 -0.688707,2.114 -0.529167,3.175 0.234593,1.56013 0.88049,3.25308 2.116667,4.23334 1.491757,1.18293 3.682183,1.65838 5.556253,1.32291 1.56507,-0.28016 3.11117,-1.30699 3.96875,-2.64583 0.91503,-1.42852 1.22115,-3.38535 0.79375,-5.02708 -0.39561,-1.51961 -1.48521,-3.04502 -2.91042,-3.70417 -2.08279,-0.96327 -4.804258,-0.71554 -6.879167,0.26458 z" class="alt-fill" data-v-551ff1c2="" style="stroke-width:0.26458332;" data-v-a53841f6></path><path id="dot-top-most-2" d="m 116.17807,51.449968 c 1.55254,0.07554 3.10305,0.885444 4.23602,1.949624 0.94914,0.891512 1.62405,2.157529 1.85208,3.439583 0.32762,1.841978 0.12803,3.928204 -0.79375,5.55625 -0.89581,1.582175 -2.53976,2.778091 -4.23333,3.439583 -1.31697,0.514395 -2.86527,0.62153 -4.23333,0.264583 -1.46613,-0.382534 -2.80089,-1.342584 -3.81993,-2.463932 -0.84726,-0.932319 -1.59028,-2.105606 -1.73632,-3.356901 -0.25292,-2.167101 0.11499,-4.740031 1.5875,-6.35 1.70054,-1.859286 4.62436,-2.601247 7.14106,-2.47879 z m -2.40391,4.656902 c -0.55562,0.234902 -1.0628,0.7058 -1.29757,1.261472 -0.30892,0.731169 -0.33167,1.660118 0,2.38125 0.33976,0.738723 1.08947,1.305394 1.85208,1.5875 0.4963,0.183593 1.08994,0.180142 1.5875,0 0.64768,-0.234492 1.29533,-0.699128 1.5875,-1.322917 0.37408,-0.798679 0.37408,-1.847154 0,-2.645833 -0.29217,-0.623789 -0.93653,-1.097736 -1.5875,-1.322917 -0.67505,-0.23351 -1.48409,-0.216705 -2.14201,0.06144 z" class="contrast-fill" data-v-551ff1c2="" style="stroke-width:0.26458332;" data-v-a53841f6></path><path id="dor-inside-3" d="m 104.00992,153.14751 c 1.42372,0.0626 2.77485,0.98101 3.78685,1.98437 0.88787,0.88029 1.59952,2.06861 1.7694,3.3073 0.22096,1.61114 -0.12995,3.42732 -1.05833,4.7625 -1.01948,1.4662 -2.74028,2.59453 -4.49792,2.91041 -1.60058,0.28765 -3.42099,-0.13911 -4.7625,-1.05833 -1.311584,-0.89871 -2.337281,-2.40903 -2.645833,-3.96875 -0.349087,-1.76462 -0.0821,-3.90057 1.058333,-5.29167 1.453772,-1.77332 4.05916,-2.74656 6.35,-2.64583 z" class="alt-fill-2" data-v-551ff1c2="" style="stroke-width:0.26458332;" data-v-a53841f6></path><path id="dot-inside-2" d="m 91.839086,136.74334 c 1.664756,0.32641 3.443631,1.05218 4.497917,2.38125 1.076839,1.35751 1.524009,3.30604 1.322916,5.02708 -0.174001,1.48917 -0.956665,3.01885 -2.116666,3.96875 -1.424796,1.16674 -3.459175,1.76997 -5.291667,1.5875 -1.491926,-0.14856 -2.939522,-1.02643 -3.96875,-2.11666 -0.866843,-0.91822 -1.460608,-2.18323 -1.5875,-3.43959 -0.154777,-1.53245 0.223156,-3.20375 1.058333,-4.49791 0.784342,-1.21539 2.095032,-2.11242 3.439584,-2.64584 0.823875,-0.32685 1.776051,-0.43512 2.645833,-0.26458 z" class="contrast-fill" data-v-551ff1c2="" style="stroke-width:0.26458332;" data-v-a53841f6></path><path id="dot-inside-topmost" d="m 115.387,94.410008 c 0.9421,0.121325 1.91323,0.45371 2.64583,1.058333 1.13209,0.93432 2.1084,2.261901 2.38125,3.704167 0.33437,1.767472 -0.0574,3.797042 -1.05833,5.291662 -0.88471,1.32107 -2.40213,2.37448 -3.96875,2.64584 -1.7915,0.31031 -3.8308,-0.2405 -5.29167,-1.32292 -1.23959,-0.91846 -2.13537,-2.4457 -2.38125,-3.96875 -0.23317,-1.44431 0.26872,-2.993084 0.95912,-4.282941 0.56483,-1.055244 1.41134,-2.058143 2.48047,-2.596224 1.27028,-0.639319 2.82289,-0.710805 4.23333,-0.529167 z" class="contrast-fill" data-v-551ff1c2="" style="stroke-width:0.26458332;" data-v-a53841f6></path><path id="dot-outside-2" d="m 83.637003,58.162091 c 1.524302,-0.221073 3.37041,0.009 4.497917,1.058333 1.082238,1.007201 1.610726,2.783211 1.322916,4.233334 -0.268193,1.351284 -1.423618,2.539323 -2.645833,3.175 -0.942186,0.490033 -2.168538,0.603525 -3.175,0.264583 -1.124482,-0.378688 -2.121864,-1.316674 -2.645833,-2.38125 -0.507798,-1.03172 -0.516861,-2.317683 -0.264584,-3.439583 0.155995,-0.693724 0.555548,-1.349298 1.058334,-1.852084 0.502786,-0.502786 1.148399,-0.956276 1.852083,-1.058333 z" class="alt-fill" data-v-551ff1c2="" style="stroke-width:0.26458332;" data-v-a53841f6></path><path id="dot-near-surface-2" d="m 117.76825,144.15167 c 0.67117,0.15495 1.27328,0.70994 1.5875,1.32292 0.56467,1.10157 0.69722,2.54436 0.26458,3.70416 -0.34874,0.93488 -1.19481,1.73483 -2.11666,2.11667 -0.89629,0.37126 -1.97548,0.25896 -2.91042,0 -0.4956,-0.13727 -0.97351,-0.41643 -1.32292,-0.79375 -0.53597,-0.57879 -0.97056,-1.33273 -1.05833,-2.11667 -0.11656,-1.04105 0.008,-2.31126 0.74901,-3.0521 1.16661,-1.16696 3.19945,-1.55242 4.80724,-1.18123 z" class="contrast-fill" data-v-551ff1c2="" style="stroke-width:0.26458332;" data-v-a53841f6></path><path id="dot-near-surface" d="m 80.99117,156.85167 c 1.228188,-0.0232 2.674106,0.36218 3.439583,1.32292 0.777223,0.97548 0.805069,2.4878 0.529167,3.70416 -0.140683,0.62022 -0.535165,1.22589 -1.058333,1.5875 -0.967942,0.66904 -2.29948,1.08477 -3.439584,0.79375 -1.029006,-0.26266 -1.893285,-1.1734 -2.38125,-2.11666 -0.366954,-0.70934 -0.441962,-1.60256 -0.264583,-2.38125 0.184795,-0.81124 0.691152,-1.57525 1.322917,-2.11667 0.510005,-0.43707 1.180534,-0.78108 1.852083,-0.79375 z" class="alt-fill" data-v-551ff1c2="" style="stroke-width:0.26458332;" data-v-a53841f6></path><path id="dot-top-most" d="m 97.130753,47.843342 c 0.783276,0.218245 1.471987,0.868696 1.852083,1.5875 0.373329,0.706005 0.506687,1.620196 0.264584,2.38125 -0.321942,1.012028 -1.147866,1.946195 -2.116667,2.38125 -0.724091,0.325164 -1.658435,0.32799 -2.38125,0 -0.853736,-0.387399 -1.522332,-1.239052 -1.852083,-2.116667 -0.248163,-0.660472 -0.204459,-1.441385 0,-2.116666 0.184297,-0.608691 0.524269,-1.242182 1.058333,-1.5875 0.900996,-0.582571 2.141439,-0.817149 3.175,-0.529167 z" class="alt-fill" data-v-551ff1c2="" style="stroke-width:0.26458332;" data-v-a53841f6></path><path id="dot-near-outside" d="m 99.185998,61.795387 c 0.699713,-0.01723 1.423432,0.364897 1.913502,0.864621 0.47029,0.47955 0.83923,1.181956 0.79375,1.852083 -0.0696,1.026155 -0.72188,2.090367 -1.5875,2.645834 -0.672148,0.431316 -1.627634,0.528936 -2.381247,0.264583 -0.706169,-0.247711 -1.328616,-0.885351 -1.5875,-1.5875 -0.310969,-0.843415 -0.286048,-1.940432 0.212612,-2.688356 0.5478,-0.821629 1.649181,-1.326955 2.636383,-1.351265 z" class="alt-fill-2" data-v-551ff1c2="" style="stroke-width:0.26458332;" data-v-a53841f6></path></g></g>', 2)
        ]));
    }
    let I0, _0;
    nn = Be(k0, [
        [
            "render",
            C0
        ],
        [
            "__scopeId",
            "data-v-a53841f6"
        ]
    ]);
    I0 = {};
    _0 = {
        xmlns: "http://www.w3.org/2000/svg",
        viewBox: "0 0 249.812 240.838"
    };
    function A0(p, a) {
        return M(), z("svg", _0, a[0] || (a[0] = [
            T("path", {
                d: "M107.587 211.454c2.623-16.6 2.49-17.741 12.243-20.752 5.656-1.746 8.445-3.763 13.982-10.11 3.6-4.127 4.145-4.423 7.703-4.175 2.106.146 8.116-.607 13.355-1.674 8.14-1.658 10.605-2.604 16.947-6.505 4.081-2.51 8.356-5.492 9.5-6.627 1.722-1.709 2.846-2.028 6.547-1.861 6.935.313 26.849-4.077 32.738-7.217 18.358-9.79 30.449-29.965 29.109-48.572-.343-4.75-3.998-15.368-6.77-19.668-1.706-2.644-1.987-3.995-1.733-8.322.373-6.329-2.224-19.946-4.609-24.167-5.208-9.222-12.272-15.442-22.014-19.386-5.23-2.117-7.505-3.75-10.353-7.429-8.302-10.725-24.088-17.77-37.122-16.568-8.299.766-11.97.481-14.889-1.157-5.34-2.995-16.486-6.338-23.072-6.919-12.623-1.113-25.145 3.001-36.879 12.118l-6.308 4.9-7.915.485c-12.346.755-24.798 4.985-32.222 10.947-4.465 3.584-10.564 11.693-12.646 16.812-1.807 4.44-3.42 6.428-7.94 9.79-12.73 9.465-20.426 20.368-23.89 33.847-1.877 7.302-1.862 7.912.468 19.296 2.499 12.21 4.57 16.784 12.287 27.129 2.285 3.063 3.408 6.26 5.73 16.314 3.112 13.469 4.598 16.894 10.983 25.31 4.505 5.938 13.306 12.036 20.957 14.52 5.304 1.722 5.417 2.168 3.091 12.213-3.101 13.397-2.967 17.757.712 23.167 4.461 6.558 15.726 12.503 25.214 13.645 5.896.71 12.809-.558 17.234-4.52 6.617-5.921 6.939-8.263 9.562-24.864zm-25.906 15.52c-5.78-.801-10.648-3.021-13.6-6.204-2.674-2.883-2.783-1.733 2.037-21.565 2.576-10.6 3.583-15.997 3.27-17.531-.145-.705-2.612-1.318-5.646-1.403-15.523-.435-23.98-5.814-30.94-19.68-2.847-5.67-5.025-15.74-4.272-19.747 1.632-8.687 2.503-10.967 6.5-17.005 4.963-7.5 12.397-12.852 23.658-17.032 7.513-2.79 9.118-4.492 8.248-8.751-.936-4.585-4.158-6.364-9.477-5.234-13.43 2.852-30.025 14.83-35.631 25.718-2.78 5.398-3.85 5.179-7.134-1.458-3.457-6.99-5.088-16.654-3.99-23.639 1.307-8.302 8.186-18.538 17.093-25.436 3.636-2.815 7.507-5.57 8.603-6.122 1.096-.552 2.422-2.744 2.946-4.872 1.64-6.657 8.315-15.808 14.17-19.428 11.647-7.2 29.355-7.26 41.15-.137 7.805 4.712 11.423 11.097 9.942 17.541-.613 2.665-5.01 6.734-7.918 7.328-2.139.437-4.73 5.01-4.23 7.464.23 1.125 1.305 2.886 2.389 3.912 3.627 3.436 14.653-.582 19.18-6.99l1.801-2.55 3.788 2.364c5.822 3.63 10.014 4.381 16.769 3.001 6.885-1.406 8.375-3.094 7.359-8.334-.713-3.678-4.106-5.599-8.356-4.73-4.324.883-8.886-.917-11.898-4.695-1.517-1.902-2.843-3.872-2.946-4.378-.686-3.36-11.42-16.881-16.218-20.432-5.123-3.79-5.418-4.208-4.038-5.726 2.197-2.416 13.9-6.66 18.866-6.841 2.373-.087 6.215.16 8.54.548 4.683.782 16.402 5.64 19.965 8.276 1.89 1.398 3.412 1.466 8.688.388 15.061-3.076 27.08 1.328 35.004 12.826 3.592 5.212 4.648 6.048 9.225 7.303 10.656 2.92 18.303 9.643 21.595 18.982 1.674 4.748 1.328 10.093-.642 9.936-.791-.063-3.988-.443-7.105-.845-3.918-.505-8.414-.162-14.572 1.113-7.86 1.628-10.699 2.58-19.367 6.493-3.17 1.431-4.548 4.315-3.804 7.961.912 4.463 4.815 6.132 9.807 4.193 13.037-5.062 17.007-6.152 22.416-6.154 7.678-.003 13.125 1.896 17.255 6.017 2.99 2.983 3.666 4.457 4.969 10.826 1.276 6.238 1.242 8.243-.218 13.016-3.157 10.316-10.467 19.352-20.004 24.728-4.27 2.407-17.332 5.973-19.098 5.215-1.068-.458-.835-2.615.97-8.989 1.307-4.612 2.095-9.76 1.752-11.44-1.644-8.047-11.583-7.228-13.093 1.078-1.046 5.752-4.996 15.288-8.082 19.512-6.494 8.89-18.565 15.857-29.213 16.857-13.2 1.241-26.057-4.68-37.306-17.18-9.922-11.026-20.051-15.373-32.003-13.734-6.73.923-7.098 1.098-8.595 4.082-1.112 2.215-1.235 3.826-.424 5.568 1.762 3.787 3.263 4.569 7.222 3.76 9.43-1.926 15.853 1.059 25.628 11.909 4.145 4.6 10.082 10.047 13.195 12.105 3.112 2.057 5.73 4.09 5.817 4.516.349 1.705-5.13 4.46-12.487 6.28-7.166 1.771-7.89 2.165-9.397 5.12-2.35 4.607-5.297 16.973-6.76 28.358-.696 5.415-1.513 10.699-1.816 11.743-.673 2.32-3.718 3.031-9.537 2.225zm62.622-100.86c1.945-1.963 2.265-5.9.988-12.152-1.583-7.75-4.517-11.868-11.312-15.879-6.355-3.75-11.262-4.542-18.715-3.02-5.96 1.217-6.323 1.446-7.495 4.71-2.418 6.73 2.64 10.57 11.532 8.754 3.6-.735 5.09-.475 7.887 1.373 3.508 2.318 3.959 3.28 5.33 11.386.636 3.76 1.237 4.783 3.342 5.696 2.685 1.166 6.854.737 8.443-.868z"
            }, null, -1)
        ]));
    }
    let rt, F0, $0, S0, U0, T0, R0, D0, N0, M0, O0, P0, L0, q0, z0, V0, j0;
    rt = Be(I0, [
        [
            "render",
            A0
        ]
    ]);
    F0 = {
        class: "llm-query-cell"
    };
    $0 = {
        class: "llm-prompt-container"
    };
    S0 = {
        class: "prompt-input-container"
    };
    U0 = {
        class: "prompt-controls",
        style: {}
    };
    T0 = {
        key: 0,
        class: "event-container"
    };
    R0 = {
        class: "events"
    };
    D0 = {
        key: 0,
        class: "query-steps"
    };
    N0 = {
        class: "query-header-content"
    };
    M0 = {
        class: "font-bold white-space-nowrap"
    };
    O0 = {
        style: {
            display: "flex",
            "flex-direction": "column"
        }
    };
    P0 = {
        key: 2,
        class: "query-answer"
    };
    L0 = {
        key: 1,
        class: "thinking-indicator"
    };
    q0 = {
        class: "thought-icon",
        style: {
            "margin-right": "0.25rem"
        }
    };
    z0 = {
        key: 2,
        class: "input-request"
    };
    V0 = {
        class: "input-request-wrapper"
    };
    j0 = {
        modelClass: kt,
        icon: "pi pi-sparkles"
    };
    rn = le({
        ...j0,
        __name: "BeakerQueryCell",
        props: [
            "index",
            "cell"
        ],
        setup (p, { expose: a }) {
            const f = p, { cell: c, isEditing: g, promptEditorMinHeight: b, promptText: d, response: o, textarea: k, events: m, execute: x, enter: v, exit: L, clear: y, respond: I } = Vt(f), S = {
                code_cell: "pi pi-code",
                thought: "thought-icon",
                user_answer: "pi pi-reply",
                user_question: "pi pi-question-circle"
            }, O = J("beakerSession"), P = Dt(), B = ue(()=>f.cell?.events?.filter(($)=>[
                        "user_question",
                        "user_answer"
                    ].includes($.type)).map(($)=>{
                    let R;
                    return $.type === "user_question" ? R = "query-answer-chat query-answer-chat-override" : R = "llm-prompt-container llm-prompt-container-chat llm-prompt-text llm-prompt-text-chat", [
                        $,
                        R
                    ];
                })), w = ue({
                get () {
                    const $ = m.value.length;
                    return $ === 0 ? [] : $ === 1 ? [
                        0
                    ] : [
                        $ - 2,
                        $ - 1
                    ];
                },
                set ($) {}
            }), A = {
                thought: "Thought",
                response: "Final Response",
                code_cell: "Code",
                user_answer: "Answer",
                user_question: "Question",
                error: "Error",
                abort: "Abort"
            }, _ = ($)=>{
                g.value || (b.value = $.target.clientHeight, g.value = !0);
            };
            return a({
                execute: x,
                enter: v,
                exit: L,
                clear: y,
                cell: c,
                editor: k
            }), ot(()=>{
                O.cellRegistry[c.value.id] = P.vnode;
            }), Nt(()=>{
                delete O.cellRegistry[c.value.id];
            }), ($, R)=>{
                const E = ge("focustrap");
                return M(), z("div", F0, [
                    T("div", {
                        class: "query",
                        onDblclick: _
                    }, [
                        R[7] || (R[7] = T("div", {
                            class: "query-steps"
                        }, "User Query:", -1)),
                        T("div", $0, [
                            K(T("div", S0, [
                                F(st, {
                                    ref_key: "textarea",
                                    ref: k,
                                    class: "prompt-input",
                                    modelValue: h(d),
                                    "onUpdate:modelValue": R[0] || (R[0] = (u)=>Ze(d) ? d.value = u : null),
                                    style: Mt({
                                        minHeight: `${h(b)}px`
                                    })
                                }, null, 8, [
                                    "modelValue",
                                    "style"
                                ]),
                                T("div", U0, [
                                    F(h(X), {
                                        label: "Submit",
                                        onClick: h(x)
                                    }, null, 8, [
                                        "onClick"
                                    ]),
                                    F(h(X), {
                                        label: "Cancel",
                                        onClick: R[1] || (R[1] = (u)=>{
                                            d.value = h(c).source, g.value = !1;
                                        })
                                    })
                                ])
                            ], 512), [
                                [
                                    Qe,
                                    h(g)
                                ]
                            ]),
                            K(T("div", {
                                class: "llm-prompt-text"
                            }, Te(h(c).source), 513), [
                                [
                                    Qe,
                                    !h(g)
                                ]
                            ])
                        ])
                    ], 32),
                    h(m).length > 0 || h(Ye)(h(m)) ? (M(), z("div", T0, [
                        T("div", R0, [
                            h(m).length > 0 ? (M(), z("div", D0, " Agent actions: ")) : ne("", !0),
                            h(m).length > 0 ? (M(), se(h(Ot), {
                                key: 1,
                                multiple: !0,
                                class: ae("query-accordion"),
                                "active-index": w.value,
                                "onUpdate:activeIndex": R[2] || (R[2] = (u)=>w.value = u)
                            }, {
                                default: ee(()=>[
                                        (M(!0), z(Ee, null, Re(h(m), (u, C)=>(M(), se(h(Pt), {
                                                key: C,
                                                pt: {
                                                    header: {
                                                        class: [
                                                            "query-tab",
                                                            `query-tab-${u.type}`
                                                        ]
                                                    },
                                                    headerAction: {
                                                        class: [
                                                            "query-tab-headeraction",
                                                            `query-tab-headeraction-${u.type}`
                                                        ]
                                                    },
                                                    content: {
                                                        class: [
                                                            `query-tab-content-${u.type}`
                                                        ]
                                                    },
                                                    headerIcon: {
                                                        class: [
                                                            `query-tab-icon-${u.type}`
                                                        ]
                                                    }
                                                }
                                            }, {
                                                header: ee(()=>[
                                                        T("span", N0, [
                                                            T("span", {
                                                                class: ae(S[u.type])
                                                            }, [
                                                                u.type === "thought" ? (M(), se(rt, {
                                                                    key: 0,
                                                                    class: "thought-icon"
                                                                })) : ne("", !0)
                                                            ], 2),
                                                            T("span", M0, Te(A[u.type]), 1)
                                                        ])
                                                    ]),
                                                default: ee(()=>[
                                                        (M(), se($e, {
                                                            key: C,
                                                            event: u,
                                                            "parent-query-cell": h(c)
                                                        }, null, 8, [
                                                            "event",
                                                            "parent-query-cell"
                                                        ]))
                                                    ]),
                                                _: 2
                                            }, 1032, [
                                                "pt"
                                            ]))), 128))
                                    ]),
                                _: 1
                            }, 8, [
                                "active-index"
                            ])) : ne("", !0),
                            (M(!0), z(Ee, null, Re(B.value, ([u, C])=>(M(), z("div", {
                                    key: u.id
                                }, [
                                    T("div", O0, [
                                        F($e, {
                                            event: u,
                                            "parent-query-cell": h(c),
                                            class: ae(C)
                                        }, null, 8, [
                                            "event",
                                            "parent-query-cell",
                                            "class"
                                        ])
                                    ])
                                ]))), 128)),
                            h(Ye)(h(m)) ? (M(), z("div", P0, [
                                R[8] || (R[8] = T("h3", {
                                    class: "query-steps"
                                }, "Result", -1)),
                                F($e, {
                                    event: h(c)?.events[h(c)?.events.length - 1],
                                    "parent-query-cell": h(c)
                                }, null, 8, [
                                    "event",
                                    "parent-query-cell"
                                ])
                            ])) : ne("", !0)
                        ])
                    ])) : ne("", !0),
                    h(c).status === "busy" ? (M(), z("div", L0, [
                        T("span", q0, [
                            F(rt)
                        ]),
                        R[9] || (R[9] = it(" Thinking ")),
                        R[10] || (R[10] = T("span", {
                            class: "thinking-animation"
                        }, null, -1))
                    ])) : ne("", !0),
                    h(c).status === "awaiting_input" ? K((M(), z("div", z0, [
                        T("div", V0, [
                            F(h(Oe), null, {
                                default: ee(()=>[
                                        F(h(Me), {
                                            placeholder: "Reply to the agent",
                                            onKeydown: [
                                                me(fe(h(I), [
                                                    "exact",
                                                    "prevent"
                                                ]), [
                                                    "enter"
                                                ]),
                                                R[3] || (R[3] = me(fe((u)=>u.target.blur(), [
                                                    "prevent",
                                                    "stop"
                                                ]), [
                                                    "escape"
                                                ])),
                                                R[4] || (R[4] = me(fe(()=>{}, [
                                                    "ctrl",
                                                    "stop"
                                                ]), [
                                                    "enter"
                                                ])),
                                                R[5] || (R[5] = me(fe(()=>{}, [
                                                    "shift",
                                                    "stop"
                                                ]), [
                                                    "enter"
                                                ]))
                                            ],
                                            autoFocus: "",
                                            modelValue: h(o),
                                            "onUpdate:modelValue": R[6] || (R[6] = (u)=>Ze(o) ? o.value = u : null)
                                        }, null, 8, [
                                            "onKeydown",
                                            "modelValue"
                                        ]),
                                        F(h(X), {
                                            icon: "pi pi-send",
                                            onClick: h(I)
                                        }, null, 8, [
                                            "onClick"
                                        ])
                                    ]),
                                _: 1
                            })
                        ])
                    ])), [
                        [
                            E
                        ]
                    ]) : ne("", !0)
                ]);
            };
        }
    });
});
export { Y0 as B, nn as S, rn as _, K0 as a, en as b, tn as c, __tla };
