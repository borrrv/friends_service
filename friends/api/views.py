from django.db.models import Q
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)

from users.models import Friends, User

from .filters import get_friends
from .serializers import (CurrentCustomSerializer, IncomingSerializer,
                          OfferSerializer, OutgoingSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CurrentCustomSerializer

    @action(detail=True, methods=['POST'])
    def offer(self, request, id):
        """Добавление в друзья"""
        user_from = self.request.user
        user_to = get_object_or_404(User, id=id)
        serializer = CurrentCustomSerializer
        repeat = Friends.objects.filter(
            user_from_id=user_from.id,
            user_to_id=user_to.id)
        obj = Friends.objects.filter(
            user_from_id=user_to.id,
            user_to_id=user_from.id)
        if user_from.id == user_to.id:
            content = {"error": "Нельзя добавить себя в друзья"}
            return Response(content, status=HTTP_400_BAD_REQUEST)
        else:
            if obj.exists():
                friends_obj = obj.first()
                friends_obj.status_user_from = True
                friends_obj.status_user_to = True
                friends_obj.save()
                content = {"message":
                           f"Пользователь {user_to} теперь у Вас в друзьях"}
                return Response(content, status=HTTP_200_OK)
            if repeat.exists():
                content = {"error":
                           "Заявка в друзья этому пользователю уже отправлена"}
                return Response(content, status=HTTP_400_BAD_REQUEST)
            serializer = OfferSerializer(
                data={
                    'user_from': user_from.id,
                    'user_to': user_to.id,
                    'status_user_from': False,
                    'status_user_to': False,
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            content = {"message": "Заявка в друзья успешно отправлена"}
            return Response(content, status=HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def outgoing(self, request):
        """Просмотр исходящих заявок"""
        user = self.request.user.id
        out = Friends.objects.filter(user_from_id=user, status_user_from=0)
        serializer = OutgoingSerializer(
            instance=out,
            many=True,
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def incoming(self, request):
        """Просмотр входящих заявок"""
        user = self.request.user.id
        inc = Friends.objects.filter(user_to_id=user, status_user_to=0)
        serializer = IncomingSerializer(
            instance=inc,
            many=True,
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def friends(self, request):
        """Просмотр друзей текущего пользователя"""
        user = self.request.user
        return Response(get_friends(self, user))

    @action(detail=True, methods=['post', 'delete'])
    def add(self, request, id):
        """Принять, отклонить заявку в друзья"""
        user_to = self.request.user
        user_from = get_object_or_404(User, id=id)
        obj = Friends.objects.filter(
            user_from_id=user_from.id,
            user_to_id=user_to.id)
        friend_obj = Friends.objects.filter(
            user_from_id=user_from.id,
            user_to_id=user_to.id,
            status_user_to=True)
        friends = obj.first()
        if self.request.method == 'POST':
            if friend_obj.exists():
                content = {"error": f"{user_from} уже у вас в друзьях"}
                return Response(content, status=HTTP_400_BAD_REQUEST)
            if obj.exists():
                friends.status_user_from = True
                friends.status_user_to = True
                friends.save()
                content = {"message":
                           f"Пользователь {user_from} теперь у Вас в друзьях"}
                return Response(content, status=HTTP_200_OK)
        if self.request.method == 'DELETE':
            print(friend_obj.first())
            if obj.exists() and friends.status_user_from is False:
                friends.status_user_from = False
                friends.status_user_to = None
                friends.save()
                content = {"message":
                           f"Вы отклонили заявку {user_from} в друзья"}
                return Response(content, status=HTTP_204_NO_CONTENT)
            else:
                content = {"error":
                           f"Нельзя отклонить заявку,{user_from} уже ваш друг"}
                return Response(content, status=HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["DELETE"])
    def delete(self, request, id):
        """Удалить пользователя из друзей"""
        user_from = self.request.user
        user_to = get_object_or_404(User, id=id)
        obj = Friends.objects.filter(
            user_from_id=user_from.id,
            user_to_id=user_to.id)
        filter_friends = Friends.objects.filter(
            user_from_id=user_to.id,
            user_to_id=user_from.id,
        )
        friends = obj.first()
        friends_2 = filter_friends.first()
        if obj.exists() or filter_friends.exists():
            try:
                if friends_2.status_user_to is None:
                    content = {"error": f"{user_to} нет в Вашем списке друзей"}
                    return Response(content, status=HTTP_204_NO_CONTENT)
                else:
                    if friends_2.status_user_from is None:
                        friends_2.delete()
                        content = {"message": f"{user_to} удален из друзей"}
                        return Response(content, status=HTTP_204_NO_CONTENT)
                    else:
                        friends_2.status_user_from = False
                        friends_2.status_user_to = None
                        friends_2.save()
                        content = {"message":
                                   f"{user_to} теперь подписан на вас"}
                        return Response(content, status=HTTP_204_NO_CONTENT)
            except AttributeError:
                if friends.status_user_from is None:
                    friends.delete()
                    content = {"error": f"{user_to} нет в Вашем списке друзей"}
                    return Response(content, status=HTTP_400_BAD_REQUEST)
                else:
                    if friends.status_user_to is None:
                        friends.delete()
                        content = {"message": f"{user_to} удален из друзей"}
                        return Response(content, status=HTTP_204_NO_CONTENT)
                    else:
                        friends.status_user_from = None
                        friends.status_user_to = False
                        friends.save()
                        content = {"message":
                                   f"{user_to} теперь подписан на вас"}
                        return Response(content, status=HTTP_204_NO_CONTENT)
        else:
            content = {"error":
                       "Вы с пользователем не подписаны друг на друга"}
            return Response(content, status=HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def status(self, request, id):
        """Проверка статуса дружбы"""
        user_from = self.request.user
        user_to = get_object_or_404(User, id=id)
        friends = Friends.objects.filter(Q(
            user_from_id=user_from.id,
            user_to_id=user_to.id,
            status_user_from=True,) |
            Q(
            user_from_id=user_to.id,
            user_to_id=user_from.id,
            status_user_from=True,)
        )
        incoming = Friends.objects.filter(Q(
            user_from_id=user_from.id,
            user_to_id=user_to.id,
            status_user_to=False,) |
            Q(
            user_from_id=user_to.id,
            user_to_id=user_from.id,
            status_user_from=False,
            status_user_to=None,)
        )
        outgoing = Friends.objects.filter(Q(
            user_from_id=user_to.id,
            user_to_id=user_from.id,
            status_user_to=False,) |
            Q(
            user_from_id=user_from.id,
            user_to_id=user_to.id,
            status_user_from=False,
            status_user_to=None,)
        )
        if user_from.id == user_to.id:
            content = {"error":
                       "Нельзя посмотреть статус дружбы с самим собой"}
            return Response(content, status=HTTP_400_BAD_REQUEST)
        if friends.first() is not None:
            content = {"message": f"{user_to} ваш друг"}
            return Response(content, status=HTTP_200_OK)
        if incoming.first() is not None:
            content = {"message":
                       f"У вас входящая завка в друзья от {user_to}"}
            return Response(content, status=HTTP_200_OK)
        if outgoing.first() is not None:
            content = {"message":
                       f"У вас исходящая заявка в друзья к {user_to}"}
            return Response(content, status=HTTP_200_OK)
        else:
            content = {"error":
                       f"Вы с {user_to} не друзья, "
                       f"и у вас с ним нет заявок друг другу"}
            return Response(content, status=HTTP_204_NO_CONTENT)
