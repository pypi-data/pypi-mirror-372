# Set shebang if needed.
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 16:52:36 2025

@author: mano
"""

import requests as r
import asyncio
import aiohttp
import yarl
import hashlib as h
import queue as q
import time


class SessionManager():
    """
    The session manager, takes care of handling each available session.

    It handles both sessions wether it is an async or sync requests session.
    """

    def __init__(self):
        self.__sessions = {
            'sync': {
                'no-metadata': None,
                'custom-metadata': dict()
            },
            'async': {
                'no-metadata': None,
                'custom-metadata': dict()
            }
        }
        self.__last_session_gathered_time = None
        self.__loop_running = False
        """
        sessions is a private attribute. It is a dict used to manage all the
        sessions that might be needed.

        The structure is such to handle sync and async sessions independently.
            Each has the keys, "no-metadata" and "custom".
                no-metadata key would be a session to manage all requests that
                wont use any
                    cookie,
                    auth,
                    .
                    .
                    .
                while custom is used to handle the sessions that require any of
                the previously commented attributes.

        last_session_gathered_time is an attribute used to store the starting
        time of the last time a session was collected.
            This allows to close the sessions automatically if no requests
            are made.

        loop_running is a bool to check if the loop to close all session
        is up and running.
        """
        return None

    def __add_session__(self, mode, hash_val=None, **aiohttp_session_kwargs):
        """
        Adds a session to the session manager if it is necessary.

        It selects the mode (async or sync, aiohttp or requests) and checks
        if there is a session already active for the specific mode and hash
        value. If it doesn't exist it adds the session, if it exist it does
        nothing.

        The hash value is used to represent the information passed in the
        header.

        aiohttp_session_kwargs are needed for async session since requests
        pacakge session doesn't have initialization params.
        base_url is removed from aiohttp params

        Parameters
        ----------
        mode : str, Literal['sync', 'async']
            The mode of the session, sync or async.
        hash_val : str, optional
            The hash value of the headers data. The default is None.
        **aiohttp_session_kwargs: optional
            The params used to build the session for aiohttp.

        Returns
        -------
        None.

        """
        if mode == 'sync':
            # If hash is None then it is a session where headers are
            # irrelevant
            if hash_val is None:
                # We check if the session already exists
                if self.__sessions[mode]['no-metadata'] is None:
                    self.__sessions[mode]['no-metadata'] = r.Session()
            # In case hash_val is not None, the session is added as one with
            # with custom params
            else:
                try:
                    self.__sessions[mode]['custom-metadata'][hash_val]
                except KeyError:
                    self.__sessions[mode]['custom-metadata'][hash_val] = (
                        r.Session()
                    )  # Between () for multiline, to avoid 79 cols limit.
        elif mode == 'async':
            if hash_val is None:
                if self.__sessions[mode]['no-metadata'] is None:
                    self.__sessions[mode]['no-metadata'] = (
                        aiohttp.ClientSession()
                    )  # Between () for multiline, to avoid 79 cols limit.
            else:
                try:
                    self.__sessions[mode]['custom-metadata'][hash_val]
                except KeyError:
                    kwargs = dict(aiohttp_session_kwargs)
                    # dict() makes a copy, to not interfere on the original.
                    kwargs.pop('base_url', None)
                    # None val prevent the KeyError if base_url is not present.
                    self.__sessions[mode]['custom-metadata'][hash_val] = (
                        aiohttp.ClientSession(**kwargs)
                    )  # Between () for multiline, to avoid 79 cols limit.
        return None

    def __select_session__(self, mode, hash_val=None,
                           **aiohttp_session_kwargs):
        """
        Returns the session of your choice and creats one if it doesn't exists.

        **aiohttp_session_kwargs is used to build the session as specified in
        the add_session method.

        Parameters
        ----------
        mode : str, Literal['sync', 'async']
            The mode of the session, sync or async.
        hash_val : str, optional
            The hash value of the headers data. The default is None.
        **aiohttp_session_kwargs: optional
            The params used to build the session for aiohttp.

        Returns
        -------
        Session
            The session object, wether sync or async.

        """
        self.__add_session__(mode, hash_val, **aiohttp_session_kwargs)
        if hash_val is None:
            return self.__sessions[mode]['no-metadata']
        else:
            return self.__sessions[mode]['custom-metadata'][hash_val]

    def __get_header_data__(self, mode, dictionary):
        """
        Gets the data from the header params of the request and pass it to str.

        Parameters
        ----------
        mode : Literal['sync', 'async']
            Mode of the request, async or sync.
        dictionary : The Kwargs of the request.
            The Keyword arguments of the request.
                - Requests package if sync mode
                - Aiohttp if async mode.

        Returns
        -------
        new_dict : dict
            Header data of request.
            It returns an empty dict if there is no header data.

        """
        request_header_params = [
            'auth',
            'cookies',
            'headers',
        ]
        aiohttp_header_params = [
            'auth',
            'cookies',
            'headers'
        ]
        if mode == 'sync':
            keywords = request_header_params
        elif mode == 'async':
            keywords = aiohttp_header_params

        # We rebuild the dictionary just to have it sorted in order to get the
        # same hash each time.
        new_dict = dict()
        for k in keywords:
            try:
                new_dict[k] = dictionary[k]
            except KeyError:
                continue
        return new_dict

    def __dict_to_str__(self, dictionary):
        """
        Transform a dict to str with specified format.

        Parameters
        ----------
        dictionary : dict
            Dict to pass to string

        Returns
        -------
        dict as str.

        """
        data_str = """"""
        for k, v in dictionary.items():
            if isinstance(v, dict):
                data_str += self.__dict_to_str__(v)
            else:
                data_str += f'{k} {str(v)}'
                # There is no need for clean readable format, since it will
                # be used just to compute the hash.
        return data_str

    def __get_hash_value_of_dict__(self, dictionary):
        """
        Computes the hash value of the passed dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary to get the hash from.

        Returns
        -------
        hash_str : str
            7 first terms of SHA1 of the dictionary.
            Returns None if the dict is empty

        """
        if not bool(dictionary):
            return None
        hasher = h.sha1(usedforsecurity=False)
        hasher.update(self.__dict_to_str__(dictionary))
        hash_str = hasher.hexdigest()
        return hash_str[:7]

    def __get_loop__(self):
        """Returns the event loop, or creats one if does not exist."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop

    def get_session(self, mode, **request_kwargs):
        """
        Gathers a session based on the url, the mode and the params.

        The gathered session will be sync or async based on the mode

        Parameters
        ----------
        mode : str, Literal[sync, async]
            The mode of the session, sync or async
        **request_kwargs : TYPE
            requests.Request kwargs if mode is sync
            aiohttp.Request kwargs if mode is async

        Returns
        -------
        session : requests.Session | aiohttp.Session
            Session of one of the packages requests or aiohttp.

        """
        header_data = self.__get_header_data__(mode, request_kwargs)
        hash_val = self.__get_hash_value_of_dict__(header_data)
        session = self.__select_session__(mode, hash_val)

        """
        We add the last time a session was gathered, and reset the last time
        a session
        """
        self.__last_session_gathered_time = time.time()
        # This function is called when a request will be made.
        # So we start the loop to close the sessions automatically when
        # necessary if it not already running.
        if not self.__loop_running:
            loop = self.__get_loop__()
            loop.create_task(self.__close_all_sessions_loop__())
        return session

    def get_all_sessions(self):
        """Returns the private attribute sessions. The dict with sessions."""
        return self.__sessions

    async def __close_all_sessions_private__(self):
        """Closes all sessions, private because it needs to be async."""
        for mode, data in self.__sessions.items():
            # mode is for sync, async start of the dict
            # data is always a dict
            for meta, data2 in data.items():
                # meta is no-metadata or custom-metadata
                # data2 could be None for no-metadata
                # or a session if it was initiated
                # or a dict for custom-metadata
                # in such case each val of the dict will be a session.
                if data2 is None:
                    continue
                elif isinstance(data2, dict):
                    for hash_val, sess in data2.items():
                        if mode == 'async':
                            await sess.close()
                        else:
                            sess.close()
                        print(f'{hash_val} ({mode}): was_closed.')
                else:
                    if mode == 'async':
                        await data2.close()
                    else:
                        data2.close()
                    print(f'no-metadata ({mode}): was_closed.')
        return None

    def close_all_sessions(self):
        """Closes all sessions."""
        # This function isn't needed, but it is here to close all sessions
        # if the user needs it.
        loop = self.__get_loop__()
        loop.create_task(self.__close_all_sessions_private__())
        return None

    async def __close_all_sessions_loop__(self):
        """Closes all sessions automatically if condition is met."""
        self.__loop_running = True
        while True:
            if self.__last_session_gathered_time is None:
                self.__loop_running = False
                return None
            elif (time.time() - self.__last_session_gathered_time) == 600:
                await self.__close_all_sessions_private__()
                self.__loop_running = True
                return None
            else:
                await asyncio.sleep(600)
        return None


