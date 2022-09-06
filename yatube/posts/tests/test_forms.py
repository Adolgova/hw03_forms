from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.authorized_client = Client()
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_client.force_login(cls.user)

        cls.group_1 = Group.objects.create(
            title='Тестовая группа1',
            slug='test-slug1',
            description='Тестовое описание1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            id=1,
            group=cls.group_1,
        )
        cls.form = PostForm()

    def test_form_create_post(self):
        """При отправке валидной формы со страницы create_post
        создаётся новая запись в базе данных.
        """

        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новая запись',
            'group': self.group_1.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': 'TestUser'}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Новая запись',
            ).exists()
        )

    def test_form_edit_post(self):
        """при отправке валидной формы со страницы post_edit
        происходит изменение поста с post_id в базе данных.
        """

        posts_count = Post.objects.count()
        form_data = {
            'text': 'Обновлённая запись поста',
            'group': self.group_2.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Обновлённая запись поста',
                group=self.group_2,
            ).exists()
        )
