from pydantic import model_validator
from typing import Self
from maleo.soma.mixins.parameter import (
    DateFilters,
    Filters,
    ListOfDataStatuses,
    SortColumns,
    Sorts,
    Search,
    UseCache,
)
from maleo.soma.schemas.pagination import BaseFlexiblePagination, BaseStrictPagination


class ReadUnpaginatedMultipleParameterSchema(
    UseCache,
    BaseFlexiblePagination,
    SortColumns,
    Search,
    ListOfDataStatuses,
    DateFilters,
):
    pass


class ReadUnpaginatedMultipleQueryParameterSchema(
    Sorts,
    Filters,
    ReadUnpaginatedMultipleParameterSchema,
):
    @model_validator(mode="after")
    def set_sort(self) -> Self:
        # * Process sort_columns parameters
        sort = []
        for item in self.sort_columns:
            sort.append(f"{item.name}.{item.order.value}")

        # * Only update if we have valid sort, otherwise keep the default
        if sort:
            self.sorts = sort

        return self

    @model_validator(mode="after")
    def set_filter(self) -> Self:
        # * Process filter parameters
        filter = []
        for item in self.date_filters:
            if item.from_date or item.to_date:
                filter_string = item.name
                if item.from_date:
                    filter_string += f"|from::{item.from_date.isoformat()}"
                if item.to_date:
                    filter_string += f"|to::{item.to_date.isoformat()}"
                filter.append(filter_string)

        # * Only update if we have valid filter, otherwise keep the default
        if filter:
            self.filters = filter

        return self


class ReadPaginatedMultipleParameterSchema(
    UseCache,
    BaseStrictPagination,
    SortColumns,
    Search,
    ListOfDataStatuses,
    DateFilters,
):
    pass


class ReadPaginatedMultipleQueryParameterSchema(
    Sorts,
    Filters,
    ReadPaginatedMultipleParameterSchema,
):
    @model_validator(mode="after")
    def set_sort(self) -> Self:
        # * Process sort_columns parameters
        sort = []
        for item in self.sort_columns:
            sort.append(f"{item.name}.{item.order.value}")

        # * Only update if we have valid sort, otherwise keep the default
        if sort:
            self.sorts = sort

        return self

    @model_validator(mode="after")
    def set_filter(self) -> Self:
        # * Process filter parameters
        filter = []
        for item in self.date_filters:
            if item.from_date or item.to_date:
                filter_string = item.name
                if item.from_date:
                    filter_string += f"|from::{item.from_date.isoformat()}"
                if item.to_date:
                    filter_string += f"|to::{item.to_date.isoformat()}"
                filter.append(filter_string)

        # * Only update if we have valid filter, otherwise keep the default
        if filter:
            self.filters = filter

        return self
