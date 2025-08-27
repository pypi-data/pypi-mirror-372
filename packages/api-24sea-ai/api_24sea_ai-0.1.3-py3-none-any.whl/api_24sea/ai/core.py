# -*- coding: utf-8 -*-
"""The api module for the api_24sea.ai subpackage"""
# Standard library imports
import datetime
import logging
from typing import Any, Dict, List, Optional, Union
from warnings import simplefilter

# Third-party imports
import httpx
import pandas as pd

# API-24SEA imports
from api_24sea import exceptions as E
from api_24sea import utils as U
from api_24sea.abc import AuthABC
from api_24sea.datasignals.core import to_star_schema

# Local imports
from . import schemas as S
from . import utils as AIU

# This filter is used to ignore the PerformanceWarning that is raised when
# the DataFrame is modified in place. This is the case when we add columns
# to the DataFrame in the get_data method.
# This is the only way to update the DataFrame in place when using accessors
# and performance is not an issue in this case.
# See https://stackoverflow.com/a/76306267/7169710 for reference.
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

logging.basicConfig(format="%(message)s", level=logging.WARNING)


class _APIMixin(AuthABC):
    """Accessor for working with ai models from the 24SEA API."""

    def __init__(self):
        super().__init__()
        self._models_overview: Optional[pd.DataFrame] = (
            self._permissions_overview
        )
        self.base_url: str = f"{self.base_url}ai/"
        self._selected_models: Optional[pd.DataFrame] = None

    @property
    def authenticated(self) -> bool:
        """Whether the client is authenticated"""
        return self._authenticated

    @property
    @U.require_auth
    def models_overview(self) -> pd.DataFrame:
        """Get the models overview DataFrame."""
        if self._models_overview is None:
            raise E.ProfileError(
                "\033[31mThe models overview is empty. "
                "Please authenticate first with the "
                "\033[1mauthenticate\033[22m method."
            )
        return self._models_overview

    @U.validate_call(config=dict(arbitrary_types_allowed=True))
    def authenticate(
        self,
        username: str,
        password: str,
        permissions_overview: Optional[pd.DataFrame] = None,
    ):
        """Authenticate with username/password"""
        self._username = username
        self._password = password
        self._models_overview = (
            permissions_overview
            if permissions_overview is not None
            else self._models_overview
        )
        self._auth = httpx.BasicAuth(self._username, self._password)

        try:
            r_profile = U.handle_request(
                f"{self.base_url}profile/",
                {"username": self._username},
                self._auth,
                {"accept": "application/json"},
            )
            if (
                r_profile.status_code == 200
                or self._models_overview is not None
            ):  # noqa: E501
                self._authenticated = True
            # fmt: off
            logging.info(f"\033[32;1m{username} has access to "
                         f"\033[4m{U.BASE_URL}.\033[0m")
            # fmt: on
        except httpx.HTTPError:
            raise E.AuthenticationError(
                "\033[31;1mThe username and/or password are incorrect.\033[0m"
            )

        if self._models_overview is not None:
            return self

        logging.info("Now getting your models_overview table...")
        r_models = U.handle_request(
            f"{self.base_url}models/",
            {"project": None, "locations": None, "models": None},
            self._auth,
            {"accept": "application/json"},
        )
        r_model_json = r_models.json()
        try:
            S.ModelsOverviewDjangoResponseSchema.validate(r_model_json)
        except Exception as exc:
            raise exc
            # raise E.ProfileError(
            # "\033[31;1mThe models overview is not valid according to "
            # "the ModelsOverviewDjangoResponseSchema.\033[0m"
            # ) from exc
        # fmt: off
        self._models_overview = AIU.process_models_overview(r_model_json)
        if self._models_overview.empty:
            raise E.ProfileError(f"\033[31;1mThe models overview is empty. This is your profile information:"  # noqa: E501  # pylint: disable=C0301
                                f"\n {r_profile.json()}")
        return self
        # fmt: on

    @U.require_auth
    @U.validate_call
    def get_models(
        self,
        site: Optional[str] = None,
        locations: Optional[Union[str, List[str]]] = None,
        models: Optional[Union[str, List[str]]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Get the models names for a site, provided the following parameters.

        Parameters
        ----------
        site : Optional[str]
            The site name. If None, the queryable models for all sites
            will be returned, and the locations and models parameters will be
            ignored.
        locations : Optional[Union[str, List[str]]]
            The locations for which to get the models. If None, all locations
            will be considered.
        models : Optional[Union[str, List[str]]]
            The models to get. They can be specified as regular expressions.
            If None, all models will be considered.

            For example:

            * | ``models=["^ACC", "^DEM"]`` will return all the models that
              | start with ACC or DEM,
            * Similarly, ``models=["windspeed$", "winddirection$"]`` will
              | return all the models that end with windspeed and
              | winddirection,
            * and ``models=[".*WF_A01.*",".*WF_A02.*"]`` will return all
              | models that contain WF_A01 or WF_A02.

        Returns
        -------
        Optional[pd.DataFrame]
            The models names for the given site, locations and models.

        .. note::
            This class method is legacy because it does not add functionality to
            the DataSignals pandas accessor.

        """
        if (
            site is None and locations is None and models is None
        ):  # Return the models overview if all parameters are None
            return self.models_overview
        url = f"{self.base_url}models/"
        if headers is None:
            headers = {"accept": "application/json"}
        if site is None:
            params = {}
        if isinstance(locations, List):
            locations = ",".join(locations)
        if isinstance(models, List):
            models = ",".join(models)
        params = {
            "project": site,
            "locations": locations,
            "models": models,
        }

        r_ = U.handle_request(url, params, self._auth, headers)

        # Set the return type of the get_models method to the models schema
        return AIU.process_models_overview(r_.json())


class AsyncAPI(_APIMixin):
    """Async version of the API class. Get model predictions from 24sea API /ai
    asyncronously"""

    def __init__(self):
        super().__init__()

    @U.require_auth
    def selected_models(self, data: pd.DataFrame) -> pd.DataFrame:
        """Return the selected models for the query."""
        if self._models_overview is None:
            raise E.ProfileError(
                "\033[31mThe models overview is empty. Please authenticate "
                "first with the \033[1mauthenticate\033[22m method."
            )
        if data.empty:
            raise E.DataSignalsError(
                "\033[31mThe \033[1mselected_models\033[22m method can only "
                "be called if the DataFrame is not empty, or after the "
                "\033[1mget_data\033[22m method has been called."
            )
        # Get the selected models as the Data columns that are available
        # in the models_overview DataFrame
        return self._models_overview[
            self._models_overview["model"].isin(data.columns)
        ].set_index("model")

    @U.require_auth
    @U.validate_call(config=dict(arbitrary_types_allowed=True))
    async def get_predictions(  # type: ignore[override]
        self,
        sites: Optional[Union[List, str]],
        locations: Optional[Union[List, str]],
        models: Union[List, str],
        start_timestamp: Union[str, datetime.datetime],
        end_timestamp: Union[str, datetime.datetime],
        as_dict: bool = False,
        as_star_schema: bool = False,
        outer_join_on_timestamp: bool = True,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[pd.DataFrame] = None,
        max_retries: int = 5,
        timeout: int = 1800,
    ) -> Optional[
        Union[
            pd.DataFrame,
            Dict[str, Union[Dict[str, pd.DataFrame], Dict[str, Any]]],
            List[Union[Any, str]],
        ]
    ]:
        """
        Get the data signals from the 24SEA API asynchronously.
        """
        if data is None:
            data = pd.DataFrame()
        data_ = pd.DataFrame()
        query = S.AIPredictionsInputSchema(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            sites=sites,
            locations=locations,
            models=models,
            headers=headers,
            outer_join_on_timestamp=outer_join_on_timestamp,
            as_dict=as_dict,
            as_star_schema=as_star_schema,
        )

        if self.models_overview is None:
            raise E.ProfileError(
                "\033[31mThe models overview is empty. Please authenticate "
                "first with the \033[1mauthenticate\033[22m method."
            )
        self._selected_models = query.get_selected_models(self.models_overview)
        grouped_models = query.group_models(self.models_overview)

        # Split tasks into chunks of 5 to avoid firing tens of requests together

        # fmt: off
        tasks = [U.fetch_data_async(f"{self.base_url}models/predict",
                                    site, location,
                                    query.start_timestamp, query.end_timestamp,
                                    query.headers, group, self._auth, timeout,
                                    max_retries, target="model")
                 for (site, location), group in grouped_models]
        chunk_size_dict = U.estimate_chunk_size(
            tasks,
            query.start_timestamp,   # type: ignore
            query.end_timestamp,     # type: ignore
            grouped_models,
            self._selected_models,
            target="model"
        )
        # fmt: on
        data_frames = []
        data_frames = await U.gather_in_chunks(
            tasks, chunk_size=chunk_size_dict["chunk_size"], timeout=timeout  # type: ignore  # pylint: disable=C0301  # noqa:E501
        )

        if outer_join_on_timestamp:
            for i, df in enumerate(data_frames):
                if df.empty:
                    continue
                df = df.set_index("timestamp")
                for col in ["site", "location"]:
                    if col in df.columns:
                        df.drop(col, axis=1, inplace=True)
                data_frames[i] = df
            data_ = pd.concat([data_] + data_frames, axis=1, join="outer")
        else:
            data_ = pd.concat([data_] + data_frames, ignore_index=True)

        if all(
            getattr(r, "status_code", 200) == 200
            for r in data_frames
            if hasattr(r, "status_code")
        ):
            logging.info("\033[32;1m✔️ Data successfully retrieved.\033[0m")
        else:
            # If any response is not 200, return the response text(s)
            return [
                getattr(r, "text", "")
                for r in data_frames
                if hasattr(r, "status_code") and r.status_code != 200
            ]
        data.drop(data.index, inplace=True)
        for col in data_.columns:
            if col in data.columns:
                del data[col]
            data[col] = data_[col]
        if as_dict:
            if as_star_schema:
                logging.info(
                    "\033[32;1m\n⏳ Converting queried data to \033[30;1mstar schema\033[0m..."
                )
                return to_star_schema(
                    data,
                    self._selected_models.reset_index(drop=True),
                    as_dict=True,
                )
            return data.reset_index().to_dict("records")
        if as_star_schema:
            logging.info(
                "\033[32;1m\n⏳ Converting queried data to \033[30;1mstar schema\033[0m..."
            )
            return to_star_schema(
                data, self._selected_models.reset_index(drop=True)
            )
        return U.parse_timestamp(data) if not data.empty else data
