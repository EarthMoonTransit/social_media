from django.test import TestCase, Client
from django.urls import reverse
from .models import  Group
from django.contrib.auth.models import User
from django.core.cache import cache


class SiteTest(TestCase):
    def setUp(self):
        self.auth_client = Client()
        self.nonauth_client = Client()

        self.auth_user = User.objects.create_user(
                        username="sarah", email="connor.s@skynet.com", password="12345"
                )

        self.auth_client.login(username="sarah", password="12345")
        self.auth_user.save()

        self.urls=(
            reverse('index'),
            reverse('profile', kwargs={'username': 'sarah'}),
            reverse('post', kwargs={"username": 'sarah', 'post_id': 1})
        )

    def test_profile(self):
        response = self.auth_client.get(
            reverse('profile', kwargs={'username': 'sarah'})
            )
        self.assertEqual(response.status_code, 200)
    
    def test_auth_post(self):
        self.auth_client.post(
            reverse('new_post'), data={'text': 'first_yeah'}
            )
        
        response = self.auth_client.get(reverse('post', kwargs={'username': 'sarah', 'post_id': 1}))

        self.assertEqual(str(response.context['post']), 'first_yeah')

    def test_nonauth_post(self):
        response = self.nonauth_client.post(
            reverse('new_post'), data={'text': 'DAVAI'}, follow=True
            )
        self.assertIn('/auth/login/?next=/new/', *response.redirect_chain)

    def test_post_exist(self):
        cache.clear()
        self.auth_client.post(reverse('new_post'), data={'text':'StEbka'})
        response = self.auth_client.get(reverse('post', kwargs={'username': 'sarah', 'post_id':1}))
        for url in self.urls:
            response = self.auth_client.get(url)
            self.assertContains(response, 'StEbka')
    
    def test_post_edit(self):
        cache.clear()
        self.auth_client.post(reverse('new_post'), data={'text': '1klas'})
        first = self.auth_client.get(reverse('post', kwargs={'username': 'sarah', 'post_id': 1}))
        self.auth_client.post(reverse('post_edit', kwargs={'username': 'sarah', 'post_id': 1}), data={'text': '2klas'})
        second = self.auth_client.get(reverse('post', kwargs={'username': 'sarah', 'post_id': 1}))
        self.assertNotEqual(first, second)
        for url in self.urls:
            response = self.auth_client.get(url)
            self.assertContains(response, '2klas')


class NotFoundTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_404(self):
        response = self.client.get('sdfsdf')
        self.assertEqual(response.status_code, 404)


class ImageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.auth_user = User.objects.create_user(
                        username="sarah", email="connor.s@skynet.com", password="12345"
                )

        self.client.login(username="sarah", password="12345")

        self.group = Group.objects.create(title='syka', slug ='noch', description='fuck')
        self.urls = (
            reverse('index'),
            reverse('profile', kwargs={'username': 'sarah'}),
            reverse('post', kwargs={'username': 'sarah', 'post_id': 1}),
        )

    def test_template_img(self):
        cache.clear()
        with open('C:\pythonProject\Dev\hw04_tests-master\hw2\media\posts\sc.jpg', 'rb') as img:
            self.client.post(reverse('new_post'), data={"author": self.auth_user, 'text': 'Yeah', "grop": self.group.pk, 'image': img})
        response = self.client.get(reverse('groups', kwargs={'slug': self.group.slug}))
        for url in self.urls:
            response = self.client.get(url)
            self.assertIn('<img', response.content.decode())

    def test_no_img(self):
        with self.assertRaises(OSError):
            with open('C:\pythonProject\Dev\hw04_tests-master\hw2\media\posts\te.txt', 'rb') as img:
               self.client.post(reverse('new_post'), data={"author": self.auth_user, 'text': 'Yeah', "grop": self.group.pk, 'image': img})


class CashTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.auth_user = User.objects.create_user(
                        username="sarah", email="connor.s@skynet.com", password="12345"
                )
        self.client.login(username="sarah", password="12345")

    def test_cash(self):
        self.client.post(reverse('new_post'), data={'author': self.auth_user, "text":'Nasvai'})
        response = self.client.get(reverse('index'))
        self.client.post(reverse('new_post'), data={'author': self.auth_user, "text":'Snus'})
        response = self.client.get(reverse('index'))
        self.assertNotIn('Snus', response.content.decode())
        cache.clear()
        response = self.client.get(reverse('index'))
        self.assertIn('Snus', response.content.decode())
