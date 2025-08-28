# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import annotations
from typing import Any


class TextWizardError(Exception):
    """
    Base class for all errors in the TextWizard library.
    """

    def __init__(self, message: str, param_name: str = None, value: Any = None):
        self.param_name = param_name
        self.value = value
        super().__init__(message)

    def __str__(self):
        base_message = super().__str__()
        if self.param_name and self.value is not None:
            return f"{base_message} (Parameter: {self.param_name}, Value: {self.value})"
        return base_message


class InvalidInputError(TextWizardError):
    """
    Raised when an input parameter is invalid.
    """

    def __init__(self, param_name: str, expected: str, received: Any):
        message = (
            f"Invalid input for '{param_name}': expected {expected}, got {type(received).__name__} "
            f"(value={received})."
        )
        super().__init__(message, param_name, received)


class MissingExtensionError(TextWizardError):
    """
    Raised when the file extension is missing for byte input.
    """

    def __init__(self):
        super().__init__("The 'extension' parameter must be specified for byte input.")


class UnsupportedFileTypeError(TextWizardError):
    """
    Raised when an unsupported file type is used.
    """

    def __init__(self, file_type: str):
        super().__init__(f"Unsupported file type: {file_type}.")


class ValidationError(TextWizardError):
    """
    Raised for generic validation errors.
    """

    def __init__(self, param_name: str, issue: str, value: Any = None):
        message = f"Validation error for '{param_name}': {issue}."
        super().__init__(message, param_name, value)


class InternalError(TextWizardError):
    """
    Raised for unexpected internal errors.
    """

    def __init__(self, original_exception: Exception):
        message = f"{str(original_exception)}"
        super().__init__(message)
        self.original_exception = original_exception


class DocFileAsBytesError(Exception):
    """
    Raised when a .doc file is passed as bytes instead of a path.
    """

    def __init__(self, message=".doc files must be passed as paths, not as bytes."):
        super().__init__(message)


class UnsupportedExtensionError(TextWizardError):
    """
    Raised when an unsupported file extension is encountered.
    """

    def __init__(self, extension):
        self.extension = extension
        self.supported_extensions = [
            "pdf",
            "doc",
            "docx",
            "xlsx",
            "xls",
            "txt",
            "csv",
            "html",
            "htm",
            "json",
            "tif",
            "tiff",
            "jpg",
            "jpeg",
            "png",
            "gif",
        ]
        super().__init__(
            f"The file extension '{self.extension}' is not supported. "
            f"Supported extensions are: {', '.join(self.supported_extensions)}."
        )
class UnsupportedExtensionAzureError(TextWizardError):
    """
    Raised when an unsupported file extension is encountered.
    """

    def __init__(self, extension):
        self.extension = extension
        self.supported_extensions = [
            "pdf",
            "docx",
            "tif",
            "tiff",
            "jpg",
            "jpeg",
            "png",
            "BMP"
        ]
        super().__init__(
            f"The file extension '{self.extension}' is not supported. "
            f"Supported extensions are: {', '.join(self.supported_extensions)}."
        )


class FileNotFoundCustomError(TextWizardError):
    """
    Raised when a file cannot be found or opened.
    """

    def __init__(self, file_path):
        super().__init__(f"File '{file_path}' does not exist.")


class AntiwordNotFoundError(Exception):
    """
    Raised when the Antiword executable is not found or not installed.
    """

    def __init__(self, message="Antiword is not installed or not in PATH."):
        super().__init__(message)


class ExtractionError(Exception):
    """
    Raised for errors during text extraction from files.
    """

    def __init__(self, message):
        super().__init__(message)


class DocxFileError(Exception):
    """
    Raised when there is an issue with the .docx file.
    """

    def __init__(self, message="Error processing the .docx file."):
        super().__init__(message)


class ImageProcessingError(Exception):
    """
    Raised when there is an issue processing an image file.
    """

    def __init__(self, message="Error processing the image file."):
        super().__init__(message)


class HtmlFileError(Exception):
    """
    Raised when there is an issue with the HTML content or file.
    """

    def __init__(self, message="Invalid HTML content or file."):
        super().__init__(message)


class JsonFileError(Exception):
    """
    Raised when there is an issue with the JSON content or file.
    """

    def __init__(self, message="Invalid JSON content or file."):
        super().__init__(message)


class TxtFileError(Exception):
    """
    Raised when a text file cannot be decoded using standard encodings.
    """

    def __init__(self, message="Failed to decode the text file."):
        super().__init__(message)


class OCRNotConfiguredError(Exception):
    """
    Raised when Tesseract OCR is not properly configured or installed.
    """

    def __init__(
        self, message="Tesseract OCR is not properly configured or installed."
    ):
        super().__init__(message)


