package main

import (
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"
	"go/token"
	"os"
	"strconv"
)

var counter int = 0

func countGoroutines(file *ast.File) {

	ast.Inspect(file, func(n ast.Node) bool {
		if block, ok := n.(*ast.BlockStmt); ok {
			for i := 0; i < len(block.List); i++ {
				if _, ok := block.List[i].(*ast.GoStmt); ok {
					newIncDecStmt := &ast.IncDecStmt{
						X: &ast.Ident{
							Name: "counter",
						},
						Tok: token.INC,
					}
					counter += 1

					block.List = append(block.List, newIncDecStmt)
				}

			}

		}

		return true
	})

	var before []ast.Decl
	var after []ast.Decl
	_ = after
	if len(file.Decls) > 0 {
		hasImport := false
		if genDecl, ok := file.Decls[0].(*ast.GenDecl); ok {
			hasImport = genDecl.Tok == token.IMPORT
		}

		if hasImport {
			before, after = []ast.Decl{file.Decls[0]}, file.Decls[1:]
		} else {
			after = file.Decls
		}
	}

	file.Decls = append(before,
		&ast.GenDecl{
			Tok: token.CONST,
			Specs: []ast.Spec{
				&ast.ValueSpec{
					Names: []*ast.Ident{ast.NewIdent("counter")},
					Type:  ast.NewIdent("string"),
					Values: []ast.Expr{
						&ast.BasicLit{
							Kind:  token.INT,
							Value: "\"" + strconv.Itoa(counter) + "\"",
						},
					},
				},
			},
		},
	)

	fmt.Print(counter)
	fmt.Printf("%s", " times a goroutine was called\n")
	file.Decls = append(file.Decls, after...)

}

func main() {

	if len(os.Args) != 2 {
		fmt.Println("Not enough args")
		return
	}

	fset := token.NewFileSet()
	if file, err := parser.ParseFile(fset, os.Args[1], nil, parser.ParseComments); err == nil {
		countGoroutines(file)

		if format.Node(os.Stdout, fset, file) != nil {
			fmt.Printf("Formatter error: %v\n", err)
		}
	} else {
		fmt.Printf("Errors in %s\n", os.Args[1])
	}
}
