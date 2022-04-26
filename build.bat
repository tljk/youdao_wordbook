@echo off
md build
for /r build\ %%i in (*.mpy) do (
	call :delete %%i
)
for /d /r src\ %%i in (*) do (
	call :makedir %%i
)
for /r src\ %%i in (*.py) do (
	call :compile %%i
)
del build\boot.py
del build\boot.mpy
copy src\boot.py build\
copy src\*.fon build\

:makedir
set var=%1
set var=%var:src=build%
md %var%
goto :eof

:compile
set var=%1
set var=%var:src=build%
set var=%var:py=mpy%
mpy-cross %1 -o %var%
goto :eof

:delete
del %1
goto :eof