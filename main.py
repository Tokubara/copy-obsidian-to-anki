import re
import clipboard
#  import urllib.request
#  import configparser
import pathlib
import shutil
import markdown
import html
from syntax_highlight import hilcd
#  import syntax_highlight
#  import logging
#  import hashlib

md_parser = markdown.Markdown(
    extensions=[
        'fenced_code',
        'footnotes',
        'md_in_html',
        'tables',
        'nl2br',
        'sane_lists'
    ]
)

class FormatConverter:
    """Converting Obsidian formatting to Anki formatting."""

    ANKI_MEDIA_PATH = pathlib.Path('/Users/quebec/Library/Application Support/Anki2/User 1/collection.media/')
    OBS_ATTACHMENT_PATH = pathlib.Path('/Users/quebec/notes/vx_attachments/')

    OBS_INLINE_MATH_REGEXP = re.compile(
        r"(?<!\$)\$(?=[\S])(?=[^$])[\s\S]*?\S\$"
    )
    OBS_DISPLAY_MATH_REGEXP = re.compile(r"\$\$[\s\S]*?\$\$")

    OBS_CODE_REGEXP = re.compile( # inline
        r"(?<!`)`(?=[^`])[\s\S]*?`"
    )
    OBS_DISPLAY_CODE_REGEXP = re.compile(
        r"^```(\w*)\n([\s\S]*)^```",
        flags=re.MULTILINE
    )
    OBS_IMG_REGEXP = re.compile(
        r"!?\[\[(.+\.png)\]\]"
    )

    ANKI_INLINE_START = r"\("
    ANKI_INLINE_END = r"\)"

    ANKI_DISPLAY_START = r"\["
    ANKI_DISPLAY_END = r"\]"

    ANKI_MATH_REGEXP = re.compile(r"(\\\[[\s\S]*?\\\])|(\\\([\s\S]*?\\\))") # 比如对应\[\alpha\]

    MATH_REPLACE = "OBSTOANKIMATH"
    INLINE_CODE_REPLACE = "OBSTOANKICODEINLINE"
    DISPLAY_CODE_REPLACE = "OBSTOANKICODEDISPLAY"
    IMG_REPLACE = "OBSTOANKIIMG"

    IMAGE_REGEXP = re.compile(r'<img alt=".*?" src="(.*?)"') # 我担心wiki link不能正确转换
    SOUND_REGEXP = re.compile(r'\[sound:(.+)\]')
    CLOZE_REGEXP = re.compile(
        r'(?:(?<!{){(?:c?(\d+)[:|])?(?!{))((?:[^\n][\n]?)+?)(?:(?<!})}(?!}))'
    )
    URL_REGEXP = re.compile(r'https?://')

    PARA_OPEN = "<p>"
    PARA_CLOSE = "</p>"

    CLOZE_UNSET_NUM = 1

    @staticmethod
    def format_note_with_url(note, url):
        for key in note["fields"]:
            note["fields"][key] += "<br>" + "".join([
                '<a',
                ' href="{}" class="obsidian-link">Obsidian</a>'.format(url)
            ])
            break  # So only does first field

    @staticmethod
    def format_note_with_frozen_fields(note, frozen_fields_dict):
        for field in note["fields"].keys():
            note["fields"][field] += frozen_fields_dict[
                note["modelName"]
            ][field]

    @staticmethod
    def inline_anki_repl(matchobject):
        """Get replacement string for Obsidian-formatted inline math."""
        found_string = matchobject.group(0)
        # Strip Obsidian formatting by removing first and last characters
        found_string = found_string[1:-1]
        # Add Anki formatting
        result = FormatConverter.ANKI_INLINE_START + found_string
        result += FormatConverter.ANKI_INLINE_END
        return result

    @staticmethod
    def display_anki_repl(matchobject): # 返回是\(公式\)
        """Get replacement string for Obsidian-formatted display math."""
        found_string = matchobject.group(0)
        # Strip Obsidian formatting by removing first two and last two chars
        found_string = found_string[2:-2]
        # Add Anki formatting
        result = FormatConverter.ANKI_DISPLAY_START + found_string
        result += FormatConverter.ANKI_DISPLAY_END
        return result

    @staticmethod
    def obsidian_to_anki_math(note_text):  # 处理了$ $和$$ $$
        """Convert Obsidian-formatted math to Anki-formatted math."""
        return FormatConverter.OBS_INLINE_MATH_REGEXP.sub(
            FormatConverter.inline_anki_repl,
            FormatConverter.OBS_DISPLAY_MATH_REGEXP.sub( # 先替换$$ $$
                FormatConverter.display_anki_repl, note_text
            )
        )

    #  @staticmethod
    #  def cloze_repl(match):
        #  id, content = match.group(1), match.group(2)
        #  if id is None:
            #  result = "{{{{c{!s}::{}}}}}".format(
                #  FormatConverter.CLOZE_UNSET_NUM,
                #  content
            #  )
            #  FormatConverter.CLOZE_UNSET_NUM += 1
            #  return result
        #  else:
            #  return "{{{{c{}::{}}}}}".format(id, content)
