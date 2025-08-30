# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations

import ast
import csv
import hashlib
import io
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, replace
from functools import singledispatchmethod
from typing import Any, List, Tuple, Union

from textwizard.utils.errors.errors import (
    CSVValidationError,
    InvalidCSVDelimiterError,
)
from textwizard.utils.wildcard import process_wildcard_words

Row = list[str]


# --------------------------------------------------------------------------- #
# Dialect                                                                     #
# --------------------------------------------------------------------------- #
@dataclass(slots=True, frozen=True)
class CsvDialect:
    """Immutable CSV dialect mirroring `csv` module options."""

    delimiter: str = ","
    quotechar: str = '"'
    escapechar: str | None = None
    doublequote: bool = True
    skipinitialspace: bool = False
    lineterminator: str = "\n"
    quoting: int = csv.QUOTE_MINIMAL

    def _kwargs(self) -> Mapping[str, Any]:
        return {
            "delimiter": self.delimiter,
            "quotechar": self.quotechar,
            "escapechar": self.escapechar,
            "doublequote": self.doublequote,
            "skipinitialspace": self.skipinitialspace,
            "lineterminator": self.lineterminator,
            "quoting": self.quoting,
        }

    def reader(self, text: str):
        return csv.reader(io.StringIO(text), **self._kwargs())

    def writer(self, rows: Iterable[Row]) -> str:
        buf = io.StringIO()
        csv.writer(buf, **self._kwargs()).writerows(rows)
        return buf.getvalue()

    def replace(self, **changes) -> "CsvDialect":
        return replace(self, **changes)


