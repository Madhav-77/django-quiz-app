from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Answer, Quiz, Question, Result
from .serializers import AnswerFeedbackSerializer, AnswerSummarySerializer, QuizListSerializer, QuizSerializer, SubmitAnswerSerializer

# view for creating quiz
class QuizCreateView(APIView):
    permission_classes = [IsAuthenticated] # restricting access without authentication
    
    def post(self, request):
        serializer = QuizSerializer(data = request.data)
        if serializer.is_valid():
            try:
                quiz_data = serializer.validated_data
                quiz = Quiz.objects.create(title = quiz_data['title'])

                # loop through questions list
                # and store to question table with 
                # current quiz object 
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
            return Response(
                {"error": "Invalid data or incomplete fields."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

# view for fetching quiz
class QuizDetailView(APIView):
    permission_classes = [IsAuthenticated] # restricting access without authentication
    
    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            quiz_serializer = QuizSerializer(quiz)

            return Response(quiz_serializer.data, status=status.HTTP_200_OK)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)

# view for submitting single answer
class SubmitAnswerView(APIView):
    permission_classes = [IsAuthenticated] # restricting access without authentication
    
    def post(self, request):
        serializer = SubmitAnswerSerializer(data=request.data)
        if serializer.is_valid():
            question_id = serializer.validated_data['question_id']
            selected_option = serializer.validated_data['selected_option']
            user = request.user
            
            # check if an answer already exists for this user and question
            existing_answer = Answer.objects.filter(question_id=question_id, user=user).first()
            if existing_answer:
                return Response(
                    {"error": "Answer already exists for this question. Please delete it before resubmitting."},
                    status=status.HTTP_409_CONFLICT
                )

            try:
                question = Question.objects.get(id=question_id)
            except Question.DoesNotExist:
                return Response({"error": "Question not found."}, status=status.HTTP_404_NOT_FOUND)

            correct_option = question.correct_option
            is_correct = selected_option == correct_option
            correct_answer_index = correct_option - 1
            message = "Correct answer!" if is_correct else f"Incorrect. The correct answer is {correct_option}: {question.options[correct_answer_index]}."

            # create the answer object in db
            try:
                answer = Answer.objects.create(
                    question=question,
                    user=user,
                    selected_option=selected_option,
                    is_correct=is_correct
                )
            except Exception as e:
                return Response({"error": "Failed to create answer entry."}, status=status.HTTP_400_BAD_REQUEST)
            
            quiz = question.quiz
            
            # creating entry in result table here
            # if entry already present
            # updating the score based on answer is right or wrong
            try:
                result, created = Result.objects.get_or_create(user=user, quiz=quiz, defaults={'score': 0})
                if not created:
                    # update score if answer is correct
                    if is_correct:
                        result.score += 1
                else:
                    # if new result was created, 
                    # set score to 1 or 0
                    result.score = 1 if is_correct else 0
            except Exception as e:
                return Response({"error": "Failed to retrieve or create result."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # add answer to the result answers list
            result.answers.add(answer)
            
            try:
                # save the result after updating the score and answer to list
                result.save()
            except Exception as e:
                return Response({"error": "Failed to save result."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # feedback response
            feedback_serializer = AnswerFeedbackSerializer(data={
                'is_correct': is_correct,
                'correct_option': correct_option,
                'message': message
            })
            
            if feedback_serializer.is_valid():
                return Response(feedback_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# view for final results for specific user and quiz
class GetResultsView(APIView):
    permission_classes = [IsAuthenticated] # restricting access without authentication

    def get(self, request, quiz_id, user_id):
        # fetch requested quiz
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)

        # fetch result associated with user and quiz
        try:
            result = Result.objects.get(quiz=quiz, user_id=user_id)
        except Result.DoesNotExist:
            return Response({"error": "Results not found for the user in this quiz."}, status=status.HTTP_404_NOT_FOUND)

        # response data
        answers = result.answers.all()
        answers_list = AnswerSummarySerializer(answers, many=True).data
        total_score = result.score
        
        response_data = {
            "quiz_id": quiz.id,
            "user_id": user_id,
            "total_score": total_score,
            "answers": answers_list
        }

        return Response(response_data, status=status.HTTP_200_OK)
   
# Deletes the result for a specific quiz and user 
# Deletes the answers for a specific quiz and user 
class DeleteResultAndAnswerView(APIView):
    def delete(self, request, quiz_id, user_id):
        try:
            result = Result.objects.get(quiz_id=quiz_id, user_id=user_id)
            result.delete()
            answer = Answer.objects.get(quiz_id=quiz_id, user_id=user_id)
            answer.delete()            
            return Response({"message": "Result and Answers deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        except Answer.DoesNotExist:
            return Response({"error": "Answers not found."}, status=status.HTTP_404_NOT_FOUND)
            
        except Result.DoesNotExist:
            return Response({"error": "Result not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": "An error occurred while deleting the result.", "message": e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# view for fetching all quiz list
class QuizListView(APIView):
    permission_classes = [IsAuthenticated] # restricting access without authentication
    
    def get(self, request):
        try:
            user = request.user
            quizzes = Quiz.objects.exclude(id__in=Result.objects.filter(user=user).values('quiz_id'))
            serializer = QuizListSerializer(quizzes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Quiz.DoesNotExist:
            raise Response({"error": "Quiz not found."}, status=status.HTTP_404_NOT_FOUND)