"""markdow popup"""

import sublime
import sublime_plugin

from .third_party import mistune
from .third_party.mistune.renderers import BaseRenderer
from .third_party.mistune.util import escape, escape_html


"""
MINIHTML REFERENCES
===================

HTML
----

TAGS
The following tags are styled by the default style sheet:
* <html>
* <head>, <style>
* <body>
* <h1>, <h2>, <h3>, <h4>, <h5>, <h6>
* <div>
* <p>
* <ul>, <ol>, <li>
* <b>, <strong>
* <i>, <em>
* <u>
* <big>, <small>
* <a>
* <code>, <var>, <tt>

Special behavior is implemented for a few tags:
* <a> — a callback can be specified via the API to handle clicks on anchor tags.
* <img> — supports PNG, JPG and GIF images from file://, res:// and data: URLs.
* <ul> — bullets are displayed for <li> tags.

Other HTML tags with special behavior are not implemented. This includes tags such as <input>, <button>, <table>, etc.

ATTRIBUTES
The following attributes are supported:
* class — for CSS selectors
* id — for CSS selectors
* style — inline CSS
* href — callback-based navigation, protocols support
* title — tooltips

BEST PRACTICES
To allow color scheme authors to tweak the look of popups and phantoms, it is best to add a unique id="" attribute to the <body> tag of your plugin’s HTML.

Within the <body> tag, add a <style> tag containing selectors that do not use the id. Leave that for selectors in color schemes to be able to override the plugin.

  <body id="my-plugin-feature">
      <style>
          div.error {
              background-color: red;
              padding: 5px;
          }
      </style>
      <div class="error"></div>
  </body>


CSS
----

The following list provides an overview of supported properties and values:
* display: none, inline, block, list-item, inline-block 4085
* margin: positive units
* margin-top: positive units
* margin-right: positive units
* margin-bottom: positive units
* margin-left: positive units
* position: static, relative
* top: positive and negative units
* right: positive and negative units
* bottom: positive and negative units
* left: positive and negative units
* background-color: colors
* font-family: comma-separated list of font families
* font-size: positive units
* font-style: normal, italic
* font-weight: normal, bold
* line-height: positive units
* text-decoration: none, underline
* text-align: left, right, center
* color: colors
* padding: positive units
* padding-top: positive units
* padding-right: positive units
* padding-bottom: positive units
* padding-left: positive units
* border: positive units or border-style or colors
* border-top: positive units or border-style or colors
* border-right: positive units or border-style or colors
* border-bottom: positive units or border-style or colors
* border-left: positive units or border-style or colors
* border-style: none, solid
* border-top-style: border-style
* border-right-style: border-style
* border-bottom-style: border-style
* border-left-style: border-style
* border-width: positive units
* border-top-width: positive units
* border-right-width: positive units
* border-bottom-width: positive units
* border-left-width: positive units
* border-color: colors
* border-top-color: colors
* border-right-color: colors
* border-bottom-color: colors
* border-left-color: colors
* border-radius: positive units
* border-top-left-radius: positive units
* border-top-right-radius: positive units
* border-bottom-right-radius: positive units
* border-bottom-left-radius: positive units
* list-style-type: circle, square and disc

"""


