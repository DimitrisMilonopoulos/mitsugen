# material-color-utilities-python

[![Chat on Matrix](https://matrix.to/img/matrix-badge.svg)](https://matrix.to/#/#AdwCustomizer:matrix.org)

Python port of material-color-utilities used for Material You colors

Original source code: https://github.com/material-foundation/material-color-utilities

NOTE: This is an **unofficial** port of material-color-utilities from JavaScript to Python

## Build and install

You need to have [Poetry](https://python-poetry.org) installed

```shell
poetry build
poetry install
```

## Usage examples for Themeing

Theme from color:

``` python
from material_color_utilities_python import *

theme = themeFromSourceColor(argbFromHex('#4285f4'))

print(theme)
```

Color from image:

``` python
from material_color_utilities_python import *

img = Image.open('path/to/image.png')
argb = sourceColorFromImage(img)

print(hexFromArgb(argb))
```

Theme from image:

``` python
from material_color_utilities_python import *

img = Image.open('/path/to/image')
basewidth = 64
wpercent = (basewidth/float(img.size[0]))
hsize = int((float(img.size[1])*float(wpercent)))
img = img.resize((basewidth,hsize),Image.Resampling.LANCZOS)
print(themeFromImage(img))

print(theme)
```
