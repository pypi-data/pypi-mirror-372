import asyncio
import json
import os
import re
from pathlib import Path
from typing import Iterable, Optional, Sequence

from telethon import TelegramClient, functions, types, errors
from tqdm import tqdm
import argparse

# ---------- utils ----------
def norm_url(u: str) -> str:
    u = str(u or "").strip()
    if not u:
        return ""
    if u.startswith("@"):
        u = u[1:]
    if "t.me/" in u:
        return u if u.startswith("http") else "https://" + u
    return "https://t.me/" + u

def safe_name(s: str) -> str:
    s = s or ""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_") or "channel"

async def get_linked_chat(client: TelegramClient, channel_entity) -> Optional[types.Channel]:
    try:
        full = await client(functions.channels.GetFullChannelRequest(channel_entity))
        linked_id = getattr(full.full_chat, "linked_chat_id", None)
        if not linked_id:
            return None
        return await client.get_entity(types.PeerChannel(linked_id))
    except errors.ChannelPrivateError:
        return None
    except Exception:
        return None

async def get_thread_top_id(client: TelegramClient, channel_entity, post_id: int) -> Optional[int]:
    try:
        res = await client(functions.messages.GetDiscussionMessage(peer=channel_entity, msg_id=post_id))
        if getattr(res, "messages", None):
            return getattr(res.messages[0], "id", None)
        return None
    except (errors.MsgIdInvalidError, errors.ChannelPrivateError):
        return None
    except Exception:
        return None

async def iter_posts(client, entity, limit: Optional[int] = None) -> Iterable[types.Message]:
    count = 0
    async for m in client.iter_messages(entity, reverse=True):
        if isinstance(m, types.MessageService):
            continue
        yield m
        count += 1
        if limit is not None and count >= limit:
            break

async def iter_comments(client, discussion_entity, root_id: int) -> Iterable[types.Message]:
    async for cm in client.iter_messages(discussion_entity, reply_to=root_id, reverse=True):
        if isinstance(cm, types.MessageService):
            continue
        yield cm

# ---------- core ----------
async def scrape_one_channel(
    client: TelegramClient,
    channel_url: str,
    out_dir: Path,
    log_every: int = 200,
    sleep_after_flood: bool = True,
    post_limit: Optional[int] = None,
) -> Optional[Path]:
    url = norm_url(channel_url)
    if not url:
        print("! Пустой адрес.")
        return None

    print(f"\n== Канал: {url}")
    try:
        entity = await client.get_entity(url)
    except Exception as e:
        print(f"  ! Не удалось получить entity: {e}")
        return None

    uname = getattr(entity, "username", None)
    base = safe_name(uname or str(getattr(entity, "id", "channel")))
    out_path = out_dir / f"posts_{base}.jsonl"
    if out_path.exists():
        out_path.unlink()

    discussion = await get_linked_chat(client, entity)

    total_posts = 0
    with out_path.open("a", encoding="utf-8") as w:
        pbar = tqdm(desc=f"Посты {uname or getattr(entity,'id', '')}", unit="post")
        count_channel_posts = 0

        async for m in iter_posts(client, entity, limit=post_limit):
            comments_text_parts, comments_count = [], 0

            if discussion and (m.replies and m.replies.replies):
                try:
                    # прямая привязка по post_id (для каналов без Тем)
                    async for cm in iter_comments(client, discussion, m.id):
                        if cm.text:
                            comments_text_parts.append(cm.text)
                        comments_count += 1
                except errors.MsgIdInvalidError:
                    # мэппинг post -> top_id (для Тем)
                    top_id = await get_thread_top_id(client, entity, m.id)
                    if top_id:
                        while True:
                            try:
                                async for cm in iter_comments(client, discussion, top_id):
                                    if cm.text:
                                        comments_text_parts.append(cm.text)
                                    comments_count += 1
                                break
                            except errors.FloodWaitError as e:
                                wait_s = int(getattr(e, "seconds", 5))
                                print(f"  ! FloodWait {wait_s}s на тред поста {m.id}")
                                if sleep_after_flood:
                                    await asyncio.sleep(wait_s)
                                    continue
                                else:
                                    break
                except errors.FloodWaitError as e:
                    wait_s = int(getattr(e, "seconds", 5))
                    print(f"  ! FloodWait {wait_s}s на тред поста {m.id}")
                    if sleep_after_flood:
                        await asyncio.sleep(wait_s)
                        try:
                            async for cm in iter_comments(client, discussion, m.id):
                                if cm.text:
                                    comments_text_parts.append(cm.text)
                                comments_count += 1
                        except errors.MsgIdInvalidError:
                            top_id = await get_thread_top_id(client, entity, m.id)
                            if top_id:
                                async for cm in iter_comments(client, discussion, top_id):
                                    if cm.text:
                                        comments_text_parts.append(cm.text)
                                    comments_count += 1

            row = {
                "channel_id": getattr(entity, "id", None),
                "channel_username": uname,
                "post_id": m.id,
                "date_utc": m.date.isoformat() if getattr(m, "date", None) else None,
                "text": m.text or "",
                "views": m.views,
                "forwards": m.forwards,
                "reactions": (
                    [
                        {
                            "reaction": (
                                r.reaction.emoticon
                                if isinstance(r.reaction, types.ReactionEmoji)
                                else str(r.reaction)
                            ),
                            "count": r.count,
                        }
                        for r in (m.reactions.results if m.reactions else [])
                    ]
                ),
                "reply_count": m.replies.replies if m.replies else 0,
                "comments_count": comments_count,
                "comments_text": "\n\n".join(comments_text_parts),
                "link": (f"https://t.me/{uname}/{m.id}" if uname else None),
            }
            w.write(json.dumps(row, ensure_ascii=False) + "\n")

            count_channel_posts += 1
            total_posts += 1
            pbar.update(1)
            if count_channel_posts % max(1, log_every) == 0:
                pbar.set_postfix_str(f"всего={total_posts}")

        pbar.close()

    print(f"Готово: постов {total_posts}. Файл: {out_path}")
    return out_path

