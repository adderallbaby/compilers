import java.util.*;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class Lexer {
  public static void main(String[] args) {
    try {

      BufferedReader reader =

          new BufferedReader(new FileReader("input.txt"));
      StringBuilder text = new StringBuilder();
      String line;

      while ((line = reader.readLine()) != null) {
        text.append(line).append("\n");
      }
      reader.close();

      Compiler Compiler = new Compiler(text.toString());
      System.out.println(Compiler.nameCodes);
      Token token;
      do {
        token = Compiler.nextToken();
        System.out.println(token);
      } while (!(token instanceof SpecToken));

    } catch (IOException e) {
      e.printStackTrace();
    }
  }
}

class Position implements Cloneable {
  int line;
  int pos;
  int index;
  String program;

  @Override
  public Position clone() {
    try {
      Position cloned = (Position) super.clone();
      return cloned;
    } catch (CloneNotSupportedException e) {
      throw new RuntimeException(e);
    }
  }

  public Position(String program) {
    this.line = 1;
    this.pos = 1;
    this.index = 0;
    this.program = program;
  }

  public char getChar() {
    return this.program.charAt(this.index);
  }

  @Override
  public String toString() {
    return '(' + String.valueOf(this.line) + ", " + String.valueOf(this.pos) + ')';
  }

  public boolean isNewLine() {
    if (this.index == '\r' && this.index + 1 < this.program.length()) {
      return this.program.charAt(index + 1) == '\n';
    }
    return this.program.charAt(index) == '\n';
  }

  public boolean isDigit() {
    return Character.isDigit(this.program.charAt(this.index)) ||
        ('a' <= Character.toLowerCase(this.program.charAt(this.index)) &&
            Character.toLowerCase(this.program.charAt(this.index)) <= 'h');

  }

  public boolean isDecimalDigit() {
    return Character.isDigit(program.charAt(index));
  }

  public boolean isLetter() {
    return Character.isLetter(program.charAt(index));
  }

  public boolean isSpace() {
    return Character.isWhitespace(program.charAt(index));
  }

  public void next() {
    if (this.index != this.program.length()) {
      if (isNewLine()) {
        if (this.program.charAt(this.index) == '\r') {
          this.index++;
        }
        this.line++;
        this.pos = 1;
      } else {
        this.pos++;
      }
      this.index++;
    }
  }

  public void skipSpaces() {
    while (isSpace()) {
      this.next();
    }
  }

  public void raiseError() {
    System.out.println("SYNTAX ERROR: " + this.toString());
    while (!isSpace() && !isNewLine()) {
      next();
      if (isNewLine()) {
        this.next();
      }
    }
    this.skipSpaces();
  }
}

class Fragment {
  Position start;
  Position following;

  public Fragment(Position start, Position following) {
    this.start = start;
    this.following = following;
  }

  @Override
  public String toString() {
    return this.start.toString() + "-" + this.following.toString();
  }
}

enum DomainTag {
  IDENT(0),
  NUMBER(1),
  KEY(2),
  END_OF_PROGRAM(3);

  private final int value;

  DomainTag(int value) {
    this.value = value;
  }

  public int getValue() {
    return value;
  }
}

abstract class Token {
  public DomainTag tag;
  public Fragment coords;

  public Token(DomainTag tag, Position start, Position following) {
    this.tag = tag;
    this.coords = new Fragment(start, following);
  }

}

class IdentToken extends Token {
  private int code;

  public IdentToken(int code, Position start, Position follow) {
    super(DomainTag.IDENT, start, follow);
    this.code = code;
  }

  @Override
  public String toString() {
    return "IDENT " + this.coords.toString() + ": " + code;
  }
}

class NumberToken extends Token {
  private int value;

  public NumberToken(int value, Position start, Position follow) {
    super(DomainTag.NUMBER, start, follow);
    this.value = value;
  }

  @Override
  public String toString() {
    return "NUMBER " + this.coords.toString() + ": " + value;
  }
}

class KeyToken extends Token {
  private String word;

  public KeyToken(String word, Position start, Position follow) {
    super(DomainTag.KEY, start, follow);
    this.word = word;
  }

