from django.db import models


class User(models.Model):
    aitu_id = models.UUIDField(primary_key=True)
    phone = models.CharField(max_length=255, unique=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    avatar = models.CharField(max_length=255, blank=True)
    avatar_thumb = models.CharField(max_length=255, blank=True)

    joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.first_name) + ' ' + str(self.last_name)

    def get_latest_scores(self):
        if not self.scores_history.filter(latest=True).exists():
            if not self.scores_history.exists():
                self.scores_history.create()
            else:
                latest = self.scores_history.order_by('date').last()
                latest.latest = True
                latest.save(update_fields=['latest'])

        return self.scores_history.filter(latest=True).last()


class Scores(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scores_history')
    date = models.DateTimeField(auto_now_add=True)
    latest = models.BooleanField(default=True)

    number_memory = models.IntegerField(blank=True, null=True, default=None)
    reaction_time = models.FloatField(blank=True, null=True, default=None)
