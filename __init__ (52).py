from django.db import models
from apps.users.models import User


class Conversation(models.Model):
    """Maps to `conversations` table."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_conversations')
    vet = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vet_conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversations'
        unique_together = ['owner', 'vet']

    def __str__(self):
        return f'Chat: {self.owner.email} ↔ {self.vet.email}'


class Message(models.Model):
    """Maps to `messages` table."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message_text = models.TextField(blank=True)
    file_url = models.TextField(blank=True)  # for images/PDFs
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']

    def __str__(self):
        return f'Msg in conv {self.conversation_id} from {self.sender.email}'
