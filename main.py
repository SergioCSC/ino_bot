import tg_api_connection


def main() -> None:
    tg_api_connection.start_long_polling()


if __name__ == '__main__':
    main()
