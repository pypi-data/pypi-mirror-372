from scipy.stats import false_discovery_control

from nonconform.estimation import StandardConformalDetector
from nonconform.strategy import Split
from nonconform.utils.data import load_thyroid
from nonconform.utils.stat import false_discovery_rate, statistical_power
from pyod.models.loci import LOCI

x_train, x_test, y_test = load_thyroid(setup=True)

ce = StandardConformalDetector(detector=LOCI(k=1), strategy=Split(n_calib=1_000))

ce.fit(x_train)
estimates = ce.predict(x_test)
# Apply FDR control
decisions = false_discovery_control(estimates, method="bh") <= 0.2

print(f"Empirical FDR: {false_discovery_rate(y=y_test, y_hat=decisions)}")
print(f"Empirical Power: {statistical_power(y=y_test, y_hat=decisions)}")
