# A news agency website
This back-end system was created for a news agency. Since the company's website was completely changed, I decided to make it public to show as a portfolio.
90 percent of app was written by me. Used technologies are Django Framework, Django Rest Framework, Docker, PostgreSQL, Elasticsearch. 
API tests were written with Unit Tests and API documentation was written with Swagger. 

## Installation on local machine
```sh
$ git clone https://github.com/yunusovbekir/post.git

# activate virtual environment
$ source .venv/bin/activate
$ pip install -r requirements.txt

# build postgres database with docker
$ cd _development/
$ docker-compose up -d --build
$ cd ../app/

# post/app/
$ python manage.py migrate
```

### Create a super user
```sh
# post/app/
$ python manage.py createsuperuser
```

### Run tests
```sh
# post/app/
python manage.py test
```

### Check PEP8 errors
```
# post/app/
flake8
```

