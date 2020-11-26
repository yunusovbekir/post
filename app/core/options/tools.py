import datetime

SIDE = 'Side'
HEADER = 'Header'
FOOTER = 'Footer'

POSITION = (
    (SIDE, 'Side'),
    (HEADER, 'Header'),
    (FOOTER, 'Footer'),
)


def user_directory_path(instance, filename):
    """
    :return: `uploads/17-04-2020/news/COVID-19.jpeg`
    """
    today = datetime.datetime.today()
    if instance._meta.verbose_name_plural.lower() == 'post contents':
        model_title = 'News'
    else:
        model_title = instance._meta.verbose_name_plural.lower()
    return "uploads/{}/{}-{}-{}/{}".format(
        model_title,
        today.day,
        today.month,
        today.year,
        filename
    )
