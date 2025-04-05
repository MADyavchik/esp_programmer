# ESP Programmer for Raspberry Pi Zero 2 W

⚡ Автономный программатор для ESP32 на базе Raspberry Pi Zero 2 W.

## Возможности:
- Выбор и прошивка .bin-файлов на ESP32
- Управление через I2C-дисплей и кнопки
- Обновление прошивок и скриптов по Wi-Fi (через git или по API)

## Структура проекта:
esp_programmer/

├── esp/

├── ui/

├── updater/

├── firmware/

└── main.py

## 🚀 Запуск:
```bash
python3 main.py

---

## 📄 `requirements.txt`

```txt
esptool
gpiozero
adafruit-circuitpython-ssd1306
requests

