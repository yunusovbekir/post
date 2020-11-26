from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    Post,
    Comment,
    PostLike,
    PostDislike,
    CommentLike,
    CommentDislike,
)


@receiver(post_save, sender=Post,
          dispatch_uid='create_post_like_dislike_tables')
def create_post_like_dislike_tables(sender, created, **kwargs):
    """
    As soon as a new Post object is created,
     create its Post Like and Post Dislike objects
    """

    instance = kwargs.get('instance')
    if created:
        PostLike.objects.create(post=instance)
        PostDislike.objects.create(post=instance)


@receiver(post_save, sender=Comment,
          dispatch_uid='create_comment_like_dislike_tables')
def create_comment_like_dislike_tables(sender, created, **kwargs):
    """
    As soon as a new Comment object is created,
     create its Comment Like and Comment Dislike objects
    """

    instance = kwargs.get('instance')
    if created:
        CommentLike.objects.create(comment=instance)
        CommentDislike.objects.create(comment=instance)
