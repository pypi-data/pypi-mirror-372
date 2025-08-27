"""
This module provides functions for validating a DICOM sessions.

The module supports compliance checks for JSON-based schema sessions and Python module-based validation models.

"""

from typing import List, Dict, Any, Optional
from dicompare.validation import BaseValidationModel, create_validation_models_from_rules
from dicompare.validation_helpers import (
    validate_constraint, validate_field_values, create_compliance_record, format_constraint_description,
    ComplianceStatus
)
import pandas as pd

def check_session_compliance_with_json_schema(
    in_session: pd.DataFrame,
    schema_session: Dict[str, Any],
    session_map: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Validate a DICOM session against a JSON schema session.
    All string comparisons occur in a case-insensitive manner with extra whitespace trimmed.
    If an input value is a list with one element and the expected value is a string,
    the element is unwrapped before comparing.

    Args:
        in_session (pd.DataFrame): Input session DataFrame containing DICOM metadata.
        schema_session (Dict[str, Any]): Schema session data loaded from a JSON file.
        session_map (Dict[str, str]): Mapping of schema acquisitions to input acquisitions.

    Returns:
        List[Dict[str, Any]]: A list of compliance issues. Acquisition-level checks yield a record with "series": None.
                              Series-level checks produce one record per schema series.
    """
    compliance_summary: List[Dict[str, Any]] = []

    def _check_acquisition_fields(
        schema_acq_name: str,
        in_acq_name: str,
        schema_fields: List[Dict[str, Any]],
        in_acq: pd.DataFrame
    ) -> None:
        for fdef in schema_fields:
            field = fdef["field"]
            expected_value = fdef.get("value")
            tolerance = fdef.get("tolerance")
            contains = fdef.get("contains")

            if field not in in_acq.columns:
                print(f"DEBUG compliance.py: Field '{field}' not found, creating NA record")
                compliance_summary.append(create_compliance_record(
                    schema_acq_name, in_acq_name, None, field,
                    expected_value, tolerance, contains, None,
                    "Field not found in input session.", False,
                    status=ComplianceStatus.NA
                ))
                continue

            actual_values = in_acq[field].unique().tolist()
            
            # Use validation helper to check field values
            passed, invalid_values, message = validate_field_values(
                field, actual_values, expected_value, tolerance, contains
            )
            
            compliance_summary.append(create_compliance_record(
                schema_acq_name, in_acq_name, None, field,
                expected_value, tolerance, contains, actual_values,
                message, passed
            ))

    def _check_series_fields(
        schema_acq_name: str,
        in_acq_name: str,
        schema_series_schema: Dict[str, Any],
        in_acq: pd.DataFrame
    ) -> None:
        
        schema_series_name = schema_series_schema.get("name", "<unnamed>")
        schema_series_fields = schema_series_schema.get("fields", [])
        
        print(f"    DEBUG _check_series_fields: series '{schema_series_name}'")
        print(f"      Schema fields: {[(f['field'], f.get('value')) for f in schema_series_fields]}")
        print(f"      Input data shape: {in_acq.shape}")
        
        matching_df = in_acq

        # First pass: check for missing fields and filter matching rows
        for fdef in schema_series_fields:
            field = fdef["field"]
            e_val = fdef.get("value")
            tol = fdef.get("tolerance")
            ctn = fdef.get("contains")

            print(f"      Processing field '{field}' with expected value: {e_val}")

            if field not in matching_df.columns:
                print(f"      ERROR: Field '{field}' not found in columns")
                compliance_summary.append(create_compliance_record(
                    schema_acq_name, in_acq_name, schema_series_name, field,
                    e_val, tol, ctn, None,
                    f"Field '{field}' not found in input for series '{schema_series_name}'.", False,
                    status=ComplianceStatus.NA
                ))
                return

            # Check current values before filtering
            print(f"      Current '{field}' values: {matching_df[field].unique()}")
            print(f"      Rows before filtering: {len(matching_df)}")
            
            # Filter rows that match this constraint
            matches = matching_df[field].apply(lambda x: validate_constraint(x, e_val, tol, ctn))
            print(f"      Matching constraint validation: {matches.sum()} of {len(matches)} rows match")
            
            matching_df = matching_df[matches]
            print(f"      Rows after filtering: {len(matching_df)}")
            
            if matching_df.empty:
                print(f"      No matching rows found, breaking")
                break

        # If no matching series found, report failure
        if matching_df.empty:
            print(f"      RESULT: No matching series found - creating failure record")
            field_names = [f["field"] for f in schema_series_fields]
            compliance_summary.append(create_compliance_record(
                schema_acq_name, in_acq_name, schema_series_name, ", ".join(field_names),
                schema_series_schema['fields'], None, None, None,
                f"Series '{schema_series_name}' not found with the specified constraints.", False
            ))
            return
        else:
            print(f"      RESULT: Found matching series with {len(matching_df)} rows - proceeding to validation")

        # Second pass: validate all field values in matching series
        actual_values_agg = {}
        constraints_agg = {}
        fail_messages = []
        any_fail = False

        for fdef in schema_series_fields:
            field = fdef["field"]
            e_val = fdef.get("value")
            tol = fdef.get("tolerance")
            ctn = fdef.get("contains")

            values = matching_df[field].unique().tolist()
            actual_values_agg[field] = values

            # Format constraint description
            constraints_agg[field] = format_constraint_description(e_val, tol, ctn)

            # Validate field values
            passed, invalid_values, message = validate_field_values(
                field, values, e_val, tol, ctn
            )
            
            if not passed:
                any_fail = True
                fail_messages.append(f"Field '{field}': {message}")

        # Create final compliance record
        field_names = [f["field"] for f in schema_series_fields]
        final_message = "; ".join(fail_messages) if any_fail else "Passed"
        
        print(f"      FINAL: Creating series compliance record - passed: {not any_fail}")
        print(f"      Field: {', '.join(field_names)}, Series: {schema_series_name}")
        
        compliance_summary.append({
            "schema acquisition": schema_acq_name,
            "input acquisition": in_acq_name,
            "series": schema_series_name,
            "field": ", ".join(field_names),
            "expected": constraints_agg,
            "value": actual_values_agg,
            "message": final_message,
            "passed": not any_fail
        })
        
        print(f"      ADDED to compliance_summary. Total records now: {len(compliance_summary)}")

    # 1) Check for unmapped reference acquisitions.
    for schema_acq_name in schema_session["acquisitions"]:
        if schema_acq_name not in session_map:
            compliance_summary.append(create_compliance_record(
                schema_acq_name, None, None, None,
                "(mapped acquisition required)", None, None, None,
                f"Schema acquisition '{schema_acq_name}' not mapped.", False
            ))

    # 2) Process each mapped acquisition.
    for schema_acq_name, in_acq_name in session_map.items():
        schema_acq = schema_session["acquisitions"].get(schema_acq_name, {})
        in_acq = in_session[in_session["Acquisition"] == in_acq_name]
        
        print(f"DEBUG: Processing acquisition '{schema_acq_name}' -> '{in_acq_name}'")
        print(f"  Schema has {len(schema_acq.get('fields', []))} fields, {len(schema_acq.get('series', []))} series")
        print(f"  Input has {len(in_acq)} rows, columns: {list(in_acq.columns)}")
        if 'ImageType' in in_acq.columns:
            print(f"  ImageType values in input: {in_acq['ImageType'].unique()}")
        
        schema_fields = schema_acq.get("fields", [])
        _check_acquisition_fields(schema_acq_name, in_acq_name, schema_fields, in_acq)
        
        schema_series = schema_acq.get("series", [])
        print(f"  Checking {len(schema_series)} series definitions...")
        for i, sdef in enumerate(schema_series):
            print(f"    Series {i}: name='{sdef.get('name')}', fields={[f['field'] for f in sdef.get('fields', [])]}")
            _check_series_fields(schema_acq_name, in_acq_name, sdef, in_acq)

    return compliance_summary


def check_session_compliance_with_python_module(
    in_session: pd.DataFrame,
    schema_models: Dict[str, BaseValidationModel],
    session_map: Dict[str, str],
    raise_errors: bool = False
) -> List[Dict[str, Any]]:
    """
    Validate a DICOM session against Python module-based validation models.

    Args:
        in_session (pd.DataFrame): Input session DataFrame containing DICOM metadata.
        schema_models (Dict[str, BaseValidationModel]): Dictionary mapping acquisition names to 
            validation models.
        session_map (Dict[str, str]): Mapping of reference acquisitions to input acquisitions.
        raise_errors (bool): Whether to raise exceptions for validation failures. Defaults to False.

    Returns:
        List[Dict[str, Any]]: A list of compliance issues, where each issue is represented as a dictionary.
    
    Raises:
        ValueError: If `raise_errors` is True and validation fails for any acquisition.
    """
    compliance_summary = []

    for schema_acq_name, in_acq_name in session_map.items():
        # Filter the input session for the current acquisition
        in_acq = in_session[in_session["Acquisition"] == in_acq_name]

        if in_acq.empty:
            compliance_summary.append({
                "schema acquisition": schema_acq_name,
                "input acquisition": in_acq_name,
                "field": "Acquisition-Level Error",
                "value": None,
                "rule_name": "Acquisition presence",
                "expected": "Specified input acquisition must be present.",
                "message": f"Input acquisition '{in_acq_name}' not found in data.",
                "passed": False,
                "status": ComplianceStatus.NA.value
            })
            continue

        # Retrieve reference model
        schema_model_cls = schema_models.get(schema_acq_name)
        if not schema_model_cls:
            compliance_summary.append({
                "schema acquisition": schema_acq_name,
                "input acquisition": in_acq_name,
                "field": "Model Error",
                "value": None,
                "rule_name": "Model presence",
                "expected": "Schema model must exist.",
                "message": f"No model found for reference acquisition '{schema_acq_name}'.",
                "passed": False,
                "status": ComplianceStatus.ERROR.value
            })
            continue
        schema_model = schema_model_cls()

        # Prepare acquisition data as a single DataFrame
        acquisition_df = in_acq.copy()

        # Validate using the reference model
        success, errors, passes = schema_model.validate(data=acquisition_df)

        # Record errors
        for error in errors:
            # Check if this is a "field not found" error
            status = ComplianceStatus.NA if "not found" in error.get('message', '').lower() else ComplianceStatus.ERROR
            compliance_summary.append({
                "schema acquisition": schema_acq_name,
                "input acquisition": in_acq_name,
                "field": error['field'],
                "value": error['value'],
                "expected": error['expected'],
                "message": error['message'],
                "rule_name": error['rule_name'],
                "passed": False,
                "status": status.value
            })

        # Record passes
        for passed_test in passes:
            compliance_summary.append({
                "schema acquisition": schema_acq_name,
                "input acquisition": in_acq_name,
                "field": passed_test['field'],
                "value": passed_test['value'],
                "expected": passed_test['expected'],
                "message": passed_test['message'],
                "rule_name": passed_test['rule_name'],
                "passed": True,
                "status": ComplianceStatus.OK.value
            })

        # Raise an error if validation fails and `raise_errors` is True
        if raise_errors and not success:
            raise ValueError(f"Validation failed for acquisition '{in_acq_name}'.")

    return compliance_summary


def check_session_compliance(
    in_session: pd.DataFrame,
    schema_data: Dict[str, Any],
    session_map: Dict[str, str],
    validation_rules: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    validation_models: Optional[Dict[str, BaseValidationModel]] = None,
    raise_errors: bool = False
) -> List[Dict[str, Any]]:
    """
    Unified compliance checking function that handles both field validation and rule validation.
    
    This function combines the functionality of check_session_compliance_with_json_schema and
    check_session_compliance_with_python_module, supporting hybrid schemas with both field
    constraints and embedded Python validation rules.
    
    Args:
        in_session (pd.DataFrame): Input session DataFrame containing DICOM metadata.
        schema_data (Dict[str, Any]): Schema data loaded from a JSON file.
        session_map (Dict[str, str]): Mapping of schema acquisitions to input acquisitions.
        validation_rules (Optional[Dict[str, List[Dict[str, Any]]]]): Dictionary mapping
            acquisition names to their validation rules (from hybrid schemas).
        validation_models (Optional[Dict[str, BaseValidationModel]]): Pre-created validation
            models. If not provided but validation_rules are, models will be created dynamically.
        raise_errors (bool): Whether to raise exceptions for validation failures. Defaults to False.
        
    Returns:
        List[Dict[str, Any]]: A list of compliance issues and passes. Each record contains:
            - schema acquisition: The reference acquisition name
            - input acquisition: The actual acquisition name in the input
            - field: The field(s) being validated
            - value: The actual value(s) found
            - expected: The expected value or constraint
            - message: Error message (for failures) or "OK" (for passes)
            - rule_name: The name of the validation rule (for rule-based validations)
            - passed: Boolean indicating if the check passed
            - status: The compliance status (OK, ERROR, NA, etc.)
            
    Raises:
        ValueError: If `raise_errors` is True and validation fails for any acquisition.
        
    Example:
        >>> # Load a hybrid schema
        >>> fields, schema_data, rules = load_hybrid_schema("schema.json")
        >>> 
        >>> # Check compliance
        >>> results = check_session_compliance(
        ...     in_session=session_df,
        ...     schema_data=schema_data,
        ...     session_map={"QSM": "qsm_acq"},
        ...     validation_rules=rules
        ... )
    """
    compliance_summary = []
    
    # Create validation models from rules if needed
    if validation_rules and not validation_models:
        validation_models = create_validation_models_from_rules(validation_rules)
    
    # Helper function for field validation (adapted from check_session_compliance_with_json_schema)
    def _check_field_compliance(
        schema_acq_name: str,
        in_acq_name: str,
        schema_fields: List[Dict[str, Any]],
        in_acq: pd.DataFrame,
        series_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Check field-level compliance for an acquisition or series."""
        field_results = []
        
        for fdef in schema_fields:
            field = fdef["field"]
            expected_value = fdef.get("value")
            tolerance = fdef.get("tolerance")
            contains = fdef.get("contains")
            
            if field not in in_acq.columns:
                field_results.append(create_compliance_record(
                    schema_acq_name, in_acq_name, series_name, field,
                    expected_value, tolerance, contains, None,
                    "Field not found in input session.", False,
                    status=ComplianceStatus.NA
                ))
                continue
            
            actual_values = in_acq[field].unique().tolist()
            
            # Use validation helper to check field values
            passed, invalid_values, message = validate_field_values(
                field, actual_values, expected_value, tolerance, contains
            )
            
            field_results.append(create_compliance_record(
                schema_acq_name, in_acq_name, series_name, field,
                expected_value, tolerance, contains, actual_values,
                message, passed
            ))
        
        return field_results
    
    # Process each mapped acquisition
    for schema_acq_name, in_acq_name in session_map.items():
        # Filter the input session for the current acquisition
        in_acq = in_session[in_session["Acquisition"] == in_acq_name]
        
        if in_acq.empty:
            compliance_summary.append({
                "schema acquisition": schema_acq_name,
                "input acquisition": in_acq_name,
                "field": "Acquisition-Level Error",
                "value": None,
                "rule_name": "Acquisition presence",
                "expected": "Specified input acquisition must be present.",
                "message": f"Input acquisition '{in_acq_name}' not found in data.",
                "passed": False,
                "status": ComplianceStatus.NA.value
            })
            continue
        
        # Get acquisition schema
        acquisitions_data = schema_data.get("acquisitions", {})
        schema_acq = acquisitions_data.get(schema_acq_name, {})
        
        # 1. Check field-level compliance
        schema_fields = schema_acq.get("fields", [])
        if schema_fields:
            field_results = _check_field_compliance(
                schema_acq_name, in_acq_name, schema_fields, in_acq
            )
            compliance_summary.extend(field_results)
        
        # 2. Check series-level field compliance
        schema_series = schema_acq.get("series", [])
        for series_def in schema_series:
            series_name = series_def.get("name", "<unnamed>")
            series_fields = series_def.get("fields", [])
            
            if series_fields:
                # Filter data for series matching
                matching_df = in_acq
                
                # Apply series field filters
                for fdef in series_fields:
                    field = fdef["field"]
                    expected = fdef.get("value")
                    tolerance = fdef.get("tolerance")
                    contains = fdef.get("contains")
                    
                    if field in matching_df.columns and expected is not None:
                        # Filter rows that match this field's constraint
                        mask = matching_df[field].apply(
                            lambda x: validate_constraint(x, expected, tolerance, contains)
                        )
                        matching_df = matching_df[mask]
                
                # Check compliance for matching rows
                if not matching_df.empty:
                    series_results = _check_field_compliance(
                        schema_acq_name, in_acq_name, series_fields, matching_df, series_name
                    )
                    compliance_summary.extend(series_results)
                else:
                    # No matching series found - create a single series-level error
                    # Build a description of the series constraints
                    constraints = []
                    for fdef in series_fields:
                        field = fdef["field"]
                        if "value" in fdef:
                            if "tolerance" in fdef:
                                constraints.append(f"{field}={fdef['value']}±{fdef['tolerance']}")
                            else:
                                constraints.append(f"{field}={fdef['value']}")
                        elif "contains" in fdef:
                            constraints.append(f"{field} contains '{fdef['contains']}'")
                    
                    constraint_desc = " AND ".join(constraints) if constraints else "series constraints"
                    field_list = ", ".join([fdef["field"] for fdef in series_fields])
                    
                    compliance_summary.append(create_compliance_record(
                        schema_acq_name, in_acq_name, series_name, field_list,
                        None, None, None,
                        None, f"No matching series found for '{series_name}' ({constraint_desc}).", False,
                        status=ComplianceStatus.NA
                    ))
        
        # 3. Check rule-based compliance if models are available
        if validation_models and schema_acq_name in validation_models:
            model = validation_models[schema_acq_name]
            
            # Ensure the model is instantiated if it's a class
            if isinstance(model, type):
                model = model()
            
            # Validate using the model
            success, errors, passes = model.validate(data=in_acq)
            
            # Record errors
            for error in errors:
                status = ComplianceStatus.NA if "not found" in error.get('message', '').lower() else ComplianceStatus.ERROR
                compliance_summary.append({
                    "schema acquisition": schema_acq_name,
                    "input acquisition": in_acq_name,
                    "field": error['field'],
                    "value": error['value'],
                    "expected": error.get('expected', error.get('rule_message', '')),
                    "message": error['message'],
                    "rule_name": error['rule_name'],
                    "passed": False,
                    "status": status.value
                })
            
            # Record passes
            for passed_test in passes:
                compliance_summary.append({
                    "schema acquisition": schema_acq_name,
                    "input acquisition": in_acq_name,
                    "field": passed_test['field'],
                    "value": passed_test['value'],
                    "expected": passed_test.get('expected', passed_test.get('rule_message', '')),
                    "message": passed_test['message'],
                    "rule_name": passed_test['rule_name'],
                    "passed": True,
                    "status": ComplianceStatus.OK.value
                })
            
            # Raise an error if validation fails and `raise_errors` is True
            if raise_errors and not success:
                raise ValueError(f"Validation failed for acquisition '{in_acq_name}'.")
    
    return compliance_summary

