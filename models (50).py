from rest_framework import serializers, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Conversation, Message
from apps.users.models import User


class ConversationSerializer(serializers.ModelSerializer):
    vet_name = serializers.SerializerMethodField()
    vet_email = serializers.EmailField(source='vet.email', read_only=True)
    owner_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'vet', 'vet_name', 'vet_email', 'owner_name',
                  'created_at', 'last_message', 'unread_count']

    def get_vet_name(self, obj):
        try:
            return obj.vet.profile.name or obj.vet.email
        except Exception:
            return obj.vet.email

    def get_owner_name(self, obj):
        try:
            return obj.owner.profile.name or obj.owner.email
        except Exception:
            return obj.owner.email

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if msg:
            return {'text': msg.message_text[:80], 'timestamp': msg.created_at}
        return None

    def get_unread_count(self, obj):
        # Placeholder — extend with read receipts
        return 0


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_email', 'sender_name',
                  'message_text', 'file_url', 'created_at']

    def get_sender_name(self, obj):
        try:
            return obj.sender.profile.name or obj.sender.email
        except Exception:
            return obj.sender.email


class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(
            owner=user
        ).union(
            Conversation.objects.filter(vet=user)
        ).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        vet_id = request.data.get('vet_id')
        vet = get_object_or_404(User, id=vet_id, role='vet')

        conv, created = Conversation.objects.get_or_create(
            owner=request.user,
            vet=vet,
        )
        return Response(
            ConversationSerializer(conv).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        conv = get_object_or_404(Conversation, id=conversation_id)
        user = self.request.user
        if conv.owner != user and conv.vet != user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()
        return Message.objects.filter(conversation=conv).select_related('sender__profile')
