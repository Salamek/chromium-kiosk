import sys

major, minor, _, _, _ = sys.version_info

python_version = '{}.{}'.format(major, minor)
python_version_up = '{}.{}'.format(major, minor + 1)


with open('PKGBUILD.tmpl', 'r', encoding='utf-8') as f:
    result = f.read().replace('{{python_version}}', python_version).replace('{{python_version_up}}', python_version_up)
    with open('PKGBUILD', 'w') as fo:
        fo.write(result)
