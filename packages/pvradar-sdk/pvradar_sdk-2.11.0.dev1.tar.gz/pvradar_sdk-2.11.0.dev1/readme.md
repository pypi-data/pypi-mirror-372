Software Developer Kit (SDK) for PVRADAR platform.

https://pvradar.com/product/python-package

# Detailed documentation

https://pvradar.com/docs/sdk

# Installation

```sh
pip install pvradar-sdk
```

# Usage

```python
from pvradar.sdk import PvradarSite, R, describe

site = PvradarSite(location=(-23.123, 115.456), interval='2020..2023')
ghi = site.resource(R.global_horizontal_irradiance)
print(ghi)
print(describe(ghi))
```

Please, contact PVRADAR for more details and features.

# LICENSE

```
Copyright (c) 2025 PVRADAR Labs GmbH <info@pvradar.com> (https://pvradar.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”) via a
publicly accessible package repository (such as PyPI), to download, install,
and use the Software for internal purposes, subject to the following
conditions:

1. The Software may not be modified, merged, adapted, reverse-engineered,
   or altered in any way.
2. The Software may not be sublicensed, resold, or distributed outside the
   original package repository from which it was obtained.
3. The Software may only be used within the legal entity that downloaded
   it and may not be shared with or used on behalf of third parties.
4. Any use of the Software outside these terms requires a separate license
   agreement.
5. All copies must retain the above copyright notice and this permission
   notice.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```
