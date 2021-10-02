from bs4 import BeautifulSoup
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import re
import clipboard

linenos = False
centerfragments = False
noclasses = True
STYLE = "default"
FONT = "Monaco"

def hilcd(code, langAlias):
    global LASTUSED
    mystyle = STYLE
    inline = False

    my_lexer = get_lexer_by_name(langAlias, stripall=False)

    # http://pygments.org/docs/formatters/#HtmlFormatter
    # {{{3
    """
nowrap
If set to True, don’t wrap the tokens at all, not even inside a <pre> tag. This disables most other options (default: False).

full
Tells the formatter to output a “full” document, i.e. a complete self-contained document (default: False).

title
If full is true, the title that should be used to caption the document (default: '').

style
The style to use, can be a string or a Style subclass (default: 'default'). This option has no effect if the cssfile and noclobber_cssfile option are given and the file specified in cssfile exists.

noclasses
If set to true, token <span> tags (as well as line number elements) will not use CSS classes, but inline styles. This is not recommended for larger pieces of code since it increases output size by quite a bit (default: False).

classprefix
Since the token types use relatively short class names, they may clash with some of your own class names. In this case you can use the classprefix option to give a string to prepend to all Pygments-generated CSS class names for token types. Note that this option also affects the output of get_style_defs().

cssclass
CSS class for the wrapping <div> tag (default: 'highlight'). If you set this option, the default selector for get_style_defs() will be this class.
If you select the 'table' line numbers, the wrapping table will have a CSS class of this string plus 'table', the default is accordingly 'highlighttable'.

cssstyles
Inline CSS styles for the wrapping <div> tag (default: '').

prestyles
Inline CSS styles for the <pre> tag (default: '').

cssfile
If the full option is true and this option is given, it must be the name of an external file. If the filename does not include an absolute path, the file’s path will be assumed to be relative to the main output file’s path, if the latter can be found. The stylesheet is then written to this file instead of the HTML file.

noclobber_cssfile
If cssfile is given and the specified file exists, the css file will not be overwritten. This allows the use of the full option in combination with a user specified css file. Default is False.

linenos
If set to 'table', output line numbers as a table with two cells, one containing the line numbers, the other the whole code. This is copy-and-paste-friendly, but may cause alignment problems with some browsers or fonts. If set to 'inline', the line numbers will be integrated in the <pre> tag that contains the code
The default value is False, which means no line numbers at all.
For compatibility with Pygments 0.7 and earlier, every true value  except 'inline' means the same as 'table' (in particular, that means also True).

hl_lines
Specify a list of lines to be highlighted.

linenostart
The line number for the first line (default: 1).

linenostep
If set to a number n > 1, only every nth line number is printed.

linenospecial
If set to a number n > 0, every nth line number is given the CSS class "special" (default: 0).

nobackground
If set to True, the formatter won’t output the background color for the wrapping element (this automatically defaults to False when there is no wrapping element [eg: no argument for the get_syntax_defs method given]) (default: False).

lineseparator
This string is output between lines of code. It defaults to "\n", which is enough to break a line inside <pre> tags, but you can e.g. set it to "<br>" to get HTML line breaks.

lineanchors
If set to a nonempty string, e.g. foo, the formatter will wrap each output line in an anchor tag with a name of foo-linenumber. This allows easy linking to certain lines.

linespans
If set to a nonempty string, e.g. foo, the formatter will wrap each output line in a span tag with an id of foo-linenumber. This allows easy access to lines via javascript.

anchorlinenos
If set to True, will wrap line numbers in <a> tags. Used in combination with linenos and lineanchors.

tagsfile
If set to the path of a ctags file, wrap names in anchor tags that link to their definitions. lineanchors should be used, and the tags file should specify line numbers (see the -n option to ctags).

tagurlformat
A string formatting pattern used to generate links to ctags definitions. Available variables are %(path)s, %(fname)s and %(fext)s. Defaults to an empty string, resulting in just #prefix-number links.

filename
A string used to generate a filename when rendering <pre> blocks, for example if displaying source code.

wrapcode
Wrap the code inside <pre> blocks using <code>, as recommended by the HTML5 specification.
    """
    # }}}
    tablestyling = ""
    #  if noclasses:
    tablestyling += "text-align: left;"
#  if gc("cssclasses") and not gc("css_custom_class_per_style"):
    #  css_class = "highlight"  # the default for pygments
