from __future__ import annotations

import json

import pandas as pd
import pytest

import great_expectations.expectations as gxe
from great_expectations.core import (
    ExpectationSuiteValidationResult,
    ExpectationValidationResult,
)
from great_expectations.core.expectation_validation_result import (
    ExpectationSuiteValidationResultMeta,
)
from great_expectations.expectations.expectation_configuration import (
    ExpectationConfiguration,
)


@pytest.mark.unit
def test_expectation_validation_result_describe_returns_expected_description():
    # arrange
    evr = ExpectationValidationResult(
        success=False,
        expectation_config=gxe.ExpectColumnValuesToBeBetween(
            column="passenger_count",
            min_value=0,
            max_value=6,
            notes="Per the TLC data dictionary, this is a driver-submitted value (historically between 0 to 6)",  # noqa: E501 # FIXME CoP
        ).configuration,
        result={
            "element_count": 100000,
            "unexpected_count": 1,
            "unexpected_percent": 0.001,
            "partial_unexpected_list": [7.0],
            "missing_count": 0,
            "missing_percent": 0.0,
            "unexpected_percent_total": 0.001,
            "unexpected_percent_nonmissing": 0.001,
            "partial_unexpected_counts": [{"value": 7.0, "count": 1}],
            "partial_unexpected_index_list": [48422],
        },
        exception_info={
            "raised_exception": False,
            "exception_traceback": None,
            "exception_message": None,
        },
    )
    # act
    description = evr.describe()
    # assert
    assert description == json.dumps(
        {
            "expectation_type": "expect_column_values_to_be_between",
            "success": False,
            "kwargs": {"column": "passenger_count", "min_value": 0.0, "max_value": 6.0},
            "result": {
                "element_count": 100000,
                "unexpected_count": 1,
                "unexpected_percent": 0.001,
                "partial_unexpected_list": [7.0],
                "missing_count": 0,
                "missing_percent": 0.0,
                "unexpected_percent_total": 0.001,
                "unexpected_percent_nonmissing": 0.001,
                "partial_unexpected_counts": [{"value": 7.0, "count": 1}],
                "partial_unexpected_index_list": [48422],
            },
        },
        indent=4,
    )


@pytest.mark.unit
def test_expectation_validation_result_describe_returns_expected_description_with_null_values():
    # It's unclear if an ExpectationValidationResult can ever be valid without an Expectation
    # or a result, but since it's typed that way we test it
    # arrange
    evr = ExpectationValidationResult(
        success=True,
        exception_info={
            "raised_exception": False,
            "exception_traceback": None,
            "exception_message": None,
        },
    )
    # act
    description = evr.describe()
    # assert
    assert description == json.dumps(
        {
            "expectation_type": None,
            "success": True,
            "kwargs": None,
            "result": {},
        },
        indent=4,
    )