# ---------- CLI ----------
def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="tg-scrape",
        description="Выгрузка постов и комментариев Telegram (JSONL на канал).",
    )
    p.add_argument("channels", nargs="*", help="Список адресов каналов (@name или https://t.me/name).")
    p.add_argument("--channels-file", type=Path, help="Путь к файлу со списком каналов (по одному в строке).")
    p.add_argument("--out-dir", type=Path, default=Path("."), help="Куда писать *.jsonl (по умолчанию текущая папка).")
    p.add_argument("--session", default="tg_scrape_session", help="Имя/путь файла сессии Telethon.")
    p.add_argument("--api-id", type=int, help="Telegram API ID (если не задан, берётся из env TELEGRAM_API_ID).")
    p.add_argument("--api-hash", help="Telegram API HASH (или env TELEGRAM_API_HASH).")
    p.add_argument("--log-every", type=int, default=200, help="Показывать прогресс каждые N постов.")
    p.add_argument("--no-sleep-after-flood", action="store_true", help="Не ждать при FloodWaitError.")
    p.add_argument("--post-limit", type=int, help="Ограничить число постов на канал (для быстрых тестов).")
    return p.parse_args(argv)

def load_channels(args: argparse.Namespace) -> list[str]:
    channels: list[str] = []
    channels.extend(args.channels or [])
    if args.channels_file:
        if not args.channels_file.exists():
            raise FileNotFoundError(f"channels-file not found: {args.channels_file}")
        with args.channels_file.open("r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s:
                    channels.append(s)
    if not channels:
        raise SystemExit("Не заданы каналы. Укажите позиционные аргументы или --channels-file.")
    return channels

async def async_entry(args: argparse.Namespace) -> int:
    api_id = args.api_id or int(os.environ.get("TELEGRAM_API_ID", "0"))
    api_hash = args.api_hash or os.environ.get("TELEGRAM_API_HASH", "")

    if not api_id or not api_hash:
        raise SystemExit("Нужны API ID/HASH. Передайте --api-id/--api-hash или задайте env TELEGRAM_API_ID/TELEGRAM_API_HASH.")

    args.out_dir.mkdir(parents=True, exist_ok=True)

    client = TelegramClient(args.session, api_id, api_hash)
    await client.start()  # при 2FA будет запрос пароля в консоли

    try:
        channels = load_channels(args)
        for ch in channels:
            await scrape_one_channel(
                client=client,
                channel_url=ch,
                out_dir=args.out_dir,
                log_every=args.log_every,
                sleep_after_flood=not args.no_sleep_after_flood,
                post_limit=args.post_limit,
            )
    finally:
        await client.disconnect()
    return 0

def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    asyncio.run(async_entry(args))
