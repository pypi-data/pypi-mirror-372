#!/usr/bin/env uv run

import sys

import httpx

import slugkit

client = slugkit.SyncClient(
    base_url="https://dev.slugkit.dev/api/v1",
    api_key="ik-Y2aHW1ACkYTfuk+qqABHUbFAI7usH+I3TEjTbnXsqRk=",
)

logins = client["manly-short-kroon-2c25"]
names = client["haply-found-dicer-82cb"]
passwords = client["aloud-godly-thong-d0b3"]


if __name__ == "__main__":
    num_names = 1
    if len(sys.argv) > 1:
        num_names = int(sys.argv[1])
    login_gen = logins.with_limit(num_names)
    name_gen = names.with_limit(num_names)
    pass_gen = passwords.with_limit(num_names)
    try:
        for login, name, password in zip(login_gen, name_gen, pass_gen):
            print(f"{login:15s}\t{name:15s}\t{password}")
    except httpx.HTTPStatusError as e:
        print(f"Error: {e.response.text}")
