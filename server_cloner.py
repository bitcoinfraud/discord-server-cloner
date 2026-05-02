import os
import requests
import time
import shutil
import fade
import base64
import json
import datetime
from datetime import datetime

def center(text, width=80):
    return text.center(width)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_ascii():
    ascii = """
 ▄████▄   ██▓     ▒█████   ███▄    █ ▓█████  ██▀███  
▒██▀ ▀█  ▓██▒    ▒██▒  ██▒ ██ ▀█   █ ▓█   ▀ ▓██ ▒ ██▒
▒▓█    ▄ ▒██░    ▒██░  ██▒▓██  ▀█ ██▒▒███   ▓██ ░▄█ ▒
▒▓▓▄ ▄██▒▒██░    ▒██   ██░▓██▒  ▐▌██▒▒▓█  ▄ ▒██▀▀█▄  
▒ ▓███▀ ░░██████▒░ ████▓▒░▒██░   ▓██░░▒████▒░██▓ ▒██▒
░ ░▒ ▒  ░░ ▒░▓  ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░
  ░  ▒   ░ ░ ▒  ░  ░ ▒ ▒░ ░ ░░   ░ ▒░ ░ ░  ░  ░▒ ░ ▒░
░          ░ ░   ░ ░ ░ ▒     ░   ░ ░    ░     ░░   ░ 
░ ░          ░  ░    ░ ░           ░    ░  ░   ░     
░                                                    
    """
    print(fade.purpleblue(ascii))

