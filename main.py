import json
import logging
import os
from datetime import datetime

import sentry_sdk
import telegram
import sentry_init
import openai
from models import Messages


bot = telegram.Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
bot_name = os.environ["TELEGRAM_BOT_NAME"]
bot_handler = f'@{bot_name}'


def telegram_webhook_handler(event: dict, context: dict) -> dict:
    raw = json.loads(event['body'])
    upd = telegram.Update.de_json(raw, bot)
    if upd.message and upd.message.text:
        try:
            is_group = upd.message.chat.type != 'private'
            is_mention = bot_handler in upd.message.text
            users = {bot_handler, f'@{upd.message.from_user.username}'}  # set of users in the thread

            messages = []
            thread_id = None
            messages_in_thread = []
            if upd.message.reply_to_message is not None:
                sender = f'@{upd.message.reply_to_message.from_user.username}'
                users.add(sender)
                try:
                    message_in_reply = Messages.get(str(upd.message.reply_to_message.message_id))
                    thread_id = message_in_reply.thread_id or message_in_reply.id
                    messages_in_thread = message_in_reply.messages_in_thread + [message_in_reply.id]
                    thread = list(Messages.batch_get(messages_in_thread))
                    thread.sort(key=lambda m: m.created)
                    for m in thread:
                        prev_msg = messages[-1] if messages else None
                        role = "assistant" if m.sender == bot_name else "user"
                        if prev_msg and prev_msg["role"] == role:
                            prev_msg["content"] += f'\n\n@{m.sender}: {m.message}'
                        else:
                            messages.append({"role": role, "content": f'@{m.sender}: {m.message}'})
                        users.add(f'@{m.sender}')
                except Messages.DoesNotExist:
                    messages.append(
                        {
                            "role": "assistant" if sender == bot_handler else "user",
                            "content": f'{bot_handler}: {upd.message.reply_to_message.text}'
                        }
                    )
            is_reply = upd.message.reply_to_message is not None and upd.message.reply_to_message.from_user.username == bot_name
            if is_group and not is_mention and not is_reply:
                return {
                    "statusCode": 200,
                    "body": json.dumps({})
                }
            messages.insert(
                0,
                {
                    "role": "system",
                    "content": "\n".join(
                        [
                            f"You are a helpful assistant. Your name is {bot_handler}.",
                            f"Other users in the chat: {users - {bot_handler}}",
                        ]
                    ),
                },
            )
            messages.append({"role": "user", "content": f'@{upd.message.from_user.username}: {upd.message.text}'})
            msg = Messages(
                id=str(upd.message.message_id),
                chat_id=str(upd.message.chat.id),
                reply_to=str(upd.message.reply_to_message.message_id) if upd.message.reply_to_message else None,
                thread_id=thread_id or str(upd.message.message_id),
                messages_in_thread=messages_in_thread,
                created=datetime.utcnow().timestamp(),
                expires=datetime.utcnow().timestamp() + 14 * 24 * 60 * 60,
                message=upd.message.text,
                sender=upd.message.from_user.username,
                meta={
                    "is_group": is_group,
                    "is_mention": is_mention,
                    "is_reply": is_reply,
                    "raw": raw,
                }
            )
            msg.save()

            reply = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )['choices'][0]['message']['content']
            msg = upd.message.reply_text(reply)
            Messages(
                id=str(msg.message_id),
                chat_id=str(upd.message.chat.id),
                reply_to=str(upd.message.message_id),
                thread_id=str(thread_id or upd.message.message_id),
                messages_in_thread=messages_in_thread + [str(upd.message.message_id)],
                created=datetime.utcnow().timestamp(),
                expires=datetime.utcnow().timestamp() + 14 * 24 * 60 * 60,
                message=reply,
                sender=bot_name,
                meta={
                    "is_group": is_group,
                    "is_mention": is_mention
                }
            ).save()
        except Exception as e:  # avoid auto-retries from Telegram eat up a hole in your pocket
            sentry_sdk.capture_exception(e)
            logging.exception(str(e), stack_info=True)

    return {
        "statusCode": 200,
        "body": json.dumps({})
    }
