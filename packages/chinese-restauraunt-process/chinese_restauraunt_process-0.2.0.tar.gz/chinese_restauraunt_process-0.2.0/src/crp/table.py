import numpy as np
import pandas as pd
from scipy.special import gammaln
from scipy.stats import t

class ChineseRestaurantTable:
    """
    Represents a table in a Chinese restaurant.

    Args:
        data (np.ndarray): A 2D array storing the table's data.
        members (set, optional): A set of unique indices representing the table's members. Defaults to an empty set.

    Attributes:
        data (np.ndarray): A 2D array storing the table's data.
        members (set): A set of unique indices representing the table's members.

    Methods:
        add_member(index): Adds a member to the table at the specified index.
        remove_member(index): Removes a member from the table at the specified index.
        return_parameters(): Returns parameters that should be implemented in subclasses.
        log_likelihood(index, posterior=False): Calculates the log likelihood of the table.
        predict(count=np.array([])): Makes predictions using the table's data.
    """

    def __init__(self, data, members=None):
        """
        Initializes a ChineseRestaurantTable object with the given data.

        Args:
            data (np.ndarray): A 2D array to be stored in the table.
            members (set, optional): A set of unique indices representing the table's members. Defaults to an empty set.

        Raises:
            TypeError: If the data is not a numpy array.
        """
        if not isinstance(data, np.ndarray):
            raise TypeError("Data must be a numpy array")
        self.data = np.array(data)
        self.members = set() if members is None else members
    
    def _row_exposure(self, index: int) -> float:
        total = float(np.sum(self.data[index]))
        return (total / self.reference_total) if self.reference_total > 0 else 1.0

    def add_member(self, index: int):
        """
        Adds a member to the table at the specified index.

        Args:
            index (int): The index at which the member is to be added.

        Raises:
            ValueError: If the index is not a valid index.
        """
        if index < 0:
            raise ValueError("Index must be a non-negative integer")
        if index not in self.members:
            self.members.add(index)
            self.alpha += self.data[index]
            self.beta += self._row_exposure(index)  # One new data point

    def remove_member(self, index: int):
        """
        Removes a member from the table at the specified index.

        Args:
            index (int): The index at which the member is to be removed.

        Raises:
            ValueError: If the index is not a valid index.
        """
        if index < 0:
            raise ValueError("Index must be a non-negative integer")
        if index in self.members:
            self.members.remove(index)
            self.alpha -= self.data[index]
            self.beta -= self._row_exposure(index)

    def return_parameters(self):
        """
        Returns parameters that should be implemented in subclasses.

        Raises:
            NotImplementedError: This method should be implemented in subclasses.
        """
        raise NotImplementedError("This method should be implemented in subclasses.")

    def log_likelihood(self, index: int, posterior: bool = False):
        """
        Calculates the log likelihood of the table.

        Args:
            index (int): The index of the table.
            posterior (bool, optional): A flag indicating whether to calculate the posterior. Defaults to False.

        Note:
            This method is currently not implemented.
        """
        pass

    def predict(self, count: np.ndarray):
        """
        Makes predictions using the table's data.

        Args:
            count (np.ndarray): A numpy array representing the count.

        Note:
            This method is currently not implemented.
        """
        pass



