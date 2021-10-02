from pygments.cmdline import main
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
import re
import clipboard

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
    linenos = False
    centerfragments = False
    noclasses = True
    STYLE = "default"

    code = clipboard.paste() # TODO 改成标准输入

    langAlias = 'python' # TODO 作为参数

    # Select the lexer for the correct language
    my_lexer = get_lexer_by_name(langAlias, stripall=True)

    # Create html formatter object including flags for line nums and css classes
    my_formatter = HtmlFormatter(
        linenos=linenos, noclasses=noclasses,
        font_size=16, style=STYLE)

    if linenos:
        if centerfragments:
            pretty_code = "".join(["<center>",
                                   highlight(code, my_lexer, my_formatter),
                                   "</center><br>"])
        else:
            pretty_code = "".join([highlight(code, my_lexer, my_formatter),
                                   "<br>"])
    else:
        if centerfragments:
            pretty_code = "".join(["<center>",
                                   highlight(code, my_lexer, my_formatter),
                                   "</center><br>"])
        else:
            pretty_code = "".join([highlight(code, my_lexer, my_formatter),
                                   "<br>"])

    pretty_code = process_html(pretty_code)
    clipboard.copy(pretty_code)

