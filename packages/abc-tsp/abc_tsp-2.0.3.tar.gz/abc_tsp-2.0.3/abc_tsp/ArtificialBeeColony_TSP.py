"""
File: ArtificialBeeColony.py
Author: Angel Sanz Gutierrez
Contact: sanzangel017@gmail.com
GitHub: AngelS017
Description: All clases and function to apply ABC in the TSP
Version: 2.0.3

This file is the ABC algorithm for TSP, which is licensed under the MIT License.
See the LICENSE file in the project root for more information.
"""

import numpy as np
import math
import random
from tqdm import tqdm
import time
import itertools
from joblib import Parallel, delayed

from numba import njit

@njit
def _distance_path_numba(path, distance_matrix):
    total_distance = 0 
    length_path = len(path) - 1
    for i in range(length_path):
        total_distance += distance_matrix[path[i], path[i + 1]]
    return total_distance

class Bee:
    def __init__(self, role, random_path, mutation_strategy, mutation_params) -> None:
        self.role = role
        self.path = np.asarray(random_path, dtype=np.int32)
        # Use to select the cities to mutation startegies, except the first one and the last one
        self.path_len = len(random_path) - 2 
        self.path_distance = 0
        self.trial = 0
        self.mutation_strategy = self._select_mutation_strategy(mutation_strategy)
        self.mutation_params = mutation_params
 

    def _select_mutation_strategy(self, mutation_strategy):
        """Selects the appropriate mutation strategy based on the provided strategy name.

        Parameters
        ----------
        self : Bee
            The instance of the bee.

        mutation_strategy : str
            The name of the mutation strategy to be used. Must be one of the keys 
            in the dictionary all_mutation_strategies.

        Returns
        -------
        function
            The mutation function corresponding to the selected strategy.

        """
        all_mutation_strategies = {
            'swap': self.swap,
            'insertion': self.insertion,
            'k_opt':self.k_opt
        }
        return all_mutation_strategies[mutation_strategy]

    @staticmethod
    def swap(len_path, path, **mutation_params):
        """Compute the new path, using two different indexes (except the first and the last) of the 
           actual path and change its values.

        Parameters
        ----------
        len_path : int
            The len of the path - 2, is needed to select the possible indexes for the swap method.
        
        path : array-like
            The actual path that conteins all the points, where the start and the end is the same point.

        mutation_params : dict
            A dictionary containing the following keys:
                - None

        Returns
        -------
        new_path: The new path.

        """
        new_path = path.copy()

        # Other way, but slower: random_index, random_index_2 = sorted(random.sample(range(1, len_path), 2))
        random_index = random.randint(1, len_path)
        random_index_2 = random.randint(1, len_path)
        while random_index == random_index_2:
            random_index_2 = random.randint(1, len_path)
        
        new_path[random_index], new_path[random_index_2] = new_path[random_index_2], new_path[random_index]
        
        return [new_path]

    @staticmethod
    def insertion(len_path, path, **mutation_params):
        """
        
        Parameters
        ----------
        len_path : int
            The len of the path - 2, is needed to select the possible indexes for the insertion method.

        path : array-like
            The actual path that conteins all the points, where the start and the end is the same point.

        mutation_params : dict
            A dictionary containing the following keys:
                - None

        Returns
        -------
        new_path: The new path.

        """
        new_path = path.copy()

        random_index = random.randint(1, len_path)
        random_index_2 = random.randint(1, len_path)
        while random_index == random_index_2:
            random_index_2 = random.randint(1, len_path)

        #value = new_path[random_index]
        #new_path = np.delete(new_path, random_index)
        #new_path = np.insert(new_path, random_index_2, value)
        new_path = np.concatenate((new_path[:random_index], new_path[random_index+1:random_index_2], [new_path[random_index]], new_path[random_index_2:]))
        
        return [new_path]

    @staticmethod
    def k_opt(len_path, path, **mutation_params):
        """Apply the k-opt method for creating a new path, where the k means the number of
           edges that is going to be remove in order to create the new conections for the path.

           Steps:
               1. Generate the random indexes for the methos, the init and end of these values can´t be
                  the first and last position of the path, taht why it starts at 1 and ends at len(path) - 2
               2. Create the segments of the path with the random indexes generated.
               3. Save the middle segments of the path, this are the ones that will be use for the k-opt method.
               4. Crete all the possible combinations for the new connections of the segments (the new edges)
               5. Create all the possibles paths.

        Parameters
        ----------
        len_path : int
            The len of the path - 2, is needed to select the possible indexes for the k_opt method.

        path : array-like
            The actual path that conteins all the points, where the start and the end is the same point.

        mutation_params : dict 
            A dictionary containing the following keys:
                - k : int
                    The number of the k-opt method that is going to perform depending of the role of the bee

        Returns
        -------
        new_path: The new path.

        """
        # Get the k value depending of the role, because maybe k_employed or k_onlooker have different values
        k = mutation_params["k_" + mutation_params["bee_role"]]

        random_index = sorted(random.sample(range(1, len_path), k))

        segments = [path[:random_index[0]+1]]
        segments.extend(path[random_index[i]+1:random_index[i+1]+1] for i in range(k-1))
        segments.append(path[random_index[-1]+1:])

        middle_segments = [[segment, segment[::-1]] for segment in segments[1:-1]]

        possible_permutations = list(itertools.chain(itertools.product(*middle_segments), itertools.product(*middle_segments[::-1])))
        
        new_path = [np.concatenate((segments[0], *perm, segments[-1])) for perm in possible_permutations]
        new_path = new_path[1:]

        return new_path


    def mutate_path(self, distance_matrix):
        """

        Parameters
        ----------
        self : Bee
            The instance of the bee.

        distance_matrix: array-like
            The matrix that conteins the euclidian distance between each point.
        
        Returns
        -------
        best_path : The best path found during the generation of the new solution

        """

        all_paths = self.mutation_strategy(self.path_len, self.path, **self.mutation_params)
        best_path = min(all_paths, key=lambda path: self.distance_path(path, distance_matrix))

        return best_path
    
    def distance_path(self, path, distance_matrix):
        """Compute the distance of all the points in the path.

        Parameters
        ----------
        self : Bee
            The instance of the bee. 

        path : array-like
            The actual path that conteins all the points, where the start and the end is the same point.
        
        distance_matrix: array-like
            The matrix that conteins the euclidian distance between each point.

        Returns
        -------
        distance: The total distance of the path.

        """
        #return np.sum(distance_matrix[path[:-1], path[1:]])
        return _distance_path_numba(path, distance_matrix)



