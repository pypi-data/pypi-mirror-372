r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

import json


def bytes_to_json(obj):
    if isinstance(obj, bytes):
        obj = obj.decode()

        if not isinstance(obj, str):
            return obj

        try:
            return json.loads(obj)
        except json.decoder.JSONDecodeError:
            return obj
    elif isinstance(obj, dict):
        return {bytes_to_json(k): bytes_to_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [bytes_to_json(i) for i in obj]
    elif isinstance(obj, tuple):
        return tuple(bytes_to_json(i) for i in obj)
    elif isinstance(obj, set):
        return {bytes_to_json(i) for i in obj}
    else:
        if not isinstance(obj, str):
            return obj

        try:
            return json.loads(obj)
        except json.decoder.JSONDecodeError:
            return obj


def merge_chunk(data: dict, chunk: dict):
    for key, chunk_value in chunk.items():
        if key in data:
            data_value = data[key]

            if isinstance(data_value, list) and isinstance(chunk_value, list):
                data[key].extend(chunk_value)
            elif isinstance(data_value, dict) and isinstance(chunk_value, dict):
                merge_chunk(data_value, chunk_value)
            else:
                data[key] = chunk_value
        else:
            data[key] = chunk_value

    return data
