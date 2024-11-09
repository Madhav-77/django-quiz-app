from rest_framework import serializers
from .models import Quiz, Question

class QuestionSerializer(serializers.ModelSerializer):
    text = serializers.CharField(max_length=500)
    options = serializers.ListField(
        child=serializers.CharField(),
        min_length=4,
        max_length=4,
        help_text="Each question must have 4 options."
    )
    correct_option = serializers.IntegerField(
        min_value=1,
        max_value=4,
        help_text="Provide the index between 1-4 for the correct option.",
        read_only=True
    )
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # remove correct_option field for GET cals
        representation.pop('correct_option', None)
        
        return representation

    class Meta:
        model = Question
        fields = ['text', 'options', 'correct_option']

class QuizSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=200)
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ['title', 'questions']
        
class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option = serializers.IntegerField(min_value=1, max_value=4)

class AnswerFeedbackSerializer(serializers.Serializer):
    is_correct = serializers.BooleanField()
    correct_option = serializers.IntegerField(min_value=1, max_value=4)
    message = serializers.CharField()