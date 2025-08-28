import os
import struct
import fcntl
import termios
from starlette.middleware.base import BaseHTTPMiddleware
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


class SqlPrintingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, debug: bool = True):
        super().__init__(app)
        self.debug = debug

    async def dispatch(self, request, call_next):
        if self.debug:
            request.state.queries = []

            @event.listens_for(Engine, "after_cursor_execute")
            def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                if not hasattr(request.state, 'queries'):
                    request.state.queries = []
                request.state.queries.append({
                    'sql': statement,
                    'time': context.execution_time
                })

        response = await call_next(request)

        if self.debug and hasattr(request.state, 'queries'):
            indentation = 2
            print(f"\n\n{' ' * indentation}\033[1;35m[SQL Queries for]\033[1;34m {request.url.path}\033[0m\n")
            width = terminal_width()
            total_time = 0.0

            for query in request.state.queries:
                nice_sql = query['sql'].replace('"', '').replace(',', ', ')
                sql = f"\033[1;31m[{query['time']}]\033[0m {nice_sql}"
                total_time += float(query['time'])

                while len(sql) > width - indentation:
                    print(f"{' ' * indentation}{sql[:width - indentation]}")
                    sql = sql[width - indentation:]
                print(f"{' ' * indentation}{sql}\n")

            print(f"{' ' * indentation}\033[1;32m[TOTAL TIME: {total_time} seconds]\033[0m")
            print(f"{' ' * indentation}\033[1;32m[TOTAL QUERIES: {len(request.state.queries)}]\033[0m")

        return response
