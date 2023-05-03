from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]
    first_name = models.CharField(max_length=254, verbose_name="Имя")
    last_name = models.CharField(max_length=254, verbose_name="Фамилия")
    username = models.CharField(
        verbose_name="username",
        max_length=254,
        unique=True,
    )
    email = models.EmailField(
        verbose_name="email address",
        max_length=254,
        unique=True,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Following(models.Model):
    follower = models.ForeignKey(
        User,
        related_name="follower",
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
    )
    following = models.ForeignKey(
        User,
        related_name="following",
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["-id"]
        constraints = [
            UniqueConstraint(
                fields=["follower", "following"], name="unique_following"
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
