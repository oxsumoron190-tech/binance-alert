import time
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.header import Header


# ============================================================
# НАСТРОЙКИ ПОЧТЫ
# ============================================================

# Ящик, с которого бот отправляет письма
EMAIL_FROM = "bernes.markusha@yandex.ru"

# Пароль приложения Яндекса
EMAIL_PASSWORD = "teleblussohzberj"

# Куда отправлять уведомления
EMAIL_TO = "bernes.markusha@yandex.ru"


# ============================================================
# НАСТРОЙКИ BINANCE
# ============================================================

SYMBOL_1 = "BZUSDT"
SYMBOL_2 = "CLUSDT"

# Проверять цены каждые N секунд
CHECK_INTERVAL = 30

# Binance USDⓈ-M Futures API
BINANCE_URL = "https://fapi.binance.com/fapi/v1/ticker/price"


# ============================================================
# ПОЛУЧЕНИЕ ЦЕНЫ
# ============================================================

def get_price(symbol):
    response = requests.get(
        BINANCE_URL,
        params={"symbol": symbol},
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return float(data["price"])


# ============================================================
# ОТПРАВКА EMAIL
# ============================================================

def send_email(price_bz, price_cl, difference, threshold):

    current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    subject = (
        f"Binance: разница BZUSDT и CLUSDT "
        f"больше {threshold:.2f} USDT"
    )

    body = f"""
СРАБОТАЛО УСЛОВИЕ BINANCE

Время: {current_time}

BZUSDT: {price_bz:.4f} USDT
CLUSDT: {price_cl:.4f} USDT

Разница:
{difference:.4f} USDT

Установленный порог:
{threshold:.4f} USDT

Условие:
BZUSDT - CLUSDT > {threshold:.4f} USDT
"""

    message = MIMEText(body, "plain", "utf-8")

    message["Subject"] = Header(subject, "utf-8")
    message["From"] = EMAIL_FROM
    message["To"] = EMAIL_TO

    with smtplib.SMTP_SSL(
        "smtp.yandex.ru",
        465,
        timeout=20
    ) as server:

        server.login(
            EMAIL_FROM,
            EMAIL_PASSWORD
        )

        server.sendmail(
            EMAIL_FROM,
            EMAIL_TO,
            message.as_string()
        )


# ============================================================
# ВВОД ПОРОГА
# ============================================================

def ask_threshold():

    while True:

        try:

            value = input(
                "\nВведите желаемую разницу "
                "между BZUSDT и CLUSDT в USDT: "
            )

            # Разрешаем ввод как 4.5, так и 4,5
            value = value.replace(",", ".")

            threshold = float(value)

            if threshold < 0:
                print("Порог не может быть отрицательным.")
                continue

            return threshold

        except ValueError:

            print(
                "Ошибка: введите число, например 4 "
                "или 4.5"
            )


# ============================================================
# ОСНОВНАЯ ПРОГРАММА
# ============================================================

def main():

    print("=" * 60)
    print("       BINANCE PRICE ALERT BOT")
    print("=" * 60)

    print()
    print("Мониторинг:")
    print(f"  {SYMBOL_1}")
    print(f"  {SYMBOL_2}")
    print()

    # Спрашиваем порог
    threshold = ask_threshold()

    print()
    print("=" * 60)
    print(f"Порог установлен: {threshold:.4f} USDT")
    print(f"Проверка каждые: {CHECK_INTERVAL} секунд")
    print(f"Email: {EMAIL_TO}")
    print("=" * 60)
    print()

    # False = письмо можно отправить
    # True  = письмо уже отправлено
    alert_sent = False

    while True:

        try:

            # Получаем цены
            price_bz = get_price(SYMBOL_1)
            price_cl = get_price(SYMBOL_2)

            # Считаем разницу
            difference = price_bz - price_cl

            current_time = datetime.now().strftime(
                "%d.%m.%Y %H:%M:%S"
            )

            print(
                f"[{current_time}] "
                f"BZUSDT: {price_bz:.4f} | "
                f"CLUSDT: {price_cl:.4f} | "
                f"Разница: {difference:.4f} | "
                f"Порог: {threshold:.4f}"
            )

            # ==================================================
            # УСЛОВИЕ СРАБОТАЛО
            # ==================================================

            if difference > threshold:

                if not alert_sent:

                    print()
                    print(
                        ">>> УСЛОВИЕ ВЫПОЛНЕНО!"
                    )

                    print(
                        ">>> Отправляю email..."
                    )

                    try:

                        send_email(
                            price_bz,
                            price_cl,
                            difference,
                            threshold
                        )

                        print(
                            ">>> Email успешно отправлен!"
                        )

                        alert_sent = True

                    except Exception as email_error:

                        print(
                            f">>> Ошибка отправки email: "
                            f"{email_error}"
                        )

                    print()

                else:

                    print(
                        ">>> Условие всё ещё выполнено. "
                        "Повторное письмо не отправляется."
                    )

            # ==================================================
            # УСЛОВИЕ СБРОСИЛОСЬ
            # ==================================================

            else:

                if alert_sent:

                    print(
                        ">>> Разница вернулась ниже "
                        "порога. Готов к следующему уведомлению."
                    )

                alert_sent = False

        except requests.exceptions.RequestException as error:

            print()
            print(
                f"Ошибка Binance/API: {error}"
            )
            print(
                "Повторная попытка через "
                f"{CHECK_INTERVAL} секунд..."
            )
            print()

        except Exception as error:

            print()
            print(
                f"Неожиданная ошибка: {error}"
            )
            print()

        # Ждём перед следующей проверкой
        time.sleep(CHECK_INTERVAL)


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == "__main__":
    main()