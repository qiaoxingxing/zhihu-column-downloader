@rem 作用：
@rem 用法：
@rem 其他：
@rem 2020/02/19 周三 23:44:03.49
@echo off&SetLocal EnableDelayEdexpansion&cd /d "%~dp0"
rem cmd.exe /K ""D:\program_files\miniconda\Scripts\activate.bat" "D:\program_files\miniconda""

set path=%path%;D:\program\miniconda\condabin
set PYTHONIOENCODING=UTF-8

set url=%~1
set title=%~2
echo %1
echo %2
title %title% - %url%

call D:/program/miniconda/Scripts/activate
python column_downloader.py "%url%" "%title%"
call conda deactivate

title done - %title% - %url%
echo %title%
echo %url%
pause
