from pynamodb.attributes import UnicodeAttribute, NumberAttribute, JSONAttribute, ListAttribute
from pynamodb.models import Model


class Messages(Model):
    class Meta:
        table_name = "gpt4-tg-bot-messages"
    id = UnicodeAttribute(hash_key=True)
    reply_to = UnicodeAttribute(null=True)
    thread_id = UnicodeAttribute(null=True)
    messages_in_thread = ListAttribute()
    chat_id = UnicodeAttribute()
    created = NumberAttribute()
    expires = NumberAttribute()  # + 14 days
    message = UnicodeAttribute()
    sender = UnicodeAttribute()
    meta = JSONAttribute()

