# price.ru parser

Простейший парсер price.ru для обновления цен на жесткие диски в Google таблице.
Для сравнения дисков используется колонка Цена за терабайт с формулой "Цена/объем".

## Алгоритм работы

- Авторизоваться в API Google
- Открыть таблицу на нужном листе
- Получить все значения ячеек из столбца со ссылками и моделями (формула [HYPERLINK](https://support.google.com/docs/answer/3093313?hl=ru))
- Для каждой ссылки из списка
  - Получить html
  - Взять цену из title
  - Обновить цену на листе

## Настройки

Настройки считываются из переменных окружения, которые можно задать с помощью файла `.env` в папке скрипта.

- `TABLE_ID` - часть ссылки на таблицу между d/ и /edit
- `SHEET_TITLE` - название листа
- `TITLE_ROWS_COUNT` - количество строк с заголовками, которые нужно пропустить
- `URL_COL_NUM` - номер столбца со ссылками и моделями
- `PRICE_COL_LTR` - буква столбца с ценой

## Использование

Для запуска должен быть установлен Docker или Python 3.13+

### Подготовка

1. Клонировать репозиторий
1. Переименовать файл `.env.example` в `.env` и указать свои значения
1. Получить по [инструкции](https://gspread.readthedocs.io/en/latest/oauth2.html) реквизиты доступа к Google API и сохранить в файл `cred.json` в поддиректорию `price_ru` рядом с `app.py`

### Запуск в Docker

Можно воспользоваться командой `make`, а если `make` не установлен:

```console
docker build --tag price_ru .
docker run \
  --rm \
  --interactive \
  --tty \
  --env-file .env \
  --volume `pwd`:`pwd` \
  --workdir `pwd` \
  price_ru \
  python -m price_ru
docker rmi price_ru
```

### Запуск с системным Python

```console
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m price_ru
```

## Разработка

1. Клонировать репозиторий
1. `pip install -r requirements.dev.txt`
1. `pre-commit install`
