import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat.
    URL: ws/chat/{conversation_id}/
    Authentication is handled by JWTAuthMiddlewareStack.
    """

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope.get('user')

        # Verify user has access to this conversation
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        has_access = await self.check_access(self.conversation_id, self.user)
        if not has_access:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send recent message history
        messages = await self.get_recent_messages(self.conversation_id)
        await self.send(text_data=json.dumps({
            'type': 'history',
            'messages': messages,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get('type', 'message')

        if msg_type == 'message':
            text = data.get('text', '').strip()
            file_url = data.get('file_url', '')

            if not text and not file_url:
                return

            # Save to database
            message = await self.save_message(
                conversation_id=self.conversation_id,
                sender=self.user,
                text=text,
                file_url=file_url,
            )

            # Broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )

        elif msg_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'user_id': self.user.id,
                    'is_typing': data.get('is_typing', False),
                }
            )

    async def chat_message(self, event):
        """Handler for group messages."""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
        }))

    async def typing_indicator(self, event):
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'is_typing': event['is_typing'],
            }))

    @database_sync_to_async
    def check_access(self, conversation_id, user):
        from .models import Conversation
        try:
            conv = Conversation.objects.get(id=conversation_id)
            return conv.owner == user or conv.vet == user
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, conversation_id, sender, text, file_url):
        from .models import Message
        msg = Message.objects.create(
            conversation_id=conversation_id,
            sender=sender,
            message_text=text,
            file_url=file_url,
        )
        return {
            'id': msg.id,
            'sender_id': sender.id,
            'sender_email': sender.email,
            'text': text,
            'file_url': file_url,
            'timestamp': msg.created_at.isoformat(),
        }

    @database_sync_to_async
    def get_recent_messages(self, conversation_id, limit=50):
        from .models import Message
        messages = Message.objects.filter(
            conversation_id=conversation_id
        ).select_related('sender').order_by('-created_at')[:limit]
        return [
            {
                'id': m.id,
                'sender_id': m.sender_id,
                'sender_email': m.sender.email,
                'text': m.message_text,
                'file_url': m.file_url,
                'timestamp': m.created_at.isoformat(),
            }
            for m in reversed(list(messages))
        ]