@pytest.mark.unit
def test_expectation_validation_result_describe_returns_expected_description_with_exception():
    # arrange
    evr = ExpectationValidationResult(
        success=False,
        expectation_config=gxe.ExpectColumnValuesToBeBetween(
            column="passenger_count",
            min_value=0,
            max_value=6,
            notes="Per the TLC data dictionary, this is a driver-submitted value (historically between 0 to 6)",  # noqa: E501 # FIXME CoP
        ).configuration,
        result={
            "element_count": 100000,
            "unexpected_count": 1,
            "unexpected_percent": 0.001,
            "partial_unexpected_list": [7.0],
            "missing_count": 0,
            "missing_percent": 0.0,
            "unexpected_percent_total": 0.001,
            "unexpected_percent_nonmissing": 0.001,
            "partial_unexpected_counts": [{"value": 7.0, "count": 1}],
            "partial_unexpected_index_list": [48422],
        },
        exception_info={
            "raised_exception": True,
            "exception_traceback": "Traceback (most recent call last): something went wrong",
            "exception_message": "Helpful message here",
        },
    )
    # act
    description = evr.describe()
    # assert
    assert description == json.dumps(
        {
            "expectation_type": "expect_column_values_to_be_between",
            "success": False,
            "kwargs": {"column": "passenger_count", "min_value": 0.0, "max_value": 6.0},
            "result": {
                "element_count": 100000,
                "unexpected_count": 1,
                "unexpected_percent": 0.001,
                "partial_unexpected_list": [7.0],
                "missing_count": 0,
                "missing_percent": 0.0,
                "unexpected_percent_total": 0.001,
                "unexpected_percent_nonmissing": 0.001,
                "partial_unexpected_counts": [{"value": 7.0, "count": 1}],
                "partial_unexpected_index_list": [48422],
            },
            "exception_info": {
                "raised_exception": True,
                "exception_traceback": "Traceback (most recent call last): something went wrong",
                "exception_message": "Helpful message here",
            },
        },
        indent=4,
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "validation_result_url",
    [
        "https://app.greatexpectations.io/organizations/my-org/data-assets/6f6d390b-a52b-41d1-b5c0-a1d57a6b4618/validations/expectation-suites/a0af0eb5-90ab-4219-ab60-482eee0a8b32/results/e77ce5e4-b71b-4f86-9c3b-f82385aab660",
        None,
    ],
)
def test_expectation_suite_validation_result_returns_expected_shape(
    validation_result_url: str | None,
):
    # arrange
    svr = ExpectationSuiteValidationResult(
        success=True,
        statistics={
            "evaluated_expectations": 2,
            "successful_expectations": 2,
            "unsuccessful_expectations": 0,
            "success_percent": 100.0,
        },
        suite_name="empty_suite",
        results=[
            ExpectationValidationResult(
                **{
                    "meta": {},
                    "success": True,
                    "exception_info": {
                        "raised_exception": False,
                        "exception_traceback": None,
                        "exception_message": None,
                    },
                    "result": {
                        "element_count": 100000,
                        "unexpected_count": 1,
                        "unexpected_percent": 0.001,
                        "partial_unexpected_list": [7.0],
                        "missing_count": 0,
                        "missing_percent": 0.0,
                        "unexpected_percent_total": 0.001,
                        "unexpected_percent_nonmissing": 0.001,
                        "partial_unexpected_counts": [{"value": 7.0, "count": 1}],
                        "partial_unexpected_index_list": [48422],
                    },
                    "expectation_config": ExpectationConfiguration(
                        **{
                            "meta": {},
                            "notes": "Per the TLC data dictionary, this is a driver-submitted value (historically between 0 to 6)",  # noqa: E501 # FIXME CoP
                            "id": "9f76d0b5-9d99-4ed9-a269-339b35e60490",
                            "kwargs": {
                                "batch_id": "default_pandas_datasource-#ephemeral_pandas_asset",
                                "mostly": 0.95,
                                "column": "passenger_count",
                                "min_value": 0.0,
                                "max_value": 6.0,
                            },
                            "type": "expect_column_values_to_be_between",
                        }
                    ),
                }
            ),
            ExpectationValidationResult(
                **{
                    "meta": {},
                    "success": True,
                    "exception_info": {
                        "raised_exception": False,
                        "exception_traceback": None,
                        "exception_message": None,
                    },
                    "result": {
                        "element_count": 100000,
                        "unexpected_count": 0,
                        "unexpected_percent": 0.0,
                        "partial_unexpected_list": [],
                        "partial_unexpected_counts": [],
                        "partial_unexpected_index_list": [],
                    },
                    "expectation_config": ExpectationConfiguration(
                        **{
                            "meta": {},
                            "id": "19c0e80c-d676-4b01-a4a3-2a568552d368",
                            "kwargs": {
                                "batch_id": "default_pandas_datasource-#ephemeral_pandas_asset",
                                "column": "trip_distance",
                            },
                            "type": "expect_column_values_to_not_be_null",
                        }
                    ),
                }
            ),
        ],
        result_url=validation_result_url,
    )
    # act
    description = svr.describe()
    # assert
    assert description == json.dumps(
        {
            "success": True,
            "statistics": {
                "evaluated_expectations": 2,
                "successful_expectations": 2,
                "unsuccessful_expectations": 0,
                "success_percent": 100.0,
            },
            "expectations": [
                {
                    "expectation_type": "expect_column_values_to_be_between",
                    "success": True,
                    "kwargs": {
                        "batch_id": "default_pandas_datasource-#ephemeral_pandas_asset",
                        "mostly": 0.95,
                        "column": "passenger_count",
                        "min_value": 0.0,
                        "max_value": 6.0,
                    },
                    "result": {
                        "element_count": 100000,
                        "unexpected_count": 1,
                        "unexpected_percent": 0.001,
                        "partial_unexpected_list": [7.0],
                        "missing_count": 0,
                        "missing_percent": 0.0,
                        "unexpected_percent_total": 0.001,
                        "unexpected_percent_nonmissing": 0.001,
                        "partial_unexpected_counts": [{"value": 7.0, "count": 1}],
                        "partial_unexpected_index_list": [48422],
                    },
                },
                {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "success": True,
                    "kwargs": {
                        "batch_id": "default_pandas_datasource-#ephemeral_pandas_asset",
                        "column": "trip_distance",
                    },
                    "result": {
                        "element_count": 100000,
                        "unexpected_count": 0,
                        "unexpected_percent": 0.0,
                        "partial_unexpected_list": [],
                        "partial_unexpected_counts": [],
                        "partial_unexpected_index_list": [],
                    },
                },
            ],
            "result_url": validation_result_url,
        },
        indent=4,
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "validation_result_url",
    [
        "https://app.greatexpectations.io/organizations/my-org/data-assets/6f6d390b-a52b-41d1-b5c0-a1d57a6b4618/validations/expectation-suites/a0af0eb5-90ab-4219-ab60-482eee0a8b32/results/e77ce5e4-b71b-4f86-9c3b-f82385aab660",
        None,
    ],
)
def test_expectation_suite_validation_asset_name_access(
    validation_result_url: str | None,
):
    # arrange
    svr = ExpectationSuiteValidationResult(
        meta=ExpectationSuiteValidationResultMeta(
            **{
                "active_batch_definition": {
                    "batch_identifiers": {},
                    "data_asset_name": "taxi_data_1.csv",
                    "data_connector_name": "default_inferred_data_connector_name",
                    "datasource_name": "pandas",
                },
                "batch_markers": {
                    "ge_load_time": "20220727T154327.630107Z",
                    "pandas_data_fingerprint": "c4f929e6d4fab001fedc9e075bf4b612",
                },
                "batch_spec": {"path": "../data/taxi_data_1.csv"},
                "checkpoint_name": "single_validation_checkpoint",
                "expectation_suite_name": "taxi_suite_1",
                "great_expectations_version": "0.15.15",
                "run_id": {
                    "run_name": "20220727-114327-my-run-name-template",
                    "run_time": "2022-07-27T11:43:27.625252+00:00",
                },
                "validation_time": "20220727T154327.701100Z",
            }
        ),
        success=True,
        statistics={
            "evaluated_expectations": 2,
            "successful_expectations": 2,
            "unsuccessful_expectations": 0,
            "success_percent": 100.0,
        },
        suite_name="empty_suite",
        results=[
            ExpectationValidationResult(
                **{
                    "meta": {},
                    "success": True,
                    "exception_info": {
                        "raised_exception": False,
                        "exception_traceback": None,
                        "exception_message": None,
                    },
                    "result": {
                        "element_count": 100000,
                        "unexpected_count": 1,
                        "unexpected_percent": 0.001,
                        "partial_unexpected_list": [7.0],
                        "missing_count": 0,
                        "missing_percent": 0.0,
                        "unexpected_percent_total": 0.001,
                        "unexpected_percent_nonmissing": 0.001,
                        "partial_unexpected_counts": [{"value": 7.0, "count": 1}],
                        "partial_unexpected_index_list": [48422],
                    },
                    "expectation_config": ExpectationConfiguration(
                        **{
                            "meta": {},
                            "notes": "Test notes",
                            "id": "9f76d0b5-9d99-4ed9-a269-339b35e60490",
                            "kwargs": {
                                "batch_id": "default_pandas_datasource-#ephemeral_pandas_asset",
                            },
                            "type": "expect_column_values_to_be_between",
                        }
                    ),
                }
            ),
        ],
        result_url=validation_result_url,
    )

    assert svr.asset_name == "taxi_data_1.csv"


