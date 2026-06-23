from __future__ import annotations

from rest_framework import serializers


class ParentMessageCreateSerializer(serializers.Serializer):
	subject = serializers.CharField(max_length=255)
	body = serializers.CharField(max_length=5000)


class ParentMessageSerializer(serializers.Serializer):
	id = serializers.CharField(read_only=True)
	sender_id = serializers.CharField()
	recipient_id = serializers.CharField()
	subject = serializers.CharField()
	body = serializers.CharField()
	is_read = serializers.BooleanField()
	created_at = serializers.CharField(read_only=True)
