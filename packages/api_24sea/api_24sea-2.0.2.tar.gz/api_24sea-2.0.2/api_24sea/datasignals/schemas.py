# -*- coding: utf-8 -*-
"""Data signals types."""
import datetime
import logging
from typing import Dict, List, Optional, Union

import pandas as pd
from pandas.core.groupby import DataFrameGroupBy
from pydantic import PositiveInt

from .. import exceptions as E
from .. import utils as U


# Shared base class for data signal schemas
class BaseDataSignalSchema(U.BaseModel):
    """
    Shared base schema for data signals requests.
    Includes common fields and validation logic for timestamp, sites, locations,
    metrics, and headers. Inherit from this class to create specific schemas for
    data retrieval and stats retrieval.
    """

    start_timestamp: Union[datetime.datetime, str]
    end_timestamp: Union[datetime.datetime, str]
    sites: Optional[Union[str, List[str]]] = None
    locations: Optional[Union[str, List[str]]] = None
    metrics: Union[str, List[str]]
    as_dict: Optional[bool] = False
    as_star_schema: Optional[bool] = False
    headers: Optional[Dict[str, str]] = {"accept": "application/json"}

    @U.field_validator("start_timestamp", "end_timestamp", mode="before")
    def validate_timestamp(cls, v: Union[datetime.datetime, str]) -> str:
        """Validate and format timestamp input."""
        if isinstance(v, str):
            try:
                datetime.datetime.strptime(v, "%Y-%m-%dT%H:%M:%SZ").astimezone(
                    datetime.timezone.utc
                )
            except Exception:
                try:
                    from shorthand_datetime import parse_shorthand_datetime

                    return parse_shorthand_datetime(v).strftime(  # type: ignore
                        "%Y-%m-%dT%H:%M:%SZ"
                    )
                except Exception as exc:
                    raise ValueError(
                        "\033[31mIncorrect start timestamp format, expected "
                        "one of the following formats:"
                        "\n               \033[1m• 'YYYY-MM-DDTHH:MM:SSZ'"
                        "\033[22m, \n               \033[1m• shorthand_datetime"
                        "-compatible string\033[22m "
                        "(https://pypi.org/project/shorthand-datetime/), or, "
                        "\n               "
                        "\033[1m• datetime.datetime\033[22m object.\033[0m\n\n"
                        "Exception originated from\n" + str(exc)
                    )
        if isinstance(v, datetime.datetime):
            return v.strftime("%Y-%m-%dT%H:%M:%SZ")
        return v

    @U.field_validator("sites", "locations", mode="before")
    def validate_sites_locations(cls, v):
        """Validate and format sites and locations input."""
        if isinstance(v, str):
            v = [v]
        if isinstance(v, List):
            v = [str(item).lower() for item in v]
        return v

    @U.field_validator("metrics", mode="before")
    def validate_metrics(cls, v):
        """Validate and format metrics input."""
        if isinstance(v, str):
            v = [v]
        if isinstance(v, List):
            # fmt: off
            v = [item.replace(" ", ".*")
                    #  .replace("_", ".*")
                     .replace("-", ".*") for item in v]
            # fmt: on
        return "|".join(v)

    @U.field_validator("headers", mode="before")
    def validate_headers(cls, v):
        """Validate and format headers input."""
        if v is None:
            return {"accept": "application/json"}
        return v

    @property
    def query_str(self) -> str:
        """Build a query string based on self."""
        return build_query_str(self)

    # @lru_cache
    def get_selected_metrics(
        self, df: Optional[pd.DataFrame], log: bool = True
    ) -> pd.DataFrame:
        """Calculate the selected metrics DataFrame based on a df (metrics
        overview) and the query object."""
        if df is None:
            raise ValueError("The provided DataFrame cannot be None.")
        return get_selected_metrics(self, df, log)

    # @lru_cache
    def group_metrics(self, df: Optional[pd.DataFrame]) -> DataFrameGroupBy:
        """Group metrics by site and location."""
        if df is None:
            raise ValueError("The provided DataFrame cannot be None.")
        s_m = self.get_selected_metrics(df, False)
        if self.metrics in (["all"], "all"):
            # For "all" metrics, create groups more efficiently
            sites_locs = s_m.assign(
                site=lambda x: x["site"].str.lower(),
                location=lambda x: x["location"].str.upper(),
            )[["site", "location"]].drop_duplicates()

            # Create grouped_metrics directly without intermediate steps
            return sites_locs.assign(metric="all").groupby(["site", "location"])
        else:
            # For specific metrics, group directly
            return s_m.assign(
                site=lambda x: x["site"].str.lower(),
                location=lambda x: x["location"].str.upper(),
            ).groupby(["site", "location"])


