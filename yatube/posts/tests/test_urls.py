from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, 200)


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='NoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        # Создаем третий клиент
        self.author = Client()
        # Клиент - автор
        self.author.force_login(PostURLTests.post.author)

    def test_urls_uses_correct_template_for_all(self):
        """Страницы доступны любому пользователю."""
        templates_url_names_for_all = {
            '/': ('posts/index.html'),
            f'/group/{PostURLTests.group.slug}/': (
                'posts/group_list.html'),
            f'/profile/{PostURLTests.user.username}/': (
                'posts/profile.html'),
            f'/posts/{PostURLTests.post.id}/': (
                'posts/post_detail.html'),
        }
        for address, template in templates_url_names_for_all.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_author_correct_template(self):
        """Страница доступна автору."""
        author_templates_url_names = {
            f'/posts/{PostURLTests.post.id}/edit/': 'posts/post_create.html',
        }
        for address, template in author_templates_url_names.items():
            with self.subTest(address=address):
                response = self.author.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_authorized_client_correct_template(self):
        """Страница доступна авторизованному пользователю."""
        authorized_templates_url_names = {
            '/create/': 'posts/post_create.html',
        }
        for address, template in authorized_templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template_for_all_404(self):
        """Ошибка при запросе несуществующей страницы."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