  @Override
  public String toString() {
    return "KEY " + this.coords.toString() + ": " + word;
  }
}

class SpecToken extends Token {
  public SpecToken(DomainTag tag, Position start, Position follow) {
    super(tag, start, follow);
  }

  @Override
  public String toString() {
    return "END TOKEN " + this.coords.toString();
  }
}

class Compiler {
  HashMap<String, Integer> nameCodes;
  Position pos;

  public Compiler(String inputText) {
    this.nameCodes = new HashMap<>();
    inputText += " " + (char) 0;
    this.pos = new Position(inputText);
  }

  public int addName(String name) {
    if (this.nameCodes.containsKey(name)) {
      return this.nameCodes.get(name);
    } else {
      int code = this.nameCodes.size();
      this.nameCodes.put(name, code);
      return code;
    }
  }

  public void printDict() {
    ArrayList<Integer> list = new ArrayList<>();
    LinkedHashMap<String, Integer> sortedMap = new LinkedHashMap<>();

    for (Map.Entry<String, Integer> entry : this.nameCodes.entrySet()) {
      list.add(entry.getValue());
    }
    Collections.sort(list, (Comparator<Integer>) (str, str1) -> (str).compareTo(str1));
    for (Integer str : list) {
      for (Map.Entry<String, Integer> entry : this.nameCodes.entrySet()) {
        if (entry.getValue().equals(str)) {
          sortedMap.put(entry.getKey(), str);
        }
      }
    }
    System.out.println(sortedMap);
  }

  public NumberToken getNumber() {
    StringBuilder numberString = new StringBuilder();
    Position start = pos.clone();
    int value = 0;
    Position cur = this.pos;
    while (!this.pos.isSpace()) {
      if (!this.pos.isDigit()) {
        this.pos.raiseError();
        return null;
      }
      numberString.append(this.pos.getChar());
      cur = this.pos;
      this.pos.next();
    }
    if (numberString.charAt(numberString.length() - 1) == 'h') {
      numberString = new StringBuilder(numberString.substring(0, numberString.length() - 1));
      value = Integer.parseInt(numberString.toString().toLowerCase(), 16);
    } else {
      value = Integer.parseInt(numberString.toString());
    }
    return new NumberToken(value, start, cur);
  }

  public Token getIdent() {
    StringBuilder ident = new StringBuilder();
    Position start = pos.clone();
    int value = 0;
    Position cur = this.pos;
    while (!this.pos.isSpace()) {
      if ((!this.pos.isLetter()) && (!this.pos.isDigit())) {

        this.pos.raiseError();
        return null;
      }

      ident.append(this.pos.getChar());
      cur = this.pos;
      this.pos.next();
    }
    if (ident.toString().equals("mov") || ident.toString().equals("eax")) {
      return new KeyToken(ident.toString(), start, cur);
    }
    if (Character.isLetter(ident.toString().charAt(0))) {
      return new IdentToken(addName(ident.toString()), start, cur);
    }

    else {
      ident = new StringBuilder(ident.toString().toLowerCase());
      for (int i = 0; i < ident.length(); i++) {
        char current = ident.charAt(i);
        if (!(Character.isDigit(current) || (current >= 'a' && current <= 'f'))) {
          this.pos.raiseError();
          return null;
        }

      }
      int val = Integer.parseInt(ident.toString(), 16);
      return new NumberToken(val, start, cur);

    }
  }

  public Token nextToken() {
    this.pos.skipSpaces();
    if (this.pos.getChar() == (char) 0) {
      return new SpecToken(DomainTag.END_OF_PROGRAM, this.pos, this.pos);
    }
    if (!(this.pos.isDigit() || this.pos.isLetter())) {
      this.pos.raiseError();
      return this.nextToken();
    }
    if (this.pos.isDecimalDigit()) {
      Token token = this.getNumber();
      if (token != null) {
        return token;
      } else {
        return this.nextToken();
      }

    } else {
      Token token = this.getIdent();
      if (!(token == null)) {
        return token;
      } else {
        return this.nextToken();
      }
    }

  }
}
