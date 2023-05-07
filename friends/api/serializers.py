from rest_framework import serializers
from users.models import User, Friends


class CustomUserSerializer(serializers.ModelSerializer):
    """Кастомный сериалайзер пользователя"""

    friends = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'friends',
        )


class OfferSerializer(serializers.ModelSerializer):
    """Сериалайзер для добавления пользователя в друзья"""

    class Meta:
        model = Friends
        fields = (
            'user_from',
            'user_to',
            'status_user_from',
            'status_user_to',
        )
    

class OutgoingSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра исходящих заявок"""
    user_to = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Friends
        fields = (
            'user_to',
        )

class IncomingSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотра входящих заявок"""

    user_from = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Friends
        fields = (
            'user_from',
        )

class FriendsSerializer(serializers.ModelSerializer):
    """Сериалайзер для просмотр друзей пользователя"""
    user_to = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Friends
        fields = (
            'user_to',
        )