#
    #  @staticmethod
    #  def curly_to_cloze(text):
        #  """Change text in curly brackets to Anki-formatted cloze."""
        #  text = FormatConverter.CLOZE_REGEXP.sub(
            #  FormatConverter.cloze_repl,
            #  text
        #  )
        #  FormatConverter.CLOZE_UNSET_NUM = 1
        #  return text

    @staticmethod
    def markdown_parse(text):
        """Apply markdown conversions to text."""
        text = md_parser.reset().convert(text)
        return text

    @staticmethod
    def is_url(text):
        """Check whether text looks like a url."""
        return bool(
            FormatConverter.URL_REGEXP.match(text)
        )

    #  @staticmethod
    #  def get_images(html_text): # 是在处理了()[]之后处理的, 已经是img tag了
        #  """Get all the images that need to be added."""
        #  for match in FormatConverter.IMAGE_REGEXP.finditer(html_text):
            #  path = match.group(1)
            #  if FormatConverter.is_url(path):
                #  continue  # Skips over images web-hosted.
            #  path = urllib.parse.unquote(path)
            #  filename = os.path.basename(path)
            #  if filename not in App.ADDED_MEDIA and filename not in MEDIA:
                #  MEDIA[filename] = file_encode(path)
                #  Adds the filename and data to media_names
#
    #  @staticmethod
    #  def get_audio(html_text):
        #  """Get all the audio that needs to be added."""
        #  for match in FormatConverter.SOUND_REGEXP.finditer(html_text):
            #  path = match.group(1)
            #  filename = os.path.basename(path)
            #  if filename not in App.ADDED_MEDIA and filename not in MEDIA:
                #  MEDIA[filename] = file_encode(path)
                #  Adds the filename and data to media_names
#
    #  @staticmethod
    #  def path_to_filename(matchobject):
        #  """Replace the src in matchobject appropriately."""
        #  found_string, found_path = matchobject.group(0), matchobject.group(1)
        #  if FormatConverter.is_url(found_path):
            #  return found_string  # So urls should not be altered.
        #  found_string = found_string.replace(
            #  found_path, os.path.basename(urllib.parse.unquote(found_path))
        #  )
        #  return found_string
#
    #  @staticmethod
    #  def fix_image_src(html_text):
        #  """Fix the src of the images so that it's relative to Anki."""
        #  return FormatConverter.IMAGE_REGEXP.sub(
            #  FormatConverter.path_to_filename,
            #  html_text
        #  )
#
    #  @staticmethod
    #  def fix_audio_src(html_text):
        #  """Fix the audio filenames so that it's relative to Anki."""
        #  return FormatConverter.SOUND_REGEXP.sub(
            #  FormatConverter.path_to_filename,
            #  html_text
        #  )
