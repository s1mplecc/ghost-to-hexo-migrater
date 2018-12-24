import logging

logging.basicConfig()


def logged(func, *args, **kwargs):
    """sda"""

    logger = logging.getLogger()

    def new_func(*args, **kwargs):
        logger.info(f'call {func.__name__} with args {args} and kwargs {kwargs}.')
        return func(*args, **kwargs)

    return new_func


@logged
def bar(a, b, c='sd'):
    print('bar')


logging.getLogger().setLevel(logging.DEBUG)
