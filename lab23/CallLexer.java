import java.util.*;
import java.util.regex.*;

class Token {
    String tokenType;
    String tokenValue;
    int line;
    int position;

    public Token(String tokenType, String value, int line, int position) {
        this.tokenType = tokenType;
        this.tokenValue = value;
        this.line = line;
        this.position = position;
    }

    @Override
    public String toString() {
        return tokenType + " " + tokenValue;
    }
}

class Lexer {
    String text;
    int line = 1;
    int position = 1;
    List<Token> tokens = new ArrayList<>();
    Map<String, String> rules = new HashMap<>();

    public Lexer(String text) {
        this.text = text;
        rules.put("NAME", "<[^<>]+>");
        rules.put("IS", "is");
        rules.put("tokens", "tokens");
        rules.put("START", "start");
        rules.put("DOT", "[.]");
        rules.put("COMMA", ",");
        rules.put("END", "\\$");
        rules.put("SPACE", "\\s+");
        rules.put("COMMENT", "<--!.*-->");
    }

    public Iterator<Token> tokenize() {
        String[] lines = text.split("\n");
        for (int i = 0; i < lines.length; i++) {
            position = 1;
            line = i + 1;
            while (position < lines[i].length() + 1) {
                for (Map.Entry<String, String> entry : rules.entrySet()) {
                    Matcher matcher = Pattern.compile(entry.getValue()).matcher(lines[i].substring(position - 1));
                    if (matcher.lookingAt()) {
                        if (!entry.getKey().equals("SPACE") && !entry.getKey().equals("COMMENT")) {
                            String value = matcher.group();
                            tokens.add(new Token(entry.getKey(), value, line, position));
                        }
                        position += matcher.end();
                        break;
                    }
                }
            }
        }
        return tokens.iterator();
    }
}

public class CallLexer {
    public static void main(String[] args) {
        try {
            String text = ""; 
            Lexer lexer = new Lexer(text + "$");
            for (Iterator<Token> it = lexer.tokenize(); it.hasNext();) {
                Token token = it.next();
                System.out.println(token.tokenType + " " + token.tokenValue);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
