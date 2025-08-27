#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Basic client for AiHorde
# Authors:
#  * blueturtleai <https://github.com/blueturtleai> Original Code
#  * Igor Támara <https://github.com/ikks>
#
# MIT lICENSE
#
# https://github.com/ikks/aihorde-client/blob/main/LICENSE

from datetime import date, datetime
from pathlib import Path
from time import sleep
from typing import Any, Dict, List, Tuple, Union
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

import abc
import asyncio
import base64
import contextvars
import functools
import json
import locale
import logging
import math
import gettext
import os
import ssl
import sys
import tempfile
import time
import traceback

_ = gettext.gettext

API_ROOT = "https://aihorde.net/api/v2/"
"""
Base URL for AIHorde API
"""

REGISTER_AI_HORDE_URL = "https://aihorde.net/register"
"""
Url to get an API Key from AI Horde
"""
ANONYMOUS_KEY = "0000000000"

# check between 8 and 15 seconds
CHECK_WAIT = 8
"""
Minimum wait time to check if the image has been generated in seconds
"""

MAX_TIME_REFRESH = 15
"""
Checking for an image generation will be at most in seconds
"""

DEFAULT_MODEL = "stable_diffusion"
"""
Model that is always present for image generation
"""

MIN_WIDTH = 64
"""
Minimum size for the image width, it's recommended to start from 384, most of the
models are trained from 512px
"""
MAX_WIDTH = 3_072
"""
Maximum size for the image width, most of the models are trained at 512px
"""

MIN_HEIGHT = 64
"""
Minimum size for the image height, it's recommended to start from 384, most of the
models are trained from 512px
"""

MAX_HEIGHT = 3_072
"""
Maximum size for the image width, most of the models are trained at 512px
"""

MIN_PROMPT_LENGTH = 10
"""
We aim to get intention from the user to generate an image, this is the minimum of
characters that we request for the prompt    
"""

MAX_MP = 4_194_304  # 2_048 * 2_048 this is 4MP
"""
At most the user should request an image of 4MP
"""

MODELS = [
    "majicMIX realistic",
    "NatViS",
    "noobEvo",
    "Nova Anime XL",
    "Nova Furry Pony",
    "NTR MIX IL-Noob XL",
    "Pony Diffusion XL",
    "Pony Realism",
    "Prefect Pony",
    "Realistic Vision",
    "SDXL 1.0",
    "Stable Cascade 1.0",
    "stable_diffusion",
]
"""
Initial list of models, new ones are downloaded from AiHorde API
"""

INPAINT_MODELS = [
    "A-Zovya RPG Inpainting",
    "Anything Diffusion Inpainting",
    "Epic Diffusion Inpainting",
    "iCoMix Inpainting",
    "Realistic Vision Inpainting",
    "stable_diffusion_inpainting",
]
"""
Initial list of inpainting models, new ones are downloaded from AiHorde API
"""

MESSAGE_PROCESS_INTERRUPTED = "Process interrupted"
"""
Allows to identify when the client received a cancellation
"""

__HORDE_CLIENT_NAME__ = "AiHordeForGimp"
"""
Default Gimp Client.  Was the first to use this client
"""


def log_exception(information):
    """
    Logs an exception including line number
    """
    dnow = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ln = information.__traceback__.tb_lineno
    logging.error(f"[{ dnow }]{ln}: { str(information) }")
    logging.error(
        "".join(
            traceback.format_exception(None, information, information.__traceback__)
        )
    )


class IdentifiedError(Exception):
    """
    Exception for identified problems with an URL

    message: explanation of the error
    url: Resource to understand and fix the problem
    """

    def __init__(self, message: str = "A custom error occurred", url: str = ""):
        self.message: str = message
        self.url: str = url
        super().__init__(self.message)

    def __str__(self):
        return self.message


