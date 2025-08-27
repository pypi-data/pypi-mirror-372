# lzl_pytools

```shell
python3 -m venv .pyenv
pip install --upgrade setuptools wheel twine

rm -rf build
rm -rf dist

python3 setup.py sdist bdist_wheel
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ your-package-name

# 测试发布
twine upload --config-file ~/.pypirc --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ lzl-pytools

# 正式发布
twine upload --config-file ~/.pypirc dist/*
https://pypi.org/project/lzl-pytools/0.1.0/
pip install lzl-pytools --index-url https://pypi.org/simple/
```