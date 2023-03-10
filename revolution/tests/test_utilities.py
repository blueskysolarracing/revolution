from unittest import TestCase, main

from revolution.utilities import interpolate


class UtilitiesTestCase(TestCase):
    def test_interpolate(self) -> None:
        self.assertAlmostEqual(interpolate(-1, 0, 1, 5, 6), 4)
        self.assertAlmostEqual(interpolate(0, 0, 1, 5, 6), 5)
        self.assertAlmostEqual(interpolate(0.5, 0, 1, 5, 6), 5.5)
        self.assertAlmostEqual(interpolate(1, 0, 1, 5, 6), 6)
        self.assertAlmostEqual(interpolate(2, 0, 1, 5, 6), 7)

        self.assertAlmostEqual(interpolate(0, 1, 2, 5, 6), 4)
        self.assertAlmostEqual(interpolate(1, 1, 2, 5, 6), 5)
        self.assertAlmostEqual(interpolate(1.5, 1, 2, 5, 6), 5.5)
        self.assertAlmostEqual(interpolate(2, 1, 2, 5, 6), 6)
        self.assertAlmostEqual(interpolate(3, 1, 2, 5, 6), 7)

        self.assertAlmostEqual(interpolate(0, 1, 2, 10, 20), 0)
        self.assertAlmostEqual(interpolate(1, 1, 2, 10, 20), 10)
        self.assertAlmostEqual(interpolate(1.5, 1, 2, 10, 20), 15)
        self.assertAlmostEqual(interpolate(2, 1, 2, 10, 20), 20)
        self.assertAlmostEqual(interpolate(3, 1, 2, 10, 20), 30)


if __name__ == '__main__':
    main()
