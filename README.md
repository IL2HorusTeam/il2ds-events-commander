IL-2 FB Horus Commander
=======================

1. Create postgres database and setup IL2_HORUS_COMMANDER_DB_URL environment variable:
    
        export IL2_HORUS_COMMANDER_DB_URL="postgres://login:password@localhost/database_name"


2. Setup IL2_HORUS_COMMANDER_SECRET_TOKEN environment variable:
    
        export IL2_HORUS_COMMANDER_SECRET_TOKEN="my_long_long_long_production_secret_random_key"

3. Install dependencies:
    
        pip install -r requirements.txt

4. Sync database (you will be asked to create a superuser):

        python ./manage.py syncdb

5. Start application

        python ./manage.py runserver
