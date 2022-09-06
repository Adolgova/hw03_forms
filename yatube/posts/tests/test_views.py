from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
import datetime as dt

from posts.models import Group, Post

COUNT_TEST_POSTS = 13
POSTS_ON_PAGE = 10

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.authorized_client_1 = Client()
        cls.user_1 = User.objects.create_user(username='TestUser1')
        cls.authorized_client_1.force_login(cls.user_1)

        cls.authorized_client_2 = Client()
        cls.user_2 = User.objects.create_user(username='TestUser2')
        cls.authorized_client_2.force_login(cls.user_2)

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
        cls.post_1 = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост1',
            group=cls.group_1,
        )
        cls.post_2 = Post.objects.create(
            author=cls.user_1,
            text='Тестовый пост2',
            group=cls.group_1,
        )

        cls.PAGES_REVERSE = {
            'index': reverse(
                'posts:index'
            ),
            'group_list_1': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group_1.slug}
            ),
            'group_list_2': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group_2.slug}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': cls.user_1.username}
            ),
            'post_detail': reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post_1.id}
            ),
            'post_create': reverse(
                'posts:post_create'
            ),
            'post_edit': reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post_1.id}
            )
        }

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            self.PAGES_REVERSE['index']: 'posts/index.html',
            self.PAGES_REVERSE['group_list_1']: 'posts/group_list.html',
            self.PAGES_REVERSE['profile']: 'posts/profile.html',
            self.PAGES_REVERSE['post_detail']: 'posts/post_detail.html',
            self.PAGES_REVERSE['post_create']: 'posts/post_create.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_1.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_views_index_group_list_profile_show_correct_context(self):
        """Шаблон index, group_list и profile, post_detail сформированы
        с правильным контекстом."""

        PAGES = {
            self.PAGES_REVERSE['index'],
            self.PAGES_REVERSE['group_list_1'],
            self.PAGES_REVERSE['profile'],
        }

        for page in PAGES:
            response = self.authorized_client_1.get(page)

            post = response.context['page_obj'][0]

            post_atribute_and_expected = {
                post.id: self.post_1.id,
                post.author.username: self.post_1.author.username,
                post.text: self.post_1.text,
                post.pub_date.date(): dt.date.today(),
                post.group.title: self.post_1.group.title,
                post.group.id: self.post_1.group.id,
                post.group.description: self.post_1.group.description,
            }

            for atribute, expected in post_atribute_and_expected.items():
                self.assertEqual(atribute, expected)

    def test_views_group_list_page_show_correct_context(self):
        """Список постов в шаблоне group_list отфильтрован по группе.
        """

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['group_list_1']
        )

        first_post = response.context['page_obj'][0]
        second_post = response.context['page_obj'][1]

        group_id_1 = first_post.group.id
        group_id_2 = second_post.group.id

        self.assertEqual(group_id_1, group_id_2)

    def test_views_profile_page_show_correct_context(self):
        """Список постов в шаблоне profile отфильтрован по пользователю.
        """

        response = self.authorized_client_1.get(self.PAGES_REVERSE['profile'])

        first_post = response.context['page_obj'][0]
        second_post = response.context['page_obj'][1]

        post_author_1 = first_post.author.id
        post_author_2 = second_post.author.id

        self.assertEqual(post_author_1, post_author_2)

    def test_views_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом:
        пост, отфильтрованный по id.
        """

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['post_detail']
        )
        post = response.context['post']

        post_atribute_and_expected = {
            post.id: self.post_1.id,
            post.author.username: self.post_1.author.username,
            post.text: self.post_1.text,
            post.pub_date.date(): dt.date.today(),
            post.group.title: self.post_1.group.title,
            post.group.id: self.post_1.group.id,
            post.group.description: self.post_1.group.description,
        }

        for atribute, expected in post_atribute_and_expected.items():
            self.assertEqual(atribute, expected)

    def test_views_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом:
        форма редактирования поста,отфильтрованного по id.
        """

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['post_edit']
        )
        form_contents = {
            'text': self.post_1.text,
            'group': self.group_1,
        }

        for value, expected in form_contents.items():
            with self.subTest(value=value):
                form_content = getattr(
                    response.context.get('form').instance,
                    value
                )
                self.assertEqual(form_content, expected)

    def test_views_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом:
        форма создания поста.
        """

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['post_edit']
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_views_post_is_on_expected_pages(self):
        """При создании поста c указанной группой этот пост
        появляется на главной странице сайта, на странице
        выбранной группы, в профайле пользователя.
        """
        reverse_names = {
            self.PAGES_REVERSE['index'],
            self.PAGES_REVERSE['profile'],
            self.PAGES_REVERSE['group_list_1'],
        }

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                context = self.authorized_client_1.get(
                    reverse_name
                ).context['page_obj']
                self.assertIn(self.post_1, context)

    def test_views_post_is_not_on_expected_pages(self):
        """При создании поста c указанной группой этот пост
        не появляется странице другой группы.
        """

        response = self.authorized_client_1.get(
            self.PAGES_REVERSE['group_list_2']
        )
        context = response.context['page_obj']
        self.assertNotIn(self.post_1, context)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Автор поста
        cls.author = User.objects.create_user(username='author')
        cls.post_author = Client()
        cls.post_author.force_login(cls.author)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Создание 13 постов
        for i in range(COUNT_TEST_POSTS):
            Post.objects.bulk_create([
                Post(author=cls.author,
                     text=f'Тестовый пост № {i}',
                     group=cls.group)
            ])

    def test_pages_contain_correct_records(self):
        '''Проверка количества постов на первой и второй страницах. '''
        paginator_pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ),
            reverse(
                'posts:profile', kwargs={'username': self.author.username}
            )
        ]
        for url in paginator_pages:
            with self.subTest(url=url):
                first_response = self.post_author.get(url)
                second_response = self.post_author.get((url) + '?page=2')
                self.assertEqual(len(
                    first_response.context['page_obj']),
                    POSTS_ON_PAGE
                )
                self.assertEqual(len(
                    second_response.context['page_obj']),
                    COUNT_TEST_POSTS - POSTS_ON_PAGE
                )
