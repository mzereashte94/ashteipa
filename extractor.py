import json
import requests

# لیست بازی‌های پرطرفدار و تست‌شده روی سرور file.ipaomtk.com
GAMES_DATA = [
    {"name": "Minecraft", "slug": "minecraft", "id": "com.mojang.minecraftpe", "desc": "Minecraft Pocket Edition Modded"},
    {"name": "GTA San Andreas", "slug": "gta-san-andreas", "id": "com.rockstargames.gtasa", "desc": "Grand Theft Auto San Andreas"},
    {"name": "Subway Surfers Hack", "slug": "subway-surfers", "id": "com.kiloo.subwaysurf", "desc": "Unlimited Coins and Keys"},
    {"name": "Roblox Mod", "slug": "roblox", "id": "com.roblox.robloxmobile", "desc": "Roblox Enhanced Mod Menu"},
    {"name": "PUBG Mobile", "slug": "pubg-mobile", "id": "com.tencent.ig", "desc": "PUBG Mobile IPA"},
    {"name": "Call of Duty Mobile", "slug": "call-of-duty-mobile", "id": "com.activision.callofduty.shooter", "desc": "COD Mobile Modded"},
    {"name": "8 Ball Pool Hack", "slug": "8-ball-pool", "id": "com.miniclip.eightballpool", "desc": "Long Line Guidelines"},
    {"name": "Clash of Clans", "slug": "clash-of-clans", "id": "com.supercell.clashofclans", "desc": "Private Server / Modded"},
    {"name": "Brawl Stars", "slug": "brawl-stars", "id": "com.supercell.brawlstars", "desc": "Brawl Stars Mod"},
    {"name": "Free Fire", "slug": "free-fire", "id": "com.dts.freefireth", "desc": "Garena Free Fire Modded"},
    {"name": "Geometry Dash", "slug": "geometry-dash", "id": "com.robtopx.geometryjump", "desc": "Full Version Unlocked"},
    {"name": "CarX Drift Racing 2", "slug": "carx-drift-racing-2", "id": "com.carxtech.carxdr2", "desc": "Unlimited Money"},
    {"name": "Farming Simulator 20", "slug": "fs20", "id": "com.giantssoftware.fs20", "desc": "Full Unlocked"},
    {"name": "Asphalt 9 Legends", "slug": "asphalt-9", "id": "com.gameloft.asphalt9", "desc": "Unlimited Nitro/Speed"},
    {"name": "FIFA Mobile", "slug": "fifa-mobile", "id": "com.ea.gp.fifamobile", "desc": "FIFA Soccer Modded"}
]

def generate_repo():
    apps_list = []

    for game in GAMES_DATA:
        slug = game["slug"]
        apps_list.append({
            "name": game["name"],
            "bundleIdentifier": f"com.ipaomtk.game.{slug}",
            "developerName": "IPAOMTK Games",
            "version": "1.0",
            "versionDate": "2026-10-06",
            "downloadURL": f"https://file.ipaomtk.com/ipa/{slug}.ipa",
            "localizedDescription": f"{game['desc']} - IPAOMTK Games",
            "iconURL": "https://ipaomtk.com/favicon.ico",
            "size": 0
        })

    repo_structure = {
        "name": "IPAOMTK Games",
        "identifier": "com.ipaomtk.games",
        "apps": apps_list
    }

    with open("apps.json", "w", encoding="utf-8") as f:
        json.dump(repo_structure, f, ensure_ascii=False, indent=2)

    print(f"Done! Created {len(apps_list)} games successfully.")

if __name__ == "__main__":
    generate_repo()
