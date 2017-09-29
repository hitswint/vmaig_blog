#! /bin/bash

# nohup gunicorn --chdir /home/swint/git-repo/vmaig_blog/ --bind unix:/tmp/vmaig_blog.socket vmaig_blog.wsgi:application --reload&
/bin/bash -c "source /home/swint/.virtualenvs/py3/bin/activate; gunicorn --chdir /home/swint/git-repo/vmaig_blog --bind 127.0.0.1:8000 vmaig_blog.wsgi:application --reload; exec /bin/bash -i"
