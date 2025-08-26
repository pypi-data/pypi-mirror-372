# SuperCollider Pygments lexer plugin

This is a Pygments lexer with custom styles for SuperCollider code. It provides syntax highlighting for SuperCollider files in Pygments-supported environments like mkdocs, sphinx, LaTeX's minted package, and more.

Pygments has a built-in lexer for SuperCollider, but the existing implementation has many issues such as not recognizing class names, incorrectly highlighting words which are not keywords in SuperCollider, etc. This plugin is a full reimplementation with much improved lexing, which means more accurate syntax highlighting of SuperCollider code. It has been submitted to the Pygments project and is awaiting review, but in the meantime, you can use it with this plugin.

## Features

- **Accurate lexer**: Recognizes SuperCollider class names, keywords, symbols, and general syntax
- **Custom color themes**: Includes both light and dark themes designed specifically for SuperCollider code
- **Easy integration**: Works with Pygments-based tools such as mkdocs, Sphinx, and LaTeX minted

## Important: Language/lexer name

**Due to a naming conflict with Pygments' built-in SuperCollider lexer, you must use `sc-plugin` as the language/lexer name wherever you want to use this plugin.**  

Do **not** use `sc` or `supercollider`, as those will use the built-in lexer.

## Installation

Install the plugin using pip:

```shell
pip install pygments-supercollider-lexer
```

## Usage

### 1. Python

In vanilla Python scripts, you can use the lexer like this:

```python
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

code = '''
SynthDef(\sine, {
    var sig = SinOsc.ar(\freq.kr(440), 0, \amp.kr(0.1));
    Out.ar(0, sig ! 2);
}).add;
'''

lexer = get_lexer_by_name('sc-plugin')
formatter = HtmlFormatter(style='supercollider_dark')  # or 'supercollider_light'
result = highlight(code, lexer, formatter)

with open("output.html", "w") as f:
    f.write(result)
```

Or on the command line:

```shell
pygmentize -l sc-plugin -O style=supercollider_dark -f html myfile.scd > output.html
```

### 2. Markdown/mkdocs

To use this lexer in markdown files with mkdocs, you need to install the [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/) and configure your `mkdocs.yml` file to include the `pymdownx.highlight` extension as well as the `pymdownx.superfences` extension.

```yaml
markdown_extensions:
  - pymdownx.highlight
  - pymdownx.superfences
```

Then, specify `sc-plugin` as the language name at the top of your code block:

````markdown
```sc-plugin
{ SinOsc.ar(440) * 0.1 }.play;
```
````

#### Using the supplied styles with mkdocs

To use the custom SuperCollider color themes that come with this plugin in a site built with mkdocs, the best solution is to generate CSS rules for the chosen style and include it in your project. Pygments makes it easy to generate CSS files for the styles with the `pygmentize` command:

```shell
# For dark theme
pygmentize -S supercollider_dark -f html -a .highlight > css/supercollider_dark.css

# For light theme  
pygmentize -S supercollider_light -f html -a .highlight > css/supercollider_light.css
```

Then, include the generated CSS files in your `mkdocs.yml`:

```yaml
extra_css:
  - css/supercollider_dark.css
```

If you want to support both light and dark modes, you can include both CSS files and wrap their contents in corresponding [prefers-color-scheme media query](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme).

If using the [Material for MkDocs theme](https://squidfunk.github.io/mkdocs-material/) to switch between light and dark modes, you can use `[data-md-color-scheme="default"]` as a selector for the light theme and `[data-md-color-scheme="slate"]` for the dark theme.

### 3. LaTeX minted

To use the lexer with the minted package in LaTeX:
```latex
\usepackage{minted}
...
\begin{minted}{sc-plugin}
// SuperCollider code here
(
SynthDef(\sine, {
    Out.ar(0, SinOsc.ar(440))
}).add;
)
\end{minted}
```

## Troubleshooting

- If you see incorrect highlighting, double-check that you are using `sc-plugin` as the language/lexer name.
- If you get "no lexer for alias" errors, ensure the plugin is installed in the same Python environment as your tool (MkDocs, Sphinx, etc).
- If you update the plugin, reinstall it with `pip install -e .` to refresh the entry points.

## Development

To contribute or modify the lexer, (fork and) clone the repository and install it in editable mode:

```shell
git clone https://github.com/aeskildsen/pygments-supercollider-lexer.git
cd pygments-supercollider-lexer
pip install -e .[dev]
```

Run tests with:

```shell
pytest
```

## License

This plugin is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.