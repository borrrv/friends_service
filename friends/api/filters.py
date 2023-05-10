from django.db.models import Q

from users.models import Friends, User


def get_friends(self, user):
    """Просмотр друзей текущего пользователя"""
    user = user
    friends = Friends.objects.filter(Q(user_from_id=user.id) |
                                     Q(user_to_id=user.id),
                                     status_user_to=True)
    friend_ids = []
    for friend in friends:
        if friends.first().user_to.id == user.id:
            friend_ids.append(friend.user_from_id)
        else:
            friend_ids.append(friend.user_to_id)
    friends_username = User.objects.filter(
        id__in=friend_ids).values_list('username', flat=True)
    return friends_username
