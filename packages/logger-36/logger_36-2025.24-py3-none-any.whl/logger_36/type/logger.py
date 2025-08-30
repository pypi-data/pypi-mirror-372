"""
Copyright CNRS (https://www.cnrs.fr/index.php/en)
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import inspect as e
import logging as l
import sys as s
import textwrap as text
import threading as thrd
import traceback as tcbk
import types as t
import typing as h
from datetime import date as date_t
from datetime import datetime as date_time_t
from pathlib import Path as path_t
from traceback import TracebackException as traceback_t

from logger_36.catalog.config.optional import (
    MEMORY_MEASURE_ERROR,
    MEMORY_MEASURE_IS_AVAILABLE,
    MISSING_RICH_MESSAGE,
    RICH_IS_AVAILABLE,
)
from logger_36.catalog.handler.console import console_handler_t
from logger_36.catalog.handler.file import file_handler_t
from logger_36.config.issue import ISSUE_CONTEXT_END, ISSUE_CONTEXT_SEPARATOR
from logger_36.config.message import (
    DATE_FORMAT,
    ELAPSED_TIME_SEPARATOR,
    LONG_ENOUGH,
    TIME_FORMAT,
    WHERE_SEPARATOR,
)
from logger_36.constant.date_time import DATE_ORIGIN, DATE_TIME_ORIGIN
from logger_36.constant.generic import NOT_PASSED
from logger_36.constant.issue import ISSUE_LEVEL_SEPARATOR, ORDER, order_h
from logger_36.constant.logger import WARNING_LOGGER_NAME, WARNING_TYPE_COMPILED_PATTERN
from logger_36.constant.memory import UNKNOWN_MEMORY_USAGE
from logger_36.constant.message import LINE_INDENT, TIME_LENGTH_m_1, expected_op_h
from logger_36.constant.path import USER_FOLDER, LAUNCH_ROOT_FILE_relative
from logger_36.constant.record import SHOW_W_RULE_ATTR, SHOW_WHERE_ATTR
from logger_36.extension.record import RecordLocation
from logger_36.task.format.message import MessageWithActualExpected
from logger_36.task.measure.chronos import ElapsedTime
from logger_36.task.measure.memory import CurrentUsage as CurrentMemoryUsage
from logger_36.type.handler import extension_t as handler_extension_t
from logger_36.type.handler import handler_h as base_handler_h
from logger_36.type.issue import NewIssue, issue_t

if RICH_IS_AVAILABLE:
    from logger_36.catalog.handler.console_rich import console_rich_handler_t
else:
    from logger_36.catalog.handler.console import (
        console_handler_t as console_rich_handler_t,
    )

base_t = l.Logger

logger_handle_raw_h = h.Callable[[l.LogRecord], None]
logger_handle_with_self_h = h.Callable[[l.Logger, l.LogRecord], None]
logger_handle_h = logger_handle_raw_h | logger_handle_with_self_h


@d.dataclass(slots=True, repr=False, eq=False)
class logger_t(base_t):
    """
    intercepted_wrn_handle: When warning interception is on, this stores the original
        "handle" method of the Python warning logger.

    _should_activate_log_interceptions: Loggers instantiated after a logger_t logger
    will be missed by an early call of ToggleLogInterceptions. Therefore, passing True
    for activate_log_interceptions only sets _should_activate_log_interceptions to True,
    which is later checked in AddHandler to effectively call ToggleLogInterceptions.
    """

    exit_on_error: bool = False  # Implies exit_on_critical.
    exit_on_critical: bool = False
    should_monitor_memory_usage: bool = False

    history: dict[date_time_t, str] = d.field(init=False, default_factory=dict)
    n_events: dict[int, int] = d.field(init=False, default_factory=dict)

    last_message_now: date_time_t = d.field(init=False, default=DATE_TIME_ORIGIN)
    last_message_date: date_t = d.field(init=False, default=DATE_ORIGIN)
    memory_usages: list[tuple[str, int]] = d.field(init=False, default_factory=list)
    context_levels: list[str] = d.field(init=False, default_factory=list)
    staged_issues: list[issue_t] = d.field(init=False, default_factory=list)
    intercepted_wrn_handle: logger_handle_h | None = d.field(init=False, default=None)
    intercepted_log_handles: dict[str, logger_handle_h] = d.field(
        init=False, default_factory=dict
    )
    intercepts_exceptions: bool = d.field(init=False, default=False)

    # Used only until the first handler is added (see AddHandler).
    _should_activate_log_interceptions: bool = d.field(init=False, default=False)

    name_: d.InitVar[str | None] = None
    level_: d.InitVar[int] = l.NOTSET
    activate_wrn_interceptions: d.InitVar[bool] = True
    activate_log_interceptions: d.InitVar[bool] = True
    activate_exc_interceptions: d.InitVar[bool] = True

    @property
    def formatted_history(self) -> str:
        """"""
        FormattedEntry = lambda _: f"{_[0]}: {_[1].replace('\n', '↲ ')}"
        return "\n".join(map(FormattedEntry, self.history.items()))

    @property
    def intercepts_warnings(self) -> bool:
        """"""
        return self.intercepted_wrn_handle is not None

    @property
    def intercepts_logs(self) -> bool:
        """"""
        return self.intercepted_log_handles.__len__() > 0

    @property
    def has_staged_issues(self) -> bool:
        """"""
        return self.staged_issues.__len__() > 0

    @property
    def n_staged_issues(self) -> int:
        """"""
        return self.staged_issues.__len__()

    @property
    def max_memory_usage(self) -> int:
        """"""
        if self.memory_usages.__len__() > 0:
            return max(tuple(zip(*self.memory_usages))[1])
        return UNKNOWN_MEMORY_USAGE

    @property
    def max_memory_usage_full(self) -> tuple[str, int]:
        """"""
        if self.memory_usages.__len__() > 0:
            where_s, usages = zip(*self.memory_usages)
            max_usage = max(usages)

            return where_s[usages.index(max_usage)], max_usage

        return "?", UNKNOWN_MEMORY_USAGE

    def __post_init__(
        self,
        name_: str | None,
        level_: int,
        activate_wrn_interceptions: bool,
        activate_log_interceptions: bool,
        activate_exc_interceptions: bool,
    ) -> None:
        """"""
        if name_ is None:
            name_ = f"{type(self).__name__}:{hex(id(self))[2:]}"

        self.history[date_time_t.now()] = (
            f'Logger "{name_}" instantiation for "{LAUNCH_ROOT_FILE_relative}"'
        )

        base_t.__init__(self, name_)
        self.setLevel(level_)
        self.propagate = False  # Part of base_t.

        if self.exit_on_error:
            self.exit_on_critical = True

        for level_id in l.getLevelNamesMapping().values():
            self.n_events[level_id] = 0

        if activate_wrn_interceptions:
            self.ToggleWarningInterceptions(True)
        if activate_log_interceptions:
            self._should_activate_log_interceptions = True
        if activate_exc_interceptions:
            self.ToggleExceptionInterceptions(True)

        if self.should_monitor_memory_usage:
            self.ActivateMemoryUsageMonitoring()

    def handle(self, record: l.LogRecord, /) -> None:
        """"""
        elapsed_time, now = ElapsedTime(should_return_now=True)

        if (date := now.date()) != self.last_message_date:
            self._AcknowledgeDateChange(date)

        # When.
        if now - self.last_message_now > LONG_ENOUGH:
            w_or_e = now.strftime(TIME_FORMAT)
        else:
            w_or_e = f"{ELAPSED_TIME_SEPARATOR}{elapsed_time:.<{TIME_LENGTH_m_1}}"
        record.when_or_elapsed = w_or_e
        self.last_message_now = now

        # Where.
        should_show_where = getattr(record, SHOW_WHERE_ATTR, record.levelno != l.INFO)
        if should_show_where or self.should_monitor_memory_usage:
            where = RecordLocation(record, should_show_where)
        else:
            where = None

        # What.
        if not isinstance(record.msg, str):
            record.msg = str(record.msg)

        base_t.handle(self, record)
        self.n_events[record.levelno] += 1

        if self.should_monitor_memory_usage:
            self.memory_usages.append((where, CurrentMemoryUsage()))

        if (self.exit_on_critical and (record.levelno is l.CRITICAL)) or (
            self.exit_on_error and (record.levelno is l.ERROR)
        ):
            # Also works if self.exit_on_error and record.levelno is l.CRITICAL since
            # __post_init__ set self.exit_on_critical if self.exit_on_error.
            s.exit(1)

    def _AcknowledgeDateChange(self, date: date_t, /) -> None:
        """"""
        self.last_message_date = date

        record = l.makeLogRecord(
            {
                "name": self.name,
                "levelno": l.INFO,  # For management by logging.Logger.handle.
                "msg": f"DATE: {date.strftime(DATE_FORMAT)}",
                SHOW_W_RULE_ATTR: True,
            }
        )
        base_t.handle(self, record)

    def ResetEventCounts(self) -> None:
        """"""
        for level_id in self.n_events:
            self.n_events[level_id] = 0

    def ToggleWarningInterceptions(self, state: bool, /) -> None:
        """"""
        if state:
            if self.intercepts_warnings:
                return

            logger = l.getLogger(WARNING_LOGGER_NAME)
            self.intercepted_wrn_handle = logger.handle
            logger.handle = t.MethodType(_HandleForWarnings(self), logger)

            l.captureWarnings(True)
            self.history[date_time_t.now()] = "Warning Interception: ON"
        else:
            if not self.intercepts_warnings:
                return

            logger = l.getLogger(WARNING_LOGGER_NAME)
            logger.handle = self.intercepted_wrn_handle
            self.intercepted_wrn_handle = None

            l.captureWarnings(False)
            self.history[date_time_t.now()] = "Warning Interception: OFF"

    def ToggleLogInterceptions(self, state: bool, /) -> None:
        """"""
        if state:
            if self._should_activate_log_interceptions or self.intercepts_logs:
                return

            # Note: Alternative to self.manager is logging.root.manager.
            all_loggers_names_but_root = self.manager.loggerDict.keys()
            all_loggers = [l.getLogger()] + [
                l.getLogger(_nme)
                for _nme in all_loggers_names_but_root
                if _nme not in (self.name, WARNING_LOGGER_NAME)
            ]
            for logger in all_loggers:
                self.intercepted_log_handles[logger.name] = logger.handle
                logger.handle = t.MethodType(
                    _HandleForInterceptions(logger, self), logger
                )

            intercepted = sorted(self.intercepted_log_handles.keys())
            if intercepted.__len__() > 0:
                as_str = ", ".join(intercepted)
                self.history[date_time_t.now()] = (
                    f"Now Intercepting LOGs from: {as_str}"
                )
        else:
            if self._should_activate_log_interceptions:
                self._should_activate_log_interceptions = False
                return

            if not self.intercepts_logs:
                return

            for name, handle in self.intercepted_log_handles.items():
                logger = l.getLogger(name)
                logger.handle = handle
            self.intercepted_log_handles.clear()
            self.history[date_time_t.now()] = "Log Interception: OFF"

    def ToggleExceptionInterceptions(self, state: bool, /) -> None:
        """"""
        if state:
            if self.intercepts_exceptions:
                return

            s.excepthook = self.DealWithException
            thrd.excepthook = self.DealWithExceptionInThread
            self.intercepts_exceptions = True
            self.history[date_time_t.now()] = "Exception Interception: ON"
        else:
            if not self.intercepts_exceptions:
                return

            s.excepthook = s.__excepthook__
            thrd.excepthook = thrd.__excepthook__
            self.intercepts_exceptions = False
            self.history[date_time_t.now()] = "Exception Interception: OFF"

    def ActivateMemoryUsageMonitoring(self) -> None:
        """"""
        if MEMORY_MEASURE_IS_AVAILABLE:
            # Useless if called from __post_init__.
            self.should_monitor_memory_usage = True
            self.history[date_time_t.now()] = (
                f'Memory usage monitoring activated for logger "{self.name}"'
            )
        else:
            self.should_monitor_memory_usage = False
            self.error(MEMORY_MEASURE_ERROR)

    def AddHandler(
        self,
        handler_t_or_handler: type[base_handler_h]
        | base_handler_h
        | l.Handler
        | l.FileHandler,
        /,
        *,
        name: str | None = None,
        level: int = l.INFO,
        message_width: int = -1,
        **kwargs,
    ) -> None:
        """
        Silently ignores re-holding request after un-holding.
        """
        if self._should_activate_log_interceptions:
            # Turn _should_activate_log_interceptions off before calling
            # ToggleLogInterceptions because it checks it.
            self._should_activate_log_interceptions = False
            self.ToggleLogInterceptions(True)

        if isinstance(handler_t_or_handler, type):
            handler = handler_t_or_handler.New(
                name=name, message_width=message_width, level=level, **kwargs
            )
        else:
            handler = handler_t_or_handler
        base_t.addHandler(self, handler)

        path = getattr(handler, "baseFilename", "")
        if isinstance(path, path_t) or (path.__len__() > 0):
            path = f"\nPath: {path}"
        self.history[date_time_t.now()] = (
            f'New handler "{handler.name}" of type "{type(handler).__name__}" and '
            f"level {handler.level}={l.getLevelName(handler.level)}{path}"
        )

    def MakeMonochrome(self) -> None:
        """"""
        self.AddHandler(console_handler_t)

    def MakeRich(self, *, alternating_logs: int = 0) -> None:
        """"""
        if RICH_IS_AVAILABLE:
            handler_kwargs = {"alternating_logs": alternating_logs}
        else:
            handler_kwargs = {}
            self.error(MISSING_RICH_MESSAGE)

        self.AddHandler(console_rich_handler_t, **handler_kwargs)

    def MakePermanent(self, path: str | path_t, /) -> None:
        """"""
        self.AddHandler(file_handler_t, path=path)

    def __call__(self, *args, **kwargs) -> None:
        """
        For a print-like calling for print-based debugging.
        """
        separator = kwargs.get("separator", " ")

        frame = e.stack(context=0)[1][0]  # 1=caller.
        details = e.getframeinfo(frame, context=0)
        path = path_t(details.filename)
        if path.is_relative_to(USER_FOLDER):
            path = path.relative_to(USER_FOLDER)
        where = f"{str(path.with_suffix(''))}.{details.function}.{details.lineno}"

        self.info(separator.join(map(str, args)) + f"\n{WHERE_SEPARATOR} " + where)

    def Log(
        self,
        message: str,
        /,
        *,
        level: int | str = l.ERROR,
        actual: h.Any = NOT_PASSED,
        expected: h.Any | None = None,
        expected_is_choices: bool = False,
        expected_op: expected_op_h = "=",
        with_final_dot: bool = True,
    ) -> None:
        """"""
        if isinstance(level, str):
            level = l.getLevelNamesMapping()[level.upper()]
        message = MessageWithActualExpected(
            message,
            actual=actual,
            expected=expected,
            expected_is_choices=expected_is_choices,
            expected_op=expected_op,
            with_final_dot=with_final_dot,
        )
        self.log(level, message)

    def LogAsIs(self, message: str, /, *, indented: bool = False) -> None:
        """"""
        if indented:
            message = text.indent(message, LINE_INDENT)

        for handler in self.handlers:
            EmitMessage = getattr(
                handler, handler_extension_t.EmitMessage.__name__, None
            )
            if EmitMessage is not None:
                EmitMessage(message)

    info_raw = LogAsIs  # To follow the convention of the logging methods info, error...

    def LogException(
        self,
        exception: Exception,
        /,
        *,
        level: int | str = l.ERROR,
        should_remove_caller: bool = False,
    ) -> None:
        """"""
        if isinstance(level, str):
            level = l.getLevelNamesMapping()[level.upper()]
        lines = tcbk.format_exception(exception)
        if should_remove_caller:
            message = "\n".join(lines[:1] + lines[2:])
        else:
            # TODO: Explain:
            #     - Why it's not: "\n".join(lines)?
            #     - Why adding exception name here and not when removing caller?
            formatted = "".join(lines)
            message = f"Exception of type {type(exception).__name__}\n----\n{formatted}"
        self.log(level, message, extra={SHOW_WHERE_ATTR: False})

    def DealWithException(self, _, exc_value, exc_traceback, /) -> None:
        """"""
        exception = exc_value.with_traceback(exc_traceback)
        self.LogException(exception, level=l.CRITICAL)
        s.exit(1)

    def DealWithExceptionInThread(
        self, exc_type, exc_value, exc_traceback, _, /
    ) -> None:
        """"""
        self.DealWithException(exc_type, exc_value, exc_traceback)

    def DisplayRule(
        self, /, *, message: str | None = None, color: str = "white"
    ) -> None:
        """"""
        for handler in self.handlers:
            EmitRule = getattr(handler, handler_extension_t.EmitRule.__name__, None)
            if EmitRule is not None:
                EmitRule(text=message, color=color)

    def AddContextLevel(self, new_level: str, /) -> None:
        """"""
        self.context_levels.append(new_level)

    def AddedContextLevel(self, new_level: str, /) -> h.Self:
        """
        Meant to be used as:
        with self.AddedContextLevel("new level"):
            ...
        """
        self.AddContextLevel(new_level)
        return self

    def StageIssue(
        self,
        message: str,
        /,
        *,
        level: int = l.ERROR,
        actual: h.Any = NOT_PASSED,
        expected: h.Any | None = None,
        expected_is_choices: bool = False,
        expected_op: expected_op_h = "=",
        with_final_dot: bool = False,
    ) -> None:
        """"""
        context = ISSUE_CONTEXT_SEPARATOR.join(self.context_levels)
        issue = NewIssue(
            context,
            ISSUE_CONTEXT_END,
            message,
            level=level,
            actual=actual,
            expected=expected,
            expected_is_choices=expected_is_choices,
            expected_op=expected_op,
            with_final_dot=with_final_dot,
        )
        self.staged_issues.append(issue)

    def PopIssues(self, /, *, should_remove_context: bool = False) -> list[str]:
        """"""
        if not self.has_staged_issues:
            return []

        output = []

        if should_remove_context:
            separator = ISSUE_CONTEXT_END
        else:
            separator = ISSUE_LEVEL_SEPARATOR
        separator_length = separator.__len__()
        for issue in self.staged_issues:
            start_idx = issue.find(separator)
            issue = issue[(start_idx + separator_length) :]
            output.append(issue)

        self.staged_issues.clear()

        return output

    def CommitIssues(
        self, /, *, order: order_h = "when", unified: bool = False
    ) -> None:
        """
        Note that issues after an issue with a level triggering process exit will not be
        logged.
        """
        if not self.has_staged_issues:
            return

        if order not in ORDER:
            raise ValueError(
                MessageWithActualExpected(
                    "Invalid commit order",
                    actual=order,
                    expected=f"One of {str(ORDER)[1:-1]}",
                )
            )

        if order == "when":
            issues = self.staged_issues
        else:  # order == "context"
            issues = sorted(self.staged_issues, key=lambda _: _.context)
        """
        Format issues as an exception:
        try:
            raise ValueError("\n" + "\n".join(issues))
        except ValueError as exception:
            lines = ["Traceback (most recent call last):"] + tcbk.format_stack()[:-1]
            lines[-1] = lines[-1][:-1]
            lines.extend(tcbk.format_exception_only(exception))
            formatted = "\n".join(lines)
        """

        hide_where = {SHOW_WHERE_ATTR: False}
        if unified:
            level, _ = issues[0].split(ISSUE_LEVEL_SEPARATOR, maxsplit=1)
            wo_level = []
            for issue in issues:
                _, issue = issue.split(ISSUE_LEVEL_SEPARATOR, maxsplit=1)
                wo_level.append(issue)
            self.log(int(level), "\n".join(wo_level), stacklevel=2, extra=hide_where)
        else:
            for issue in issues:
                level, issue = issue.split(ISSUE_LEVEL_SEPARATOR, maxsplit=1)
                self.log(int(level), issue, stacklevel=2, extra=hide_where)
        self.staged_issues.clear()

    def __enter__(self) -> None:
        """"""
        pass

    def __exit__(
        self,
        exc_type: Exception | None,
        exc_value: str | None,
        traceback: traceback_t | None,
        /,
    ) -> bool:
        """"""
        _ = self.context_levels.pop()
        return False


def _HandleForWarnings(interceptor: base_t, /) -> logger_handle_h:
    """"""

    def handle_p(_: base_t, record: l.LogRecord, /) -> None:
        pieces = WARNING_TYPE_COMPILED_PATTERN.match(record.msg)
        if pieces is None:
            # The warning message does not follow the default format.
            interceptor.handle(record)
            return

        GetPiece = pieces.group
        path = GetPiece(1)
        line = GetPiece(2)
        kind = GetPiece(3)
        message = GetPiece(4)

        path_as_t = path_t(path)
        line = int(line)
        line_content = path_as_t.read_text().splitlines()[line - 1]
        message = message.replace(line_content.strip(), "").strip()

        duplicate = l.makeLogRecord(record.__dict__)
        duplicate.msg = f"{kind}: {message}"
        duplicate.pathname = path
        duplicate.module = path_as_t.stem
        duplicate.funcName = "<function>"
        duplicate.lineno = line

        interceptor.handle(duplicate)

    return handle_p


def _HandleForInterceptions(
    intercepted: base_t, interceptor: base_t, /
) -> logger_handle_h:
    """"""

    def handle_p(_: base_t, record: l.LogRecord, /) -> None:
        duplicate = l.makeLogRecord(record.__dict__)
        duplicate.msg = f"{record.msg} :{intercepted.name}:"
        interceptor.handle(duplicate)

    return handle_p


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
