You will need Python 3.10 or lower to run this server. This is because of pysha3, which will not install on newer versions.

## Docker configuration
If you want run this project with docker, you need to change `DATABASE_HOST=db` and `REDIS_HOST=redis`