# nohup gunicorn --chdir /home/swint/git-repo/vmaig_blog/ --bind unix:/tmp/vmaig_blog.socket wsgi:application --reload&
nohup gunicorn --chdir /home/swint/git-repo/vmaig_blog/ --bind 127.0.0.1:8000 wsgi:application --reload&