#  else:
    css_class = f"shf__{mystyle}__highlight"
    my_formatter = HtmlFormatter(
        cssclass=css_class,
        cssstyles=tablestyling,
        font_size=16,
        linenos=linenos, 
        lineseparator="<br>",
        nobackground=False,  # True would solve night mode problem without any config (as long as no line numbers are used)
        noclasses=noclasses,
        style=mystyle,
        wrapcode=True)

    pygmntd = highlight(code, my_lexer, my_formatter).rstrip()
    # when using noclasses/inline styling pygments adds line-height 125%, see
    # see https://github.com/pygments/pygments/blob/2fe2152377e317fd215776b6d7467bda3e8cda28/pygments/formatters/html.py#L269
    # It's seems to be only relevant for IE and makes the line numbers misaligned on my PC. So I remove it.
    if noclasses:
        pygmntd = pygmntd.replace('line-height: 125%;', '')
    if inline:
        pretty_code = "".join([pygmntd, "<br>"])
        replacements = {
            '<div class=': '<span class=',
            "<pre": "<code",
            "</pre></div>": "</code></span>",
            "<br>": "",
            "</br>": "",
            "</ br>": "",
            "<br />": "",
            'style="line-height: 125%"': '',
        }
        for k, v in replacements.items():
            pretty_code = pretty_code.replace(k, v)
    else:
        if linenos:
            pretty_code = "".join([pygmntd, "<br>"])
        # to show line numbers pygments uses a table. The background color for the code
        # highlighting is limited to this table
        # If pygments doesn't use linenumbers it doesn't use a table. This means
        # that the background color covers the whole width of the card.
        # I don't like this. I didn't find an easier way than reusing the existing
        # solution.
        # Glutanimate removed the table in the commit
        # https://github.com/glutanimate/syntax-highlighting/commit/afbf5b3792611ecd2207b9975309d05de3610d45
        # which hasn't been published on Ankiweb in 2019-10-02.
        else:
            pretty_code = "".join([f'<table class="{css_class}table"><tbody><tr><td>',
                                    pygmntd,
                                    "</td></tr></tbody></table><br>"])
        """
        I can't solely rely on the pygments-HTMLFormatter
        A lot of the stuff I did before 2020-11 with bs4 can indeed be done by adjusting
        the HTMLFormatter options:
        - I can override the ".card {text-align: center}" by using the option "cssstyles"
          (Inline CSS styles for the wrapping <div> tag).
        - I can set a custom class by adjusting the option "cssclass" which defaults to "highlight"
          Besides this there are the classes linenos and linenodiv. BUT I don't need to customize 
          the latter classes. I can also work with longer css rules: 
             /*syntax highlighting fork add-on: dark background*/
             .night_mode .shf__default__highlight{
             background-color: #222222 !important;
             }
             /*syntax highlighting fork add-on: line numbers: white on black: sometimes a span is used, sometimes not*/
             .night_mode .shf__default__highlighttable tr td.linenos div.linenodiv pre span {
             background-color: #222222 !important;
             color: #f0f0f0 !important;
             }
             .night_mode .shf__default__highlighttable tr td.linenos div.linenodiv pre {
             background-color: #222222 !important;
             color: #f0f0f0 !important;
             }
        BUT as far as I see I can't set inline styling for the surrounding table. But to center the
        table I need to add something like "margin: 0 auto;". If you rely on css it's easy because
        the "the wrapping table will have a CSS class of [the cssclass] string plus 'table', the 
        default is accordingly 'highlighttable'.". But my option should work without the user
        adjusting each template and the editor.
        I also need to set the font.
        """
        if centerfragments or noclasses:
            soup = BeautifulSoup(pretty_code, 'html.parser')
            if centerfragments:
                tablestyling = "margin: 0 auto;"
                for t in soup.findAll("table"):
                    if t.has_attr('style'):
                        t['style'] = tablestyling + t['style']
                    else:
                        t['style'] = tablestyling
            if noclasses:
                for t in soup.findAll("code"):
                    t['style'] = "font-family: %s;" % FONT
            pretty_code = str(soup)
            return pretty_code


basic_stylesheet = """
QMenu::item {
    padding-top: 16px;
    padding-bottom: 16px;
    padding-right: 75px;
    padding-left: 20px;
    font-size: 15px;
}
QMenu::item:selected {
    background-color: #fd4332;
}
"""
def process_html(html):
    """Modify highlighter output to address some Anki idiosyncracies"""
    # 1.) "Escape" curly bracket sequences reserved to Anki's card template
    # system by placing an invisible html tag inbetween
    for pattern, replacement in ((r"{{", r"{<!---->{"),
                                 (r"}}", r"}<!---->}"),
                                 (r"::", r":<!---->:")):
        html = re.sub(pattern, replacement, html)
    return html

if __name__ == '__main__':  # pragma: no cover

    code = clipboard.paste() # TODO 改成标准输入

    langAlias = 'python' # TODO 作为参数
    pretty_code = hilcd(code, 'python')
    clipboard.copy(pretty_code)

