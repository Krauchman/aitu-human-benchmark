from django.db import models


class User(models.Model):
    aitu_id = models.UUIDField(primary_key=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    avatar = models.CharField(max_length=255, blank=True)
    avatar_thumb = models.CharField(max_length=255, blank=True)

    joined = models.DateTimeField(auto_now_add=True)


class Scores(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores_history')
    date = models.DateTimeField(auto_now_add=True)

    number_memory = models.IntegerField(blank=True, null=True)
    reaction_time = models.FloatField(blank=True, null=True)