@pytest.mark.unit
def test_render_updates_rendered_content():
    evr = ExpectationValidationResult(
        success=False,
        expectation_config=gxe.ExpectColumnValuesToBeBetween(
            column="passenger_count",
            min_value=0,
            max_value=6,
            notes="Per the TLC data dictionary, this is a driver-submitted value (historically between 0 to 6)",  # noqa: E501 # FIXME CoP
        ).configuration,
        result={
            "element_count": 100000,
            "unexpected_count": 1,
            "unexpected_percent": 0.001,
            "partial_unexpected_list": [7.0],
            "missing_count": 0,
            "missing_percent": 0.0,
            "unexpected_percent_total": 0.001,
            "unexpected_percent_nonmissing": 0.001,
            "partial_unexpected_counts": [{"value": 7.0, "count": 1}],
            "partial_unexpected_index_list": [48422],
        },
    )

    assert evr.rendered_content is None

    evr.render()

    assert evr.rendered_content is not None


class TestSerialization:
    @pytest.mark.unit
    def test_expectation_validation_results_serializes(self) -> None:
        evr = ExpectationValidationResult(
            success=True,
            expectation_config=gxe.ExpectColumnDistinctValuesToEqualSet(
                column="passenger_count",
                value_set=[1, 2],
            ).configuration,
            result={
                "details": {
                    "observed_value": pd.Series({"a": 1, "b": 2, "c": 4}),
                }
            },
        )

        # Ensure the results are serializable.
        as_dict = evr.describe_dict()
        from_describe_dict = json.dumps(as_dict, indent=4)
        from_describe = evr.describe()

        assert from_describe_dict == from_describe
        assert as_dict["result"]["details"]["observed_value"] == [
            {"index": "a", "value": 1},
            {"index": "b", "value": 2},
            {"index": "c", "value": 4},
        ]

    @pytest.mark.unit
    def test_expectation_suite_validation_results_serializes(self) -> None:
        svr = ExpectationSuiteValidationResult(
            success=True,
            statistics={
                "evaluated_expectations": 2,
                "successful_expectations": 2,
                "unsuccessful_expectations": 0,
                "success_percent": 100.0,
            },
            suite_name="whatever",
            results=[
                ExpectationValidationResult(
                    success=True,
                    expectation_config=gxe.ExpectColumnDistinctValuesToEqualSet(
                        column="passenger_count",
                        value_set=[1, 2],
                    ).configuration,
                    result={
                        "details": {
                            "observed_value": pd.Series({"a": 1, "b": 2, "c": 4}),
                        }
                    },
                )
            ],
        )

        # Ensure the results are serializable.
        as_dict = svr.describe_dict()
        from_describe_dict = json.dumps(as_dict, indent=4)
        from_describe = svr.describe()

        assert from_describe_dict == from_describe
        assert as_dict["expectations"][0]["result"]["details"]["observed_value"] == [
            {"index": "a", "value": 1},
            {"index": "b", "value": 2},
            {"index": "c", "value": 4},
        ]