class GetOldestTimestampSchema(U.BaseModel):
    """
    Schema for oldest timestamp requests.
    """

    site: str  # renamed from 'sites' to match caller
    locations: Optional[Union[str, List[str]]] = None
    headers: Optional[Dict[str, str]] = {"accept": "application/json"}

    @U.field_validator("locations", mode="before")
    def validate_locations(cls, v) -> Optional[str]:
        """Normalize locations to a comma-separated lower-case string."""
        if v is None:
            return v
        if isinstance(v, list):
            return ",".join([str(item).lower() for item in v])
        if isinstance(v, str):
            return v.lower()
        raise TypeError("locations must be a string or list of strings")

    @U.field_validator("site", mode="before")
    def validate_site(cls, v):
        """Normalize site to a lower-case string."""
        if isinstance(v, str):
            return v.lower()
        raise TypeError("site must be a string")

    @U.field_validator("headers", mode="before")
    def validate_headers(cls, v) -> Dict[str, str]:
        if v is None:
            return {"accept": "application/json"}
        if isinstance(v, dict):
            return v
        raise TypeError("headers must be a dictionary")

    @property
    def query_str(self) -> str:
        # fmt: off
        if self.locations is None:
            return ("(site_id.str.lower() == @query.site or "
                    "site.str.lower() == @query.site)")
        return ("(site_id.str.lower() == @query.site or "
                "site.str.lower() == @query.site) "
                "and (location.str.lower() == @query.locations.split(',') or "
                "location_id.str.lower() == @query.locations.split(','))")
        # fmt: on

    def get_selected_locations(
        self, df: Optional[pd.DataFrame]
    ) -> pd.DataFrame:
        """Get the selected locations DataFrame based on the query object."""
        if df is None:
            raise ValueError("The provided DataFrame cannot be None.")
        return get_selected_locations(self, df)


class GetData(BaseDataSignalSchema):
    """
    A pydantic schema for the data signals (data retrieval).
    Includes all common fields plus 'outer_join_on_timestamp' for join behavior.
    """

    outer_join_on_timestamp: bool

    @U.field_validator("outer_join_on_timestamp", mode="before")
    def validate_outer_join_on_timestamp(cls, v):
        if v is None:
            return False
        return v


class GetStats(BaseDataSignalSchema):
    """
    A pydantic schema for the data signals (stats retrieval).
    Inherits all common fields from the base schema.
    """

    # Placeholder for future stats-specific fields or methods
    # Currently, it inherits all common fields from BaseDataSignalSchema
    pass


class GetAvailability(BaseDataSignalSchema):
    """
    A pydantic schema for the data signals (availability retrieval).
    Inherits all common fields from the base schema.
    """

    # Placeholder for future availability-specific fields or methods
    # Currently, it inherits all common fields from BaseDataSignalSchema
    granularity: Union[str, PositiveInt]
    sampling_interval_seconds: Optional[int] = None

    @U.field_validator("granularity", mode="before")
    def validate_granularity(cls, v):
        valid_granularities = ["day", "week", "month", "year"]
        if isinstance(v, str):
            if v not in valid_granularities:
                # fmt: off
                raise ValueError(f"Invalid granularity: {v}. "
                                 f"Must be one of {valid_granularities}.")
                # fmt: on
            return v
        return v

    @U.field_validator("sampling_interval_seconds", mode="before")
    def validate_sampling_interval_seconds(cls, v):
        if v is None:
            return 600
        return v


def build_query_str(query: BaseDataSignalSchema) -> str:
    """
    Build a query string based on the provided BaseDataSignalSchema instance.

    Parameters
    ----------
    query : BaseDataSignalSchema
        The query object containing the filtering criteria.

    Returns
    -------
    str
        The constructed query string.
    """
    if query.sites is None and query.locations is None:
        return "metric.str.contains(@query.metrics, case=False, regex=True)"
    elif query.sites is None and query.locations is not None:
        return (
            "(location.str.lower() == @query.locations or location_id.str.lower() == @query.locations) "
            "and metric.str.contains(@query.metrics, case=False, regex=True)"
        )
    elif query.locations is None and query.sites is not None:
        return (
            "(site.str.lower() == @query.sites or site_id.str.lower() == @query.sites) "
            "and metric.str.contains(@query.metrics, case=False, regex=True)"
        )
    elif (
        query.sites is not None
        and query.locations is not None
        and (query.metrics == ["all"] or query.metrics == "all")
    ):
        return (
            "(site_id.str.lower() == @query.sites or site.str.lower() == @query.sites) "
            "and (location.str.lower() == @query.locations or location_id.str.lower() == @query.locations)"
        )
    else:
        return (
            "(site_id.str.lower() == @query.sites or site.str.lower() == @query.sites) "
            "and (location.str.lower() == @query.locations or location_id.str.lower() == @query.locations) "
            "and metric.str.contains(@query.metrics, case=False, regex=True)"
        )


