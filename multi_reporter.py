import asyncio
import aiohttp
import json
import time
import random
import os
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(name)

BOT_TOKEN = os.getenv("BOT_TOKEN", "7881255831:AAGp12FwrkVZBY_1psohKv2kp90puQICwJc")
BOT_TOKENS = [BOT_TOKEN]

REPORT_REASONS = {"spam":1,"violence":2,"child_abuse":3,"pornography":4,"copyright":5,"fake":6,"other":7}

class Reporter:
    def init(self, tokens):
        self.tokens = tokens
        self.stats = defaultdict(lambda: {"success": 0, "total": 0})
        self.session = None
        
    async def init(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        log.info(f"🚀 Bot ready: {len(self.tokens)} accounts")
        
    async def close(self):
        if self.session:
            await self.session.close()
    
    def get_chat_id(self, link):
        link = link.strip().lower().replace("https://", "").replace("http://", "")
        if link.startswith("t.me/"):
            link = link[5:]
        if link.startswith(('+', '@')):
            return link
        return ""
    
    async def report(self, link, reason="spam"):
        token = self.tokens[0]
        self.stats[0]["total"] += 1
        
        try:
            chat_id = self.get_chat_id(link)
            if not chat_id:
                return False, "Invalid link"
            
            data = {
                "chat_id": chat_id,
                "reason": REPORT_REASONS.get(reason, 1),
                "type": "chat"
            }
            
            url = f"https://api.telegram.org/bot{token}/reportChat"
            async with self.session.post(url, json=data) as resp:
                result = await resp.json()
                if result.get("ok"):
                    self.stats[0]["success"] += 1
                    log.info(f"✅ Reported: {chat_id}")
                    return True, chat_id
                else:
                    log.error(f"❌ Failed: {result}")
                    return False, result.get("description", "Error")
        except Exception as e:
            log.error(f"❌ Exception: {e}")
            return False, str(e)

async def main_loop():
    reporter = Reporter(BOT_TOKENS)
    await reporter.init()
    
    log.info("🔥 Telegram Reporter ACTIVE - Railway Ready!")
    log.info("📊 Stats will log every 60s")
    
    while True:
        try:
            # Show stats every minute
            total = reporter.stats[0]["total"]
            success = reporter.stats[0]["success"]
            rate = (success/total*100) if total else 0
            log.info(f"📈 STATS: {success}/{total} ({rate:.1f}%)")
            await asyncio.sleep(60)
        except KeyboardInterrupt:
            break
    
    await reporter.close()

if name == "main":
    asyncio.run(main_loop())
