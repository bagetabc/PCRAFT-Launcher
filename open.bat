@echo off
title PCRAFT Launcher v5.0 - Liquid Glass Edition
color 0A
chcp 65001 >nul 2>&1

:: Получаем путь к папке со скриптом
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Устанавливаем кодировку
chcp 65001 >nul 2>&1

echo ============================================================
echo    PCRAFT MINECRAFT LAUNCHER - LIQUID GLASS EDITION
echo    Version 5.0.0
echo ============================================================
echo.

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не установлен!
    echo.
    echo Пожалуйста, установите Python 3.7 или выше с python.org
    echo.
    pause
    exit /b 1
)

:: Показываем версию Python
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python: %PYTHON_VERSION%

:: Проверка наличия основного скрипта
if not exist "pcraft_launcher.py" (
    echo [ОШИБКА] Файл pcraft_launcher.py не найден!
    echo.
    pause
    exit /b 1
)

:: Проверка Java
java -version >nul 2>&1
if errorlevel 1 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Java не найдена!
    echo Minecraft требует Java 8 или выше для работы.
    echo Скачать: https://adoptium.net/
    echo.
    choice /C YN /M "Продолжить запуск без Java"
    if errorlevel 2 exit /b 1
) else (
    echo [OK] Java установлена
)

echo.
echo [ЗАПУСК] Запуск PCRAFT Launcher...
echo.

:: Запуск лаунчера
python pcraft_launcher.py

:: Проверка кода выхода
if errorlevel 1 (
    echo.
    echo [ОШИБКА] Лаунчер завершился с ошибкой
    echo.
    echo Возможные решения:
    echo 1. Установите зависимости: pip install Pillow
    echo 2. Проверьте подключение к интернету
    echo 3. Перезапустите лаунчер от имени администратора
    echo.
)

echo.
echo Спасибо за использование PCRAFT Launcher!
pause