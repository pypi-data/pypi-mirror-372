"""
Copyright CNRS (https://www.cnrs.fr/index.php/en)
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import time
import typing as h

from logger_36.config.message import (
    ELAPSED_TIME_SEPARATOR,
    LEVEL_CLOSING,
    LEVEL_OPENING,
    MESSAGE_MARKER,
    TIME_FORMAT,
)

TIME_LENGTH = time.strftime(TIME_FORMAT, time.gmtime(0)).__len__()
TIME_LENGTH_m_1 = TIME_LENGTH - ELAPSED_TIME_SEPARATOR.__len__()
LOG_LEVEL_LENGTH = 1 + LEVEL_OPENING.__len__() + LEVEL_CLOSING.__len__()
CONTEXT_LENGTH = TIME_LENGTH + LOG_LEVEL_LENGTH
LINE_INDENT = (CONTEXT_LENGTH + MESSAGE_MARKER.__len__() + 2) * " "
NEXT_LINE_PROLOGUE = "\n" + LINE_INDENT

expected_op_h = h.Literal[":", ": ", "=", "!=", ">=", "<="]
EXPECTED_OP: tuple[str, ...] = h.get_args(expected_op_h)

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
