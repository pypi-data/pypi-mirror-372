import numpy as np
from tqdm import tqdm
from .table import ChineseRestaurantTable, DirichletMultinomialTable, NegativeBinomialTable

class ChineseRestaurantProcess:
    """
    A Chinese Restaurant Process (CRP) model.

    The CRP is a Bayesian nonparametric model for classifying data.
    It is a special case of the Dirichlet process mixture model.

    Attributes:
        data (np.array): The initial data.
        classes (dict): A dictionary of classes, where each key is a class ID and each value is a ChineseRestaurantTable object.
        assignments (list): A list of class IDs assigned to each data point.
        expected_number_of_classes (int): The expected number of classes.
        _alpha (float): The prior shape parameter.
        _table_type (class): The type of table to use.
    """

    _table_type = NegativeBinomialTable

    def __init__(self, data: np.array, expected_number_of_classes: int = 1):
        """
        Initialize the CRP model.

        Args:
            data (np.array): The initial data.
            expected_number_of_classes (int): The expected number of classes. Defaults to 1.

        Raises:
            ValueError: If the data is not a NumPy array.
        """
        self.data = data
        self.classes = {}
        self.assignments = [-1] * data.shape[0]
        self.expected_number_of_classes = expected_number_of_classes
        self._alpha = self.expected_number_of_classes / np.log(self.data.shape[0])

    def set_table_type(self, cls):
        """
        Set the type of table to use.

        Args:
            cls (class): The type of table to use.

        Notes:
            The table type is stored in the `_table_type` attribute.
        """
        self._table_type = cls

    def generate_new_table(self):
        """
        Generate a new table.

        Returns:
            ChineseRestaurantTable: A new table.
        """
        return self._table_type(self.data)

    def add_table(self, table: ChineseRestaurantTable, index: int):
        """
        Add a table to the model.

        Args:
            table (ChineseRestaurantTable): The table to add.
            index (int): The index of the data point to assign to the table.

        Notes:
            The table is assigned to the data point with the smallest unused lot ID.
        """
        new_class_id = 0
        while new_class_id in self.classes:
            new_class_id += 1
        self.classes[new_class_id] = table
        self.classes[new_class_id].add_member(index)
        self.assignments[index] = new_class_id

    def remove_table(self, class_id):
        """
        Remove a table from the model.

        Args:
            class_id (int): The ID of the table to remove.

        Raises:
            ValueError: If the class ID does not exist.
        """
        if class_id in self.classes:
            for member in self.classes[class_id].members:
                self.assignments[member] = -1
            del self.classes[class_id]
        else:
            raise ValueError(f"Class ID {class_id} does not exist.")

    def return_class_parameters(self, index: int = None):
        """
        Return the parameters of the classes.

        Args:
            index (int): An optional index to return parameters for. Defaults to None.

        Returns:
            dict: A dictionary of class parameters, where each key is a class ID and each value is a pandas Series.
        """
        return {
            k: v.get_parameters(index=index) for k, v in self.classes.items()
        }
    
    def _reindex_classes(self) -> None:
        """Compress class IDs to 0..K-1 and update assignments accordingly."""
        if not self.classes:
            return
        old_ids = sorted(self.classes.keys())
        old_to_new = {old: new for new, old in enumerate(old_ids)}
        # remap classes
        self.classes = {old_to_new[old]: tab for old, tab in self.classes.items()}
        # remap assignments
        self.assignments = [
            (-1 if cid == -1 else old_to_new.get(cid, -1))
            for cid in self.assignments
        ]

    def run(self, epochs: int = 1, min_membership: float = 0.01):
        """
        Run the CRP model.
        """
        n = self.data.shape[0]
        for epoch in range(epochs):
            order = np.random.permutation(n)
            pbar = tqdm(order, desc=f"Epoch {epoch+1}/{epochs}", dynamic_ncols=True, leave=True)

            # show initial K
            K_prev = None
            K = len(self.classes)
            pbar.set_postfix_str(f"K={K}")
            K_prev = K

            for index in pbar:
                crp_new = self.generate_new_table()
                cluster_keys = list(self.classes.keys()) + ["new"]
                nlls = []
                for k in self.classes:
                    table = self.classes[k]
                    log_like = table.log_likelihood(index, posterior=True)
                    log_prior = np.log1p(len(table.members))
                    nlls.append(log_like + log_prior)

                log_new = crp_new.log_likelihood(index, posterior=True) + np.log(self._alpha)
                nlls.append(log_new)

                probs = np.exp(nlls - np.max(nlls))
                probs /= probs.sum()
                sampled_idx = np.random.choice(len(probs), p=probs)
                sampled_class = cluster_keys[sampled_idx]

                if sampled_class == "new":
                    self.add_table(crp_new, index)
                else:
                    self.classes[sampled_class].add_member(index)
                    self.assignments[index] = int(sampled_class)

                # update tqdm postfix only when K changes
                K = len(self.classes)
                if K != K_prev:
                    pbar.set_postfix_str(f"K={K}")
                    K_prev = K

            # compress class IDs at the end of the epoch
            self._reindex_classes()


    def predict(self, X_new: np.ndarray, min_membership: float = 0.01) -> np.ndarray:
        """
        Predict the class labels for the new data points.

        Args:
            X_new (np.ndarray): The new data points.
            min_membership (float): The minimum membership threshold. Defaults to 0.01.

        Returns:
            np.ndarray: The predicted class labels.

        Raises:
            ValueError: If no classes have been trained.
        """
        if not self.classes:
            raise ValueError("No classes have been trained. Run `run()` before predicting.")

        n_total = self.data.shape[0]
        valid_classes = {
            k: v for k, v in self.classes.items()
            if len(v.members) >= min_membership * n_total
        }

        if not valid_classes:
            raise ValueError("No classes meet the minimum membership threshold.")

        class_keys = np.array(list(valid_classes.keys()))
        class_tables = [valid_classes[k] for k in class_keys]
        class_log_priors = np.log([len(table.members) for table in class_tables])

        assignments = np.empty(X_new.shape[0], dtype=class_keys.dtype)

        for i, x in enumerate(tqdm(X_new, desc="Predicting")):
            nlls = np.array([
                table.predict(x) + log_prior
                for table, log_prior in zip(class_tables, class_log_priors)
            ])
            assignments[i] = class_keys[np.argmax(nlls)]

        return assignments