class DirichletMultinomialTable(ChineseRestaurantTable):
    """
    Represents a table in a Dirichlet-Multinomial model.

    Args:
        data (np.ndarray): A 2D array storing the table's data.
        members (set, optional): A set of unique indices representing the table's members. Defaults to an empty set.

    Attributes:
        data (np.ndarray): A 2D array storing the table's data.
        members (set): A set of unique indices representing the table's members.
        concentration (np.ndarray): A 1D array representing the concentration parameters.

    Methods:
        add_member(index): Adds a member to the table at the specified index.
        remove_member(index): Removes a member from the table at the specified index.
        return_parameters(index=None): Returns the parameters of the table.
        _dirichlet_multinomial_log_likelihood(count, concentration): Calculates the log likelihood of the Dirichlet-Multinomial model.
        log_likelihood(index, posterior=False): Calculates the log likelihood of the table.
        predict(count=np.array([])): Makes predictions using the table's data.
    """

    def __init__(self, data: np.ndarray):
        """
        Initializes a DirichletMultinomialTable object with the given data.

        Args:
            data (np.ndarray): A 2D array to be stored in the table.

        Raises:
            TypeError: If the data is not a numpy array.
        """
        if not isinstance(data, np.ndarray):
            raise TypeError("Data must be a numpy array")
        self.data = np.array(data)
        self.members = set()
        self.concentration = np.ones((1, self.data.shape[1]))  # shape: (D,)

    def add_member(self, index: int):
        """
        Adds a member to the table at the specified index.

        Args:
            index (int): The index at which the member is to be added.

        Raises:
            ValueError: If the index is not a valid index.
        """
        if index < 0:
            raise ValueError("Index must be a non-negative integer")
        if index not in self.members:
            self.members.add(index)
            self.concentration += self.data[index]

    def remove_member(self, index: int):
        """
        Removes a member from the table at the specified index.

        Args:
            index (int): The index at which the member is to be removed.

        Raises:
            ValueError: If the index is not a valid index.
        """
        if index < 0:
            raise ValueError("Index must be a non-negative integer")
        if index in self.members:
            self.members.remove(index)
            self.concentration -= self.data[index]

    def return_parameters(self, index: int = None):
        """
        Returns the parameters of the table.

        Args:
            index (int, optional): The index at which to return the parameters. Defaults to None.

        Returns:
            pd.Series: A pandas series containing the concentration parameters.
        """
        parameters = pd.Series({
            "concentration": self.concentration
        })

        if index is not None:
            parameters.index = index
            return parameters
        else:
            return parameters

    def _dirichlet_multinomial_log_likelihood(self, count: np.ndarray, concentration: np.ndarray) -> float:
        """
        Calculates the log likelihood of the Dirichlet-Multinomial model.

        Args:
            count (np.ndarray): A 1D array representing the count.
            concentration (np.ndarray): A 1D array representing the concentration parameters.

        Returns:
            float: The log likelihood of the Dirichlet-Multinomial model.
        """
        N = np.sum(count)
        return (
            np.sum(gammaln(N + 1)) - np.sum(gammaln(count + 1)) + np.sum(gammaln(concentration)) - np.sum(gammaln(concentration + N)) + np.sum(gammaln(count + concentration) - gammaln(concentration))
        )

    def log_likelihood(self, index: int, posterior: bool = False):
        """
        Calculates the log likelihood of the table.

        Args:
            index (int): The index of the table.
            posterior (bool, optional): A flag indicating whether to calculate the posterior. Defaults to False.

        Returns:
            float: The log likelihood of the table.
        """
        if posterior:
            concentration = self.concentration + self.data[index]
        else:
            concentration = self.concentration
        return self._dirichlet_multinomial_log_likelihood(self.data[index], concentration)

    def predict(self, count: np.ndarray):
        """
        Makes predictions using the table's data.

        Args:
            count (np.ndarray): A 1D array representing the count.

        Returns:
            float: The prediction.
        """
        return self._dirichlet_multinomial_log_likelihood(count, self.concentration)



