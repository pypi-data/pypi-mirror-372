import { i as we, j as q, a as be, L as ke, M as xe, T as _e, b as Ce, w as Ie, _ as Ve, c as ve, d as D, e as Re, f as Ee, g as $e, __tla as __tla_0 } from "./DebugPanel.vue_vue_type_style_index_0_lang-PW_f_WLw.js";
import { g as Fe, f as ge, _ as Se, a as Me, b as Ue, u as Oe, c as Ne, d as Le, e as Pe, h as je, l as qe, __tla as __tla_1 } from "./IntegrationPanel.vue_vue_type_style_index_0_lang-Dl0CwqlQ.js";
import { N as Te } from "./NotebookSvg-DhCzyRVi.js";
import { d as de, aa as he, i as te, ab as ye, f as O, r as u, g as j, J as ce, y as I, o as v, B as n, u as i, E as o, $ as P, ac as Ae, G as ae, M as R, a8 as Be, L as E, I as m, j as x, a1 as K, ad as T, z as ue, A as re, a9 as me, K as G, ae as De, a0 as ze, Q as Je, O as Ke, Y as Ge, af as Qe, n as fe } from "./primevue-1TEWPnDt.js";
import { u as We, __tla as __tla_2 } from "./index-D-jLGYR3.js";
import { s as Ye } from "./jupyterlab-C2EV-Dpr.js";
import "./xlsx-Ck9ILNdx.js";
import "./_plugin-vue_export-helper-DlAUqK2U.js";
import "./codemirror-C5EHd1r4.js";
import { __tla as __tla_3 } from "./pdfjs-4lX-eNFD.js";
let Pt;
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
    let He, Xe, Ze, et, tt, at, lt, nt, ot, st, it, ut, rt, dt, ct, pt, vt, mt, ft, gt, ht, yt, wt, bt, kt, xt, _t, Ct, It, Vt;
    He = {
        class: "integration-editor"
    };
    Xe = {
        key: 0,
        class: "integration-loading"
    };
    Ze = {
        key: 1,
        class: "integration-main-content"
    };
    et = {
        class: "integration-header"
    };
    tt = {
        class: "constrained-editor-height"
    };
    at = [
        "value"
    ];
    lt = [
        "value"
    ];
    nt = {
        key: 0,
        style: {
            display: "flex",
            "flex-direction": "column",
            gap: "0.5rem"
        }
    };
    ot = {
        class: "constrained-editor-height"
    };
    st = {
        style: {
            flex: "1 0",
            margin: "0.2rem",
            display: "flex",
            "justify-content": "flex-end"
        }
    };
    it = {
        key: 0,
        style: {
            "flex-shrink": "0"
        }
    };
    ut = de({
        __name: "IntegrationEditor",
        props: he({
            fetchResources: {
                type: Function
            },
            deleteResource: {
                type: Function
            },
            modifyResource: {
                type: Function
            },
            modifyIntegration: {
                type: Function
            }
        }, {
            modelValue: {},
            modelModifiers: {}
        }),
        emits: [
            "update:modelValue"
        ],
        setup (N) {
            const U = te("show_toast"), f = N, r = te("beakerSession"), a = ye(N, "modelValue"), $ = (s)=>Object.values(s).toSorted((t, y)=>t?.name.localeCompare(y?.name)), b = O(()=>Object.fromEntries(Object.entries(a.value.integrations ?? {}).filter(([s, t])=>Fe(t) === "adhoc"))), z = O(()=>$(b.value)), d = O(()=>b.value[a.value.selected]), k = O(()=>ge(a.value.integrations[a.value.selected]?.resources, "file")), A = u(), S = u([]), M = u([]);
            j(()=>a.value.selected, ()=>{
                a.value.unsavedChanges = !1, M.value = [], S.value = [], f.fetchResources();
            });
            const c = ()=>{
                const t = {
                    name: "New Integration",
                    source: "This is the prompt information that the agent will consult when using the integration. Include API details or how to find datasets here.",
                    description: "This is the description that the agent will use to determine when this integration should be used.",
                    provider: Object.keys(a.value?.integrations).length ? Object.values(a.value.integrations).at(0)?.provider : "adhoc:specialist_agents",
                    slug: "new_integration",
                    uuid: "new",
                    url: ""
                };
                a.value.integrations.new = t, a.value.selected = "new", a.value.unsavedChanges = !0;
                const y = A?.value?.$el;
                y?.select(), y?.focus();
            }, p = (s, t)=>{
                const y = (e)=>{
                    s() ? e() : setTimeout(()=>y(e), t);
                };
                return new Promise(y);
            }, L = We();
            j(()=>L, (s)=>{
                s.query?.selected === "new" ? a.value.finishedInitialLoad ? c() : p(()=>a.value.finishedInitialLoad, 100).then(()=>c()) : a.value.selected = s.query?.selected ?? a.value.selected;
            }, {
                immediate: !0,
                deep: !0
            }), j(a, ({ unsavedChanges: s })=>{
                s ? onbeforeunload = ()=>!0 : onbeforeunload = void 0;
            });
            const h = u();
            j(()=>[
                    d?.value?.description
                ], (s)=>{
                h.value && (h.value.model = s[0]);
            });
            const _ = u();
            j(()=>[
                    d.value?.source
                ], (s)=>{
                _.value && (_.value.model = s[0]);
            });
            const V = u(void 0), le = u(void 0), F = u(void 0), Q = u(void 0), W = u(void 0), J = O(()=>{
                const s = [];
                for (const t of Object.values(k.value))RegExp(`{{\\s*${t?.name}\\s*}}`).test(d?.value?.source) || s.push(t.name);
                return s;
            }), B = ()=>a.value.unsavedChanges ? confirm("You currently have unsaved changes that would be lost with this change. Are you sure?") : !0, Y = async (s)=>{
                a.value.unsavedChanges = !0, delete d.value.resources[s], S.value.push(s);
            }, g = u(), ne = ()=>{
                g.value = void 0, F.value?.click();
            }, H = we.parse(document.cookie)._xsrf, X = async ()=>{
                if (d?.value !== void 0) {
                    for (const s of S.value)await f.deleteResource(s);
                    if (S.value = [], a.value.selected === "new") {
                        const s = d.value.source, t = [
                            ...M.value
                        ];
                        await f.modifyIntegration({
                            ...d.value,
                            source: ""
                        });
                        for (const y of t)await f.modifyResource(y);
                        d.value.source = s;
                    } else for (const [s, t] of Object.entries(k.value))await f.modifyResource(t, s);
                    await f.modifyIntegration(d.value, a.value.selected), U({
                        title: "Saved!",
                        detail: "The session will now reconnect and load the new definition.",
                        severity: "success",
                        life: 4e3
                    }), delete a.value.integrations.new, a.value.unsavedChanges = !1;
                }
            }, Z = async ()=>{
                const s = Q.value.uploadfiles?.files;
                await ee(s);
            }, oe = async ()=>{
                const s = W.value.uploadfilesMultiple?.files;
                await ee(s);
            }, ee = async (s)=>{
                a.value.unsavedChanges = !0;
                const t = Array.from(s).map(async (y)=>{
                    const e = [], l = y.stream().getReader();
                    for(var w = (await l.read()).value; w?.length > 0;)e.push(Array.from(w, (ie)=>String.fromCharCode(ie)).join("")), w = (await l.read()).value;
                    const C = {
                        resource_type: "file",
                        integration: a.value.selected,
                        content: String(e),
                        filepath: y.name,
                        name: y.name.split(".")[0]
                    };
                    a.value.selected !== "new" ? await f.modifyResource(C) : M.value.push(C);
                });
                await Promise.all(t);
            }, se = async (s)=>{
                const t = d.value.resources[s], y = new Blob([
                    t?.content
                ], {
                    type: "text/plain"
                }), e = window.URL.createObjectURL(y), l = document.createElement("a");
                l.href = e, l.download = t.filepath, l.click(), window.URL.revokeObjectURL(e), l.remove();
            };
            return (s, t)=>{
                const y = ce("tooltip");
                return v(), I("div", He, [
                    i(r).status === "connecting" ? (v(), I("div", Xe, [
                        o(i(Ae)),
                        P(" Loading integrations... " + ae(i(r)?.status), 1)
                    ])) : (v(), I("div", Ze, [
                        n("div", et, [
                            o(i(Be), {
                                options: z.value.map((e)=>({
                                        label: e.name,
                                        value: e.uuid
                                    })),
                                "option-label": (e)=>e?.label ?? "Select integration...",
                                "option-value": "value",
                                placeholder: "Select a integration...",
                                onClick: t[0] || (t[0] = (e)=>{
                                    B() ? a.value.unsavedChanges = !1 : e.preventDefault;
                                }),
                                modelValue: a.value.selected,
                                "onUpdate:modelValue": t[1] || (t[1] = (e)=>a.value.selected = e)
                            }, null, 8, [
                                "options",
                                "option-label",
                                "modelValue"
                            ]),
                            o(i(E), {
                                onClick: t[2] || (t[2] = ()=>{
                                    B() && c();
                                }),
                                label: "New Integration"
                            })
                        ]),
                        o(i(T), {
                            legend: "Name"
                        }, {
                            default: m(()=>[
                                    d.value ? (v(), x(i(K), {
                                        key: 0,
                                        ref_key: "nameInput",
                                        ref: A,
                                        modelValue: d.value.name,
                                        "onUpdate:modelValue": t[3] || (t[3] = (e)=>d.value.name = e),
                                        placeholder: d.value?.name ? "Name" : "No integration selected.",
                                        onChange: t[4] || (t[4] = (e)=>{
                                            a.value.unsavedChanges = !0;
                                        })
                                    }, null, 8, [
                                        "modelValue",
                                        "placeholder"
                                    ])) : (v(), x(i(K), {
                                        key: 1,
                                        disabled: "",
                                        placeholder: "No integration selected."
                                    }))
                                ]),
                            _: 1
                        }),
                        o(i(T), {
                            legend: "Description"
                        }, {
                            default: m(()=>[
                                    t[11] || (t[11] = n("p", null, " The description, used by both users and the agent, provides a brief summary of the purpose of this integration. The agent will use this to select which integration best matches a user's request. ", -1)),
                                    n("div", tt, [
                                        d.value ? (v(), x(q, {
                                            key: 0,
                                            language: "markdown",
                                            "autocomplete-enabled": !1,
                                            modelValue: d.value.description,
                                            "onUpdate:modelValue": t[5] || (t[5] = (e)=>d.value.description = e),
                                            onChange: t[6] || (t[6] = (e)=>a.value.unsavedChanges = !0),
                                            ref_key: "descriptionEditor",
                                            ref: h
                                        }, null, 8, [
                                            "modelValue"
                                        ])) : (v(), x(q, {
                                            key: 1,
                                            language: "markdown",
                                            autocompleteEnabled: !1,
                                            disabled: "",
                                            modelValue: V.value,
                                            "onUpdate:modelValue": t[7] || (t[7] = (e)=>V.value = e),
                                            placeholder: "No integration selected."
                                        }, null, 8, [
                                            "modelValue"
                                        ]))
                                    ])
                                ]),
                            _: 1
                        }),
                        o(i(T), {
                            legend: "User Files"
                        }, {
                            default: m(()=>[
                                    t[13] || (t[13] = n("p", null, " Uploaded files will be used by the agent in one of two ways: either included in the instruction body, or when running code based on a user's request. For included documentation, these files should be included in the body and will be used in determining what steps to take for the user's request. For large datasets, these are used once the agent is executing a request. ", -1)),
                                    n("form", {
                                        ref_key: "uploadForm",
                                        ref: Q
                                    }, [
                                        n("input", {
                                            onChange: Z,
                                            ref_key: "fileInput",
                                            ref: le,
                                            type: "file",
                                            style: {
                                                display: "none"
                                            },
                                            name: "uploadfiles"
                                        }, null, 544),
                                        n("input", {
                                            type: "hidden",
                                            name: "_xsrf",
                                            value: i(H)
                                        }, null, 8, at)
                                    ], 512),
                                    n("form", {
                                        ref_key: "uploadFormMultiple",
                                        ref: W
                                    }, [
                                        n("input", {
                                            onChange: oe,
                                            ref_key: "fileInputMultiple",
                                            ref: F,
                                            type: "file",
                                            style: {
                                                display: "none"
                                            },
                                            name: "uploadfilesMultiple",
                                            multiple: ""
                                        }, null, 544),
                                        n("input", {
                                            type: "hidden",
                                            name: "_xsrf",
                                            value: i(H)
                                        }, null, 8, lt)
                                    ], 512),
                                    (v(!0), I(ue, null, re(k.value, (e, l)=>(v(), x(i(me), {
                                            key: e?.filepath
                                        }, {
                                            start: m(()=>[
                                                    G(o(i(E), {
                                                        icon: "pi pi-download",
                                                        style: {
                                                            width: "32px",
                                                            height: "32px"
                                                        },
                                                        onClick: (w)=>se(l)
                                                    }, null, 8, [
                                                        "onClick"
                                                    ]), [
                                                        [
                                                            y,
                                                            "Download"
                                                        ]
                                                    ])
                                                ]),
                                            center: m(()=>[
                                                    o(i(K), {
                                                        modelValue: e.name,
                                                        "onUpdate:modelValue": (w)=>e.name = w,
                                                        type: "text"
                                                    }, null, 8, [
                                                        "modelValue",
                                                        "onUpdate:modelValue"
                                                    ])
                                                ]),
                                            end: m(()=>[
                                                    G(o(i(E), {
                                                        icon: "pi pi-trash",
                                                        severity: "danger",
                                                        style: {
                                                            width: "32px",
                                                            height: "32px"
                                                        },
                                                        onClick: (w)=>Y(l)
                                                    }, null, 8, [
                                                        "onClick"
                                                    ]), [
                                                        [
                                                            y,
                                                            "Remove File"
                                                        ]
                                                    ])
                                                ]),
                                            _: 2
                                        }, 1024))), 128)),
                                    (v(!0), I(ue, null, re(M.value, (e, l)=>(v(), x(i(me), {
                                            key: e?.filepath
                                        }, {
                                            start: m(()=>t[12] || (t[12] = [
                                                    n("span", null, "Pending Upload", -1)
                                                ])),
                                            center: m(()=>[
                                                    o(i(K), {
                                                        modelValue: e.name,
                                                        "onUpdate:modelValue": (w)=>e.name = w,
                                                        type: "text"
                                                    }, null, 8, [
                                                        "modelValue",
                                                        "onUpdate:modelValue"
                                                    ])
                                                ]),
                                            end: m(()=>[
                                                    G(o(i(E), {
                                                        icon: "pi pi-trash",
                                                        severity: "danger",
                                                        style: {
                                                            width: "32px",
                                                            height: "32px"
                                                        },
                                                        onClick: (w)=>M.value.splice(l, 1)
                                                    }, null, 8, [
                                                        "onClick"
                                                    ]), [
                                                        [
                                                            y,
                                                            "Remove File"
                                                        ]
                                                    ])
                                                ]),
                                            _: 2
                                        }, 1024))), 128)),
                                    o(i(E), {
                                        onClick: ne,
                                        style: {
                                            width: "fit-content",
                                            height: "32px"
                                        },
                                        label: "Add New Files",
                                        icon: "pi pi-plus",
                                        disabled: !d.value
                                    }, null, 8, [
                                        "disabled"
                                    ])
                                ]),
                            _: 1
                        }),
                        J.value.length > 0 ? (v(), I("div", nt, [
                            o(i(De), {
                                icon: "pi pi-exclamation-triangle",
                                severity: "warning",
                                size: "large"
                            }, {
                                default: m(()=>[
                                        P(" Some files are not included: " + ae(J.value.join(", ")) + "; see the above documentation about how to reference these files. ", 1)
                                    ]),
                                _: 1
                            })
                        ])) : R("", !0),
                        o(i(T), {
                            legend: "Agent Instructions"
                        }, {
                            default: m(()=>[
                                    t[14] || (t[14] = n("p", null, " Agent instructions will be given to the agent when it creates a plan to execute a user's request. ", -1)),
                                    t[15] || (t[15] = n("span", {
                                        style: {
                                            "margin-bottom": "1rem"
                                        }
                                    }, [
                                        P(" Files uploaded above can be referenced in the below agent instructions with "),
                                        n("span", {
                                            style: {
                                                "font-family": "monospace"
                                            }
                                        }, "{filename}"),
                                        P(", such as if you uploaded a file named "),
                                        n("span", {
                                            style: {
                                                "font-family": "monospace"
                                            }
                                        }, "documentation.txt"),
                                        P(" and it shows above with the name "),
                                        n("span", {
                                            style: {
                                                "font-family": "monospace"
                                            }
                                        }, "documentation"),
                                        P(", adding "),
                                        n("span", {
                                            style: {
                                                "font-family": "monospace"
                                            }
                                        }, "{documentation}"),
                                        P(" to the body below will ensure the agent can read your uploaded file. ")
                                    ], -1)),
                                    n("div", ot, [
                                        d.value ? (v(), x(q, {
                                            key: 0,
                                            language: "markdown",
                                            autocompleteEnabled: !0,
                                            "autocomplete-options": Object.values(k.value).map((e)=>e.name),
                                            modelValue: d.value.source,
                                            "onUpdate:modelValue": t[8] || (t[8] = (e)=>d.value.source = e),
                                            onChange: t[9] || (t[9] = (e)=>a.value.unsavedChanges = !0),
                                            ref_key: "instructionEditor",
                                            ref: _
                                        }, null, 8, [
                                            "autocomplete-options",
                                            "modelValue"
                                        ])) : (v(), x(q, {
                                            key: 1,
                                            language: "markdown",
                                            autocompleteEnabled: !1,
                                            disabled: "",
                                            modelValue: V.value,
                                            "onUpdate:modelValue": t[10] || (t[10] = (e)=>V.value = e),
                                            placeholder: "No integration selected."
                                        }, null, 8, [
                                            "modelValue"
                                        ]))
                                    ])
                                ]),
                            _: 1
                        })
                    ])),
                    n("div", st, [
                        a.value.unsavedChanges ? (v(), I("div", it, [
                            o(i(E), {
                                onClick: X,
                                disabled: !d.value,
                                icon: "pi pi-save",
                                label: "Save Changes",
                                severity: "success"
                            }, null, 8, [
                                "disabled"
                            ])
                        ])) : R("", !0)
                    ])
                ]);
            };
        }
    });
    rt = {
        class: "examples-panel"
    };
    dt = {
        key: 0,
        class: "header-controls"
    };
    ct = {
        style: {
            display: "flex",
            "flex-direction": "column",
            "padding-top": "0.25rem",
            "padding-bottom": "0.25rem",
            gap: "0.5rem",
            width: "100%"
        }
    };
    pt = {
        key: 0
    };
    vt = {
        key: 1,
        class: "examples-editor-list"
    };
    mt = [
        "onMouseenter"
    ];
    ft = {
        class: "example-editor-card-title"
    };
    gt = {
        class: "example-editor-card-title-text"
    };
    ht = {
        key: 2,
        class: "example-editor-focused"
    };
    yt = {
        class: "example-editor-button-container"
    };
    wt = {
        class: "example-buttons-left"
    };
    bt = {
        class: "example-buttons-right"
    };
    kt = {
        class: "example-editor-main-content",
        style: {
            "flex-direction": "column"
        }
    };
    xt = {
        class: "example-editor-button-container"
    };
    _t = {
        class: "example-buttons-left"
    };
    Ct = de({
        __name: "ExamplesPanel",
        props: he({
            disabled: {
                type: Boolean
            },
            deleteResource: {
                type: Function
            },
            modifyResource: {
                type: Function
            }
        }, {
            modelValue: {},
            modelModifiers: {}
        }),
        emits: [
            "update:modelValue"
        ],
        setup (N) {
            const U = N, f = ye(N, "modelValue"), r = u({
                view: "tableOfContents"
            }), a = u(), $ = u(void 0), b = O(()=>ge(f.value.integrations[f.value.selected]?.resources, "example")), z = (c, p, L)=>{
                if (c === void 0) return !0;
                const h = c.toLowerCase(), _ = (p ?? "").toLowerCase(), V = (L ?? "").toLowerCase();
                return h.trim() === "" || _.includes(h) || V.includes(h);
            }, d = async ()=>{
                let c = f.value.integrations[f.value.selected]?.resources;
                c == null && (f.value.integrations[f.value.selected].resources = {}, c = f.value.integrations[f.value.selected].resources), c.new = {
                    resource_type: "example",
                    query: "New Example",
                    code: "",
                    notes: ""
                }, r.value = {
                    view: "focused",
                    focusedExampleId: "new"
                };
            }, k = (c)=>{
                $.value = void 0, r.value = {
                    view: "focused",
                    focusedExampleId: c
                };
            }, A = ()=>{
                r.value = {
                    view: "tableOfContents"
                };
                const c = f.value.integrations[f.value.selected]?.resources;
                c?.new && delete c.new;
            }, S = async ()=>{
                if (r.value.view === "tableOfContents") return;
                const c = f.value.integrations[f.value.selected]?.resources;
                r.value.focusedExampleId === "new" ? (await U.modifyResource(c[r.value.focusedExampleId]), delete c.new) : await U.modifyResource(c[r.value.focusedExampleId], r.value.focusedExampleId), r.value = {
                    view: "tableOfContents"
                };
            }, M = async ()=>{
                if (r.value.view === "tableOfContents") return;
                let c = f.value.integrations[f.value.selected]?.resources;
                r.value.focusedExampleId === "new" ? c?.new && delete c.new : (delete c[r.value.focusedExampleId], U.deleteResource(r.value.focusedExampleId)), r.value = {
                    view: "tableOfContents"
                };
            };
            return (c, p)=>{
                const L = ce("tooltip");
                return v(), I("div", rt, [
                    r.value.view === "tableOfContents" ? (v(), I("div", dt, [
                        o(i(Je), null, {
                            default: m(()=>[
                                    o(i(ze), null, {
                                        default: m(()=>p[6] || (p[6] = [
                                                n("i", {
                                                    class: "pi pi-search"
                                                }, null, -1)
                                            ])),
                                        _: 1
                                    }),
                                    o(i(K), {
                                        placeholder: "Search Examples...",
                                        modelValue: a.value,
                                        "onUpdate:modelValue": p[0] || (p[0] = (h)=>a.value = h)
                                    }, null, 8, [
                                        "modelValue"
                                    ]),
                                    a.value !== void 0 && a.value !== "" ? G((v(), x(i(E), {
                                        key: 0,
                                        icon: "pi pi-times",
                                        severity: "danger",
                                        onClick: p[1] || (p[1] = ()=>{
                                            a.value = void 0;
                                        })
                                    }, null, 512)), [
                                        [
                                            L,
                                            "Clear Search",
                                            void 0,
                                            {
                                                left: !0
                                            }
                                        ]
                                    ]) : R("", !0)
                                ]),
                            _: 1
                        }),
                        o(i(E), {
                            style: {
                                height: "32px",
                                width: "fit-content",
                                "flex-shrink": "0"
                            },
                            icon: "pi pi-plus",
                            label: "Add New Example",
                            disabled: c.disabled,
                            onClick: d
                        }, null, 8, [
                            "disabled"
                        ]),
                        n("div", ct, [
                            c.disabled ? (v(), I("p", pt, "New integration must be saved first to allow editing examples.")) : R("", !0),
                            n("i", null, ae(Object.keys(b.value ?? {}).length) + " examples available:", 1)
                        ])
                    ])) : R("", !0),
                    r.value.view === "tableOfContents" ? (v(), I("div", vt, [
                        (v(!0), I(ue, null, re(b.value ?? {}, (h, _)=>(v(), I("div", {
                                class: "example-card",
                                key: _,
                                onMouseleave: p[2] || (p[2] = (V)=>$.value = void 0),
                                onMouseenter: (V)=>$.value = _
                            }, [
                                z(a.value, h?.query, h?.notes) ? (v(), x(i(Ke), {
                                    key: 0,
                                    onClick: (V)=>k(_),
                                    pt: {
                                        root: {
                                            style: "transition: background-color 150ms linear;" + ($.value === _ ? "background-color: var(--surface-100); cursor: pointer;" : "")
                                        }
                                    }
                                }, {
                                    title: m(()=>[
                                            n("div", ft, [
                                                n("span", gt, ae(h?.query), 1),
                                                n("i", {
                                                    class: "pi pi-chevron-right example-arrow",
                                                    style: Ge($.value === _ ? "opacity: 1;" : "opacity: 0;")
                                                }, null, 4)
                                            ])
                                        ]),
                                    _: 2
                                }, 1032, [
                                    "onClick",
                                    "pt"
                                ])) : R("", !0)
                            ], 40, mt))), 128))
                    ])) : r.value.view === "focused" ? (v(), I("div", ht, [
                        n("div", yt, [
                            n("div", wt, [
                                o(i(E), {
                                    severity: "warning",
                                    icon: "pi pi-arrow-left",
                                    onClick: A,
                                    label: "Cancel Editing",
                                    style: {
                                        width: "fit-content"
                                    }
                                })
                            ]),
                            n("div", bt, [
                                o(i(E), {
                                    icon: "pi pi-trash",
                                    severity: "danger",
                                    label: "Delete Example",
                                    onClick: M
                                })
                            ])
                        ]),
                        n("div", kt, [
                            o(i(T), {
                                legend: "Query"
                            }, {
                                default: m(()=>[
                                        p[7] || (p[7] = n("p", null, 'The query tells the specialist agent what task this example is for, e.g. "Fetch and display specific studies about a given topic.".', -1)),
                                        n("div", null, [
                                            b.value?.[r.value?.focusedExampleId]?.query !== void 0 ? (v(), x(q, {
                                                key: 0,
                                                language: "markdown",
                                                autocompleteEnabled: !1,
                                                modelValue: b.value[r.value.focusedExampleId].query,
                                                "onUpdate:modelValue": p[3] || (p[3] = (h)=>b.value[r.value.focusedExampleId].query = h)
                                            }, null, 8, [
                                                "modelValue"
                                            ])) : R("", !0)
                                        ])
                                    ]),
                                _: 1
                            }),
                            o(i(T), {
                                legend: "Description"
                            }, {
                                default: m(()=>[
                                        p[8] || (p[8] = n("p", null, "Providing a description helps the specialist agent know when and in what cases this examples is useful.", -1)),
                                        n("div", null, [
                                            b.value?.[r.value?.focusedExampleId]?.notes !== void 0 ? (v(), x(q, {
                                                key: 0,
                                                language: "markdown",
                                                autocompleteEnabled: !1,
                                                modelValue: b.value[r.value.focusedExampleId].notes,
                                                "onUpdate:modelValue": p[4] || (p[4] = (h)=>b.value[r.value.focusedExampleId].notes = h)
                                            }, null, 8, [
                                                "modelValue"
                                            ])) : R("", !0)
                                        ])
                                    ]),
                                _: 1
                            }),
                            o(i(T), {
                                legend: "Code"
                            }, {
                                default: m(()=>[
                                        p[9] || (p[9] = n("p", null, "Code given for a specific example helps the specialist agent use a known-working approach to handle the user's request.", -1)),
                                        n("div", null, [
                                            b.value?.[r.value?.focusedExampleId]?.code !== void 0 ? (v(), x(q, {
                                                key: 0,
                                                autocompleteEnabled: !1,
                                                modelValue: b.value[r.value.focusedExampleId].code,
                                                "onUpdate:modelValue": p[5] || (p[5] = (h)=>b.value[r.value.focusedExampleId].code = h),
                                                language: "python"
                                            }, null, 8, [
                                                "modelValue"
                                            ])) : R("", !0)
                                        ])
                                    ]),
                                _: 1
                            })
                        ]),
                        n("div", xt, [
                            n("div", _t, [
                                o(i(E), {
                                    icon: "pi pi-check-circle",
                                    onClick: S,
                                    label: "Apply Changes",
                                    style: {
                                        width: "fit-content"
                                    },
                                    severity: "success"
                                })
                            ])
                        ])
                    ])) : R("", !0)
                ]);
            };
        }
    });
    It = {
        class: "integration-container"
    };
    Vt = {
        class: "beaker-notebook"
    };
    Pt = de({
        __name: "IntegrationsInterface",
        props: [
            "config",
            "connectionSettings",
            "sessionName",
            "sessionId",
            "defaultKernel",
            "renderers"
        ],
        setup (N) {
            const U = u(), f = u(), r = u(), a = u(), $ = u(), b = u(), z = u(!1), d = new URLSearchParams(window.location.search), k = d.has("session") ? d.get("session") : "notebook_dev_session", A = d.has("selected") ? d.get("selected") : void 0, S = N, M = [
                ...Ye.map((e)=>new Ce(e)).map(Ie),
                be,
                ke,
                xe,
                _e
            ], c = u("connecting"), p = u([]), L = u([]), h = u(null), _ = u(!1), { theme: V, toggleDarkMode: le } = te("theme"), F = te("beakerAppConfig");
            F.setPage("integrations");
            const Q = u(), W = u(), J = u(!1);
            u(), u(!1);
            const B = u();
            Qe(()=>{
                J.value || (fe(()=>$.value.selectPanel("integrations")), fe(()=>b.value.selectPanel("examples")), document.querySelector("div.sidemenu.right").style.width = "36vi", document.querySelector("div.sidemenu.left").style.width = "25vi", J.value = !0);
            });
            const Y = O(()=>f?.value?.beakerSession), g = u({
                selected: A,
                integrations: {},
                unsavedChanges: !1,
                finishedInitialLoad: !1
            }), ne = async ()=>{
                const e = g.value.integrations?.[g.value?.selected];
                if (e !== void 0) {
                    if (g.value?.selected === "new") {
                        (e?.resources === void 0 || e?.resources === null) && (e.resources = {});
                        return;
                    }
                    e.resources = Object.fromEntries((await Ue(k, g.value.selected))?.map((l)=>[
                            l.resource_id,
                            l
                        ]) ?? []);
                }
            }, pe = async ()=>{
                g.value.integrations = await qe(k), g.value.finishedInitialLoad = !0;
            }, H = async (e, l)=>{
                if (l) g.value.integrations[l] = await Oe(k, l, e);
                else {
                    const w = await Ne(k, e);
                    g.value.integrations[w.uuid] = w, g.value.selected = w.uuid;
                }
            }, X = async (e, l)=>{
                const w = g.value.integrations?.[g.value?.selected];
                if (l) w.resources[l] = await Le(k, g.value.selected, l, e);
                else {
                    const C = await Pe(k, g.value.selected, e);
                    w.resources[C.resource_id] = C;
                }
            }, Z = async (e)=>{
                await je(k, g.value.selected, e);
            };
            j(Y, async ()=>pe());
            const oe = O(()=>{
                const e = [];
                if (!F?.config?.pages || Object.hasOwn(F.config.pages, "notebook")) {
                    const l = "/" + (F?.config?.pages?.notebook?.default ? "" : "notebook") + window.location.search;
                    e.push({
                        type: "link",
                        href: l,
                        label: "Navigate to notebook view",
                        component: Te,
                        componentStyle: {
                            fill: "currentColor",
                            stroke: "currentColor",
                            height: "1rem",
                            width: "1rem"
                        }
                    });
                }
                if (!F?.config?.pages || Object.hasOwn(F.config.pages, "chat")) {
                    const l = "/" + (F?.config?.pages?.chat?.default ? "" : "chat") + window.location.search;
                    e.push({
                        type: "link",
                        href: l,
                        icon: "comment",
                        label: "Navigate to chat view"
                    });
                }
                return e.push({
                    type: "button",
                    icon: V.mode === "dark" ? "sun" : "moon",
                    command: le,
                    label: `Switch to ${V.mode === "dark" ? "light" : "dark"} mode.`
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
            });
            j(()=>U?.value?.notebook.cells, (e)=>{
                e?.length === 0 && U.value.insertCellBefore();
            }, {
                deep: !0
            });
            const ee = (e)=>{
                e.header.msg_type === "preview" ? Q.value = e.content : e.header.msg_type === "kernel_state_info" ? W.value = e.content : e.header.msg_type === "debug_event" && p.value.push({
                    type: e.content.event,
                    body: e.content.body,
                    timestamp: e.header.date
                });
            }, se = (e, l)=>{
                L.value.push({
                    type: l,
                    body: e,
                    timestamp: e.header.date
                });
            }, s = (e)=>{
                console.log("Unhandled message recieved", e);
            }, t = (e)=>{
                c.value = e == "idle" ? "connected" : e;
            }, y = async ()=>{
                await Y.value.session.sendBeakerMessage("reset_request", {});
            };
            return (e, l)=>{
                const w = ce("autoscroll");
                return v(), x(Ve, {
                    title: e.$tmpl._("short_title", "Beaker Notebook"),
                    "title-extra": h.value,
                    "header-nav": oe.value,
                    ref_key: "beakerInterfaceRef",
                    ref: f,
                    connectionSettings: S.config,
                    defaultKernel: "beaker_kernel",
                    sessionId: i(k),
                    renderers: M,
                    savefile: h.value,
                    onIopubMsg: ee,
                    onUnhandledMsg: s,
                    onAnyMsg: se,
                    onSessionStatusChanged: t
                }, {
                    "left-panel": m(()=>[
                            o(ve, {
                                ref_key: "sideMenuRef",
                                ref: $,
                                position: "left",
                                highlight: "line",
                                expanded: !0,
                                initialWidth: "25vi",
                                maximized: _.value
                            }, {
                                default: m(()=>[
                                        o(D, {
                                            id: "files",
                                            label: "Files",
                                            icon: "pi pi-folder",
                                            "no-overflow": "",
                                            lazy: !0
                                        }, {
                                            default: m(()=>[
                                                    o(Ee, {
                                                        ref_key: "filePanelRef",
                                                        ref: r,
                                                        onPreviewFile: l[1] || (l[1] = (C, ie)=>{
                                                            B.value = {
                                                                url: C,
                                                                mimetype: ie
                                                            }, z.value = !0, b.value.selectPanel("file-contents");
                                                        })
                                                    }, null, 512)
                                                ]),
                                            _: 1
                                        }),
                                        o(D, {
                                            id: "integrations",
                                            label: "Integrations",
                                            icon: "pi pi-database"
                                        }, {
                                            default: m(()=>[
                                                    o(Me, {
                                                        modelValue: g.value.integrations,
                                                        "onUpdate:modelValue": l[2] || (l[2] = (C)=>g.value.integrations = C)
                                                    }, null, 8, [
                                                        "modelValue"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        S.config.config_type !== "server" ? (v(), x(D, {
                                            key: 0,
                                            id: "config",
                                            label: `${e.$tmpl._("short_title", "Beaker")} Config`,
                                            icon: "pi pi-cog",
                                            lazy: !0,
                                            position: "bottom"
                                        }, {
                                            default: m(()=>[
                                                    o($e, {
                                                        ref_key: "configPanelRef",
                                                        ref: a,
                                                        onRestartSession: y
                                                    }, null, 512)
                                                ]),
                                            _: 1
                                        }, 8, [
                                            "label"
                                        ])) : R("", !0)
                                    ]),
                                _: 1
                            }, 8, [
                                "maximized"
                            ])
                        ]),
                    "right-panel": m(()=>[
                            o(ve, {
                                ref_key: "rightSideMenuRef",
                                ref: b,
                                position: "right",
                                highlight: "line",
                                expanded: !0,
                                initialWidth: "36vi",
                                maximized: _.value
                            }, {
                                default: m(()=>[
                                        o(D, {
                                            id: "file-contents",
                                            label: "File Contents",
                                            icon: "pi pi-file beaker-zoom",
                                            "no-overflow": ""
                                        }, {
                                            default: m(()=>[
                                                    o(Se, {
                                                        url: B.value?.url,
                                                        mimetype: B.value?.mimetype
                                                    }, null, 8, [
                                                        "url",
                                                        "mimetype"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        o(D, {
                                            id: "examples",
                                            label: "Example Editor",
                                            icon: "pi pi-list-check",
                                            "no-overflow": ""
                                        }, {
                                            default: m(()=>[
                                                    o(Ct, {
                                                        modelValue: g.value,
                                                        "onUpdate:modelValue": l[3] || (l[3] = (C)=>g.value = C),
                                                        disabled: !g.value.selected || g.value.selected === "new",
                                                        deleteResource: Z,
                                                        modifyResource: X
                                                    }, null, 8, [
                                                        "modelValue",
                                                        "disabled"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        o(D, {
                                            id: "kernel-logs",
                                            label: "Logs",
                                            icon: "pi pi-list",
                                            position: "bottom"
                                        }, {
                                            default: m(()=>[
                                                    G(o(Re, {
                                                        entries: p.value,
                                                        onClearLogs: l[4] || (l[4] = (C)=>p.value.splice(0, p.value.length))
                                                    }, null, 8, [
                                                        "entries"
                                                    ]), [
                                                        [
                                                            w
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
                    default: m(()=>[
                            n("div", It, [
                                n("div", Vt, [
                                    o(ut, {
                                        modelValue: g.value,
                                        "onUpdate:modelValue": l[0] || (l[0] = (C)=>g.value = C),
                                        deleteResource: Z,
                                        modifyResource: X,
                                        modifyIntegration: H,
                                        fetchResources: ne
                                    }, null, 8, [
                                        "modelValue"
                                    ])
                                ])
                            ])
                        ]),
                    _: 1
                }, 8, [
                    "title",
                    "title-extra",
                    "header-nav",
                    "connectionSettings",
                    "sessionId",
                    "savefile"
                ]);
            };
        }
    });
});
export { Pt as default, __tla };