class TestExpectationValidationResultHash:
    @pytest.mark.unit
    def test_hash_consistency_with_equality(self):
        config1 = ExpectationConfiguration(
            type="expect_column_values_to_not_be_null", kwargs={"column": "test_column"}
        )
        config2 = ExpectationConfiguration(
            type="expect_column_values_to_not_be_null", kwargs={"column": "test_column"}
        )

        result1 = ExpectationValidationResult(
            success=True,
            expectation_config=config1,
            result={"observed_value": 100},
            meta={"test": "value"},
            exception_info={"raised_exception": False},
        )

        result2 = ExpectationValidationResult(
            success=True,
            expectation_config=config2,
            result={"observed_value": 100},
            meta={"test": "value"},
            exception_info={"raised_exception": False},
        )

        assert result1 == result2
        assert hash(result1) == hash(result2)

    @pytest.mark.unit
    def test_hash_different_for_different_success(self):
        config = ExpectationConfiguration(
            type="expect_column_values_to_not_be_null", kwargs={"column": "test_column"}
        )

        result1 = ExpectationValidationResult(
            success=True, expectation_config=config, result={"observed_value": 100}
        )

        result2 = ExpectationValidationResult(
            success=False, expectation_config=config, result={"observed_value": 100}
        )

        assert result1 != result2
        assert hash(result1) != hash(result2)

    @pytest.mark.unit
    def test_hash_different_for_different_results(self):
        config = ExpectationConfiguration(
            type="expect_column_values_to_not_be_null", kwargs={"column": "test_column"}
        )

        result1 = ExpectationValidationResult(
            success=True, expectation_config=config, result={"observed_value": 100}
        )

        result2 = ExpectationValidationResult(
            success=True, expectation_config=config, result={"observed_value": 200}
        )

        assert result1 != result2
        assert hash(result1) != hash(result2)

    @pytest.mark.unit
    def test_hash_stable_across_runs(self):
        config = ExpectationConfiguration(
            type="expect_column_values_to_not_be_null", kwargs={"column": "test_column"}
        )

        result = ExpectationValidationResult(
            success=True,
            expectation_config=config,
            result={"observed_value": 100},
            meta={"test": "value"},
            exception_info={"raised_exception": False},
        )

        hash1 = hash(result)
        hash2 = hash(result)
        hash3 = hash(result)

        assert hash1 == hash2 == hash3


