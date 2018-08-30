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
                ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotNegatedTestExpr(
                    ns.OpExpr(None,
                              ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                              [ns.SubOpExpr(vl.Operator('>'),
                                            ns.AtomExpr(ns.IntAtom(vl.Int('1')), []))],
                              None)
                )])])),
                ns.CompoundStmtBlock([
                    ns.IfStmt(
                        ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotNegatedTestExpr(
                            ns.OpExpr(None,
                                      ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                                      [ns.SubOpExpr(vl.Operator('>'),
                                                    ns.AtomExpr(ns.IntAtom(vl.Int('2')), []))],
                                      None)
                        )])])),
                        ns.CompoundStmtBlock([
                            ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([
                                ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotNegatedTestExpr(
                                    ns.OpExpr(None,
                                              ns.AtomExpr(ns.IntAtom(vl.Int('9')), []),
                                              [],
                                              None)
                                )])]))
                            ])))
                        ]),
                        [],
                        None
                    )
                ]),
                [],
                ns.ElseStmt(ns.CompoundStmtBlock([
                    ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([
                        ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotNegatedTestExpr(
                            ns.OpExpr(None,
                                      ns.AtomExpr(ns.IntAtom(vl.Int('19')), []),
                                      [],
                                      None)
                        )])]))
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
                ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotNegatedTestExpr(
                    ns.OpExpr(None,
                              ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                              [ns.SubOpExpr(vl.Operator('>'),
                                            ns.AtomExpr(ns.IntAtom(vl.Int('1')), []))],
                              None)
                )])])),
                ns.CompoundStmtBlock([
                    ns.IfStmt(
                        ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotNegatedTestExpr(
                            ns.OpExpr(None,
                                      ns.AtomExpr(ns.NameAtom(vl.Name('x')), []),
                                      [ns.SubOpExpr(vl.Operator('>'),
                                                    ns.AtomExpr(ns.IntAtom(vl.Int('2')), []))],
                                      None)
                        )])])),
                        ns.CompoundStmtBlock([
                            ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([
                                ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotNegatedTestExpr(
                                    ns.OpExpr(None,
                                              ns.AtomExpr(ns.IntAtom(vl.Int('9')), []),
                                              [],
                                              None)
                                )])]))
                            ])))
                        ]),
                        [],
                        ns.ElseStmt(ns.CompoundStmtBlock([
                            ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([
                                ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotNegatedTestExpr(
                                    ns.OpExpr(None,
                                              ns.AtomExpr(ns.IntAtom(vl.Int('42')), []),
                                              [],
                                              None)
                                )])]))
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
