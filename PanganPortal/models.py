from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField()

    def update_rating(self):
        # Рассчитываем суммарный рейтинг каждой статьи автора, умножаем на 3
        post_rating = self.post_set.aggregate(models.Sum('rating'))['rating__sum'] * 3 or 0

        # Рассчитываем суммарный рейтинг всех комментариев автора
        comment_rating = self.user.comment_set.aggregate(models.Sum('rating'))['rating__sum'] or 0

        # Рассчитываем суммарный рейтинг всех комментариев к статьям автора
        comment_rating_to_posts = self.post_set.aggregate(models.Sum('comment__rating'))['comment__rating__sum'] or 0

        # Обновляем рейтинг автора
        self.rating = post_rating + comment_rating + comment_rating_to_posts
        self.save()

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    CHOICES = [('article', 'Статья'), ('news', 'Новость')]
    type = models.CharField(max_length=10, choices=CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.IntegerField()

    def preview(self):
        preview_length = 124
        if len(self.content) > preview_length:
            return self.content[:preview_length] + '...'
        else:
            return self.content

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField()

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