class DomainManager():
    """
    The domain manager handles each of the requested domains.

    It handles their queues.
    """

    def __init__(self, sleep_time: float | int = 0.25):
        self.__domains = dict()
        self.__minimum_sleep_time = sleep_time
        return None

    def __get_host(self, url):
        """
        Gets the host (or domain) of a url.

        Parameters
        ----------
        url : str | yarl.URL
            URL to get the host from

        Returns
        -------
        str
            Host of a url.

        """
        return yarl.URL(url).host

    def __add_domain(self, url):
        """
        Extracts the domain from the url and adds the domain if needed.

        Parameters
        ----------
        url : str | yarl.URL
            A url with a domain.

        Returns
        -------
        None.

        """
        host = self.__get_host(url)
        try:
            self.__domains[host]
        except KeyError:
            self.__domains[host] = {
                'queue': q.Queue(),
                'last_time': 0,
                'lock': asyncio.Lock()
            }
        return None

    def __update_time(self, host: str):
        """Updates the last time a request was made to the host of the url."""
        self.__domains[host]['last_time'] = time.time()
        return None

    def get_sleep_time(self, url: str):
        """
        Reads the last time a domain was asked to and calculates how much
        sleep time is needed to wait till making next request.

        Parameters
        ----------
        url : str
            URL where you will make the request.

        Returns
        -------
        sleep_time : TYPE
            DESCRIPTION.

        """
        host = self.__get_host(url)
        self.__add_domain(url)
        last_time = self.__domains[host]['last_time']
        delta_current = time.time() - last_time
        self.__update_time(host)
        if delta_current > self.__minimum_sleep_time:
            return self.__minimum_sleep_time
        return 0

    def add_url(self, url):
        """
        Adds a url to the proper queue.

        Parameters
        ----------
        url : str | yarl.url
            url to add.

        Returns
        -------
        None.
        """
        host = self.__get_host(url)
        self.__add_domain(url)
        self.__domains[host]['queue'].put(yarl.URL(url), False)
        # we shouldn't get a Full error since there is no limit.
        return None

    def get_url(self, host: str):
        """
        Gets the latest url from the specified host.

        Parameters
        ----------
        host : str
            host of where you want to get the url from.

        Returns
        -------
        yarl.URL
            The first url in the queue. None if it is empty.

        """
        try:
            return self.__domains[host]['queue'].get(False)
        except q.Empty:
            return None

    def get_lock(self, url: str):
        """Sets the host as blocked."""
        host = self.__get_host(url)
        self.__add_domain(url)
        lock = self.__domains[host]['lock']
        return lock



