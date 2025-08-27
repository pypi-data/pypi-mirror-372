import { d as j, r as b, j as E, o as l, u as g, L as re, I as A, B as y, as as ve, _ as T, a as ne, w as Y, at as fe, y as c, aq as D, A as q, ar as F, z, ad as me, E as x, G as V, i as S, f as R, U as Q, V as U, W as X, J as ce, K as G, X as ye, M as B, au as _e, n as J, $ as ge, R as ke, s as be } from "./primevue-1TEWPnDt.js";
import { h as I, k as he, j as Z, n as we, m as N, o as Ce, __tla as __tla_0 } from "./DebugPanel.vue_vue_type_style_index_0_lang-PW_f_WLw.js";
import { f as ee, __tla as __tla_1 } from "./index-D-jLGYR3.js";
import { g as ie } from "./jupyterlab-C2EV-Dpr.js";
let xt, bt, Fe, kt, gt, ht, xe, wt, Ct;
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
    })()
]).then(async ()=>{
    let $e;
    xe = j({
        __name: "AnnotationButton",
        props: {
            action: {
                type: Function,
                async default () {
                    console.log("no action defined");
                }
            }
        },
        setup (i) {
            const u = i, v = b(!1), a = async ()=>{
                v.value = !0;
                try {
                    await u.action();
                } finally{
                    v.value = !1;
                }
            };
            return (t, e)=>(l(), E(g(re), {
                    onClick: a,
                    size: "small",
                    disabled: v.value,
                    loading: v.value
                }, {
                    icon: A(()=>e[0] || (e[0] = [
                            y("span", {
                                class: "pi pi-search pi-exclamation-triangle"
                            }, null, -1)
                        ])),
                    _: 1
                }, 8, [
                    "disabled",
                    "loading"
                ]));
        }
    });
    gt = {
        __name: "ContainedTextArea",
        props: {
            maxHeight: {
                type: [
                    Number,
                    String
                ],
                default: "12rem"
            }
        },
        emits: [
            "submit"
        ],
        setup (i, { emit: u }) {
            ve((s)=>({
                    fd6f281e: v.maxHeight
                }));
            const v = i, a = u, t = (s)=>{
                e.value = s.target.offsetHeight >= 180;
            }, e = b(!1);
            return (s, n)=>(l(), E(g(fe), {
                    onKeyup: t,
                    onKeydown: [
                        n[0] || (n[0] = ne(Y((o)=>a("submit"), [
                            "exact",
                            "prevent"
                        ]), [
                            "enter"
                        ])),
                        n[1] || (n[1] = ne(Y((o)=>o.target.blur(), [
                            "prevent"
                        ]), [
                            "escape"
                        ]))
                    ],
                    autoResize: "",
                    rows: "1",
                    class: T([
                        {
                            "scroll-input": e.value
                        },
                        "resizeable-textarea"
                    ])
                }, null, 8, [
                    "class"
                ]));
        }
    };
    $e = {
        key: 1
    };
    kt = j({
        __name: "PreviewPanel",
        props: {
            previewData: {}
        },
        setup (i) {
            const u = i;
            return (v, a)=>u.previewData ? (l(), E(g(D), {
                    key: 0,
                    multiple: "",
                    activeIndex: [
                        ...Array(u.previewData.length).keys()
                    ],
                    class: "preview-accordion"
                }, {
                    default: A(()=>[
                            (l(!0), c(z, null, q(u.previewData, (t, e)=>(l(), E(g(F), {
                                    key: e,
                                    header: e.toString(),
                                    class: "preview-accordion-tab"
                                }, {
                                    default: A(()=>[
                                            (l(!0), c(z, null, q(t, (s, n)=>(l(), E(g(me), {
                                                    class: "preview-container",
                                                    key: n,
                                                    legend: n.toString(),
                                                    toggleable: !0
                                                }, {
                                                    default: A(()=>[
                                                            x(I, {
                                                                class: "contextpreview-mime-bundle code-cell-output preview-container-table-wrapper",
                                                                mimeBundle: s
                                                            }, null, 8, [
                                                                "mimeBundle"
                                                            ])
                                                        ]),
                                                    _: 2
                                                }, 1032, [
                                                    "legend"
                                                ]))), 128))
                                        ]),
                                    _: 2
                                }, 1032, [
                                    "header"
                                ]))), 128))
                        ]),
                    _: 1
                }, 8, [
                    "activeIndex"
                ])) : (l(), c("div", $e, "No preview yet"));
        }
    });
    var K, se;
    function Ae() {
        if (se) return K;
        se = 1, K = e;
        var i = /(?:(?:\u001b\[)|\u009b)(?:(?:[0-9]{1,3})?(?:(?:;[0-9]{0,3})*)?[A-M|f-m])|\u001b[A-M]/, u = {
            reset: [
                "fff",
                "000"
            ],
            black: "000",
            red: "ff0000",
            green: "209805",
            yellow: "e8bf03",
            blue: "0000ff",
            magenta: "ff00ff",
            cyan: "00ffee",
            lightgrey: "f0f0f0",
            darkgrey: "888"
        }, v = {
            30: "black",
            31: "red",
            32: "green",
            33: "yellow",
            34: "blue",
            35: "magenta",
            36: "cyan",
            37: "lightgrey"
        }, a = {
            1: "font-weight:bold",
            2: "opacity:0.5",
            3: "<i>",
            4: "<u>",
            8: "display:none",
            9: "<del>"
        }, t = {
            23: "</i>",
            24: "</u>",
            29: "</del>"
        };
        [
            0,
            21,
            22,
            27,
            28,
            39,
            49
        ].forEach(function(n) {
            t[n] = "</span>";
        });
        function e(n) {
            if (!i.test(n)) return n;
            var o = [], f = n.replace(/\033\[(\d+)m/g, function(C, d) {
                var h = a[d];
                if (h) return ~o.indexOf(d) ? (o.pop(), "</span>") : (o.push(d), h[0] === "<" ? h : '<span style="' + h + ';">');
                var H = t[d];
                return H ? (o.pop(), H) : "";
            }), r = o.length;
            return r > 0 && (f += Array(r + 1).join("</span>")), f;
        }
        e.setColors = function(n) {
            if (typeof n != "object") throw new Error("`colors` parameter must be an Object.");
            var o = {};
            for(var f in u){
                var r = n.hasOwnProperty(f) ? n[f] : null;
                if (!r) {
                    o[f] = u[f];
                    continue;
                }
                if (f === "reset") {
                    if (typeof r == "string" && (r = [
                        r
                    ]), !Array.isArray(r) || r.length === 0 || r.some(function(d) {
                        return typeof d != "string";
                    })) throw new Error("The value of `" + f + "` property must be an Array and each item could only be a hex string, e.g.: FF0000");
                    var C = u[f];
                    r[0] || (r[0] = C[0]), (r.length === 1 || !r[1]) && (r = [
                        r[0]
                    ], r.push(C[1])), r = r.slice(0, 2);
                } else if (typeof r != "string") throw new Error("The value of `" + f + "` property must be a hex string, e.g.: FF0000");
                o[f] = r;
            }
            s(o);
        }, e.reset = function() {
            s(u);
        }, e.tags = {}, Object.defineProperty ? (Object.defineProperty(e.tags, "open", {
            get: function() {
                return a;
            }
        }), Object.defineProperty(e.tags, "close", {
            get: function() {
                return t;
            }
        })) : (e.tags.open = a, e.tags.close = t);
        function s(n) {
            a[0] = "font-weight:normal;opacity:1;color:#" + n.reset[0] + ";background:#" + n.reset[1], a[7] = "color:#" + n.reset[1] + ";background:#" + n.reset[0], a[90] = "color:#" + n.darkgrey;
            for(var o in v){
                var f = v[o], r = n[f] || "000";
                a[o] = "color:#" + r, o = parseInt(o), a[(o + 10).toString()] = "background:#" + r;
            }
        }
        return e.reset(), K;
    }
    var He = Ae();
    const le = ie(He);
    var W, ae;
    function Re() {
        if (ae) return W;
        ae = 1;
        var i = /["'&<>]/;
        W = u;
        function u(v) {
            var a = "" + v, t = i.exec(a);
            if (!t) return a;
            var e, s = "", n = 0, o = 0;
            for(n = t.index; n < a.length; n++){
                switch(a.charCodeAt(n)){
                    case 34:
                        e = "&quot;";
                        break;
                    case 38:
                        e = "&amp;";
                        break;
                    case 39:
                        e = "&#39;";
                        break;
                    case 60:
                        e = "&lt;";
                        break;
                    case 62:
                        e = "&gt;";
                        break;
                    default:
                        continue;
                }
                o !== n && (s += a.substring(o, n)), o = n + 1, s += e;
            }
            return o !== n ? s + a.substring(o, n) : s;
        }
        return W;
    }
    var Se = Re();
    let oe, Te, Me, Ee, Be, Pe, je, Le, Ve, ue, Oe, Ie, Ne, qe, ze, De, Qe, Ue, Ke, We, Ye, Ge, Je, Xe, Ze, et, tt, nt, st, lt, at, ot, rt, ct, it, ut, dt, pt;
    oe = ie(Se);
    Te = {
        key: 0
    };
    Me = {
        class: "code-cell-output-box-dropdown"
    };
    Ee = [
        "innerHTML"
    ];
    Be = {
        key: 3
    };
    Pe = {
        key: 1
    };
    je = [
        "onClickCapture"
    ];
    Le = [
        "innerHTML"
    ];
    Ve = {
        key: 3
    };
    ue = j({
        __name: "BeakerCodeCellOutput",
        props: [
            "outputs",
            "busy",
            "dropdownLayout"
        ],
        setup (i) {
            const u = i, v = (t)=>{
                const e = b(t?.metadata || (t.metadata = {}));
                e.value.collapsed = !e.value.collapsed;
            }, a = (t)=>{
                const e = Array.isArray(t.traceback) ? t.traceback?.join(`
`) : t.traceback?.toString();
                return {
                    "application/vnd.jupyter.error": t,
                    "application/vnd.jupyter.stderr": e || `${t.ename}: ${t.evalue}`
                };
            };
            return (t, e)=>(l(), c("div", {
                    class: T([
                        "code-cell-output",
                        {
                            "code-cell-output-dropdown": u.dropdownLayout
                        }
                    ])
                }, [
                    i.dropdownLayout ? (l(), c("div", Te, [
                        y("div", Me, [
                            x(g(D), null, {
                                default: A(()=>[
                                        x(g(F), {
                                            class: "code-cell-output-dropdown-tab",
                                            pt: {
                                                header: {
                                                    class: [
                                                        "code-cell-output-dropdown-header"
                                                    ]
                                                },
                                                headerAction: {
                                                    class: [
                                                        "code-cell-output-dropdown-headeraction"
                                                    ]
                                                },
                                                content: {
                                                    class: [
                                                        "code-cell-output-dropdown-content"
                                                    ]
                                                },
                                                headerIcon: {
                                                    class: [
                                                        "code-cell-output-dropdown-icon"
                                                    ]
                                                }
                                            }
                                        }, {
                                            header: A(()=>e[0] || (e[0] = [
                                                    y("span", {
                                                        class: "flex align-items-center gap-2 w-full",
                                                        style: {
                                                            "font-weight": "normal"
                                                        }
                                                    }, [
                                                        y("span", null, "Outputs")
                                                    ], -1)
                                                ])),
                                            default: A(()=>[
                                                    (l(!0), c(z, null, q(u.outputs, (s)=>(l(), c("div", {
                                                            class: "code-cell-dropdown-content",
                                                            key: `${s}-dropdown`
                                                        }, [
                                                            s.output_type == "stream" ? (l(), c("div", {
                                                                key: 0,
                                                                class: T(s.output_type),
                                                                innerHTML: g(le)(g(oe)(s.text))
                                                            }, null, 10, Ee)) : [
                                                                "display_data",
                                                                "execute_result"
                                                            ].includes(s.output_type) ? (l(), E(I, {
                                                                key: 1,
                                                                "mime-bundle": s.data,
                                                                class: "mime-bundle",
                                                                collapse: "true"
                                                            }, null, 8, [
                                                                "mime-bundle"
                                                            ])) : s.output_type == "error" ? (l(), c("div", {
                                                                key: 2,
                                                                class: T(s.output_type)
                                                            }, [
                                                                x(I, {
                                                                    "mime-bundle": a(s),
                                                                    collapse: "true"
                                                                }, null, 8, [
                                                                    "mime-bundle"
                                                                ])
                                                            ], 2)) : (l(), c("div", Be, V(s), 1))
                                                        ]))), 128))
                                                ]),
                                            _: 1
                                        })
                                    ]),
                                _: 1
                            })
                        ])
                    ])) : (l(), c("div", Pe, [
                        (l(!0), c(z, null, q(u.outputs, (s)=>(l(), c("div", {
                                class: T([
                                    "code-cell-output-box",
                                    {
                                        "collapsed-output": s.metadata?.collapsed
                                    }
                                ]),
                                key: s
                            }, [
                                y("div", {
                                    class: "output-collapse-box",
                                    onClickCapture: Y((n)=>v(s), [
                                        "stop",
                                        "prevent"
                                    ])
                                }, null, 40, je),
                                s.output_type == "stream" ? (l(), c("div", {
                                    key: 0,
                                    class: T(s.output_type),
                                    innerHTML: g(le)(g(oe)(s.text))
                                }, null, 10, Le)) : [
                                    "display_data",
                                    "execute_result"
                                ].includes(s.output_type) ? (l(), E(I, {
                                    key: 1,
                                    "mime-bundle": s.data,
                                    class: "mime-bundle",
                                    collapse: "true"
                                }, null, 8, [
                                    "mime-bundle"
                                ])) : s.output_type == "error" ? (l(), c("div", {
                                    key: 2,
                                    class: T(s.output_type)
                                }, [
                                    x(I, {
                                        "mime-bundle": a(s),
                                        collapse: "true"
                                    }, null, 8, [
                                        "mime-bundle"
                                    ])
                                ], 2)) : (l(), c("div", Ve, V(s), 1))
                            ], 2))), 128))
                    ]))
                ], 2));
        }
    });
    Oe = {
        class: "code-cell"
    };
    Ie = {
        class: "code-cell-grid"
    };
    Ne = {
        class: "code-output"
    };
    qe = {
        class: "state-info"
    };
    ze = {
        key: 0,
        class: "pi pi-spin pi-spinner busy-icon"
    };
    De = {
        modelClass: he,
        icon: "pi pi-code"
    };
    Fe = j({
        ...De,
        __name: "BeakerCodeCell",
        props: [
            "cell",
            "hideOutput",
            "codeStyles"
        ],
        emits: [
            "blur"
        ],
        setup (i, { expose: u, emit: v }) {
            const a = i, t = b(a.cell), { theme: e } = S("theme"), s = S("session"), n = b(), o = S("beakerSession"), f = S("notebook"), r = U(), C = b([]);
            let d;
            ((m)=>{
                m.Success = "ok", m.Modified = "modified", m.Error = "error", m.Pending = "pending", m.None = "none";
            })(d || (d = {}));
            const h = R(()=>typeof t.value?.last_execution?.checkpoint_index < "u"), H = ()=>t.value.rollback(s), M = R(()=>t.value?.busy), $ = async ()=>{
                const m = {
                    notebook_id: f.id,
                    cells: [
                        {
                            cell_id: t.value.id,
                            content: t.value.source
                        }
                    ]
                };
                await s.executeAction("lint_code", m).done;
            }, _ = R(()=>{
                const m = "secondary";
                return {
                    ok: "success",
                    modified: "warning",
                    error: "danger",
                    pending: m,
                    none: m
                }[t.value?.last_execution?.status] || m;
            }), p = (m)=>{
                f && f.selectCell(t.value), m.stopPropagation();
            };
            function k() {
                t.value.reset_execution_state();
            }
            const w = R(()=>o.activeContext?.language?.slug || void 0), P = (m)=>{
                a.cell.execute(s), L();
            }, te = (m)=>{
                n.value?.focus(), m === "start" ? m = 0 : m === "end" && (m = n.value?.view?.state?.doc?.length), m !== void 0 && n.value?.view?.dispatch({
                    selection: {
                        anchor: m,
                        head: m
                    }
                });
            }, L = ()=>{
                n.value?.blur();
                const m = r.vnode.el;
                ee(m)?.focus();
            };
            return u({
                execute: P,
                enter: te,
                exit: L,
                clear: ()=>{
                    t.value.source = "", t.value.outputs.splice(0, t.value.outputs.length);
                },
                cell: t,
                editor: n,
                lintAnnotations: C
            }), Q(()=>{
                o.cellRegistry[t.value.id] = r.vnode;
            }), X(()=>{
                delete o.cellRegistry[t.value.id];
            }), (m, O)=>{
                const de = ce("tooltip");
                return l(), c("div", Oe, [
                    y("div", Ie, [
                        y("div", {
                            class: T([
                                "code-data",
                                {
                                    "dark-mode": g(e).mode === "dark",
                                    [i.codeStyles]: a.codeStyles
                                }
                            ])
                        }, [
                            x(Z, {
                                "display-mode": "dark",
                                language: w.value,
                                modelValue: t.value.source,
                                "onUpdate:modelValue": O[0] || (O[0] = (pe)=>t.value.source = pe),
                                ref_key: "codeEditorRef",
                                ref: n,
                                placeholder: "Your code...",
                                disabled: M.value,
                                onChange: k,
                                onClick: p,
                                annotations: C.value,
                                "annotation-provider": "linter"
                            }, null, 8, [
                                "language",
                                "modelValue",
                                "disabled",
                                "annotations"
                            ])
                        ], 2),
                        y("div", Ne, [
                            G(x(ue, {
                                outputs: t.value.outputs,
                                busy: M.value,
                                "dropdown-layout": !1
                            }, null, 8, [
                                "outputs",
                                "busy"
                            ]), [
                                [
                                    ye,
                                    !i.hideOutput && t.value.outputs.length
                                ]
                            ])
                        ]),
                        y("div", qe, [
                            y("div", null, [
                                x(g(_e), {
                                    class: T([
                                        "execution-count-badge",
                                        {
                                            secondary: _.value === "secondary"
                                        }
                                    ]),
                                    severity: _.value,
                                    value: t.value.execution_count || " "
                                }, null, 8, [
                                    "class",
                                    "severity",
                                    "value"
                                ])
                            ]),
                            M.value ? (l(), c("i", ze)) : B("", !0),
                            G(x(xe, {
                                action: $,
                                text: ""
                            }, null, 512), [
                                [
                                    de,
                                    {
                                        value: "Analyze this code.",
                                        showDelay: 300
                                    },
                                    void 0,
                                    {
                                        bottom: !0
                                    }
                                ]
                            ]),
                            h.value ? (l(), E(g(re), {
                                key: 1,
                                class: "rollback-button",
                                severity: _.value,
                                icon: "pi pi-undo",
                                size: "small",
                                onClick: H
                            }, null, 8, [
                                "severity"
                            ])) : B("", !0)
                        ])
                    ])
                ]);
            };
        }
    });
    Qe = [
        "innerHTML"
    ];
    Ue = {
        key: 1
    };
    Ke = {
        class: "markdown-edit-cell-grid"
    };
    We = {
        modelClass: we,
        icon: "pi pi-pencil"
    };
    bt = j({
        ...We,
        __name: "BeakerMarkdownCell",
        props: [
            "cell"
        ],
        setup (i, { expose: u }) {
            const v = i, a = U(), t = S("beakerSession"), e = b(v.cell), { theme: s } = S("theme"), n = b(!1), o = b(null), f = b(null), r = S("notebook"), C = b(e.value.source), d = R(()=>N.parse(v.cell?.source || "")), h = (p)=>{
                r.selectCell(e.value), p.stopPropagation();
            }, H = ()=>{
                n.value = !1, e.value.source = C.value;
            }, M = (p)=>{
                n.value || (n.value = !0), J(()=>{
                    f.value?.focus(), p === "start" ? p = 0 : p === "end" && (p = f.value?.view?.state?.doc?.length), p !== void 0 && f.value?.view?.dispatch({
                        selection: {
                            anchor: p,
                            head: p
                        }
                    });
                });
            };
            return u({
                execute: H,
                enter: M,
                exit: ()=>{
                    if (C.value === e.value.source) n.value = !1;
                    else {
                        f.value?.blur();
                        const p = a.vnode.el;
                        ee(p)?.focus();
                    }
                },
                clear: ()=>{
                    e.value.source = "";
                },
                model: e,
                editor: f
            }), Q(()=>{
                N.setOptions({}), t.cellRegistry[e.value.id] = a.vnode;
            }), X(()=>{
                delete t.cellRegistry[e.value.id];
            }), (p, k)=>(l(), c("div", {
                    class: "markdown-cell",
                    onDblclick: k[1] || (k[1] = (w)=>M())
                }, [
                    n.value ? (l(), c("div", Ue, [
                        y("div", Ke, [
                            y("div", {
                                class: T([
                                    "markdown-edit-data",
                                    {
                                        "dark-mode": g(s).mode === "dark"
                                    }
                                ]),
                                ref: o.value
                            }, [
                                x(Z, {
                                    modelValue: C.value,
                                    "onUpdate:modelValue": k[0] || (k[0] = (w)=>C.value = w),
                                    placeholder: "Your markdown...",
                                    ref_key: "codeEditorRef",
                                    ref: f,
                                    autofocus: !1,
                                    language: "markdown",
                                    "display-mode": "dark",
                                    onClick: h
                                }, null, 8, [
                                    "modelValue"
                                ])
                            ], 2)
                        ])
                    ])) : (l(), c("div", {
                        key: 0,
                        innerHTML: d.value
                    }, null, 8, Qe))
                ], 32));
        }
    });
    Ye = {
        class: "llm-query-event"
    };
    Ge = {
        key: 0
    };
    Je = {
        key: 1
    };
    Xe = [
        "innerHTML"
    ];
    Ze = {
        key: 3
    };
    et = {
        key: 4
    };
    tt = [
        "innerHTML"
    ];
    nt = {
        key: 5,
        style: {
            position: "relative"
        }
    };
    st = {
        key: 6
    };
    lt = {
        key: 7
    };
    at = {
        key: 0,
        class: "pre"
    };
    ot = {
        key: 1,
        class: "pre"
    };
    rt = {
        key: 0,
        class: "pre"
    };
    ht = j({
        __name: "BeakerQueryCellEvent",
        props: [
            "event",
            "parentQueryCell",
            "codeStyles",
            "shouldHideAnsweredQuestions"
        ],
        setup (i, { expose: u }) {
            const v = S("beakerSession"), a = S("notebook"), t = b(), e = i;
            Q(()=>{
                N.setOptions({});
            });
            const s = ()=>{
                a && a.selectCell(e.event?.content.cell_id);
            }, n = R(()=>v.session.notebook.cells.indexOf(e.parentQueryCell.value)), o = R(()=>a ? n.value.toString() === a.selectedCellId : !1), f = R(()=>e.parentQueryCell?.children?.map((p)=>p?.outputs?.every((k)=>{
                        if (k?.data !== void 0) {
                            const w = Object.keys(k?.data);
                            return k?.output_type === "execute_result" && w.length === 1 && w[0] === "text/plain";
                        } else return !0;
                    })).every((p)=>p) ? [] : e.parentQueryCell?.children?.entries()), r = R(()=>{
                const _ = [];
                return e.parentQueryCell?.children?.entries()?.forEach(([p, k])=>{
                    k?.outputs?.forEach((w)=>{
                        const P = [
                            "image/png",
                            "text/html"
                        ];
                        [
                            "execute_result",
                            "display_data"
                        ].includes(w?.output_type) && P.map((L)=>Object.keys(w?.data ?? []).includes(L)).some((L)=>L) && _.push(p);
                    });
                }), _;
            }), C = (_)=>{
                const p = v.session.notebook;
                for (const k of p.cells){
                    const w = k.children?.find((P)=>P.id === _);
                    if (typeof w < "u") return w;
                }
            }, d = (_)=>[
                    "response",
                    "user_answer",
                    "user_question"
                ].includes(_.type), h = (_)=>!(_.type === "response" && _.content === "None"), H = (_)=>_.type === "user_question" && _.waitForUserInput, M = R(()=>d(e.event) ? N.parse(e.event.content, {
                    async: !1
                }).trim() : "");
            function $() {}
            return u({
                execute: $
            }), (_, p)=>{
                const k = ce("keybindings");
                return l(), c("div", Ye, [
                    H(i.event) ? (l(), c("div", Ge, p[0] || (p[0] = [
                        y("span", {
                            class: "waiting-text"
                        }, [
                            y("i", {
                                class: "pi pi-spin pi-spinner",
                                style: {
                                    "font-size": "1rem"
                                }
                            }),
                            ge(" Waiting for user input in conversation. ")
                        ], -1)
                    ]))) : i.event.type === "user_question" && e.shouldHideAnsweredQuestions ? (l(), c("div", Je)) : d(i.event) && h(i.event) ? (l(), c("div", {
                        key: 2,
                        innerHTML: M.value,
                        class: "md-inline"
                    }, null, 8, Xe)) : B("", !0),
                    e.event?.type === "response" && f.value !== 0 ? (l(), c("div", Ze, [
                        x(g(D), {
                            multiple: !0,
                            "active-index": r.value
                        }, {
                            default: A(()=>[
                                    (l(!0), c(z, null, q(f.value, ([w, P])=>(l(), E(g(F), {
                                            key: w,
                                            pt: {
                                                header: {
                                                    class: [
                                                        "agent-response-header"
                                                    ]
                                                },
                                                headerAction: {
                                                    class: [
                                                        "agent-response-headeraction"
                                                    ]
                                                },
                                                content: {
                                                    class: [
                                                        "agent-response-content"
                                                    ]
                                                },
                                                headerIcon: {
                                                    class: [
                                                        "agent-response-icon"
                                                    ]
                                                }
                                            }
                                        }, {
                                            header: A(()=>p[1] || (p[1] = [
                                                    y("span", {
                                                        class: "flex align-items-center gap-2 w-full"
                                                    }, [
                                                        y("span", null, "Outputs")
                                                    ], -1)
                                                ])),
                                            default: A(()=>[
                                                    x(ue, {
                                                        outputs: P?.outputs
                                                    }, null, 8, [
                                                        "outputs"
                                                    ])
                                                ]),
                                            _: 2
                                        }, 1024))), 128))
                                ]),
                            _: 1
                        }, 8, [
                            "active-index"
                        ])
                    ])) : e.event?.type === "thought" ? (l(), c("div", et, [
                        y("div", {
                            innerHTML: g(N).parse(e.event.content.thought)
                        }, null, 8, tt)
                    ])) : e.event?.type === "code_cell" ? (l(), c("div", nt, [
                        G(x(Fe, {
                            onClick: s,
                            cell: C(e?.event.content.cell_id),
                            "drag-enabled": !1,
                            "code-styles": e.codeStyles,
                            class: T({
                                selected: o.value,
                                "query-event-code-cell": !0
                            }),
                            "hide-output": !1,
                            ref_key: "codeCellRef",
                            ref: t
                        }, null, 8, [
                            "cell",
                            "code-styles",
                            "class"
                        ]), [
                            [
                                k,
                                {
                                    "keydown.enter.ctrl.prevent.capture.in-editor": (w)=>{
                                        t.value.execute();
                                    },
                                    "keydown.enter.shift.prevent.capture.in-editor": (w)=>{
                                        t.value.execute();
                                    }
                                }
                            ]
                        ]),
                        ke(_.$slots, "code-cell-controls")
                    ])) : e.event?.type === "error" && e.event.content.ename === "CancelledError" ? (l(), c("span", st, p[2] || (p[2] = [
                        y("h4", {
                            class: "p-error"
                        }, "Request cancelled.", -1)
                    ]))) : e.event?.type === "error" ? (l(), c("span", lt, [
                        y("div", null, [
                            e?.event.content.ename ? (l(), c("pre", at, "                    " + V(e?.event.content.ename) + `
                `, 1)) : B("", !0),
                            e?.event.content.evalue ? (l(), c("pre", ot, "                    " + V(e?.event.content.evalue) + `
                `, 1)) : B("", !0),
                            x(g(D), null, {
                                default: A(()=>[
                                        x(g(F), {
                                            pt: {
                                                header: {
                                                    class: [
                                                        "agent-response-header"
                                                    ]
                                                },
                                                headerAction: {
                                                    class: [
                                                        "agent-response-headeraction"
                                                    ]
                                                },
                                                content: {
                                                    class: [
                                                        "agent-response-content",
                                                        "agent-response-content-error"
                                                    ]
                                                },
                                                headerIcon: {
                                                    class: [
                                                        "agent-response-icon"
                                                    ]
                                                }
                                            }
                                        }, {
                                            header: A(()=>p[3] || (p[3] = [
                                                    y("span", {
                                                        class: "flex align-items-center gap-2 w-full"
                                                    }, [
                                                        y("span", {
                                                            class: "font-bold white-space-nowrap"
                                                        }, "Traceback:")
                                                    ], -1)
                                                ])),
                                            default: A(()=>[
                                                    e?.event.content.traceback ? (l(), c("pre", rt, "                            " + V(e?.event.content.traceback?.join(`
`)) + `
                        `, 1)) : B("", !0)
                                                ]),
                                            _: 1
                                        })
                                    ]),
                                _: 1
                            })
                        ])
                    ])) : B("", !0)
                ]);
            };
        }
    });
    ct = [
        "error",
        "response"
    ];
    wt = (i)=>i?.length > 0 ? ct.includes(i[i.length - 1].type) : !1;
    Ct = (i)=>{
        const u = be(i.cell), v = b(u.value.source === ""), a = b(100), t = b(u.value.source), e = b(""), s = b(), n = S("session"), o = S("beakerSession"), f = U(), r = R(()=>[
                ...i.cell.events
            ]);
        function C() {
            const $ = f?.root?.props?.config, _ = $ ? $.extra?.send_notebook_state : void 0;
            u.value.source = t.value, v.value = !1, J(()=>{
                i.cell.execute(n, _).registerMessageHook((k)=>{
                    k.cell = u.value;
                });
            });
        }
        function d($) {
            v.value || (v.value = !0), $ === "start" ? $ = 0 : $ === "end" && ($ = s.value?.$el?.value.length || -1), J(()=>{
                s.value?.$el?.focus(), s.value.$el.setSelectionRange($, $);
            });
        }
        function h() {
            t.value === u.value.source ? v.value = !1 : s.value?.$el?.blur();
        }
        function H() {
            u.value.source = "", v.value = !0, a.value = 100, t.value = "", e.value = "";
        }
        function M() {
            e.value.trim() && (i.cell.respond(e.value, n), e.value = "");
        }
        return {
            cell: u,
            isEditing: v,
            promptEditorMinHeight: a,
            promptText: t,
            response: e,
            textarea: s,
            session: n,
            beakerSession: o,
            events: r,
            execute: C,
            enter: d,
            exit: h,
            clear: H,
            respond: M
        };
    };
    it = {
        class: "raw-cell"
    };
    ut = {
        class: "raw-cell-header"
    };
    dt = {
        key: 0
    };
    pt = {
        modelClass: Ce,
        icon: "pi pi-question-circle"
    };
    xt = j({
        ...pt,
        __name: "BeakerRawCell",
        props: [
            "cell"
        ],
        setup (i, { expose: u }) {
            const v = i, a = U(), t = b(v.cell), e = b(null), s = S("beakerSession");
            let n;
            ((d)=>{
                d.Success = "success", d.Modified = "modified", d.Error = "error", d.Pending = "pending";
            })(n || (n = {})), R(()=>[]);
            const o = (d)=>{
                r();
            }, f = (d)=>{
                e.value?.focus(), d === "start" ? d = 0 : d === "end" && (d = e.value?.view?.state?.doc?.length), d !== void 0 && e.value?.view?.dispatch({
                    selection: {
                        anchor: d,
                        head: d
                    }
                });
            }, r = ()=>{
                e.value.blur();
                const d = a.vnode.el;
                ee(d)?.focus();
            };
            return u({
                execute: o,
                enter: f,
                exit: r,
                clear: ()=>{
                    t.value.source = "";
                },
                model: t,
                editor: e
            }), Q(()=>{
                s.cellRegistry[t.value.id] = a.vnode;
            }), X(()=>{
                delete s.cellRegistry[t.value.id];
            }), (d, h)=>(l(), c("div", it, [
                    y("div", ut, [
                        h[1] || (h[1] = y("span", {
                            class: "raw-cell-title"
                        }, "Raw cell", -1)),
                        v.cell.cell_type !== "raw" ? (l(), c("span", dt, " - (Unrenderable cell type '" + V(v.cell.cell_type) + "')", 1)) : B("", !0)
                    ]),
                    x(Z, {
                        "display-mode": "dark",
                        language: "julia",
                        modelValue: t.value.source,
                        "onUpdate:modelValue": h[0] || (h[0] = (H)=>t.value.source = H),
                        ref_key: "codeEditorRef",
                        ref: e,
                        placeholder: "Raw cell content...",
                        autofocus: !1
                    }, null, 8, [
                        "modelValue"
                    ])
                ]));
        }
    });
});
export { xt as _, bt as a, Fe as b, kt as c, gt as d, ht as e, xe as f, wt as i, Ct as u, __tla };
