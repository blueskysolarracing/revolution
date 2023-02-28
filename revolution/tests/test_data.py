from dataclasses import dataclass
from unittest import TestCase, main

from revolution.data import DataAccessor, DataManager


@dataclass
class _MockData:
    one: int = 1
    two: int = 2
    three: int = 3


class DataAccessorTestCase(TestCase):
    def test_getattr(self) -> None:
        data = _MockData()

        for data_accessor in (
            DataAccessor(data, DataAccessor.Mode.READ),
            DataAccessor(
                data,
                DataAccessor.Mode.READ | DataAccessor.Mode.WRITE,
            ),
        ):
            self.assertEqual(getattr(data_accessor, 'one'), 1)
            self.assertEqual(getattr(data_accessor, 'two'), 2)
            self.assertEqual(getattr(data_accessor, 'three'), 3)

        for data_accessor in (
            DataAccessor(data, DataAccessor.Mode(0)),
            DataAccessor(data, DataAccessor.Mode.WRITE),
        ):
            self.assertRaises(ValueError, getattr, data_accessor, 'one')
            self.assertRaises(ValueError, getattr, data_accessor, 'two')
            self.assertRaises(ValueError, getattr, data_accessor, 'three')

    def test_setattr(self) -> None:
        data = _MockData()

        for data_accessor in (
            DataAccessor(data, DataAccessor.Mode.WRITE),
            DataAccessor(
                data,
                DataAccessor.Mode.READ | DataAccessor.Mode.WRITE,
            ),
        ):
            setattr(data_accessor, 'one', -1)
            setattr(data_accessor, 'two', -2)
            setattr(data_accessor, 'three', -3)

        self.assertEqual(data.one, -1)
        self.assertEqual(data.two, -2)
        self.assertEqual(data.three, -3)

        for data_accessor in (
            DataAccessor(data, DataAccessor.Mode(0)),
            DataAccessor(data, DataAccessor.Mode.READ),
        ):
            self.assertRaises(ValueError, setattr, data_accessor, 'one', 1)
            self.assertRaises(ValueError, setattr, data_accessor, 'two', 2)
            self.assertRaises(ValueError, setattr, data_accessor, 'three', 3)

        self.assertEqual(data.one, -1)
        self.assertEqual(data.two, -2)
        self.assertEqual(data.three, -3)

    def test_close(self) -> None:
        data = _MockData()

        for data_accessor in (
            DataAccessor(data, DataAccessor.Mode.READ),
            DataAccessor(data, DataAccessor.Mode.WRITE),
            DataAccessor(data, DataAccessor.Mode.WRITE),
        ):
            data_accessor.close()

            self.assertRaises(ValueError, getattr, data_accessor, 'one')
            self.assertRaises(ValueError, getattr, data_accessor, 'two')
            self.assertRaises(ValueError, getattr, data_accessor, 'three')
            self.assertRaises(ValueError, setattr, data_accessor, 'one', -1)
            self.assertRaises(ValueError, setattr, data_accessor, 'two', -2)
            self.assertRaises(ValueError, setattr, data_accessor, 'three', -3)


class DataManagerTestCase(TestCase):
    def test_read(self) -> None:
        data = _MockData()
        data_manager = DataManager(data)

        with data_manager.read() as data:
            self.assertEqual(data.one, 1)
            self.assertEqual(data.two, 2)
            self.assertEqual(data.three, 3)
            self.assertRaises(ValueError, setattr, data, 'one', -1)
            self.assertRaises(ValueError, setattr, data, 'two', -2)
            self.assertRaises(ValueError, setattr, data, 'three', -3)

        with data_manager.read() as data:
            self.assertEqual(data.one, 1)
            self.assertEqual(data.two, 2)
            self.assertEqual(data.three, 3)

    def test_write(self) -> None:
        data = _MockData()
        data_manager = DataManager(data)

        with data_manager.write() as data:
            self.assertRaises(ValueError, getattr, data, 'one')
            self.assertRaises(ValueError, getattr, data, 'two')
            self.assertRaises(ValueError, getattr, data, 'three')
            data.one = -1
            data.two = -2
            data.three = -3

        with data_manager.read() as data:
            self.assertEqual(data.one, -1)
            self.assertEqual(data.two, -2)
            self.assertEqual(data.three, -3)

    def test_read_and_write(self) -> None:
        data = _MockData()
        data_manager = DataManager(data)

        with data_manager.read_and_write() as data:
            self.assertEqual(data.one, 1)
            self.assertEqual(data.two, 2)
            self.assertEqual(data.three, 3)
            data.one = -1
            data.two = -2
            data.three = -3

        with data_manager.read() as data:
            self.assertEqual(data.one, -1)
            self.assertEqual(data.two, -2)
            self.assertEqual(data.three, -3)

    def test_closure(self) -> None:
        data = _MockData()
        data_manager = DataManager(data)

        for manage in (
                data_manager.read,
                data_manager.write,
                data_manager.read_and_write,
        ):
            with manage() as data:
                pass

            self.assertRaises(ValueError, getattr, data, 'one')
            self.assertRaises(ValueError, getattr, data, 'two')
            self.assertRaises(ValueError, getattr, data, 'three')
            self.assertRaises(ValueError, setattr, data, 'one', -1)
            self.assertRaises(ValueError, setattr, data, 'two', -2)
            self.assertRaises(ValueError, setattr, data, 'three', -3)

    def test_copy(self) -> None:
        data = _MockData()
        data_manager = DataManager(data)

        with data_manager.copy() as data_copy:
            data_copy.one = -1
            data_copy.two = -2
            data_copy.three = -3

            self.assertEqual(data_copy.one, -1)
            self.assertEqual(data_copy.two, -2)
            self.assertEqual(data_copy.three, -3)

            with data_manager.read() as data:
                self.assertEqual(data.one, 1)
                self.assertEqual(data.two, 2)
                self.assertEqual(data.three, 3)


if __name__ == '__main__':
    main()
