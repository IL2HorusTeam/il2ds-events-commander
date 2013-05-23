IL-2 FB Horus Commander
=======================

1. Create PostgreSQL database and setup IL2_HORUS_COMMANDER_DB_URL environment variable:

        export IL2_HORUS_COMMANDER_DB_URL="postgres://login:password@localhost/database_name"


2. Setup IL2_HORUS_COMMANDER_SECRET_TOKEN environment variable:

        export IL2_HORUS_COMMANDER_SECRET_TOKEN="my_long_long_long_production_secret_random_key"

3. Install Redis

4. For running on Unix-like systems install Wine

5. Install dependencies:

        pip install -r requirements.txt

6. Sync database (you will be asked to create a superuser):

        python ./manage.py syncdb

7. Collect static files:

        python ./manage.py collectstatic

8. Start application

        python ./manage.py runserver
