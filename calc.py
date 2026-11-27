import csv
import os
import sys
from collections import defaultdict

DEFAULT_PATH = "data/sales.csv"
OUTPUT_PATH = os.path.join("output", "daily_by_sku.csv")


def normalize_status(raw):
    s = (raw or "").strip().lower()
    if s.startswith("cancel"):
        return "cancelled"
    if s.startswith("deliver"):
        return "delivered"
    return "unknown"


def read_rows(path):
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            row["line"] = line_no
            row["status_raw"] = row["status"]
            row["status_norm"] = normalize_status(row["status"])
            rows.append(row)
    return rows


def split_unknown(rows):
    known = [r for r in rows if r["status_norm"] != "unknown"]
    unknown = [r for r in rows if r["status_norm"] == "unknown"]
    return known, unknown


def dedupe(rows):
    seen = {}
    unique = []
    duplicates = []
    for r in rows:
        key = r["order_id"]
        if key in seen:
            duplicates.append(r)
            first = seen[key]
            for col in ("order_date", "sku", "quantity", "price", "status_norm"):
                if first[col] != r[col]:
                    print("ПРЕДУПРЕЖДЕНИЕ: order_id %s: строка %d отличается от строки %d (поле %s)"
                          % (key, r["line"], first["line"], col))
                    break
        else:
            seen[key] = r
            unique.append(r)
    return unique, duplicates


def split_data_errors(rows):
    ok = []
    errors = []
    for r in rows:
        if r["status_norm"] == "delivered" and (r["quantity"] or "").strip() == "":
            errors.append(r)
        else:
            ok.append(r)
    return ok, errors


def aggregate(rows):
    order_ids = defaultdict(set)
    revenue = defaultdict(int)
    for r in rows:
        key = (r["sku"], r["order_date"])
        order_ids[key].add(r["order_id"])
        if r["status_norm"] == "delivered":
            revenue[key] += int(r["quantity"]) * int(r["price"])
    result = []
    for key in sorted(order_ids):
        sku, date = key
        result.append((sku, date, len(order_ids[key]), revenue[key]))
    return result


def write_result(result, path=OUTPUT_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sku", "order_date", "orders", "revenue"])
        writer.writerows(result)


def print_control_totals(rows, unknown, duplicates, errors, valid, result):
    total_orders = sum(r[2] for r in result)
    total_revenue = sum(r[3] for r in result)
    accounted = len(valid) + len(duplicates) + len(unknown) + len(errors)
    print("--- Контрольные цифры ---")
    print("Прочитано строк:", len(rows))
    print("Дублей:", len(duplicates))
    print("Неизвестных статусов:", len(unknown))
    print("Ошибок данных (delivered без quantity):", len(errors))
    print("Уникальных заказов в расчёте:", len(valid))
    print("Строк в результате:", len(result))
    print("Сумма orders:", total_orders)
    print("Сумма revenue:", total_revenue)
    print("Баланс (прочитано = учтено + дубли + неизвестные + ошибки):",
          len(rows) == accounted)
    print("Сумма orders = уникальных заказов:", total_orders == len(valid))
    print("Статусы после нормализации (строк):")
    for norm in ("delivered", "cancelled", "unknown"):
        total = sum(1 for r in rows if r["status_norm"] == norm)
        odd = sum(1 for r in rows if r["status_norm"] == norm and r["status_raw"] != norm)
        print("  %s: %d (нестандартное написание: %d)" % (norm, total, odd))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
    if not os.path.isfile(path):
        print("ОШИБКА: входной файл не найден: %s" % path)
        sys.exit(1)
    os.makedirs("output", exist_ok=True)
    os.makedirs("errors", exist_ok=True)

    rows = read_rows(path)
    known, unknown = split_unknown(rows)
    if unknown:
        print("ПРЕДУПРЕЖДЕНИЕ: неизвестных статусов: %d" % len(unknown))
    unique, duplicates = dedupe(known)
    valid, errors = split_data_errors(unique)
    if errors:
        print("ПРЕДУПРЕЖДЕНИЕ: delivered без quantity, исключено: %d" % len(errors))
    result = aggregate(valid)
    write_result(result)
    print_control_totals(rows, unknown, duplicates, errors, valid, result)

if __name__ == "__main__":
    main()