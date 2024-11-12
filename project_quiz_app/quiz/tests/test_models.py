from django.forms import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User
from quiz.models import Answer, Question, Quiz, Result

class TestQuizModel(TestCase):
    # this will run before each test
    # this will create Quiz instance for test methods to test
    def setUp(self):
        self.quiz = Quiz.objects.create(title="Sample Quiz")

    # test that Quiz instance is created with the title field
    def test_quiz_creation(self):
        self.assertEqual(self.quiz.title, "Sample Quiz")
        self.assertIsInstance(self.quiz, Quiz)

    # test that title field has max length of 200
    def test_quiz_title_max_length(self):
        max_length = self.quiz._meta.get_field('title').max_length
        self.assertEqual(max_length, 200)

class TestQuestionModel(TestCase):
    # this will run before each test
    # this will create Quiz instance for test methods to test
    def setUp(self):
        self.quiz = Quiz.objects.create(title="Sample Quiz")

    # create a Question instance associated with the quiz
    def test_question_creation(self):
        question = Question.objects.create(
            quiz=self.quiz,
            text="Sample Question?",
            options=["Option 1", "Option 2", "Option 3", "Option 4"],
            correct_option=1
        )
        
        # checks if question is created correctly with right attributes
        self.assertEqual(question.text, "Sample Question?")
        self.assertEqual(question.quiz, self.quiz)
        self.assertEqual(question.correct_option, 1)
        self.assertEqual(question.options, ["Option 1", "Option 2", "Option 3", "Option 4"])

    # test that title field has max length of 500
    def test_text_field_max_length(self):
        question = Question(
            quiz=self.quiz,
            text="A" * 500,
            options=["Option 1", "Option 2", "Option 3", "Option 4"],
            correct_option=1
        )
        question.full_clean()
        self.assertEqual(len(question.text), 500)

        # test exceeding the max length
        question.text = "A" * 501
        with self.assertRaises(ValidationError):
            question.full_clean()

class TestAnswerModel(TestCase):
    # this will run before each test
    # this will create Answer instance for test methods to test
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.quiz = Quiz.objects.create(title="Sample Quiz")
        self.question = Question.objects.create(
            quiz=self.quiz,
            text="Sample Question?",
            options=["Option 1", "Option 2", "Option 3", "Option 4"],
            correct_option=1
        )
        self.answer = Answer.objects.create(
            question=self.question,
            user=self.user,
            selected_option=1,
            is_correct=True
        )

    # test that Answer instance is created with the title field
    def test_answer_creation(self):
        self.assertEqual(self.answer.question, self.question)
        self.assertEqual(self.answer.user, self.user)
        self.assertEqual(self.answer.selected_option, 1)
        self.assertTrue(self.answer.is_correct)
    
    def test_selected_option_field(self):
        answer = Answer.objects.create(
            question=self.question,
            user=self.user,
            selected_option=3,
            is_correct=False
        )
        self.assertEqual(answer.selected_option, 3)
                
    # test the BooleanField 'is_correct'
    def test_is_correct_field(self):
        answer = Answer.objects.create(
            question=self.question,
            user=self.user,
            selected_option=2,
            is_correct=True
        )
        self.assertTrue(answer.is_correct)

        answer = Answer.objects.create(
            question=self.question,
            user=self.user,
            selected_option=3,
            is_correct=False
        )
        self.assertFalse(answer.is_correct)

class TestResultModel(TestCase):
    
    # this will run before each test
    # this will create Quiz, User, Answer instance for test methods to test
    def setUp(self):
        self.quiz = Quiz.objects.create(title="Sample Quiz")
        self.user = User.objects.create(username="testuser")
        self.answer1 = Answer.objects.create(
            question=self.quiz.questions.create(text="Sample Question 1?", options=["Option 1", "Option 2", "Option 3", "Option 4"], correct_option=1),
            user=self.user,
            selected_option=1,
            is_correct=True
        )
        self.answer2 = Answer.objects.create(
            question=self.quiz.questions.create(text="Sample Question 2", options=["Option 1", "Option 2", "Option 3", "Option 4"], correct_option=2),
            user=self.user,
            selected_option=1,
            is_correct=False
        )
    
    # test that Result instance is created
    def test_result_creation(self):
        result = Result.objects.create(
            quiz=self.quiz,
            user=self.user,
            score=8
        )
        
        self.assertEqual(result.quiz, self.quiz)
        self.assertEqual(result.user, self.user)
        self.assertEqual(result.score, 8)
        self.assertEqual(result.answers.count(), 0)
        
    # test that Result can associate with multiple answers
    def test_result_with_answers(self):
        result = Result.objects.create(
            quiz=self.quiz,
            user=self.user,
            score=8
        )
        result.answers.add(self.answer1, self.answer2)
        
        self.assertEqual(result.answers.count(), 2)
        self.assertIn(self.answer1, result.answers.all())
        self.assertIn(self.answer2, result.answers.all())