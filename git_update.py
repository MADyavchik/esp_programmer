import subprocess

def update_repo():
    try:
        print("[UPDATE] Выполняю git pull...")
        # Выполнение команды git pull
        result = subprocess.run(['git', 'pull', 'origin', 'main'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[UPDATE] Результат:\n{result.stdout.decode()}")
        if result.returncode == 0:
            print("[UPDATE] Обновление прошло успешно.")
        else:
            print(f"[UPDATE] Ошибка при обновлении:\n{result.stderr.decode()}")
    except Exception as e:
        print(f"[UPDATE] Ошибка при выполнении git pull: {str(e)}")
