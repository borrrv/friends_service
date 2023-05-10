from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Friends(models.Model):
    user_from = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='friends',
        verbose_name='Пользователь',
    )
    user_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_friend',
    )
    status_user_from = models.BooleanField(null=True)
    status_user_to = models.BooleanField(null=True)

    class Meta:
        verbose_name = 'Друзья'
        verbose_name_plural = 'Друзья'
        ordering = ('id',)

    def __str__(self):
        return f"{self.user_to}"
