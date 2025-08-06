@echo off
setlocal enabledelayedexpansion

echo 🚀 Setting up Mermaid to PDF Converter...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.7+ first.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✅ Python %python_version% detected

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r scripts\requirements.txt

REM Create output directory
if not exist "output" mkdir output

echo ✅ Setup completed successfully!
echo.
echo 📋 Usage:
echo    python scripts\simple_pdf_converter.py docs\flow-diagram.md
echo    python scripts\simple_pdf_converter.py docs\flow-diagram.md custom_output_dir
echo.
echo 🎯 Converting diagrams now...

REM Convert the flow diagram
if exist "docs\flow-diagram.md" (
    python scripts\simple_pdf_converter.py docs\flow-diagram.md
    echo.
    echo 🎉 Conversion completed! Check the 'output' directory for PDF files.
) else (
    echo ⚠️  docs\flow-diagram.md not found. Please run the conversion manually:
    echo    python scripts\simple_pdf_converter.py ^<your-markdown-file^>
)

pause 