class FileFormatError(Exception):
    """
    Raised when the file format is not supported or invalid.
    """

    def __init__(self, message="The file format is not supported or invalid."):
        super().__init__(message)


class FileProcessingError(Exception):
    """
    Raised when an error occurs during the processing of a file.
    """

    def __init__(self, message="An error occurred while processing the file."):
        super().__init__(message)


class PatternNotFoundError(Exception):
    def __init__(self, pattern_name):
        super().__init__(
            f"The pattern '{pattern_name}' does not exist in PatternManager."
        )


class InvalidTextInputError(Exception):
    def __init__(self, value):
        super().__init__(
            f"Invalid text input: expected a non-empty string, got {type(value).__name__}."
        )


class CleanerConfigurationError(Exception):
    def __init__(self, issue):
        super().__init__(f"Configuration error in Cleaner: {issue}.")


class HTMLPlaceholderError(Exception):
    """
    Custom exception for handling HTML placeholder errors.

    Raised when an issue occurs during the replacement or restoration
    of HTML placeholders, such as collisions or missing placeholders.

    Args:
        message (str): Description of the error.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"HTMLPlaceholderError: {self.message}"


class XMLPlaceholderError(Exception):
    """
    Custom exception for handling XML placeholder errors.

    Raised when an issue occurs during the replacement or restoration
    of XML placeholders, such as collisions or missing placeholders.

    Args:
        message (str): Description of the error.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"XMLPlaceholderError: {self.message}"


class PlaceholderError(TextWizardError):
    """
    Raised when a placeholder is not removed from the text after processing.

    Attributes:
        placeholder (str): The placeholder that caused the error.
        message (str): Explanation of the error.
    """

    def __init__(self, placeholder, message=None):
        self.placeholder = placeholder
        self.message = (
            message or f"Placeholder '{placeholder}' was not removed from the text."
        )
        super().__init__(self.message)


class CSVValidationError(Exception):
    """
    Raised when a validation error occurs in CSV operations.

    Attributes:
        message (str): Description of the validation error.
    """

    def __init__(self, message="CSV validation error occurred"):
        super().__init__(message)
        self.message = message


class InvalidCSVDelimiterError(CSVValidationError):
    """
    Raised when an invalid CSV delimiter is provided.

    Attributes:
        delimiter (str): The invalid delimiter that was provided.
        message (str): Description of the error.
    """

    def __init__(self, delimiter, message=None):
        self.delimiter = delimiter
        if message is None:
            message = f"Invalid CSV delimiter: '{delimiter}' is not supported."
        super().__init__(message)


class ColumnNotFoundError(TextWizardError):
    """
    Raised when a specified column name does not exist in the CSV header.
    """
    def __init__(self, column_name):
        super().__init__(f"Column '{column_name}' does not exist in the CSV header.")
        self.column_name = column_name


class InvalidPagesError(TextWizardError):
    """
    Raised when the `pages` argument is not an int or a list of ints.
    """
    def __init__(self, pages):
        super().__init__(
            "Parameter `pages` must be an int or a list of ints ≥ 1.",
            "pages",
            pages,
        )
        
class UnsupportedCountImageError(TextWizardError):
    """
    Raised when the provided file is not a PDF or DOCX
    for embedded‐image counting.
    """
    def __init__(self, ext: str | None):
        supported = ["pdf", "docx"]
        super().__init__(
            f"The extension '{ext}' is not supported for image counting. "
            f"Supported extensions: {', '.join(supported)}.",
            "extension",
            ext
        )
        
class AWSCredentialsError(TextWizardError):
    """
    Raised when AWS OCR backend is selected but required credentials are missing.
    """
    def __init__(self, missing: list[str]):
        msg = f"Missing AWS OCR configuration parameters: {missing}"
        super().__init__(msg, param_name="ocr_backend", value="aws")

class AzureCredentialsError(TextWizardError):
    """
    Raised when Azure OCR backend is selected but endpoint or key are missing.
    """
    def __init__(self):
        msg = "Azure OCR requires both 'azure_endpoint' and 'azure_key'."
        super().__init__(msg, param_name="ocr_backend", value="azure")

class DictionaryUnsupportedError(Exception):
    pass

class DictionaryUnavailableError(Exception):
    def __init__(self, url: str):
        super().__init__(f"Dictionary asset not available at: {url}")
        self.url = url

class DictionaryFileNotFoundError(Exception):
    def __init__(self, path: str):
        super().__init__(f"Dictionary file not found: {path}")
        self.path = path

class JiebaMissingError(Exception):
    pass