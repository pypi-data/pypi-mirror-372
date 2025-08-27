import numpy as np

from hestia.utils import _discretizer


def test_discretizer():
    labels = np.array([i/100 for i in range(100)])
    discrete_labels = _discretizer(labels, n_bins=2)
    np.testing.assert_almost_equal(np.array([i//50 for i in range(100)]).reshape(-1, 1), discrete_labels)