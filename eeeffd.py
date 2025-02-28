import requests
import aiohttp
import aiofiles
import os
from bs4 import BeautifulSoup
from userbot.events import register
from userbot.cmdhelp import CmdHelp

# EFFEKT URL-LƏRİ
EFFECTS = {
    "qan": "https://m.photofunia.com/categories/hallowen/blood_writing",
    "yanmis": "https://m.photofunia.com/categories/horror/burnt-paper",
    "isli": "https://m.photofunia.com/categories/vip/ash-text",
    "ucan": "https://m.photofunia.com/categories/vip/skywriting",
    "ag": "https://m.photofunia.com/categories/vip/snow-text",
    "susa": "https://m.photofunia.com/categories/flags/azerbaijan-flag",
    "neeon": "https://m.photofunia.com/categories/signs/neon-sign",
    "taxta": "https://m.photofunia.com/categories/vip/wood-text",
    "karnaval": "https://m.photofunia.com/categories/festive/carnival",
    "supurge": "https://m.photofunia.com/categories/halloween/broomstick",
}

@register(outgoing=True, pattern=r"^.(qan|yanmis|isli|ucan|ag|susa|neeon|taxta|karnaval|supurge) (.*)")
async def effect_yazi(event):
    effect = event.pattern_match.group(1)  # Effektin adı
    text = event.pattern_match.group(2)  # Yazı

    await event.edit(f"`{effect}` effekti ilə `{text}` hazırlanır... 🖌️")

    # Effekt URL-sini əldə edirik
    effect_url = EFFECTS.get(effect)
    if not effect_url:
        await event.edit(f"❌ Effekt `{effect}` tapılmadı!")
        return

    # **Effekti tətbiq edən funksiya**
    image_path = await apply_effect(effect_url, text, effect)
    
    if image_path:
        await event.client.send_file(
            event.chat_id,
            image_path,
            caption=f"🖌️ `{text}` üçün `{effect}` efekti tətbiq edildi!\n⚝ **𝑺𝑰𝑳𝑮𝑰 𝑼𝑺𝑬𝑹𝑩𝑶𝑻** ⚝",
            reply_to=event.reply_to_msg_id
        )
        os.remove(image_path)  # Yaddaşı boşaltmaq üçün şəkili silirik
    else:
        await event.edit("❌ **Şəkil yaradılarkən xəta baş verdi!**")

# **Photofunia effektini tətbiq edən funksiya**
# **Photofunia effektini tətbiq edən funksiya**
async def apply_effect(effect_url, text, effect_name):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async with session.get(effect_url) as response:
            if response.status != 200:
                return None

            soup = BeautifulSoup(await response.text(), "html.parser")

        # Effekt üçün form-un action URL-sini tapırıq
        form = soup.find("form", {"class": "effect-form"})
        if not form:
            return None

        form_action = "https://m.photofunia.com" + form["action"]
        payload = {"text": text}

        # Effektə uyğun şəkil yaratmaq
        async with session.post(form_action, data=payload) as result:
            result_soup = BeautifulSoup(await result.text(), "html.parser")
            img_tag = result_soup.find("img", class_=["result-image", "img-responsive"])

            if not img_tag or "src" not in img_tag.attrs:
                return None

            img_url = "https://m.photofunia.com" + img_tag["src"]
            async with session.get(img_url, ssl=False) as img_response:
                if img_response.status != 200:
                    return None

                img_data = await img_response.read()
                img_path = f"{effect_name}.jpg"

                async with aiofiles.open(img_path, "wb") as img_file:
                    await img_file.write(img_data)

                return img_path
