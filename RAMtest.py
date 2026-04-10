from pmlb import fetch_data
from sklearn.model_selection import train_test_split
import numpy as np
import gplearn
from gplearn.genetic import SymbolicRegressor
from sklearn.utils.random import check_random_state
from memory_profiler import memory_usage
import csv
import os
import multiprocessing

def ram_test(cache_size, X_train, y_train):
    est_gp = SymbolicRegressor(population_size=1000,
                        generations=500, tournament_size=20,
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
    est_gp.fit(X_train, y_train)
    print("Fitting result = ",est_gp._program)

def worker(cache_size, X_train, y_train, random_state_data, queue):
    mem_usage = memory_usage((ram_test, (cache_size, X_train, y_train)), interval=0.1, timeout=None, max_iterations=None)
    avg_mem = np.mean(mem_usage)
    max_mem = np.max(mem_usage)
    queue.put({'cache_size': cache_size, 'avg_ram_mib': round(avg_mem, 3), 'max_ram_mib': round(max_mem, 3), 'random_state_data': random_state_data})
    
if __name__ == "__main__":
    cache_sizes = [100, 500, 1000, 5000,10000]
    csv_file = 'mem_results_PMLB_215_2dplanes_ARC.csv'

    with open(csv_file, 'w', newline='') as f:
        fieldnames = ['cache_size', 'avg_ram_mib', 'max_ram_mib', 'random_state_data']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        # Write the header
        writer.writeheader()
        
        for random_state_data in range(0,8):
            features, labels = fetch_data('344_mv', return_X_y=True, local_cache_dir='./')
            # local_cache_dir so that you do not need to redownload the pmlb datasets again
            X_train, X_test, y_train, y_test = train_test_split(features, labels,
                                                                train_size=0.75,
                                                                test_size=0.25,
                                                                random_state=random_state_data)

            queue = multiprocessing.Queue()

            for cache_size in cache_sizes:
                p = multiprocessing.Process(target=worker, args=(cache_size, X_train, y_train, random_state_data, queue))
                p.start()
                p.join()
                result = queue.get()
                print(f"cache_size = {result['cache_size']}: Avg RAM = {result['avg_ram_mib']:.3f} MiB, Max RAM = {result['max_ram_mib']:.3f} MiB, random_state_data = {random_state_data}")
                writer.writerow(result)

    print(f"\nAll results have been written to '{os.path.abspath(csv_file)}'.")