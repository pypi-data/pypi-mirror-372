import unittest
from pygments import highlight
from pygments.formatters import HtmlFormatter, TerminalFormatter
from supercollider_lexer import SuperColliderLexer

class TestSuperColliderStyle(unittest.TestCase):
    
    def setUp(self):
        self.lexer = SuperColliderLexer()
        self.dark_style = 'supercollider_dark'
        self.light_style = 'supercollider_light'

    def test_html_output_with_dark_style(self):
        """Test HTML output contains expected style colors"""
        code = 'SinOsc.ar(440) // A simple sine wave'
        formatter = HtmlFormatter(style=self.dark_style, noclasses=True)
        html_output = highlight(code, self.lexer, formatter)
        
        # Should contain inline styles with our colors
        self.assertIn('color:', html_output)
        # Should contain our specific colors (without # since HTML formatter may modify them)
        expected_colors = ['f8f8f2', '1b89ff', 'a8cee0']  # primary, class, comment colors
        for color in expected_colors:
            self.assertIn(color.upper(), html_output)

    def test_html_output_with_light_style(self):
        """Test HTML output with light style"""
        code = 'var freq = 440; // frequency'
        formatter = HtmlFormatter(style=self.light_style, noclasses=True)
        html_output = highlight(code, self.lexer, formatter)
        
        # Should contain our light theme colors
        expected_colors = ['07060D', '902000', '2C4263']  # primary, keyword_declaration, comment
        for color in expected_colors:
            self.assertIn(color, html_output)

    def test_terminal_output_dark_style(self):
        """Test terminal output with dark style"""
        code = 'true false nil'
        formatter = TerminalFormatter(style=self.dark_style)
        terminal_output = highlight(code, self.lexer, formatter)
        
        # Terminal output should contain ANSI escape codes
        self.assertIn('\x1b[', terminal_output)  # ANSI escape sequence start

    def test_different_token_colors(self):
        """Test that different token types get different colors"""
        code = '''
        SinOsc.ar(440)  // class and number
        var freq = "hello"  // keyword and string
        '''
        formatter = HtmlFormatter(style=self.dark_style, noclasses=True)
        html_output = highlight(code, self.lexer, formatter)
        
        # Extract unique color values from the HTML
        import re
        color_pattern = r'color:\s*#([0-9a-fA-F]{6})'
        colors_found = set(re.findall(color_pattern, html_output))
        
        # Should have multiple different colors
        self.assertGreater(len(colors_found), 1, 
                          "Should have multiple different colors for different token types")

    def test_style_consistency(self):
        """Test that the same token type gets consistent styling"""
        code1 = 'SinOsc'
        code2 = 'Array'
        
        formatter = HtmlFormatter(style=self.dark_style, noclasses=True)
        html1 = highlight(code1, self.lexer, formatter)
        html2 = highlight(code2, self.lexer, formatter)
        
        # Both should be class names and get the same color
        import re
        color_pattern = r'color:\s*(#[0-9a-fA-F]{6})'
        colors1 = re.findall(color_pattern, html1)
        colors2 = re.findall(color_pattern, html2)
        
        if colors1 and colors2:
            self.assertEqual(colors1[0], colors2[0], 
                           "Same token types should get the same color")

    def test_comment_styling(self):
        """Test that comments get italic styling"""
        code = '// This is a comment'
        formatter = HtmlFormatter(style=self.dark_style, noclasses=True)
        html_output = highlight(code, self.lexer, formatter)
        
        # Should contain italic styling for comments
        self.assertIn('font-style: italic', html_output)

    def test_bold_styling(self):
        """Test that certain elements get bold styling"""
        code = 'var SinOsc'  # keyword declaration and class
        formatter = HtmlFormatter(style=self.dark_style, noclasses=True)
        html_output = highlight(code, self.lexer, formatter)
        
        # Should contain bold styling
        self.assertIn('font-weight: bold', html_output)

    def test_style_comparison(self):
        """Test that dark and light styles produce different output"""
        code = 'SinOsc.ar(440) // sine wave'
        
        dark_formatter = HtmlFormatter(style=self.dark_style, noclasses=True)
        light_formatter = HtmlFormatter(style=self.light_style, noclasses=True)
        
        dark_output = highlight(code, self.lexer, dark_formatter)
        light_output = highlight(code, self.lexer, light_formatter)
        
        # Outputs should be different
        self.assertNotEqual(dark_output, light_output)
        
        # Should contain different color values
        import re
        color_pattern = r'color:\s*(#[0-9a-fA-F]{6})'
        dark_colors = set(re.findall(color_pattern, dark_output))
        light_colors = set(re.findall(color_pattern, light_output))
        
        # Should have some different colors
        self.assertNotEqual(dark_colors, light_colors)


if __name__ == '__main__':
    unittest.main()