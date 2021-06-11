from PIL import Image, ImageDraw, ImageFont
lenth = 12.5


string1 = """
+---------+----------+--------+-----------+
|      НЗ | Дата     |   Сума |   Залишок |
+=========+==========+========+===========+
| 2312555 | 02-06-21 | 800.5  |   29200.5 |
+---------+----------+--------+-----------+
| 2312555 | 02-06-21 | 300.75 |   28899.8 |
+---------+----------+--------+-----------+
| 2312555 | 02-06-21 | 800.5  |   29200.5 |
+---------+----------+--------+-----------+
| 2312555 | 02-06-21 | 300.75 |   28899.8 |
+---------+----------+--------+-----------+
"""
img = Image.new('RGB', (275, int(lenth*string1.count("\n"))), color=(255, 255, 255))
d = ImageDraw.Draw(img)

# print(string1.count("\n"))
font_size = 10
unicode_font = ImageFont.truetype("consola.ttf", font_size)
d.text((5, 0), string1, font=unicode_font, fill=(0, 0, 0))

img.save('pil_text_font.png')