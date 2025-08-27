import { d as O, r as g, y as b, o as f, E as u, u as l, a9 as G, I as x, L as I, Q as A, a0 as F, B as m, a1 as B, af as Q, g as D, z as U, f as V, w as X, Y as z, M as C, j as S, G as j, ab as Y, i as ee, J as te, K as ne, A as ae, ah as oe, O as se } from "./primevue-1TEWPnDt.js";
import { _ as Z } from "./_plugin-vue_export-helper-DlAUqK2U.js";
import { _ as re } from "./jupyterlab-C2EV-Dpr.js";
import { getDocument as W, __tla as __tla_0 } from "./pdfjs-4lX-eNFD.js";
import { j as N, h as le, m as ie, __tla as __tla_1 } from "./DebugPanel.vue_vue_type_style_index_0_lang-PW_f_WLw.js";
import { R as q, __tla as __tla_2 } from "./index-D-jLGYR3.js";
let Ue, tt, Ke, He, Xe, Qe, et, Te, Ye, Ze, Je;
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
    let ue, de, ce, pe, ve, fe, me, ge, ye, we, he, _e, ke, be, xe, $e, Ce, Pe, Le;
    ue = O({
        __name: "PDFControls",
        props: [
            "page",
            "scale",
            "isLoading",
            "sidebarCallback"
        ],
        emits: [
            "pdf-page-next",
            "pdf-page-prev",
            "pdf-zoom-in",
            "pdf-zoom-out"
        ],
        setup (e, { emit: t }) {
            const s = e, n = t, h = g(null), y = (d)=>`${Math.floor(d * 100)}%`;
            return (d, o)=>(f(), b("div", {
                    ref_key: "controlsContainer",
                    ref: h,
                    class: "controls-container"
                }, [
                    u(l(G), null, {
                        start: x(()=>[
                                u(l(I), {
                                    class: "pdf-ui-button",
                                    icon: "pi pi-chevron-left",
                                    onClick: o[0] || (o[0] = (i)=>n("pdf-page-prev")),
                                    disabled: e.isLoading
                                }, null, 8, [
                                    "disabled"
                                ]),
                                u(l(I), {
                                    class: "pdf-ui-button",
                                    icon: "pi pi-chevron-right",
                                    onClick: o[1] || (o[1] = (i)=>n("pdf-page-next")),
                                    disabled: e.isLoading
                                }, null, 8, [
                                    "disabled"
                                ]),
                                u(l(A), {
                                    class: "pdf-ui-inputselection"
                                }, {
                                    default: x(()=>[
                                            u(l(F), null, {
                                                default: x(()=>o[4] || (o[4] = [
                                                        m("i", {
                                                            class: "pi pi-book"
                                                        }, null, -1)
                                                    ])),
                                                _: 1
                                            }),
                                            u(l(B), {
                                                placeholder: "Page",
                                                value: s?.page
                                            }, null, 8, [
                                                "value"
                                            ])
                                        ]),
                                    _: 1
                                })
                            ]),
                        center: x(()=>[
                                u(l(I), {
                                    class: "pdf-ui-button",
                                    icon: "pi pi-search-minus",
                                    onClick: o[2] || (o[2] = (i)=>n("pdf-zoom-out"))
                                }),
                                u(l(I), {
                                    class: "pdf-ui-button",
                                    icon: "pi pi-search-plus",
                                    onClick: o[3] || (o[3] = (i)=>n("pdf-zoom-in"))
                                }),
                                u(l(A), {
                                    class: "pdf-ui-inputselection"
                                }, {
                                    default: x(()=>[
                                            u(l(F), null, {
                                                default: x(()=>o[5] || (o[5] = [
                                                        m("i", {
                                                            class: "pi pi-search"
                                                        }, null, -1)
                                                    ])),
                                                _: 1
                                            }),
                                            u(l(B), {
                                                placeholder: "Zoom",
                                                value: y(s?.scale)
                                            }, null, 8, [
                                                "value"
                                            ])
                                        ]),
                                    _: 1
                                })
                            ]),
                        _: 1
                    })
                ], 512));
        }
    });
    de = Z(ue, [
        [
            "__scopeId",
            "data-v-b6ee0017"
        ]
    ]);
    ce = {
        __name: "PDFPage",
        props: [
            "sidebarCallback",
            "url",
            "scale",
            "page"
        ],
        setup (e, { expose: t }) {
            const s = async function() {
                const p = await re(()=>import("./pdfjs-4lX-eNFD.js").then(async (m)=>{
                        await m.__tla;
                        return m;
                    }), []);
                p.GlobalWorkerOptions.workerSrc = new URL("/static/pdf.worker-DHtGXOM1.mjs", import.meta.url).toString();
            }, n = e, h = g(null), y = g(null);
            let d = null;
            const o = g(!1), i = g(null);
            let c = null;
            const k = async (p)=>{
                if (!d) return;
                o.value = !0;
                const a = await d.getPage(p), _ = a.getViewport({
                    scale: n.scale
                });
                if (!y.value) return;
                const w = y.value.getContext("2d");
                y.value.width = _.width, y.value.height = _.height;
                const T = {
                    canvasContext: w,
                    viewport: _
                };
                c = a.render(T), await c.promise, o.value = !1;
            }, P = async ()=>{
                if (typeof n.url == "object" && n.url instanceof File) {
                    const p = new FileReader;
                    p.readAsArrayBuffer(n.url), p.onload = async (a)=>{
                        d = await W({
                            data: a.target.result
                        }).promise, i.value = d?._pdfInfo?.numPages, k(n.page);
                    };
                } else typeof n.url == "string" && (d = await W(n.url).promise, i.value = d?._pdfInfo?.numPages, k(n.page));
            };
            return t({
                pages: i,
                isLoading: o,
                renderTask: c
            }), Q(async ()=>{
                await s(), await P();
            }), D(()=>[
                    n.url
                ], P), D(()=>[
                    n.scale,
                    n.page
                ], ()=>k(n.page)), (p, a)=>(f(), b("div", {
                    ref_key: "pdfContainer",
                    ref: h,
                    class: "pdf-container"
                }, [
                    m("canvas", {
                        ref_key: "canvas",
                        ref: y,
                        class: "pdf-canvas"
                    }, null, 512)
                ], 512));
        }
    };
    pe = Z(ce, [
        [
            "__scopeId",
            "data-v-e9dd6f42"
        ]
    ]);
    ve = 4;
    fe = O({
        __name: "PDFPreview",
        props: {
            url: {}
        },
        setup (e, { expose: t }) {
            const s = [
                .25,
                .5,
                .75,
                .9,
                1,
                1.1,
                1.25,
                1.5,
                2,
                3,
                4
            ], n = (i, c, k)=>i <= c ? c : i >= k ? k : i, h = e, y = g(1), d = g(null), o = g(ve);
            return t({
                pdf: d
            }), (i, c)=>(f(), b(U, null, [
                    u(de, {
                        onPdfPageNext: c[0] || (c[0] = ()=>{
                            y.value = n(y.value + 1, 1, d.value?.pages ?? 1);
                        }),
                        onPdfPagePrev: c[1] || (c[1] = ()=>{
                            y.value = n(y.value - 1, 1, d.value?.pages ?? 1);
                        }),
                        onPdfZoomIn: c[2] || (c[2] = ()=>{
                            o.value = n(o.value + 1, 0, s.length - 1);
                        }),
                        onPdfZoomOut: c[3] || (c[3] = ()=>{
                            o.value = n(o.value - 1, 0, s.length - 1);
                        }),
                        page: y.value,
                        scale: s[o.value]
                    }, null, 8, [
                        "page",
                        "scale"
                    ]),
                    u(pe, {
                        ref_key: "pdf",
                        ref: d,
                        url: h.url,
                        scale: s[o.value],
                        page: y.value
                    }, null, 8, [
                        "url",
                        "scale",
                        "page"
                    ])
                ], 64));
        }
    });
    me = {
        class: "preview-container-pre"
    };
    ge = {
        key: 0,
        class: "preview-standard-toolbar"
    };
    ye = {
        class: "preview-under-toolbar"
    };
    we = {
        key: 0
    };
    he = {
        key: 1,
        class: "preview-payload"
    };
    _e = {
        key: 0,
        class: "pdf-preview"
    };
    ke = {
        key: 1,
        class: "text-preview"
    };
    be = {
        key: 2,
        class: "image-preview"
    };
    xe = [
        "src"
    ];
    $e = {
        key: 3,
        class: "csv-preview"
    };
    Ce = 500;
    Pe = 260;
    Ue = O({
        __name: "FileContentsPanel",
        props: [
            "url",
            "mimetype"
        ],
        setup (e) {
            const t = g(), s = g(), n = g(""), h = g(!1), y = ()=>{
                const r = ($)=>{
                    const E = window.innerWidth - ($.x - P.value / 2);
                    p.value = Math.min(Math.max(E, Pe), window.innerWidth * .9);
                }, v = ()=>{
                    document.querySelector("body").removeEventListener("mousemove", r), document.querySelector("body").removeEventListener("mouseup", this);
                };
                document.querySelector("body").addEventListener("mousemove", r), document.querySelector("body").addEventListener("mouseup", v);
            }, d = (r)=>r.startsWith("image/") ? "image" : r === "application/pdf" ? "pdf" : r === "text/csv" ? "csv" : r === "text/tsv" ? "tsv" : r === "application/vnd.ms-excel" || r === "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ? "excel" : "plaintext", o = {
                "application/pdf": {
                    overridesToolbar: !0,
                    skipContents: !0
                },
                "image/png": {
                    skipContents: !0
                },
                "text/csv": {
                    hasRawToggle: !0
                },
                "text/tsv": {
                    hasRawToggle: !0
                }
            }, i = g({
                isLoading: !1,
                contentLength: -1
            }), c = g(!1), k = new TextDecoder, P = g(5), p = g(614 + P.value), a = e, _ = V(()=>a.mimetype ?? n.value ?? ""), w = g(), T = V(()=>{
                const r = i.value?.contents, v = d(_.value);
                return v === "image" || v === "pdf" ? "<loaded elsewhere via url>" : r ? r.length === 0 ? "<file is 0 bytes>" : v === "excel" ? r : k.decode(r) : "";
            });
            D(()=>[
                    T.value
                ], (r, v)=>{
                t.value && (t.value.model = r[0]);
            });
            const H = V(()=>{
                const r = a.url?.split("/");
                return r === void 0 ? "No file selected." : r.length > 0 ? r[r.length - 1] : "";
            }), J = async (r)=>{
                const v = await fetch(r, {
                    method: "HEAD"
                });
                return [
                    "Content-Type",
                    "Content-Length"
                ].map(($)=>v.headers.get($));
            }, K = async (r)=>{
                w.value = new AbortController;
                const v = await fetch(r, {
                    signal: w.value.signal
                }), $ = [];
                for await (const L of v.body)$.push(L);
                if ($.length === 0) return [];
                const E = new Uint8Array($.map((L)=>L.length).reduce((L, M)=>L + M));
                return $.reduce((L, M)=>(E.set(M, L), L + M.length), 0), E;
            };
            return D(()=>[
                    a.url,
                    a.mimetype
                ], async (r, v)=>{
                v.length >= 2 && v[1] === "application/pdf" && console.log("interrupted pdf rendering for another preview"), i.value = {
                    isLoading: !0,
                    contentLength: 0
                };
                const $ = setTimeout(()=>{
                    c.value = !0;
                }, Ce), [E, L] = await J(a.url);
                a.mimetype === void 0 || a.mimetype == null ? n.value = E : n.value = void 0, i.value.contentLength = parseInt(L, 10), (o[a.mimetype] ?? {})?.skipContents || (i.value.contents = await K(a.url)), i.value.isLoading = !1, c.value = !1, clearTimeout($);
            }), (r, v)=>(f(), b("div", me, [
                    m("div", {
                        class: "preview-draggable",
                        style: z(`width: ${P.value}px;`),
                        onMousedown: v[0] || (v[0] = X(($)=>y(), [
                            "left",
                            "prevent"
                        ]))
                    }, null, 36),
                    m("div", {
                        class: "preview-container-main",
                        style: z(`max-width: calc(100% - ${P.value}px);`)
                    }, [
                        o[_.value]?.overridesToolbar ? C("", !0) : (f(), b("div", ge, [
                            u(l(G), null, {
                                center: x(()=>[
                                        m("span", null, j(H.value), 1)
                                    ]),
                                end: x(()=>[
                                        o[_.value]?.hasRawToggle ? (f(), S(l(I), {
                                            key: 0,
                                            class: "preview-raw",
                                            onClick: v[1] || (v[1] = ($)=>h.value = !h.value),
                                            label: h.value ? "Rich View" : "Raw View"
                                        }, null, 8, [
                                            "label"
                                        ])) : C("", !0)
                                    ]),
                                _: 1
                            })
                        ])),
                        m("div", ye, [
                            c.value && i.value.isLoading ? (f(), b("div", we, [
                                u(l(I), {
                                    class: "preview-cancel",
                                    onClick: v[2] || (v[2] = ($)=>w.value.abort()),
                                    severity: "danger",
                                    label: "Cancel Preview"
                                }),
                                m("span", null, "File is " + j(i.value.contentLength / 1e6) + " MB", 1)
                            ])) : C("", !0),
                            i.value.isLoading ? C("", !0) : (f(), b("div", he, [
                                d(_.value) === "pdf" ? (f(), b("div", _e, [
                                    u(fe, {
                                        ref_key: "pdfPreviewRef",
                                        ref: s,
                                        url: e.url
                                    }, null, 8, [
                                        "url"
                                    ])
                                ])) : C("", !0),
                                d(_.value) === "plaintext" ? (f(), b("div", ke, [
                                    u(N, {
                                        readonly: !0,
                                        "display-mode": "dark",
                                        modelValue: T.value,
                                        ref_key: "codeEditorRef",
                                        ref: t,
                                        placeholder: "Loading...",
                                        language: _.value === "text/x-python" ? "python" : void 0
                                    }, null, 8, [
                                        "modelValue",
                                        "language"
                                    ])
                                ])) : C("", !0),
                                d(_.value) === "image" ? (f(), b("div", be, [
                                    m("img", {
                                        src: e.url
                                    }, null, 8, xe)
                                ])) : C("", !0),
                                [
                                    "csv",
                                    "tsv",
                                    "excel"
                                ].includes(d(_.value)) ? (f(), b("div", $e, [
                                    !h.value && !i.value.isLoading ? (f(), S(le, {
                                        key: 0,
                                        mimeBundle: {
                                            [_.value]: T.value
                                        }
                                    }, null, 8, [
                                        "mimeBundle"
                                    ])) : C("", !0),
                                    h.value ? (f(), S(N, {
                                        key: 1,
                                        "display-mode": "dark",
                                        modelValue: T.value,
                                        ref_key: "codeEditorRef",
                                        ref: t,
                                        placeholder: "Loading..."
                                    }, null, 8, [
                                        "modelValue"
                                    ])) : C("", !0)
                                ])) : C("", !0)
                            ]))
                        ])
                    ], 4)
                ]));
        }
    });
    Le = (e)=>[
            e.sessionId,
            e?.integrationId,
            e?.resourceType,
            e?.resourceId
        ].filter((t)=>t).join("/");
    async function R(e, t, s) {
        const n = `/beaker/integrations/${Le(t)}`;
        console.log(`api request: ${e} ${n}`);
        const h = await fetch(n, {
            method: e,
            headers: {
                "Content-Type": "application/json"
            },
            ...s === void 0 ? {} : {
                body: JSON.stringify(s)
            }
        });
        if (!h.ok) throw new Error(h.statusText);
        return await h.json();
    }
    Te = (e)=>e.provider.split(":")[0];
    Ze = async (e)=>(await R("GET", {
            sessionId: e
        })).integrations;
    He = async (e, t)=>await R("POST", {
            sessionId: e
        }, t);
    Je = async (e, t, s)=>await R("POST", {
            sessionId: e,
            integrationId: t
        }, s);
    Ke = async (e, t)=>(await R("GET", {
            sessionId: e,
            integrationId: t,
            resourceType: "all"
        })).resources;
    Qe = async (e, t, s)=>await R("POST", {
            sessionId: e,
            integrationId: t,
            resourceType: "new"
        }, s);
    Xe = async (e, t, s, n)=>await R("POST", {
            sessionId: e,
            integrationId: t,
            resourceType: "new",
            resourceId: s
        }, n);
    Ye = async (e, t, s)=>await R("DELETE", {
            sessionId: e,
            integrationId: t,
            resourceType: "any",
            resourceId: s
        });
    et = function(e, t) {
        return Object.fromEntries(Object.entries(e ?? {}).filter(([s, n])=>n.resource_type === t));
    };
    let Ie, Re, Ee, Se, De, Me, Ve, je, Oe, Ae, Fe;
    Ie = {
        class: "integrations-panel"
    };
    Re = {
        class: "integration-header"
    };
    Ee = {
        style: {
            display: "flex",
            "flex-direction": "column",
            "padding-top": "0.25rem",
            "padding-bottom": "0.25rem",
            gap: "0.5rem",
            width: "100%"
        }
    };
    Se = {
        style: {
            display: "flex",
            "flex-direction": "column",
            "padding-top": "0.25rem",
            "padding-bottom": "0.25rem",
            gap: "0.5rem",
            width: "100%"
        }
    };
    De = {
        class: "integration-list"
    };
    Me = {
        class: "integration-provider"
    };
    Ve = [
        "onMouseenter"
    ];
    je = {
        class: "integration-card-title"
    };
    Oe = {
        class: "integration-card-title-text"
    };
    Ae = {
        key: 0
    };
    Fe = [
        "innerHTML"
    ];
    tt = O({
        __name: "IntegrationPanel",
        props: {
            modelValue: {},
            modelModifiers: {}
        },
        emits: [
            "update:modelValue"
        ],
        setup (e) {
            const t = g(void 0), s = Y(e, "modelValue"), n = new URLSearchParams(window.location.search), h = n.has("session") ? `&session=${n.get("session")}` : "";
            ee("beakerSession");
            const y = (p)=>p.toSorted((a, _)=>a?.name.localeCompare(_?.name)), d = (p)=>p.filter((a)=>t?.value === void 0 || a?.name?.toLowerCase()?.includes(t?.value?.toLowerCase())), o = (p)=>p.map((a)=>({
                        ...a,
                        description: ie.parse(a?.description ?? "")
                    })), i = (p)=>o(d(y(p))), c = V(()=>Object.values(s.value)), k = g(void 0), P = g(void 0);
            return D(t, ()=>{
                const p = d(c.value);
                if (p.length === 1) {
                    k.value = p[0].slug;
                    return;
                }
                k.value = void 0;
            }), (p, a)=>{
                const _ = te("tooltip");
                return f(), b("div", Ie, [
                    m("div", Re, [
                        u(l(A), null, {
                            default: x(()=>[
                                    u(l(F), null, {
                                        default: x(()=>a[3] || (a[3] = [
                                                m("i", {
                                                    class: "pi pi-search"
                                                }, null, -1)
                                            ])),
                                        _: 1
                                    }),
                                    u(l(B), {
                                        placeholder: "Search Integrations...",
                                        modelValue: t.value,
                                        "onUpdate:modelValue": a[0] || (a[0] = (w)=>t.value = w)
                                    }, null, 8, [
                                        "modelValue"
                                    ]),
                                    t.value !== void 0 && t.value !== "" ? ne((f(), S(l(I), {
                                        key: 0,
                                        icon: "pi pi-times",
                                        severity: "danger",
                                        onClick: a[1] || (a[1] = ()=>{
                                            t.value = void 0;
                                        })
                                    }, null, 512)), [
                                        [
                                            _,
                                            "Clear Search"
                                        ]
                                    ]) : C("", !0)
                                ]),
                            _: 1
                        }),
                        m("div", Ee, [
                            u(l(q), {
                                to: `/integrations?selected=new${l(h)}`,
                                "aria-label": "Edit {{ integration?.name }} "
                            }, {
                                default: x(()=>[
                                        u(l(I), {
                                            style: {
                                                height: "32px"
                                            },
                                            icon: "pi pi-plus",
                                            label: "Add New Integration"
                                        })
                                    ]),
                                _: 1
                            }, 8, [
                                "to"
                            ])
                        ]),
                        m("div", Se, [
                            m("div", null, [
                                m("i", null, j(c.value.length) + " integrations available:", 1)
                            ])
                        ])
                    ]),
                    m("div", De, [
                        m("div", Me, [
                            (f(!0), b(U, null, ae(i(Object.values(s.value)), (w)=>(f(), b("div", {
                                    class: "integration-card",
                                    key: w?.name,
                                    onMouseleave: a[2] || (a[2] = (T)=>P.value = void 0),
                                    onMouseenter: (T)=>P.value = w.uuid
                                }, [
                                    u(l(se), {
                                        pt: {
                                            root: {
                                                style: "transition: background-color 150ms linear;" + (P.value === w.uuid ? "background-color: var(--p-surface-c); cursor: pointer;" : "")
                                            }
                                        },
                                        onClick: (T)=>{
                                            k.value = k.value === w.uuid ? void 0 : w.uuid;
                                        }
                                    }, oe({
                                        title: x(()=>[
                                                m("div", je, [
                                                    m("span", Oe, j(w?.name), 1),
                                                    k.value === w.uuid ? (f(), b("span", Ae, [
                                                        u(l(q), {
                                                            to: `/integrations?selected=${w?.uuid}${l(h)}`,
                                                            "aria-label": "Edit {{ integration?.name }} "
                                                        }, {
                                                            default: x(()=>[
                                                                    l(Te)(w) === "adhoc" ? (f(), S(l(I), {
                                                                        key: 0,
                                                                        style: {
                                                                            width: "fit-content",
                                                                            height: "32px",
                                                                            "margin-right": "0.5rem"
                                                                        },
                                                                        icon: "pi pi-pencil",
                                                                        label: "Edit"
                                                                    })) : C("", !0)
                                                                ]),
                                                            _: 2
                                                        }, 1032, [
                                                            "to"
                                                        ])
                                                    ])) : C("", !0)
                                                ])
                                            ]),
                                        _: 2
                                    }, [
                                        k.value === w.uuid ? {
                                            name: "content",
                                            fn: x(()=>[
                                                    m("div", {
                                                        class: "integration-main-content",
                                                        style: {
                                                            overflow: "hidden"
                                                        },
                                                        innerHTML: w.description
                                                    }, null, 8, Fe)
                                                ]),
                                            key: "0"
                                        } : void 0
                                    ]), 1032, [
                                        "pt",
                                        "onClick"
                                    ])
                                ], 40, Ve))), 128))
                        ])
                    ])
                ]);
            };
        }
    });
});
export { Ue as _, tt as a, Ke as b, He as c, Xe as d, Qe as e, et as f, Te as g, Ye as h, Ze as l, Je as u, __tla };
