# tg-scrape-comments

CLI для выгрузки **постов и комментариев** из публичных Telegram-каналов в **JSONL**  
Основано на [Telethon]. Авторизация — через ваш Telegram-аккаунт (номер → код → 2FA при наличии).

- Требования: Python ≥ 3.10
- ОС: Linux, macOS, Windows
- Команда CLI: `tg-scrape`
- Пакет на PyPI: `tg-scrape-comments`

## Установка

### Из PyPI
```bash
pip install tg-scrape-comments
```

### Из GitHub (без клонирования)
```bash
pip install "git+https://github.com/Frantsuzova/tg_scrape_comments@main"
```

### Локально из исходников
```bash
git clone https://github.com/Frantsuzova/tg_scrape_comments.git
cd tg_scrape_comments
pip install .
```

## Быстрый старт

1) Получите API ID и API HASH: https://my.telegram.org → **API development tools**.  
2) Запуск (первые 5 постов для проверки):
```bash
tg-scrape @durov --out-dir ./out --post-limit 5   --api-id 123456 --api-hash xxxxxxxxxxxxxxxxxxxxxxxx
```
При первом запуске будет интерактивный запрос телефона, кода и (при 2FA) пароля. Создастся файл сессии.

### Использование переменных окружения
```bash
# Linux/macOS
export TELEGRAM_API_ID=123456
export TELEGRAM_API_HASH=xxxxxxxxxxxxxxxxxxxxxxxx
tg-scrape @durov --out-dir ./out

# Windows PowerShell
$env:TELEGRAM_API_ID="123456"
$env:TELEGRAM_API_HASH="xxxxxxxxxxxxxxxxxxxxxxxx"
tg-scrape @durov --out-dir .\out
```

### Несколько каналов
```bash
# списком
tg-scrape @durov @telegram https://t.me/some_public_channel --out-dir ./out

# из файла (по одному адресу в строке: @name или https://t.me/name)
tg-scrape --channels-file channels.txt --out-dir ./out
```

## Результат

На каждый канал создаётся файл `posts_<username_или_id>.jsonl` в `--out-dir`.  
Каждая строка — один пост с агрегированными комментариями (если у канала есть связанный чат/форум).

Пример строки:
```json
{
  "channel_id": 1006503122,
  "channel_username": "durov",
  "post_id": 1234,
  "date_utc": "2025-08-27T10:15:00+00:00",
  "text": "Текст поста",
  "views": 12345,
  "forwards": 10,
  "reactions": [{"reaction":"👍","count":5},{"reaction":"🔥","count":2}],
  "reply_count": 42,
  "comments_count": 40,
  "comments_text": "Комментарий 1\n\nКомментарий 2\n\n…",
  "link": "https://t.me/durov/1234"
}
```

Быстрая проверка после запуска:
```bash
tg-scrape --help
ls -lh ./out
head -n 2 ./out/posts_*.jsonl
```

## Параметры CLI

```
tg-scrape [channels ...]
  --channels-file PATH      Путь к файлу со списком каналов (по одному в строке).
  --out-dir PATH            Куда писать *.jsonl (по умолчанию текущая папка).
  --session PATH_OR_NAME    Имя/путь файла сессии Telethon (по умолчанию tg_scrape_session).
  --api-id INT              Telegram API ID (или env TELEGRAM_API_ID).
  --api-hash STR            Telegram API HASH (или env TELEGRAM_API_HASH).
  --log-every INT           Прогресс каждые N постов (по умолчанию 200).
  --no-sleep-after-flood    Не ждать при FloodWaitError (по умолчанию ждёт).
  --post-limit INT          Ограничить число постов на канал (для быстрых тестов).
```

## Примечания и ограничения

- Работает с публичными каналами и их обсуждениями, доступными вашему аккаунту.
- Если у канала нет связанного чата/форума → `comments_count=0`, `comments_text=""`.
- Для каналов с Темами выполняется мэппинг поста на `top_id` треда.
- Telegram может возвращать `FloodWait` — по умолчанию ожидание включено; можно отключить флагом.
- Не публикуйте `API_HASH` и не коммитьте файлы `*.session`.

## Google Colab

В Colab используйте `%env`, а не `!export`:
```python
%env TELEGRAM_API_ID=123456
%env TELEGRAM_API_HASH=xxxxxxxxxxxxxxxxxxxxxxxx
```
Запуск:
```bash
!tg-scrape @durov --out-dir ./out --post-limit 5
```
Если интерактивный ввод кода не появляется, можно вызвать модуль напрямую из Python:
```python
import tg_scrape_comments.cli as cli
cli.main(["@durov","--out-dir","./out","--post-limit","5",
          "--api-id","123456","--api-hash","xxxxxxxxxxxxxxxxxxxxxxxx"])
```

## Частые вопросы

**Почему файл иногда называется `posts_<id>.jsonl`, а не `posts_<username>.jsonl`?**  
У каналов без `username` используется числовой `id`.

**Как ускорить проверку?**  
Флаг `--post-limit N` и выбор небольшого числа каналов.

**Можно выгружать только посты без комментариев?**  
Пока нет. Планируется флаг `--no-comments` в следующих версиях.

## Лицензия
MIT

[Telethon]: https://github.com/LonamiWebs/Telethon
