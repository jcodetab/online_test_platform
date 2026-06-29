from django.db import models
from django.contrib.auth.models import User



class Message(models.Model):
    sender = models.CharField(max_length=100)
    recipient = models.CharField(max_length=100)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)      

    def __str__(self):
        return f'{self.sender} -> {self.recipient}: {self.text}'
    

class MessageTest(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    def __str__(self):
        return self.title
    

class TestResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message_test = models.ForeignKey(MessageTest, on_delete=models.CASCADE)
    score = models.IntegerField()  
    completed_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"{self.user.username} - {self.message_test.title} - {self.score}"
    



    


    

