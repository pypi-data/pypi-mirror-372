import json
from pathlib import Path

import typer
from pydantic import ValidationError
from typing_extensions import Annotated

from . import utils
from .logger import VerbosityLevel, configure_logger, log_error, logger
from .models import latest_dictionary_model, legacy_dictionary_model

bump_dictionary = typer.Typer(
    help="Bump Neurobagel data dictionaries to the latest version of the data dictionary schema.",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_markup_mode="rich",
)


@bump_dictionary.command()
def main(
    data_dictionary: Annotated[
        Path,
        typer.Argument(
            help="Path to the Neurobagel data dictionary JSON file to be updated."
        ),
    ],
    output: Annotated[
        Path,
        typer.Argument(
            help="Path to save the updated data dictionary JSON file."
        ),
    ] = Path("updated_dictionary.json"),
    verbosity: Annotated[
        VerbosityLevel,
        typer.Option(
            "--verbosity",
            "-v",
            callback=configure_logger,
            help="Set the verbosity level of the output. 0 = show errors only; 1 = show errors, warnings, and informational messages; 3 = show all logs, including debug messages.",
        ),
    ] = VerbosityLevel.INFO,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            "-f",
            help="Overwrite the output file if it already exists.",
        ),
    ] = False,
):
    if output.exists() and not overwrite:
        raise typer.Exit(
            typer.style(
                f"Output file {output} already exists. Use --overwrite or -f to overwrite.",
                fg=typer.colors.RED,
            )
        )

    input_dict = utils.load_json(data_dictionary)

    latest_dictionary_schema = (
        latest_dictionary_model.DataDictionary.model_json_schema()
    )
    if not utils.get_validation_errors_for_schema(
        input_dict, latest_dictionary_schema
    ):
        log_error(
            logger,
            "Data dictionary is already up-to-date with the latest schema.",
        )

    try:
        legacy_dictionary_model.DataDictionary.model_validate(input_dict)
    except ValidationError as legacy_schema_validation_errs:
        invalid_cols = {}
        # Below, we customize the user-facing error to avoid printing a large number of non-discriminative
        # validation errors from Pydantic attempts to validate the dict against each possible column type
        for validation_err in legacy_schema_validation_errs.errors():
            # In a validation error, "loc" gives us the location of the error (the first item being the column name key)
            # and "input" gives us the actual offending value (the contents of the column dict).
            # Since a single column can produce multiple validation errors, here we collect each unique offending column once.
            invalid_cols.update(
                {validation_err["loc"][0]: validation_err["input"]}
            )

        invalid_col_err_messages = ""
        for col_name, col_contents in invalid_cols.items():
            invalid_col_err_messages += (
                f" -> {col_name}: {col_contents} "
                + "is not a valid column annotation under the legacy schema\n"
            )
        log_error(
            logger,
            "The data dictionary is not valid against the legacy schema and may be too outdated to upgrade automatically. "
            "Please re-annotate your dataset using the latest version of the annotation tool to continue.\n"
            f"Found {len(invalid_cols)} error(s):\n"
            f"{invalid_col_err_messages}",
        )

    updated_dict = utils.convert_transformation_to_format(input_dict)
    updated_dict = utils.encode_variable_type(updated_dict)

    latest_schema_validation_errs = utils.get_validation_errors_for_schema(
        updated_dict, latest_dictionary_schema
    )
    if latest_schema_validation_errs:
        validation_errs = ""
        for error in latest_schema_validation_errs:
            validation_errs += (
                " -> "
                + ".".join(map(str, error.path))
                + f": {error.message}\n"
            )
        log_error(
            logger,
            "Unexpected validation errors occurred after upgrading the data dictionary to the latest schema.\n"
            f"Found {len(latest_schema_validation_errs)} error(s):\n"
            f"{validation_errs}"
            "Something likely went wrong in the upgrade process on our side. "
            "Please open an issue in https://github.com/neurobagel/bump-dictionary/issues.",
        )

    with open(output, "w", encoding="utf-8") as f:
        json.dump(updated_dict, f, ensure_ascii=False, indent=2)

    logger.info(
        f"Successfully updated data dictionary. Output saved to {output}"
    )
