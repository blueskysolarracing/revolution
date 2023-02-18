from multiprocessing import Process, log_to_stderr
from logging import DEBUG

from revolution import Application, Context, Environment

_logger = log_to_stderr(DEBUG)


def main() -> None:
    _logger.info('Launching revolution...')

    context = Context()
    environment = Environment(context)
    processes = []

    for application_type in Application.__subclasses__():
        if application_type.endpoint is not None:
            processes.append(
                Process(
                    target=application_type.main,
                    name=application_type.endpoint.name,
                    args=(environment,),
                ),
            )

    for process in processes:
        process.start()

    for process in processes:
        process.join()


if __name__ == '__main__':
    main()
