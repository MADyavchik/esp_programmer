import subprocess

def update_repo():
    try:
        # Запуск git pull
        print("[UPDATE] Выполняю git pull...")
        process = subprocess.Popen(
            ['git', 'pull', 'origin', 'main'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate()  # Считываем вывод после выполнения команды
        if process.returncode == 0:
            return stdout.decode('utf-8'), None  # Возвращаем результат успешного выполнения
        else:
            return None, stderr.decode('utf-8')  # Возвращаем ошибку, если она есть
    except Exception as e:
        return None, str(e)  # Возвращаем исключение, если произошла ошибка
