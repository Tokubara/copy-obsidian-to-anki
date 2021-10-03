### 用到的项目
大部分代码来自于这两个项目:
- [Obsidian_to_Anki](https://github.com/Pseudonium/Obsidian_to_Anki.git). 代码高亮以外. 对应main.py.
- [syntax-highlighting](https://github.com/glutanimate/syntax-highlighting.git). 处理代码高亮. 对应syntax_highlight.py.

### 作用
将 剪切板上的 obsidian markdown 文本转换为html, 写入剪切板, 用于拷贝到anki中.
为什么强调是 obsidian markdown, 以及目标是anki? 因为做了这几个处理:
- 图片语法, obsidian用的是wiki link. 也就是`![[]]`. 可以通过修改`OBS_IMG_REGEXP`来支持一般的图片语法.
- 目标是anki, 是因为把图片拷贝到了anki的media目录下, 并且img的路径也只有图片名.

除了`markdown`包提供的解析, 单独处理了这些:
- 图片, `![[Figure 9.1.png]]`这样的.
- 代码块

### 用法
拷贝obsidian的markdown, 执行`python3 main.py`, 剪切板就会是渲染过的内容. 只在mac上使用了, windows应该还有其它需要改的地方.
main.py需要修改以下地方:
- `ANKI_MEDIA_PATH`, 改成anki的媒体文件的目录.
- `OBS_ATTACHMENT_PATH`, 改成obsidian的附件目录.

### 没处理的
- 没有处理音频.
- 没处理 obsidian 的内链. 原因是我主要用标题块链接, obsidian 目前好像还无法外链直接跳转到标题.
