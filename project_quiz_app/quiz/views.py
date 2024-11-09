from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .models import Quiz, Question
from .serializers import QuizSerializer

class QuizCreateView(APIView):
    def post(self, request):
        serializer = QuizSerializer(data = request.data)
        if serializer.is_valid():
            try:
                quiz_data = serializer.validated_data
                quiz = Quiz.objects.create(title = quiz_data['title'])

                # loop through questions list
                # and push to current quiz
                question_objects = []
                for question_data in quiz_data['questions']:
                    question = Question(
                        quiz = quiz,
                        text = question_data['text'],
                        options = question_data['options'],
                        correct_option = question_data['correct_option']
                    )
                    question_objects.append(question)
                
                # bulk create for inserting all questions at once
                Question.objects.bulk_create(question_objects)

                return Response(
                    {"message": "Quiz created successfully.", "quiz_id": quiz.id},
                    status = status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {"error": f"An error occurred: {str(e)}"},
                    status = status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            raise Response(
                {"error": "Invalid data or incomplete fields."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
class QuizDetailView(APIView):
    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            quiz_serializer = QuizSerializer(quiz)

            return Response(quiz_serializer.data, status=status.HTTP_200_OK)
        except Quiz.DoesNotExist:
            raise Response({"error": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)