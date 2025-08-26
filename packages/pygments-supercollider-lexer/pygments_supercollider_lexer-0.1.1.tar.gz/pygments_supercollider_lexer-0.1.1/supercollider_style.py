'''
    Light and dark styles for SuperCollider code.

    :copyright: Copyright 2025 by Anders Eskildsen
    :license: MIT, see LICENSE for details.
'''

from pygments.style import Style
from pygments.token import Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Text

__all__ = ['SuperColliderDark', 'SuperColliderLight']

def make_sc_styles(colors):
    '''
    Create a SuperCollider styles dict from a dictionary of colors.
    '''
    return {
        Number: colors['number'],
        Name: colors['primary'],
        Text: colors['primary'],
        Operator: colors['primary'],
        Punctuation: colors['primary'],
        Comment: f"italic {colors['comment']}",
        Name.Class: f"bold {colors['class']}",
        Name.Variable: f"bold {colors['env_variable']}",
        Keyword: colors['accent'],
        Keyword.Declaration: f"bold {colors['keyword_declaration']}",
        Keyword.Constant: colors['number'],
        String: colors['string'],
        String.Symbol: colors['accent'],
        String.Char: colors['char'],
    }

class SuperColliderDark(Style):
    '''
    This style accompanies the SuperCollider lexer and is designed for use with dark themes.
    '''
    name = 'supercollider_dark'

    colors = {
        'primary': '#f8f8f2',
        'accent': '#a6e22e',
        'number': "#ff60f4",
        'comment': "#a8cee0",
        'class': '#1b89ff',
        'env_variable': '#fd9d2f',
        'keyword_declaration': '#de4d45',
        'string': '#618bff',
        'char': "#d84841",
        'background': '#272822',
        'highlight': '#575C3A',
    }

    styles = make_sc_styles(colors)

    #: overall background color (``None`` means transparent)
    background_color = colors['background']

    #: highlight background color
    highlight_color = colors['highlight']

    #: line number font color
    line_numbers = 'inherit'

    #: line number background color
    line_number_background_color = 'transparent'

class SuperColliderLight(Style):
    '''
    This style accompanies the SuperCollider lexer and is designed for light themes.
    '''
    name = 'supercollider_light'

    colors = {
        'primary': "#07060D",
        'accent': '#007020',
        'number': "#ab2ea3",
        'comment': "#2C4263",
        'class': '#0E84B5',
        'env_variable': "#c76b02",
        'keyword_declaration': '#902000',
        'string': '#4070A0',
        'char': '#4070A0',
        'background': '#f0f0f0',
        'highlight': '#ffffcc',
    }

    styles = make_sc_styles(colors)

    background_color = colors['background']
    highlight_color = colors['highlight']
    line_numbers = 'inherit'
    line_number_background_color = 'transparent'