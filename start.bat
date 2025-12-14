@echo off
echo ========================================
echo Retail Beverage AI Assistant
echo ========================================
echo.
echo Database холболтыг шалгаж байна...
python test_connection.py
echo.
echo Серверийг эхлүүлж байна...
python run.py
pause

