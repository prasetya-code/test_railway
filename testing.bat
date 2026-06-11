@echo off
setlocal EnableExtensions

echo ==================================
echo Running DJLint Reformat...
echo ==================================
djlint app --reformat

echo.
echo ==================================
echo Running Stylint Fix...
echo ==================================

pushd node
echo Go to node directory

call npm run fix_css

echo.
echo Go back to root directory
popd

echo.
echo ==================================
echo Running Ruff Auto Fix...
echo ==================================
ruff check --fix .

echo.
echo ==================================
echo Running Ruff Format...
echo ==================================
ruff format .

echo.
echo ==================================
echo Running Ruff Recheck...
echo ==================================
ruff check .

echo.
echo ==================================
echo Running Pytest...
echo ==================================
echo.
pytest

echo.
echo ==================================
echo All tests passed successfully!
echo ==================================
exit /b 0


:error
echo.
echo ==================================
echo ERROR: Build / tests failed!
echo ==================================
exit /b 1