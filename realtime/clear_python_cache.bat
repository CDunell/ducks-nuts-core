@echo off
echo [🧹] Clearing Python cache...

REM Delete all __pycache__ folders
for /r %%i in (.) do (
  if /i "%%~nxi"=="__pycache__" (
    echo Deleting: %%i
    rmdir /s /q "%%i"
  )
)

REM Delete all .pyc files
for /r %%f in (*.pyc) do (
  echo Deleting: %%f
  del /q "%%f"
)

REM Optional: Restart virtual environment
echo.
echo [✅] Python cache cleared.
echo [⚠️] Remember to reactivate your environment:
echo     .\.venv\Scripts\Activate.ps1

pause