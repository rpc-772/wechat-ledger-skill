import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone


def load_dotenv(path=".env"):
    env_map = {}
    if not os.path.exists(path):
        return env_map

    with open(path, "r", encoding="utf-8-sig") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env_map[key.strip()] = value.strip()
    return env_map


def get_config(name, dotenv):
    value = os.getenv(name)
    if value:
        return value
    return dotenv.get(name, "")


def notion_request(method, path, api_key, notion_version, body=None):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": notion_version,
    }
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(
        url=f"https://api.notion.com{path}",
        method=method,
        headers=headers,
        data=data,
    )

    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def get_category(text):
    rules = [
        (["\u5348\u996d", "\u65e9\u9910", "\u665a\u996d", "\u5496\u5561", "\u5976\u8336"], "\u9910\u996e"),
        (["\u5730\u94c1", "\u516c\u4ea4", "\u6253\u8f66", "\u505c\u8f66"], "\u4ea4\u901a"),
        (["\u5de5\u8d44", "\u5956\u91d1", "\u62a5\u9500", "\u9000\u6b3e"], "\u5de5\u8d44"),
    ]
    for keywords, category in rules:
        if any(keyword in text for keyword in keywords):
            return category
    return "\u5176\u4ed6"


def notion_category(category):
    mapping = {
        "\u9910\u996e": "\u98df\u54c1",
        "\u4ea4\u901a": "\u4ea4\u901a\u5de5\u5177",
        "\u5de5\u8d44": "\u5de5\u8cc7",
        "\u5176\u4ed6": "\u5176\u4ed6",
    }
    return mapping.get(category, "\u5176\u4ed6")


def parse_message(message):
    raw_message = message.strip()
    if not raw_message:
        raise RuntimeError("\u8bb0\u8d26\u5931\u8d25\uff1a\u6d88\u606f\u4e0d\u80fd\u4e3a\u7a7a")

    payment_methods = [
        "\u5fae\u4fe1",
        "\u652f\u4ed8\u5b9d",
        "\u94f6\u884c\u5361",
        "\u73b0\u91d1",
    ]
    payment = next((item for item in payment_methods if item in raw_message), "")

    amount_matches = list(re.finditer(r"([+-]?\d+(?:\.\d{1,2})?)", raw_message))
    if not amount_matches:
        raise RuntimeError("\u8bb0\u8d26\u5931\u8d25\uff1a\u91d1\u989d\u4e0d\u660e\u786e")

    amount_match = amount_matches[-1]
    amount_token = amount_match.group(1)
    amount = abs(float(amount_token))

    income_hints = [
        "+",
        "\u6536\u5165",
        "\u5de5\u8d44",
        "\u5956\u91d1",
        "\u62a5\u9500",
        "\u9000\u6b3e",
    ]
    ledger_type = "\u652f\u51fa"
    if any(hint in raw_message for hint in income_hints):
        ledger_type = "\u6536\u5165"

    name_text = raw_message.replace(payment, "") if payment else raw_message
    name_text = name_text[: amount_match.start()] + name_text[amount_match.end() :]
    name_text = re.sub(r"[\s\uff1a:,\uff0c]+", "", name_text)
    name = name_text.strip() or "\u8bb0\u8d26"

    return {
        "name": name,
        "amount": amount,
        "type": ledger_type,
        "category": get_category(raw_message),
        "payment_method": payment,
        "time": datetime.now().astimezone().isoformat(timespec="seconds"),
        "note": "",
        "raw_message": raw_message,
        "confirmed": True,
    }


def rich_text(text):
    if not text:
        return {"rich_text": []}
    return {
        "rich_text": [
            {
                "text": {
                    "content": text,
                }
            }
        ]
    }


