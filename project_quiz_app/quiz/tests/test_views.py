from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from quiz.models import Answer, Question, Quiz, Result
from rest_framework_simplejwt.tokens import RefreshToken
class QuizCreateViewTest(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.url = '/quiz/api/create/'

        self.valid_payload = {
            "title": "Sample Quiz",
            "questions": [
                {
                    "text": "Sample Question 1?",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_option": 2
                },
                {
                    "text": "Sample Question 2?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_option": 1
                }
            ]
        }

        self.invalid_payload = {
            "title": "",
            "questions": [
                {
                    "text": "Incomplete Question?",
                    "options": ["Only Option"],
                    "correct_option": 1
                }
            ]
        }

    def test_create_quiz_with_valid_data(self):
        response = self.client.post(self.url, data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], "Quiz created successfully.")
        self.assertIn('quiz_id', response.data)

    def test_create_quiz_with_invalid_data(self):
        response = self.client.post(self.url, data=self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_create_quiz_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.url, data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class QuizDetailViewTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.login(username="testuser", password="testpass")
        self.quiz = Quiz.objects.create(title="Sample Quiz")
        self.url = f'/quiz/api/display/{self.quiz.id}/'

    def test_quiz_detail_success(self):
        self.quiz = Quiz.objects.create(title="Sample Quiz")
        
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.quiz.title)

    def test_quiz_detail_not_found(self):
        self.url = f'/quiz/api/display/232/'
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Quiz not found.")

class SubmitAnswerViewTest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')
        self.url = '/quiz/api/submit_answer/'
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        self.quiz = Quiz.objects.create(title="Sample Quiz")
        self.question = Question.objects.create(
            quiz=self.quiz,
            text="Sample Question?",
            options=["Option 1", "Option 2", "Option 3", "Option 4"],
            correct_option=2
        )

    def test_submit_valid_answer(self):
        data = {
            'question_id': self.question.id,
            'selected_option': 2
        }

        # Include the Authorization header with the JWT token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_correct'], True)
        self.assertIn('message', response.data)
        
        data = {
            'question_id': 99999,
            'selected_option': 2
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Question not found.")
        
    def test_submit_answer_without_authentication(self):
        self.client.logout()
        data = {
            'question_id': self.question.id,
            'selected_option': 2
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
    
    def test_submit_incorrect_answer(self):
        data = {
            'question_id': self.question.id,
            'selected_option': 3
        }
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_correct'], False)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "Incorrect. The correct answer is 2: Option 2.")

class GetResultsViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.quiz = Quiz.objects.create(title="Sample Quiz")

        self.question = Question.objects.create(
            quiz=self.quiz,
            text="Sample question?",
            correct_option=4,
            options=["2", "3", "4", "5"]
        )

        self.answer1 = Answer.objects.create(
            user=self.user, question=self.question, selected_option=2, is_correct=False
        )
        self.answer2 = Answer.objects.create(
            user=self.user, question=self.question, selected_option=4, is_correct=True
        )

        self.result = Result.objects.create(quiz=self.quiz, user=self.user, score=3)
        self.result.answers.set([self.answer1, self.answer2])

        self.url = f'http://127.0.0.1:8000/quiz/api/results/{self.quiz.id}/{self.user.id}/'

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.client = APIClient()

    def test_get_results_success(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quiz_id'], self.quiz.id)
        self.assertEqual(response.data['user_id'], self.user.id)
        self.assertEqual(response.data['total_score'], self.result.score)

        self.assertEqual(len(response.data['answers']), 2)

        answer_data = response.data['answers']
        self.assertEqual(answer_data[0]['selected_option'], 2)
        self.assertEqual(answer_data[0]['is_correct'], False)
        self.assertEqual(answer_data[1]['selected_option'], 4)
        self.assertEqual(answer_data[1]['is_correct'], True)

    def test_get_results_no_result(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get(f'/quiz/api/results/{self.quiz.id}/123/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Results not found for the user in this quiz.")
        
    def test_get_results_invalid_quiz(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        response = self.client.get('/quiz/api/results/9999/11212/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Quiz not found.")

class DeleteResultAndAnswerViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.quiz = Quiz.objects.create(title="Sample Quiz")

        self.question = Question.objects.create(
            quiz=self.quiz,
            text="Sample question?",
            correct_option=4,
            options=["2", "3", "4", "5"]
        )

        self.answer = Answer.objects.create(
            user=self.user, question=self.question, selected_option=4, is_correct=True
        )

        self.result = Result.objects.create(quiz=self.quiz, user=self.user, score=4)
        self.result.answers.set([self.answer])

        self.url = f'/quiz/api/delete/{self.quiz.id}/{self.user.id}/'

        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        self.client = APIClient()

    def test_delete_result_not_found(self):
        self.result.delete()

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Result not found.")

    def test_delete_invalid_quiz_or_user(self):
        invalid_url = f'/quiz/api/delete/9999/{self.user.id}/'

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        response = self.client.delete(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Result not found.")

    def test_delete_without_authentication(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")