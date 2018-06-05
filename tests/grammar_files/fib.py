import viper.lexer as vl
import viper.parser.ast.nodes as ns


tree = ns.FileInput([
    ns.FileStmt(ns.FuncDef(
        vl.Name('fib'),
        [ns.Parameter(None,
                      vl.Name('n'),
                      vl.Class('Int'))],
        vl.Class('Int'),
        ns.CompoundStmtBlock([
            ns.IfStmt(
                ns.TestExpr(ns.OrTestExpr([
                    ns.AndTestExpr([ns.NotTestExpr([
                        ns.OpExpr(None,
                                  ns.AtomExpr(ns.NameAtom(vl.Name('n')), []),
                                  [ns.SubOpExpr(vl.Operator('=='),
                                                ns.AtomExpr(ns.NumberAtom(vl.Number('1')), []))],
                                  None)])]),
                    ns.AndTestExpr([ns.NotTestExpr([
                        ns.OpExpr(None,
                                  ns.AtomExpr(ns.NameAtom(vl.Name('n')), []),
                                  [ns.SubOpExpr(vl.Operator('=='),
                                                ns.AtomExpr(ns.NumberAtom(vl.Number('2')), []))],
                                  None)])])])),
                ns.CompoundStmtBlock([ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([
                    ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                        ns.OpExpr(None,
                                  ns.AtomExpr(ns.NumberAtom(vl.Number('1')), []),
                                  [],
                                  None)])])]))])))]),
                [],
                None
            ),
            ns.SimpleStmt(ns.ReturnStmt(ns.TestExprList([
                ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                    ns.OpExpr(None,
                              ns.AtomExpr(ns.NameAtom(vl.Name('fib')), [
                                  ns.Call([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                                      ns.OpExpr(None,
                                                ns.AtomExpr(ns.NameAtom(vl.Name('n')), []),
                                                [ns.SubOpExpr(vl.Operator('-'),
                                                              ns.AtomExpr(ns.NumberAtom(vl.Number('1')), []))],
                                                None)])])]))])]),
                              [ns.SubOpExpr(vl.Operator('+'),
                                            ns.AtomExpr(ns.NameAtom(vl.Name('fib')), [
                                                ns.Call([ns.TestExpr(ns.OrTestExpr([ns.AndTestExpr([ns.NotTestExpr([
                                                    ns.OpExpr(None,
                                                              ns.AtomExpr(ns.NameAtom(vl.Name('n')), []),
                                                              [ns.SubOpExpr(vl.Operator('-'),
                                                                            ns.AtomExpr(ns.NumberAtom(vl.Number('2')),
                                                                                        []))],
                                                              None)])])]))])]))],
                              None)
                ])])]))
            ])))
        ])
    ))
])
