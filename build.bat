@echo off
md build
for /d /r src\ %%i in (*) do (
	call :makedir %%i
)
for /r src\ %%i in (*.py) do (
	call :compile %%i
)
pause

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
