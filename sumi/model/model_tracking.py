import time as t
import uuid
from model.base_model import BaseModel
from peewee import *


class TwitterTracking(BaseModel):
    user_id = CharField(max_length=255, null=True, unique=True)
    user_profile = CharField(max_length=255, null=True)
    create_time = BigIntegerField(null=True)
    user_screen_name = CharField(max_length=255, null=True)
