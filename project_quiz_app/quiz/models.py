from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    text = models.CharField(max_length=500)
    options = models.JSONField()
    correct_option = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.quiz.title} - {self.text}"
    
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='answer_user', on_delete=models.CASCADE)
    selected_option = models.PositiveIntegerField()
    is_correct = models.BooleanField()
    
class Result(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='results_quiz', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='results_user', on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    answers = models.ManyToManyField(Answer)
    
    def __str__(self):
        return f"Result for Quiz {self.quiz.title} by User {self.user.username}"
