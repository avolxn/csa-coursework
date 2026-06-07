# Курсовая работа: Результат теста

Каталог сдачи:

- `DB` — SQL-схема PostgreSQL, начальные данные и backup;
- `Documents` — пояснительная записка в `DOCX/PDF` и генератор отчета;
- `Source` — исходный код backend и frontend.

## Стек

- frontend: React + Vite
- backend: Python + FastAPI
- DB: PostgreSQL

## Запуск

Терминал 1:

```bash
cd Source/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Терминал 2:

```bash
cd Source/frontend
npm install
npm run dev
```

Открыть:

- frontend: <http://localhost:5173>
- Swagger UI: <http://127.0.0.1:8000/docs>

## Демо-доступ

- `admin@example.com` / `password`
- `maria.teacher@example.com` / `password`
- `anna@example.com` / `password`

Данные backend хранятся только в памяти и сбрасываются после перезапуска сервера. На клиенте в `localStorage` сохраняется только последний введенный email.

## База данных

В папке `DB` лежат:

- `schema.sql` — полная PostgreSQL-схема;
- `BIVT-24-4_Eldashov_VE_7.sql` — SQL-скрипт создания схемы и начальных данных;
- `BIVT-24-4_Eldashov_VE_7.dump` — backup PostgreSQL в формате `pg_dump -Fc`.

Пример восстановления:

```bash
createdb test_results_course
pg_restore -d test_results_course DB/BIVT-24-4_Eldashov_VE_7.dump
```