class RequestsManager():
    """
    Request manager handles allows you to make requests and/or schedule them.

    It can be both sync or async.
    """

    def __init__(self,
                 sleep_time: int | float = 0.25,
                 print_url: bool = False
                 ):

        self.__SM = SessionManager()
        self.__DM = DomainManager(sleep_time)

        self.__print_url = print_url
        return None

    def sync_request(self, method, url, **request_kwargs):
        """Makes a request using requests package."""
        if self.__print_url:
            print(url)
        S = self.__SM.get_session('sync', **request_kwargs)
        sleep_time = self.__DM.get_sleep_time(url)
        time.sleep(sleep_time)
        response = S.request(method, url, **request_kwargs)
        return response

    async def async_request(self, method, url, **aiohttp_kwargs):
        """Makes a request async using aiohttp package."""
        lock = self.__DM.get_lock(url)
        async with lock:  # This way the host is blocked until this one finish.
            if self.__print_url:
                print(url)
                S = self.__SM.get_session('async', **aiohttp_kwargs)
                sleep_time = self.__DM.get_sleep_time(url)
                await asyncio.sleep(sleep_time)
                response = await S.request(method, url, **aiohttp_kwargs)
        return response

    def close_all_sessions(self):
        """Closes all sessions."""
        self.__SM.close_all_sessions()
        return None
