import subprocess

# Функция для обновления репозитория
def update_repo():
    try:
        print("[GIT] Выполняю git pull...")
        # Запускаем команду git pull
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)

        if result.returncode == 0:
            print("[GIT] Репозиторий успешно обновлен!")
        else:
            print(f"[GIT] Ошибка при обновлении: {result.stderr}")
    except Exception as e:
        print(f"[GIT] Ошибка: {e}")
