# ...existing code...
from django.conf import settings
from django.db import models

class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField("Nom", max_length=150)
    email = models.EmailField("Email")
    subject = models.CharField("Objet", max_length=255)
    body = models.TextField("Message")
    is_read = models.BooleanField("Lu", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} — {self.name}"
# ...existing code...