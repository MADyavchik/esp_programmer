# utils.py
import time
import traceback
import asyncio
import functools
import inspect

def log_error(e):
    with open("error.log", "a") as f:
        f.write(f"{time.ctime()}: {repr(e)}\n")
        traceback.print_exc(file=f)

def safe_async(coro_func):
    try:
        loop = asyncio.get_running_loop()
        loop.call_soon_threadsafe(lambda: asyncio.create_task(coro_func()))
    except RuntimeError:
        print("⚠️ Нет активного event loop для safe_async")

def log_async(func):
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        print(f"🚀 Старт async: {func.__name__}")
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"💥 Ошибка в {func.__name__}: {e}")
            log_error(e)
            raise
        finally:
            print(f"✅ Завершено: {func.__name__}")
    return async_wrapper
