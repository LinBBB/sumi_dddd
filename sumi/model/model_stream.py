import time as t
import uuid
from model.base_model import BaseModel
from peewee import *

class TokenMapping(BaseModel):
    symbol = CharField(max_length=255, null=True)
    name = CharField(max_length=255, null=True)
    address = CharField(max_length=255, null=True)
    chain_id = BigIntegerField( null=True)
    decimals = BigIntegerField( null=True)
    logo_url = CharField(max_length=255, null=True)
    pool_address = CharField(max_length=512, null=True)
    gecko_id = CharField(max_length=255, null=True)
    chain_name = CharField(max_length=255, null=True)
    twitter_name = CharField(max_length=255, null=True)
    twitter_id = BigIntegerField( null=True)
    twitter_url = CharField(max_length=255, null=True)

class EventTag(BaseModel):
    id = IntegerField(primary_key=True)
    tag_name = CharField(max_length=255)



class AllChain(BaseModel):
    chain_icon = CharField()
    chain_id = IntegerField(primary_key=True)

class TreeOfData(BaseModel):
    id = UUIDField()
    title = CharField(null=False)
    body = TextField(null=False)
    icon = CharField(null=False)
    image = CharField(null=True)
    requireInteraction = BooleanField(null=True)
    link = CharField(null=True)
    time = TimestampField(null=False)
    twitterId = CharField(null=False)
    isReply = BooleanField(null=False)
    isRetweet = BooleanField(null=False)
    isQuote = BooleanField(null=False)
    suggestions = TextField(null=False)
    source = CharField(null=False)
    ts = TimestampField(default=int(t.time()), index=True)
    symbol = CharField(null=False)
    price = CharField(null=False)
    tag = CharField(null=False)
    platform = CharField(null=False)
    token_info = TextField(null=False)


class TwitterPost(BaseModel):
    screen_name = CharField(max_length=255)
    user_id = CharField(max_length=255)
    body = TextField()
    profile_image = CharField(max_length=255)
    images = TextField(null=True)
    link = CharField(max_length=255, null=True)
    entry_id = CharField(max_length=255, null=True)
    info = TextField(null=True)
    time = BigIntegerField(null=True)
    retweet = IntegerField(null=True)
    like = IntegerField(null=True)
    quote = IntegerField(null=True)
    reply = IntegerField(null=True)
    entities = TextField(null=True)
    view = CharField(max_length=255)
    source = CharField(max_length=255)
    created_at = BigIntegerField(null=True)
    original_content = TextField(null=True)
    original_screen_name = CharField(max_length=255, null=True)
    original_user_id = CharField(max_length=255, null=True)
    original_url = CharField(max_length=255, null=True)
    original_profile = CharField(max_length=255, null=True)
    original_create_time = BigIntegerField(null=True)
    original_type = CharField(max_length=255, null=True)
    token = CharField(max_length=255, null=True)
    token_info = TextField(null=True)
    suggestions = TextField(null=True)
    data_source = CharField(max_length=255, null=True)
