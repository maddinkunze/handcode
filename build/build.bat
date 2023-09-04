<NUL set /p="Building with " & python --version
python setup.py build
python finish.py
pause