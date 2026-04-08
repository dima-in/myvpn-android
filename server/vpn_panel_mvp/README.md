# VPN Panel MVP

Простая веб-панель для управления клиентами Xray/VLESS Reality.

## Что умеет

- список клиентов
- создание клиента
- генерация VLESS-ссылки
- генерация QR-кода
- отключение/включение клиента
- удаление клиента

## Стек

- FastAPI
- SQLite
- Jinja2
- qrcode
- uvicorn

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Открыть:
`http://127.0.0.1:8001`