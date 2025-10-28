import pathlib
import sys

major, minor, _, _, _ = sys.version_info

python_version = f"{major}.{minor}"
python_version_up = f"{major}.{minor + 1}"


with pathlib.Path("PKGBUILD.tmpl").open("r", encoding="utf-8") as f:
    result = f.read().replace("{{python_version}}", python_version).replace("{{python_version_up}}", python_version_up)
    with pathlib.Path("PKGBUILD").open("w") as fo:
        fo.write(result)
