import os
import struct
import fcntl
import termios
from django.db import connection
from django.conf import settings


def terminal_width():
    """
    Function to compute the terminal width.
    """
    width = 0
    try:
        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(1, termios.TIOCGWINSZ, s)
        width = struct.unpack('HHHH', x)[1]
    except (struct.error, fcntl.error, termios.error) as e:
        print(f"Error computing terminal width: {e}")

    if width <= 0:
        try:
            width = int(os.environ['COLUMNS'])
        except (KeyError, ValueError) as e:
            print(f"Error getting terminal width from environment: {e}")

    return width if width > 0 else 80


def SqlPrintingMiddleware(get_response):
    """
    Middleware to print SQL queries in the terminal during a request in debug mode.
    """
    def middleware(request):
        response = get_response(request)

        if not settings.DEBUG or not connection.queries:
            return response

        indentation = 2
        print(f"\n\n{' ' * indentation}\033[1;35m[SQL Queries for]\033[1;34m {request.path_info}\033[0m\n")
        width = terminal_width()
        total_time = 0.0

        for query in connection.queries:
            nice_sql = query['sql'].replace('"', '').replace(',', ', ')
            sql = f"\033[1;31m[{query['time']}]\033[0m {nice_sql}"
            total_time += float(query['time'])

            while len(sql) > width - indentation:
                print(f"{' ' * indentation}{sql[:width - indentation]}")
                sql = sql[width - indentation:]
            print(f"{' ' * indentation}{sql}\n")

        print(f"{' ' * indentation}\033[1;32m[TOTAL TIME: {total_time} seconds]\033[0m")
        print(f"{' ' * indentation}\033[1;32m[TOTAL QUERIES: {len(connection.queries)}]\033[0m")

        return response

    return middleware
