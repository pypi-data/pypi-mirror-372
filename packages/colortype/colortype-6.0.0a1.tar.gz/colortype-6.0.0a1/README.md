# ansiconsole

ansiconsole is a lightweight python library for ansi text styling, colors, and cursor control. it supports standard ansi styles, 256-color, and rgb values, giving you full control over your terminal output.

## features

- text styles: bold, underline, dim, blink, reverse
- foreground and background colors
- light colors and bright backgrounds
- 256-color support
- rgb custom foreground and background colors
- cursor movement and line control
- console() function for inline formatting

## installation

```bash
pip install ansiconsole
````

## usage

```python
from ansiconsole import console

print(console("hello, [red]world[reset]!"))
print(console("[b_blue][white] info: [reset] this text has background and style"))
print(console("[up]moves cursor up"))
print(console("[rgb(255,0,0)]custom red text[rgb(0,0,0)]"))
```

## changelog

see [changelog.md](changelog.md) for full release history.

## license

this project is licensed under the mit license.