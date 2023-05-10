from rest_framework import serializers

from users.models import Friends, User

from .filters import get_friends


class CurrentCustomSerializer(serializers.ModelSerializer):
    """Кастомный сериалайзер для вывод информации о текущем пользователе"""

    friends = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'friends',
        )

    def get_friends(self, obj):
        """Просмотр друзей текущего пользователя"""
        user = self.context.get('request').user
        return get_friends(self, user)


class CustomUserSerializer(serializers.ModelSerializer):
    """Кастомный сериалайзер пользователя"""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
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
    """
    Сериалайзер для просмотра исходящих заявок
    и друзей пользователя
    """
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
