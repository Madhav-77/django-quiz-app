from django.urls import path
from .views import DeleteResultAndAnswerView, GetResultsView, QuizCreateView, QuizDetailView, SubmitAnswerView, QuizListView

urlpatterns = [
    path('api/quizzes/', QuizListView.as_view(), name='list-quizzes'),
    path('api/quizzes/create/', QuizCreateView.as_view(), name='create-quiz'),
    path('api/quizzes/<int:quiz_id>/', QuizDetailView.as_view(), name='retrieve-quiz'),
    path('api/quizzes/submit/', SubmitAnswerView.as_view(), name='submit-answer'),
    path('api/quizzes/<int:quiz_id>/users/<int:user_id>/results/', GetResultsView.as_view(), name='get-results'),
    path('api/quizzes/<int:quiz_id>/users/<int:user_id>/delete/', DeleteResultAndAnswerView.as_view(), name='delete-results-and-answers'),
]