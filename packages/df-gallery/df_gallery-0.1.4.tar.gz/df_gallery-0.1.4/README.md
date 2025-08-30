# df-gallery

[![PyPI](https://img.shields.io/pypi/v/df-gallery.svg)](https://pypi.org/project/df-gallery/)
[![Python Versions](https://img.shields.io/pypi/pyversions/df-gallery.svg)](https://pypi.org/project/df-gallery/)
[![License](https://img.shields.io/pypi/l/df-gallery.svg)](LICENSE)

# df-gallery

Generate a fast, filterable, shuffleable HTML image gallery from a CSV. Great for poking at large image folders with rich metadata filters (pandas-ish syntax in the browser).

## Install
```bash
# from PyPI 
pip install df-gallery

# OR for development
uv venv && uv pip install -e .[dev]

## Usage

df-gallery path/to/images.csv \
  --out gallery.html \
  --path-col filename \
  --img-root /absolute/or/relative/prefix \
  --relative-to-html \
  --chunk 500 \
  --tile 200 \
  --title "My Image Gallery"
```

or `dfg`

 The CSV must contain a column with image paths or URLs (default: filename). All columns become filterable fields in the UI.

 ## Development
uv run pytest
uv build            # builds wheel + sdist
uv publish          # publishes to PyPI (set PYPI token first)

## License

---

## LICENSE (MIT)
```text
MIT License

Copyright (c) 2025 Freddie Lichtenstein

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
