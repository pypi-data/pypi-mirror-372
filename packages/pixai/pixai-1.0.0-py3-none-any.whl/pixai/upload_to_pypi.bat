@echo off
echo ==============================
echo   Build & Upload to PyPI
echo ==============================

REM --- SET ENVIRONMENT VARIABLES ---
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmcCJDJlZTU0NzNiLTg2NDEtNDYyNC05MWM0LTJhM2NkZjhmODI1NwACKlszLCIyMjI2NTRkZi01NDFmLTRhYWEtOWQzMC1hNjk0MmZiN2ZjMzQiXQAABiC-PmC1vJsHJsJeLtxsh7e1y_qCMpW50iZpHtLdr3HRLg
REM --- HAPUS FOLDER DIST SEBELUM BUILD ---
if exist dist rmdir /s /q dist

REM --- BUILD PACKAGE (SDIST & WHEEL) ---
python setup.py sdist bdist_wheel

REM --- UPLOAD KE PYPI ---
twine upload dist/*

pause