class ArtificialBeeColonyOptimizer:
    def __init__(self, ini_end_city, population, employed_percentage, limit, epochs, distance_matrix, employed_mutation_strategy, onlooker_mutation_strategy, 
                 mutation_params=None, seed=1234, verbose=1):
        all_stategies = ['swap', 'insertion', 'k_opt']
        # Check that all parameters have the correct values
        assert ini_end_city < distance_matrix.shape[0], "You must choose a correct city"
        assert 0.1 <= employed_percentage <= 0.9, "The value of employed_percentage must be between 0.1 and 0.9"
        assert epochs > 0, "The number of epochs must be greater than 0"
        assert employed_mutation_strategy in all_stategies, "Unknown employed mutation strategy, must be one of theese: " + ', '.join(all_stategies)
        assert onlooker_mutation_strategy in all_stategies, "Unknown onlooker mutation strategy, must be one of theese: " + ', '.join(all_stategies)

        if employed_mutation_strategy == 'k_opt':
            assert mutation_params['k_employed'] >= 2, "The value of k_employed for k_opt must be 2 or more"
        if onlooker_mutation_strategy == 'k_opt':
            assert mutation_params['k_onlooker'] >= 2, "The value of k_onlooker for k_opt must be 2 or more"

        np.random.seed(seed)
        random.seed(seed)

        self.ini_end_city = ini_end_city
        self.population = population
        self.employed_percentage = employed_percentage
        self.num_employed_bees = math.floor(population * employed_percentage)
        self.limit = limit
        self.epochs = epochs
        self.distance_matrix = distance_matrix
        self.employed_mutation_strategy = employed_mutation_strategy
        self.onlooker_mutation_strategy = onlooker_mutation_strategy
        self.mutation_params = mutation_params
        self.verbose = verbose

        # Trade off time-memory
        self.num_cities = self.distance_matrix.shape[0]
        self.other_cities = np.delete(np.arange(self.num_cities), self.ini_end_city)
        
        # Execute always the last
        self.colony = self.initialize_colony_with_roles()
        
        
    def initialize_colony_with_roles(self):
        """

        Parameters
        ----------
        self : ArtificialBeeColonyOptimizer
            The instance of the optimizer that manages the bee colony. 

        Returns
        -------
        colony : 

        """

        colony = []
        for i in range(self.population):
            #random_path = np.insert(np.random.permutation(self.other_cities), [0, len(self.other_cities)], self.ini_end_city)
            
            random_path = np.empty(len(self.other_cities) + 2, dtype=np.int32)
            random_path[0], random_path[-1] = self.ini_end_city, self.ini_end_city
            random_path[1:-1] = np.random.permutation(self.other_cities)
            
            if i >= self.num_employed_bees:
                onlooker_mutation_params = self.mutation_params.copy()
                onlooker_mutation_params['bee_role'] = 'onlooker'

                bee = Bee('onlooker', random_path, self.onlooker_mutation_strategy, onlooker_mutation_params)
            else:
                employed_mutation_params = self.mutation_params.copy()
                employed_mutation_params['bee_role'] = 'employed'

                bee = Bee('employed', random_path, self.employed_mutation_strategy, employed_mutation_params)
                
            bee.path_distance = bee.distance_path(bee.path, self.distance_matrix)
            colony.append(bee)

        return colony

    def employed_bee_behavior(self, bee):
        """The bee will perform the employed behavior, in which a new path is generated and 
           if the new path distance is better than the old one the path and his distance is 
           actualized in the bee. The number of trials increase only when the new distance is worse.

        Parameters
        ----------
        self : ArtificialBeeColonyOptimizer
            The instance of the optimizer that manages the bee colony. 

        bee : Bee
            The bee of the colony which is going to perform the employed behavior.

        Returns
        -------
        bee : The bee of the colony with updated parameters.

        """
        new_path = bee.mutate_path(self.distance_matrix)
        new_path_distance = bee.distance_path(new_path, self.distance_matrix)
        
        if new_path_distance < bee.path_distance:
            bee.path = new_path
            bee.path_distance = new_path_distance
            bee.trial = 0
        else:
            bee.trial += 1

    def calculate_probabilities(self):
        """Compute the probability of choosing each solution in the colony, where the distance path of
           each bee is divided by the sum of all distances in the colony

        Parameters
        ----------
        self : ArtificialBeeColonyOptimizer
            The instance of the optimizer that manages the bee colony. 

        Returns
        -------
        probabilities_bee_solution : The array of probabilities.

        """

        path_distances = np.array([bee.path_distance for bee in self.colony])
        fitness = 1 / path_distances
        return fitness / np.sum(fitness)

    def roulette_wheel_selection(self, probabilities):
        """Apply the roulet wheel selction to choose the best solution in the colony 
           for the onlooker bee

        Parameters
        ----------
        self : ArtificialBeeColonyOptimizer
            The instance of the optimizer that manages the bee colony. 

        probabilities : array-like
            The array of probabilities.

        Returns
        -------
        bee : The best bee to choose in the colony

        """

        return self.colony[np.random.choice(len(probabilities), p=probabilities)]
    
        # Another way to make roulette wheel selection, more interpretable but more computationally expensive:
        """
        cumulative_probabilities = np.cumsum(probabilities)
        r = np.random.rand()
        for index, cumulative_probability in enumerate(cumulative_probabilities):
            if r < cumulative_probability:
                return self.colony[index]
        return self.colony[-1]
        """
       

    def onlooker_bee_behavior(self, bee, probabilities_bee_solution):
        """The bee will perform the onlooker behavior, in which a possible solution will be 
            choosen if a random numeber is lower than the probability of that solution 
            (the solutions with high probability will be the ones most likely to be chosen) then
            a new path is generated and if the new path distance is better than the old one 
            the path and his distance is actualized in the bee. The number of trials increase 
            only when the new distance is worse.

        Parameters
        ----------
        self : ArtificialBeeColonyOptimizer
            The instance of the optimizer that manages the bee colony.

        bee : Bee
            The bee of the colony which is going to perform the employed behavior.
        
        probabilities_bee_solution : array-like
            The array of probabilities of all bees in the colony.

        Returns
        -------
        None
            This method updates the bee 

        """

        best_bee_colony = self.roulette_wheel_selection(probabilities_bee_solution)

        # Create a new path from the best bee found (path) local search
        new_path = best_bee_colony.mutate_path(self.distance_matrix)
        new_path_distance = best_bee_colony.distance_path(new_path, self.distance_matrix)
        
        if new_path_distance < best_bee_colony.path_distance:
            bee.path = new_path
            bee.path_distance = new_path_distance
            bee.trial = 0
        else:
            # Update the current onlooker bee with the best solution found until now
            # because the new posible solution is worst
            bee.path = best_bee_colony.path
            bee.path_distance = best_bee_colony.path_distance

            bee.trial += 1

    def scout_bee_behavior(self):
        """The bee will perform the scout behavior, where all the bees in the 
            colony that have passed the threshold of trials have initialized 
            their parameters.

        Parameters
        ----------
        self : ArtificialBeeColonyOptimizer
            The instance of the optimizer that manages the bee colony.

        Returns
        -------
        None

        """

        for bee in self.colony[:self.num_employed_bees]:
            if bee.trial > self.limit:
                #random_path = np.insert(np.random.permutation(self.other_cities), [0, len(self.other_cities)], self.ini_end_city)
                
                random_path = np.empty(len(self.other_cities) + 2, dtype=np.int32)
                random_path[0], random_path[-1] = self.ini_end_city, self.ini_end_city
                random_path[1:-1] = np.random.permutation(self.other_cities)

                bee.trial = 0
                bee.path = random_path
                bee.path_distance = bee.distance_path(bee.path, self.distance_matrix)

    
    def find_best_path(self):
        """Find the best path among all the bees in the colony and also the sitance of
           that path.

        Parameters
        ----------
        self : ArtificialBeeColonyOptimizer
            The instance of the optimizer that manages the bee colony. 

        Returns
        -------
        path : The best path found among all the bees in the colony
        path_distance : The total distance of the best path found

        """

        min_bee = min(self.colony, key=lambda bee: bee.path_distance)
        return min_bee.path, min_bee.path_distance

    def fit(self, disable_progress_bar=False):
        """Train the ABC algorithm to find the best path in the TSP.

        Parameters
        ----------
        self : ArtificialBeeColonyOptimizer
            The instance of the optimizer that manages the bee colony.
        
        disable_progress_bar : bool
            Wether or not to disable the progress bar of the trining process

        Returns
        -------
        execution_time : float 
            The time taken to train the ABC model.
        
        paths_distances : list
            The distances of all the paths founds during training.
        
        final_best_path: list
            The best path (sequence of cities) found by the ABC algorithm in this run.
            
        final_best_path_distance: float
            The total distance of the best path found during this run.

        """

        start = time.time()

        paths_distances = []

        for _ in tqdm(range(self.epochs), desc="Training Progress", unit="epoch", disable=disable_progress_bar):
            for employed_index in range(self.num_employed_bees):
                self.employed_bee_behavior(self.colony[employed_index])
            
            probabilities_bee_solution = self.calculate_probabilities()
            
            for onlooker_index in range(self.num_employed_bees, self.population):
                self.onlooker_bee_behavior(self.colony[onlooker_index], probabilities_bee_solution)
                
            self.scout_bee_behavior()

            _, best_path_distance = self.find_best_path()
            paths_distances.append(best_path_distance)

        final_best_path_distance = np.min(paths_distances)
        final_best_path, _ = self.find_best_path()
        if self.verbose == 1:
            print(f"Params:\n\t("
                  f"ini_end_city={self.ini_end_city}, "
                  f"population={self.population}, "
                  f"epochs={self.epochs},",
                  f"limit={self.limit},",
                  f"employed_percentage={self.employed_percentage},",
                  f"onlooker_percentage={1-self.employed_percentage})"
                )
            print("\nMin path distance: ", final_best_path_distance)
            print("The best path found is: \n", final_best_path)

        end = time.time()
        execution_time = end - start

        return execution_time, paths_distances, final_best_path, final_best_path_distance

    @staticmethod
    def run_single_params(ini_end_city, distance_matrix, params):
        """Train the ABC algorithm using a specific set of hyperparameters.

        Parameters
        ----------
        ini_end_city : int
            The index of the city where the path is going to start and end. This is used to ensure that 
            the generated paths in the optimization start and finish at the same city.
        
        distance_matrix: array-like
            The matrix that conteins the euclidian distance between each point.

        param_grid: dict
            A dictionary where the keys are the hyperparameter names (e.g., 'population', 'employed_percentage') 
            and the values of each hyperparameter to fit the ABC algorithm.


        Returns
        -------
        params: dict
            The same hyperparameters used for this specific run of the ABC algorithm.
        
        final_best_path: list
            The best path found by the ABC algorithm in this run.
            
        final_best_path_distance: float
            The total distance of the best path found during this run.

        """

        abc_optimizer = ArtificialBeeColonyOptimizer(
            ini_end_city=ini_end_city,
            population=params["population"],
            employed_percentage=params["employed_percentage"],
            limit=params["limit"],
            epochs=params["epochs"],
            distance_matrix=distance_matrix,
            employed_mutation_strategy=params["employed_mutation_strategy"],
            onlooker_mutation_strategy=params["onlooker_mutation_strategy"],
            mutation_params=params["mutation_params"],
            verbose=0
        )

        _, _, final_best_path, final_best_path_distance = abc_optimizer.fit(disable_progress_bar=True)

        return params, final_best_path, final_best_path_distance

    @staticmethod
    def grid_search_abc(distance_matrix, ini_end_city, param_grid, n_jobs=1, refit=False):
        """
        Parameters
        ----------
        distance_matrix: array-like
            The matrix that conteins the euclidian distance between each point.

        ini_end_city : int
            The index of the city where the path is going to start and end. This is used to ensure that 
            the generated paths in the optimization start and finish at the same city.

        param_grid: dict
            A dictionary where the keys are the hyperparameter names (e.g., 'population', 'employed_percentage') 
            and the values are lists of possible values for those hyperparameters. The grid search will 
            try all combinations of these values.

        n_jobs: int, optional, default=1
            The number of jobs to run in parallel for the grid search. If `n_jobs` is set to -1, it uses all 
            available processors. If it is set to 1, the grid search will run sequentially.

        refit: bool, optional, default=False
            If True, the model will be refit using the best hyperparameters found during the grid search. 
            The final results, including the execution time, paths, and distances, will be included in the output.

        Returns
        -------
        output: dict
            A dictionary containing the following keys:
            
            - 'best_params': dict
                The combination of hyperparameters that achieved the best performance (i.e., minimized the path distance).
            
            - 'best_distance': float
                The shortest path distance found during the grid search.
            
            If refit is set to True, additional keys are included:
            
            - 'execution_time': float
                The time taken to refit the model using the best parameters.
            
            - 'paths_distances': list
                A list of distances for each path iteration during the refitting process.
            
            - 'final_best_path': list
                The best path found after refitting the model using the optimal hyperparameters.
            
            - 'final_best_path_distance': float
                The distance of the best path found after refitting the model.

        """
        mutation_strategies_params = {
            'k_opt': ['k_employed', 'k_onlooker'],
            'swap': [],
            'insertion': []
        }

        keys_to_keep = ['population', 'employed_percentage', 'limit', 'epochs', 
                        'employed_mutation_strategy', 'onlooker_mutation_strategy', 
                        'mutation_params']

        best_distance = np.inf
        best_params = None

        keys = param_grid.keys()
        values = param_grid.values()
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

        final_combinations = []
        for test in combinations:
            mutation_params = {}

            # Employed
            employed_strategy = test['employed_mutation_strategy']
            
            # Get the parameters that need that employed mutation strategy
            employed_params = mutation_strategies_params.get(employed_strategy, [])
            # Check if the parameters neeeded for the strategy is in the dictionary and is for the employed bees
            for param in employed_params:
                if param in test and "employed" in param:
                    mutation_params[param] = test.pop(param)

            # Onlooker
            onlooker_strategy = test['onlooker_mutation_strategy']
            
            # Get the parameters that need that employed mutation strategy
            onlooker_params = mutation_strategies_params.get(onlooker_strategy, [])
            # Check if the parameters neeeded for the strategy is in the dictionary and is for the employed bees
            for param in onlooker_params:
                if param in test and "onlooker" in param:
                    mutation_params[param] = test.pop(param)

            # Add the mutation_params dictionary as needed
            test['mutation_params'] = mutation_params

            # Remove the parameters of the other mutation strategies that are not used
            test = {key: test[key] for key in keys_to_keep}

            if test not in final_combinations:
                final_combinations.append(test)

        print("Number of experimets: ", len(final_combinations))
        results = Parallel(n_jobs=n_jobs)(delayed(ArtificialBeeColonyOptimizer.run_single_params)(ini_end_city, distance_matrix, params) 
                                          for params in tqdm(final_combinations, desc="Grid Search complete"))
        
        for params, _, distance in results:
            if distance < best_distance:
                best_distance = distance
                best_params = params

        output = {
            'best_params': best_params,
            'best_distance': best_distance
        }

        if refit:
            abc_optimizer = ArtificialBeeColonyOptimizer(
                ini_end_city=ini_end_city,
                population=best_params["population"],
                employed_percentage=best_params["employed_percentage"],
                limit=best_params["limit"],
                epochs=best_params["epochs"],
                distance_matrix=distance_matrix,
                employed_mutation_strategy=best_params["employed_mutation_strategy"],
                onlooker_mutation_strategy=best_params["onlooker_mutation_strategy"],
                mutation_params=best_params["mutation_params"],
                verbose=0
            )

            execution_time, paths_distances, final_best_path, final_best_path_distance = abc_optimizer.fit()

            output = ({
                'best_params': best_params,
                'execution_time': execution_time,
                'final_best_path': final_best_path,
                'final_best_path_distance': final_best_path_distance,
                'paths_distances': paths_distances,
            })

        return output

    def print_colony(self):
        """Print some information such as roles, path distance and trials of each bee in the colony.

        Parameters
        ----------
        self : ArtificialBeeColonyOptimizer
            The instance of the optimizer that manages the bee colony.

        Returns
        -------

        """
        for index, bee in enumerate(self.colony):
            print("Bee ", index, ": ", bee.role)
            print("Path distance: ", bee.path_distance)
            print("Trial: ", bee.trial)
            print("__________\n")

