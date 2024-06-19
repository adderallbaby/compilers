import abc
import enum
import re
import sys
import typing
from dataclasses import dataclass
from pprint import pprint

import parser_edsl as pe


class Type(abc.ABC):
    pass


class BasicType(enum.Enum):
    Integer = 'INTEGER'
    Real = 'REAL'
    Boolean = 'BOOLEAN'


@dataclass
class ConstDef:
    name: str
    type: Type


class UserListType(Type):
    name: list[Type]


@dataclass
class TypeDef:
    name: str
    definition: Type or UserListType


class Statement(abc.ABC):
    pass


@dataclass
class UserType(Type):
    name: str


@dataclass
class UserConst(ConstDef):
    name: str
    type: UserType


@dataclass
class UserFieldListRecordType(Type):
    left: str
    right: str


@dataclass
class UserFileType(Type):
    name: str


@dataclass
class UserFieldListType(Type):
    name: str


@dataclass
class UserSetType(Type):
    name: str


@dataclass
@dataclass
class UserArrayType(Type):
    list_itself: UserListType
    list_of: Type


@dataclass
class UserArrowType(Type):
    name: Type


@dataclass
class UserDotsType(Type):
    left: ConstDef
    right: ConstDef
# class UserArrayType(Type):


@dataclass
class Program:
    type_defs: list[TypeDef]

    Const_defs: list[ConstDef]


@dataclass
class RecordField(Type):
    name: str
    type: Type


class Expr(abc.ABC):
    pass


@dataclass
class AssignStatement(Statement):
    Constiable: str
    expr: Expr


@dataclass
class IfStatement(Statement):
    condition: Expr
    then_branch: Statement
    else_branch: Statement


@dataclass
class WhileStatement(Statement):
    condition: Expr
    body: Statement


@dataclass
class ForStatement(Statement):
    Constiable: str
    start: Expr
    end: Expr
    body: Statement


@dataclass
class BlockStatement(Statement):
    body: list[Statement]


@dataclass
class UserSubCaseType(Type):
    left: str
    right: Type


@dataclass
class EmptyStatement(Statement):
    pass


@dataclass
class UserCycleType(Type):
    left: str
    right: Type


@dataclass
class ConstiableExpr(Expr):
    Constname: str


@dataclass
class ConstExpr(Expr):
    value: typing.Any
    type: BasicType or UserType


