from django.db import models


class Record(models.Model):
    player_name = models.CharField(max_length=50)
    score = models.IntegerField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'records'
        managed = False
        ordering = ['-score', '-created_at']

    def __str__(self):
        return f"{self.player_name} - {self.score}"