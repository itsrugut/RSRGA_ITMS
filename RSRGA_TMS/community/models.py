from django.db import models


# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=100)  # Title of the event
    date = models.DateTimeField()  # Date and time of the event
    description = models.TextField()  # Description of the event

    def __str__(self):
        return self.title


class Feedback(models.Model):
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name or 'Anonymous'} on {self.timestamp}"
