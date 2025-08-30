from typing import TypeAlias

import yaml.parser
import yaml.scanner
from pydantic import ValidationError

ValidationErrorType: TypeAlias = ValidationError | yaml.parser.ParserError | yaml.scanner.ScannerError | ValueError
