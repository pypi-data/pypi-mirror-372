import os
import struct
import fcntl
import termios
from flask import request, g
from sqlalchemy import event
from sqlalchemy.engine import Engine


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


def SqlPrintingMiddleware(app):
    @app.before_request
    def before_request():
        g.queries = []

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if 'queries' not in g:
            g.queries = []
        g.queries.append({
            'sql': statement,
            'time': context.execution_time
        })

    @app.after_request
    def after_request(response):
        if app.config['DEBUG'] and hasattr(g, 'queries'):
            indentation = 2
            print(f"\n\n{' ' * indentation}\033[1;35m[SQL Queries for]\033[1;34m {request.path}\033[0m\n")
            width = terminal_width()
            total_time = 0.0

            for query in g.queries:
                nice_sql = query['sql'].replace('"', '').replace(',', ', ')
                sql = f"\033[1;31m[{query['time']}]\033[0m {nice_sql}"
                total_time += float(query['time'])

                while len(sql) > width - indentation:
                    print(f"{' ' * indentation}{sql[:width - indentation]}")
                    sql = sql[width - indentation:]
                print(f"{' ' * indentation}{sql}\n")

            print(f"{' ' * indentation}\033[1;32m[TOTAL TIME: {total_time} seconds]\033[0m")
            print(f"{' ' * indentation}\033[1;32m[TOTAL QUERIES: {len(g.queries)}]\033[0m")

        return response
