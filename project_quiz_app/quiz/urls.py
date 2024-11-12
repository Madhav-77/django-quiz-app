from django.urls import path
from .views import DeleteResultAndAnswerView, GetResultsView, QuizCreateView, QuizDetailView, SubmitAnswerView, QuizListView

urlpatterns = [
    path('api/quiz_list/', QuizListView.as_view(), name='get-quiz-list'),
    path('api/create/', QuizCreateView.as_view(), name='create-quiz'),
    path('api/display/<int:quiz_id>/', QuizDetailView.as_view(), name='get-quiz'),
    path('api/submit_answer/', SubmitAnswerView.as_view(), name='submit_answer'),
    path('api/results/<int:quiz_id>/<int:user_id>/', GetResultsView.as_view(), name='get_result'),
    path('api/delete/<int:quiz_id>/<int:user_id>/', DeleteResultAndAnswerView.as_view(), name='delete_result_answer'),
]