class NegativeBinomialTable(ChineseRestaurantTable):
    """
    Represents a table in a Negative Binomial model.

    Attributes:
        data (np.ndarray): A 2D array storing the table's data.
        members (set): A set of unique indices representing the table's members.
        alpha (np.ndarray): A 1D array representing the shape parameters.
        beta (np.ndarray): A 1D array representing the rate parameters.
        reference_total (float): The total count of self.data.
    """

    def __init__(self, data: np.ndarray):
        """
        Initializes a NegativeBinomialTable object with the given data.

        Args:
            data (np.ndarray): A 2D array to be stored in the table.

        Raises:
            TypeError: If the data is not a numpy array.
        """
        if not isinstance(data, np.ndarray):
            raise TypeError("Data must be a numpy array")
        self.data = np.array(data)
        self.members = set()
        self.alpha = np.ones(self.data.shape[1])  # prior shape
        self.beta = np.ones(self.data.shape[1])   # prior rate
        self.reference_total = np.mean(np.sum(self.data, axis=1))

    def _row_exposure(self, index: int) -> float:
        total = float(np.sum(self.data[index]))
        return (total / self.reference_total) if self.reference_total > 0 else 1.0

    def add_member(self, index: int):
        """
        Adds a member to the table at the specified index.

        Args:
            index (int): The index at which the member is to be added.

        Raises:
            ValueError: If the index is not a valid index.
        """
        if index < 0:
            raise ValueError("Index must be a non-negative integer")
        if index not in self.members:
            self.members.add(index)
            self.alpha += self.data[index]
            self.beta += self._row_exposure(index)  # One new data point

    def remove_member(self, index: int):
        """
        Removes a member from the table at the specified index.

        Args:
            index (int): The index at which the member is to be removed.

        Raises:
            ValueError: If the index is not a valid index.
        """
        if index < 0:
            raise ValueError("Index must be a non-negative integer")
        if index in self.members:
            self.members.remove(index)
            self.alpha -= self.data[index]
            self.beta -= self._row_exposure(index)
    
    def _gamma_poisson_log_likelihood(self, count: np.ndarray, alpha: np.ndarray, beta: np.ndarray) -> float:
        """
        Calculates the log likelihood of the Negative Binomial model.

        Args:
            count (np.ndarray): A 1D array representing the count.
            alpha (np.ndarray): A 1D array representing the shape parameters.
            beta (np.ndarray): A 1D array representing the rate parameters.

        Returns:
            float: The log likelihood of the Negative Binomial model.
        """
        count = np.asarray(count).reshape(-1)
        alpha = np.asarray(alpha).reshape(-1)
        beta = np.asarray(beta).reshape(-1)

        # Compute size factor from total count vs. mean total count of self.data
        total = np.sum(count)
        reference_total = self.reference_total
        size_factor = total / reference_total if reference_total > 0 else 1.0
        log_sf = np.log(size_factor)

        # Gamma-Poisson log-likelihood with offset
        term1 = gammaln(count + alpha)
        term2 = -gammaln(count + 1)
        term3 = -gammaln(alpha)
        term4 = alpha * np.log(beta / (beta + np.exp(log_sf)))
        term5 = count * np.log(np.exp(log_sf) / (beta + np.exp(log_sf)))

        return np.sum(term1 + term2 + term3 + term4 + term5)

    def return_parameters(self, index: int = None) -> pd.DataFrame:
        """
        Returns the parameters of the table.

        Args:
            index (int, optional): The index at which to return the parameters. Defaults to None.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the shape and rate parameters.
        """
        parameters = pd.DataFrame({
            "mean": self.alpha,
            "dispersion": self.beta / (1 + self.beta)
        })

        if index is not None:
            parameters.index = index
            return parameters
        else:
            return parameters

    def log_likelihood(self, index: int, posterior: bool = False) -> float:
        """
        Calculates the log likelihood of the table.

        Args:
            index (int): The index of the table.
            posterior (bool, optional): A flag indicating whether to calculate the posterior. Defaults to False.

        Returns:
            float: The log likelihood of the table.
        """
        x = self.data[index]
        if posterior:
            alpha = self.alpha + x
            beta = self.beta + self._row_exposure(index)
        else:
            alpha = self.alpha
            beta = self.beta

        return self._gamma_poisson_log_likelihood(x, alpha, beta)

    def predict(self, count: np.ndarray) -> float:
        """
        Makes predictions using the table's data.

        Args:
            count (np.ndarray): A 1D array representing the count.

        Returns:
            float: The prediction.
        """
        return self._gamma_poisson_log_likelihood(count, self.alpha, self.beta)



