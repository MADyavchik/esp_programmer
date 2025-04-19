# utils.py
import time
import traceback
from your_error_logger import log_error  # если есть логгер, иначе пиши прямо тут

def log_async(func):
    async def wrapper(*args, **kwargs):
        print(f"🟢 START {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            print(f"✅ END {func.__name__}")
            return result
        except Exception as e:
            print(f"❌ ERROR in {func.__name__}: {e}")
            traceback.print_exc()
            log_error(e)
            raise
    return wrapper
