from telethon import TelegramClient, events
from contextlib import contextmanager
import requests
import json
import logging
from tools import encryptContent
from web import db
from web.models import MessageEvent, Listing, ListingStateEnum


logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)


@contextmanager
def ignored(*exceptions):
    """
    Handles the ignore exceptions
    """
    try:
        yield
    except exceptions:
        pass

class RelayBot(TelegramClient):
    """
    Messaging bot.
    Deals with all the messaging connections
    """
    async def __init__(self, *a, **kw):
        await super().__init__(*a, **kw)
        self.messageRelay = {}
        self.presentAction = None
        
    async def connect(self):
        await super().connect()
        self.me = await self.get_me()
        
    def add_endpoint_args(self, threadLock, secondaryTelegramID, primaryTelegramID, listingID, secondaryUserID):
        self.lock = threadLock
        self.secondaryTelegramID, self.primaryTelegramID, self.listingID, self.secondaryUserID = secondaryTelegramID, primaryTelegramID, listingID, secondaryUserID
        self.add_event_handler(self.action_handler, events.UserUpdate(chats = [self.secondaryTelegramID, primaryTelegramID]))
        self.add_event_handler(self.edit_handler, events.MessageEdited(chats = [self.secondaryTelegramID, primaryTelegramID]))
        self.add_event_handler(self.read_handler, events.MessageRead(chats = [self.secondaryTelegramID, primaryTelegramID]))
        self.add_event_handler(self.message_handler, events.NewMessage(incoming = True, chats = [self.secondaryTelegramID, primaryTelegramID]))
        
    
    async def command_handler(self, event):
        sender = await event.get_sender()
        otherID = self.secondaryTelegramID if sender.id == self.primaryTelegramID else self.primaryTelegramID
        command = event.pattern_match.group(1)
        if command == "describe":
            productDescription = listing.query.get(int(self.listingID)).description
            await event.reply(productDescription)
            newEvent = MessageEvent(messageID = event.message.id, messageEvent = encryptContent(str({'message': productDescription})), eventType = command)
            db.session.add(newEvent)
            db.session.commit()
        
        elif command == "updateProductToSatisfied":
            if sender.id == self.primaryTelegramID:
                try:
                    presentListing = Listing.query.get(int(self.listingID))
                    presentListing.state = ListingStateEnum.SATISFIED.name
                    presentListing.satisfier = self.secondaryUserID
                    self.lock.acquire()
                    db.session.commit()
                    self.lock.release()
                    await event.reply("Product Listing has been updated to Satisfied")
                    newMessage = await client.send_message(otherID, "Product Listing has been updated to Satisfied")
                    newEvent = MessageEvent(messageID = event.message.id, relayId = newMessage.id, messageEvent = encryptContent(str({'message': "Product Listing has been updated to Satisfied"})), eventType = command)
                    self.lock.acquire()
                    db.session.add(newEvent)
                    db.session.commit()
                    self.lock.release()
                except Exception as error:
                    await event.reply("Failed to update listing state to Satisfied")
                    newEvent = MessageEvent(messageID = event.message.id, messageEvent = encryptContent(str({'message': error})), eventType = "Failed")
                    self.lock.acquire()
                    db.session.add(newEvent)
                    db.session.commit()
                    self.lock.release()
            else:
                await event.reply("Cannot update product description as you are not the seller")
                newEvent = MessageEvent(messageID = event.message.id, messageEvent = encryptContent(str({'message': "Cannot update product description as you are not the seller"})), eventType = command)
                self.lock.acquire()
                db.session.add(newEvent)
                db.session.commit()
                self.lock.release()
        
        elif command == "updateProductToUnavailable":
            if sender.id == self.primaryTelegramID:
                try:
                    presentListing = Listing.query.get(int(self.listingID))
                    presentListing.state = ListingStateEnum.UNAVAILABLE.name
                    self.lock.acquire()
                    db.session.commit()
                    self.lock.release()
                    await event.reply("Product Listing has been updated to Unavailable")
                    newMessage = await client.send_message(otherID, "Product Listing has been updated to Unavailable")
                    newEvent = MessageEvent(messageID = event.message.id, relayId = newMessage.id, messageEvent = encryptContent(str({'message': "Product Listing has been updated to Unavailable"})), eventType = command)
                    self.lock.acquire()
                    db.session.add(newEvent)
                    db.session.commit()
                    self.lock.release()
                except Exception as error:
                    await event.reply("Failed to update listing state to Unavailable")
                    newEvent = MessageEvent(messageID = event.message.id, messageEvent = encryptContent(str({'message': error})), eventType = "Failed")
                    self.lock.acquire()
                    db.session.add(newEvent)
                    db.session.commit()
                    self.lock.release()
            else:
                await event.reply("Cannot update product description as you are not the seller")
                newEvent = MessageEvent(messageID = event.message.id, messageEvent = encryptContent(str({'message': "Cannot update product description as you are not the seller"})), eventType = command)
                self.lock.acquire()
                db.session.add(newEvent)
                db.session.commit()
                self.lock.release()
        
        elif command == "end":
            await event.reply(f"Conversation was ended by {sender.username}")
            newMessage = await client.send_message(otherID, f"Conversation was ended by {sender.username}")
            newEvent = MessageEvent(messageID = event.message.id, relayId = newMessage.id, messageEvent = encryptContent(str({'message': f"Conversation was ended by {sender.username}"})), eventType = command)
            self.lock.acquire()
            db.session.add(newEvent)
            db.session.commit()
            self.lock.release()
            await client.disconnect()
            
        else:
            await event.reply("This is an unsupported command. You could escape this property by placing using two forward slashes or including more in your message")
            
        raise events.StopPropagation

    with ignored(StopIteration):
        async def action_handler(self, event):
            otherID = self.secondaryTelegramID if sender.id == self.primaryTelegramID else self.primaryTelegramID
            if event.action:
                if self.presentAction:
                    self.presentAction.send("cancel")
                else:
                    self.presentAction = relayAction(otherID, event.action)
                newEvent = MessageEvent(messageEvent = encryptContent(str(event.to_dict())), eventType = "chat_action")
                self.lock.acquire()
                db.session.add(newEvent)
                db.session.commit()
                self.lock.release()
            
            if event.cancel:
                if self.presentAction:
                    self.presentAction.send("cancel")
                await client.action(otherID, "cancel")
            
                
        async def relayAction(pid, action):
            with client.action(pid, action):
                while True:
                    state = (yield)
                    if state == 'cancel':
                        break
                
    async def edit_handler(self, event):
        otherID = self.secondaryTelegramID if sender.id == self.primaryTelegramID else self.primaryTelegramID
        await client.edit_message(self.messageRelay[event.id], event.message)
        newEvent = MessageEvent(messageID = event.id, relayID = self.messageRelay[event.id], messageEvent = encryptContent(str(event.to_dict())), eventType = "message_edit")
        self.lock.acquire()
        db.session.add(newEvent)
        db.session.commit()
        self.lock.release()
        
        
    async def read_handler(self, event):
        otherID = self.secondaryTelegramID if sender.id == self.primaryTelegramID else self.primaryTelegramID
        await client.send_read_acknowledge(entity = otherID, message = [messageRelay[mId] for mId in event.message_ids], max_id = messageRelay[event.max_id])
        newEvent = MessageEvent(messageID = mID, messageEvent = encryptContent(str(event.to_dict())), eventType = "read_acknowledgement")
        self.lock.acquire()
        db.session.add(newEvent)
        db.session.commit()
        self.lock.release()
        
    async def message_handler(self, event):
        otherID = self.secondaryTelegramID if sender.id == self.primaryTelegramID else self.primaryTelegramID
        newMessage = await client.send_message(otherID, event.message)
        messageRelay[event.message.id] = newMessage.id
        newEvent = MessageEvent(messageID = event.message.id, relayID = newMessage.id, messageEvent = encryptContent(str(event.to_dict())), eventType = "read_acknowledgement")
        self.lock.acquire()
        db.session.add(newEvent)
        db.session.commit()
        self.lock.release()