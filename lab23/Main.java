import java.io.*;
import java.util.*;
import java.util.regex.*;

class TreeNode {
    static int num = 0;
    int instanceValue = 0;
//String content;
    Token content;
    List<TreeNode> children = new ArrayList<>();

    public TreeNode(Token content) {
        TreeNode.num++;
        this.instanceValue = TreeNode.num;
        this.content = content;
    }

    public void replaceName(String name) {
    Map<String, String> rules = new HashMap<>();
        rules.put("NAME", "<[^<>]+>");
        rules.put("IS", "is");
        rules.put("tokens", "tokens");
        rules.put("START", "start");
        rules.put("DOT", "[.]");
        rules.put("COMMA", ",");
        rules.put("END", "\\$");
        rules.put("SPACE", "\\s+");

        for (TreeNode child : children) {
            if (child.content.tokenValue.equals("NAME")) {
                child.content.tokenValue = name;
                break;
            }else if(rules.containsKey(child.content.tokenValue)){
//System.out.println(child.content.tokenValue + " content");
              child.content.tokenValue = rules.get(child.content.tokenValue);
              break;
            }
        }
    }

    public void addChild(TreeNode child) {
        children.add(child);
    }

    @Override
    public String toString() {
        return String.valueOf(content);
    }

    public void printGraph(FileWriter f) throws IOException {
        f.write(String.format("%d [label = \"%s\"]\n", instanceValue, String.valueOf(content.tokenValue)));
        for (TreeNode child : children) {
            f.write(String.format("%d -> %d\n", instanceValue, child.instanceValue));
        }
        for (TreeNode child : children) {
            child.printGraph(f);
        }
    }
}

class Predicter {
    String GRAMMAR = "GRAMMAR";
    String UNITS = "UNITS";
    String UNIT = "UNIT";
    String TOKENS = "TOKENS";
    String TERMS = "TERMS";
    String RULES = "RULES";
    String RULE = "RULE";
    String NAMES = "NAMES";
    String AXIOM = "AXIOM";

    String tokenss = "tokens";
    String start = "START";
    String is_t = "IS";
    String DOT = "DOT";
    String COMMA = "COMMA";
    String NAME = "NAME";
    String END = "END";
//Token eps = ""
    List<TreeNode> magazine = new ArrayList<>();
    List<String> terminals = Arrays.asList(tokenss, start, is_t, DOT, COMMA, NAME);
    List<String> nonterminals = Arrays.asList(GRAMMAR, UNIT, UNITS, TOKENS, TERMS, RULES, RULE, NAMES, AXIOM);
    Iterator<Token> tokens;
    Map<List<String>, List<String>> table = new HashMap<>();

    public Predicter(Iterator<Token> tokenIterator) {
        this.tokens = tokenIterator;
        table.put(Arrays.asList(GRAMMAR, tokenss), Arrays.asList(UNIT, UNITS, AXIOM));
        table.put(Arrays.asList(UNITS, tokenss), Arrays.asList(UNIT, UNITS));
        table.put(Arrays.asList(UNIT, tokenss), Arrays.asList(TOKENS, RULE, RULES));
        table.put(Arrays.asList(TOKENS, tokenss), Arrays.asList(tokenss, NAME, TERMS));
        table.put(Arrays.asList(RULES, tokenss), new ArrayList<>());
        table.put(Arrays.asList(RULES, NAME), Arrays.asList(RULE, RULES));
        table.put(Arrays.asList(RULE, NAME), Arrays.asList(NAME, is_t, NAMES, DOT));
        table.put(Arrays.asList(NAMES, NAME), Arrays.asList(NAME, NAMES));
        table.put(Arrays.asList(UNITS, start), new ArrayList<>());
        table.put(Arrays.asList(RULES, start), new ArrayList<>());
        table.put(Arrays.asList(AXIOM, start), Arrays.asList(start, NAME, DOT, END));
        table.put(Arrays.asList(TERMS, DOT), Arrays.asList(DOT));
        table.put(Arrays.asList(NAMES, DOT), new ArrayList<>());
        table.put(Arrays.asList(TERMS, COMMA), Arrays.asList(COMMA, NAME, TERMS));
    }

