# Bank Widget

`Bank Widget` — учебный проект для анализа банковских транзакций с разбиением на:

- веб-представления (`views.py`);
- сервисные функции (`services.py`);
- отчеты (`reports.py`);
- утилиты чтения/подготовки данных.

Проект использует `pandas`, `requests`, `pytest` и покрывает сценарии из курсового задания: страницы «Главная» и «События», сервисы поиска/кешбэка/инвесткопилки, а также отчеты по тратам.

## Каталог товаров (`Product`, `Category`)

Реализованы классы для учебного задания по ООП:

- `src/product.py` — товар (`name`, `description`, `price`, `quantity`);
- `src/category.py` — категория (`name`, `description`, `products`) с атрибутами класса `category_count` и `product_count`, которые обновляются при создании объекта;
- `src/utils/products_loader.py` — загрузка категорий и товаров из `data/products.json`.

Пример:

```python
from src.category import Category
from src.product import Product
from src.utils.products_loader import load_categories_from_json

product = Product("Наушники", "Беспроводные", 19990.0, 8)
category = Category("Аудио", "Звуковая техника", [product])

categories = load_categories_from_json("data/products.json")
print(Category.category_count, Category.product_count)
```

## Структура

Основные новые модули:

- `src/views.py` — JSON-ответы для страниц «Главная» и «События»;
- `src/services.py` — сервисные функции:
  - выгодные категории кешбэка,
  - инвесткопилка,
  - простой поиск,
  - поиск по телефону,
  - поиск переводов физлицам;
- `src/reports.py` — отчеты и декоратор сохранения результата в файл;
- `tests/test_views.py`, `tests/test_services.py`, `tests/test_reports.py` — тесты для новых модулей;
- `tests/test_product_category.py` — тесты для `Product`, `Category` и загрузки из JSON.

## Установка

```bash
git clone <repo_url>
cd bank_widget_2
poetry install
```

## Веб-страницы (`src/views.py`)

### `home_page(date_time, data, settings_path="user_settings.json") -> str`

Возвращает JSON для страницы «Главная»:

- `greeting` (утро/день/вечер/ночь);
- `cards` (последние 4 цифры, сумма расходов, кешбэк);
- `top_transactions` (топ-5 по убыванию суммы);
- `currency_rates`;
- `stock_prices`.

Входная дата: `YYYY-MM-DD HH:MM:SS`.  
Диапазон данных: от начала месяца до входящей даты.

### `events_page(date_time, data, range_key="M", settings_path="user_settings.json") -> str`

Возвращает JSON для страницы «События»:

- `expenses`:
  - `total_amount`,
  - `main` (топ-7 категорий + `Остальное`),
  - `transfers_and_cash` (категории `Наличные` и `Переводы`);
- `income`:
  - `total_amount`,
  - `main`;
- `currency_rates`;
- `stock_prices`.

Поддерживаемые диапазоны `range_key`: `W`, `M`, `Y`, `ALL`.

## Сервисы (`src/services.py`)

- `cashback_categories(data, year, month) -> str`  
  JSON по категориям с потенциальным кешбэком (топ-3).

- `investment_bank(month, transactions, limit) -> float`  
  Расчет отложенной суммы при округлении трат до `limit`.

- `simple_search(data, query) -> str`  
  Поиск по подстроке в `Категория`/`Описание` (регистронезависимый).

- `search_by_phone_numbers(data) -> str`  
  Поиск транзакций с мобильными номерами (форматы `+7 (...)` и `8...`).

- `search_personal_transfers(data) -> str`  
  Поиск переводов физлицам (`Категория == "Переводы"` и шаблон `Имя Ф.`).

## Отчеты (`src/reports.py`)

Декоратор:

- `@report_to_file()` — сохраняет результат в файл с именем по умолчанию;
- `@report_to_file("custom_name.json")` — сохраняет в указанный файл.

Функции отчетов:

- `spending_by_category(transactions, category, date=None) -> pd.DataFrame`
- `spending_by_weekday(transactions, date=None) -> pd.DataFrame`
- `spending_by_workday(transactions, date=None) -> pd.DataFrame`

Если дата не передана, берется текущая. Анализ — за последние 3 месяца.

## Пользовательские настройки

Пример `user_settings.json`:

```json
{
  "user_currencies": ["USD", "EUR"],
  "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
}
```

## Тестирование

```bash
poetry run pytest -q
```

Покрытие:

```bash
poetry run pytest --cov=src --cov-report=term-missing
```

## Пример использования

```python
import json

from src.views import home_page

response = home_page("2024-01-20 10:00:00", data, settings_path="user_settings.json")
payload = json.loads(response)
print(payload["greeting"])
```