class HTMLRenderer(BaseRenderer):
    """custom html renderer"""

    NAME = "html"
    HARMFUL_PROTOCOLS = {
        "javascript:",
        "vbscript:",
        "data:",
    }

    def __init__(self, escape=True, allow_harmful_protocols=None):
        super(HTMLRenderer, self).__init__()
        self._escape = escape
        self._allow_harmful_protocols = allow_harmful_protocols

    def _safe_url(self, url):
        if self._allow_harmful_protocols is None:
            schemes = self.HARMFUL_PROTOCOLS
        elif self._allow_harmful_protocols is True:
            schemes = None
        else:
            allowed = set(self._allow_harmful_protocols)
            schemes = self.HARMFUL_PROTOCOLS - allowed

        if schemes:
            for s in schemes:
                if url.lower().startswith(s):
                    url = "#harmful-link"
                    break
        return url

    def text(self, text):
        if self._escape:
            return escape(text)
        return escape_html(text)

    def link(self, link, text=None, title=None):
        target = self._safe_url(link)
        opt_title = f' title="{escape_html(title)}"'
        text = text or link
        return f'<a href="{target}"{opt_title}>{text}</a>'

    def image(self, src, alt="", title=None):
        src = self._safe_url(src)
        alt = escape_html(alt)
        opt_title = f' title="{escape_html(title)}"'
        return f'<img src="{src}" alt="{alt}"{opt_title} />'

    def emphasis(self, text):
        return f"<em>{text}</em>"

    def strong(self, text):
        return f"<strong>{text}</strong>"

    def codespan(self, text):
        return f'<span class="code">{escape(text)}</span>'

    def linebreak(self):
        return "<br />\n"

    def inline_html(self, html):
        if self._escape:
            return escape(html)
        return html

    def paragraph(self, text):
        return f"<p>{text}</p>\n"

    def heading(self, text, level):
        return f"<h{level}>{text}</h{level}>\n"

    def newline(self):
        return ""

    def thematic_break(self):
        return "<hr />\n"

    def block_text(self, text):
        return text

    def block_code(self, code, info=None):
        opt_lang = ""
        info = info or ""

        if info := info.strip():
            lang = info.split(None, 1)[0]
            lang = escape_html(lang)
            opt_lang = f' class="language-{lang}"'

        return f'<pre class="code-block"><code{opt_lang}>{escape(code)}</code></pre>\n'

    def block_quote(self, text):
        return f'<blockquote class="blockquote">\n{text}</blockquote>\n'

    def block_html(self, html):
        if not self._escape:
            return f"{html}\n"

        return f"<p>{escape(html)}</p>\n"

    def block_error(self, html):
        return f'<div class="error">{html}</div>\n'

    def list(self, text, ordered, level, start=None):
        if ordered:
            opt_start = f' start="{start}"' if start is not None else ""
            return f"<ol{opt_start}>{text}</ol>\n"

        return f"<ul>\n{text}</ul>\n"

    def list_item(self, text, level):
        return f"<li>{text}</li>\n"

    def finalize(self, data):
        return "".join(data)


css_style = """\
body {
    margin: 0.5em;
    font-family: BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
    line-height: 1.5;
}
pre {
    background-color: color(var(--background) alpha(0.5));
}
.code,.code-block,.blockquote {
    background-color: color(var(--background) alpha(0.8));
}
pre,.code,.code-block {
    font-family: monospace;
}
.code {
    display: inline;
    padding: 0, 0.3em, 0, 0.3em;
    border-radius: 0.2em;
    border-style: solid;
}
pre,.code-block,.blockquote {
    display: block;
    padding : 0.5em;
    margin: 0.3em;
    border-radius: 0.3em;
}
.code-block {
}
.blockquote {
}
ul,ol {
    margin: 0.5em;
    padding: 0;
}
"""


class MarkdownPopupCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, text: str, point: int = -1):
        self.show(self.view, point, text)

    @staticmethod
    def convert_markdown(markdown: str) -> str:
        """convert markdown to html"""

        escape = False  # ignore html tag unescaped
        hard_wrap = True  # break newline with <br>

        renderer = HTMLRenderer(escape=escape)
        md = mistune.Markdown(
            renderer, inline=mistune.InlineParser(renderer, hard_wrap=hard_wrap)
        )
        return md(markdown)

    @staticmethod
    def wrap_html(content: str, style: str = ""):
        return (
            '<body id="my-plugin-feature">\n'
            f"<style>\n{style}\n</style>\n"
            f"<div>\n{content}\n</div>\n"
            "</body>"
        )

    @staticmethod
    def adapt_pre_block(text: str) -> str:
        lines = []
        pre_block = False
        for line in text.split("\n"):
            if not pre_block:
                # open pre block
                if line.startswith("<pre"):
                    pre_block = True

            if pre_block:
                # closing pre block
                if line.endswith("/pre>"):
                    pre_block = False

                else:
                    # inside pre block
                    line = line.replace("  ", "&nbsp;&nbsp;")
                    line = f"{line}<br />"

                lines.append(line)
                continue

            # outside pre block
            lines.append(line)

        return "\n".join(lines)

    def show(self, view: sublime.View, point: int, text: str):
        html_text = self.convert_markdown(text)
        text = self.wrap_html(html_text, style=css_style)
        text = self.adapt_pre_block(text)

        view.show_popup(
            text,
            location=point,
            flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY
            | sublime.COOPERATE_WITH_AUTO_COMPLETE,
            max_width=1024,
        )
