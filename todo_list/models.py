from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    #task title,date created and time(for database), optional due date, completion status(todo, completed)->changes by button star
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    important = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True) 
    due_date = models.DateField(blank=True, null=True)
    #This is a string representation of the tasks
    def __str__(self):
        return self.title 