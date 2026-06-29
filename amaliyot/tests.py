from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from amaliyot.models import TestSession, Question, TestAnswer
from .models import Subject, Topic, Test



class SimpleTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.subject = Subject.objects.create(name='Math')
        self.topic = Topic.objects.create(name='Algebra', subject=self.subject)
        self.test = Test.objects.create(title='Algebra Basics', subject=self.subject, creator=self.user, is_paid=False, view_mode='public')

    def test_subject_creation(self):
        self.assertEqual(str(self.subject), 'Math')

    def test_topic_creation(self):
        self.assertEqual(str(self.topic), 'Algebra')

    def test_test_creation(self):
        self.assertEqual(str(self.test), 'Algebra Basics')


class SubmitAnswerTestCase(APITestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        
        self.session = TestSession.objects.create(user=self.user)
        
    
        self.question = Question.objects.create(
            text="Namuna savol?"
        )
        
        self.url = reverse('submit-answer')  
        
    def test_submit_answer_success(self):
        data = {
            "session_id": self.session.id,
            "question_id": self.question.id,
            "selected_answers": [1, 2]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Javob saqlandi.')
        
        
        self.assertTrue(TestAnswer.objects.filter(session=self.session, question=self.question).exists())
        
    def test_submit_answer_missing_fields(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_submit_answer_invalid_session_or_question(self):
        data = {
            "session_id": 9999,  
            "question_id": 9999,
            "selected_answers": [1]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