def build_payload(parsed, schema, database_id):
    properties = schema.get("properties", {})
    title_property = next((name for name, value in properties.items() if value.get("type") == "title"), None)
    if not title_property:
        raise RuntimeError("\u8bb0\u8d26\u5931\u8d25\uff1aNotion \u5b57\u6bb5\u4e0e\u5f53\u524d\u8bb0\u8d26\u6620\u5c04\u4e0d\u517c\u5bb9")

    payload_properties = {
        title_property: {
            "title": [
                {
                    "text": {
                        "content": parsed["name"],
                    }
                }
            ]
        }
    }

    if "\u91d1\u984d" in properties:
        payload_properties["\u91d1\u984d"] = {"number": parsed["amount"]}

    if "\u8cfc\u8cb7\u65e5\u671f" in properties:
        payload_properties["\u8cfc\u8cb7\u65e5\u671f"] = {"date": {"start": parsed["time"]}}

    if "\u985e\u5225" in properties:
        payload_properties["\u985e\u5225"] = {"select": {"name": notion_category(parsed["category"])}}

    extra_note_parts = []

    if "\u985e\u578b" in properties:
        payload_properties["\u985e\u578b"] = {"select": {"name": parsed["type"]}}
    else:
        extra_note_parts.append(f"\u985e\u578b\uff1a{parsed['type']}")

    if "\u652f\u4ed8\u65b9\u5f0f" in properties and parsed["payment_method"]:
        payload_properties["\u652f\u4ed8\u65b9\u5f0f"] = {"select": {"name": parsed["payment_method"]}}
    elif parsed["payment_method"]:
        extra_note_parts.append(f"\u652f\u4ed8\u65b9\u5f0f\uff1a{parsed['payment_method']}")

    if "\u539f\u59cb\u6d88\u606f" in properties:
        payload_properties["\u539f\u59cb\u6d88\u606f"] = rich_text(parsed["raw_message"])
    else:
        extra_note_parts.append(f"\u539f\u59cb\u6d88\u606f\uff1a{parsed['raw_message']}")

    if "\u5df2\u78ba\u8a8d" in properties:
        payload_properties["\u5df2\u78ba\u8a8d"] = {"checkbox": True}
    elif "\u5df2\u786e\u8ba4" in properties:
        payload_properties["\u5df2\u786e\u8ba4"] = {"checkbox": True}
    else:
        extra_note_parts.append("\u5df2\u78ba\u8a8d\uff1atrue")

    note_text = parsed["note"]
    if extra_note_parts:
        extra_text = "\uff1b".join(extra_note_parts)
        note_text = f"{note_text}\uff1b{extra_text}" if note_text else extra_text

    if "\u5099\u5fd8" in properties:
        payload_properties["\u5099\u5fd8"] = rich_text(note_text)
    elif "\u5907\u6ce8" in properties:
        payload_properties["\u5907\u6ce8"] = rich_text(note_text)

    return {
        "parent": {
            "type": "database_id",
            "database_id": database_id,
        },
        "properties": payload_properties,
    }


def process_message(message, write=False):
    dotenv = load_dotenv()
    api_key = get_config("NOTION_API_KEY", dotenv)
    database_id = get_config("NOTION_DATA_SOURCE_ID", dotenv)
    create_version = get_config("NOTION_VERSION", dotenv) or "2025-09-03"
    schema_version = "2022-06-28"

    if not api_key:
        raise RuntimeError("\u8bb0\u8d26\u5931\u8d25\uff1a\u672a\u914d\u7f6e NOTION_API_KEY")
    if not database_id:
        raise RuntimeError("\u8bb0\u8d26\u5931\u8d25\uff1a\u672a\u914d\u7f6e NOTION_DATA_SOURCE_ID")

    parsed = parse_message(message)
    schema = notion_request("GET", f"/v1/databases/{database_id}", api_key, schema_version)
    payload = build_payload(parsed, schema, database_id)

    if not write:
        return {
            "mode": "dry-run",
            "database_title": "".join(item.get("plain_text", "") for item in schema.get("title", [])),
            "name": parsed["name"],
            "amount": parsed["amount"],
            "type": parsed["type"],
            "category": parsed["category"],
            "payment_method": parsed["payment_method"],
            "payload": payload,
        }

    response = notion_request("POST", "/v1/pages", api_key, create_version, payload)
    if not response.get("id"):
        raise RuntimeError("\u8bb0\u8d26\u5931\u8d25\uff1aNotion API \u8c03\u7528\u5931\u8d25")

    payment_text = parsed["payment_method"] or "\u672a\u586b"
    return {
        "ok": True,
        "reply": f"\u5df2\u8bb0\uff1a{parsed['name']} / {parsed['amount']} / {payment_text}",
        "page_id": response["id"],
        "parsed": parsed,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--message", required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = process_message(args.message, write=args.write)
    if args.write:
        print(result["reply"])
        return
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