def get_selected_metrics(
    query: BaseDataSignalSchema,
    metrics_overview: pd.DataFrame,
    log: bool = True,
) -> pd.DataFrame:
    """
    Calculate the selected metrics DataFrame based on the metrics_overview,
    and the query object.

    Parameters
    ----------
    metrics_overview : pd.DataFrame
        The metrics overview DataFrame.
    query_str : str
        The query string to filter metrics.
    log : bool, optional
        Whether to log the selected metrics, by default True.

    Returns
    -------
    pd.DataFrame
        The filtered and sorted metrics DataFrame.
    """
    selected = metrics_overview.query(query.query_str).sort_values(
        ["site", "location", "data_group", "short_hand", "statistic"],
        ascending=[True, True, False, True, True],
    )
    if log:
        logging.info("\033[32;1mMetrics selected for the query:\033[0m\n")
        logging.info(selected[["metric", "unit_str", "site", "location"]])
    if selected.empty:
        raise E.DataSignalsError(
            "\033[31;1mNo metrics found for the given query.\033[0m"
            "\033[33;1m\nHINT:\033[22m Check \033[2msites\033[22m, "
            "\033[2mlocations\033[22m, and \033[2mmetrics\033[22m "
            "provided.\033[0m\n\n"
            "Provided:\n"
            f"  • sites: {query.sites}\n"
            f"  • locations: {query.locations}\n"
            f"  • metrics: {query.metrics}\n"
        )
    return selected


def get_selected_locations(
    query: GetOldestTimestampSchema,
    metrics_overview: pd.DataFrame,
    log: bool = True,
) -> pd.DataFrame:
    """
    Calculate the selected locations DataFrame based on the metrics_overview,
    and the query object.

    Parameters
    ----------
    query: GetOldestTimestampSchema
        Timestamp schema query class instance.
    metrics_overview : pd.DataFrame
        The metrics overview DataFrame.
    log : bool, optional
        Whether to log the selected locations, by default True.

    Returns
    -------
    pd.DataFrame
        The filtered and sorted locations DataFrame.
    """
    # fmt: off
    selected = metrics_overview \
        .query(query.query_str)[["site", "location",
                                 "site_id", "location_id"]] \
        .assign(site_lower=lambda x: x["site"].str.lower(),
                location_lower=lambda x: x["location"].str.lower()) \
        .drop_duplicates(subset=["site_lower", "location_lower"]) \
        .drop(columns=["site_lower", "location_lower"]) \
        .sort_values(["site", "location"], ascending=[True, True])
    # fmt: on
    if log:
        logging.info("\033[32;1mLocations selected for the query:\033[0m\n")
        logging.info(selected[["site", "location"]])
    if selected.empty:
        raise E.DataSignalsError(
            "\033[31;1mNo locations found for the given query.\033[0m"
            "\033[33;1m\nHINT:\033[22m Check \033[2msites\033[22m and "
            "\033[2mlocations\033[22m provided.\033[0m\n\n"
            "Provided:\n"
            f"  • site: {query.site}\n"
            f"  • locations: {query.locations}\n"
        )
    # Check if site_id matches multiple sites
    unique_sites = selected[["site", "site_id"]].drop_duplicates()
    site_id_matches = unique_sites[
        unique_sites["site_id"].str.lower() == query.site
    ]
    if len(site_id_matches) > 1:
        matching_sites = site_id_matches["site"].tolist()
        raise E.DataSignalsError(
            f"\033[31;1msite_id '{query.site}' matches multiple sites: "
            f"{matching_sites}\033[0m\n\033[33;1mHINT:\033[22m Use the site "
            "name directly as input parameter rather than the site_id to avoid "
            "ambiguity.\033[0m\n"
        )
    return selected
