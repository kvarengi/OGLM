#!/bin/bash
# OGLM Azimuth Terminal Launcher
# Работает на Mac, Linux, Termux

echo "🚀 Launching OGLM Azimuth Terminal..."
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден"
    echo "   Установите Python 3.6+ и попробуйте снова"
    exit 1
fi

# Проверка версии Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.6"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "❌ Python $PYTHON_VERSION слишком старый"
    echo "   Нужен Python $REQUIRED_VERSION или новее"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION найден"
echo ""

# Определяем директорию скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TERMINAL_SCRIPT="$SCRIPT_DIR/azimuth_terminal.py"

# Проверка файла терминала
if [ ! -f "$TERMINAL_SCRIPT" ]; then
    echo "❌ azimuth_terminal.py не найден"
    echo "   Убедитесь, что вы в правильной директории"
    exit 1
fi

# Делаем исполняемым
chmod +x "$TERMINAL_SCRIPT"

# Запускаем
echo "🌊 Starting terminal..."
echo ""
python3 "$TERMINAL_SCRIPT" "$@"

