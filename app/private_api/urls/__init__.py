"""
To add URLs for another app:
    1. Create `api.urls.your_app_name.py` file.
    2. Set the `app_name` variable for this file.
    3. Add `urlpatterns` list, do not use words like "api",
        or "your_app_name" in your path.
    4. Go to `api.urls.__init__py` file.
    5. Import your module like `from api.urls import your_app_name`.
    6. Add new element to `all_patterns` list:
        all_patterns += [
            path('your_app_name/', include('api.urls.your_app_name'))
        ]

    Note: At step #6 you can set your path to anything you want
    but for convention use "your_app_name" if not required otherwise.

    After this steps you can reverse your url like this:
        >> from django.urls import reverse
        >> reverse('api:your_app_name:your_path_name')
        >> # Note the double namespace!
"""
from django.urls import include, path

app_name = 'private_api'

OK = [
    path('', include('private_api.urls.user')),
    path('', include('private_api.urls.core')),
    path('', include('private_api.urls.photos')),
    path('', include('private_api.urls.videos')),
]
NOT_OK = [
    path('', include('private_api.urls.stories')),
    path('posts/', include('private_api.urls.news')),
]

urlpatterns = [
    path('admin/', include(OK)),
    path('admin/', include(NOT_OK)),
]
