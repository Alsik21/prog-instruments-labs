import csv
import re
from checksum import calculate_checksum, serialize_result

# 10 регулярных выражений для валидации данных
REGEX_EMAIL = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
REGEX_HTTP_STATUS = re.compile(r"^\d{3} [A-Za-z].*$")
REGEX_SNILS = re.compile(r"^\d{11}$")
REGEX_PASSPORT = re.compile(r"^\d{2} \d{2} \d{6}$")
REGEX_IP_V4 = re.compile(
    r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)
REGEX_LONGITUDE = re.compile(
    r"^-?(180(\.0+)?|1[0-7][0-9](\.[0-9]+)?|[0-9]{1,2}(\.[0-9]+)?)$"
)
REGEX_HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
REGEX_ISBN = re.compile(r"^(?:\d[- ]?){9}[\dXx]$|^(?:\d[- ]?){12}\d$")
REGEX_LOCALE_CODE = re.compile(r"^[a-z]{2,3}(-[a-z0-9]{2,4})?(_\d)?$")
REGEX_TIME = re.compile(r"^([01]\d|2[0-3]):[0-5]\d:[0-5]\d(\.\d{1,6})?$")

VALIDATORS = {
    "email": REGEX_EMAIL,
    "http_status_message": REGEX_HTTP_STATUS,
    "snils": REGEX_SNILS,
    "passport": REGEX_PASSPORT,
    "ip_v4": REGEX_IP_V4,
    "longitude": REGEX_LONGITUDE,
    "hex_color": REGEX_HEX_COLOR,
    "isbn": REGEX_ISBN,
    "locale_code": REGEX_LOCALE_CODE,
    "time": REGEX_TIME,
}


def validate_csv(file_path):
    invalid_row_numbers = []

    with open(file_path, mode="r", encoding="utf-16") as f:
        reader = csv.DictReader(f, delimiter=";")

        # ВАЖНО: start=0, так как первая строка с данными должна иметь номер 0!
        for row_num, row in enumerate(reader, start=0):
            is_valid = True
            for col_name, value in row.items():
                if col_name in VALIDATORS:
                    if not VALIDATORS[col_name].match(value):
                        is_valid = False
                        break

            if not is_valid:
                invalid_row_numbers.append(row_num)

    return invalid_row_numbers


def main():
    file_name = "1.csv"

    # 1. Получаем список номеров строк с ошибками
    invalid_rows = validate_csv(file_name)
    print(f"Найдено невалидных строк: {len(invalid_rows)}")

    # 2. Считаем контрольную сумму (MD5 хеш)
    checksum = calculate_checksum(invalid_rows)
    print(f"Контрольная сумма: {checksum}")

    # 3. Сохраняем результат (не забудь поменять номер варианта на свой!)
    my_variant = 1
    serialize_result(my_variant, checksum)

    print("Результат сохранен в result.json")


if __name__ == "__main__":
    main()