class InformerFrontend(metaclass=abc.ABCMeta):
    """
    Implementing this interface for an application frontend gives
    AIHordeClient a way to inform progress.  It's expected that
    AIHordeClient receives as parameter an instance of this Interface
    to be able to send messages and updates to the user.
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "show_message")
            and callable(subclass.show_message)
            and hasattr(subclass, "show_error")
            and callable(subclass.show_error)
            and hasattr(subclass, "just_asked_for_update")
            and callable(subclass.just_asked_for_update)
            and hasattr(subclass, "has_asked_for_update")
            and callable(subclass.has_asked_for_update)
            and hasattr(subclass, "update_status")
            and callable(subclass.update_status)
            and hasattr(subclass, "set_finished")
            and callable(subclass.set_finished)
            and hasattr(subclass, "path_store_directory")
            and callable(subclass.path_store_directory)
            or NotImplemented
        )

    def __init__(self):
        self.generated_url = None

    @abc.abstractclassmethod
    def show_message(
        self, message: str, url: str = "", title: str = "", buttons: int = 0
    ):
        """
        Shows an informative message dialog
        if url is given, shows OK, Cancel, when the user presses OK, opens the URL in the
        browser
        title is the title of the dialog to be shown
        buttons are the options that the user can have
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def show_error(self, message, url="", title="", buttons=0):
        """
        Shows an error message dialog
        if url is given, shows OK, Cancel, when the user presses OK, opens the URL in the
        browser
        title is the title of the dialog to be shown
        buttons are the options that the user can have
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def has_asked_for_update(self) -> bool:
        """
        Informs if there has been asked for update
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def just_asked_for_update(self) -> None:
        """
        The update has been just asked
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def update_status(self, text: str, progress: float = 0.0):
        """
        Updates the status to the frontend and the progress from 0 to 100
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def set_finished(self):
        """
        Tells the frontend that the process has finished successfully
        """
        raise NotImplementedError

    @abc.abstractclassmethod
    def path_store_directory(self) -> str:
        """
        Returns the basepath for the directory offered by the frontend
        to store data for the plugin, cache and user settings
        """
        raise NotImplementedError

    def set_generated_image_url_status(self, url: str, valid_to: int) -> None:
        """
        Expected to be invoked from AiHordeClient to store the

        url: of the image being generated and the timestamp for validity and
        valid_to: the time when the image is expected to be generated in seconds.
        """
        self.generated_url = url
        # The images will be generated at most in ten minutes, else the
        # process is cancelled in the server
        self.valid_until = datetime.now().timestamp() + min(valid_to, 600)

    def get_generated_image_url_status(self) -> Union[Tuple[str, int, str], None]:
        """
        Expected to be invoked by the UI to fetch information for an
        image that possibly has been started to being generated,

        Returns:
        None if there is no generation information, else returns

        the URL
        approximate checktime to be reviewed as a timestamp
        text telling the URL and the expected time to be generated
        """
        if not self.generated_url:
            return None

        return (
            self.generated_url,
            self.valid_until,
            _("Please visit\n  {}\nat around {} to fetch your generated images").format(
                self.generated_url,
                datetime.fromtimestamp(self.valid_until).strftime(
                    "%H:%M:%S (%Y-%m-%d)"
                ),
            ),
        )


