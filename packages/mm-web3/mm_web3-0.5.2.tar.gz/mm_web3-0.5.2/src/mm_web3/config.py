import sys
import tomllib
from pathlib import Path
from typing import Any, NoReturn, Self, TypeVar
from zipfile import ZipFile

import mm_print
from mm_result import Result
from pydantic import BaseModel, ConfigDict, ValidationError

T = TypeVar("T", bound="Web3CliConfig")


class Web3CliConfig(BaseModel):
    """Base configuration class for cryptocurrency CLI tools.

    Provides TOML file loading with optional ZIP archive support,
    validation error handling, and debug printing capabilities.
    """

    model_config = ConfigDict(extra="forbid")

    def print_and_exit(self, exclude: set[str] | None = None, count: set[str] | None = None) -> NoReturn:
        """Print config as JSON and exit the program.

        Args:
            exclude: Fields to exclude from output
            count: Fields to show as length instead of full content
        """
        data = self.model_dump(exclude=exclude)
        if count:
            for k in count:
                data[k] = len(data[k])
        mm_print.json(data)
        sys.exit(0)

    @classmethod
    def read_toml_config_or_exit(cls, config_path: Path, zip_password: str = "") -> Self:  # nosec
        """Read TOML config file, exit on error.

        Args:
            config_path: Path to TOML file or ZIP archive
            zip_password: Password for encrypted ZIP archives

        Returns:
            Validated config instance
        """
        res: Result[Self] = cls.read_toml_config(config_path, zip_password)
        if res.is_ok():
            return res.unwrap()
        cls._print_error_and_exit(res)

    @classmethod
    async def read_toml_config_or_exit_async(cls, config_path: Path, zip_password: str = "") -> Self:  # nosec
        """Read TOML config file with async validation, exit on error.

        Args:
            config_path: Path to TOML file or ZIP archive
            zip_password: Password for encrypted ZIP archives

        Returns:
            Validated config instance
        """
        res: Result[Self] = await cls.read_toml_config_async(config_path, zip_password)
        if res.is_ok():
            return res.unwrap()
        cls._print_error_and_exit(res)

    @classmethod
    def _load_toml_data(cls, config_path: Path, zip_password: str = "") -> dict[str, Any]:  # nosec
        """Load TOML data from file or ZIP archive.

        Args:
            config_path: Path to TOML file or ZIP archive
            zip_password: Password for encrypted ZIP archives

        Returns:
            Parsed TOML data as dictionary
        """
        config_path = config_path.expanduser()
        if config_path.name.endswith(".zip"):
            return tomllib.loads(read_text_from_zip_archive(config_path, password=zip_password))
        with config_path.open("rb") as f:
            return tomllib.load(f)

    @classmethod
    def read_toml_config(cls, config_path: Path, zip_password: str = "") -> Result[Self]:  # nosec
        """Read and validate TOML config file.

        Args:
            config_path: Path to TOML file or ZIP archive
            zip_password: Password for encrypted ZIP archives

        Returns:
            Result containing validated config or error details
        """
        try:
            data = cls._load_toml_data(config_path, zip_password)
            return Result.ok(cls(**data))
        except ValidationError as e:
            return Result.err(("validator_error", e), extra={"errors": e.errors()})
        except Exception as e:
            return Result.err(e)

    @classmethod
    async def read_toml_config_async(cls, config_path: Path, zip_password: str = "") -> Result[Self]:  # nosec
        """Read and validate TOML config file with async validators.

        Use this method when your config has async model validators that
        need to perform network requests or database queries.

        Args:
            config_path: Path to TOML file or ZIP archive
            zip_password: Password for encrypted ZIP archives

        Returns:
            Result containing validated config or error details
        """
        try:
            data = cls._load_toml_data(config_path, zip_password)
            model = await cls.model_validate(data)  # type: ignore[misc]
            return Result.ok(model)
        except ValidationError as e:
            return Result.err(("validator_error", e), extra={"errors": e.errors()})
        except Exception as e:
            return Result.err(e)

    @classmethod
    def _print_error_and_exit(cls, res: Result[Any]) -> NoReturn:
        """Print validation errors and exit with status code 1.

        Args:
            res: Failed Result containing error information
        """
        if res.error == "validator_error" and res.extra:
            mm_print.plain("config validation errors")
            for e in res.extra["errors"]:
                loc = e["loc"]
                field = ".".join(str(lo) for lo in loc) if len(loc) > 0 else ""
                mm_print.plain(f"{field} {e['msg']}")
        else:
            mm_print.plain(f"can't parse config file: {res.error} {res.extra}")
        sys.exit(1)


def read_text_from_zip_archive(zip_archive_path: Path, filename: str | None = None, password: str | None = None) -> str:
    """Read text content from ZIP archive.

    Args:
        zip_archive_path: Path to ZIP archive
        filename: Specific file to read (first file if None)
        password: Archive password if encrypted

    Returns:
        Decoded text content of the file
    """
    with ZipFile(zip_archive_path) as zipfile:
        if filename is None:
            filename = zipfile.filelist[0].filename
        return zipfile.read(filename, pwd=password.encode() if password else None).decode()
