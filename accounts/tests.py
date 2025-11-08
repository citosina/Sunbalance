"""Tests for the accounts app."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class RegistrationTests(APITestCase):
    def test_register_creates_user_and_returns_payload(self):
        payload = {"username": "sunny", "email": "s@example.com", "password": "strongpass"}
        response = self.client.post(reverse("accounts-register"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="sunny").exists())

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(username="sunny", password="strongpass")
        payload = {"username": "sunny", "email": "s@example.com", "password": "strongpass"}
        response = self.client.post(reverse("accounts-register"), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_endpoint_returns_tokens(self):
        User.objects.create_user(username="sunny", password="strongpass")
        response = self.client.post(reverse("token_obtain_pair"), {"username": "sunny", "password": "strongpass"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
