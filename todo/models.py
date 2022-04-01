from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings
    

class Group(models.Model):
    title = models.CharField(max_length=50)
    group_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Note(models.Model):
    title = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(1, "Title must be greater than 1 characters")]
    )
    group_id = models.ForeignKey(Group, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL,
        through='Done', related_name='done_things')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    

class Done(models.Model) :

    thing = models.ForeignKey(Note, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='done_users')

    # https://docs.djangoproject.com/en/3.0/ref/models/options/#unique-together
    class Meta:
        unique_together = ('thing', 'user')

    def __str__(self) :
        return '%s likes %s'%(self.user.username, self.thing.title[:10])