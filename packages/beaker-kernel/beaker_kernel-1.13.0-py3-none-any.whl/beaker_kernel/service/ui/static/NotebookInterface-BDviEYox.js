import { J as fe, a as pe, L as ve, M as me, T as ke, b as be, w as _e, _ as ye, c as J, d as f, e as ge, f as he, g as Ce, __tla as __tla_0 } from "./DebugPanel.vue_vue_type_style_index_0_lang-PW_f_WLw.js";
import { B as we, _ as xe, a as Ie, b as $e, S as Se, c as Ne, __tla as __tla_1 } from "./BeakerQueryCell.vue_vue_type_style_index_0_lang-Dt4dB8m3.js";
import { a as Re, b as Me, __tla as __tla_2 } from "./index-D-jLGYR3.js";
import { d as X, f as M, y as z, o as v, z as Pe, A as Be, B as j, E as n, G as Ae, u as R, H as Fe, r as s, i as U, g as G, j as w, I as i, J as H, K as D, L as ze, M as Q, n as W, N as De } from "./primevue-1TEWPnDt.js";
import { _ as je, a as Oe, b as Te, __tla as __tla_3 } from "./MediaPanel.vue_vue_type_style_index_0_lang-BO_XdLt2.js";
import { _ as Ke, a as Ee, l as Le, __tla as __tla_4 } from "./IntegrationPanel.vue_vue_type_style_index_0_lang-Dl0CwqlQ.js";
import { _ as Ve, a as qe, b as Je, c as Ue, __tla as __tla_5 } from "./BeakerRawCell.vue_vue_type_style_index_0_lang-DHQ28atJ.js";
import { s as Ge } from "./jupyterlab-C2EV-Dpr.js";
import "./xlsx-Ck9ILNdx.js";
import "./_plugin-vue_export-helper-DlAUqK2U.js";
import "./codemirror-C5EHd1r4.js";
import { __tla as __tla_6 } from "./pdfjs-4lX-eNFD.js";
let dt;
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
    })(),
    (()=>{
        try {
            return __tla_6;
        } catch  {}
    })()
]).then(async ()=>{
    let He, Qe, We, Xe;
    He = {
        class: "kernel-state-panel"
    };
    Qe = X({
        __name: "KernelStatePanel",
        props: {
            data: {}
        },
        setup (P) {
            const l = P, g = M(()=>l?.data?.["x-application/beaker-subkernel-state"]?.["application/json"]), h = M(()=>{
                const x = {
                    ...g.value
                }, k = (r)=>(r.children = r?.children?.map((m)=>k(m)), r.key = r.label, r), p = {};
                for (const [r, m] of Object.entries(x)){
                    if (p[r] = [], Array.isArray(m)) {
                        p[r] = m.map((b)=>({
                                label: b,
                                key: b,
                                children: []
                            }));
                        continue;
                    }
                    for (const [b, I] of Object.entries(m))p[r].push(k(I));
                }
                return p;
            });
            return (x, k)=>(v(), z("div", He, [
                    (v(!0), z(Pe, null, Be(h.value, (p, r)=>(v(), z("div", {
                            key: r
                        }, [
                            j("h4", null, Ae(r), 1),
                            n(R(Fe), {
                                value: p,
                                class: "kernel-state-tree",
                                onNodeSelect: ()=>{}
                            }, null, 8, [
                                "value"
                            ])
                        ]))), 128))
                ]));
        }
    });
    We = {
        class: "notebook-container"
    };
    Xe = {
        class: "welcome-placeholder"
    };
    dt = X({
        __name: "NotebookInterface",
        props: [
            "config",
            "connectionSettings",
            "sessionName",
            "sessionId",
            "defaultKernel",
            "renderers"
        ],
        setup (P) {
            const l = s(), g = s(), h = s(), x = s(), k = s(), p = s(), r = s(), m = s(!1), b = new URLSearchParams(window.location.search), I = b.has("session") ? b.get("session") : "notebook_dev_session", O = P, Y = [
                ...Ge.map((e)=>new be(e)).map(_e),
                fe,
                pe,
                ve,
                me,
                ke
            ], Z = {
                code: Je,
                markdown: qe,
                query: xe,
                raw: Ve
            }, ee = s("connecting"), $ = s([]), te = s([]);
            s();
            const B = s(null), C = s(null), T = s();
            s(!1);
            const _ = s(!1);
            s();
            const { theme: K, toggleDarkMode: le } = U("theme"), S = U("beakerAppConfig");
            S.setPage("notebook");
            const E = s(), L = s(), A = s(), oe = M(()=>{
                const e = [];
                if (!S?.config?.pages || Object.hasOwn(S.config.pages, "chat")) {
                    const t = "/" + (S?.config?.pages?.chat?.default ? "" : "chat") + window.location.search;
                    e.push({
                        type: "link",
                        href: t,
                        icon: "comment",
                        label: "Navigate to chat view"
                    });
                }
                return e.push({
                    type: "button",
                    icon: K.mode === "dark" ? "sun" : "moon",
                    command: le,
                    label: `Switch to ${K.mode === "dark" ? "light" : "dark"} mode.`
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
            }), y = M(()=>g?.value?.beakerSession), N = s({});
            G(y, async ()=>{
                N.value = await Le(I);
            }), G(()=>l?.value?.notebook.cells, (e)=>{
                e?.length === 0 && l.value.insertCellBefore();
            }, {
                deep: !0
            });
            const ne = (e)=>{
                e.header.msg_type === "preview" ? E.value = e.content : e.header.msg_type === "kernel_state_info" ? L.value = e.content : e.header.msg_type === "debug_event" ? $.value.push({
                    type: e.content.event,
                    body: e.content.body,
                    timestamp: e.header.date
                }) : e.header.msg_type === "chat_history" ? (T.value = e.content, console.log(e.content)) : e.header.msg_type === "lint_code_result" && e.content.forEach((t)=>{
                    y.value.findNotebookCellById(t.cell_id).lintAnnotations.push(t);
                });
            }, ae = (e, t)=>{
                te.value.push({
                    type: t,
                    body: e,
                    timestamp: e.header.date
                });
            }, se = (e)=>{
                console.log("Unhandled message recieved", e);
            }, ie = (e)=>{
                ee.value = e == "idle" ? "connected" : e;
            }, re = async ()=>{
                await y.value.session.sendBeakerMessage("reset_request", {});
            }, F = (e, t)=>{
                const a = l.value;
                y.value?.session.loadNotebook(e), C.value = t;
                const d = a.notebook.cells.map((o)=>o.id);
                d.includes(a.selectedCellId) || W(()=>{
                    a.selectCell(d[0]);
                });
            }, ce = async (e)=>{
                C.value = e, e && (k.value?.selectPanel("Files"), await h.value.refresh(), await h.value.flashFile(e));
            }, V = ()=>{
                l.value?.selectPrevCell();
            }, q = ()=>{
                const e = l.value.notebook.cells[l.value.notebook.cells.length - 1];
                l.value.selectedCell().cell.id === e.id ? r.value.$el.querySelector("textarea")?.focus() : l.value?.selectNextCell();
            }, u = {}, de = {
                "keydown.enter.ctrl.prevent.capture.in-cell": ()=>{
                    l.value?.selectedCell().execute(), l.value?.selectedCell().exit();
                },
                "keydown.enter.shift.prevent.capture.in-cell": ()=>{
                    const e = l.value?.selectedCell();
                    e.execute(), l.value?.selectNextCell() || (l.value?.insertCellAfter(e, void 0, !0), W(()=>{
                        l.value?.selectedCell().enter();
                    }));
                },
                "keydown.enter.exact.prevent.stop.!in-editor": ()=>{
                    l.value?.selectedCell().enter();
                },
                "keydown.esc.exact.prevent": ()=>{
                    l.value?.selectedCell().exit();
                },
                "keydown.up.!in-editor.prevent": V,
                "keydown.up.in-editor.capture": (e)=>{
                    const t = e.target, d = t.closest(".beaker-cell")?.getAttribute("cell-id");
                    if (d !== void 0) {
                        const o = y.value.findNotebookCellById(d);
                        if (Me(o.editor)) {
                            const c = l.value.prevCell();
                            c && (o.exit(), l.value.selectCell(c.cell.id, !0, "end"), e.preventDefault(), e.stopImmediatePropagation());
                        }
                    } else t.closest(".agent-query-container") && (t.blur(), l.value.selectCell(l.value.notebook.cells[l.value.notebook.cells.length - 1].id, !0, "end"), e.preventDefault(), e.stopImmediatePropagation());
                },
                "keydown.down.in-editor.capture": (e)=>{
                    const d = e.target.closest(".beaker-cell")?.getAttribute("cell-id");
                    if (d !== void 0) {
                        const o = y.value.findNotebookCellById(d);
                        if (Re(o.editor)) {
                            const c = l.value.nextCell();
                            if (c) o.exit(), l.value.selectCell(c.cell.id, !0, "start"), e.preventDefault(), e.stopImmediatePropagation();
                            else {
                                const ue = l.value.notebook.cells[l.value.notebook.cells.length - 1];
                                l.value.selectedCell().cell.id === ue.id && (o.exit(), r.value.$el.querySelector("textarea")?.focus(), e.preventDefault(), e.stopImmediatePropagation());
                            }
                        }
                    }
                },
                "keydown.k.!in-editor": V,
                "keydown.down.!in-editor.prevent": q,
                "keydown.j.!in-editor": q,
                "keydown.a.prevent.!in-editor": (e)=>{
                    const t = l.value;
                    t?.selectedCell().exit(), t?.insertCellBefore();
                },
                "keydown.b.prevent.!in-editor": ()=>{
                    const e = l.value;
                    e?.selectedCell().exit(), e?.insertCellAfter();
                },
                "keydown.d.!in-editor": ()=>{
                    const e = l.value, t = e.selectedCell(), a = ()=>{
                        delete u.d;
                    };
                    if (u.d === void 0) {
                        const o = setTimeout(a, 1e3);
                        u.d = {
                            cell_id: t.id,
                            timeout: o
                        };
                    } else {
                        const { cell_id: o, timeout: c } = u.d;
                        o === t.id && (e?.removeCell(t), B.value = t.cell, delete u.d), c && window.clearTimeout(c);
                    }
                },
                "keydown.y.!in-editor": ()=>{
                    const t = l.value.selectedCell(), a = ()=>{
                        delete u.y;
                    };
                    if (u.y === void 0) {
                        const o = setTimeout(a, 1e3);
                        u.y = {
                            cell_id: t.id,
                            timeout: o
                        };
                    } else {
                        const { cell_id: o, timeout: c } = u.y;
                        o === t.id && (B.value = t.cell, delete u.y), c && window.clearTimeout(c);
                    }
                },
                "keydown.p.!in-editor": (e)=>{
                    const t = l.value;
                    let a = De(B.value);
                    if (a !== null) {
                        if (t.notebook.cells.map((o)=>o.id).includes(a.id)) {
                            const o = a.constructor, c = {
                                ...a,
                                id: void 0,
                                executionCount: void 0,
                                busy: void 0,
                                last_execution: void 0
                            };
                            a = new o(c);
                        }
                        e.key === "p" ? t?.insertCellAfter(t.selectedCell(), a) : e.key === "P" && t?.insertCellBefore(t.selectedCell(), a), a.value = null;
                    }
                }
            };
            return (e, t)=>{
                const a = H("autoscroll"), d = H("keybindings");
                return v(), w(ye, {
                    title: e.$tmpl._("short_title", "Beaker Notebook"),
                    "title-extra": C.value,
                    "header-nav": oe.value,
                    ref_key: "beakerInterfaceRef",
                    ref: g,
                    connectionSettings: O.config,
                    defaultKernel: "beaker_kernel",
                    sessionId: R(I),
                    renderers: Y,
                    savefile: C.value,
                    onIopubMsg: ne,
                    onUnhandledMsg: se,
                    onAnyMsg: ae,
                    onSessionStatusChanged: ie,
                    onOpenFile: F
                }, {
                    "left-panel": i(()=>[
                            n(J, {
                                ref_key: "sideMenuRef",
                                ref: k,
                                position: "left",
                                highlight: "line",
                                expanded: !0,
                                initialWidth: "25vi",
                                maximized: _.value
                            }, {
                                default: i(()=>[
                                        n(f, {
                                            label: "Context Info",
                                            icon: "pi pi-home"
                                        }, {
                                            default: i(()=>[
                                                    n(Oe)
                                                ]),
                                            _: 1
                                        }),
                                        n(f, {
                                            id: "files",
                                            label: "Files",
                                            icon: "pi pi-folder",
                                            "no-overflow": "",
                                            lazy: !0
                                        }, {
                                            default: i(()=>[
                                                    n(he, {
                                                        ref_key: "filePanelRef",
                                                        ref: h,
                                                        onOpenFile: F,
                                                        onPreviewFile: t[1] || (t[1] = (o, c)=>{
                                                            A.value = {
                                                                url: o,
                                                                mimetype: c
                                                            }, m.value = !0, p.value.selectPanel("file-contents");
                                                        })
                                                    }, null, 512)
                                                ]),
                                            _: 1
                                        }),
                                        n(f, {
                                            icon: "pi pi-comments",
                                            label: "Chat History"
                                        }, {
                                            default: i(()=>[
                                                    n(R(Te), {
                                                        "chat-history": T.value
                                                    }, null, 8, [
                                                        "chat-history"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        Object.keys(N.value).length > 0 ? (v(), w(f, {
                                            key: 0,
                                            id: "integrations",
                                            label: "Integrations",
                                            icon: "pi pi-database"
                                        }, {
                                            default: i(()=>[
                                                    n(Ee, {
                                                        modelValue: N.value,
                                                        "onUpdate:modelValue": t[2] || (t[2] = (o)=>N.value = o)
                                                    }, null, 8, [
                                                        "modelValue"
                                                    ])
                                                ]),
                                            _: 1
                                        })) : Q("", !0),
                                        O.config.config_type !== "server" ? (v(), w(f, {
                                            key: 1,
                                            id: "config",
                                            label: `${e.$tmpl._("short_title", "Beaker")} Config`,
                                            icon: "pi pi-cog",
                                            lazy: !0,
                                            position: "bottom"
                                        }, {
                                            default: i(()=>[
                                                    n(Ce, {
                                                        ref_key: "configPanelRef",
                                                        ref: x,
                                                        onRestartSession: re
                                                    }, null, 512)
                                                ]),
                                            _: 1
                                        }, 8, [
                                            "label"
                                        ])) : Q("", !0)
                                    ]),
                                _: 1
                            }, 8, [
                                "maximized"
                            ])
                        ]),
                    "right-panel": i(()=>[
                            n(J, {
                                ref_key: "rightSideMenuRef",
                                ref: p,
                                position: "right",
                                highlight: "line",
                                expanded: !0,
                                initialWidth: "25vi",
                                maximized: _.value
                            }, {
                                default: i(()=>[
                                        n(f, {
                                            label: "Preview",
                                            icon: "pi pi-eye",
                                            "no-overflow": ""
                                        }, {
                                            default: i(()=>[
                                                    n(Ue, {
                                                        previewData: E.value
                                                    }, null, 8, [
                                                        "previewData"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        n(f, {
                                            id: "file-contents",
                                            label: "File Contents",
                                            icon: "pi pi-file beaker-zoom",
                                            "no-overflow": ""
                                        }, {
                                            default: i(()=>[
                                                    n(Ke, {
                                                        url: A.value?.url,
                                                        mimetype: A.value?.mimetype
                                                    }, null, 8, [
                                                        "url",
                                                        "mimetype"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        n(f, {
                                            id: "media",
                                            label: "Graphs and Images",
                                            icon: "pi pi-chart-bar",
                                            "no-overflow": ""
                                        }, {
                                            default: i(()=>[
                                                    n(je)
                                                ]),
                                            _: 1
                                        }),
                                        n(f, {
                                            id: "kernel-state",
                                            label: "Kernel State",
                                            icon: "pi pi-server",
                                            "no-overflow": ""
                                        }, {
                                            default: i(()=>[
                                                    n(Qe, {
                                                        data: L.value
                                                    }, null, 8, [
                                                        "data"
                                                    ])
                                                ]),
                                            _: 1
                                        }),
                                        n(f, {
                                            id: "kernel-logs",
                                            label: "Logs",
                                            icon: "pi pi-list",
                                            position: "bottom"
                                        }, {
                                            default: i(()=>[
                                                    D(n(ge, {
                                                        entries: $.value,
                                                        onClearLogs: t[3] || (t[3] = (o)=>$.value.splice(0, $.value.length))
                                                    }, null, 8, [
                                                        "entries"
                                                    ]), [
                                                        [
                                                            a
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
                    default: i(()=>[
                            j("div", We, [
                                D((v(), w(we, {
                                    ref_key: "beakerNotebookRef",
                                    ref: l,
                                    "cell-map": Z
                                }, {
                                    default: i(()=>[
                                            n(Ie, {
                                                "default-severity": "",
                                                saveAvailable: !0,
                                                "save-as-filename": C.value,
                                                onNotebookSaved: ce,
                                                onOpenFile: F
                                            }, {
                                                "end-extra": i(()=>[
                                                        n(R(ze), {
                                                            onClick: t[0] || (t[0] = (o)=>{
                                                                _.value = !_.value, g.value.setMaximized(_.value);
                                                            }),
                                                            icon: `pi ${_.value ? "pi-window-minimize" : "pi-window-maximize"}`,
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
                                            D((v(), w($e, {
                                                "selected-cell": l.value?.selectedCellId
                                            }, {
                                                "notebook-background": i(()=>[
                                                        j("div", Xe, [
                                                            n(Se)
                                                        ])
                                                    ]),
                                                _: 1
                                            }, 8, [
                                                "selected-cell"
                                            ])), [
                                                [
                                                    a
                                                ]
                                            ]),
                                            n(Ne, {
                                                ref_key: "agentQueryRef",
                                                ref: r,
                                                class: "agent-query-container"
                                            }, null, 512)
                                        ]),
                                    _: 1
                                })), [
                                    [
                                        d,
                                        de,
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
export { dt as default, __tla };
