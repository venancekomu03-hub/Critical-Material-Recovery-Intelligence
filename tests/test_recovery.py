
import unittest
import numpy as np


def recovered_mass(component_count, mass_mg, efficiency):
    if component_count < 0 or mass_mg < 0:
        raise ValueError("Count and mass cannot be negative")

    if not 0 <= efficiency <= 1:
        raise ValueError("Efficiency must be between 0 and 1")

    return component_count * mass_mg * efficiency


class TestRecoveryCalculations(unittest.TestCase):

    def test_known_result(self):
        result = recovered_mass(10, 0.5, 0.8)
        self.assertAlmostEqual(result, 4.0)

    def test_zero_components(self):
        self.assertEqual(recovered_mass(0, 0.5, 0.8), 0)

    def test_zero_efficiency(self):
        self.assertEqual(recovered_mass(10, 0.5, 0), 0)

    def test_full_efficiency(self):
        self.assertEqual(recovered_mass(10, 0.5, 1), 5.0)

    def test_invalid_efficiency(self):
        with self.assertRaises(ValueError):
            recovered_mass(10, 0.5, 1.5)

    def test_monte_carlo_mean(self):
        rng = np.random.default_rng(42)
        samples = rng.uniform(0.25, 0.75, 10000)

        # The theoretical mean of Uniform(a,b) is (a+b)/2
        self.assertAlmostEqual(samples.mean(), 0.5, delta=0.01)


if __name__ == "__main__":
    unittest.main()
