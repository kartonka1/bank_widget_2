# Bank Widget

Проект **Bank Widget** предназначен для работы с банковскими операциями клиента.  
Он позволяет маскировать номера карт и счетов, фильтровать и сортировать транзакции,  
а также эффективно работать с большими массивами данных с помощью генераторов.

---

##  Установка

Клонируйте репозиторий:

```bash
git clone https://github.com/kartonka1/bank_widget.git
Перейдите в папку проекта и установите зависимости:

bash
Копировать код
cd bank_widget
poetry install
Запуск основного файла:

bash
Копировать код
poetry run python main.py
 Функции проекта
 mask_account_card(data: str) -> str
Принимает строку с типом и номером карты или счёта, возвращает замаскированный номер.

Примеры:

python
Копировать код
mask_account_card("Visa Platinum 7000792289606361")
# "Visa Platinum 7000 79** **** 6361"

mask_account_card("Счет 73654108430135874305")
# "Счет **4305"
 get_date(date_str: str) -> str
Конвертирует дату ISO-формата в формат ДД.ММ.ГГГГ.

python
Копировать код
get_date("2024-03-11T02:26:18.671407")
# "11.03.2024"
 get_mask_card_number(card_number: int) -> str
Маскирует номер банковской карты.

 get_mask_account(account_number: int) -> str
Маскирует номер банковского счёта.

 filter_by_state(operations, state="EXECUTED")
Фильтрует операции по полю state.

 sort_by_date(operations, reverse=True)
Сортирует операции по дате (по умолчанию — по убыванию).

 Модуль generators
Модуль содержит функции и генераторы для обработки больших массивов транзакций.

 filter_by_currency(transactions, currency)
Возвращает итератор, который выдаёт транзакции с указанной валютой.

Пример:

python
Копировать код
usd_tx = filter_by_currency(transactions, "USD")
print(next(usd_tx))
print(next(usd_tx))
 transaction_descriptions(transactions)
Генератор, который последовательно выдаёт описания операций.

Пример:

python
Копировать код
for desc in transaction_descriptions(transactions):
    print(desc)
 card_number_generator(start, stop)
Генератор номеров карт в формате:

nginx
Копировать код
XXXX XXXX XXXX XXXX
Пример:

python
Копировать код
for num in card_number_generator(1, 5):
    print(num)
 Тестирование
В проекте используются:

pytest

pytest-cov

отчёт покрытия создаётся в формате HTML

Запуск тестов:

bash
Копировать код
poetry run pytest
Запуск тестов с покрытием:

bash
Копировать код
poetry run pytest --cov=src --cov-report=html
После выполнения отчёт доступен в:

bash
Копировать код
htmlcov/index.html
 Покрытие тестами: 100%
Покрыты тестами:

masks.py

processing.py

widget.py

generators.py

 Лицензия
Проект предоставляется "как есть", без каких-либо гарантий.