from django.db import IntegrityError
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from quiz.models import Answer, Question, Quiz
from quiz.serializers import AnswerSummarySerializer, QuestionSerializer, QuizSerializer, SubmitAnswerSerializer
from django.contrib.auth.models import User

class QuestionSerializerTest(APITestCase):
    # Set up a quiz object, used for creating questions
    def setUp(self):
        self.quiz = Quiz.objects.create(title="Sample Quiz")
        self.valid_data = {
            'text': "Sample Question?",
            'options': ["Option 1", "Option 2", "Option 3", "Option 4"],
            'correct_option': 4
        }
        self.invalid_data = {
            'text': "Sample Question?",
            'options': ["Option 1", "Option 2", "Option 3"], # invalid, less than 4 options
            'correct_option': 5 # invalid, correct_option should be between 1 and 4
        }

    # test to serialize invalid data, will raise validation error
    def test_invalid_serializer(self):
        serializer = QuestionSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        
        self.assertIsNot('options', serializer.errors)
        self.assertIsNot('correct_option', serializer.errors)

    # test that options has exactly 4 options
    def test_options_length_validation(self):
        invalid_data = self.valid_data.copy()
        invalid_data['options'] = ["Option 1", "Option 2", "Option 3"] # Invalid
        
        serializer = QuestionSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('options', serializer.errors)

        invalid_data['options'] = ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"] # invalid
        
        serializer = QuestionSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('options', serializer.errors)

    # test that correct_option is excluded in GET API
    def test_to_exclude_correct_option(self):
        question = Question.objects.create(
            quiz=self.quiz,
            text="Sample Question?",
            options=["Option 1", "Option 2", "Option 3", "Option 4"],
            correct_option=3
        )
        serializer = QuestionSerializer(question)
        representation = serializer.data
        
        self.assertNotIn('correct_option', representation)
        self.assertEqual(representation['text'], "Sample Question?")
        self.assertEqual(representation['options'], ["Option 1", "Option 2", "Option 3", "Option 4"])

