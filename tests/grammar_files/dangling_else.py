import viper.lexer as vl
import viper.parser.ast.nodes as ns


tree = ns.FileInput([
    ns.FileStmt(ns.FuncDef(
        vl.Name('func1'),
        [ns.Parameter(
            None,
            vl.Name('x'),
            vl.Class('Int')
        )],
        vl.Class('Int'),
        ns.CompoundStmtBlock([
            ns.IfStmt(
                ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                    ns.OpExpr(None,
                              ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                              [ns.SubOpExpr(vl.Operator('>'),
                                            ns.AtomExpr(ns.NumberAtom(vl.Number('1')), []))],
                              None)
                ])])])),
                ns.CompoundStmtBlock([
                    ns.IfStmt(
                        ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                            ns.OpExpr(None,
                                      ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                                      [ns.SubOpExpr(vl.Operator('>'),
                                                    ns.AtomExpr(ns.NumberAtom(vl.Number('2')), []))],
                                      None)
                        ])])])),
                        ns.CompoundStmtBlock([
                            ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([
                                ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                                    ns.OpExpr(None,
                                              ns.AtomExpr(ns.NumberAtom(vl.Number('9')), []),
                                              [],
                                              None)
                                ])])]))
                            ])))
                        ]),
                        [],
                        None
                    )
                ]),
                [],
                ns.ElseStmt(ns.CompoundStmtBlock([
                    ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([
                        ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                            ns.OpExpr(None,
                                      ns.AtomExpr(ns.NumberAtom(vl.Number('19')), []),
                                      [],
                                      None)
                        ])])]))
                    ])))
                ]))
            )
        ])
    )),
    ns.FileStmt(ns.FuncDef(
        vl.Name('func2'),
        [ns.Parameter(
            None,
            vl.Name('x'),
            vl.Class('Int')
        )],
        vl.Class('Int'),
        ns.CompoundStmtBlock([
            ns.IfStmt(
                ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                    ns.OpExpr(None,
                              ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                              [ns.SubOpExpr(vl.Operator('>'),
                                            ns.AtomExpr(ns.NumberAtom(vl.Number('1')), []))],
                              None)
                ])])])),
                ns.CompoundStmtBlock([
                    ns.IfStmt(
                        ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                            ns.OpExpr(None,
                                      ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                                      [ns.SubOpExpr(vl.Operator('>'),
                                                    ns.AtomExpr(ns.NumberAtom(vl.Number('2')), []))],
                                      None)
                        ])])])),
                        ns.CompoundStmtBlock([
                            ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([
                                ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                                    ns.OpExpr(None,
                                              ns.AtomExpr(ns.NumberAtom(vl.Number('9')), []),
                                              [],
                                              None)
                                ])])]))
                            ])))
                        ]),
                        [],
                        ns.ElseStmt(ns.CompoundStmtBlock([
                            ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([
                                ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                                    ns.OpExpr(None,
                                              ns.AtomExpr(ns.NumberAtom(vl.Number('42')), []),
                                              [],
                                              None)
                                ])])]))
                            ])))
                        ]))
                    )
                ]),
                [],
                None
            )
        ])
    )),
])
