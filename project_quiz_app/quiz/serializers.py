from rest_framework import serializers
from .models import Quiz, Question

class QuestionSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=500)
    options = serializers.ListField(
        child=serializers.CharField(max_length=255),
        min_length=4,
        max_length=4,
        help_text="Each question must have 4 options."
    )
    correct_option = serializers.IntegerField(
        min_value=1,
        max_value=4,
        help_text="Provide the index between 1-4 for the correct option."
    )

    class Meta:
        model = Question
        fields = ['text', 'options', 'correct_option']

class QuizSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=200)
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['title', 'questions']