def save_json(data, name):
    with open(f"data/{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def request_data(url, headers):
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.json()
        else:
            print(center(f"✗ error {r.status_code} accesing to {url}"))
            return []
    except Exception as e:
        print(center(f"✗ exception accesing {url}: {e}"))
        return []

def download_guild_data(token, guild_id):
    headers = {"authorization": token}
    os.makedirs("data", exist_ok=True)

    guild_info = request_data(f"https://discord.com/api/v9/guilds/{guild_id}", headers)
    if not guild_info:
        return None

    name = guild_info.get("name", "unknown").lower()
    icon = guild_info.get("icon")
    icon_url = f"https://cdn.discordapp.com/icons/{guild_id}/{icon}.png" if icon else None

    if icon_url:
        img_data = requests.get(icon_url).content
        with open("data/icon.png", "wb") as f:
            f.write(img_data)

    save_json(guild_info, "info")
    print(center(f"server: {name}"))

    data_summary = {"name": name}

    endpoints = {
        "roles": f"https://discord.com/api/v9/guilds/{guild_id}/roles",
        "channels": f"https://discord.com/api/v9/guilds/{guild_id}/channels",
        "emojis": f"https://discord.com/api/v9/guilds/{guild_id}/emojis",
        "stickers": f"https://discord.com/api/v9/guilds/{guild_id}/stickers"
    }

    for name, url in endpoints.items():
        print(center(f"downloading {name}..."))
        data = request_data(url, headers)
        save_json(data, name)
        print(center(f"✓ {len(data)} {name} saved"))
        data_summary[name] = len(data)

    return data_summary

def upload_roles(token, target_id):
    try:
        with open("data/roles.json", encoding="utf-8") as f:
            roles = json.load(f)
    except:
        print(center("✗ couldn't read roles.json"))
        return

    headers = {"authorization": token, "content-type": "application/json"}
    for role in roles[::-1]:
        payload = {
            "name": role["name"].lower(),
            "color": role["color"],
            "permissions": role["permissions"],
            "mentionable": role["mentionable"],
            "hoist": role["hoist"]
        }
        r = requests.post(f"https://discord.com/api/v9/guilds/{target_id}/roles", headers=headers, json=payload)
        status = "✓" if r.status_code in [200, 201] else f"✗ ({r.status_code})"
        print(center(f"[{status}] rol: {role['name'].lower()}"))

def upload_emojis(token, target_id):
    headers = {"authorization": token, "content-type": "application/json"}
    try:
        with open("data/emojis.json", encoding="utf-8") as f:
            emojis = json.load(f)
        for emoji in emojis:
            url = f"https://cdn.discordapp.com/emojis/{emoji['id']}.{'gif' if emoji['animated'] else 'png'}"
            img_data = base64.b64encode(requests.get(url).content).decode()
            payload = {"name": emoji["name"].lower(), "image": f"data:image/png;base64,{img_data}"}
            r = requests.post(f"https://discord.com/api/v9/guilds/{target_id}/emojis", headers=headers, json=payload)
            print(center(f"[{'✓' if r.status_code == 201 else '✗'}] emoji: {emoji['name'].lower()}"))
    except:
        print(center("✗ error uploading emojis"))
    if r.status_code == 429 or r.status_code == 403:
        print(center("! limit reached. jumping."))

def upload_channels(token, target_id):
    headers = {"authorization": token, "content-type": "application/json"}
    try:
        with open("data/channels.json", encoding="utf-8") as f:
            channels = json.load(f)
        for ch in channels:
            if ch["type"] == 4:
                payload = {"name": ch["name"].lower(), "type": 4}
                requests.post(f"https://discord.com/api/v9/guilds/{target_id}/channels", headers=headers, json=payload)
        for ch in channels:
            if ch["type"] in [0, 2]:
                payload = {
                    "name": ch["name"].lower(),
                    "type": ch["type"],
                    "bitrate": ch.get("bitrate", 64000),
                    "user_limit": ch.get("user_limit", 0),
                    "rate_limit_per_user": ch.get("rate_limit_per_user", 0),
                    "topic": ch.get("topic", "")
                }
                if ch.get("parent_id"):
                    payload["parent_id"] = ch["parent_id"]
                requests.post(f"https://discord.com/api/v9/guilds/{target_id}/channels", headers=headers, json=payload)
        print(center("✓ uploaded channels"))
    except:
        print(center("✗ error uploading channels"))
    if r.status_code == 429 or r.status_code == 403:
        print(center("! limit reached. jumping."))

def upload_stickers(token, target_id):
    headers = {"authorization": token}
    try:
        with open("data/stickers.json", encoding="utf-8") as f:
            stickers = json.load(f)
        for s in stickers:
            ext = {1: "png", 2: "apng", 3: "json"}.get(s["format_type"], "png")
            url = f"https://media.discordapp.net/stickers/{s['id']}.{ext}"
            img = requests.get(url).content
            files = {"file": (f"sticker.{ext}", img, "image/png")}
            payload = {"name": s["name"].lower(), "description": "clonado", "tags": s.get("tags", "🙂")}
            r = requests.post(f"https://discord.com/api/v9/guilds/{target_id}/stickers", headers=headers, data=payload, files=files)
            print(center(f"[{'✓' if r.status_code == 201 else '✗'}] sticker: {s['name'].lower()}"))
    except:
        print(center("✗ error uploading stickers"))
    if r.status_code == 429 or r.status_code == 403:
        print(center("! limit reached. jumping."))

def update_server_name_icon(token, target_id):
    headers = {"authorization": token, "content-type": "application/json"}
    try:
        with open("data/info.json", encoding="utf-8") as f:
            info = json.load(f)
        name = info.get("name", "servidor clonado")
        with open("data/icon.png", "rb") as img:
            b64img = base64.b64encode(img.read()).decode()
        payload = {"name": name.lower(), "icon": f"data:image/png;base64,{b64img}"}
        r = requests.patch(f"https://discord.com/api/v9/guilds/{target_id}", headers=headers, json=payload)
        print(center(f"{'✓' if r.status_code == 200 else '✗'} updated name and icon"))
    except:
        print(center("✗ couldn't update server name or icon"))

def main():
    start = time.time()
    now = datetime.now().strftime("%H.%M.%S")
    os.system(f'title t.me/ritual1337 | server cloner | {now}')
    clear()
    draw_ascii()

    token = input("user token: ").strip()
    gid = input("id of the server u want to clone: ").strip()

    clear()
    draw_ascii()
    print(center("analyzing and downloading data from the server..."))
    info = download_guild_data(token, gid)
    if not info:
        print(center("couldn't access that server"))
        return

    print()
    print(center(f"name of the server: {info['name']}"))
    print(center(f"roles: {info.get('roles', 0)}"))
    print(center(f"channels: {info.get('channels', 0)}"))
    print(center(f"emojis: {info.get('emojis', 0)}"))
    print(center(f"stickers: {info.get('stickers', 0)}"))

    resp = input("\nupload to another server? (y/n): ").lower()
    if resp == "y":
        tid = input("destination server id: ").strip()
        clear()
        draw_ascii()
        print(center("uploading data..."))
        update_server_name_icon(token, tid)
        upload_roles(token, tid)
        upload_channels(token, tid)
        upload_emojis(token, tid)
        upload_stickers(token, tid)
        print(center("completed cloning."))
    else:
        print(center("done."))
        elapsed = time.time() - start
        print()
        print(center(f"total time: {elapsed:.2f} seconds"))
        input()

if __name__ == "__main__":
    main()
