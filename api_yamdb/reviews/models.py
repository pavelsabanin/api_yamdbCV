from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from .validators import validate_year
from django.conf import settings


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь')
    )

    email = models.EmailField(unique=True, max_length=254)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=USER)
    bio = models.TextField(blank=True)


class Genre(models.Model):
    name = models.CharField(max_length=256)
    # slug для url
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('-id', )

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256, )
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-id', )

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(verbose_name='Название', max_length=256)
    year = models.PositiveIntegerField(verbose_name='Год',
                                       validators=[validate_year],
                                       db_index=True)
    description = models.TextField(verbose_name='Описание', blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 blank=True, null=True,
                                 related_name='title',
                                 verbose_name='Категория')
    genre = models.ManyToManyField(Genre, blank=True, related_name='title',
                                   verbose_name='Жанр')

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['-id']


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE,
        verbose_name='Название', related_name='reviews'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='reviews'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата', auto_now_add=True, db_index=True
    )
    score = models.PositiveIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(1), MaxValueValidator(10)
        ]
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_name'
            )
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    text = models.TextField(verbose_name='Текст')
    review = models.ForeignKey(Review, on_delete=models.CASCADE,
                               verbose_name='Отзыв',
                               related_name='comments_review')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор',
                               related_name='comments_author')
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.SET_NULL, blank=True,
                              null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, blank=True,
                              null=True)
