# AI Assistant Test Project

Небольшой Django-проект для прототипа AI-ассистента с API, обработкой документов и базовой пользовательской системой.

## Что уже есть

- Django + Django REST Framework как основа backend.
- Модули для загрузки и парсинга документов (`pdf`, `docx`, `doc`, `txt`, `csv`, `json`, `md/markdown`, `tsv`, `djvu`, `xls/xlsx`, `odt/ods`).
- Базовая доменная модель для базы знаний, документов и чанков.
- Зачатки AI-функциональности: эмбеддинги, чанкование и поиск по данным.
- Базовые пользовательские сущности, авторизация и permissions.

## Текущий статус разработки

Проект находится в стадии **активной разработки (MVP/прототип)**:

- ключевые модули и структура уже собраны;
- часть функционала реализована в базовом виде;
- требуется доработка бизнес-логики, интеграций и покрытие тестами.

## Быстрый старт (локально)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```


## Пользователи и администрирование

### Как создать первого администратора после запуска сервера

После `python manage.py migrate` и `python manage.py runserver` создайте суперпользователя Django:

```bash
python manage.py createsuperuser
```

Затем назначьте ему роль приложения (`group_type=admin`, `access_level=admin`), чтобы работали права из `users.permissions`:

```bash
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); u=User.objects.get(username='admin'); p=u.profile; p.group_type='admin'; p.access_level='admin'; p.save(); print('OK')"
```

Теперь этот пользователь может создавать новых пользователей через API:

- `POST /users/admin/users/` — создать пользователя;
- `PATCH /users/admin/users/<user_id>/role-access/` — изменить роль/уровень доступа;
- `DELETE /users/admin/users/<user_id>/` — деактивировать пользователя.

### Как добавлять новых пользователей

#### Вариант 1 (рекомендуется): через API под админом

1. Получите токен/авторизуйтесь администратором.
2. Отправьте запрос на создание пользователя:

```bash
curl -X POST http://127.0.0.1:8000/users/admin/users/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_user",
    "email": "new_user@example.com",
    "password": "StrongPass123!",
    "group_type": "standard",
    "access_level": "4",
    "is_active": true
  }'
```

#### Вариант 2: через Django shell (служебный/аварийный)

```bash
python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); u=User.objects.create_user(username='new_user', email='new_user@example.com', password='StrongPass123!'); p=u.profile; p.group_type='standard'; p.access_level='4'; p.save(); print(u.id)"
```

## Структура проекта (кратко)

- `config/` — настройки и маршрутизация Django-проекта.
- `core/` — базовая логика приложения и AI-пайплайн.
- `db_server/` — модели/сервисы базы знаний и документов.
- `parser_app/` — парсинг документов разных форматов.
- `users/` — пользователи, авторизация, permissions.
- `ai_assistent_app/` — API-слой для ассистента.