class QuizSerializerTest(TestCase):
    
    # Setting up data
    def setUp(self):
        self.valid_question_data = {
            'text': "Sample question?",
            'options': ["Option 1", "Option 2", "Option 3", "Option 4"],
            'correct_option': 4
        }

    def test_valid_serializer(self):
        quiz_data = {
            'title': "Quiz",
            'questions': [self.valid_question_data]
        }
        serializer = QuizSerializer(data=quiz_data)
        
        self.assertTrue(serializer.is_valid())
        
        quiz = serializer.save()
        self.assertEqual(quiz.title, "Quiz")
        self.assertEqual(quiz.questions.count(), 1)
        
        # verify the question data in quiz
        question = quiz.questions.first()
        self.assertEqual(question.text, "Sample question?")
        self.assertEqual(question.options, ["Option 1", "Option 2", "Option 3", "Option 4"])
        self.assertEqual(question.correct_option, 4)

    def test_invalid_serializer_missing_title(self):
        quiz_data = {
            'title': None,
            'questions': [self.valid_question_data]
        }
        serializer = QuizSerializer(data=quiz_data)
        
        # invalid due to missing title
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    # invalid question with missing 'correct_option'
    def test_invalid_serializer_invalid_question(self):
        invalid_question_data = {
            'text': "Sample question?",
            'options': ["Option 1", "Option 2", "Option 3", "Option 4"]
        }
        quiz_data = {
            'title': "Quiz",
            'questions': [invalid_question_data]
        }
        serializer = QuizSerializer(data=quiz_data)
        
        # fail, missing 'correct_option'
        self.assertFalse(serializer.is_valid())
        self.assertIn('questions', serializer.errors)
        
    # invalid question less than 4 options
    def test_invalid_question_options_length(self):
        invalid_question_data = {
            'text': "Sample question?",
            'options': ["Option 1", "Option 2"], # Incorrect
            'correct_option': 4
        }
        quiz_data = {
            'title': "Quiz",
            'questions': [invalid_question_data]
        }
        serializer = QuizSerializer(data=quiz_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('questions', serializer.errors)

    # out-of-range 'correct_option'
    def test_invalid_question_correct_option(self):
        invalid_question_data = {
            'text': "Sample question?",
            'options': ["Option 1", "Option 2", "Option 3", "Option 4"],
            'correct_option': 5 # Out of range
        }
        quiz_data = {
            'title': "Quiz",
            'questions': [invalid_question_data]
        }
        serializer = QuizSerializer(data=quiz_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('questions', serializer.errors)

    # Quiz without questions
    def test_empty_quiz(self):
        quiz_data = {
            'title': "Empty Quiz",
            'questions': []
        }
        serializer = QuizSerializer(data=quiz_data)
        
        self.assertTrue(serializer.is_valid())
        quiz = serializer.save()
        self.assertEqual(quiz.title, "Empty Quiz")
        self.assertEqual(quiz.questions.count(), 0)

    # Quiz with valid questions
    def test_multiple_questions(self):
        multiple_questions_data = [
            {
                'text': "Sample question?",
                'options': ["Option 1", "Option 2", "Option 3", "Option 4"],
                'correct_option': 4
            },
            {
                'text': "Sample question 2?",
                'options': ["Option 6", "Option 7", "Option 8", "Option 9"],
                'correct_option': 1
            }
        ]
        quiz_data = {
            'title': "Quiz",
            'questions': multiple_questions_data
        }
        serializer = QuizSerializer(data=quiz_data)
        
        self.assertTrue(serializer.is_valid())
        quiz = serializer.save()
        
        self.assertEqual(quiz.title, "Quiz")
        self.assertEqual(quiz.questions.count(), 2)
        
        first_question = quiz.questions.first()
        self.assertEqual(first_question.text, "Sample question?")
        self.assertEqual(first_question.correct_option, 4)

class AnswerSummarySerializerTest(APITestCase):
    
    def setUp(self):
        quiz = Quiz.objects.create(title="Sample Quiz")
        self.user = User.objects.create(username="testuser")
        
        self.question = Question.objects.create(
            quiz=quiz,
            options=['1', '2', '3', '4'],
            text="Sample Question?",
            correct_option=4
        )

        self.answer = Answer.objects.create(
            user=self.user,
            question=self.question,
            selected_option=4,
            is_correct=True
        )

    def test_valid_serializer(self):
        serializer = AnswerSummarySerializer(instance=self.answer)
        
        self.assertEqual(serializer.data['question_id'], self.answer.question.id)
        self.assertEqual(serializer.data['correct_option'], self.answer.question.correct_option)
        self.assertEqual(serializer.data['selected_option'], self.answer.selected_option)
        self.assertEqual(serializer.data['is_correct'], self.answer.is_correct)

    # Test Answer instance without a question
    def test_invalid_answer_no_question(self):
        with self.assertRaises(IntegrityError):
            Answer.objects.create(selected_option=4, is_correct=False)
            
    # Test selected option is incorrect
    def test_invalid_selected_option(self):
        answer = Answer.objects.create(
            user=self.user,
            question=self.question,
            selected_option=3,
            is_correct=False
        )
        serializer = AnswerSummarySerializer(instance=answer)

        self.assertEqual(serializer.data['is_correct'], False)
        self.assertEqual(serializer.data['selected_option'], 3)
        self.assertEqual(serializer.data['question_id'], answer.question.id)
        self.assertEqual(serializer.data['correct_option'], answer.question.correct_option)
        
    # Test Create multiple answers
    def test_multiple_answers(self):
        answer1 = Answer.objects.create(
            user=self.user,
            question=self.question,
            selected_option=4,
            is_correct=True
        )
        answer2 = Answer.objects.create(
            user=self.user,
            question=self.question,
            selected_option=3,
            is_correct=False
        )
        
        answers = [answer1, answer2]
        serializer = AnswerSummarySerializer(answers, many=True)
        
        self.assertEqual(len(serializer.data), 2)
        self.assertEqual(serializer.data[0]['is_correct'], True)
        self.assertEqual(serializer.data[0]['selected_option'], 4)
        self.assertEqual(serializer.data[1]['is_correct'], False)
        self.assertEqual(serializer.data[1]['selected_option'], 3)
  
class SubmitAnswerSerializerTest(APITestCase):
    
    def test_valid_data(self):
        data = {'question_id': 1, 'selected_option': 2}
        serializer = SubmitAnswerSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_question_id(self):
        data = {'selected_option': 2}
        serializer = SubmitAnswerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('question_id', serializer.errors)

    def test_missing_selected_option(self):
        data = {'question_id': 1}
        serializer = SubmitAnswerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('selected_option', serializer.errors)

    def test_selected_option_out_of_range(self):
        data = {'question_id': 1, 'selected_option': 5}
        serializer = SubmitAnswerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('selected_option', serializer.errors)

    def test_selected_option_below_min_value(self):
        data = {'question_id': 1, 'selected_option': 0}
        serializer = SubmitAnswerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('selected_option', serializer.errors)      