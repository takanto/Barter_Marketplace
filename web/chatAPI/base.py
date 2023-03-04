from telethon import TelegramClient, events
import logging
import RelayBot
import os
from flask import redirect
from web import db
from web.models import Relay
from dotenv import load_dotenv

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)


load_dotenv()
async def launchRelay(threadLock, buyer, seller, productID, secondaryID = None, primaryID = None, listingID = None, secondaryUserID = None):
    #TODO
    BOT_TOKEN_KEY = os.getenv('BOT_TOKEN_KEY')
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')
    async def main():
        # Getting information about yourself
        me = await client.get_me()
        
        botFather = client.get_entity('t.me/botfather')

        # You can send messages to yourself...
        await client.send_message(botFather, '/start')

        await client.send_message(botFather, '/newbot')
        # ...to some chat ID
        await client.send_message(botFather, f'MM {buyer}/{seller}: {productID}')
        # ...to your contacts
        await client.send_message(botFather, f'MM_{buyer}/{seller}_{productID}_bot')
        # ...or even to any username
        botInfo = await client.get_messages(botFather)
        
        botInfo = [txt for ent, txt in botInfo.get_entities_text()]
        
        global relayKey
        relayKey = botInfo[1]

        await client.send_message(botFather, '/setdescription')
        
        await client.send_message(botFather, f'@MM_{buyer}/{seller}_{productID}_bot')
        
        await client.send_message(botFather, f'This is a conversation relating to the product "{productTitle}" between "{buyer}" and "{seller}".\n\nPress start to allow this messages from this conversation.\n')
        
        await client.send_message(botFather, '/setProfilePhoto')
        
        await client.send_message(botFather, f'@MM_{buyer}/{seller}_{productID}_bot')
        
        await client.send_file(botFather, iconURL)
        
        await client.send_message(botFather, '/setabouttext')
        
        await client.send_message(botFather, f'@MM_{buyer}/{seller}_{productID}_bot')
        
        await client.send_message(botFather, f'This is a conversation relating to the product "{productTitle}" between "{buyer}" and "{seller}".\n\nPress start to allow this messages from this conversation.\n')
        
        await client.send_message(botFather, '/setcommands')
        
        await client.send_message(botFather, f'@MM_{buyer}/{seller}_{productID}_bot')
        
        await client.send_message(botFather, 'describe - Display Product Details\nupdateProductToSatisfied - This is for the poster to update the product Status to **Satisfied** from Telegram\nupdateProductToUnavailable - This is for the seller to update the product Status to **Unavailable** from Telegram\nend - This is for both parties to easily end a marketplace conversation and stop receiving messages')

    
    relayKey = Relay.query.filter_by(name = f'MM_{buyer}/{seller}_{productID}_bot').first().token
    if relayKey is None:
        client = TelegramClient('main', API_ID, API_HASH)
        async with client:
            client.loop.run_until_complete(main())
        mmBot = TelegramClient('MM_bot', API_ID, API_HASH).start(bot_token = BOT_TOKEN_KEY)
        await mmBot.send_message(primaryID, f"MM_{buyer}/{seller}_{productID} has a conversation for you.")
        await mmBot.disconnect()
        client.run_until_disconnected()
        newRelay = Relay(name = f'MM_{buyer}/{seller}_{productID}_bot', token = relayKey)
        db.session.add(newRelay)
        db.session.commit()

    relay = RelayBot(f'MM_{buyer}/{seller}_{productID}_bot', API_ID, API_HASH)
    relay.add_endpoint_args(threadLock, secondaryTelegramID, secondaryTelegramID, listingID, secondaryUserID)
    relay = relay.start(bot_token = relayKey)
    relay.run_until_disconnected()