class BernoulliTable(ChineseRestaurantTable):
    """
    A Bernoulli table to analyze binary data.

    Attributes:
        data (np.ndarray): A 2D NumPy array of binary data.
        members (set): A set of unique member indices.
        alpha (np.ndarray): A 1D NumPy array representing prior shape.
        beta (np.ndarray): A 1D NumPy array representing prior rate.
        reference_total (float): The reference total probability.
    """

    def __init__(self, data: np.ndarray):
        """
        Initialize a Bernoulli table.

        Args:
            data (np.ndarray): A 2D NumPy array of binary data.

        Raises:
            AssertionError: If the input data is not binary (0 or 1).

        Notes:
            The data is stored as a 2D NumPy array, where each row represents
            a single observation, and each column represents a binary feature.
        """
        self.data = np.array(data)
        self.members = set()

        D = self.data.shape[1]
        self.alpha = np.ones(D)  # prior shape
        self.beta = np.ones(D)   # prior rate

        self.reference_total = np.mean(np.sum(data, axis=1))

    def add_member(self, index: int):
        """
        Add a new member to the table.

        Args:
            index (int): The index of the new member.

        Notes:
            The new member is added to the set of unique member indices.
            The prior shape and rate are updated accordingly.

        Raises:
            AssertionError: If the index is already in the set of unique member indices.
        """
        if index not in self.members:
            self.members.add(index)
            self.alpha += self.data[index]
            self.beta += 1 - self.data[index]

    def remove_member(self, index: int):
        """
        Remove a member from the table.

        Args:
            index (int): The index of the member to be removed.

        Notes:
            The member is removed from the set of unique member indices.
            The prior shape and rate are updated accordingly.

        Raises:
            AssertionError: If the index is not in the set of unique member indices.
        """
        if index in self.members:
            self.members.remove(index)
            self.alpha -= self.data[index]
            self.beta -= 1 - self.data[index]

    def _bernoulli_likelihood(self, count: np.ndarray, alpha: np.ndarray, beta: np.ndarray) -> float:
        """
        Calculate the Bernoulli likelihood.

        Args:
            count (np.ndarray): A 1D NumPy array of observed counts.
            alpha (np.ndarray): A 1D NumPy array representing prior shape.
            beta (np.ndarray): A 1D NumPy array representing prior rate.

        Returns:
            float: The Bernoulli likelihood.

        Notes:
            The Bernoulli likelihood is calculated using the formula:
            log(count * (alpha / (alpha + beta))) + log((1 - count) * (beta / (alpha + beta)))
        """
        return (
            np.sum(count * np.log(alpha / (alpha + beta))) +
            np.sum((1 - count) * np.log(beta / (alpha + beta)))
        )

    def return_parameters(self, index: int = None):
        """
        Return the parameters of the table.

        Args:
            index (int): An optional index to return parameters for.

        Returns:
            pd.Series: A pandas Series containing the parameters.

        Notes:
            The parameters are returned as a pandas Series with a single column
            containing the probability.
        """
        parameters = pd.Series({
            "probability": self.alpha / (self.alpha + self.beta)
        })

        if index is not None:
            parameters.index = index
            return parameters
        else:
            return parameters

    def log_likelihood(self, index: int, posterior: bool = False):
        """
        Calculate the log likelihood.

        Args:
            index (int): The index of the observation to calculate the log likelihood for.
            posterior (bool): An optional flag to indicate if the log likelihood is for the posterior distribution.

        Returns:
            float: The log likelihood.

        Notes:
            The log likelihood is calculated using the formula:
            log(count * (alpha / (alpha + beta))) + log((1 - count) * (beta / (alpha + beta)))
            If posterior is True, the log likelihood is calculated for the posterior distribution.
        """
        x = self.data[index]
        if posterior:
            alpha = self.alpha + x
            beta = self.beta + 1 - x
        else:
            alpha = self.alpha
            beta = self.beta

        return self._bernoulli_likelihood(x, alpha, beta)

    def predict(self, count: np.ndarray):
        """
        Make predictions using the Bernoulli table.

        Args:
            count (np.ndarray): A 1D NumPy array of observed counts.

        Returns:
            float: The predicted values.

        Notes:
            The predictions are calculated using the formula:
            log(count * (alpha / (alpha + beta)))
        """
        return self._bernoulli_likelihood(count, self.alpha, self.beta)



