# Foodgram — продуктовый помощник

**Foodgram** — веб-приложение для публикации и хранения кулинарных рецептов.

Пользователи могут создавать рецепты, просматривать рецепты других авторов, добавлять понравившиеся блюда в избранное и формировать список покупок из необходимых ингредиентов.

## Возможности проекта

- Регистрация и авторизация пользователей.
- Создание, просмотр, редактирование и удаление рецептов.
- Загрузка изображений готовых блюд.
- Поиск рецептов по тегам и авторам.
- Добавление рецептов в избранное.
- Подписка на авторов и просмотр их рецептов.
- Добавление рецептов в список покупок.
- Скачивание списка покупок с суммарным количеством ингредиентов.
- Получение коротких ссылок на рецепты.
- REST API для взаимодействия с приложением.

## Стек технологий

**Backend:**
- Python 3.12
- Django
- Django REST Framework
- Djoser
- PostgreSQL 16
- Gunicorn

**Frontend:**
- React
- JavaScript
- HTML
- CSS

**Инфраструктура:**
- Docker
- Docker Compose
- Nginx 1.25.4
- Git и GitHub

## Развёрнутый проект

**Foodgram доступен по адресу:** http://51.250.1.60/

Приложение развёрнуто на удалённом сервере с использованием Docker Compose, PostgreSQL, Gunicorn и Nginx.

**Административная панель:** http://51.250.1.60/admin/

## Запуск проекта через Docker

Для запуска приложения необходимо установить Docker с поддержкой Docker Compose.

### 1. Клонирование репозитория

```bash
git clone https://github.com/Katrin7828/foodgram.git
cd foodgram
```

### 2. Настройка переменных окружения

Перейдите в директорию `infra`:

```bash
cd infra
```

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Укажите собственные значения пароля PostgreSQL и секретного ключа Django.

Пример содержимого `.env`:

```dotenv
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=your_secure_password
DB_HOST=db
DB_PORT=5432

SECRET_KEY=your_unique_django_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,backend
CSRF_TRUSTED_ORIGINS=http://localhost:8080

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0

EMAIL_HOST=localhost
EMAIL_PORT=25
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=False
```

Файл `.env` содержит конфиденциальные настройки и не должен добавляться в Git.

### 3. Запуск контейнеров

Находясь в директории `infra`, выполните:

```bash
docker compose up -d
```

Docker Compose запускает следующие сервисы:

- `db` — база данных PostgreSQL.
- `backend` — Django API.
- `frontend` — клиентская часть приложения.
- `nginx` — веб-сервер для обработки запросов и раздачи статических файлов.

### 4. Применение миграций

```bash
docker compose exec backend python manage.py migrate
```

### 5. Сбор статических файлов

```bash
docker compose exec backend python manage.py collectstatic --noinput
```

### 6. Создание администратора

```bash
docker compose exec backend python manage.py createsuperuser
```

После выполнения команд приложение будет доступно по адресу:

**http://localhost:8080/**

Административная панель Django:

**http://localhost:8080/admin/**

## Заполнение базы данных

В директории `data` находятся файлы с ингредиентами:

- `ingredients.csv` — ингредиенты в формате CSV.
- `ingredients.json` — ингредиенты в формате JSON.

Каждый ингредиент содержит название и единицу измерения.

Пример данных из `ingredients.csv`:

```csv
абрикосовое варенье,г
абрикосовое пюре,г
абрикосовый сок,мл
авокадо,г
```

Перед использованием приложения необходимо загрузить ингредиенты в базу данных PostgreSQL.

Способ импорта зависит от формата данных и предусмотренного в проекте механизма загрузки. Файлы CSV и JSON служат исходными наборами данных; они не загружаются в PostgreSQL автоматически при запуске контейнеров.

## Документация API

Документация API находится в директории `docs`.

При корректной настройке Nginx документация доступна по адресу:

**http://localhost:8080/api/docs/**

API предоставляет возможности для работы с пользователями, рецептами, ингредиентами, тегами, подписками, избранным и списком покупок.

## Примеры API-запросов

### Получение списка рецептов

**GET** `/api/recipes/`

Пример ответа:

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "tags": [
        {
          "id": 1,
          "name": "Завтрак",
          "slug": "breakfast"
        }
      ],
      "author": {
        "id": 1,
        "username": "user",
        "first_name": "Иван",
        "last_name": "Иванов",
        "email": "user@example.com",
        "is_subscribed": false,
        "avatar": null
      },
      "ingredients": [
        {
          "id": 1,
          "name": "Молоко",
          "measurement_unit": "мл",
          "amount": 200
        }
      ],
      "is_favorited": false,
      "is_in_shopping_cart": false,
      "name": "Молочная каша",
      "image": "http://localhost:8080/media/recipes/example.png",
      "text": "Смешать ингредиенты и приготовить кашу.",
      "cooking_time": 15
    }
  ]
}
```

### Получение списка ингредиентов

**GET** `/api/ingredients/`

Пример ответа:

```json
[
  {
    "id": 1,
    "name": "Абрикосовое варенье",
    "measurement_unit": "г"
  },
  {
    "id": 2,
    "name": "Абрикосовое пюре",
    "measurement_unit": "г"
  }
]
```

### Создание рецепта

**POST** `/api/recipes/`

Для выполнения запроса необходима авторизация.

Пример тела запроса:

```json
{
  "ingredients": [
    {
      "id": 1,
      "amount": 200
    }
  ],
  "tags": [1],
  "image": "data:image/png;base64,iVBORw0KGgo...",
  "name": "Новый рецепт",
  "text": "Описание приготовления.",
  "cooking_time": 20
}
```

При успешном создании рецепта сервер возвращает статус `201 Created` и данные созданного рецепта.

### Получение короткой ссылки на рецепт

**GET** `/api/recipes/1/get-link/`

Пример ответа:

```json
{
  "short-link": "http://localhost:8080/s/aB12Cd/"
}
```

### Получение списка подписок

**GET** `/api/users/subscriptions/`

Для выполнения запроса необходима авторизация.

Ответ содержит список авторов, на которых подписан пользователь, количество их рецептов и краткую информацию о рецептах.

Параметр `recipes_limit` позволяет ограничить количество рецептов каждого автора в ответе.

Пример:

```text
/api/users/subscriptions/?recipes_limit=2
```

## Автор проекта

**Екатерина Реутская**

GitHub: [Katrin7828](https://github.com/Katrin7828)
