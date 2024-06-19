#!/bin/bash
rm -f output.txt
flex lexer.l
bison -d  parser.y
gcc -o lab parser.tab.c lex.yy.c
rm -f lex.yy.c parser.tab.?
./lab input.txt >> output.txt