# --------------------------------------------------------------------------- #
# Cleaner                                                                     #
# --------------------------------------------------------------------------- #
class CSVCleaner:

    VALID_DELIMITERS = [",", ";", "|", "\t"]

    def __init__(self, dialect: CsvDialect | None = None) -> None:
        self._dialect = dialect or CsvDialect()
        self._data: str = ""

    @property
    def dialect(self) -> CsvDialect:
        return self._dialect

    @dialect.setter
    def dialect(self, new: CsvDialect) -> None:
        if new.delimiter not in self.VALID_DELIMITERS:
            raise InvalidCSVDelimiterError(
                f"Invalid delimiter {new.delimiter!r}; "
                f"valid choices: {self.VALID_DELIMITERS}"
            )
        self._dialect = new

    @property
    def delimiter(self) -> str:
        return self._dialect.delimiter

    @delimiter.setter
    def delimiter(self, d: str) -> None:
        if d not in self.VALID_DELIMITERS:
            raise InvalidCSVDelimiterError(
                f"Invalid delimiter {d!r}; valid choices: {self.VALID_DELIMITERS}"
            )
        self._dialect = self._dialect.replace(delimiter=d)

    def clean(
        self,
        csv_data: str,
        *,
        dialect: CsvDialect | None = None,
        csv_delimiter: str | None = None,
        **flags,
    ) -> str:
        d = dialect or self._dialect
        if csv_delimiter:
            d = d.replace(delimiter=self._check_delim(csv_delimiter))

        self._validate_csv(csv_data, d)

        self._data = csv_data
        p = {k: v for k, v in flags.items() if v is not None}

        if p.get("csv.trim_whitespace"):
            self._trim_whitespace(d)
        if "csv.remove_columns" in p:
            self._remove_columns(p["csv.remove_columns"], d)
        if "csv.remove_row_index" in p:
            self._remove_row(p["csv.remove_row_index"], d)
        if "csv.remove_values" in p:
            self._remove_values(p["csv.remove_values"], d)
        if p.get("csv.remove_duplicates_rows"):
            self._remove_duplicate_rows()
        if p.get("csv.remove_empty_columns"):
            self._remove_empty_columns(d)
        if p.get("csv.remove_empty_rows"):
            self._remove_empty_rows(d)

        return self._data


    def _check_delim(self, d: str) -> str:
        if d not in self.VALID_DELIMITERS:
            raise InvalidCSVDelimiterError(
                f"Invalid delimiter {d!r}; valid choices: {self.VALID_DELIMITERS}"
            )
        return d

    @staticmethod
    def _coerce_patterns(vals) -> list[str]:
        if isinstance(vals, str):
            txt = vals.strip()
            if txt and txt[0] in "[(":
                for loader in (json.loads, ast.literal_eval):
                    try:
                        return [str(v) for v in loader(txt)]
                    except Exception:
                        pass
            return [txt]
        if isinstance(vals, (list, tuple, set)):
            return [str(v) for v in vals]
        raise TypeError("csv.remove_values expects str/list/tuple/set")

    @staticmethod
    def _validate_csv(text: str, dialect: CsvDialect) -> None:
        rdr = dialect.reader(text)
        try:
            header = next(rdr)
        except StopIteration:
            raise CSVValidationError("CSV is empty") from None
        ncols = len(header)
        for idx, row in enumerate(rdr, start=2):
            if len(row) != ncols:
                raise CSVValidationError(
                    f"Row {idx} has {len(row)} columns; expected {ncols}"
                )

    def _rw(self, dialect: CsvDialect) -> Tuple[csv.reader, csv.writer, io.StringIO]:
        buf = io.StringIO(self._data)
        rdr = csv.reader(buf, **dialect._kwargs())
        out = io.StringIO()
        wtr = csv.writer(out, **dialect._kwargs())
        return rdr, wtr, out


    def _remove_columns(
        self,
        cols: Union[str, int, Iterable[Union[str, int]]],
        dialect: CsvDialect,
    ) -> None:
        if isinstance(cols, (str, int)):
            cols = [cols]

        rdr, wtr, out = self._rw(dialect)
        try:
            header = next(rdr)
        except StopIteration:
            self._data = ""
            return

        n = len(header)
        removed: set[int] = set()
        for spec in cols:
            avail = [i for i in range(n) if i not in removed]
            if isinstance(spec, int):
                if 0 <= spec < n:
                    removed.add(spec)
                continue
            try:
                idx = next(i for i in avail if header[i] == spec)
                removed.add(idx)
            except StopIteration:
                continue

        keep = [i for i in range(n) if i not in removed]
        if not keep:
            self._data = ""
            return

        wtr.writerow([header[i] for i in keep])
        for row in rdr:
            filtered = [row[i] for i in keep]
            if any(cell.strip() for cell in filtered):
                wtr.writerow(filtered)

        first = out.getvalue().splitlines()[0].split(dialect.delimiter)
        blank = all(c.strip().strip('"').strip("'") == "" for c in first)
        self._data = "" if blank else out.getvalue()

    # rows -------------------------------------------------------------------
    @singledispatchmethod
    def _remove_row(self, index, dialect: CsvDialect) -> None:  # noqa: D401
        raise TypeError("Unsupported type for csv.remove_row_index")

    @_remove_row.register
    def _(self, index: int, dialect: CsvDialect) -> None:
        self._remove_rows_core([index], dialect)

    @_remove_row.register
    def _(self, index: Iterable, dialect: CsvDialect) -> None:
        self._remove_rows_core([i for i in index if isinstance(i, int)], dialect)

    def _remove_rows_core(self, indices: List[int], dialect: CsvDialect) -> None:
        to_remove = sorted(set(indices), reverse=True)
        rdr, wtr, buf = self._rw(dialect)
        for i, row in enumerate(rdr):
            if i not in to_remove:
                wtr.writerow(row)
        self._data = buf.getvalue()

    # values -----------------------------------------------------------------
    def _remove_values(self, vals, dialect: CsvDialect) -> None:
        pats = self._coerce_patterns(vals)
        if not any(ch in p for p in pats for ch in "*?[]"):
            to_remove = set(pats)
        else:
            to_remove = process_wildcard_words(
                self._data, pats, csv_delimiter=dialect.delimiter
            )

        delim = dialect.delimiter
        out = []
        for rec in self._data.splitlines():
            buf, cells, in_q, i = [], [], False, 0
            while i < len(rec):
                ch = rec[i]
                if ch == dialect.quotechar and (i == 0 or rec[i - 1] != "\\"):
                    in_q = not in_q
                if ch == delim and not in_q:
                    raw = "".join(buf)
                    cells.append("" if raw in to_remove else raw)
                    buf.clear()
                else:
                    buf.append(ch)
                i += 1
            raw = "".join(buf)
            cells.append("" if raw in to_remove else raw)
            out.append(delim.join(cells))
        self._data = "\n".join(out) + ("\n" if out else "")

    # duplicates --------------------------------------------------------------
    def _remove_duplicate_rows(self) -> None:
        lines = self._data.splitlines(keepends=True)
        seen, out = set(), []
        for line in lines:
            h = hashlib.blake2b(
                line.encode("utf-8", "surrogatepass"), digest_size=8
            ).digest()
            if h not in seen:
                seen.add(h)
                out.append(line)
        self._data = "".join(out)

    # whitespace --------------------------------------------------------------
    def _trim_whitespace(self, dialect: CsvDialect) -> None:
        delim, quote = dialect.delimiter, dialect.quotechar
        records, buf, in_q = [], [], False
        for ch in self._data:
            if ch == quote and (not buf or buf[-1] != "\\"):
                in_q = not in_q
            if ch == "\n" and not in_q:
                records.append("".join(buf))
                buf.clear()
            else:
                buf.append(ch)
        if buf:
            records.append("".join(buf))

        out = []
        for rec in records:
            cells, buf, in_q, i = [], [], False, 0
            while i < len(rec):
                ch = rec[i]
                if ch == quote and (i == 0 or rec[i - 1] != "\\"):
                    in_q = not in_q
                if ch == delim and not in_q:
                    cells.append("".join(buf).strip(" \t"))
                    buf.clear()
                    i += 1
                    while i < len(rec) and rec[i] in " \t" and rec[i] != delim:
                        i += 1
                    continue
                buf.append(ch)
                i += 1
            cells.append("".join(buf).strip(" \t"))
            out.append(delim.join(cells))

        self._data = "\n".join(out) + ("\n" if out else "")

    # empty columns -----------------------------------------------------------
    def _remove_empty_columns(self, dialect: CsvDialect) -> None:
        rdr, wtr, out = self._rw(dialect)
        rows = list(rdr)
        if not rows:
            return
        keep = [any(cell.strip() for cell in col) for col in zip(*rows)]
        for row in rows:
            wtr.writerow([cell for i, cell in enumerate(row) if keep[i]])
        self._data = out.getvalue()

    # empty rows --------------------------------------------------------------
    def _remove_empty_rows(self, dialect: CsvDialect) -> None:
        lines, new = self._data.splitlines(keepends=True), []
        for line in lines:
            raw = line.rstrip("\r\n")
            if not raw:
                continue
            if dialect.quotechar in raw:
                new.append(line)
                continue
            row = next(csv.reader([raw], **dialect._kwargs()))
            if any(cell.strip() for cell in row):
                new.append(line)
        self._data = "".join(new)
        if self._data and not self._data.endswith("\n"):
            self._data += "\n"
