%{
#include <stdio.h>
#include "lexer.h"
%}

%define api.pure
%locations

%lex-param {yyscan_t scanner}  /* параметр для yylex() */
/* параметры для yyparse() */
%parse-param {yyscan_t scanner}
%parse-param {long env[26]}
%parse-param {int tab}
%parse-param {bool user_tab}

%union {
    double number;
    char* string;
    char* ident;
    char* comment;
}

%left '+' '-'
%left MUL DIV
%token LEFT_PAREN RIGHT_PAREN COMMA END SUB BYVAL AS DIM ASSIGN MY_TRUE MY_FALSE ENTER
%token IF FOR TO NEXT THEN ELSE MY_RETURN MY_EXIT GREATER_THAN CONST TYPE KW_END KW_OF 
%token ARRAY KW_SET SEMICOLON COLON EQUALS TWODOTS KW_FILE KW_RECORD KW_CASE ARROW
%token LEFT_BRACKET RIGHT_BRACKET 
%token <number> NUMBER
%token <comment> COMMENT
%token <ident> IDENT


%{
int yylex(YYSTYPE *yylval_param, YYLTYPE *yylloc_param, yyscan_t scanner);
void yyerror(YYLTYPE *loc, yyscan_t scanner, long env[26], int tab, bool user_tab, const char *message);
%}

%{
void print_tabs(int tab) {
    for(int i = 0; i < tab; i++) {
        printf("  ");
    }
}


%}

%%
Program:
        Block Program
        |
        
 
Block:
        TYPE{printf("type\n"); tab =1 ; } Typedef Typedefs
        | CONST{printf("const\n"); tab = 1;} Constdef Constdefs
        ;
LB: 
        LEFT_BRACKET{printf("[");}
        | {printf("[");}

        ;
RB: 
        RIGHT_BRACKET{printf("]");}
        |{printf("]");}
  
        ;
Typedefs:
        Typedef Typedefs
        | 
        ;
Typedef:
        IDENT[L]{print_tabs(tab);printf("%s ", $L);}  EQUALS {printf("= ");user_tab=false;}  BigType SEMICOLON {printf(";\n");}
        ;

Constdefs:
        Constdef Constdefs
        |
        ;
Constdef:
        IDENT[L]{print_tabs(tab);printf("%s ", $L);}  EQUALS{printf("= ");}   Expr SEMICOLON {printf(";\n");} 
        ;
SimpleType:
        LEFT_PAREN{printf("(");}   IDENT[L]{printf("%s", $L);}   Identifiers RIGHT_PAREN {printf(")");} 
        | Expr TWODOTS {printf("..");}  Expr
        | IDENT[R] {printf("%s", $R);}
        ;
Identifiers:
        COMMA{printf(", ");} IDENT[L]{printf("%s", $L);} Identifiers
        |
        ;
BigType:
        SimpleType
        | PackableType
        | ARROW{printf("^");} IDENT[L]{printf("%s", $L);}
        ;
PackableType: 
        ARRAY{printf("ARRAY ");}  LB Wrapped RB KW_OF {printf(" OF ");} BigType
        | KW_SET {printf("SET");} KW_OF {printf(" OF ");} BigType
        | KW_FILE  {printf("FILE");}  KW_OF{printf(" OF ");}  BigType 
        | KW_RECORD  {tab += 1;  printf("RECORD\n");user_tab = true;} FieldList KW_END {tab-=1;printf("\n");print_tabs(tab);printf("end");}
        ;
Wrapped:
        SimpleType SimpleTypes
        ;
SimpleTypes:
        COMMA{printf(", ");} SimpleType SimpleTypes
        |
        ;

FieldList:
        FieldRecord FieldList
        |
        ;
FieldRecords:
        SEMICOLON {printf(";\n");} FieldRecord
        |
        ;
FieldRecord:
        {if(user_tab) print_tabs(tab);}AnotherWrapped COLON {printf(": ");} BigType FieldRecords
        | CaseType
        ;
CaseType:
        KW_CASE {print_tabs(tab); printf("case ");} IDENT[L] {printf("%s ", $L);} COLON {printf(": ");} IDENT[R] {printf("%s ", $R);} KW_OF         {printf("OF\n");} FourthWrapped
        ;

FourthWrapped:
        {tab+=1;print_tabs(tab);}IDENT[L]{printf("%s", $L);} Identifiers COLON {printf(":");}  LEFT_PAREN {printf("(\n");tab+=1;}FieldList          RIGHT_PAREN {tab -=1;printf("\n");print_tabs(tab);printf(")");tab-=1;}Cycle
        ;

Cycle:
        SEMICOLON {printf(";\n");}  FourthWrapped   
        | 
        ;
AnotherWrapped:
        IDENT[L] {printf("%s", $L);}  Identifiers
        ;


Expr:
        IDENT {printf("%s", $1);}
        | Literal
        | Expr '+' { printf(" + "); } Expr  
        | Expr '-' { printf(" - "); } Expr  
        | Expr MUL { printf(" * "); } Expr 
        | Expr DIV { printf(" / "); } Expr
        ;
Literal:
        NUMBER {printf("%ld", $1);}

        ;
           



%%



int main(int argc, char *argv[]) {
    FILE *input = 0;
    long env[26] = { 0 };
    int tab = 0;
    bool user_tab = false;
    yyscan_t scanner;
    struct Extra extra;

    if (argc > 1) {
        input = fopen(argv[1], "r");
    } else {
        printf("No file in command line, use stdin\n");
        input = stdin;
    }

    init_scanner(input, &scanner, &extra);
    yyparse(scanner, env, tab, user_tab);
    destroy_scanner(scanner);

    if (input != stdin) {
        fclose(input);
    }

    return 0;
}
