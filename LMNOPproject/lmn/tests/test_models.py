from django.test import TestCase

from django.contrib.auth.models import User
from django.db import IntegrityError
# Create your tests here.


class TestUser(TestCase):

    def test_create_user_all_fields_required(self):

        # TODO is this testing the right thing? 

        u = User()
        with self.assertRaises(IntegrityError):
            u.save()

        u = User(username='bob')
        with self.assertRaises(IntegrityError):
            u.save()

        u = User(username='bob', email='bob@bob.com')
        with self.assertRaises(IntegrityError):
            u.save()

        u = User(username='bob', email='bob@bob.com', first_name='bob')
        with self.assertRaises(IntegrityError):
            u.save()


    def test_create_user_duplicate_username_fails(self):

        user = User(username='bob', email='bob@bob.com', first_name='bob', last_name='bob')
        user.save()

        user2 = User(username='bob', email='another_bob@bob.com', first_name='bob', last_name='bob')
        with self.assertRaises(IntegrityError):
            user2.save()


    def test_create_user_duplicate_username_case_insensitive_fails(self):

        user = User(username='bob', email='bob@bob.com', first_name='bob', last_name='bob')
        user.save()

        user2 = User(username='Bob', email='another_bob@bob.com', first_name='bob', last_name='bob')
        with self.assertRaises(IntegrityError):
            user2.save()


    def test_create_user_duplicate_email_fails(self):
        user = User(username='bob', email='bob@bob.com', first_name='bob', last_name='bob')
        user.save()

        user2 = User(username='bob', email='bob@bob.com', first_name='bob', last_name='bob')
        with self.assertRaises(IntegrityError):
            user2.save()


    def test_create_user_duplicate_email_case_insensitive_fails(self):
        user = User(username='bob', email='bob@bob.com', first_name='bob', last_name='bob')
        user.save()

        user2 = User(username='another_bob', email='Bob@bob.com', first_name='bob', last_name='bob')
        with self.assertRaises(IntegrityError):
            user2.save()
