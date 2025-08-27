import { d as D, i as P, r as k, j as E, o as a, u as t, O as me, I as u, E as n, a as L, w as T, L as M, Q as pe, n as fe, y as v, B as p, R as ae, z as G, A as le, S as ge, f as C, g as se, U as _e, V as ye, W as ke, J as W, M as I, K as B, X as de, Y as ie, Z as re, G as ne, _ as F, $ as X, a0 as we, a1 as be, N as ce, a2 as Ce, p as xe } from "./primevue-1TEWPnDt.js";
import { B as $e, a as qe, L as Se, b as Re, w as Ie, _ as Me, c as ue, d as R, e as Ee, f as Pe, g as Ne, __tla as __tla_0 } from "./DebugPanel.vue_vue_type_style_index_0_lang-PW_f_WLw.js";
import { d as ve, u as Te, i as J, e as oe, _ as Be, a as Ve, b as ze, c as Qe, __tla as __tla_1 } from "./BeakerRawCell.vue_vue_type_style_index_0_lang-DHQ28atJ.js";
import { _ as Ae, a as Le, b as De, __tla as __tla_2 } from "./MediaPanel.vue_vue_type_style_index_0_lang-BO_XdLt2.js";
import { N as Fe } from "./NotebookSvg-DhCzyRVi.js";
import { _ as He, a as Oe, l as Ue, __tla as __tla_3 } from "./IntegrationPanel.vue_vue_type_style_index_0_lang-Dl0CwqlQ.js";
import { _ as Ke } from "./_plugin-vue_export-helper-DlAUqK2U.js";
import { s as je } from "./jupyterlab-C2EV-Dpr.js";
import "./xlsx-Ck9ILNdx.js";
import { __tla as __tla_4 } from "./index-D-jLGYR3.js";
import "./codemirror-C5EHd1r4.js";
import { __tla as __tla_5 } from "./pdfjs-4lX-eNFD.js";
let Ft;
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
    })(),
    (()=>{
        try {
            return __tla_3;
        } catch  {}
    })(),
    (()=>{
        try {
            return __tla_4;
        } catch  {}
    })(),
    (()=>{
        try {
            return __tla_5;
        } catch  {}
    })()
]).then(async ()=>{
    let Je, Ge, We, Xe, Ye, Ze, et, tt, nt, st, ot, lt, at, it, rt, ct, ut, pt, dt, vt, ht, mt, ft, gt, _t, yt, kt, wt, bt, Ct, xt, $t, qt, St, Rt, It;
    Je = D({
        __name: "AgentQuery",
        props: [
            "placeholder"
        ],
        emits: [
            "select-cell",
            "run-cell"
        ],
        setup (x, { emit: g }) {
            const _ = P("beakerSession"), s = k(""), r = x, m = P("session"), c = ($)=>{
                const f = m.notebook;
                if (!s.value.trim()) return;
                if (f.cells.length === 1) {
                    const h = f.cells[0];
                    h.cell_type === "code" && h.source === "" && h.execution_count === null && h.outputs.length === 0 && f.removeCell(0);
                }
                const i = m.addQueryCell(s.value);
                s.value = "", fe(()=>{
                    _.findNotebookCellById(i.id).execute();
                });
            };
            return ($, f)=>(a(), E(t(me), {
                    class: "agent-input-card"
                }, {
                    content: u(()=>[
                            n(t(pe), null, {
                                default: u(()=>[
                                        n(ve, {
                                            class: "agent-query-textarea",
                                            onKeydown: [
                                                L(T(c, [
                                                    "exact",
                                                    "prevent"
                                                ]), [
                                                    "enter"
                                                ]),
                                                f[0] || (f[0] = L(T((i)=>i.target.blur(), [
                                                    "prevent",
                                                    "stop"
                                                ]), [
                                                    "escape"
                                                ]))
                                            ],
                                            modelValue: s.value,
                                            "onUpdate:modelValue": f[1] || (f[1] = (i)=>s.value = i),
                                            placeholder: r.placeholder ?? "How can the agent help?"
                                        }, null, 8, [
                                            "onKeydown",
                                            "modelValue",
                                            "placeholder"
                                        ]),
                                        n(t(M), {
                                            icon: "pi pi-send",
                                            outlined: "",
                                            onClick: c
                                        })
                                    ]),
                                _: 1
                            })
                        ]),
                    _: 1
                }));
        }
    });
    Ge = {
        class: "cell-container"
    };
    We = {
        class: "flex-background"
    };
    Xe = {
        class: "chat-help-text-display query-answer-chat-override"
    };
    Ye = D({
        __name: "ChatPanel",
        props: [
            "cellMap"
        ],
        setup (x) {
            const g = P("session"), _ = x;
            return (s, r)=>(a(), v("div", Ge, [
                    p("div", We, [
                        ae(s.$slots, "notebook-background")
                    ]),
                    p("span", Xe, [
                        ae(s.$slots, "help-text")
                    ]),
                    (a(!0), v(G, null, le(t(g).notebook.cells, (m, c)=>(a(), E(ge(_.cellMap[m.cell_type]), {
                            cell: m,
                            key: c,
                            class: "beaker-chat-cell"
                        }, null, 8, [
                            "cell"
                        ]))), 128))
                ]));
        }
    });
    Ze = {
        class: "llm-query-cell"
    };
    et = {
        class: "llm-prompt-container llm-prompt-container-chat"
    };
    tt = {
        class: "prompt-input-container"
    };
    nt = {
        class: "prompt-controls"
    };
    st = [
        "data-cell-id"
    ];
    ot = {
        key: 0,
        class: "event-container"
    };
    lt = {
        class: "events"
    };
    at = {
        class: "white-space-nowrap",
        style: {
            display: "flex",
            "align-items": "center",
            "font-weight": "400",
            "font-family": "'Courier New', Courier, monospace",
            "font-size": "0.8rem",
            color: "var(--p-text-color-secondary)"
        }
    };
    it = {
        style: {
            display: "flex",
            "flex-direction": "column"
        }
    };
    rt = {
        class: "white-space-nowrap",
        style: {
            display: "flex",
            "align-items": "center",
            "font-weight": "400",
            "font-family": "'Courier New', Courier, monospace",
            "font-size": "0.8rem",
            color: "var(--p-text-color-secondary)"
        }
    };
    ct = {
        key: 1,
        class: "query-answer-chat-override"
    };
    ut = {
        key: 1,
        class: "input-request-chat-override"
    };
    pt = {
        class: "input-request-wrapper input-request-wrapper-chat"
    };
    dt = {
        modelClass: $e,
        icon: "pi pi-sparkles"
    };
    vt = D({
        ...dt,
        __name: "ChatQueryCell",
        props: [
            "index",
            "cell"
        ],
        setup (x, { expose: g }) {
            const _ = x, { cell: s, isEditing: r, promptEditorMinHeight: m, promptText: c, response: $, textarea: f, events: i, execute: h, enter: w, exit: N, clear: b, respond: q } = Te(_);
            let V;
            ((l)=>{
                l[l.NotExecuted = 0] = "NotExecuted", l[l.Running = 1] = "Running", l[l.Done = 2] = "Done";
            })(V || (V = {}));
            const S = P("activeQueryCell"), H = P("beakerSession"), Y = ye(), O = C(()=>{
                const l = "Thinking";
                if (i.value.length < 1) return l;
                const o = i.value[i.value.length - 1];
                if (o.type === "thought") return o.content.thought;
                {
                    let y = 2, e = i.value[i.value.length - y];
                    if (e === void 0) return l;
                    for(; e.type !== "thought" && i.value.length >= y;)y += 1, e = i.value[i.value.length - y];
                    if (e.type === "thought") {
                        if (e.content.thought === "Thinking..." && o.type === "response") return "Thinking...";
                        const d = {
                            user_question: "(awaiting user input)",
                            user_answer: "(answer received, thinking)",
                            code_cell: "(code is now running)"
                        };
                        return d[o.type] ? `${e.content.thought} ${d[o.type]}` : e.content.thought;
                    } else return l;
                }
            }), z = (l, o = !1)=>{
                const y = ce(s.value);
                if (o) {
                    S.value = y;
                    return;
                }
                ce(S.value)?.id === y?.id ? S.value = null : S.value = y;
            }, Q = C(()=>{
                const l = i.value.length;
                return _.cell.status === "busy" ? 1 : l === 0 ? 0 : J(i.value) ? 2 : 1;
            });
            se(Q, (l, o)=>{
                l === 1 && o !== 1 && z(null, !0);
            });
            const A = C(()=>_.cell?.events?.filter((l)=>[
                        "user_question",
                        "user_answer"
                    ].includes(l.type)).map((l)=>{
                    var o;
                    return l.type === "user_question" ? o = "query-answer-chat query-answer-chat-override" : o = "llm-prompt-container llm-prompt-container-chat llm-prompt-text llm-prompt-text-chat", [
                        l,
                        o
                    ];
                })), U = (l)=>l.status === "busy", Z = (l)=>{
                r.value || (m.value = l.target.clientHeight, r.value = !0);
            }, ee = C(()=>A.value.some(([l])=>l.type === "user_answer")), te = (l, o)=>l.type !== "user_answer" ? !1 : !A.value.slice(o + 1).some(([e])=>e.type === "user_answer");
            return g({
                execute: h,
                enter: w,
                exit: N,
                clear: b,
                cell: s,
                editor: f
            }), _e(()=>{
                H.cellRegistry[s.value.id] = Y.vnode;
            }), ke(()=>{
                delete H.cellRegistry[s.value.id];
            }), (l, o)=>{
                const y = W("focustrap");
                return a(), v("div", Ze, [
                    p("div", {
                        class: "query query-chat",
                        onDblclick: Z
                    }, [
                        p("div", et, [
                            B(p("div", tt, [
                                n(ve, {
                                    ref_key: "textarea",
                                    ref: f,
                                    class: "prompt-input",
                                    modelValue: t(c),
                                    "onUpdate:modelValue": o[0] || (o[0] = (e)=>re(c) ? c.value = e : null),
                                    style: ie({
                                        minHeight: `${t(m)}px`
                                    })
                                }, null, 8, [
                                    "modelValue",
                                    "style"
                                ]),
                                p("div", nt, [
                                    n(t(M), {
                                        label: "Submit",
                                        onClick: t(h)
                                    }, null, 8, [
                                        "onClick"
                                    ]),
                                    n(t(M), {
                                        label: "Cancel",
                                        onClick: o[1] || (o[1] = (e)=>{
                                            c.value = t(s).source, r.value = !1;
                                        })
                                    })
                                ])
                            ], 512), [
                                [
                                    de,
                                    t(r)
                                ]
                            ]),
                            p("div", {
                                style: ie({
                                    visibility: t(r) ? "hidden" : "visible",
                                    height: t(r) ? "0px" : "auto",
                                    padding: t(r) ? "0px" : "0.5rem"
                                }),
                                class: "llm-prompt-text llm-prompt-text-chat",
                                "data-cell-id": t(s).id
                            }, ne(t(s).source), 13, st)
                        ])
                    ], 32),
                    t(i).length > 0 || t(J)(t(i)) || U(t(s)) ? (a(), v("div", ot, [
                        p("div", lt, [
                            ee.value ? I("", !0) : (a(), v("div", {
                                key: 0,
                                class: F([
                                    "expand-thoughts-button",
                                    {
                                        expanded: t(S) === t(s)
                                    }
                                ]),
                                onClick: z
                            }, [
                                p("div", at, [
                                    p("i", {
                                        class: F([
                                            "pi pi-sparkles",
                                            {
                                                "animate-sparkles": Q.value === 1
                                            }
                                        ]),
                                        style: {
                                            color: "var(--p-yellow-500)",
                                            "font-size": "1.25rem",
                                            "margin-right": "0.6rem"
                                        }
                                    }, null, 2),
                                    X(" " + ne(O.value), 1)
                                ]),
                                n(t(M), {
                                    icon: t(S) === t(s) ? "pi pi-times" : "pi pi-search",
                                    text: "",
                                    rounded: "",
                                    style: {
                                        "background-color": "var(--p-surface-c)",
                                        color: "var(--p-text-color-secondary)",
                                        width: "2rem",
                                        height: "2rem",
                                        padding: "0"
                                    }
                                }, null, 8, [
                                    "icon"
                                ])
                            ], 2)),
                            (a(!0), v(G, null, le(A.value, ([e, d], K)=>(a(), v(G, {
                                    key: e.id
                                }, [
                                    p("div", it, [
                                        n(oe, {
                                            event: e,
                                            "parent-query-cell": t(s),
                                            class: F(d)
                                        }, null, 8, [
                                            "event",
                                            "parent-query-cell",
                                            "class"
                                        ])
                                    ]),
                                    te(e, K) ? (a(), v("div", {
                                        key: 0,
                                        class: F([
                                            "expand-thoughts-button",
                                            {
                                                expanded: t(S) === t(s)
                                            }
                                        ]),
                                        onClick: z
                                    }, [
                                        p("div", rt, [
                                            p("i", {
                                                class: F([
                                                    "pi pi-sparkles",
                                                    {
                                                        "animate-sparkles": Q.value === 1
                                                    }
                                                ]),
                                                style: {
                                                    color: "var(--p-yellow-500)",
                                                    "font-size": "1.25rem",
                                                    "margin-right": "0.6rem"
                                                }
                                            }, null, 2),
                                            X(" " + ne(O.value), 1)
                                        ]),
                                        n(t(M), {
                                            icon: t(S) === t(s) ? "pi pi-times" : "pi pi-search",
                                            text: "",
                                            rounded: "",
                                            style: {
                                                "background-color": "var(--p-surface-c)",
                                                color: "var(--p-text-color-secondary)",
                                                width: "2rem",
                                                height: "2rem",
                                                padding: "0"
                                            }
                                        }, null, 8, [
                                            "icon"
                                        ])
                                    ], 2)) : I("", !0)
                                ], 64))), 128)),
                            t(J)(t(i)) ? (a(), v("div", ct, [
                                n(oe, {
                                    event: t(s)?.events[t(s)?.events.length - 1],
                                    "parent-query-cell": t(s)
                                }, null, 8, [
                                    "event",
                                    "parent-query-cell"
                                ])
                            ])) : I("", !0)
                        ])
                    ])) : I("", !0),
                    t(s).status === "awaiting_input" ? B((a(), v("div", ut, [
                        p("div", pt, [
                            n(t(pe), null, {
                                default: u(()=>[
                                        n(t(we), null, {
                                            default: u(()=>o[6] || (o[6] = [
                                                    p("i", {
                                                        class: "pi pi-exclamation-triangle"
                                                    }, null, -1)
                                                ])),
                                            _: 1
                                        }),
                                        n(t(be), {
                                            placeholder: "Reply to the agent",
                                            onKeydown: [
                                                L(T(t(q), [
                                                    "exact",
                                                    "prevent"
                                                ]), [
                                                    "enter"
                                                ]),
                                                o[2] || (o[2] = L(T((e)=>e.target.blur(), [
                                                    "prevent",
                                                    "stop"
                                                ]), [
                                                    "escape"
                                                ])),
                                                o[3] || (o[3] = L(T(()=>{}, [
                                                    "ctrl",
                                                    "stop"
                                                ]), [
                                                    "enter"
                                                ])),
                                                o[4] || (o[4] = L(T(()=>{}, [
                                                    "shift",
                                                    "stop"
                                                ]), [
                                                    "enter"
                                                ]))
                                            ],
                                            autoFocus: "",
                                            modelValue: t($),
                                            "onUpdate:modelValue": o[5] || (o[5] = (e)=>re($) ? $.value = e : null)
                                        }, null, 8, [
                                            "onKeydown",
                                            "modelValue"
                                        ]),
                                        n(t(M), {
                                            icon: "pi pi-send",
                                            onClick: t(q)
                                        }, null, 8, [
                                            "onClick"
                                        ])
                                    ]),
                                _: 1
                            })
                        ])
                    ])), [
                        [
                            y
                        ]
                    ]) : I("", !0)
                ]);
            };
        }
    });
    ht = D({
        __name: "ChatQueryCellEvent",
        props: [
            "event",
            "parentQueryCell"
        ],
        setup (x) {
            const g = k(!1), _ = x, s = (r)=>{
                r.stopPropagation(), g.value = !g.value;
            };
            return (r, m)=>(a(), E(oe, {
                    event: _.event,
                    "parent-query-cell": _.parentQueryCell,
                    "code-styles": g.value ? "" : "code-cell-collapsed",
                    "should-hide-answered-questions": !0
                }, {
                    "code-cell-controls": u(()=>[
                            n(t(M), {
                                icon: g.value ? "pi pi-window-maximize" : "pi pi-window-minimize",
                                size: "small",
                                class: "code-cell-toggle-button",
                                onClick: T(s, [
                                    "stop"
                                ]),
                                title: g.value ? "Expand code cell" : "Shrink code cell"
                            }, null, 8, [
                                "icon",
                                "title"
                            ])
                        ]),
                    _: 1
                }, 8, [
                    "event",
                    "parent-query-cell",
                    "code-styles"
                ]));
        }
    });
    mt = {
        class: "thoughts-pane"
    };
    ft = {
        key: 0
    };
    gt = {
        key: 0
    };
    _t = {
        key: 1
    };
    yt = {
        key: 1,
        class: "thoughts-pane-content"
    };
    kt = {
        class: "pane-actions"
    };
    wt = {
        class: "events-scroll-container"
    };
    bt = {
        key: 0,
        class: "no-thoughts-message"
    };
    Ct = {
        key: 0,
        class: "progress-area"
    };
    xt = D({
        __name: "AgentActivityPane",
        props: {
            isChatEmpty: {
                type: Boolean
            }
        },
        emits: [
            "scrollToMessage"
        ],
        setup (x, { emit: g }) {
            const _ = g, s = x, r = P("activeQueryCell"), m = C(()=>!J(r.value?.events || [])), c = C(()=>r.value ? r.value?.events || [] : null), $ = ()=>{
                _("scrollToMessage");
            }, f = C(()=>c.value ? c.value.filter((h)=>![
                        "user_answer",
                        "response"
                    ].includes(h.type)).map((h, w, N)=>{
                    const b = w === N.length - 1;
                    return h.type === "user_question" && b && m.value ? {
                        ...h,
                        waitForUserInput: !0
                    } : h;
                }) : []), i = C(()=>{
                if (!c.value || m.value) return !1;
                const h = c.value.length === 1 && c.value[0].type === "response";
                return r.value?.status === "idle" && h;
            });
            return (h, w)=>{
                const N = W("tooltip"), b = W("autoscroll");
                return a(), v("div", mt, [
                    t(r) ? (a(), v("div", yt, [
                        p("div", kt, [
                            B(n(t(M), {
                                icon: "pi pi-arrow-circle-right",
                                text: "",
                                onClick: $
                            }, null, 512), [
                                [
                                    N,
                                    "Scroll to related user message.",
                                    void 0,
                                    {
                                        bottom: !0
                                    }
                                ]
                            ])
                        ]),
                        B((a(), v("div", wt, [
                            i.value ? (a(), v("div", bt, w[1] || (w[1] = [
                                p("em", null, "No agent activity from this query.", -1)
                            ]))) : (a(!0), v(G, {
                                key: 1
                            }, le(f.value, (q, V)=>(a(), E(ht, {
                                    key: `${V}-${t(r).id}`,
                                    event: q,
                                    "parent-query-cell": t(r)
                                }, null, 8, [
                                    "event",
                                    "parent-query-cell"
                                ]))), 128))
                        ])), [
                            [
                                b
                            ]
                        ]),
                        m.value ? (a(), v("div", Ct, [
                            n(t(Ce), {
                                mode: "indeterminate"
                            })
                        ])) : I("", !0)
                    ])) : (a(), v("div", ft, [
                        s.isChatEmpty ? (a(), v("span", gt, " Start a conversation to view Beaker's activity as you interact with it. ")) : (a(), v("em", _t, w[0] || (w[0] = [
                            X("Select "),
                            p("i", {
                                class: "pi pi-search magnifier-reference"
                            }, null, -1),
                            X(" agent activity from the conversation to view details.")
                        ])))
                    ]))
                ]);
            };
        }
    });
    $t = Ke(xt, [
        [
            "__scopeId",
            "data-v-26c0ca7c"
        ]
    ]);
    qt = {
        class: "chat-layout"
    };
    St = {
        class: "chat-container"
    };
    Rt = [
        "innerHTML"
    ];
    It = {
        key: 0,
        class: "spacer right"
    };
    Ft = D({
        __name: "ChatInterface",
        props: [
            "config",
            "connectionSettings",
            "sessionName",
            "sessionId",
            "defaultKernel",
            "renderers"
        ],
        setup (x) {
            const g = k(), _ = k(!1), { theme: s, toggleDarkMode: r } = P("theme"), m = P("beakerAppConfig");
            m.setPage("chat");
            const c = k(), $ = k(), f = k([]), i = k(null), h = k(), w = k(), N = k(!1), b = C(()=>g?.value?.beakerSession), q = k({});
            se(b, async ()=>{
                q.value = await Ue(A);
            });
            const V = C(()=>(b.value?.session?.notebook?.cells ?? []).length === 0), S = C(()=>{
                const e = b.value?.session?.notebook?.cells ?? [];
                if (e.length == 0) return !1;
                const d = e[e.length - 1];
                return d?.cell_type === "query" && d?.status === "awaiting_input";
            }), H = ()=>{
                i.value = null;
            }, Y = ()=>{
                const e = document.querySelector(`[data-cell-id="${i.value?.id}"]`);
                e && e.scrollIntoView({
                    behavior: "smooth"
                });
            };
            se(i, (e)=>{
                if (!c.value) return;
                const d = !!c.value.getSelectedPanelInfo();
                e ? c.value.selectPanel("agent-actions") : d && c.value.hidePanel();
            });
            const O = C(()=>{
                const e = [
                    {
                        type: "button",
                        command: ()=>{
                            window.confirm("This will reset your entire session, clearing the notebook and removing any updates to the environment. Proceed?") && b.value.session.reset();
                        },
                        icon: "refresh",
                        label: "Reset Session"
                    }
                ];
                if (!m?.config?.pages || Object.hasOwn(m.config.pages, "notebook")) {
                    const d = "/" + (m?.config?.pages?.notebook?.default ? "" : "notebook") + window.location.search;
                    e.push({
                        type: "link",
                        href: d,
                        component: Fe,
                        componentStyle: {
                            fill: "currentColor",
                            stroke: "currentColor",
                            height: "1rem",
                            width: "1rem"
                        },
                        label: "Navigate to notebook view"
                    });
                }
                return e.push({
                    type: "button",
                    icon: s.mode === "dark" ? "sun" : "moon",
                    command: r,
                    label: `Switch to ${s.mode === "dark" ? "light" : "dark"} mode.`
                }, {
                    type: "link",
                    href: "https://jataware.github.io/beaker-kernel",
                    label: "Beaker Documentation",
                    icon: "book",
                    rel: "noopener",
                    target: "_blank"
                }, {
                    type: "link",
                    href: "https://github.com/jataware/beaker-kernel",
                    label: "Check us out on Github",
                    icon: "github",
                    rel: "noopener",
                    target: "_blank"
                }), e;
            }), z = (e)=>{
                b.value?.session.loadNotebook(e);
            }, Q = new URLSearchParams(window.location.search), A = Q.has("session") ? Q.get("session") : "chat_dev_session", U = x, Z = [
                ...je.map((e)=>new Re(e)).map(Ie),
                qe,
                Se
            ], ee = {
                code: ze,
                markdown: Ve,
                query: vt,
                raw: Be
            }, te = k("connecting"), l = (e)=>{
                e.header.msg_type === "preview" ? $.value = e.content : e.header.msg_type === "debug_event" ? f.value.push({
                    type: e.content.event,
                    body: e.content.body,
                    timestamp: e.header.date
                }) : e.header.msg_type === "chat_history" && (h.value = e.content);
            }, o = (e)=>{
                te.value = e == "idle" ? "connected" : e;
            }, y = async ()=>{
                await b.value.session.sendBeakerMessage("reset_request", {});
            };
            return xe("activeQueryCell", i), (e, d)=>{
                const K = W("autoscroll");
                return a(), E(Me, {
                    title: e.$tmpl._("short_title", "Beaker Chat"),
                    ref_key: "beakerInterfaceRef",
                    ref: g,
                    "header-nav": O.value,
                    connectionSettings: U.config,
                    sessionId: t(A),
                    defaultKernel: "beaker_kernel",
                    renderers: Z,
                    onSessionStatusChanged: o,
                    onIopubMsg: l,
                    onOpenFile: z,
                    "style-overrides": [
                        "chat"
                    ]
                }, {
                    "left-panel": u(()=>[
                            n(ue, {
                                position: "left",
                                highlight: "line",
                                expanded: !1,
                                initialWidth: "25vi",
                                maximized: _.value
                            }, {
                                default: u(()=>[
                                        n(R, {
                                            label: "Context Info",
                                            icon: "pi pi-home"
                                        }, {
                                            default: u(()=>[
                                                    n(Le)
                                                ]),
                                            _: 1
                                        }),
                                        n(R, {
                                            id: "files",
                                            label: "Files",
                                            icon: "pi pi-folder",
                                            "no-overflow": "",
                                            lazy: !0
                                        }, {
                                            default: u(()=>[
                                                    n(Pe, {
                                                        ref: "filePanelRef",
                                                        onOpenFile: z,
                                                        onPreviewFile: d[0] || (d[0] = (j, he)=>{
                                                            w.value = {
                                                                url: j,
                                                                mimetype: he
                                                            }, N.value = !0, c.value.selectPanel("file-contents");
                                                        })
                                                    }, null, 512)
                                                ]),
                                            _: 1
                                        }),
                                        n(R, {
                                            icon: "pi pi-comments",
                                            label: "Chat History"
                                        }, {
                                            default: u(()=>[
                                                    n(t(De), {
                                                        "chat-history": h.value
                                                    }, null, 8, [
                                                        "chat-history"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        Object.keys(q.value).length > 0 ? (a(), E(R, {
                                            key: 0,
                                            id: "integrations",
                                            label: "Integrations",
                                            icon: "pi pi-database"
                                        }, {
                                            default: u(()=>[
                                                    n(Oe, {
                                                        modelValue: q.value,
                                                        "onUpdate:modelValue": d[1] || (d[1] = (j)=>q.value = j)
                                                    }, null, 8, [
                                                        "modelValue"
                                                    ])
                                                ]),
                                            _: 1
                                        })) : I("", !0),
                                        U.config.config_type !== "server" ? (a(), E(R, {
                                            key: 1,
                                            id: "config",
                                            label: `${e.$tmpl._("short_title", "Beaker")} Config`,
                                            icon: "pi pi-cog",
                                            lazy: !0,
                                            position: "bottom"
                                        }, {
                                            default: u(()=>[
                                                    n(Ne, {
                                                        ref: "configPanelRef",
                                                        onRestartSession: y
                                                    }, null, 512)
                                                ]),
                                            _: 1
                                        }, 8, [
                                            "label"
                                        ])) : I("", !0)
                                    ]),
                                _: 1
                            }, 8, [
                                "maximized"
                            ])
                        ]),
                    "right-panel": u(()=>[
                            n(ue, {
                                ref_key: "rightSideMenuRef",
                                ref: c,
                                position: "right",
                                highlight: "line",
                                expanded: !0,
                                "initial-width": "35vw",
                                onPanelHide: H
                            }, {
                                default: u(()=>[
                                        n(R, {
                                            label: "Agent Activity",
                                            id: "agent-actions",
                                            icon: "pi pi-lightbulb",
                                            position: "top",
                                            selected: !0
                                        }, {
                                            default: u(()=>[
                                                    n($t, {
                                                        onScrollToMessage: Y,
                                                        "is-chat-empty": V.value
                                                    }, null, 8, [
                                                        "is-chat-empty"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        n(R, {
                                            label: "Preview",
                                            icon: "pi pi-eye",
                                            "no-overflow": ""
                                        }, {
                                            default: u(()=>[
                                                    n(Qe, {
                                                        previewData: $.value
                                                    }, null, 8, [
                                                        "previewData"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        n(R, {
                                            id: "file-contents",
                                            label: "File Contents",
                                            icon: "pi pi-file beaker-zoom",
                                            "no-overflow": ""
                                        }, {
                                            default: u(()=>[
                                                    n(He, {
                                                        url: w.value?.url,
                                                        mimetype: w.value?.mimetype
                                                    }, null, 8, [
                                                        "url",
                                                        "mimetype"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        n(R, {
                                            id: "media",
                                            label: "Graphs and Images",
                                            icon: "pi pi-chart-bar",
                                            "no-overflow": ""
                                        }, {
                                            default: u(()=>[
                                                    n(Ae)
                                                ]),
                                            _: 1
                                        }),
                                        n(R, {
                                            id: "kernel-logs",
                                            label: "Logs",
                                            icon: "pi pi-list",
                                            position: "bottom"
                                        }, {
                                            default: u(()=>[
                                                    B(n(Ee, {
                                                        entries: f.value,
                                                        onClearLogs: d[2] || (d[2] = (j)=>f.value.splice(0, f.value.length))
                                                    }, null, 8, [
                                                        "entries"
                                                    ]), [
                                                        [
                                                            K
                                                        ]
                                                    ])
                                                ]),
                                            _: 1
                                        })
                                    ]),
                                _: 1
                            }, 512)
                        ]),
                    default: u(()=>[
                            p("div", qt, [
                                p("div", St, [
                                    B((a(), E(Ye, {
                                        "cell-map": ee
                                    }, {
                                        "help-text": u(()=>[
                                                p("div", {
                                                    innerHTML: e.$tmpl._("chat_welcome_html", `
                                <p>Hi! I'm your Beaker Agent and I can help you do programming and software engineering tasks.</p>
                                <p>Feel free to ask me about whatever the context specializes in..</p>
                                <p>
                                    On top of answering questions, I can actually run code in a python environment, and evaluate the results.
                                    This lets me do some pretty awesome things like: web scraping, or plotting and exploring data.
                                    Just shoot me a message when you're ready to get started.
                                </p>
                            `)
                                                }, null, 8, Rt)
                                            ]),
                                        "notebook-background": u(()=>d[3] || (d[3] = [
                                                p("div", {
                                                    class: "welcome-placeholder"
                                                }, null, -1)
                                            ])),
                                        _: 1
                                    })), [
                                        [
                                            K
                                        ]
                                    ]),
                                    B(n(Je, {
                                        class: "agent-query-container agent-query-container-chat",
                                        placeholder: e.$tmpl._("agent_query_prompt", "Message to the agent")
                                    }, null, 8, [
                                        "placeholder"
                                    ]), [
                                        [
                                            de,
                                            !S.value
                                        ]
                                    ])
                                ]),
                                _.value ? I("", !0) : (a(), v("div", It))
                            ])
                        ]),
                    _: 1
                }, 8, [
                    "title",
                    "header-nav",
                    "connectionSettings",
                    "sessionId"
                ]);
            };
        }
    });
});
export { Ft as default, __tla };