class GaussianTable(ChineseRestaurantTable):
    """
    Represents a table in a Gaussian model using a Normal-Inverse-Gamma prior.

    Attributes:
        data (np.ndarray): A 2D array storing the table's data.
        members (set): A set of unique indices representing the table's members.
        mu0 (np.ndarray): Prior mean.
        lambda0 (float): Prior strength for mean.
        alpha0 (float): Prior shape for variance.
        beta0 (float): Prior scale for variance.
    """

    def __init__(self, data: np.ndarray):
        if not isinstance(data, np.ndarray):
            raise TypeError("Data must be a numpy array")

        self.data = np.array(data)
        self.members = set()

        # Prior parameters
        self.mu0 = np.zeros(self.data.shape[1])
        self.lambda0 = 1.0
        self.alpha0 = 2.0
        self.beta0 = 2.0

        # Posterior parameters
        self._update_posterior()

    def _update_posterior(self):
        """
        Recalculate posterior parameters based on current members.
        """
        if not self.members:
            self.mu_n = self.mu0
            self.lambda_n = self.lambda0
            self.alpha_n = self.alpha0
            self.beta_n = self.beta0
            return

        member_data = self.data[list(self.members)]
        n = len(self.members)
        x_bar = np.mean(member_data, axis=0)
        sse = np.sum((member_data - x_bar) ** 2, axis=0)

        self.lambda_n = self.lambda0 + n
        self.mu_n = (self.lambda0 * self.mu0 + n * x_bar) / self.lambda_n
        self.alpha_n = self.alpha0 + n / 2
        self.beta_n = self.beta0 + 0.5 * sse + \
            (self.lambda0 * n * (x_bar - self.mu0) ** 2) / (2 * self.lambda_n)

    def add_member(self, index: int):
        if index < 0 or index >= len(self.data):
            raise ValueError("Index must be valid and non-negative")
        if index not in self.members:
            self.members.add(index)
            self._update_posterior()

    def remove_member(self, index: int):
        if index in self.members:
            self.members.remove(index)
            self._update_posterior()

    def log_likelihood(self, index: int, posterior: bool = False) -> float:
        """
        Compute log-likelihood of the data at `index` under the model.
        If `posterior=True`, use updated parameters including that point.
        """
        x = self.data[index]
        mu = self.mu_n
        lambda_ = self.lambda_n
        alpha = self.alpha_n
        beta = self.beta_n

        if posterior:
            # Temporarily add and remove index to get posterior with this data point
            self.add_member(index)
            mu = self.mu_n
            lambda_ = self.lambda_n
            alpha = self.alpha_n
            beta = self.beta_n
            self.remove_member(index)

        # Student-t log likelihood approximation
        dof = 2 * alpha
        scale = np.sqrt(beta * (lambda_ + 1) / (alpha * lambda_))
        t_logpdf = t.logpdf(x, df=dof, loc=mu, scale=scale)
        return np.sum(t_logpdf)

    def predict(self, x: np.ndarray) -> float:
        """
        Predict the log likelihood of a new observation x.
        """
        x = np.asarray(x)
        return self.log_likelihood(index=None, posterior=False)

    def return_parameters(self, index=None) -> pd.DataFrame:
        """
        Returns current posterior mean and variance estimates.
        """
        mean = self.mu_n
        var = self.beta_n / (self.alpha_n - 1)
        parameters = pd.DataFrame({
            "mean": mean,
            "variance": var
        })

        if index is not None:
            parameters.index = index
        return parameters
