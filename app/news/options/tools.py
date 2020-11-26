import re
from django.template.defaultfilters import slugify

# ------------------------------ News Status ----------------------------------

CLOSED = 'Closed'
STAFF_ONLY = 'Staff only'
OPEN = 'Open'

NEWS_STATUS = (
    (CLOSED, 'Closed'),
    (STAFF_ONLY, 'Staff only'),
    (OPEN, 'Open'),
)

TOP_NEWS = (
    (1, "Top Left"),
    (2, "Top Right"),
)
# ------------------------------ Title Types ----------------------------------

PLAIN = 'Plain'
BOLD = 'Bold'
RED = 'Red'

TITLE_TYPES = (
    (PLAIN, 'Plain'),
    (BOLD, 'Bold'),
    (RED, 'Red'),
)

# ------------------------------ Post Content Types ---------------------------

MAIN_TEXT = 'Main Text'
TEXT = 'Text'
ACCORDION = 'Accordion'
VIDEO = 'Video'
GALLERY = 'Gallery'
QUOTE = 'Quote'

CONTENT_TYPES = (
    (MAIN_TEXT, 'Main Text'),
    (TEXT, 'Text'),
    (ACCORDION, 'Accordion'),
    (VIDEO, 'Video'),
    (GALLERY, 'Gallery'),
    (QUOTE, 'Quote'),
)


# ----------------------------- Tools -----------------------------------------


def truncate_sentence(value):
    """
    Return the first two sentence of the given value

    :param `value` => Text
    """
    return ' '.join(re.split(r'(?<=[.!?])\s', value)[:2])


def to_e_alphabet(title):
    for value in title:
        if value in ["ə", "Ə"]:
            title = title.replace(value, "e")
        elif value in ["ı"]:
            title = title.replace(value, "i")
    return title


def generate_unique_slug(klass, field):
    """
    return unique slug if origin slug is exist.
    eg: `foo-bar` => `foo-bar-1`

    :param `klass` is Class model.
    :param `field` is specific field for title.
    """
    field = to_e_alphabet(field)
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    while klass.objects.filter(slug=unique_slug).exists():
        unique_slug = '%s-%d' % (origin_slug, numb)
        numb += 1
    return unique_slug
