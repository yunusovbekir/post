from rest_framework.exceptions import ValidationError


def get_comment_count_tool(post):
    """
    Get count of direct comments on a post and their replies
    """
    direct_comment_count = post.post_commented.count()
    replied_comments_count = 0
    for count in post.post_commented.all():
        for _ in count.reply.all():
            replied_comments_count += 1
    return direct_comment_count + replied_comments_count


def name_validation(value, error_message_1, error_message_2):
    """
    Validation function for Contact Form
    :param value: field name
    :param error_message_1: exception message for first condition
    :param error_message_2: exception message for second condition
    :return: error-free value
    """
    if not value:
        raise ValidationError(error_message_1)
    if any([letter for letter in value
            if not letter.isalpha() and not letter.isspace()]):
        raise ValidationError(error_message_2)
    return value


def normalize_email(email):
    """
    Normalize the email address by making lowercase the domain part of it.
    """
    email = email or ''
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except ValueError:
        pass
    else:
        email = email_name + '@' + domain_part.lower()
    return email
