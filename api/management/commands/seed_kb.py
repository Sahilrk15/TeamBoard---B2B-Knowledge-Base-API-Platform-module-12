from django.core.management.base import BaseCommand

from api.models import KBEntry


ENTRIES = [
    {
        'question': 'What is select_related in Django ORM?',
        'answer': 'select_related performs a SQL JOIN and fetches related objects in the same query, reducing the number of database round-trips for foreign key and one-to-one relationships.',
        'category': KBEntry.Category.DATABASE,
    },
    {
        'question': 'How does transaction.atomic() work?',
        'answer': 'transaction.atomic() wraps a block of code so all its database writes either all commit together or all roll back together if an exception is raised inside the block.',
        'category': KBEntry.Category.DATABASE,
    },
    {
        'question': 'What is a JWT token?',
        'answer': 'A JWT (JSON Web Token) is a compact, signed token made of a header, payload, and signature, used to prove a request comes from an authenticated party without a server-side session.',
        'category': KBEntry.Category.API,
    },
    {
        'question': 'When should I use Q objects?',
        'answer': 'Q objects let you build complex queries with OR conditions or nested logic that a plain filter() call with keyword arguments cannot express, such as question__icontains=x OR answer__icontains=x.',
        'category': KBEntry.Category.DATABASE,
    },
    {
        'question': 'What is the difference between authentication and authorization?',
        'answer': 'Authentication verifies who a user is, typically via credentials or a token. Authorization determines what that authenticated user is allowed to do.',
        'category': KBEntry.Category.API,
    },
    {
        'question': 'How do Django signals work?',
        'answer': 'Signals let one part of an application notify other parts when an event occurs, such as post_save firing after a model instance is saved, without the sender needing to know who is listening.',
        'category': KBEntry.Category.FRAMEWORK,
    },
    {
        'question': 'What is a ViewSet in Django REST Framework?',
        'answer': 'A ViewSet groups related views (list, create, retrieve, update, delete) into a single class and, combined with a router, automatically generates the URL patterns for a resource.',
        'category': KBEntry.Category.FRAMEWORK,
    },
    {
        'question': 'What is the difference between WSGI and ASGI?',
        'answer': 'WSGI handles one request per thread synchronously, blocking the thread on I/O. ASGI supports asynchronous request handling, freeing the worker to handle other requests while waiting on I/O.',
        'category': KBEntry.Category.FRAMEWORK,
    },
    {
        'question': 'How do I connect to a managed cloud database?',
        'answer': 'Store the host, port, database name, username, and password as environment variables, then configure your ORM connection settings to read from those variables rather than hardcoding credentials.',
        'category': KBEntry.Category.CLOUD,
    },
    {
        'question': 'What is horizontal scaling?',
        'answer': 'Horizontal scaling adds more machines or instances to handle load, as opposed to vertical scaling, which adds more resources (CPU, RAM) to a single existing machine.',
        'category': KBEntry.Category.CLOUD,
    },
    {
        'question': 'What does idempotent mean for an API endpoint?',
        'answer': 'An idempotent endpoint produces the same result no matter how many times the same request is repeated, GET, PUT, and DELETE are typically idempotent, while POST usually is not.',
        'category': KBEntry.Category.API,
    },
    {
        'question': 'What is database indexing?',
        'answer': 'An index is a data structure that lets the database find rows matching a query faster than scanning every row, at the cost of extra storage and slightly slower writes.',
        'category': KBEntry.Category.DATABASE,
    },
]


class Command(BaseCommand):
    help = 'Seeds the knowledge base with sample Q&A entries.'

    def handle(self, *args, **options):
        created_count = 0
        for entry in ENTRIES:
            _, created = KBEntry.objects.get_or_create(
                question=entry['question'],
                defaults={
                    'answer': entry['answer'],
                    'category': entry['category'],
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded {created_count} new KB entries ({len(ENTRIES)} total defined).'
            )
        )
