from django.db import models


class Post(models.Model):
    """
    Простая модель, чтобы `new.views.home()` мог отобразить список постов.
    """

    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title

