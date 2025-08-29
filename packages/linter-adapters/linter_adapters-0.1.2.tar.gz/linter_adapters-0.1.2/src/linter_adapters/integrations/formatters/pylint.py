from typing import *


class PylintMessage(NamedTuple):
    type: str
    module: str
    obj: str
    line: int | None
    column: int | None
    endColumn: int | None
    endLine: int | None
    path: str
    symbol: str
    message: str
    message_id: str  # should be `message-id`
    
    def asdict(self) -> dict[str, Any]:
        result = self._asdict()
        result['message-id'] = result.pop('message_id')
        return result


__all__ = \
[
    'PylintMessage',
]
