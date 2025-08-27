from argenta.response.status import Status
from argenta.command.flag.flags import (
    ValidInputFlags,
    UndefinedInputFlags,
    InvalidValueInputFlags,
)


class Response:
    __slots__ = ("status", "valid_flags", "undefined_flags", "invalid_value_flags")

    def __init__(
        self,
        status: Status | None = None,
        valid_flags: ValidInputFlags = ValidInputFlags(),
        undefined_flags: UndefinedInputFlags = UndefinedInputFlags(),
        invalid_value_flags: InvalidValueInputFlags = InvalidValueInputFlags(),
    ):
        """
        Public. The entity of the user input sent to the handler
        :param status: the status of the response
        :param valid_flags: valid input flags
        :param undefined_flags: undefined input flags
        :param invalid_value_flags: input flags with invalid values
        """
        self.status = status
        self.valid_flags = valid_flags
        self.undefined_flags = undefined_flags
        self.invalid_value_flags = invalid_value_flags
