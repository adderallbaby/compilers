#!bin/bash
flex main.l
gcc -Wall lex.yy.c
./a.out input.txt
