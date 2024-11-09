from django.urls import path
from .views import QuizCreateView, QuizDetailView, SubmitAnswerView

urlpatterns = [
    path('create/', QuizCreateView.as_view(), name='create-quiz'),
    path('display/<int:quiz_id>/', QuizDetailView.as_view(), name='get-quiz'),
    path('submit_answer/', SubmitAnswerView.as_view(), name='submit_answer'),
]