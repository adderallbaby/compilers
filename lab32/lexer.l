%option reentrant noyywrap bison-bridge bison-locations
%option extra-type="struct Extra *"

/* Подавление предупреждений для -Wall */
%option noinput nounput

%{

#include <stdio.h>
#include <stdlib.h>
#include "lexer.h"
#include "parser.tab.h"  /* файл генерируется Bison’ом */

#define YY_USER_ACTION \
  { \
    int i; \
    struct Extra *extra = yyextra; \
    if (! extra->continued ) { \
      yylloc->first_line = extra->cur_line; \
      yylloc->first_column = extra->cur_column; \
    } \
    extra->continued = false; \
    for (i = 0; i < yyleng; ++i) { \
      if (yytext[i] == '\n') { \
        extra->cur_line += 1; \
        extra->cur_column = 1; \
      } else { \
        extra->cur_column += 1; \
      } \
    } \
    yylloc->last_line = extra->cur_line; \
    yylloc->last_column = extra->cur_column; \
  }

void yyerror(YYLTYPE *loc, yyscan_t scanner, long env[26], int i, int tab, bool user_tab, const char *message) {
    printf("Error (%d,%d): %s\n", loc->first_line, loc->first_column, message);
}
%}
DIGIT    [0-9]
LETTER   [a-zA-Z]
IDENT    {LETTER}({LETTER}|{DIGIT})*
NUMBER   {DIGIT}+

%%
[\n\t ]+
\{.*\}  



end return KW_END;
SET return KW_SET;
\; return SEMICOLON;
TYPE return TYPE;
CONST return CONST;
FILE return KW_FILE;
RECORD return KW_RECORD;
OF return KW_OF;
ARRAY return ARRAY;
\^ return ARROW;
\.\. return TWODOTS;
=  return EQUALS;
\+  return '+';
\-  return '-';
\*  return MUL;
\/  return DIV;
\: return COLON;
\( return LEFT_PAREN;
\) return RIGHT_PAREN;
,   return COMMA;
case return KW_CASE;
True return MY_TRUE;
False return MY_FALSE;
\[ return LEFT_BRACKET;
\] return RIGHT_BRACKET;


[0-9]+(\.[0-9]+)? {
    yylval->number = atof(yytext);
    return NUMBER;
}

{IDENT}    {   
                yylval->ident = strdup(yytext); 
                return IDENT; 
            }


%%
void init_scanner(FILE *input, yyscan_t *scanner, struct Extra *extra) {
    extra->continued = false;
    extra->cur_line = 1;
    extra->cur_column = 1;

    yylex_init(scanner);
    yylex_init_extra(extra, scanner);
    yyset_in(input, *scanner);
}

void destroy_scanner(yyscan_t scanner) {
    yylex_destroy(scanner);
}