#
    @staticmethod
    def format(note_text):
        """Apply all format conversions to note_text."""
        note_text = FormatConverter.obsidian_to_anki_math(note_text)
        # Extract the parts that are anki math
        math_matches = [ # 不知道有什么用, 就算有用也很靠后了
            math_match.group(0)
            for math_match in FormatConverter.ANKI_MATH_REGEXP.finditer(
                note_text
            )
        ]
        # Replace them to be later added back, so they don't interfere
        # with markdown parsing
        note_text = FormatConverter.ANKI_MATH_REGEXP.sub( #? 为什么要做这个替换? 把\(公式\)替换为了常量字符串
            FormatConverter.MATH_REPLACE, note_text
        )
        # Now same with code!
        #  inline_code_matches = [
            #  code_match.group(0)
            #  for code_match in FormatConverter.OBS_CODE_REGEXP.finditer(
                #  note_text
            #  )
        #  ]
        #  note_text = FormatConverter.OBS_CODE_REGEXP.sub(
            #  FormatConverter.INLINE_CODE_REPLACE, note_text # 类似把`内容`, 替换为常量字符串
        #  )
        display_code_matches = [ # 类似inline code的处理
            (code_match.group(1), code_match.group(2))
            for code_match in FormatConverter.OBS_DISPLAY_CODE_REGEXP.finditer(
                note_text
            )
        ]
        note_text = FormatConverter.OBS_DISPLAY_CODE_REGEXP.sub(
            FormatConverter.DISPLAY_CODE_REPLACE, note_text
        )
        img_matches = [ # 类似inline code的处理
            img_match.group(1)
            for img_match in FormatConverter.OBS_IMG_REGEXP.finditer(
                note_text
            )
        ]
        note_text = FormatConverter.OBS_IMG_REGEXP.sub(
            FormatConverter.IMG_REPLACE, note_text # 类似把`内容`, 替换为常量字符串
        )
        #  if cloze:
            #  note_text = FormatConverter.curly_to_cloze(note_text)
        #  for code_match in inline_code_matches:
            #  note_text = note_text.replace(
                #  FormatConverter.INLINE_CODE_REPLACE,
                #  code_match,
                #  1
            #  )
        note_text = FormatConverter.markdown_parse(note_text)
        # Add back the parts that are anki math
        for math_match in math_matches:
            note_text = note_text.replace(
                FormatConverter.MATH_REPLACE,
                html.escape(math_match), #? escape的作用是什么?
                1
            )
        for code_match in display_code_matches:
            note_text = note_text.replace(
                FormatConverter.DISPLAY_CODE_REPLACE,
                hilcd(code_match[1], code_match[0]),
                1
            )
        for img_match in img_matches:
            note_text = note_text.replace(
                FormatConverter.IMG_REPLACE,
                f'<img src="{img_match}">', #? escape的作用是什么?
                1 # 参数1是很重要的, 避免全部替换
            )
            img_path = FormatConverter.ANKI_MEDIA_PATH / img_match
            # 拷贝图片
            if not img_path.is_file():
                #  import pdb; pdb.set_trace()
                shutil.copy(str(FormatConverter.OBS_ATTACHMENT_PATH / img_match), str(FormatConverter.ANKI_MEDIA_PATH))

        #  FormatConverter.get_images(note_text)
        #  FormatConverter.get_audio(note_text)
        #  note_text = FormatConverter.fix_image_src(note_text)
        #  note_text = FormatConverter.fix_audio_src(note_text)
        note_text = note_text.strip()
        # Remove unnecessary paragraph tag
        if note_text.startswith(
            FormatConverter.PARA_OPEN
        ) and note_text.endswith(
            FormatConverter.PARA_CLOSE
        ):
            note_text = note_text[len(FormatConverter.PARA_OPEN):]
            note_text = note_text[:-len(FormatConverter.PARA_CLOSE)]
        return note_text

if __name__ == '__main__':
    markdown_text = clipboard.paste()
    assert markdown_text is not None, "text is none"
    anki_text = FormatConverter.format(markdown_text)
    clipboard.copy(anki_text)
