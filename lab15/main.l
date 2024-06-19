%option noyywrap bison-bridge bison-locations
%{
    #include <stdio.h>
    #include <stdlib.h>
	
  #define TAG_NUMBER 1
	#define TAG_OP 2
	#define TAG_COMMENT 3
	#define T_EOF 0
	#define MAX_STR_CONST 200

	

    char *tag_names[] = {
		"END_OF_PROGRAM", "NUMBER", "OP", "COMMENT"
    };


    typedef struct Position Position;
    struct Position {
        int line, pos, index;
    };

    void print_pos(Position *p) {
        printf("(%d,%d)",p->line,p->pos);
    }

    struct Fragment {
        Position starting, following;
    };
	
    typedef struct Fragment YYLTYPE;
    typedef struct Fragment Fragment;
	
    void print_frag(Fragment* f) {
    	print_pos(&(f->starting));
    	printf("-");
    	print_pos(&(f->following));
    } 
    
	
	union Token {
		//unsigned long num; 
    int num;
    //number_token;
		char op_token;
		char *comment_token;
	};

    typedef union Token YYSTYPE;
	
    int continued;
    struct Position cur;
	
    #define YY_USER_ACTION {             \
        int i;                           \
        if (!continued)                  \
            yylloc->starting = cur;      \
        continued = 0;                   \
        for ( i = 0; i < yyleng; i++){   \
            if ( yytext[i] == '\n'){     \
                cur.line++;              \
                cur.pos = 1;             \
            }                            \
            else                         \
                cur.pos++;               \
            cur.index++;                 \
        }                                \
        yylloc->following = cur;         \
    } 
	

    void init_scanner (const char *path){
        continued = 0;
        cur.line = 1;
        cur.pos = 1;
        cur.index = 0;

		    yyin = fopen(path, "r");
    }

    void err(char *msg, char *lexem) {
    printf("Error");
    print_pos(&cur);
    printf(": %s %s\n", msg, lexem);
}


    typedef struct{
        int size;
        char** names;
    } commentTable;
 
    void create_comment_table(commentTable * t){
        t->size = 0;
        t->names = NULL;
    }
 
    int add_comment(commentTable* table, char* name){
        for (int i = 0; i < table->size; i++){
            if (strcmp(name, table->names[i]) == 0){
                return i;
            }
        }
 
        table->size++;
        if (table->size == 1){
            table->names = (char**)malloc(sizeof(char*) * (table->size));
        }
        else {
            table->names = (char**)realloc(table->names, sizeof(char*) * (table->size));
        }
        table->names[table->size - 1] = (char*)malloc(sizeof(char)*strlen(name));
        strcpy(table->names[table->size - 1], name);
        return table->size-1;
    }
 
    commentTable table;


	

%}

%option noyywrap

NUMBER 0|[1-9][0-9]*
OPERATION [+\-\*/\(\)]
COMMENT (\(\*\n*.*\n*\*\))
SPACE [ \t\n]*
 		

%%														
{NUMBER} {

    //printf("%d", yytext);
    yylval->num =atoi(yytext);
//strtoul(yytext, NULL, 10); 
    return TAG_NUMBER;
}

{OPERATION} {
    	yylval->op_token = yytext[0];

//print_pos(&cur);
return TAG_OP;
}

{COMMENT}	{ 
    add_comment(&table, yytext);
//return TAG_COMMENT;
}															
{SPACE}	{}											

. err("error", yytext);


%%
int main(int argc,
    const char ** argv) {
    int tag;
    YYSTYPE value;
    YYLTYPE coords;

    create_comment_table( & table);
    init_scanner(argv[1]);
    do {
        tag = yylex( & value, & coords);
        if (tag == 0)
            break;

        print_frag( & coords);
        printf(" %s", tag_names[tag]);
        if (tag == TAG_NUMBER) {
            printf(": %d\n", value.num);
        }
        if (tag == TAG_OP) {
            printf(": %c\n", value.op_token);
        }

    } while (tag != 0);
    printf("Comments here\n");
    for (int i = 0; i < table.size; i++) {
        printf("%s\n", table.names[i]);
    }
      free(table.names);

    return 0;
}
