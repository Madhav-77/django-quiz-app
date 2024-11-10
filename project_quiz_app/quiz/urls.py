from django.urls import path
from .views import GetResultsView, QuizCreateView, QuizDetailView, SubmitAnswerView

urlpatterns = [
    path('api/create/', QuizCreateView.as_view(), name='create-quiz'),
    path('api/display/<int:quiz_id>/', QuizDetailView.as_view(), name='get-quiz'),
    path('api/submit_answer/', SubmitAnswerView.as_view(), name='submit_answer'),
    path('api/results/<int:quiz_id>/<int:user_id>/', GetResultsView.as_view(), name='get_results'),
]