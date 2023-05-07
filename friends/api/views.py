from djoser.views import UserViewSet
from .serializers import FriendsSerializer, IncomingSerializer, CustomUserSerializer, OfferSerializer, OutgoingSerializer
from users.models import User, Friends
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_200_OK

class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    
    """Добавление в друзья"""
    @action(detail=True, methods=['POST'])
    def offer(self, request, id):
        user_from = self.request.user
        user_to = get_object_or_404(User, id=id)
        serializer = CustomUserSerializer
        repeat = Friends.objects.filter(user_from_id=user_from.id, user_to_id=user_to.id)
        obj = Friends.objects.filter(user_from_id=user_to.id, user_to_id=user_from.id)
        if user_from.id == user_to.id:
            content = {"error": "Нельзя добавить себя в друзья"}
            return Response(content, status=HTTP_400_BAD_REQUEST)
        else:
            if obj.exists():
                friends_obj = obj.first()
                friends_obj.status_user_from = True
                friends_obj.status_user_to = True
                friends_obj.save()
                content = {"message": f"Пользователь {user_to} теперь у Вас в друзьях"}
                return Response(content, status=HTTP_200_OK)
            if repeat.exists():
                content = {"error": "Вы уже отправили заявку в друзья этому пользователю"}
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

    """Просмотр исходящих заявок"""
    @action(detail=False, methods=['get'])
    def outgoing(self, request):
        user = self.request.user.id
        out = Friends.objects.filter(user_from_id=user, status_user_from=0)
        serializer = OutgoingSerializer(
            instance=out,
            many=True,
        )
        return Response(serializer.data)
    
    """Просмотр входящих заявок"""
    @action(detail=False, methods=['get'])
    def incoming(self, request):
        user = self.request.user.id
        inc = Friends.objects.filter(user_to_id=user, status_user_to=0)
        serializer = IncomingSerializer(
            instance=inc,
            many=True,
        )
        return Response(serializer.data)
    
    """Просмотр моих друзей"""
    @action(detail=False, methods=['get'])
    def friends(self, request):
        user = self.request.user.id
        friend = Friends.objects.filter(user_from_id=user, status_user_from=1)
        serializer = FriendsSerializer(
            instance=friend,
            many=True
        )
        return Response(serializer.data)
    
    """Принять, отклонить заявку в друзья"""
    @action(detail=True, methods=['post', 'delete'])
    def add(self, request, id):
        user_to = self.request.user
        user_from = get_object_or_404(User, id=id)
        obj = Friends.objects.filter(user_from_id=user_from.id, user_to_id=user_to.id)
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
                content = {"message": f"Пользователь {user_from} теперь у Вас в друзьях"}
                return Response(content, status=HTTP_200_OK)
        if self.request.method == 'DELETE':
            if obj.exists() and friends.status_user_from == False:
                friends.status_user_from = False
                friends.status_user_to = None
                friends.save()
                content = {"message": f"Вы отклонили заявку {user_from} в друзья"}
                return Response(content, status=HTTP_204_NO_CONTENT)
            else:
                content = {"error": f"Нельзя отклонить заявку, так как {user_from} уже у вас в друзьях"}
                return Response(content, status=HTTP_204_NO_CONTENT)
    
    """Удалить пользователя из друзей"""
    @action(detail=True, methods=["DELETE"])
    def delete(self, request, id):
        user_from = self.request.user
        user_to = get_object_or_404(User, id=id)
        obj = Friends.objects.filter(user_from_id=user_from.id, user_to_id=user_to.id)
        filter_friends = Friends.objects.filter(
            user_from_id=user_to.id,
            user_to_id=user_from.id,
        )
        friends = obj.first()
        friends_2 = filter_friends.first()
        print(friends)
        print(friends_2)
        if obj.exists() or filter_friends.exists():
            try:
                if friends_2.status_user_to == None:
                    content = {"error": f"{user_to} нет в Вашем списке друзей"}
                    return Response(content, status=HTTP_204_NO_CONTENT)
                else:
                    if friends_2.status_user_from == None:
                        friends_2.delete()
                        content = {"message": f"{user_to} удален из друзей"}
                        return Response(content, status=HTTP_204_NO_CONTENT)
                    else:
                        friends_2.status_user_from = False
                        friends_2.status_user_to = None
                        friends_2.save()
                        content = {"message": f"{user_to} теперь подписан на вас"}
                        return Response(content, status=HTTP_204_NO_CONTENT)
            except AttributeError:
                if friends.status_user_from == None:
                    friends.delete()
                    content = {"error": f"{user_to} нет в Вашем списке друзей"}
                    return Response(content, status=HTTP_400_BAD_REQUEST)
                else:
                    if friends.status_user_to == None:
                        friends.delete()
                        content = {"message": f"{user_to} удален из друзей"}
                        return Response(content, status=HTTP_204_NO_CONTENT)
                    else:
                        friends.status_user_from = None
                        friends.status_user_to = False
                        friends.save()
                        content = {"message": f"{user_to} теперь подписан на вас"}
                        return Response(content, status=HTTP_204_NO_CONTENT)
        else:
            content = {"error": "Вы с пользователем не подписаны друг на друга"}
            return Response(content, status=HTTP_400_BAD_REQUEST)