    public TreeNode topDownParse() {

        TreeNode endNode = new TreeNode(new Token("END", "end", 0, 0));
        this.magazine.add(endNode);
        TreeNode root = new TreeNode(new Token("GRAMMAR", "GRAMMAR", 0, 0));
        this.magazine.add(root);
        Token a = tokens.next();
        List<String> result = new ArrayList<>();
        TreeNode curX = null;
        Map<String, String> rules = new HashMap<>();
        //rules.put("NAME", "<[^<>]+>");
        rules.put("IS", "is");
        rules.put("tokens", "tokens");
        rules.put("START", "start");
        rules.put("DOT", "[.]"); 
        rules.put("COMMA", ",");
        rules.put("END", "\\$");
        rules.put("SPACE", "\\s+");


        while (true) {
            TreeNode x = this.magazine.get(this.magazine.size() - 1);
            if (x.content.tokenValue.equals("END")) {
                break;
            }
            //System.out.println(x.content.tokenValue + " " +  a.tokenType);
            if (this.terminals.contains(x.content.tokenValue)) {
                if (x.content.tokenValue.equals(a.tokenType)) {
                    if (a.tokenType.equals("NAME")) {
                        //if(a.tokenValue.equals("<plus sign>")){
                        //  System.out.println("here it is");
                        //}
                        curX.replaceName(a.tokenValue);
                    }else if (rules.containsKey(a.tokenType)){
                                              curX.replaceName(a.tokenValue);}
                    this.magazine.remove(this.magazine.size() - 1);
                    a = tokens.next();
                } else {
                    throw new IllegalArgumentException("Проблема с токеном " + a.tokenType + ": " + a.tokenValue);
                }

            } else if (this.table.containsKey(Arrays.asList(x.content.tokenValue, a.tokenType))) {

                this.magazine.remove(this.magazine.size() - 1);
                List<TreeNode> newNodes = new ArrayList<>();
                for (int i = 0; i < this.table.get(Arrays.asList(x.content.tokenValue, a.tokenType)).size(); i++) {
                    newNodes.add(new TreeNode(
                          new Token(this.table.get(Arrays.asList(x.content.tokenValue, a.tokenType)).get(i),this.table.get(Arrays.asList(x.content.tokenValue, a.tokenType)).get(i) , x.content.line, x.content.position)));
                }
                if (newNodes.size() == 0) {
//x.addChild(new TreeNode("epsilon"));
                  x.addChild(new TreeNode(new Token("eps", "eps", x.content.line, x.content.position)));
                }
                for (TreeNode y : newNodes) {
                    curX = x;

                    x.addChild(y);
                }
                for (int i = newNodes.size() - 1; i >= 0; i--) {
                    this.magazine.add(newNodes.get(i));
                }
                result.add(Arrays.asList(x.content.tokenValue, this.table.get(Arrays.asList(x.content.tokenValue, a.tokenType))).toString());
            } else {
                throw new IllegalArgumentException("Проблема с токеном " + a.tokenType + ": " + a.tokenValue);
            }
        }
        return root;
    }




}
public class Main {
    public static void main(String[] args) {
        try (Scanner scanner = new Scanner(new File("test1.txt"))) {
            String text = scanner.useDelimiter("\\A").next();
            Lexer lexer = new Lexer(text + "$");
            Iterator<Token> iterator = lexer.tokenize();
            Predicter predicter = new Predicter(iterator);
            TreeNode root = predicter.topDownParse();

            try (FileWriter writer = new FileWriter("graph.dot")) {
                writer.write("digraph {\n");
                writer.write("rankdir=LR\n");
                root.printGraph(writer);
                writer.write("}");
            } catch (IOException e) {
                System.out.println("Error writing to file: " + e.getMessage());
            }
        } catch (FileNotFoundException e) {
            System.out.println("File not found: " + e.getMessage());
        } 
    }
}
