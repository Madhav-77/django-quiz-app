from rest_framework import serializers
from .models import Answer, Quiz, Question, Result

# used in QuizSerializer for set of questions
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
        help_text="Provide the index between 1-4 for the correct option."
    )
    
    # to reuse the same serializer for fetching quiz 
    # and hide the correct_option field
    # used in GET cals 'get-quiz' API
    def to_representation(self, instance):
        representation = super().to_representation(instance)        
        representation.pop('correct_option', None)
        return representation

    class Meta:
        model = Question
        fields = ['id', 'text', 'options', 'correct_option']

# validates and serializes fields 
# for create quiz API and Get quiz API
class QuizSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=200)
    questions = QuestionSerializer(many=True) # question serializer to show questions

    class Meta:
        model = Quiz
        fields = ['title', 'questions']
        
    def create(self, validated_data):
        # Extract the questions data from the validated data
        questions_data = validated_data.pop('questions')
        
        # Create the quiz object first
        quiz = Quiz.objects.create(**validated_data)
        
        # Now create the questions and associate them with the quiz
        for question_data in questions_data:
            Question.objects.create(quiz=quiz, **question_data)
        
        return quiz

# validates the answers list for final result view
class AnswerSummarySerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source='question.id')
    correct_option = serializers.IntegerField(source='question.correct_option')
    
    class Meta:
        model = Answer
        fields = ['question_id', 'selected_option', 'correct_option', 'is_correct']

# validates submit answer request
class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option = serializers.IntegerField(min_value=1, max_value=4)

# validates the answer feedback received by user after answer submission
class AnswerFeedbackSerializer(serializers.Serializer):
    is_correct = serializers.BooleanField()
    correct_option = serializers.IntegerField(min_value=1, max_value=4)
    message = serializers.CharField()
    
class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title']