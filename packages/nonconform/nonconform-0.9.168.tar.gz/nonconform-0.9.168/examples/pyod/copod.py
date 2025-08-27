from scipy.stats import false_discovery_control

from nonconform.estimation import StandardConformalDetector
from nonconform.strategy import Jackknife
from nonconform.utils.data import load_breast
from nonconform.utils.stat import false_discovery_rate, statistical_power
from pyod.models.copod import COPOD

x_train, x_test, y_test = load_breast(setup=True)

ce = StandardConformalDetector(
    detector=COPOD(),
    strategy=Jackknife(),
)

ce.fit(x_train)
estimates = ce.predict(x_test)

decisions = false_discovery_control(estimates, method="bh") <= 0.2

print(f"Empirical FDR: {false_discovery_rate(y=y_test, y_hat=decisions)}")
print(f"Empirical Power: {statistical_power(y=y_test, y_hat=decisions)}")
