from rest_framework import serializers


from users.models import User, Scores


class UserSerializer(serializers.ModelSerializer):

    id = serializers.UUIDField(source='aitu_id')

    name = serializers.CharField(source='first_name')
    lastname = serializers.CharField(source='last_name')

    avatarThumb = serializers.CharField(source='avatar_thumb', required=False)

    class Meta:
        model = User
        fields = ['id', 'name', 'lastname', 'avatar', 'avatarThumb', 'joined']
