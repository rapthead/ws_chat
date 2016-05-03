from rest_framework import serializers
from .models import Message, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('pk', 'title',)


class TagField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        serializer = TagSerializer(value)
        return serializer.data


class MessageSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.display_name')
    time = serializers.ReadOnlyField()
    # tags = TagSerializer(many=True, required=False)
    # tags = serializers.StringRelatedField(many=True, required=False)
    tags = TagField(many=True, required=False, queryset=Tag.objects.all())
    # tags = serializers.RelatedField(read_only=True, many=True)
    # tags = serializers.HyperlinkedRelatedField(many=True, view_name='tag-detail', read_only=True)

    class Meta:
        model = Message
        fields = ('pk', 'message', 'user', 'time', 'tags')
