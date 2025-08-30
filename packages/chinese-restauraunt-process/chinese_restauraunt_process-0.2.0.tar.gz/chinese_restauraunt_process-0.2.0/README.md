# chinese_restaurant_process

chinese_restaurant_process is a Python package that provides an easy to use interface for simulating the Chinese Restaurant Process (CRP), a popular model in Bayesian nonparametrics.

## Installation
---------------

### Installation Methods

You can install Chinese Restaurant Process using pip:

```bash
pip install chinese_restaurant_process
```

You can install the latest version directly from the GitHub repository using pip:
```bash
pip install git+https://github.com/jhaberbe/chinese_restaurant_process
```

Or, if you want to install the package from source, you can use:
```bash
git clone https://github.com/jhaberbe/chinese_restaurant_process.git
pip install .
```

## Usage
--------

### Example Use Cases

To perform the initial inference of classes:

```python
import numpy as np
from crp.process import ChineseRestaurantProcess

# Your data, (n_samples, n_features)
X = np.random.randint(1, 100, size=(1000, 10))

# Run inference on train data.
crp = ChineseRestaurantProcess(X, expected_number_of_classes=1)
crp.run(epochs=1)
```

After training, you can predict the class of new data points:

```python
# Your data, (n_samples, n_features)
X_new = np.random.randint(1, 100, size=(1000, 10))

# Setting min_membership = 0.01 is recommended usually.
# Since this is random data, we set it to 0
labels = crp.predict(X_new, min_membership=0.0)
```

### Documentation

<<<<<<< HEAD
We have a few tutorials in the `notebook/` folder. They go over basic usage, and also try to explain how inference is going to be performed.
=======
We have several notebooks in the `notebooks` directory that demonstrate the usage of the Chinese Restaurant Process. You can run these notebooks to see how the package works in practice.
>>>>>>> c78e78c2e5e62d5fa474627a86c92687e57afef4

Recommended reading order is:
- Usage.ipynb
- What-The-Heck-Is-Collapsed-Gibbs-Sampling.ipynb
- Explaining-Class-Structure.ipynb

## Contributing
------------

We welcome contributions. If you'd like to contribute, please follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch for your changes.
3. Make the changes to your branch.
4. Commit your changes with a meaningful commit message.
5. Create a pull request against the main branch.

#### Right now, work is being done to add the following features:
- [ ] Improve sampling of inital hyperparameters, right now the hyperparameters are sampled are fixed, and it works well for most cases, but it would be nice to have a more robust sampling method.
- [ ] Infinitely Nested Chinese Restaurant Process, as described by [Blei et al. (2010)](https://cocosci.princeton.edu/tom/papers/ncrp.pdf). Some work is already done, but it is not yet ready for use (`notebook/In Progress/Nested-Chinese-Restaurant-Process.ipynb`).
- [ ] More distributions (Gaussian, Gamma, etc. etc.)
- [ ] Plotting utilities to visualize the class structure of the CRP.
- [ ] Utilities to extract out which features are most important for each class.
- [ ] Testing (I've never done testing before, so this will be a learning experience for me).

## License
--------

Chinese Restaurant Process is released under the GPL v3 license. See the LICENSE file for more information.