class AiHordeClient:
    """
    Interaction with AI Horde platform, currently supports:
    * Fetching the most used models in the month
    * Reviewing the credits of an api_key
    * Requesting an image async and go all the way down until getting the image
    * Checking if there is a newer version of the frontend client

    Attributes:

    settings: configured in the constructor and later updated
    """

    # check model updates
    MAX_DAYS_MODEL_UPDATE = 5
    """
    We check at least this number of days for new models
    """

    MAX_MODELS_LIST = 50
    """
    Max Number of models to be presented to the user
    """

    CHECK_WAIT = 5
    """
    Number of seconds to wait before checking again if the image is generated
    """

    MAX_TIME_REFRESH = 15
    """
    If we are in a queue waiting, this is the max time in seconds before asking
    if we are still in queue
    """

    MODEL_REQUIREMENTS_URL = "https://raw.githubusercontent.com/Haidra-Org/AI-Horde-image-model-reference/refs/heads/main/stable_diffusion.json"
    """
    URL of model requirements, the information is injected in the payload to have defaults and avoid warnings
    """

    def __init__(
        self,
        client_version: str,
        url_version_update: str,
        client_help_url: str,
        client_download_url: str,
        settings: json = None,
        client_name: str = __HORDE_CLIENT_NAME__,
        informer: InformerFrontend = None,
    ):
        """
        Creates an AI Horde client with the given settings, if None, the API_KEY is
        set to ANONYMOUS_KEY, the name to identify the client to AI Horde and
        a reference of an object that allows the client to send messages to the
        user.
        """
        if informer is None or not isinstance(informer, InformerFrontend):
            raise IdentifiedError("You must instatiate an informer")
        if settings is None:
            self.settings = {"api_key": ANONYMOUS_KEY}
        else:
            self.settings: json = settings

        if "max_wait_minutes" not in self.settings:
            self.settings["max_wait_minutes"] = 1

        self.client_version: str = client_version

        # When the async request is succesfull, we store the status_url to download
        # later if there is a problem
        self.status_url: str = ""
        self.wait_time: int = 1000

        self.url_version_update: str = url_version_update
        self.client_help_url: str = client_help_url
        self.client_download_url: str = client_download_url

        self.api_key: str = self.settings["api_key"]
        self.client_name: str = client_name
        self.headers: json = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apikey": self.api_key,
            "Client-Agent": self.client_name,
        }
        self.informer: InformerFrontend = informer
        self.progress: float = 0.0
        self.progress_text: str = _("Starting...")
        self.warnings: List[Dict[str, Any]] = []

        # Sync informer and async request
        self.finished_task: bool = True
        self.censored: bool = False
        self.max_time = datetime.now().timestamp() + (
            60 * self.settings["max_wait_minutes"]
        )
        self.factor = 5 / (3.0 * settings["max_wait_minutes"])
        dt = self.headers.copy()
        del dt["apikey"]
        # Beware, not logging the api_key
        logging.debug(dt)

        self._should_stop = False
        self.process_interrupted = False

    def __url_open__(
        self,
        url: Union[str, Request],
        timeout: float = 10,
        refresh_each: float = 0.5,
        only_read=False,
    ) -> None:
        """
        Opens a url request async with standard urllib, taking into account
        timeout informs `refresh_each` seconds.

        Fallsback to no async if running on older python version

        * url to open, can be a request
        * timeout how long to wait before raising a TimeoutError
        * refresh_each the time in seconds(can be non integer greater than 0)
        to tick

        Uses self.finished_task
        Invokes self.__inform_progress__()
        Stores the result in self.response_data
        """

        def windowspython_nossl():
            # https://github.com/ikks/gimp-stable-diffusion/issues/1
            context = ssl._create_unverified_context()
            if only_read:
                with urlopen(url, timeout=timeout, context=context) as response:
                    logging.debug("windows working")
                    self.response_data = response.read()
            else:
                with urlopen(url, timeout=timeout, context=context) as response:
                    logging.debug("Data arrived")
                    self.response_data = json.loads(response.read().decode("utf-8"))

        def real_url_open():
            if isinstance(url, Request):
                logging.debug(f"starting request {url.full_url}")
            else:
                logging.debug(f"starting request {url}")
            try:
                if os.name == "nt" and self.client_name == "AiHordeForGimp":
                    windowspython_nossl()
                else:
                    with urlopen(url, timeout=timeout) as response:
                        if isinstance(url, Request):
                            logging.debug(f"Data arrived from {url.full_url}")
                        else:
                            logging.debug(f"Data arrived from {url}")
                        if only_read:
                            self.response_data = response.read()
                        else:
                            self.response_data = json.loads(
                                response.read().decode("utf-8")
                            )
            except Exception as ex:
                log_exception(ex)
                self.timeout = ex

            self.finished_task = True

        async def counter(until: int = 10) -> None:
            now = time.perf_counter()
            initial = now
            for i in range(0, until):
                if self._should_stop:
                    self.process_interrupted = True
                    logging.debug("Interrupted")
                    break
                if self.finished_task:
                    if isinstance(url, Request):
                        logging.debug(f"{url.full_url} took {now - initial}")
                    else:
                        logging.debug(f"{url} took {now - initial}")
                    break
                await asyncio.sleep(refresh_each)
                now = time.perf_counter()
                self.__inform_progress__()

        async def requester_with_counter() -> None:
            the_counter = asyncio.create_task(counter(int(timeout / refresh_each)))
            await asyncio.to_thread(real_url_open)
            await the_counter
            logging.debug("finished request")

        async def local_to_thread(func, /, *args, **kwargs):
            """
            python3.8 version does not have to_thread
            https://stackoverflow.com/a/69165563/107107
            """
            loop = asyncio.get_running_loop()
            ctx = contextvars.copy_context()
            func_call = functools.partial(ctx.run, func, *args, **kwargs)
            return await loop.run_in_executor(None, func_call)

        async def local_requester_with_counter():
            """
            Auxiliary function to add support for python3.8 missing
            asyncio.to_thread
            """
            task = asyncio.create_task(counter(int(timeout / refresh_each)))
            await local_to_thread(real_url_open)
            self.finished_task = True
            await task

        if self.process_interrupted:
            raise IdentifiedError(MESSAGE_PROCESS_INTERRUPTED)

        self.finished_task = False
        running_python_version = [int(i) for i in sys.version.split()[0].split(".")]
        self.timeout = False
        self.response_data = None
        if running_python_version >= [3, 9]:
            asyncio.run(requester_with_counter())
        elif running_python_version >= [3, 7]:
            ## python3.7 introduced create_task
            # https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task
            asyncio.run(local_requester_with_counter())
        else:
            # Falling back to urllib, user experience will be uglier
            # when waiting...
            try:
                if self._should_stop:
                    self.process_interrupted = True
                    self.finished_task = True
                    logging.debug("Interrupted")
                    return
                if os.name == "nt" and self.client_name == "AiHordeForGimp":
                    windowspython_nossl()
                else:
                    with urlopen(url, timeout=timeout) as response:
                        logging.debug(f"Data arrived from {url}")
                        if only_read:
                            self.response_data = response.read()
                        else:
                            self.response_data = json.loads(
                                response.read().decode("utf-8")
                            )
            except Exception as ex:
                log_exception(ex)
                self.timeout = ex
            self.finished_task = True

        if self.process_interrupted:
            raise IdentifiedError(MESSAGE_PROCESS_INTERRUPTED)

        if self.timeout:
            raise self.timeout

    def __update_models_requirements__(self) -> None:
        """
        Downloads model requirements.
        Usually it is a value to be updated, taking the lowest possible value.
        Add range when min and/or max are present as prefix of an attribute,
        the range is stored under the same name of the prefix attribute
        replaced.

        For example min_steps  and max_steps become range_steps
        max_cfg_scale becomes range_cfg_scale.

        Modifies self.settings["local_settings"]["requirements"]
        """
        # download json
        # filter the models that have requirements rules, store
        # the rules processed to be used later easily.
        # Store fixed value and range when possible
        # clip_skip
        # cfg_scale
        #
        # min_steps max_steps
        # min_cfg_scale max_cfg_scale
        # max_cfg_scale can be alone
        # [samplers]   -> can be single
        # [schedulers] -> can be single
        #

        if "local_settings" not in self.settings:
            return

        logging.debug("Getting requirements for models")
        url = self.MODEL_REQUIREMENTS_URL
        self.progress_text = _("Updating model requirements...")
        self.__url_open__(url)
        model_information = self.response_data
        req_info = {}

        for model, reqs in model_information.items():
            if "requirements" not in reqs:
                continue
            req_info[model] = {}
            # Model with requirement
            settings_range = {}
            for name, val in reqs["requirements"].items():
                # extract range where possible
                if name.startswith("max_"):
                    name_req = "range_" + name[4:]
                    if name_req in settings_range:
                        settings_range[name_req][1] = val
                    else:
                        settings_range[name_req] = [0, val]
                elif name.startswith("min_"):
                    name_req = "range_" + name[4:]
                    if name_req in settings_range:
                        settings_range[name_req][0] = val
                    else:
                        settings_range[name_req] = [val, val]
                else:
                    req_info[model][name] = val

            for name, range_vals in settings_range.items():
                if range_vals[0] == range_vals[1]:
                    req_info[model][name[6:]] = range_vals[0]
                else:
                    req_info[model][name] = range_vals

        logging.debug(f"We have requirements for {len(req_info)} models")

        if "requirements" not in self.settings["local_settings"]:
            logging.debug("Creating requirements in local_settings")
            self.settings["local_settings"]["requirements"] = req_info
        else:
            logging.debug("Updating requirements in local_settings")
            self.settings["local_settings"]["requirements"].update(req_info)

    def __get_model_requirements__(self, model: str) -> json:
        """
        Given the name of a model, fetch the requirements if any,
        to have the opportunity to mix the requirements for the
        model.

        Replaces values that must be fixed and if a value is out
        of range replaces by the min possible value of the range,
        if it was a list of possible values like schedulers, the
        key is replaced by scheduler_name and is enforced to have
        a valid value, if it resulted that was a wrong value,
        takes the first available option.

        Intended to set defaults for the model with the requirements
        present in self.MODEL_REQUIREMENTS_URL json

        The json return has keys with range_ or configuration requirements
        such as steps, cfg_scale, clip_skip, name of a sampler or a scheduler.
        """
        reqs = {}
        if not self.settings or "local_settings" not in self.settings:
            logging.debug("Too brand new... ")
            self.settings["local_settings"] = {}
        if "requirements" not in self.settings["local_settings"]:
            text_doing = self.progress_text
            self.__update_models_requirements__()
            self.progress_text = text_doing

        settings = self.settings["local_settings"]["requirements"].get(model, {})

        if not settings:
            logging.debug(f"No requirements for {model}")
            return reqs

        for key, val in settings.items():
            if key.startswith("range_") and (
                key[6:] not in settings
                or (settings[key[6:]] < val[0])
                or (val[1] < settings[key[6:]])
            ):
                reqs[key[6:]] = val[0]
            elif isinstance(val, list):
                key_name = key[:-1] + "_name"
                if key_name not in settings or settings[key_name] not in val:
                    reqs[key_name] = val[0]
            else:
                reqs[key] = val

        logging.debug(f"Requirements for { model } are { reqs }")
        return reqs

    def __get_model_restrictions__(self, model: str) -> json:
        """
        Returns a json that offers for each key a fixed value or
        a range for the requirements present in self.settings["local_settings"].
         * Fixed Value
         * Range

        Most commonly the result is an empty json.

        Intended for UI validation.

        Can offer range for initial min or max values, and also a
        list of strings or fixed values.
        """
        return self.settings.get("requirements", {model: {}}).get(model, {})

    def cancel_process(self):
        """
        Interrupts the process.  The effect is to finish the process with
        an IdentifiedException with MESSAGE_PROCESS_INTERRUPTED
        """
        self._should_stop = True

    def refresh_models(self):
        """
        Refreshes the model list with the MAX_MODELS_LIST more used including
        always stable_diffusion if not specified, we update self.settings to
        store the date when the models were refreshed.

        Informs if there are new models.
        """
        default_models = MODELS
        self.staging = "Refresh models"
        previous_update = self.settings.get(
            "local_settings", {"date_refreshed_models": "2025-07-01"}
        ).get("date_refreshed_models", "2025-07-01")
        today = datetime.now().date()
        days_updated = (
            today - date(*[int(i) for i in previous_update.split("-")])
        ).days
        if days_updated < AiHordeClient.MAX_DAYS_MODEL_UPDATE:
            logging.debug(f"No need to update models {previous_update}")
            return

        logging.debug("time to update models")
        locals = self.settings.get("local_settings", {"models": MODELS})
        locals["date_refreshed_models"] = today.strftime("%Y-%m-%d")

        url = API_ROOT + "stats/img/models?model_state=known"
        self.headers["X-Fields"] = "month"

        self.progress_text = _("Updating Models...")
        self.__inform_progress__()
        try:
            self.__url_open__(url)
            del self.headers["X-Fields"]
        except TimeoutError:
            logging.debug("Failed updating models due to timeout")
            return
        except (HTTPError, URLError):
            message = _(
                "Service failed to get latest models, check your Internet connection"
            )
            self.informer.show_error(message)
            return

        # Select the most popular models
        popular_models = sorted(
            [(key, val) for key, val in self.response_data["month"].items()],
            key=lambda c: c[1],
            reverse=True,
        )
        logging.debug(f"Downloaded {len(popular_models)}")
        if self.settings.get("mode", "") == "MODE_INPAINTING":
            popular_models = [
                (key, val)
                for key, val in popular_models
                if key.lower().count("inpaint") > 0
            ][: AiHordeClient.MAX_MODELS_LIST]
            default_models = INPAINT_MODELS
        else:
            popular_models = [
                (key, val)
                for key, val in popular_models
                if key.lower().count("inpaint") == 0
            ][: AiHordeClient.MAX_MODELS_LIST]

        fetched_models = [model[0] for model in popular_models]
        default_model = self.settings.get("default_model", DEFAULT_MODEL)
        if default_model not in fetched_models:
            fetched_models.append(default_model)
        if len(fetched_models) > 3:
            compare = set(fetched_models)
            new_models = compare.difference(locals.get("models", default_models))
            if new_models:
                logging.debug(f"New models {len(new_models)}")
                locals["models"] = sorted(fetched_models, key=lambda c: c.upper())
                size_models = len(new_models)
                if size_models == 1:
                    message = (
                        _("We have a new model:") + "\n\n * " + next(iter(new_models))
                    )
                else:
                    if size_models > 10:
                        message = (
                            _("We have {} new models, including:").format(size_models)
                            + "\n * "
                            + "\n * ".join(list(new_models)[:10])
                        )
                    else:
                        message = (
                            _("We have {} new models:").format(size_models)
                            + "\n * "
                            + "\n * ".join(list(new_models)[:10])
                        )

                self.informer.show_message(message)

        self.settings["local_settings"] = locals

        self.__update_models_requirements__()
        if "model" in self.settings:
            if self.settings["model"] not in locals["models"]:
                self.settings["model"] = locals["models"][0]
        logging.debug(self.settings["local_settings"])

    def check_update(self) -> str:
        """
        Inform the user regarding a plugin update. Returns "" if the
        installed is the latest one. Else the localized message,
        defaulting to english if there is no locale for the message.
        """
        message = ""

        if self.informer.has_asked_for_update():
            logging.debug(
                "We already checked for a new version during this session",
            )
            return ""
        logging.debug("Checking for update")

        try:
            # Check for updates by fetching version information from a URL
            url = self.url_version_update
            self.__url_open__(url, 15)
            data = self.response_data

            # During this session we will not check for update again
            self.informer.just_asked_for_update()
            local_version = (*(int(i) for i in str(self.client_version).split(".")),)
            if isinstance(data["version"], int):
                # incoming_version has a deprecated format, local is newer
                return ""
            incoming_version = (*(int(i) for i in data["version"].split(".")),)

            if local_version < incoming_version:
                lang = locale.getlocale()[0][:2]
                message = data["message"].get(lang, data["message"]["en"])
        except (HTTPError, URLError):
            message = _(
                "Failed to check for most recent version, check your Internet connection"
            )
        return message

    def get_balance(self) -> str:
        """
        Given an AI Horde token, present in the api_key,
        returns the balance for the account. If happens to be an
        anonymous account, invites to register
        """
        if self.api_key == ANONYMOUS_KEY:
            return _("Register at ") + REGISTER_AI_HORDE_URL
        url = API_ROOT + "find_user"
        request = Request(url, headers=self.headers)
        try:
            self.__url_open__(request, 15)
            data = self.response_data
            logging.debug(data)
        except HTTPError as ex:
            raise (ex)

        return f"\n\nYou have { data['kudos'] } kudos"

    def generate_image(self, options: json) -> [str]:
        """
        options have been prefilled for the selected model
        informer will be acknowledged on the process via show_progress
        Executes the flow to get an image from AI Horde

        1. Invokes endpoint to launch a work for image generation
        2. Reviews the status of the work
        3. Waits until the max_wait_minutes for the generation of
        the image passes or the image is generated
        4. Retrieves the resulting images and returns the local path of
        the downloaded images

        When no success, returns [].  raises exceptions, but tries to
        offer helpful messages.

        Also checks for update of the plugin.

        Downloads the most popular models and reviews the requirements
        to adjust the configuration to avoid warnings of misconfigurations
        outside the requirements.
        """
        images_names = []
        self.stage = "Nothing"
        self.settings.update(options)
        self.api_key = options["api_key"]
        self.headers["apikey"] = self.api_key
        self.check_counter = 1
        self.check_max = (options["max_wait_minutes"] * 60) / AiHordeClient.CHECK_WAIT
        # Id assigned when requesting the generation of an image
        self.id = ""

        # Used for the progressbar.  We depend on the max time the user indicated
        self.max_time = datetime.now().timestamp() + options["max_wait_minutes"] * 60
        self.factor = 5 / (
            3.0 * options["max_wait_minutes"]
        )  # Percentage and minutes 100*ellapsed/(max_wait*60)

        self.progress_text = _("Contacting the Horde...")
        try:
            params = {
                "cfg_scale": float(options["prompt_strength"]),
                "steps": int(options["steps"]),
                "seed": options["seed"],
            }
            restrictions = self.__get_model_requirements__(options["model"])
            params.update(restrictions)

            width = max(options["image_width"], MIN_WIDTH)
            width = min(options["image_width"], MAX_WIDTH)
            height = max(options["image_height"], MIN_HEIGHT)
            height = min(options["image_height"], MAX_HEIGHT)

            if width * height > MAX_MP:
                factor = (width * 1.0) / height
                ratio = math.sqrt(MAX_MP / (width * height))
                if factor < 1.0:
                    width = width * ratio * factor
                    height = height * ratio * factor
                else:
                    height = height * ratio / factor
                    width = width * ratio / factor
                width = int(width)
                height = int(height)

            if width % 64 != 0:
                width = int(width / 64) * 64

            if height % 64 != 0:
                height = int(height / 64) * 64

            params.update({"width": int(width)})
            params.update({"height": int(height)})

            data_to_send = {
                "params": params,
                "prompt": options["prompt"],
                "nsfw": options["nsfw"],
                "censor_nsfw": options["censor_nsfw"],
                "r2": True,
            }

            data_to_send.update({"models": [options["model"]]})

            mode = options.get("mode", "")
            if mode == "MODE_IMG2IMG":
                data_to_send.update({"source_image": options["source_image"]})
                data_to_send.update({"source_processing": "img2img"})
                data_to_send["params"].update(
                    {"denoising_strength": (1 - float(options["init_strength"]))}
                )
                data_to_send["params"].update({"n": options["nimages"]})
            elif mode == "MODE_INPAINTING":
                data_to_send.update({"source_image": options["source_image"]})
                data_to_send.update({"source_processing": "inpainting"})
                data_to_send["params"].update({"n": options["nimages"]})

            dt = data_to_send.copy()
            if "source_image" in dt:
                del dt["source_image"]
                dt["source_image_size"] = len(data_to_send["source_image"])
            logging.debug(dt)

            post_data = json.dumps(data_to_send).encode("utf-8")

            url = f"{ API_ROOT }generate/async"

            request = Request(url, headers=self.headers, data=post_data)
            try:
                self.stage = "Contacting..."
                self.__inform_progress__()
                self.__url_open__(request, 15)
                data = self.response_data
                logging.debug(data)
                if "warnings" in data:
                    self.warnings = data["warnings"]
                text = _("Horde Contacted")
                logging.debug(text + f" {self.check_counter} { self.progress }")
                self.progress_text = text
                self.__inform_progress__()
                self.id = data["id"]
                self.status_url = f"{ API_ROOT }generate/status/{ self.id }"
                self.wait_time = data.get("wait_time", self.wait_time)
            except TimeoutError as ex:
                message = _(
                    "When trying to ask for the image, the Horde was too slow, try again later"
                )
                log_exception(ex)
                raise IdentifiedError(message)
            except HTTPError as ex:
                try:
                    data = ex.read().decode("utf-8")
                    data = json.loads(data)
                    message = data.get("message", str(ex))
                    if data.get("rc", "") == "KudosUpfront":
                        if self.api_key == ANONYMOUS_KEY:
                            message = (
                                _(
                                    f"Register at { REGISTER_AI_HORDE_URL  } and use your key to improve your rate success. Detail:"
                                )
                                + f" { message }."
                            )
                        else:
                            message = (
                                f"{ self.client_help_url } "
                                + _("to learn to earn kudos. Detail:")
                                + f" { message }."
                            )
                except Exception as ex2:
                    log_exception(ex2)
                    message = str(ex)
                logging.debug(message, data)
                if self.api_key == ANONYMOUS_KEY and REGISTER_AI_HORDE_URL in message:
                    self.informer.show_error(f"{ message }", url=REGISTER_AI_HORDE_URL)
                else:
                    self.informer.show_error(f"{ message }")
                return ""
            except URLError as ex:
                log_exception(ex)
                if data:
                    logging.debug(data)
                self.informer.show_error(
                    _("Internet required, chek your connection: ") + f"'{ ex }'."
                )
                return ""
            except Exception as ex:
                log_exception(ex)
                self.informer.show_error(str(ex))
                return ""

            self.__check_if_ready__()
            self.wait_time = 0
            images = self.__get_images__()
            images_names = self.__get_images_filenames__(images)
            self.status_url = ""

        except IdentifiedError as ex:
            if ex.url:
                self.informer.show_error(str(ex), url=ex.url)
            else:
                self.informer.show_error(str(ex))
            return ""
        except Exception as ex:
            log_exception(ex)
            self.informer.show_error(_("Service failed with: ") + f"'{ ex }'.")
            return ""
        finally:
            self.informer.set_finished()
            message = self.check_update()
            if message:
                self.informer.show_message(message, url=self.client_download_url)

        return images_names

    def __inform_progress__(self):
        """
        Reports to informer the progress updating the attribute progress
        with the percentage elapsed time since the job started
        """
        progress = 100 - (int(self.max_time - datetime.now().timestamp()) * self.factor)

        logging.debug(
            f'[{progress:.2f}/{self.settings["max_wait_minutes"] * 60}] {self.progress_text}',
        )

        if self.informer and progress != self.progress:
            self.informer.update_status(self.progress_text, progress)
            self.progress = progress

    def __check_if_ready__(self) -> bool:
        """
        Queries AI horde API to check if the requested image has been generated,
        returns False if is not ready, otherwise True.
        When the time to get an image has been reached raises an Exception, also
        throws exceptions when there are network problems.

        Calls itself until max_time has been reached or the information from the API
        helps to conclude that the time will be longer than user configured.

        self.id holds the ID of the task that generates the image
        * Uses self.response_data
        * Uses self.check_counter
        * Uses self.max_time
        * Queries self.api_key
        """
        url = f"{ API_ROOT }generate/check/{ self.id }"

        self.__url_open__(url)
        data = self.response_data

        logging.debug(data)

        self.check_counter = self.check_counter + 1

        if data["finished"]:
            self.progress_text = _("Downloading generated image...")
            self.__inform_progress__()
            return True

        if data["processing"] == 0:
            if data["queue_position"] == 0:
                text = _("You are first in the queue")
            else:
                text = _("Queue position: ") + str(data["queue_position"])
            logging.debug(f"Wait time {data['wait_time']}")
        elif data["processing"] > 0:
            text = _("Generating...")
            logging.debug(text + f" {self.check_counter} { self.progress }")
        self.progress_text = text

        if self.check_counter < self.check_max:
            if (
                data["processing"] == 0
                and data["wait_time"] + datetime.now().timestamp() > self.max_time
            ):
                # If we are in queue, we will not be served in time
                logging.debug(data)
                self.informer.set_generated_image_url_status(
                    self.status_url, data["wait_time"]
                )
                logging.debug(self.informer.get_generated_image_url_status())
                if self.api_key == ANONYMOUS_KEY:
                    message = (
                        _("Get a free API Key at ")
                        + REGISTER_AI_HORDE_URL
                        + _(
                            ".\n This model takes more time than your current configuration."
                        )
                    )
                    raise IdentifiedError(message, url=REGISTER_AI_HORDE_URL)
                else:
                    message = (
                        _("Please try another model,")
                        + _("{} would take more time than you configured,").format(
                            self.settings["model"]
                        )
                        + _(" or try again later.")
                    )
                    raise IdentifiedError(message, url=self.status_url)

            if data["is_possible"] is True:
                # We still have time to wait, given that the status is processing, we
                # wait between 5 secs and 15 secs to check again
                wait_time = min(
                    max(AiHordeClient.CHECK_WAIT, int(data["wait_time"] / 2)),
                    AiHordeClient.MAX_TIME_REFRESH,
                )
                for i in range(1, wait_time * 2):
                    sleep(0.5)
                    self.__inform_progress__()
                self.__check_if_ready__()
                return False
            else:
                logging.debug(data)
                raise IdentifiedError(
                    _(
                        "There are no workers available with these settings. Please try again later."
                    )
                )
        else:
            if self.api_key == ANONYMOUS_KEY:
                message = (
                    _("Get an Api key for free at ")
                    + REGISTER_AI_HORDE_URL
                    + _(
                        ".\n This model takes more time than your current configuration."
                    )
                )
                raise IdentifiedError(message, url=REGISTER_AI_HORDE_URL)
            else:
                minutes = (self.check_max * AiHordeClient.CHECK_WAIT) / 60
                logging.debug(data)
                if minutes == 1:
                    raise IdentifiedError(
                        _("Probably your image will take one additional minute.")
                        + " "
                        + _("Please try again later.")
                    )
                else:
                    raise IdentifiedError(
                        _(
                            "Probably your image will take {} additional minutes."
                        ).format(minutes)
                        + _("Please try again later.")
                    )
        return False

    def __get_images__(self):
        """
        Returns the image information of a generated image.
        At this stage AI horde has generated the images and it's time
        to download them all.
        """
        self.stage = "Getting images"
        url = f"{ API_ROOT }generate/status/{ self.id }"
        self.progress_text = _("Fetching images...")
        self.__inform_progress__()
        self.__url_open__(url)
        data = self.response_data
        logging.debug(data)
        if len(data["generations"]) == 0:
            return []
        if data["generations"][0]["censored"]:
            image = data["generations"][0]
            message = f'«{ self.settings["prompt"] }»' + _(
                " is censored, try changing the prompt wording"
            )
            logging.error(message)
            logging.error(image["gen_metadata"])
            self.informer.show_error(message, title="warning")
            self.censored = True

        return data["generations"]

    def __get_images_filenames__(self, images: List[Dict[str, Any]]) -> List[str]:
        """
        Downloads the generated images and returns the full path of the
        downloaded images.
        """
        self.stage = "Downloading images"
        logging.debug("Start to download generated images")
        generated_filenames = []
        cont = 1
        nimages = len(images)
        for image in images:
            with tempfile.NamedTemporaryFile(
                "wb+", delete=False, suffix=".webp"
            ) as generated_file:
                if image["img"].startswith("https"):
                    logging.debug(f"Downloading { image['img'] }")
                    if nimages == 1:
                        self.progress_text = _("Downloading result...")
                    else:
                        self.progress_text = (
                            _("Downloading image") + f" { cont }/{ nimages }"
                        )
                    self.__inform_progress__()
                    self.__url_open__(image["img"], only_read=True)
                    bytes = self.response_data
                else:
                    logging.debug(f"Storing embebed image { cont }")
                    bytes = base64.b64decode(image["img"])

                logging.debug(f"Dumping to { generated_file.name }")
                generated_file.write(bytes)
                generated_filenames.append(generated_file.name)
                cont += 1
        if self.warnings:
            message = (
                _(
                    "You may need to reduce your settings or choose another model, or you may have been censored. Horde message"
                )
                + ":\n * "
                + "\n * ".join([i["message"] for i in self.warnings])
            )
            logging.debug(self.warnings)
            self.informer.show_error(message, title="warning")
            self.warnings = []
        self.refresh_models()
        return generated_filenames

    def get_imagename(self) -> str:
        """
        Returns a name and the model for the image, intended to be used as identifier
        To be run after a succesful generation
        """
        if "prompt" not in self.settings:
            return "AIHorde will be invoked and this image will appear"
        return self.settings["prompt"] + " " + self.settings["model"]

    def get_title(self) -> str:
        """
        Returns the prompt and model used and attribution to AIHorde
        Intended to be used as the title to offer the user some information
        """
        if "prompt" not in self.settings:
            return "AIHorde will be invoked and this image will appear"
        return self.settings["prompt"] + _(" generated by ") + "AIHorde"

    def get_tooltip(self) -> str:
        """
        Intended for assistive technologies, returns prompt and model used
        """
        if "prompt" not in self.settings:
            return "AIHorde will be invoked and this image will appear"
        return (
            self.settings["prompt"]
            + _(" with ")
            + self.settings["model"]
            + _(" generated by ")
            + "AIHorde"
        )

    def get_full_description(self) -> str:
        """
        Returns the options used for image_generation
        Useful for reproducibility. Intended to be run after a succesful generation
        """
        if "prompt" not in self.settings:
            return "AIhorde shall be working sometime in the future"

        options = [
            "prompt",
            "model",
            "seed",
            "image_width",
            "image_height",
            "prompt_strength",
            "steps",
            "nsfw",
            "censor_nsfw",
        ]

        result = ["".join((op, " : ", str(self.settings[op]))) for op in options]

        return "\n".join(result)

    def get_settings(self) -> json:
        """
        Returns the stored settings
        """
        return self.settings

    def set_settings(self, settings: json):
        """
        Store the given settings, useful when fetching from a file or updating
        based on user selection.
        """
        self.settings = settings


