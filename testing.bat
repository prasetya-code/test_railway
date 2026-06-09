@echo off
setlocal

echo ==================================
echo Running DJLint Reformat...
echo ==================================
djlint app --reformat || goto :error

echo.
echo ==================================
echo Running Stylint Fix...
echo ==================================

pushd node || goto :error
echo Go to node directory

call npm run fix_css || goto :error

echo.
echo Go back to root directory
popd

echo.
echo ==================================
echo Running Ruff Auto Fix...
echo ==================================
ruff check --fix . || goto :error

echo.
echo ==================================
echo Running Ruff Format...
echo ==================================
ruff format . || goto :error

echo.
echo ==================================
echo Running Ruff Recheck...
echo ==================================
ruff check . || goto :error

echo.
echo ==================================
echo Running Pytest...
echo ==================================
pytest || goto :error

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