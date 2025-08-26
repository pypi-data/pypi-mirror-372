import unittest
from pygments.token import Token
from supercollider_lexer import SuperColliderLexer


class TestSuperColliderLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = SuperColliderLexer()

    def _tokenize(self, code):
        """Helper method to tokenize code and return list of (token_type, value) tuples"""
        return list(self.lexer.get_tokens(code))

    def test_lexer_name_and_aliases(self):
        """Test lexer metadata"""
        self.assertEqual(self.lexer.name, 'SuperCollider')
        self.assertIn('sc-plugin', self.lexer.aliases)

    def test_comments(self):
        """Test comment tokenization"""
        code = """// This is a line comment
/* This is a block comment */
"""
        tokens = self._tokenize(code)
        
        comment_tokens = [t for t in tokens if t[0] in Token.Comment]
        self.assertEqual(len(comment_tokens), 4)

    def test_numbers(self):
        """Test numeric literals"""
        code = "42 3.14159 -7 0.5 1e6 pi inf 0x0"
        tokens = self._tokenize(code)
        
        number_tokens = [t for t in tokens if t[0] in Token.Number]
        self.assertEqual(len(number_tokens), 8)

    def test_strings(self):
        """Test string literals"""
        code = '"hello world" "Super\"Collider"'
        tokens = self._tokenize(code)

        print(tokens)
        
        string_tokens = [t for t in tokens if t[0] in Token.Literal.String]
        self.assertEqual(len(string_tokens), 8)

    def test_symbols(self):
        """Test symbol literals"""
        code = r"\symbol 'freq' 'o.43.xyz'"
        tokens = self._tokenize(code)
        
        symbol_tokens = [t for t in tokens if t[0] is Token.Literal.String.Symbol]
        self.assertEqual(len(symbol_tokens), 3)

    def test_keywords(self):
        """Test some of SuperCollider's keywords"""
        code = "var arg true sauce nil.isNil thisFunction esac  thisThread"
        tokens = self._tokenize(code)
        keyword_tokens = [t for t in tokens if t[0] in Token.Keyword]
        name_pseudo_tokens = [t for t in tokens if t[0] is Token.Name.Builtin.Pseudo]
        self.assertEqual(len(keyword_tokens), 4)
        self.assertEqual(len(name_pseudo_tokens), 2)

    def test_operators(self):
        """Test operators"""
        code = "+ - * / % == != < > <= >= && ||"
        tokens = self._tokenize(code)
        
        operator_tokens = [t for t in tokens if t[0] in Token.Operator]
        self.assertEqual(len(operator_tokens), 13)

    def test_punctuation(self):
        """Test punctuation marks"""
        code = "{ } ( ) [ ] ; ,"
        tokens = self._tokenize(code)
        
        punct_tokens = [t for t in tokens if t[0] in Token.Punctuation]
        self.assertEqual(len(punct_tokens), 8)

    def test_identifiers(self):
        """Test identifier tokenization"""
        code = "SinOsc LFNoise1 myVariable ~myBus"
        tokens = self._tokenize(code)
        
        # Check that we get name tokens
        name_tokens = [t for t in tokens if t[0] in Token.Name]
        self.assertEqual(len(name_tokens), 4)

    def test_class_names(self):
        """Test class name recognition"""
        code = "SinOsc Array chutney String"
        tokens = self._tokenize(code)
        
        # Class names (starting with uppercase) should be recognized
        class_tokens = [t for t in tokens if t[0] is Token.Name.Class]
        self.assertEqual(len(class_tokens), 3)

    def test_syntax(self):
        """Test class method call syntax"""
        code = "SinOsc.ar(440, 0, 0.5)"
        tokens = self._tokenize(code)
        
        # Should contain class name, dot, method name, and parentheses
        dot_tokens = [t for t in tokens if t[1] == '.']
        paren_tokens = [t for t in tokens if t[1] in '()']
        name_tokens = [t for t in tokens if t[0] is Token.Name]
        classname_tokens = [t for t in tokens if t[0] is Token.Name.Class]
        number_tokens = [t for t in tokens if t[0] in Token.Literal.Number]
        
        self.assertEqual(len(dot_tokens), 1)
        self.assertEqual(len(paren_tokens), 2)
        self.assertEqual(len(name_tokens), 1)
        self.assertEqual(len(classname_tokens), 1)
        self.assertEqual(len(number_tokens), 3)

    def test_whitespace_handling(self):
        """Test whitespace tokenization"""
        code = "a    b\n\tc"
        tokens = self._tokenize(code)
        
        whitespace_tokens = [t for t in tokens if t[0] in Token.Text and t[1].strip() == '']
        self.assertEqual(len(whitespace_tokens), 3)


if __name__ == '__main__':
    unittest.main()