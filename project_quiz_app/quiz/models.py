from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    title = models.CharField(max_length=200)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE) # foreign key to map with quiz object
    text = models.CharField(max_length=500)
    options = models.JSONField(default=list)
    correct_option = models.PositiveIntegerField()
    
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE) # foreign key to map with question object
    user = models.ForeignKey(User, related_name='answer_user', on_delete=models.CASCADE) # foreign key to map with user object
    selected_option = models.PositiveIntegerField()
    is_correct = models.BooleanField()
    
class Result(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='results_quiz', on_delete=models.CASCADE) # foreign key to map with quiz object
    user = models.ForeignKey(User, related_name='results_user', on_delete=models.CASCADE) # foreign key to map with user object
    score = models.PositiveIntegerField()
    answers = models.ManyToManyField(Answer)