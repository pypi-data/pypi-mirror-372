"""
Copyright CNRS (https://www.cnrs.fr/index.php/en)
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import logging as l
import typing as h
from pathlib import Path as path_t

from logger_36.config.message import (
    FALLBACK_MESSAGE_WIDTH,
    LEVEL_CLOSING,
    LEVEL_OPENING,
    MESSAGE_MARKER,
    WHERE_SEPARATOR,
)
from logger_36.constant.message import NEXT_LINE_PROLOGUE
from logger_36.constant.record import SHOW_W_RULE_ATTR, WHEN_OR_ELAPSED_ATTR, WHERE_ATTR
from logger_36.constant.rule import (
    DEFAULT_RULE,
    DEFAULT_RULE_LENGTH,
    MIN_HALF_RULE_LENGTH,
    RULE_CHARACTER,
)
from logger_36.extension.line import WrappedLines


class extension_t:
    def __init__(
        self,
        name: str | None,
        message_width: int,
        PreProcessedMessage: h.Callable[[str], str] | None,
    ) -> None:
        """"""
        self.name = name
        self.message_width = message_width
        self.PreProcessedMessage = PreProcessedMessage

        self.__post_init__()

    def __post_init__(self) -> None:
        """"""
        if self.name is None:
            self.name = f"{type(self).__name__}:{hex(id(self))[2:]}"

        if 0 < self.message_width < FALLBACK_MESSAGE_WIDTH:
            self.message_width = FALLBACK_MESSAGE_WIDTH

    @classmethod
    def New(cls, **kwargs) -> h.Self:
        """
        Interest: default arguments, no prescribed argument order, variable argument list.
        """
        raise NotImplementedError

    def MessageFromRecord(
        self, record: l.LogRecord, /, *, rule_color: str | None = None
    ) -> tuple[str, bool]:
        """
        The second returned value is is_not_a_rule.
        """
        message = record.msg  # See logger_36.catalog.handler.README.txt.
        if self.PreProcessedMessage is not None:
            message = self.PreProcessedMessage(message)

        if hasattr(record, SHOW_W_RULE_ATTR):
            return self.Rule(text=message, color=rule_color), False

        if (self.message_width <= 0) or (message.__len__() <= self.message_width):
            if "\n" in message:
                message = NEXT_LINE_PROLOGUE.join(message.splitlines())
        else:
            if "\n" in message:
                lines = WrappedLines(message.splitlines(), self.message_width)
            else:
                lines = WrappedLines([message], self.message_width)
            message = NEXT_LINE_PROLOGUE.join(lines)

        when_or_elapsed = getattr(record, WHEN_OR_ELAPSED_ATTR, None)
        if when_or_elapsed is None:
            return message, True

        if (where := getattr(record, WHERE_ATTR, None)) is None:
            where = ""
        else:
            where = f"{NEXT_LINE_PROLOGUE}{WHERE_SEPARATOR} {where}"

        return (
            f"{when_or_elapsed}"
            f"{LEVEL_OPENING}{record.levelname[0]}{LEVEL_CLOSING} "
            f"{MESSAGE_MARKER} {message}{where}"
        ), True

    def Rule(self, /, *, text: str | None = None, color: str = "black") -> str | h.Any:
        """
        Return type hint h.Any: For Rich, for example.
        """
        if text is None:
            if self.message_width > 0:
                return self.message_width * RULE_CHARACTER
            return DEFAULT_RULE

        if self.message_width > 0:
            target_width = self.message_width
        else:
            target_width = DEFAULT_RULE_LENGTH
        half_rule_length = max(
            (target_width - text.__len__() - 2) // 2, MIN_HALF_RULE_LENGTH
        )
        half_rule = half_rule_length * RULE_CHARACTER

        return f"{half_rule} {text} {half_rule}"

    def EmitMessage(self, message: str, /) -> None:
        """"""
        raise NotImplementedError

    def EmitRule(self, /, *, text: str | None = None, color: str = "black") -> None:
        """"""
        self.EmitMessage(self.Rule(text=text, color=color))


class handler_t(l.Handler, extension_t):
    def __init__(
        self,
        name: str | None,
        message_width: int,
        PreProcessedMessage: h.Callable[[str], str] | None,
        level: int,
        *_,
    ) -> None:
        """"""
        l.Handler.__init__(self)
        extension_t.__init__(self, name, message_width, PreProcessedMessage)
        __post_init__(self, level)


class file_handler_t(l.FileHandler, extension_t):
    def __init__(
        self,
        name: str | None,
        message_width: int,
        PreProcessedMessage: h.Callable[[str], str] | None,
        level: int,
        path: str | path_t | None,
        *_,
    ) -> None:
        """"""
        if path is None:
            raise ValueError("Missing file or folder.")
        if isinstance(path, str):
            path = path_t(path)
        if path.exists():
            raise ValueError(f"File or folder already exists: {path}.")

        l.FileHandler.__init__(self, path)
        extension_t.__init__(self, name, message_width, PreProcessedMessage)
        __post_init__(self, level)


any_handler_t = handler_t | file_handler_t


def __post_init__(handler: any_handler_t, level: int) -> None:
    """"""
    handler.setLevel(level)


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
