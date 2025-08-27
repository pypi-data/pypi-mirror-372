# Setup the development env unix
```sh
virtualenv venv
. ./venv/bin/activate
```

# Setup the development env win10
```sh
python -m venv venv
. .\venv\Scripts\activate
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python.exe -m pip install --upgrade pip
pip install pytest
pip install python-dotenv
pip install requests
pip install pydantic
copy .\.env.template .\.env
```
# Before publish the packages
```sh
pip install --upgrade pip
pip install --upgrade setuptools wheel
pip install twine
```
# How to cleanup generated files to publish
```powershell
Remove-Item .\build\ -Force -Recurse
Remove-Item .\dist\ -Force -Recurse
Remove-Item .\hnt_nf_jira_library.egg-info\ -Force -Recurse
```
# Before publish the packages
```sh
pip install --upgrade pip
pip install --upgrade setuptools wheel
pip install twine
```
# How to publish the package to test.pypi.org
```sh
python setup.py sdist bdist_wheel
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

# How to publish the package to pypi.org (username/password see lastpass Pypi)
```sh
python setup.py sdist bdist_wheel
python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```
