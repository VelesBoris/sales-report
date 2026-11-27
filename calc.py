import csv
from collections import Counter

DEFAULT_PATH = "data/sales.csv"


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


def main():
    rows = read_rows(DEFAULT_PATH)
    known, unknown = split_unknown(rows)
    if unknown:
        print("ПРЕДУПРЕЖДЕНИЕ: неизвестных статусов: %d" % len(unknown))
    unique, duplicates = dedupe(known)

    print("Прочитано строк:", len(rows))
    print("Неизвестных статусов:", len(unknown))
    print("Дублей удалено:", len(duplicates))
    print("Уникальных заказов:", len(unique))
    print("Проверка баланса:", len(rows) == len(unique) + len(duplicates) + len(unknown))
    print("Исходный статус -> итоговый:")
    counts = Counter((r["status_raw"], r["status_norm"]) for r in rows)
    for (raw, norm), n in sorted(counts.items(), key=lambda x: (x[0][1], x[0][0])):
        print("  %r -> %s: %d" % (raw, norm, n))



if __name__ == "__main__":
    main()