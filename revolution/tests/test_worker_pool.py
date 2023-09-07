from unittest import main, TestCase
from threading import Lock

from revolution.worker_pool import WorkerPool


class WorkerPoolTestCase(TestCase):
    def test_add_and_join(self) -> None:
        counter = 0
        lock = Lock()
        worker_pool = WorkerPool()

        def increment(value: int) -> None:
            nonlocal counter

            with lock:
                counter += value

        for i in range(10):
            worker_pool.add(increment, i)

        worker_pool.join()
        self.assertEqual(counter, 45)


if __name__ == '__main__':
    main()
