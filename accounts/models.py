from django.db import models
from django.contrib.auth.models import User



class ProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='account/',blank=True, null=True,)
    date_of_birth = models.DateTimeField(blank=True, null=True,)
    address = models.TextField(blank=True, null=True,)

    def __str__(self):
        return self.address

    class Meta:
        db_table = 'Profile'
        managed = True
        verbose_name = 'Profile'
        verbose_name_plural = 'Profile'


class SomeModel(models.Model):
    field1 = models.CharField(max_length=100)
    field2 = models.IntegerField()
    field3 = models.EmailField()

    def __str__(self):
        return self.field1  
    

