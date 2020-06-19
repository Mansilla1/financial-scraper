from rest_framework import serializers

class ScrapingSerializer(serializers.Serializer):
    save = serializers.BooleanField(required=False, default=False)