@dataclass
class BinOpExpr(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class UnOpExpr(Expr):
    op: str
    expr: Expr


@dataclass
class UserCaseType(Type):
    ident: str
    typeIdent: Type


INTEGER = pe.Terminal('INTEGER', '[0-9]+', int, priority=7)
REAL = pe.Terminal(
    'REAL', '[0-9]+(\\.[0-9]*)?(e[-+]?[0-9]+)?', float, priority=6)
CONSTANT = pe.Terminal("CONSTANT",
                       r'((\+|\-|)([0-9]+(\\.[0-9]*)?(e[-+]?[0-9]+)?)|([A-Za-z][A-Za-z0-9]*))|(\'[a-zA-Z])+\'', str.upper)
VARNAME = pe.Terminal('VARNAME', '[A-Za-z][A-Za-z0-9]*', str.upper, priority=6)


# = pe.Terminal("PACKED", "PACKED | ", str.upper)


def make_keyword(image):
    return pe.Terminal(image, image, lambda name: None,
                       re_flags=re.IGNORECASE, priority=10)


KW_Array, KW_File, KW_Record, KW_OF, KW_SET, KW_Const, KW_BEGIN, KW_END, KW_INTEGER, KW_REAL, KW_BOOLEAN, KW_TYPE = \
    map(make_keyword, 'array file record of set const begin end integer real boolean type'.split())


KW_IF, KW_THEN, KW_ELSE, KW_WHILE, KW_DO, KW_FOR, KW_TO = \
    map(make_keyword, 'if then else while do for to'.split())

KW_OR, KW_DIV, KW_MOD, KW_AND, KW_NOT, KW_TRUE, KW_FALSE = \
    map(make_keyword, 'or div mod and not true false'.split())


NProgram, Block, Blocks, NConstDefs, NConstDef, NType, NStatements, NDecl, NTypeDefs, NTypeDef, Identifier, Unsigned_number, Unsigned_constant, Constant_Identifier, Constant, Start_Constant, Middle_Constant, Simple_Type, Identifiers, BigType, PackableType, Start_Packable, End_Packable, Simple_Types, FieldList, Cycle, Constants, Wrapped, Wrapped2, FieldRecord, Starter, \
    Wrapped3, CaseType, Wrapped4 = \
    map(pe.NonTerminal, 'Program Block Blocks ConstDefs ConstDef Type Statements Decl TypeDefs \
        TypeDef Identifier Unsigned_number Unsigned_constant Constant_Identifier Constant '
                        'Start_Constant Middle_Constant SimpleType Identifiers BigType PackableType \
        StartPackable EndPackable '
                        'SimpleTypes FieldList Cycle Constants Wrapped Wrapped2 FieldRecord \
        Starter Wrapped3 CaseType Wrapped4'.split())

NStatement, NExpr, NCmpOp, NArithmExpr, NAddOp = \
    map(pe.NonTerminal, 'Statement Expr CmpOp ArithmOp AddOp'.split())

NTerm, NMulOp, NFactor, NPower, NConst = \
    map(pe.NonTerminal, 'Term MulOp Factor Power Const'.split())


NProgram |= Block, Blocks, Program
Blocks |= Block, Blocks, lambda block, blocks: blocks + [block]
Blocks |= lambda: []
Block |= KW_TYPE, NTypeDefs
Block |= KW_Const, NConstDefs
NTypeDefs |= NTypeDef, NTypeDefs, lambda typedef, typedefs: typedefs + \
    [typedef]
NConstDefs |= lambda: []

NConstDefs |= NConstDef, NConstDefs, lambda constdef, constdefs: constdefs + \
    [constdef]
NTypeDefs |= lambda: []
NTypeDef |= VARNAME, '=', BigType, ';', TypeDef
NConstDef |= VARNAME, "=", NConst, ';', ConstDef
Identifier |= VARNAME
Unsigned_number |= REAL
Unsigned_constant |= Constant_Identifier, ConstDef
Unsigned_constant |= Unsigned_number, ConstDef
Unsigned_constant |= '\'', VARNAME, '\'', ConstDef
Constant |= CONSTANT
Simple_Type |= NType
Simple_Type |= '(', Identifier, Identifiers, ')', lambda ident, idents: idents + \
    [ident]
Simple_Type |= NConst, '..', NConst, UserDotsType
Identifiers |= ',', Identifier, Identifiers, lambda ident, idents: idents + \
    [ident]
Identifiers |= lambda: []
BigType |= Simple_Type
BigType |= PackableType
PackableType |= End_Packable
# Start_Packable |= PACKED

End_Packable |= KW_Array, Wrapped, KW_OF, BigType, UserArrayType
Wrapped |= Simple_Type, Simple_Types, lambda st, sts: sts + [st]
End_Packable |= KW_SET, KW_OF, BigType, UserSetType
End_Packable |= KW_File, KW_OF, BigType, UserFileType
End_Packable |= KW_Record, FieldList, 'end', UserFieldListType
Simple_Types |= ',', Simple_Type, Simple_Types, lambda st, sts: sts + [st]
Simple_Types |= lambda: []
FieldList |= FieldRecord, FieldList, lambda r, l: l + [r]
FieldList |= lambda: []
FieldRecord |= Wrapped2, ":", BigType, ';', lambda l, r: UserFieldListRecordType(
    l, r)
FieldRecord |= Wrapped2, ":", BigType, lambda l, r: UserFieldListRecordType(
    l, r)

Wrapped2 |= Identifier, Identifiers, lambda id, ids: ids + [id]
CaseType |= Identifier, ':', NType, UserCaseType
FieldRecord |= 'case', CaseType, KW_OF,  Wrapped4, UserFieldListRecordType
Wrapped4 |= Starter, Cycle, lambda s, c: c+[s]
Starter |= Wrapped3, ":", '(', FieldList, ')', UserSubCaseType
Wrapped3 |= NConst, Constants, lambda c, cs: cs+[c]
Cycle |= ';', Starter, Cycle, lambda s, c: c + [s]
Cycle |= lambda: []
Constants |= ',', NConst, Constants, lambda c, cs: cs+[c]
Constants |= lambda: []


# , KW_BEGIN, NStatements, KW_END, Program
# ,
# KW_Const, NConstDefs, KW_TYPE, NTypeDefs  -> NDECL

# NDecl |= NDecl, KW_TYPE, NTypeDefs
# NDecl |= NDecl, KW_Const, NConstDefs
# NDecl |= lambda: []
"""
GRAMMAR -> BLOCK BLOCKS .
BLOCKS -> BLOCK BLOCKS | .
BLOCK -> type TYPEDEF | const CONSTDEF .
TYPEDEF -> SINGLETYPE TYPEDEF | .
IDENTIFIER -> LETTER LOD .
LOD -> LETTER | DIGIT | .
UNSIGNED_INT -> DIGIT DIGITS | .
DIGITS -> DIGIT DIGITS | .
UNSIGNED_NUMBER -> UNSIGNED_INT MIDDLE END .
MIDDLE -> DOT DIGIT DIGITS | .
END -> E  AFTERE | .
AFTERE -> plus UNSIGNED_INT | minus UNIGNED_INT .
UNSIGNED_CONSTANT -> CONSTANT_IDENTIFIER | UNSIGNED_NUMBER | NIL | q CHARACTER q .
CONSTANT -> START_CONST MIDDLE_CONST .
START_CONST -> plus | minus | q CHARACTER CHARACTERS q .
CHARACTERS -> CHARACTER CHARACTERS | .
MIDDLE_CONST -> CONSTANT_IDENTIFIER | UNSIGNED_NUMBER .
SIMPLE_TYPE -> TYPE_IDENTIFIER |
              lb IDENTIFIER IDENTIFIERS rb | CONSTANT dd CONSTANT .
IDENTIFIERS -> COMMA IDENTIFIER IDENTIFIERS | .

TYPE -> SIMPLE_TYPE |
arrow TYPE_IDENTIFIER |
PACKABLE | .
PACKABLE -> START_PACKABLE END_PACKABLE .
START_PACKABLE -> packed | .
END_PACKABLE -> array lsb SIMPLE_TYPE SIMPLE_TYPES rsb of TYPE | file of TYPE | set of TYPE | record FIELD_LIST end .
SIMPLE_TYPES -> COMMA SIMPLE_TYPE | .
FIELD_LIST -> IDENTIFIER IDENTIFIERS colon TYPE semicolon FIELD_LIST | case IDENTIFIER colon TYPE_IDENTIFIER of CYCLE .
CYCLE -> CONSTANT CONSTANTS colon lb FIELD_LIST rb CYCLE | .
CONSTANTS -> COMMA CONSTANT CONSTANTS | .
"""
# NIdent |= VARNAME
'''
S -> 'a' A | 'a'
A -> ',' 'a' A | ',' 'a'


'''
# NTypeDef |= VARNAME, '=', KW_RECORD, NAncestorType, NConstsDefs, KW_END, ';', \
#    lambda Constname, ancestorType, ConstsDefs: TypeDef(Constname, ancestorType, ConstsDefs)
NType |= KW_INTEGER, lambda: BasicType.Integer
NType |= KW_REAL, lambda: BasicType.Real
NType |= KW_BOOLEAN, lambda: BasicType.Boolean
NType |= '^', NType, lambda typee: UserArrowType(typee)
# NUserType |= VARNAME, lambda ty: UserType(ty)
NType |= VARNAME, lambda typee: UserType(typee)
NExpr |= NArithmExpr
NExpr |= NArithmExpr, NCmpOp, NArithmExpr, BinOpExpr


def make_op_lambda(op):
    return lambda: op


for op in ('>', '<', '>=', '<=', '=', '<>'):
    NCmpOp |= op, make_op_lambda(op)

NArithmExpr |= NTerm
NArithmExpr |= '+', NTerm, lambda t: UnOpExpr('+', t)
NArithmExpr |= '-', NTerm, lambda t: UnOpExpr('-', t)
NArithmExpr |= NArithmExpr, NAddOp, NTerm, BinOpExpr

NAddOp |= '+', lambda: '+'
NAddOp |= '-', lambda: '-'
NAddOp |= KW_OR, lambda: 'or'

NTerm |= NFactor
NTerm |= NTerm, NMulOp, NFactor, BinOpExpr

NMulOp |= '*', lambda: '*'
NMulOp |= '/', lambda: '/'
NMulOp |= KW_DIV, lambda: 'div'
NMulOp |= KW_MOD, lambda: 'mod'
NMulOp |= KW_AND, lambda: 'and'

NFactor |= NPower
NFactor |= NPower, '**', NFactor, lambda p, f: BinOpExpr(p, '**', f)


NConst |= INTEGER, lambda v: ConstExpr(v, BasicType.Integer)
NConst |= REAL, lambda v: ConstExpr(v, BasicType.Real)
NConst |= KW_TRUE, lambda: ConstExpr(True, BasicType.Boolean)
NConst |= KW_FALSE, lambda: ConstExpr(False, BasicType.Boolean)
NConst |= VARNAME, lambda v: ConstExpr(v, UserType)
p = pe.Parser(NProgram)
assert p.is_lalr_one()
p.add_skipped_domain('\\s')
p.add_skipped_domain('(\\(\\*|\\{).*?(\\*\\)|\\})')


for filename in sys.argv[1:]:
    try:
        with open(filename) as f:
            tree = p.parse(f.read())
            pprint(tree)
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}')
    except Exception as e:
        print(e)
