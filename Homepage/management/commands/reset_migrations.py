# myapp/management/commands/drop_all_tables.py
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Drop all tables from the database"

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute(
                """
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema()) LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
            """
            )
        self.stdout.write(self.style.SUCCESS("Successfully dropped all tables"))


# # myapp/management/commands/reset_migrations.py
# from django.core.management.base import BaseCommand
# from django.db import connection


# class Command(BaseCommand):
#     help = "Reset migration history"

#     def handle(self, *args, **kwargs):
#         with connection.cursor() as cursor:
#             # cursor.execute("DROP TABLE django_admin_log;")
#             cursor.execute("DELETE FROM django_migrations WHERE app = 'admin';")
#             cursor.execute("DELETE FROM django_migrations WHERE app = 'Homepage';")
#             cursor.execute("DELETE FROM django_migrations WHERE app = 'blog';")
#             cursor.execute("DELETE FROM django_migrations WHERE app = 'cv_api';")
#             cursor.execute("DELETE FROM django_migrations WHERE app = 'i';")
#             cursor.execute("DELETE FROM django_migrations WHERE app = 'book_';")
#             cursor.execute("DELETE FROM django_migrations WHERE app = 'cart';")
#             cursor.execute("DELETE FROM django_migrations WHERE app = 'checkout';")
#         self.stdout.write(self.style.SUCCESS("Successfully reset migration history"))
