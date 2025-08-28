###############################################################################
#
# (C) Copyright 2023 EVERYSK TECHNOLOGIES
#
# This is an unpublished work containing confidential and proprietary
# information of EVERYSK TECHNOLOGIES. Disclosure, use, or reproduction
# without authorization of EVERYSK TECHNOLOGIES is prohibited.
#
###############################################################################
from concurrent.futures import ThreadPoolExecutor, Future, wait
from contextvars import Context, copy_context
from typing import Any

from everysk.core.log import Logger
from everysk.core.object import BaseObject


log = Logger(name='everysk-thread-error-log')


###############################################################################
#   Thread Class Implementation
###############################################################################
class Thread(BaseObject):
    ## Private attributes
    _pool: 'ThreadPool' = None

    ## Public attributes
    args: tuple = None
    kwargs: dict = None
    target: callable = None

    def __init__(self, target: callable, args: tuple = (), kwargs: dict = None):
        """
        Use to execute the target inside a Thread and do parallel process.
        This differs from the Python Threads for the capacity to use contextVars
        and return the result.
        AnOther ability

        Args:
            target (callable): The function that will be executed.
            args (tuple, optional): The args attributes to be sent to the function. Defaults to ().
            kwargs (dict, optional): The args attributes to be sent to the function. Defaults to None.

        Example:
            >>> from everysk.core.threads import Thread
            >>> def sum(a, b):
            ...     return a + b
            ...
            >>> thread = Thread(target=sum, args=(1, 2))
            >>> thread.start()
            >>> thread.join()
            3
            >>> thread = Thread(target=sum, kwargs={'a': 1, 'b': 2})
            >>> thread.start()
            >>> thread.join()
            3
        """
        super().__init__(target=target, args=args, kwargs=kwargs)
        if self.kwargs is None:
            self.kwargs = {}

        self._pool = ThreadPool(concurrency=1, silent=True)

    def join(self) -> Any | None:
        """
        Wait for the Thread to finish and returns the result.
        """
        self._pool.wait()
        return self._pool.results[0]

    def run(self) -> Any:
        """
        The method used to run the target inside the Thread.
        """
        self._pool.add(target=self.target, args=self.args, kwargs=self.kwargs)

    def start(self) -> None:
        """
        The method used to start the Thread.
        """
        self.run()


###############################################################################
#   ThreadPool Class Implementation
###############################################################################
class ThreadPool(ThreadPoolExecutor):
    context: Context = None
    default_error_value: Any = Undefined
    futures: list[Future] = None
    results: list = None
    silent: bool = True

    def __init__(self, concurrency: int | None = None, silent: bool = True, default_error_value: Any = Undefined) -> None:
        """
        ThreadPool is a queue to execute threads and control the concurrency.
        If some error occur inside a Thread, we raise the exception or just log the exception.
        If concurrency is not passed, then the default value is min(32, os.cpu_count() + 4).

        Args:
            concurrency (int | None, optional): The number of Threads that will be running simultaneously. Defaults to None.
            silent (bool, optional): To log the error or raise. Defaults to True.
            default_error (Any, optional): The default value to be stored as result if an error occur. Defaults to Undefined.

        Example:

            >>> from time import sleep
            >>> from everysk.core.datetime import DateTime
            >>> from everysk.core.threads import ThreadPool

            >>> def sum(a: int, b: int) -> int:
            ...     print(DateTime.now().strftime('%H:%M:%S'))
            ...     sleep(1)
            ...     return a + b

            >>> pool = ThreadPool(6)
            >>> for i in range(0, 6):
            ...     pool.add(target=sum, args=(i, i))
            >>> pool.wait()
            19:24:22
            19:24:22
            19:24:22
            19:24:22
            19:24:22
            19:24:22
            >>> pool.results
            [0, 2, 4, 6, 8, 10]

            >>> pool = ThreadPool(2)
            >>> for i in range(0, 6):
            ...     pool.add(target=sum, args=(i,i))
            >>> pool.wait()
            19:25:09
            19:25:09
            19:25:10
            19:25:10
            19:25:11
            19:25:11
            >>> pool.results
            [0, 2, 4, 6, 8, 10]
        """
        self.context = copy_context()
        self.futures = []
        self.results = []
        self.silent = silent
        self.default_error_value = default_error_value
        super().__init__(concurrency, initializer=self._set_child_context)

    def _set_child_context(self) -> None:
        """ Used to pass the context values to the child Threads. """
        for var, value in self.context.items():
            var.set(value)

    def add(self, target: callable, args: tuple = (), kwargs: dict = None) -> None:
        """
        Add the target to the queue to be processed later in a Thread.

        Args:
            target (callable): The function that will be executed in the Thread.
            args (tuple, optional): The arguments that are needed to this function. Defaults to ().
            kwargs (dict, optional): The keyword arguments that are needed to this function. Defaults to None.
        """
        if kwargs is None:
            kwargs = {}

        future = self.submit(target, *args, **kwargs)
        # We add these info on the future to be used later if some error occur
        future.target = target
        future.args = args
        future.kwargs = kwargs

        self.futures.append(future)

    def wait(self) -> None:
        """ This method is used to wait for all threads to complete and generate the results. """
        wait(self.futures)

        for future in self.futures:
            try:
                self.results.append(future.result())
            except Exception as error: # pylint: disable=broad-exception-caught
                if self.silent:
                    self.results.append(self.default_error_value)
                    log.error(
                        'Thread execution error -> target: %s',
                        future.target.__name__,
                        extra={
                            'labels': {
                                'args': future.args,
                                'kwargs': future.kwargs,
                            }
                        }
                    )
                else:
                    raise error

        # This is a Garbage Collector for the ThreadPool
        self.shutdown()
