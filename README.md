# daily_by_sku

Скрипт `calc.py` читает выгрузку заказов `sales.csv` и строит `output/daily_by_sku.csv`: по каждой паре «sku — день» число уникальных заказов (`orders`, включая cancelled) и выручку по delivered (`revenue`).

## Как запустить

**Зависимости:** не нужны. Python 3.8+, только стандартная библиотека.

1. Клонируйте репозиторий и перейдите в его папку:
   ```
   git clone <адрес репозитория>
   cd <папка репозитория>
   ```
2.  Положите в папку `data` выгрузку как `data/sales.csv`. Формат: CSV, UTF-8, запятая, колонки `order_id, order_date, sku, quantity, price, status`.
3. Запустите из папки репозитория:
   ```
   python calc.py
   ```
   или двойным кликом по `run.bat` (Windows). Другой путь к файлу: `python calc.py путь\к\файлу.csv`.

**Результат:** `output/daily_by_sku.csv` (колонки `sku, order_date, orders, revenue`, сортировка по sku, затем по дате). Контрольные цифры печатаются в консоль.