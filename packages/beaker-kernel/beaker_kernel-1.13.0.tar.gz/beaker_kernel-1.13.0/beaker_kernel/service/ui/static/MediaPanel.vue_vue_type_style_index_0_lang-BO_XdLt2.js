import { d as L, r as S, i as j, f as y, J as N, y as i, o as l, E as _, I as h, K as $, $ as k, G as m, B as e, u as v, H as O, M as H, z as D, A as F, a3 as V, a4 as K, j as P, S as A, a5 as W, a6 as G, Y as T, a7 as R, Q as q, a0 as U, a8 as J, L as B, a9 as Q } from "./primevue-1TEWPnDt.js";
import { h as Y, __tla as __tla_0 } from "./DebugPanel.vue_vue_type_style_index_0_lang-PW_f_WLw.js";
let Ee, Le, ze;
let __tla = Promise.all([
    (()=>{
        try {
            return __tla_0;
        } catch  {}
    })()
]).then(async ()=>{
    let X, Z, ee, te, se, oe, ae, le, ne, re, ie, de, ue, ce, pe, me, ve, ge, ye, _e, he, fe, be, ke, xe, we, $e, He, Ce, Me;
    X = {
        class: "info-panel-container"
    };
    Z = {
        style: {
            cursor: "help",
            "border-bottom": "1px dotted var(--p-text-color-secondary)"
        }
    };
    Le = L({
        __name: "InfoPanel",
        setup (C) {
            S(!0);
            const x = S({
                0: !0,
                1: !0,
                2: !0,
                3: !0
            }), s = j("beakerSession"), c = y(()=>{
                const d = s?.activeContext, a = s?.session.kernelInfo;
                return {
                    ...d,
                    kernelInfo: a
                };
            }), p = y(()=>{
                const d = c.value;
                if (!d) return [];
                const a = [
                    {
                        key: "0",
                        label: "Kernel",
                        icon: "pi pi-fw pi-cog",
                        expanded: !0,
                        children: [
                            {
                                key: "0-1",
                                label: `${d?.info?.subkernel} (${d?.info?.language})`
                            }
                        ]
                    }
                ];
                return a.push({
                    key: "3",
                    label: "Tools",
                    icon: "pi pi-fw pi-wrench",
                    expanded: !0,
                    children: Object.keys(d?.info?.agent?.tools || {}).map((n, o)=>({
                            key: `3-${o}`,
                            label: n.replace("PyPackageAgent.", ""),
                            data: d.info.agent.tools[n],
                            type: "tool"
                        }))
                }), a;
            });
            return (d, a)=>{
                const n = N("tooltip");
                return l(), i("div", X, [
                    _(v(O), {
                        value: p.value,
                        loading: !p.value,
                        expandedKeys: x.value,
                        "onUpdate:expandedKeys": a[1] || (a[1] = (o)=>x.value = o)
                    }, {
                        loadingicon: h(()=>a[2] || (a[2] = [
                                e("div", {
                                    class: "loading-area"
                                }, " No Context Loaded. ", -1)
                            ])),
                        action: h((o)=>[
                                $((l(), i("div", {
                                    onMousedown: a[0] || (a[0] = (u)=>{
                                        u.detail > 1 && u.preventDefault();
                                    }),
                                    style: {
                                        cursor: "pointer",
                                        "border-bottom": "1px dotted var(--p-text-color-secondary)"
                                    }
                                }, [
                                    k(m(o.node.label), 1)
                                ], 32)), [
                                    [
                                        n,
                                        {
                                            value: `${o.node.data}`,
                                            pt: {
                                                text: {
                                                    style: {
                                                        width: "20rem"
                                                    }
                                                },
                                                root: {
                                                    style: {
                                                        marginLeft: "1rem"
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                ])
                            ]),
                        tool: h((o)=>[
                                $((l(), i("span", Z, [
                                    k(m(o.node.label), 1)
                                ])), [
                                    [
                                        n,
                                        {
                                            value: `${o.node.data}`,
                                            pt: {
                                                text: {
                                                    style: {
                                                        width: "20rem"
                                                    }
                                                },
                                                root: {
                                                    style: {
                                                        marginLeft: "1rem"
                                                    }
                                                }
                                            }
                                        }
                                    ]
                                ])
                            ]),
                        _: 1
                    }, 8, [
                        "value",
                        "loading",
                        "expandedKeys"
                    ])
                ]);
            };
        }
    });
    ee = {
        class: "chat-history-message"
    };
    te = {
        class: "chat-history-message-title"
    };
    se = {
        style: {
            "font-weight": "500"
        }
    };
    oe = {
        key: 0,
        class: "chat-history-message-tool-use pi pi-hammer"
    };
    ae = {
        class: "chat-history-message-title-token-count"
    };
    le = {
        key: 0,
        class: "message-text monospace"
    };
    ne = {
        key: 1,
        class: "toolcall-info"
    };
    re = {
        class: "tool-call-title"
    };
    ie = {
        class: "monospace"
    };
    de = L({
        __name: "ChatHistoryMessage",
        props: [
            "record",
            "idx",
            "tool-call-message"
        ],
        setup (C) {
            const x = C, s = S(!0), c = y(()=>x.record?.message), p = (d)=>d && d.replace(/(?<edge>[-_]|\b)(?<letter>.)/g, (a, n, o, u, f, w)=>o.toUpperCase());
            return (d, a)=>{
                const n = N("tooltip");
                return l(), i("div", ee, [
                    _(v(R), {
                        class: "chat-history-message-panel",
                        toggleable: !0,
                        style: T({
                            collapsed: s.value
                        }),
                        onToggle: a[2] || (a[2] = (o)=>s.value = !s.value),
                        pt: {
                            contentContainer: ({ state: o })=>(o.d_collapsed = !1, s.value ? "collapsed" : void 0)
                        }
                    }, {
                        header: h(()=>[
                                e("div", {
                                    class: "chat-history-message-header-container",
                                    onClick: a[0] || (a[0] = (o)=>s.value = !s.value)
                                }, [
                                    e("div", te, [
                                        e("span", se, m(p(c.value?.type)) + "Message ", 1),
                                        c.value?.type.toLowerCase() === "ai" && c.value?.tool_calls ? $((l(), i("span", oe, null, 512)), [
                                            [
                                                n,
                                                `Tool${c.value.tool_calls.length > 1 ? "s" : ""} called: ` + c.value.tool_calls.map((o)=>`'${o.name}'`).join(", ")
                                            ]
                                        ]) : H("", !0)
                                    ]),
                                    e("span", ae, m((C.record?.token_count / 1e3).toFixed(2)) + "k tokens ", 1)
                                ])
                            ]),
                        togglericon: h(()=>[
                                (l(), P(A(s.value ? v(W) : v(G))))
                            ]),
                        default: h(()=>[
                                e("div", null, [
                                    c.value.text.trim() ? (l(), i("div", le, m(c.value?.text.trim()), 1)) : H("", !0),
                                    c.value?.type === "ai" && c.value?.tool_calls?.length > 0 ? (l(), i("div", ne, [
                                        (l(!0), i(D, null, F(c.value?.tool_calls, (o)=>(l(), i("div", {
                                                key: o.id
                                            }, [
                                                e("div", re, [
                                                    a[3] || (a[3] = k(" Tool:   ")),
                                                    e("span", ie, m(o.name), 1)
                                                ]),
                                                a[4] || (a[4] = e("div", null, " Arguments: ", -1)),
                                                _(v(V), {
                                                    showGridlines: "",
                                                    stripedRows: "",
                                                    class: "chat-history-datatable",
                                                    value: Object.entries(o?.args).map(([u, f])=>({
                                                            key: u,
                                                            value: f
                                                        }))
                                                }, {
                                                    default: h(()=>[
                                                            _(v(K), {
                                                                field: "key"
                                                            }),
                                                            _(v(K), {
                                                                field: "value"
                                                            })
                                                        ]),
                                                    _: 2
                                                }, 1032, [
                                                    "value"
                                                ])
                                            ]))), 128))
                                    ])) : H("", !0)
                                ]),
                                s.value ? (l(), i("div", {
                                    key: 0,
                                    class: "expand",
                                    onClick: a[1] || (a[1] = (o)=>s.value = !1)
                                }, "Click to expand")) : H("", !0)
                            ]),
                        _: 1
                    }, 8, [
                        "style",
                        "pt"
                    ])
                ]);
            };
        }
    });
    ue = {
        class: "chat-history-panel"
    };
    ce = {
        class: "chat-history-model"
    };
    pe = {
        class: "model-info"
    };
    me = {
        class: "model-specs",
        style: {
            display: "grid",
            "grid-template-columns": "max-content auto",
            "column-gap": "1rem",
            "row-gap": "0.5rem"
        }
    };
    ve = {
        key: 0,
        class: "model-spec-label"
    };
    ge = {
        key: 1
    };
    ye = {
        class: "context-window-usage"
    };
    _e = {
        class: "progress-bar-container"
    };
    he = {
        class: "progress-bar"
    };
    fe = {
        style: {
            width: "100%",
            position: "absolute",
            top: "1%",
            "text-align": "center"
        }
    };
    be = {
        class: "progress-bar-map"
    };
    ke = {
        class: "progress-bar-map-row overhead"
    };
    xe = {
        class: "progress-bar-map-row summary"
    };
    we = {
        class: "progress-bar-map-row message"
    };
    $e = {
        class: "progress-bar-map-row total"
    };
    He = {
        class: "chat-history-records"
    };
    ze = L({
        __name: "ChatHistoryPanel",
        props: {
            chatHistory: {}
        },
        emits: [],
        setup (C, { emit: x }) {
            const s = C, c = y(()=>{
                const r = s.chatHistory?.model?.context_window, t = s.chatHistory?.token_estimate;
                if (r && t) {
                    const g = t / r;
                    return Math.round(g * 1e3) / 10;
                } else return null;
            }), p = y(()=>s.chatHistory?.model?.context_window), d = y(()=>Math.round(s.chatHistory?.overhead_token_count / p.value * 1e3) / 10), a = y(()=>Math.round(s.chatHistory?.message_token_count / p.value * 1e3) / 10), n = y(()=>Math.round(s.chatHistory?.summary_token_count / p.value * 1e3) / 10), o = y({
                get () {
                    return Math.round(s.chatHistory?.summarization_threshold / p.value * 1e3) / 10;
                },
                set (r) {
                    console.log(r);
                }
            }), u = y(()=>s.chatHistory?.overhead_token_count + s.chatHistory?.message_token_count + s.chatHistory?.summary_token_count), f = y(()=>{
                const r = u.value, t = M(b(r)), g = M(b(p.value));
                return `${c.value?.toLocaleString()}% (~ ${t} / ${g})`;
            }), w = (r)=>s.chatHistory?.records?.map((t)=>t.message).find((t)=>t.type === "ai" && t.tool_calls?.map((g)=>g.id).includes(r)), z = (r)=>{
                if (r?.message?.tool_call_id) return w(r.message.tool_call_id);
            }, b = (r)=>Math.round(r / 500) * .5, M = (r)=>{
                let t = "k", g = r.toLocaleString();
                return r >= 1e3 && (t = "M", g = (r / 1e3).toFixed(2)), `${g.toLocaleString()}${t}`;
            };
            return (r, t)=>{
                const g = N("tooltip");
                return l(), i("div", ue, [
                    e("div", ce, [
                        e("div", pe, [
                            t[2] || (t[2] = e("h4", null, "Current model", -1)),
                            e("div", me, [
                                t[0] || (t[0] = e("div", {
                                    class: "model-spec-label"
                                }, "Model Provider:", -1)),
                                e("div", null, m(s.chatHistory?.model?.provider), 1),
                                t[1] || (t[1] = e("div", {
                                    class: "model-spec-label"
                                }, "Model Name:", -1)),
                                e("div", null, m(s.chatHistory?.model?.model_name), 1),
                                s.chatHistory?.model?.context_window ? (l(), i("div", ve, "Context window:")) : H("", !0),
                                s.chatHistory?.model?.context_window ? (l(), i("div", ge, m(s.chatHistory?.model?.context_window.toLocaleString()) + " tokens", 1)) : H("", !0)
                            ])
                        ])
                    ]),
                    e("div", ye, [
                        t[11] || (t[11] = e("h4", null, "Context window usage", -1)),
                        e("div", _e, [
                            e("div", he, [
                                e("span", {
                                    class: "progress-bar-usage overhead",
                                    style: T({
                                        width: `${d.value}%`
                                    })
                                }, null, 4),
                                e("span", {
                                    class: "progress-bar-usage summary",
                                    style: T({
                                        width: `${n.value}%`
                                    })
                                }, null, 4),
                                e("span", {
                                    class: "progress-bar-usage message",
                                    style: T({
                                        width: `${a.value}%`
                                    })
                                }, null, 4)
                            ]),
                            e("div", {
                                style: T([
                                    {
                                        width: "2px",
                                        height: "100%",
                                        "background-color": "var(--p-orange-600)",
                                        position: "absolute",
                                        top: "0"
                                    },
                                    {
                                        left: `${o.value}%`
                                    }
                                ])
                            }, null, 4),
                            e("div", {
                                style: T([
                                    {
                                        width: "2px",
                                        height: "100%",
                                        "background-color": "var(--p-red-600)",
                                        position: "absolute",
                                        top: "0"
                                    },
                                    {
                                        left: "85%"
                                    }
                                ])
                            }),
                            e("div", fe, m(f.value), 1)
                        ]),
                        e("div", be, [
                            $((l(), i("div", ke, [
                                t[3] || (t[3] = e("span", {
                                    class: "progress-bar-map-circle overhead"
                                }, null, -1)),
                                t[4] || (t[4] = k(" Estimated token overhead: ")),
                                e("span", null, m(M(b(r.chatHistory?.overhead_token_count))), 1)
                            ])), [
                                [
                                    g,
                                    "Tokens used in tool definitions, subkernel state, etc. (estimated)"
                                ]
                            ]),
                            $((l(), i("div", xe, [
                                t[5] || (t[5] = e("span", {
                                    class: "progress-bar-map-circle summary"
                                }, null, -1)),
                                t[6] || (t[6] = k(" Estimated summarized token usage: ")),
                                e("span", null, m(M(b(r.chatHistory?.summary_token_count))), 1)
                            ])), [
                                [
                                    g,
                                    "Token used by summaries. (estimated)"
                                ]
                            ]),
                            $((l(), i("div", we, [
                                t[7] || (t[7] = e("span", {
                                    class: "progress-bar-map-circle message"
                                }, null, -1)),
                                t[8] || (t[8] = k(" Estimated message token usage: ")),
                                e("span", null, m(M(b(r.chatHistory?.message_token_count))), 1)
                            ])), [
                                [
                                    g,
                                    "Tokens used by all unsummarized messages. (estimated)"
                                ]
                            ]),
                            $((l(), i("div", $e, [
                                t[9] || (t[9] = e("span", {
                                    class: "progress-bar-map-circle total"
                                }, null, -1)),
                                t[10] || (t[10] = k(" Estimated total token usage: ")),
                                e("span", null, m(M(b(u.value))), 1)
                            ])), [
                                [
                                    g,
                                    "Total tokens of current conversational history, favoring summaries. (estimated)"
                                ]
                            ])
                        ])
                    ]),
                    t[12] || (t[12] = e("h4", null, "Messages", -1)),
                    e("div", He, [
                        (l(!0), i(D, null, F(s.chatHistory?.records, (E, I)=>(l(), P(de, {
                                key: E.uuid,
                                record: E,
                                idx: I,
                                "tool-call-message": z(E)
                            }, null, 8, [
                                "record",
                                "idx",
                                "tool-call-message"
                            ]))), 128))
                    ])
                ]);
            };
        }
    });
    Ce = {
        class: "media-focus"
    };
    Me = {
        class: "media-mime-bundle"
    };
    Ee = L({
        __name: "MediaPanel",
        setup (C) {
            const x = j("session"), s = S(0), c = [
                "image/png",
                "text/html"
            ], p = y(()=>{
                const a = [], n = x.notebook.cells, o = (u)=>{
                    const f = [];
                    if (u.cell_type === "query") for (const w of u?.children ?? [])f.push(...o(w));
                    else if (u.cell_type === "code") for (const w of u?.outputs ?? []){
                        const z = w?.data ?? {};
                        c.forEach((b)=>{
                            z[b] && f.push(w);
                        });
                    }
                    return f;
                };
                for (const u of n)a.push(...o(u));
                return a;
            }), d = y(()=>p?.value?.[s?.value]?.data);
            return (a, n)=>(l(), i("div", Ce, [
                    _(v(Q), {
                        class: "media-toolbar"
                    }, {
                        start: h(()=>[
                                _(v(B), {
                                    icon: "pi pi-arrow-left",
                                    class: "media-toolbar-button",
                                    onClick: n[0] || (n[0] = ()=>{
                                        s.value -= Math.min(s.value, 1);
                                    })
                                }),
                                _(v(B), {
                                    icon: "pi pi-arrow-right",
                                    class: "media-toolbar-button",
                                    onClick: n[1] || (n[1] = ()=>{
                                        s.value += s.value >= p.value.length - 1 ? 0 : 1;
                                    })
                                })
                            ]),
                        end: h(()=>[
                                _(v(q), null, {
                                    default: h(()=>[
                                            _(v(U), {
                                                class: "media-dropdown-icon"
                                            }, {
                                                default: h(()=>n[3] || (n[3] = [
                                                        e("i", {
                                                            class: "pi pi-chart-bar"
                                                        }, null, -1)
                                                    ])),
                                                _: 1
                                            }),
                                            _(v(J), {
                                                modelValue: s.value,
                                                "onUpdate:modelValue": n[2] || (n[2] = (o)=>s.value = o),
                                                options: Array.from(p.value.map((o, u)=>({
                                                        label: u + 1,
                                                        value: u
                                                    }))),
                                                "option-label": "label",
                                                "option-value": "value"
                                            }, null, 8, [
                                                "modelValue",
                                                "options"
                                            ]),
                                            _(v(U), null, {
                                                default: h(()=>[
                                                        k("/ " + m(p.value.length ?? 0), 1)
                                                    ]),
                                                _: 1
                                            })
                                        ]),
                                    _: 1
                                })
                            ]),
                        _: 1
                    }),
                    e("div", Me, [
                        d.value !== void 0 ? (l(), P(Y, {
                            key: 0,
                            "mime-bundle": d.value,
                            class: "code-cell-output"
                        }, null, 8, [
                            "mime-bundle"
                        ])) : H("", !0)
                    ])
                ]));
        }
    });
});
export { Ee as _, Le as a, ze as b, __tla };
