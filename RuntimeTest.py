from pmlb import fetch_data
from sklearn.model_selection import train_test_split
import numpy as np
import gplearn
from gplearn.genetic import SymbolicRegressor
from sklearn.utils.random import check_random_state
from cProfile import Profile
from pstats import Stats, SortKey
import csv
import os
from sklearn.metrics import r2_score, mean_absolute_error

def RuntimeTest(cache_size, X_train, X_test, y_train, y_test):
    est_gp = SymbolicRegressor(population_size=5000,
                        generations=100, tournament_size=100,
                        stopping_criteria=0.,
                        function_set=('add', 'sub', 'mul', 'div'),
                        init_method='half and half',
                        p_crossover=0.9, p_subtree_mutation=0.01,
                        p_hoist_mutation=0.01, p_point_mutation=0.01,
                        p_point_replace=0.05,
                        verbose=1,
                        parsimony_coefficient=0.001,
                        random_state=0,
                        cache_type='ARC',
                        cache_size=cache_size)
    
    print(f"Version: {gplearn.__version__}")
    with Profile() as profile:
        est_gp.fit(X_train, y_train)
    print(f"Fitting result: {est_gp._program}")

    stats = Stats(profile)
    stats.strip_dirs().sort_stats(SortKey.CUMULATIVE)

    # print("---- The cumulative time of the execute function ----")
    stats.print_stats('execute')
    # stats.print_callees('execute')

    # print("\n---- Global Performance Analysis Information ----")
    # stats.print_stats()
    overall_runtime = stats.total_tt
    cumtime_execute = sum(info[3] for func, info in stats.stats.items() if func[2] == 'execute')
    overall_runtime = round(overall_runtime, 3)
    cumtime_execute = round(cumtime_execute, 3)
    
    y_pred = est_gp.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    print(f"Test R^2 Score: {r2}")

    mae = mean_absolute_error(y_test, y_pred)
    print(f"Test Mean Absolute Error (MAE): {mae}")
    return overall_runtime, cumtime_execute, r2, mae

if __name__ == "__main__":
    cache_sizes = [100, 500, 1000, 5000, 10000]
    csv_file = './runtime_results_PMLB_503_wind_ARC.csv'

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['cache_size', 'overall_runtime', 'cumtime_execute', 'random_state_data', 'r2_score', 'mae'])
        for random_state_data in range(0,8):
            features, labels = fetch_data('225_puma8NH', return_X_y=True, local_cache_dir='./')
            # local_cache_dir so that you do not need to redownload the pmlb datasets again
            X_train, X_test, y_train, y_test = train_test_split(features, labels,
                                                                train_size=0.75,
                                                                test_size=0.25,
                                                                random_state=random_state_data)

            for cache_size in cache_sizes:
                overall_runtime, cumtime_execute, r2, mae = RuntimeTest(cache_size, X_train, X_test, y_train, y_test)
                print(f"\nrandom_state_data = {random_state_data}, cache_size = {cache_size}, overall_runtime = {overall_runtime}, cumtime_execute = {cumtime_execute}, r2_score = {r2}, mae = {mae}")
                writer.writerow([cache_size, overall_runtime, cumtime_execute, random_state_data, r2, mae])
    print(f"\nAll results have been written to {csv_file}")