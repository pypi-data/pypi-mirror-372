import unittest
import pikobs

def unittest_timeserie(path_reference):
    """
    Run unit tests for the `timeserie` module using a reference dataset.

    This function executes a series of unit tests designed to validate the
    functionality and integrity of time series operations within the `pikobs` module.
    The tests will compare the output from various time series functions against
    a set of expected results stored in the reference location.

    Parameters:
    reference_path (str): The path to the reference data directory.
                          This directory should contain the expected results for
                          comparison during the tests.

    Returns:
    None

    Example:
        To run the unit tests, specify the path to your reference data:
        
        >>> import pikobs
        >>> pikobs.unittest_timeserie('/home/dlo001/Plotout/pikobs/pikobs/unittest_reference/unittest_timeserie')

    Notes:
    - The reference dataset should be kept up-to-date with any changes to the
      `timeserie` module to ensure accurate testing.
    - Ensure the environment is correctly configured to include all dependencies
      required by the `pikobs` module.
    """
    pikobs.TestCallPikObs_timeserie.path_reference = path_reference
    suite = unittest.TestLoader().loadTestsFromTestCase(pikobs.TestCallPikObs_timeserie)
    runner = unittest.TextTestRunner()
    runner.run(suite)

def unittest_scatter(path_reference):
    """
    Executes thessss unittests for timing series analysis.

    Args:
        path_reference (str): Path to the reference directory used in tests.
    """
    pikobs.TestCallPikObs_timeserie.path_reference = path_reference
    suite = unittest.TestLoader().loadTestsFromTestCase(pikobs.TestCallPikObs_timeserie)
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        unittest_timeserie(sys.argv[1])
    else:
        print("Please provide the reference path as an argument.")
