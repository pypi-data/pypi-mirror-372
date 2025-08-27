import { j as fe, S as W, a as ye, L as be, b as _e, w as ke, _ as he, c as ie, d as T, e as we, f as xe, __tla as __tla_0 } from "./DebugPanel.vue_vue_type_style_index_0_lang-PW_f_WLw.js";
import { B as $e, _ as Ce, a as Se, b as Ae, S as Me, c as Re, __tla as __tla_1 } from "./BeakerQueryCell.vue_vue_type_style_index_0_lang-Dt4dB8m3.js";
import { d as q, i as F, r as s, f as N, g as ce, y as h, o as p, E as l, B as n, u, ai as Ne, G as x, $ as X, L as U, I as r, j as M, M as L, ad as oe, z as re, A as ue, a7 as pe, _ as J, J as Y, H as Ie, K as O, w as De, a3 as se, a4 as K, a1 as Le, O as Oe, n as de, N as Ee } from "./primevue-1TEWPnDt.js";
import { _ as Pe, a as ze, b as je, c as Be, __tla as __tla_2 } from "./BeakerRawCell.vue_vue_type_style_index_0_lang-DHQ28atJ.js";
import { s as Ve } from "./jupyterlab-C2EV-Dpr.js";
import "./xlsx-Ck9ILNdx.js";
import { __tla as __tla_3 } from "./index-D-jLGYR3.js";
import "./_plugin-vue_export-helper-DlAUqK2U.js";
import "./codemirror-C5EHd1r4.js";
let Bt;
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
    })()
]).then(async ()=>{
    let Te, Ke, Fe, He, Je, Ue, qe, Ge, Qe, We, Xe, Ye, Ze, et, tt, ot, st, lt, nt, at, it, dt, ct, rt, ut, pt, vt, mt, gt, ft, yt, bt, _t, kt, ht, wt, xt, $t, Ct, St, At, Mt, Rt;
    Te = {
        class: "execute-action-container"
    };
    Ke = {
        class: "docs"
    };
    Fe = {
        key: 0
    };
    He = {
        style: {
            "font-weight": "bold"
        }
    };
    Je = {
        key: 1
    };
    Ue = {
        class: "code"
    };
    qe = q({
        __name: "BeakerExecuteAction",
        props: [
            "actions",
            "rawMessages",
            "selectedAction"
        ],
        emits: [
            "clearSelection"
        ],
        setup (f, { expose: I, emit: $ }) {
            const i = f, _ = $, b = F("session"), w = F("beakerSession"), t = F("show_toast"), a = s(), c = s(`{
}`), o = s([]), v = s(), C = s(), E = s(1), S = s(void 0), B = s();
            s();
            const P = s(), V = ()=>{
                S.value = `beaker-custom-${a.value}-${E.value}`, E.value += 1;
                const g = b.executeAction(a.value, JSON.parse(c.value), S.value);
                g.onResponse = async (m)=>{
                    B.value = m;
                }, g.onReply = async (m)=>{
                    P.value = m;
                }, g.done.then(()=>{
                    t({
                        title: "Success",
                        detail: "Message processed."
                    });
                });
            }, D = N(()=>i.actions !== void 0 ? i.actions : w.activeContext?.info.actions), H = N(()=>Object.keys(D.value)), G = (g)=>{
                o.value = g.query ? H.value.filter((m)=>m.includes(g.query)) : H.value;
            }, le = (g)=>{
                Q(g.value);
            }, Q = (g)=>{
                C.value = g;
                const m = D.value[g];
                m !== void 0 && (a.value !== g && (a.value = g), c.value = m.default_payload, v.value = m.docs);
            }, Z = N(()=>S.value ? i.rawMessages.filter((g)=>g.body.header?.msg_id === S.value || g.body.parent_header?.msg_id === S.value) : []);
            return ce(()=>i.selectedAction, async (g)=>{
                g !== void 0 && (Q(g), _("clearSelection"));
            }), I({
                selectAction: Q
            }), (g, m)=>(p(), h("div", Te, [
                    l(u(Ne), {
                        class: "action-name-input",
                        placeholder: "Action Name",
                        dropdown: "",
                        modelValue: a.value,
                        "onUpdate:modelValue": m[0] || (m[0] = (A)=>a.value = A),
                        suggestions: o.value,
                        onComplete: G,
                        onItemSelect: le,
                        dropdownClass: "ac-button"
                    }, null, 8, [
                        "modelValue",
                        "suggestions"
                    ]),
                    n("div", Ke, [
                        C.value ? (p(), h("div", Fe, [
                            n("span", He, x(C.value), 1),
                            m[2] || (m[2] = n("br", null, null, -1)),
                            m[3] || (m[3] = n("br", null, null, -1)),
                            n("span", null, x(v.value), 1)
                        ])) : (p(), h("div", Je, " Select an action to see the docstring... "))
                    ]),
                    n("div", Ue, [
                        m[4] || (m[4] = X(" Action Payload ")),
                        l(fe, {
                            "tab-size": 2,
                            language: "javascript",
                            modelValue: c.value,
                            "onUpdate:modelValue": m[1] || (m[1] = (A)=>c.value = A)
                        }, null, 8, [
                            "modelValue"
                        ])
                    ]),
                    l(u(U), {
                        icon: "pi pi-bolt",
                        size: "small",
                        onClick: V,
                        label: "Send",
                        iconPos: "right"
                    }),
                    m[5] || (m[5] = n("h3", null, "Results:", -1)),
                    l(u(oe), {
                        legend: "Reply",
                        toggleable: !0
                    }, {
                        default: r(()=>[
                                P.value ? (p(), M(u(W), {
                                    key: 0,
                                    data: P.value
                                }, null, 8, [
                                    "data"
                                ])) : L("", !0)
                            ]),
                        _: 1
                    }),
                    l(u(oe), {
                        legend: "Response (Optional)",
                        toggleable: !0
                    }, {
                        default: r(()=>[
                                B.value ? (p(), M(u(W), {
                                    key: 0,
                                    data: B.value
                                }, null, 8, [
                                    "data"
                                ])) : L("", !0)
                            ]),
                        _: 1
                    }),
                    l(u(oe), {
                        legend: "Raw Messages (Debug)",
                        toggleable: !0,
                        collapsed: !0
                    }, {
                        default: r(()=>[
                                (p(!0), h(re, null, ue(Z.value, (A, ee)=>(p(), M(u(pe), {
                                        class: J([
                                            "log-panel",
                                            {
                                                odd: ee % 2 !== 0
                                            }
                                        ]),
                                        "data-index": A.timestamp,
                                        key: `${A.type}-${A.timestamp}`,
                                        header: A.type
                                    }, {
                                        default: r(()=>[
                                                l(u(W), {
                                                    data: A.body,
                                                    deep: 2,
                                                    showLength: "",
                                                    showIcon: "",
                                                    showDoubleQuotes: !0,
                                                    showLineNumber: !1
                                                }, null, 8, [
                                                    "data"
                                                ])
                                            ]),
                                        _: 2
                                    }, 1032, [
                                        "class",
                                        "data-index",
                                        "header"
                                    ]))), 128))
                            ]),
                        _: 1
                    })
                ]));
        }
    });
    Ge = [
        "onDblclick"
    ];
    Qe = {
        style: {
            cursor: "help",
            "border-bottom": "1px dotted var(--p-text-color-secondary)"
        }
    };
    We = q({
        __name: "ContextPanel",
        emits: [
            "action-selected"
        ],
        setup (f, { emit: I }) {
            s(!0);
            const $ = s({
                0: !0,
                1: !0,
                2: !0,
                3: !0
            }), i = I, _ = F("beakerSession"), b = N(()=>{
                const t = _?.activeContext?.info;
                if (!t) return [];
                const a = [
                    {
                        key: "0",
                        label: "Kernel",
                        icon: "pi pi-fw pi-cog",
                        expanded: !0,
                        children: [
                            {
                                key: "0-1",
                                label: `${t.subkernel} (${t.language})`
                            }
                        ]
                    },
                    {
                        key: "1",
                        label: "Actions",
                        icon: "pi pi-fw pi-send",
                        expanded: !0,
                        children: Object.keys(t.actions).map((c, o)=>({
                                dblClick: (v)=>{},
                                key: `1-${o}`,
                                label: c,
                                data: t.actions[c].docs + `

Example payload:
` + t.actions[c].default_payload,
                                type: "action"
                            }))
                    }
                ];
                return t.procedures.length && a.push({
                    key: "2",
                    label: "Procedures",
                    icon: "pi pi-fw pi-tablet",
                    expanded: !0,
                    children: t.procedures.map((c, o)=>({
                            key: `2-${o}`,
                            label: c
                        }))
                }), a.push({
                    key: "3",
                    label: "Tools",
                    icon: "pi pi-fw pi-wrench",
                    expanded: !0,
                    children: Object.keys(t?.agent?.tools || {}).map((c, o)=>({
                            key: `3-${o}`,
                            label: c.replace("PyPackageAgent.", ""),
                            data: t.agent.tools[c],
                            type: "tool"
                        }))
                }), Object.keys(t.custom_messages).length && a.push({
                    key: "4",
                    label: "Custom Messages",
                    icon: "pi pi-fw pi-comment",
                    expanded: !1,
                    children: Object.keys(t.custom_messages).map((c, o)=>({
                            key: `4-${o}`,
                            label: c,
                            data: t.custom_messages[c].docs + `

Example payload:
` + t.custom_messages[c].default_payload,
                            type: "tool"
                        }))
                }), a;
            }), w = (t)=>{
                i("action-selected", t);
            };
            return (t, a)=>{
                const c = Y("tooltip");
                return p(), M(u(Ie), {
                    value: b.value,
                    loading: !b.value,
                    expandedKeys: $.value,
                    "onUpdate:expandedKeys": a[1] || (a[1] = (o)=>$.value = o)
                }, {
                    loadingicon: r(()=>a[2] || (a[2] = [
                            n("div", {
                                class: "loading-area"
                            }, " No Context Loaded. ", -1)
                        ])),
                    action: r((o)=>[
                            O((p(), h("div", {
                                onMousedown: a[0] || (a[0] = (v)=>{
                                    v.detail > 1 && v.preventDefault();
                                }),
                                onDblclick: De((v)=>w(o.node.label), [
                                    "stop",
                                    "prevent"
                                ]),
                                style: {
                                    cursor: "pointer",
                                    "border-bottom": "1px dotted var(--p-text-color-secondary)"
                                }
                            }, [
                                X(x(o.node.label), 1)
                            ], 40, Ge)), [
                                [
                                    c,
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
                    tool: r((o)=>[
                            O((p(), h("span", Qe, [
                                X(x(o.node.label), 1)
                            ])), [
                                [
                                    c,
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
                ]);
            };
        }
    });
    Xe = {
        class: "log-message"
    };
    Ye = {
        class: "log-message-header-container"
    };
    Ze = {
        class: "log-message-title"
    };
    et = {
        key: 0
    };
    tt = {
        style: {
            "font-weight": "500",
            "text-wrap": "nowrap"
        }
    };
    ot = {
        style: {
            "font-weight": "500"
        }
    };
    st = {
        class: "log-message-date"
    };
    lt = {
        key: 1,
        style: {
            "font-style": "italic",
            color: "var(--p-surface-f)",
            "margin-bottom": "0.5rem",
            "margin-top": "0rem"
        }
    };
    nt = [
        "onclick"
    ];
    at = {
        class: "log-dropdown-label"
    };
    it = {
        key: 2,
        class: "log-dropdown-additional-details"
    };
    dt = [
        "onclick"
    ];
    ct = {
        class: "log-dropdown-label"
    };
    rt = {
        key: 0,
        class: "log-dropdown-body"
    };
    ut = [
        "onclick"
    ];
    pt = {
        class: "log-dropdown-label"
    };
    vt = {
        key: 1,
        class: "log-dropdown-body"
    };
    mt = [
        "onclick"
    ];
    gt = {
        class: "log-dropdown-label"
    };
    ft = {
        key: 2,
        class: "log-dropdown-body"
    };
    yt = {
        class: "log-message-details"
    };
    bt = {
        style: {
            "font-style": "italic",
            color: "var(--p-surface-f)",
            "font-size": "0.85rem"
        }
    };
    _t = q({
        __name: "JSONMessage",
        props: [
            "logEntry",
            "options"
        ],
        setup (f) {
            const I = f, $ = N(()=>I.options?.value?.includes("quotes")), i = N(()=>I.options?.value?.includes("linenum")), _ = s(!1), b = s(!1), w = s(!1), t = s(!1);
            return (a, c)=>(p(), h("div", Xe, [
                    f.logEntry?.body ? (p(), M(u(pe), {
                        key: 0,
                        class: "log-message-panel"
                    }, {
                        header: r(()=>[
                                n("div", Ye, [
                                    n("div", Ze, [
                                        f.logEntry?.body?.parent_header?.msg_type ? (p(), h("div", et, [
                                            n("span", tt, x(f.logEntry?.body?.parent_header?.msg_type) + " > ", 1)
                                        ])) : L("", !0),
                                        n("span", ot, x(f.logEntry?.body?.header?.msg_type), 1),
                                        n("span", null, "(" + x(f.logEntry.type) + ")", 1)
                                    ]),
                                    n("span", st, x(f.logEntry?.timestamp.split("T")[1].slice(0, -1)), 1)
                                ])
                            ]),
                        default: r(()=>[
                                f.logEntry?.body?.content && Object.keys(f.logEntry?.body?.content).length > 0 ? (p(), M(u(se), {
                                    key: 0,
                                    showGridlines: "",
                                    stripedRows: "",
                                    class: "log-info-datatable",
                                    value: Object.entries(f.logEntry?.body?.content).map(([o, v])=>({
                                            key: o,
                                            value: v
                                        }))
                                }, {
                                    default: r(()=>[
                                            l(u(K), {
                                                field: "key"
                                            }),
                                            l(u(K), {
                                                field: "value"
                                            })
                                        ]),
                                    _: 1
                                }, 8, [
                                    "value"
                                ])) : (p(), h("p", lt, " (Empty body.) ")),
                                n("div", {
                                    class: "log-dropdown log-dropdown-details",
                                    onclick: ()=>{
                                        _.value = !_.value;
                                    }
                                }, [
                                    n("span", {
                                        class: J([
                                            "pi",
                                            {
                                                "pi-angle-right": !_.value,
                                                "pi-angle-down": _.value
                                            }
                                        ])
                                    }, null, 2),
                                    n("span", at, x(_.value ? "Hide" : "Show") + " Additional Details ", 1)
                                ], 8, nt),
                                _.value ? (p(), h("div", it, [
                                    n("div", {
                                        class: "log-dropdown log-dropdown-header",
                                        onclick: ()=>{
                                            w.value = !w.value;
                                        }
                                    }, [
                                        n("span", {
                                            class: J([
                                                "pi",
                                                {
                                                    "pi-angle-right": !w.value,
                                                    "pi-angle-down": w.value
                                                }
                                            ])
                                        }, null, 2),
                                        n("span", ct, x(w.value ? "Hide" : "Show") + " Header ", 1)
                                    ], 8, dt),
                                    w.value ? (p(), h("div", rt, [
                                        l(u(se), {
                                            showGridlines: "",
                                            stripedRows: "",
                                            class: "log-info-datatable",
                                            value: Object.entries(f.logEntry?.body?.header).map(([o, v])=>({
                                                    key: o,
                                                    value: v
                                                }))
                                        }, {
                                            default: r(()=>[
                                                    l(u(K), {
                                                        field: "key"
                                                    }),
                                                    l(u(K), {
                                                        field: "value"
                                                    })
                                                ]),
                                            _: 1
                                        }, 8, [
                                            "value"
                                        ])
                                    ])) : L("", !0),
                                    n("div", {
                                        class: "log-dropdown log-dropdown-parent-header",
                                        onclick: ()=>{
                                            t.value = !t.value;
                                        }
                                    }, [
                                        n("span", {
                                            class: J([
                                                "pi",
                                                {
                                                    "pi-angle-right": !t.value,
                                                    "pi-angle-down": t.value
                                                }
                                            ])
                                        }, null, 2),
                                        n("span", pt, x(t.value ? "Hide" : "Show") + " Parent Header ", 1)
                                    ], 8, ut),
                                    t.value ? (p(), h("div", vt, [
                                        l(u(se), {
                                            showGridlines: "",
                                            stripedRows: "",
                                            class: "log-info-datatable",
                                            value: Object.entries(f.logEntry?.body?.parent_header).map(([o, v])=>({
                                                    key: o,
                                                    value: v
                                                }))
                                        }, {
                                            default: r(()=>[
                                                    l(u(K), {
                                                        field: "key"
                                                    }),
                                                    l(u(K), {
                                                        field: "value"
                                                    })
                                                ]),
                                            _: 1
                                        }, 8, [
                                            "value"
                                        ])
                                    ])) : L("", !0),
                                    n("div", {
                                        class: "log-dropdown log-dropdown-raw",
                                        onclick: ()=>{
                                            b.value = !b.value;
                                        }
                                    }, [
                                        n("span", {
                                            class: J([
                                                "pi",
                                                {
                                                    "pi-angle-right": !b.value,
                                                    "pi-angle-down": b.value
                                                }
                                            ])
                                        }, null, 2),
                                        n("span", gt, x(b.value ? "Hide" : "Show") + " Raw Message (JSON) ", 1)
                                    ], 8, mt),
                                    b.value ? (p(), h("div", ft, [
                                        l(u(W), {
                                            data: f.logEntry.body,
                                            deep: 2,
                                            showLength: "",
                                            showIcon: "",
                                            showDoubleQuotes: $.value,
                                            showLineNumber: i.value
                                        }, null, 8, [
                                            "data",
                                            "showDoubleQuotes",
                                            "showLineNumber"
                                        ])
                                    ])) : L("", !0)
                                ])) : L("", !0),
                                n("div", yt, [
                                    n("span", bt, x(f.logEntry?.body?.header?.msg_id), 1)
                                ])
                            ]),
                        _: 1
                    })) : L("", !0)
                ]));
        }
    });
    kt = {
        class: "data-container"
    };
    ht = {
        class: "log-container"
    };
    wt = {
        class: "flex-container"
    };
    xt = {
        class: "p-input-icon-left",
        style: {
            padding: "0",
            margin: "0"
        }
    };
    $t = {
        class: "sort-actions p-buttonset"
    };
    Ct = {
        class: "bottom-actions"
    };
    St = {
        key: 1
    };
    At = q({
        __name: "MessagesPanel",
        props: [
            "entries",
            "sortby"
        ],
        emits: [
            "clearLogs"
        ],
        setup (f, { emit: I }) {
            const $ = f, i = s(""), _ = s("asc"), b = s([]);
            N(()=>b.value.includes("quotes")), N(()=>b.value.includes("linenum"));
            const w = N(()=>{
                const t = $.sortby || ((v)=>v.timestamp), a = (v, C)=>t(v) > t(C) ? 1 : t(v) < t(C) ? -1 : 0, c = (v, C)=>t(v) < t(C) ? 1 : t(v) > t(C) ? -1 : 0, o = $.entries?.filter((v)=>v.type.includes(i.value));
                return _.value === "asc" ? o.sort(a) : o.sort(c);
            });
            return (t, a)=>{
                const c = Y("tooltip");
                return p(), h("div", kt, [
                    n("div", ht, [
                        n("div", wt, [
                            n("div", xt, [
                                a[4] || (a[4] = n("i", {
                                    class: "pi pi-search"
                                }, null, -1)),
                                l(u(Le), {
                                    modelValue: i.value,
                                    "onUpdate:modelValue": a[0] || (a[0] = (o)=>i.value = o),
                                    size: "small",
                                    placeholder: "Type"
                                }, null, 8, [
                                    "modelValue"
                                ])
                            ]),
                            n("div", $t, [
                                O(l(u(U), {
                                    onClick: a[1] || (a[1] = (o)=>_.value = "asc"),
                                    outlined: "",
                                    size: "small",
                                    icon: "pi pi-sort-numeric-down",
                                    "aria-label": "Sort Time Asc"
                                }, null, 512), [
                                    [
                                        c,
                                        "Sort Asc",
                                        void 0,
                                        {
                                            bottom: !0
                                        }
                                    ]
                                ]),
                                O(l(u(U), {
                                    onClick: a[2] || (a[2] = (o)=>_.value = "desc"),
                                    outlined: "",
                                    size: "small",
                                    icon: "pi pi-sort-numeric-up-alt",
                                    "aria-label": "Sort Time Desc"
                                }, null, 512), [
                                    [
                                        c,
                                        "Sort Desc",
                                        void 0,
                                        {
                                            bottom: !0
                                        }
                                    ]
                                ])
                            ])
                        ]),
                        (p(!0), h(re, null, ue(w.value, (o)=>(p(), M(_t, {
                                "log-entry": o,
                                key: `${o.type}-${o.timestamp}`
                            }, null, 8, [
                                "log-entry"
                            ]))), 128)),
                        n("div", Ct, [
                            w.value.length ? (p(), M(u(U), {
                                key: 0,
                                label: "Clear Logs",
                                severity: "warning",
                                size: "small",
                                onClick: a[3] || (a[3] = (o)=>t.$emit("clearLogs"))
                            })) : (p(), h("p", St, " No logs. Ensure debug is enabled on context configuration. "))
                        ])
                    ])
                ]);
            };
        }
    });
    Mt = {
        class: "notebook-container"
    };
    Rt = {
        class: "welcome-placeholder"
    };
    Bt = q({
        __name: "DevInterface",
        props: [
            "config",
            "connectionSettings",
            "sessionName",
            "sessionId",
            "defaultKernel",
            "renderers"
        ],
        setup (f) {
            F("beakerAppConfig").setPage("dev");
            const $ = s(), i = s(), _ = s(), b = s(), w = s(), t = new URLSearchParams(window.location.search), a = t.has("session") ? t.get("session") : "dev_session", c = f, o = [
                ...Ve.map((e)=>new _e(e)).map(ke),
                ye,
                be
            ], v = {
                code: je,
                markdown: ze,
                query: Ce,
                raw: Pe
            }, C = s("connecting"), E = s([]), S = s([]), B = s();
            s();
            const P = s(null);
            s();
            const V = s(null), D = s(!1);
            s(!1), s(null), s(!1);
            const H = s(), G = s(), { theme: le, toggleDarkMode: Q } = F("theme"), Z = N(()=>_?.value?.beakerSession), g = (e)=>{
                e.header.msg_type === "preview" && (B.value = e.content), e.header.msg_type === "debug_event" && E.value.push({
                    type: e.content.event,
                    body: e.content.body,
                    timestamp: e.header.date
                });
            };
            ce(()=>i?.value?.notebook.cells, (e)=>{
                e?.length === 0 && i.value.insertCellBefore();
            }, {
                deep: !0
            });
            const m = (e, d)=>{
                /^complete_/.test(e.header.msg_type) || S.value.push({
                    type: d,
                    body: e,
                    timestamp: e.header.date
                });
            }, A = (e)=>{
                console.log("Unhandled message recieved", e);
            }, ee = (e)=>{
                C.value = e == "idle" ? "connected" : e;
            }, ve = (e)=>{
                H.value?.selectPanel("action"), G.value?.selectAction(e);
            }, te = (e, d)=>{
                const y = i.value;
                Z.value?.session.loadNotebook(e), V.value = d;
                const z = y.notebook.cells.map((k)=>k.id);
                z.includes(y.selectedCellId) || de(()=>{
                    y.selectCell(z[0]);
                });
            }, me = async (e)=>{
                V.value = e, e && (w.value?.selectPanel("Files"), await b.value.refresh(), await b.value.flashFile(e));
            }, ne = ()=>{
                i.value?.selectPrevCell();
            }, ae = ()=>{
                i.value?.selectNextCell();
            }, R = {}, ge = {
                "keydown.enter.ctrl.prevent.capture.in-cell": ()=>{
                    i.value?.selectedCell().execute(), i.value?.selectedCell().exit();
                },
                "keydown.enter.shift.prevent.capture.in-cell": ()=>{
                    const e = i.value?.selectedCell();
                    e.execute(), i.value?.selectNextCell() || (i.value?.insertCellAfter(e, void 0, !0), de(()=>{
                        i.value?.selectedCell().enter();
                    }));
                },
                "keydown.enter.exact.prevent.stop.!in-editor": ()=>{
                    i.value?.selectedCell().enter();
                },
                "keydown.esc.exact.prevent": ()=>{
                    i.value?.selectedCell().exit();
                },
                "keydown.up.!in-editor.prevent": ne,
                "keydown.k.!in-editor": ne,
                "keydown.down.!in-editor.prevent": ae,
                "keydown.j.!in-editor": ae,
                "keydown.a.prevent.!in-editor": (e)=>{
                    const d = i.value;
                    d?.selectedCell().exit(), d?.insertCellBefore();
                },
                "keydown.b.prevent.!in-editor": ()=>{
                    const e = i.value;
                    e?.selectedCell().exit(), e?.insertCellAfter();
                },
                "keydown.d.!in-editor": ()=>{
                    const e = i.value, d = e.selectedCell(), y = ()=>{
                        delete R.d;
                    };
                    if (R.d === void 0) {
                        const k = setTimeout(y, 1e3);
                        R.d = {
                            cell_id: d.id,
                            timeout: k
                        };
                    } else {
                        const { cell_id: k, timeout: j } = R.d;
                        k === d.id && (e?.removeCell(d), P.value = d.cell, delete R.d), j && window.clearTimeout(j);
                    }
                },
                "keydown.y.!in-editor": ()=>{
                    const d = i.value.selectedCell(), y = ()=>{
                        delete R.y;
                    };
                    if (R.y === void 0) {
                        const k = setTimeout(y, 1e3);
                        R.y = {
                            cell_id: d.id,
                            timeout: k
                        };
                    } else {
                        const { cell_id: k, timeout: j } = R.y;
                        k === d.id && (P.value = d.cell, delete R.y), j && window.clearTimeout(j);
                    }
                },
                "keydown.p.!in-editor": (e)=>{
                    const d = i.value;
                    let y = Ee(P.value);
                    if (y !== null) {
                        if (d.notebook.cells.map((k)=>k.id).includes(y.id)) {
                            const k = y.constructor, j = {
                                ...y,
                                id: void 0,
                                executionCount: void 0,
                                busy: void 0,
                                last_execution: void 0
                            };
                            y = new k(j);
                        }
                        e.key === "p" ? d?.insertCellAfter(d.selectedCell(), y) : e.key === "P" && d?.insertCellBefore(d.selectedCell(), y), y.value = null;
                    }
                }
            };
            return (e, d)=>{
                const y = Y("autoscroll"), z = Y("keybindings");
                return p(), M(he, {
                    title: "Beaker Dev Interface",
                    "title-extra": V.value,
                    connectionSettings: c.config,
                    ref_key: "beakerInterfaceRef",
                    ref: _,
                    sessionId: u(a),
                    defaultKernel: "beaker_kernel",
                    renderers: o,
                    onIopubMsg: g,
                    onUnhandledMsg: A,
                    onAnyMsg: m,
                    onSessionStatusChanged: ee,
                    onOpenFile: te
                }, {
                    "left-panel": r(()=>[
                            l(ie, {
                                position: "left",
                                "show-label": !0,
                                highlight: "line",
                                expanded: !1,
                                initialWidth: "20vi",
                                maximized: D.value
                            }, {
                                default: r(()=>[
                                        l(T, {
                                            label: "Info",
                                            icon: "pi pi-home"
                                        }, {
                                            default: r(()=>[
                                                    l(We, {
                                                        context: $.value?.info,
                                                        onActionSelected: ve
                                                    }, null, 8, [
                                                        "context"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        l(T, {
                                            id: "files",
                                            label: "Files",
                                            icon: "pi pi-file-export",
                                            "no-overflow": ""
                                        }, {
                                            default: r(()=>[
                                                    l(xe, {
                                                        ref_key: "filePanelRef",
                                                        ref: b,
                                                        onOpenFile: te
                                                    }, null, 512)
                                                ]),
                                            _: 1
                                        })
                                    ]),
                                _: 1
                            }, 8, [
                                "maximized"
                            ])
                        ]),
                    "right-panel": r(()=>[
                            l(ie, {
                                position: "right",
                                ref_key: "rightMenu",
                                ref: H,
                                highlight: "line",
                                "show-label": !0,
                                expanded: !1,
                                initialWidth: "20vi",
                                maximized: D.value
                            }, {
                                default: r(()=>[
                                        l(T, {
                                            tabId: "preview",
                                            label: "Preview",
                                            icon: "pi pi-eye"
                                        }, {
                                            default: r(()=>[
                                                    l(Be, {
                                                        previewData: B.value
                                                    }, null, 8, [
                                                        "previewData"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        l(T, {
                                            tabId: "action",
                                            label: "Actions",
                                            icon: "pi pi-send"
                                        }, {
                                            default: r(()=>[
                                                    l(u(Oe), {
                                                        class: "debug-card"
                                                    }, {
                                                        title: r(()=>d[3] || (d[3] = [
                                                                X("Execute an Action")
                                                            ])),
                                                        content: r(()=>[
                                                                l(qe, {
                                                                    ref_key: "executeActionRef",
                                                                    ref: G,
                                                                    rawMessages: S.value
                                                                }, null, 8, [
                                                                    "rawMessages"
                                                                ])
                                                            ]),
                                                        _: 1
                                                    })
                                                ]),
                                            _: 1
                                        }),
                                        l(T, {
                                            tabId: "logging",
                                            label: "Logging",
                                            icon: "pi pi-list"
                                        }, {
                                            default: r(()=>[
                                                    O(l(we, {
                                                        entries: E.value,
                                                        onClearLogs: d[1] || (d[1] = (k)=>E.value.splice(0, E.value.length))
                                                    }, null, 8, [
                                                        "entries"
                                                    ]), [
                                                        [
                                                            y
                                                        ]
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        l(T, {
                                            label: "Messages",
                                            icon: "pi pi-comments"
                                        }, {
                                            default: r(()=>[
                                                    O(l(At, {
                                                        entries: S.value,
                                                        onClearLogs: d[2] || (d[2] = (k)=>S.value.splice(0, S.value.length))
                                                    }, null, 8, [
                                                        "entries"
                                                    ]), [
                                                        [
                                                            y
                                                        ]
                                                    ])
                                                ]),
                                            _: 1
                                        })
                                    ]),
                                _: 1
                            }, 8, [
                                "maximized"
                            ])
                        ]),
                    default: r(()=>[
                            n("div", Mt, [
                                O((p(), M($e, {
                                    ref_key: "beakerNotebookRef",
                                    ref: i,
                                    "cell-map": v
                                }, {
                                    default: r(()=>[
                                            l(Se, {
                                                "default-severity": "",
                                                saveAvailable: !0,
                                                "save-as-filename": V.value,
                                                onNotebookSaved: me,
                                                onOpenFile: te
                                            }, {
                                                "end-extra": r(()=>[
                                                        l(u(U), {
                                                            onClick: d[0] || (d[0] = (k)=>{
                                                                D.value = !D.value;
                                                            }),
                                                            icon: `pi ${D.value ? "pi-window-minimize" : "pi-window-maximize"}`,
                                                            size: "small",
                                                            text: ""
                                                        }, null, 8, [
                                                            "icon"
                                                        ])
                                                    ]),
                                                _: 1
                                            }, 8, [
                                                "save-as-filename"
                                            ]),
                                            O((p(), M(Ae, {
                                                "selected-cell": i.value?.selectedCellId
                                            }, {
                                                "notebook-background": r(()=>[
                                                        n("div", Rt, [
                                                            l(Me)
                                                        ])
                                                    ]),
                                                _: 1
                                            }, 8, [
                                                "selected-cell"
                                            ])), [
                                                [
                                                    y
                                                ]
                                            ]),
                                            l(Re, {
                                                class: "agent-query-container"
                                            })
                                        ]),
                                    _: 1
                                })), [
                                    [
                                        z,
                                        ge,
                                        void 0,
                                        {
                                            top: !0
                                        }
                                    ]
                                ])
                            ])
                        ]),
                    _: 1
                }, 8, [
                    "title-extra",
                    "connectionSettings",
                    "sessionId"
                ]);
            };
        }
    });
});
export { Bt as default, __tla };
