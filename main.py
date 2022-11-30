import tg_api_connector


def main() -> None:
    tg_api_connector.start_long_polling()


if __name__ == '__main__':
    main()
