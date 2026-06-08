@echo off
setlocal

echo ==================================
echo Running DJLint Lint...
echo ==================================
djlint app --lint
if errorlevel 1 goto :error

echo ==================================
echo Running DJLint Check...
echo ==================================
djlint app --check
if errorlevel 1 goto :error

echo ==================================
echo Running DJLint Reformat...
echo ==================================
djlint app --reformat
if errorlevel 1 goto :error

::echo ==================================
::echo Running Stylint...
::echo ==================================
::stylint .
::if errorlevel 1 goto :error

echo ==================================
echo Running Ruff Auto Fix...
echo ==================================
ruff check --fix .
if errorlevel 1 goto :error

echo ==================================
echo Running Ruff Format...
echo ==================================
ruff format .
if errorlevel 1 goto :error

echo ==================================
echo Running Ruff Recheck...
echo ==================================
ruff check .
if errorlevel 1 goto :error

echo ==================================
echo Running Pytest...
echo ==================================
pytest
if errorlevel 1 goto :error

echo.
echo ==================================
echo All tests passed successfully!
echo ==================================
exit /b 0

:error
echo.
echo ==================================
echo Testing failed!
echo ==================================
exit /b 1