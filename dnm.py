#!/usr/bin/env python3

import os
import openai
import asyncio

class Role():
    USER      = 0
    ASSISTANT = 1
    SYSTEM    = 2
    roles = ["user", "assistant", "system"]

openai.api_key = os.getenv("OPENAI_API_KEY")

def create_chat_message(role, content):
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": Role.roles[role], "content": content}
      ]
    )

    print(completion.choices[0].message.content)



create_chat_message(2, "Hello")
