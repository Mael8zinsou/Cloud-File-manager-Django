from django.db import models
from django.contrib.auth.models import User
#from django.contrib.auth.models import Group

# On va utiliser la classe User de django qui provient de  from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')
    members = models.ManyToManyField(User, through='Membership', related_name='group_memberships')

class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
