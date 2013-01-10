@echo off
REM This is a convenient windows batch file for setting up enviroment

REM Use current directory for name of the project!!!
for %%* in (.) do set ParentDirName=%%~p*
for %%* in (.) do set CurrDirName=%%~n*
echo Current project name: %CurrDirName%

set PYTHON_ROOT=C:\Python27
set PROJECT_NAME=%CurrDirName%
set PROJECT_SETTINGS=%cd%\%PROJECT_NAME%\configs\local_settings.py

REM The name of the virtualenv when you ran:
REM virtualenv venv
set VIRTUALENV=%ParentDirName%venvs/%PROJECT_NAME%

REM Grab the parent of current 'CD' directory
for %%F in ("%CD%") do set PROJECTS_ROOT=%%~dpF

set PYTHONHOME=%PYTHON_ROOT%
set PROJECT_ROOT=%PROJECTS_ROOT%%PROJECT_NAME%

set PATH=%PATH%;%PROJECT_ROOT%scripts\windows

set PYTHONPATH=%PROJECTS_ROOT%;%PROJECT_ROOT%;%PROJECT_ROOT%\%CurrDirName%;%VIRTUALENV%\Lib\site-packages;%PYTHON_ROOT%;%PYTHON_ROOT%\Lib;%PYTHON_ROOT%\DLLs

cd %PROJECT_NAME%

REM Activate virtual environment
REM %PROJECT_ROOT%\%VIRTUALENV%\Scripts\activate.bat
%VIRTUALENV%\Scripts\activate.bat

