import time
from fastapi import HTTPException, Request


class RateLimiterMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        The __call__ function is a special function that allows an object to be called like a function.
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.

        :param cls: Refer to the class itself, and is used in a similar way to self
        :param *args: Get a tuple of arguments, and **kwargs is used to get a dictionary of keyword arguments
        :param **kwargs: Pass a variable number of keyword arguments to a function
        :return: The instance of the class
        :doc-author: Trelent
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class RateLimiter(metaclass=RateLimiterMeta):
    def __init__(self, max_requests, window_time):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance variables that will be used by other methods in this class.


        :param self: Represent the instance of the class
        :param max_requests: Set the maximum number of requests that can be made in a given time frame
        :param window_time: Set the time window for which we want to check if a request has been made
        :return: An instance of the class
        :doc-author: Trelent
        """
        self.requests = {}
        self.max_requests = max_requests
        self.window_time = window_time

    def is_allowed(self, client_id):
        """
        The is_allowed function takes in a client_id and returns True if the client is allowed to make another request,
        and False otherwise. The function keeps track of how many requests each client has made within a window of time.
        If the number of requests exceeds max_requests within that window, then the function will return False for that
        client until enough time has passed.

        :param self: Allow an instance of the class to access its own attributes and methods
        :param client_id: Identify the client making the request
        :return: True or false
        :doc-author: Trelent
        """
        current_time = time.time()
        request_info = self.requests.get(client_id)

        if request_info is None:
            self.requests[client_id] = [current_time, 1]
            return True

        last_request_time, request_count = request_info

        if current_time - last_request_time > self.window_time:
            self.requests[client_id] = [current_time, 1]
            return True

        if request_count < self.max_requests:
            self.requests[client_id][1] += 1
            return True

        return False


rate_limiter = RateLimiter(3, 120)


def limit_allowed(request: Request) -> bool:
    """
    The limit_allowed function is a rate limiter that limits the number of requests per client.
        It uses the RateLimiter class to accomplish this task. The function takes in a request object,
        and returns True if the client has not exceeded their limit, or raises an HTTPException with
        status code 429 (Too Many Requests) if they have.

    :param request: Request: Get the client id from the request
    :return: True or raises an httpexception
    :doc-author: Trelent
    """
    global rate_limiter
    # print(id(rate_limiter))
    # print(rate_limiter.requests)
    client_id = request.client
    if rate_limiter.is_allowed(client_id):
        return True
    else:
        raise HTTPException(status_code=429, detail="Too Many Requests")