class TestExpectationSuiteValidationResultHash:
    @pytest.mark.unit
    def test_hash_consistency_with_equality(self):
        config = ExpectationConfiguration(
            type="expect_column_values_to_not_be_null", kwargs={"column": "test_column"}
        )

        evr = ExpectationValidationResult(
            success=True, expectation_config=config, result={"observed_value": 100}
        )

        result1 = ExpectationSuiteValidationResult(
            suite_name="test_suite",
            success=True,
            results=[evr],
            suite_parameters={"param": "value"},
            statistics={"evaluated_expectations": 1},
            meta={"test": "value"},
        )

        result2 = ExpectationSuiteValidationResult(
            suite_name="test_suite",
            success=True,
            results=[evr],
            suite_parameters={"param": "value"},
            statistics={"evaluated_expectations": 1},
            meta={"test": "value"},
        )

        assert result1 == result2
        assert hash(result1) == hash(result2)

    @pytest.mark.unit
    def test_hash_different_for_different_success(self):
        config = ExpectationConfiguration(
            type="expect_column_values_to_not_be_null", kwargs={"column": "test_column"}
        )

        evr = ExpectationValidationResult(
            success=True, expectation_config=config, result={"observed_value": 100}
        )

        result1 = ExpectationSuiteValidationResult(
            suite_name="test_suite",
            success=True,
            results=[evr],
            suite_parameters={"param": "value"},
        )

        result2 = ExpectationSuiteValidationResult(
            suite_name="test_suite",
            success=False,
            results=[evr],
            suite_parameters={"param": "value"},
        )

        assert result1 != result2
        assert hash(result1) != hash(result2)

    @pytest.mark.unit
    def test_hash_stable_across_runs(self):
        config = ExpectationConfiguration(
            type="expect_column_values_to_not_be_null", kwargs={"column": "test_column"}
        )

        evr = ExpectationValidationResult(
            success=True, expectation_config=config, result={"observed_value": 100}
        )

        result = ExpectationSuiteValidationResult(
            suite_name="test_suite",
            success=True,
            results=[evr],
            suite_parameters={"param": "value"},
            statistics={"evaluated_expectations": 1},
            meta={"test": "value"},
        )

        hash1 = hash(result)
        hash2 = hash(result)
        hash3 = hash(result)

        assert hash1 == hash2 == hash3
