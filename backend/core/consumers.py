import datetime
import json
from time import localtime
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Chat, Message
import base64
from django.core.files.base import ContentFile
from io import BytesIO
from django.utils import timezone



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    
    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = data['sender']  # Assuming 'sender' is the user's ID in the front-end
        file_data = data.get('file', None)  # Get file data (if any)

        # Retrieve the User instance based on the sender_id
        sender = await sync_to_async(User.objects.get)(id=sender_id)

        # Use the chat ID passed from the WebSocket URL
        chat = await sync_to_async(Chat.objects.get)(id=self.chat_id)

        # Get receiver from chat participants
        receiver = await sync_to_async(lambda: chat.participants.exclude(id=sender.id).first())()

        # If a file is sent, decode it
        if file_data:
            # Extract file type and base64 data
            file_type = file_data.split(';')[0].split('/')[1]
            file_content = file_data.split(',')[1]
            decoded_file = base64.b64decode(file_content)

            # Create a file object
            file_name = f"message_{timezone.now().strftime('%Y%m%d%H%M%S')}.{file_type}"
            file = ContentFile(decoded_file, name=file_name)

            # Save the file to the database
            message_obj = await sync_to_async(Message.objects.create)(
                chat_id=chat.id,
                sender=sender,
                receiver=receiver,
                content=message,
                file=file
            )
        else:
            # Create a new message without file
            message_obj = await sync_to_async(Message.objects.create)(
                chat_id=chat.id,
                sender=sender,
                receiver=receiver,
                content=message,
                file=None
            )

        # Broadcast the message with file (if any)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username,  # Send the sender's username
                'receiver': receiver.username,  # Send the receiver's username
                'timestamp': timezone.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
                'file': message_obj.file.url if message_obj.file else None  # Send file URL if available
            }
        )

    # Helper method to get the receiver from the chat participants
    def get_receiver(self, sender):
        # Assuming each chat has exactly two participants
        return sender.chats.first().participants.exclude(id=sender.id).first()

    # Helper method to either get an existing chat or create a new one
    def get_or_create_chat(self, sender, receiver):
        # Check if a chat already exists between the sender and receiver
        chat = Chat.objects.filter(participants=sender).filter(participants=receiver).first()

        if not chat:
            # If no existing chat, create a new one
            chat = Chat.objects.create()
            chat.participants.add(sender, receiver)
            chat.save()
        
        return chat


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']
        file = event.get('file', None)  # Get the file if it's part of the event
        chat_id = event['chat_id']  # Add chat_id to the event

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp,
            'file': file,
            'chat_id': chat_id,  # Include chat_id in the message
        }))

    

