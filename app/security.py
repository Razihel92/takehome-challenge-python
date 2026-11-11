import asyncio

from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


async def hash_password(password: str) -> str:
    return await asyncio.to_thread(password_hash.hash, password)
