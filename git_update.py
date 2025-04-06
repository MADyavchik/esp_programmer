import subprocess
import os
import sys

# Функция для обновления репозитория
def update_repo():
    try:
        print("[GIT] Выполняю git pull...")
        # Запускаем команду git pull
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)

        if result.returncode == 0:
            print("[GIT] Репозиторий успешно обновлен!")

            # Перезапуск программы только после успешного обновления
            print("[GIT] Перезапуск программы...")
            os.execv(sys.executable, ['python3'] + sys.argv)  # Перезапуск текущего скрипта (main.py)
        else:
            print(f"[GIT] Ошибка при обновлении: {result.stderr}")

    except Exception as e:
        print(f"[GIT] Ошибка: {e}")
