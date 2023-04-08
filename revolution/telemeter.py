from dataclasses import asdict, dataclass, field
from functools import partial
from hashlib import md5
from json import dumps
from logging import getLogger
from time import sleep
from typing import ClassVar

from periphery import Serial

from revolution.application import Application
from revolution.environment import Endpoint

_logger = getLogger(__name__)


@dataclass
class Telemeter(Application):
    endpoint: ClassVar[Endpoint] = Endpoint.TELEMETER
    timeout: ClassVar[float] = 0.1
    begin_token: ClassVar[bytes] = b'__BEGIN__'
    separator_token: ClassVar[bytes] = b'__SEPARATOR__'
    end_token: ClassVar[bytes] = b'__END__'
    serial: Serial = field(default_factory=partial(Serial, '', 100000))  # TODO

    def _setup(self) -> None:
        super()._setup()

        self._worker_pool.add(self.__update)

    def __update(self) -> None:
        while self._status:
            with self.environment.copy() as data:
                data_token = dumps(asdict(data)).encode()

            checksum_token = md5(data_token).digest()
            tokens = (
                self.begin_token,
                data_token,
                self.separator_token,
                checksum_token,
                self.end_token,
            )
            raw_data = b''.join(tokens)

            self.serial.write(raw_data)
            sleep(self.timeout)