class HordeClientSettings:
    """
    Store and load settings
    """

    def __init__(self, base_directory: Path = None):
        if base_directory is None:
            base_directory = tempfile.gettempdir()
        self.base_directory = base_directory
        self.settingsfile = "stablehordesettings.json"
        self.file = base_directory / self.settingsfile
        os.makedirs(base_directory, exist_ok=True)

    def load(self) -> json:
        if not os.path.exists(self.file):
            return {"api_key": ANONYMOUS_KEY}
        with open(self.file) as myfile:
            return json.loads(myfile.read())

    def save(self, settings: json):
        with open(self.file, "w") as myfile:
            myfile.write(json.dumps(settings))
        os.chmod(self.file, 0o600)


class ProcedureInformation:
    def __init__(
        self,
        model_choices: List[str],
        action: str,
        cache_key: str,
        default_model: str,
        refreshed_date: str = None,
    ):
        self.model_choices = model_choices
        self.action = action
        self.cache_key = cache_key
        self.default_model = default_model
        if refreshed_date is None:
            self.refreshed_date = "2025-07-01"

    # Load the refreshed, stored as
    def update_choices_from(self, choices: json):
        """
        choices is expected to have an structure like:
        { self.cache_key: {"models": [], "date_refreshed_models": "YYYY-MM-DD"} }

        the choices are updated if the structure is present and there are options present
        """
        logging.debug(f"fetching choices from {self.cache_key}")
        if self.cache_key not in choices or not choices[self.cache_key]["models"]:
            return
        self.model_choices = choices[self.cache_key]["models"]
        self.refreshed_date = choices[self.cache_key]["date_refreshed_models"]

    def update_choices_into(self, new_choices: json, st_manager: HordeClientSettings):
        """
        updates st_manager with new_settings
        updates stored choices with most recent information from st_manager
        """
        if not new_choices:
            return
        logging.debug("storing choices")
        current_choices = st_manager.load()
        if "api_key" in current_choices:
            del current_choices["api_key"]
        current_choices[self.cache_key] = {
            "date_refreshed_models": new_choices["date_refreshed_models"],
            "models": new_choices["models"],
        }
        if "requirements" in new_choices:
            if "requirements" in current_choices:
                current_choices["requirements"].update(new_choices["requirements"])
            else:
                current_choices["requirements"] = new_choices["requirements"]

        logging.debug(current_choices)
        st_manager.save(current_choices)
