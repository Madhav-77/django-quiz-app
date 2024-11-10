from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from .models import Answer, Quiz, Question
from .serializers import AnswerFeedbackSerializer, QuizSerializer, SubmitAnswerSerializer

class QuizCreateView(APIView):
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]
    
    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            quiz_serializer = QuizSerializer(quiz)

            return Response(quiz_serializer.data, status=status.HTTP_200_OK)
        except Quiz.DoesNotExist:
            raise Response({"error": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)
        
class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = SubmitAnswerSerializer(data=request.data)
        if serializer.is_valid():
            question_id = serializer.validated_data['question_id']
            selected_option = serializer.validated_data['selected_option']
            user = request.user

            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                raise Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)

            correct_option = question.correct_option
            is_correct = selected_option == correct_option
            correct_answer_index = correct_option - 1
            message = "Correct answer!" if is_correct else f"Incorrect. The correct answer is {correct_option}: {question.options[correct_answer_index]}."

            # Create or update the answer entry
            Answer.objects.create(
                question=question,
                user=user,
                selected_option=selected_option,
                is_correct=is_correct
            )

            # Prepare feedback response
            feedback_serializer = AnswerFeedbackSerializer(data={
                'is_correct': is_correct,
                'correct_option': correct_option,
                'message': message
            })
            if feedback_serializer.is_valid():
                return Response(feedback_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)