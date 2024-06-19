# Индивидуальный вариант 
Объявления типов и констант в Паскале:

В `record`’е точка с запятой  _разделяет_  поля и после  `case` 
 дополнительный  `end`  не ставится. 
 См. https://bernd-oppolzer.de/PascalReport.pdf, третья с конца страница.
```
Type
  Coords = Record x, y: INTEGER end;
Const
  MaxPoints = 100;
type
  CoordsVector = array 1..MaxPoints of Coords;

(* графический и текстовый дисплеи *)
const
  Heigh = 480;
  Width = 640;
  Lines = 24;
  Columns = 80;
type
  BaseColor = (red, green, blue, highlited);
  Color = set of BaseColor;
  GraphicScreen = array 1..Heigh of array 1..Width of Color;
  TextScreen = array 1..Lines of array 1..Columns of
    record
      Symbol : CHAR;
      SymColor : Color;
      BackColor : Color
    end;

{ определения токенов }
TYPE
  Domain = (Ident, IntNumber, RealNumber);
  Token = record
    fragment : record
      start, following : record
        row, col : INTEGER
      end
    end;
    case tokType : Domain of
      Ident : (
        name : array 1..32 of CHAR
      );
      IntNumber : (
        intval : INTEGER
      );
      RealNumber : (
        realval : REAL
      )
  end;

  Year = 1900..2050;

  List = record
    value : Token;
    next : ^List
  end;
```

# Реализация  

## Абстрактный синтаксис 
Программа состоит из блоков, каждый из которых - объявление типов или констант и начинается со слова 
type и const соответственно.
```
NProgram -> ( Block ) *
Block -> KW_TYPE, ( NTypeDef )+
Block -> KW_Const, ( NConstDef )+
```
После слова type идут объявления типов, каждое из которых имеет вид
присваивания переменной какого-то типа, он может иметь вид простого типа, ссылки, двух констант,
разделенных двумя точками, двух или более типов, заключенных в скобки, массив типов (ARRAY ... OF ...), 
множество типов (SET ... OF...), файл (FILE ... OF ...), или record.
```
NTypeDef -> VARNAME, '=', BigType, ';', TypeDef
Simple_Type -> NType
Simple_Type -> '(', Identifier, (',', Identifier )*, ')'
Simple_Type -> NConst, '..', NConst, UserDotsType
BigType -> Simple_Type
BigType -> PackableType
PackableType -> End_Packable
End_Packable -> KW_Array, Wrapped, KW_OF, BigType
Wrapped -> Simple_Type, Simple_Types
End_Packable -> KW_SET, KW_OF, BigType
End_Packable -> KW_File, KW_OF, BigType
End_Packable -> KW_Record, FieldList, 'end'
Simple_Types -> ',', Simple_Type, Simple_Types
Simple_Types -> lambda: []

```
Record начинается с ключевого слова record, за которым следует структура 
fieldList, содержащая поля, разделенные точкой с запятой. Поля имеют вид перечисление идентификаторов : тип.
Последним полем record'а может быть поле, которое начинается со слова case, за которым следует идентификатор,
точка с запятой, идентификатор типа, ключевое слово OF, затем подполя, разделенные точкой с запятой.
```
FieldList -> FieldRecord, FieldList
FieldList -> 
FieldRecord -> Wrapped2, ":", BigType, ';'
FieldRecord -> Wrapped2, ":", BigType
Wrapped2 -> ( Identifier )+
CaseType -> Identifier, ':', NType
FieldRecord -> 'case', CaseType, KW_OF,  Wrapped4
Wrapped4 -> Starter, Cycle
Cycle -> (';', Starter )*
Constants -> (',', NConst )*
```
Подполя имеют вид перечиление констант : ( fieldList ). После слова const идут объявления констант, каждое
из которых имеет вид имя = значение. 
```
Starter -> Wrapped3, ":", '(', FieldList, ')'
Wrapped3 -> NConst, Constants
```

## Лексическая структура и конкретный синтаксис 
Лексическая структура
```
INTEGER ='[0-9]+'
REAL = '[0-9]+(\\.[0-9]*)?(e[-+]?[0-9]+)?'
CONSTANT = '((\+|\-|)([0-9]+(\\.[0-9]*)?(e[-+]?[0-9]+)?)|'([A-Za-z][A-Za-z0-9]*))|(\'[a-zA-Z])+\''
VARNAME = '[A-Za-z][A-Za-z0-9]*'

```
Конкретный синтаксис
```
NProgram |= Block, Blocks, Program
Blocks |= Block, Blocks
Blocks |= 
Block |= KW_TYPE, NTypeDefs
Block |= KW_Const, NConstDefs
NTypeDefs |= NTypeDef, NTypeDefs
NConstDefs |= 
NConstDefs |= NConstDef, NConstDefs
NTypeDefs |= 
NTypeDef |= VARNAME, '=', BigType, ';', TypeDef
NConstDef |= VARNAME, "=", NConst, ';', ConstDef
Identifier |= VARNAME
Unsigned_number |= REAL
Unsigned_constant |= Constant_Identifier, ConstDef
Unsigned_constant |= Unsigned_number, ConstDef
Unsigned_constant |= '\'', VARNAME, '\'', ConstDef
Constant |= CONSTANT
Simple_Type |= NType
Simple_Type |= '(', Identifier, Identifiers, ')'
Simple_Type |= NConst, '..', NConst
Identifiers |= ',', Identifier, Identifiers
Identifiers |= 
BigType |= Simple_Type
BigType |= PackableType
PackableType |= End_Packable
End_Packable |= KW_Array, Wrapped, KW_OF, BigType 
Wrapped |= Simple_Type, Simple_Types
End_Packable |= KW_SET, KW_OF, BigType 
End_Packable |= KW_File, KW_OF, BigType, 
End_Packable |= KW_Record, FieldList, 'end'
Simple_Types |= ',', Simple_Type, Simple_Types
Simple_Types |= lambda: []
FieldList |= FieldRecord, FieldList
FieldList |= 
FieldRecord |= Wrapped2, ":", BigType, ';'
FieldRecord |= Wrapped2, ":", BigType
Wrapped2 |= Identifier, Identifiers
CaseType |= Identifier, ':', NType
FieldRecord |= 'case', CaseType, KW_OF,  Wrapped4
Wrapped4 |= Starter, Cycle
Starter |= Wrapped3, ":", '(', FieldList, ')'
Wrapped3 |= NConst, Constants
Cycle |= ';', Starter, Cycle
Cycle |= 
Constants |= ',', NConst, Constants
Constants |= 
```

