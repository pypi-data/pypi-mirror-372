"""
Copyright CNRS (https://www.cnrs.fr/index.php/en)
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import json
import logging as l
import typing as h

from logger_36.type.handler import handler_t as base_t

formats_h = h.Literal["json", "message", "raw"]


class memory_handler_t(base_t):
    def __init__(
        self, name: str | None, message_width: int, level: int, format_: formats_h
    ) -> None:
        """"""
        assert format_ in h.get_args(formats_h)

        base_t.__init__(self, name, message_width, None, level)

        self.format_ = format_
        self.records = []

    @classmethod
    def New(
        cls,
        /,
        *,
        name: str | None = None,
        message_width: int = -1,
        level: int = l.NOTSET,
        format_: formats_h = "message",
        **_,
    ) -> h.Self:
        """"""
        return cls(name, message_width, level, format_)

    def emit(self, record: l.LogRecord, /) -> None:
        """"""
        level = record.levelno

        if self.format_ == "raw":
            is_not_a_rule = True
        elif self.format_ == "message":
            record, is_not_a_rule = self.MessageFromRecord(record)
        else:
            record = json.dumps(record.__dict__)
            is_not_a_rule = True

        self.records.append((level, record, is_not_a_rule))

    def EmitMessage(self, message: str, /) -> None:
        """"""
        if self.format_ == "message":
            message_key = "msg"
        else:
            message_key = "message"
        record = l.makeLogRecord(
            {"name": "<UNKNOWN LOGGER>", "levelno": l.INFO, message_key: message}
        )
        self.emit(record)


"""
COPYRIGHT NOTICE

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

SEE LICENCE NOTICE: file README-LICENCE-utf8.txt at project source root.
"""
