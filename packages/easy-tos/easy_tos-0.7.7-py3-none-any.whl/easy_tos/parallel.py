import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from tqdm import tqdm
import traceback

def multi_process_tasks(data_list, 
                       func,
                       map_func = None,
                       max_workers=os.cpu_count(),
                       desc='Processing objects',
                       verbose=False
    ):
    results = {}
    def _id(input):
        return input
    
    if map_func is None:
        map_func = _id
        
    with tqdm(total=len(data_list)) as pbar:
        future_to_path = {}
        success_count = 0
        fail_count = 0 
        pbar.set_description(desc)
        pbar.set_postfix({'✅ Success': success_count, '❌ Fail': fail_count})
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            for data in data_list:
                taskID = map_func(data)
                future_to_path[executor.submit(func, data)] = taskID
            for future in as_completed(future_to_path):
                taskID = future_to_path[future]
                try:
                    result = future.result()
                    success_count += 1
                    if result is not None:
                        results[taskID] = result
                except Exception as exc:
                    fail_count += 1
                    print(f'{taskID} generated an exception: {exc}')
                    if verbose:
                        traceback.print_exc()
                finally:
                    pbar.update(1)
                    pbar.set_postfix({'✅ Success': success_count, '❌ Fail': fail_count})
    print(f"\nAll Done! ✅ Success: {success_count} | ❌ Fail: {fail_count}")
    return results


def multi_thread_tasks(data_list, 
                       func,
                       map_func = None,
                       max_workers=os.cpu_count(),
                       desc='Processing objects',
                       verbose=False
    ):
    results = {}
    def _id(input):
        return input
    
    if map_func is None:
        map_func = _id
        
    with tqdm(total=len(data_list)) as pbar:
        future_to_path = {}
        success_count = 0
        fail_count = 0 
        pbar.set_postfix({'✅ Success': success_count, '❌ Fail': fail_count})
        pbar.set_description(desc)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for data in data_list:
                taskID = map_func(data)
                future_to_path[executor.submit(func, data)] = taskID
            for future in as_completed(future_to_path):
                taskID = future_to_path[future]
                try:
                    result = future.result()
                    success_count += 1
                    if result is not None:
                        results[taskID] = result
                except Exception as exc:
                    fail_count += 1
                    print(f'{taskID} generated an exception: {exc}')
                    if verbose:
                        traceback.print_exc()
                finally:
                    pbar.update(1)
                    pbar.set_postfix({'✅ Success': success_count, '❌ Fail': fail_count})
    print(f"\nAll Done! ✅ Success: {success_count} | ❌ Fail: {fail_count}")
    return results

def split_task_to_nodes(all_uids, total_nodes, GPUs_per_node, verbose=False):
    # Split UIDs among nodes
    node_uid_list = []
    chunk_size = len(all_uids) // total_nodes
    remainder = len(all_uids) % total_nodes

    start = 0
    for i in range(total_nodes):
        extra = 1 if i < remainder else 0  # Distribute remainder across first few nodes
        end = start + chunk_size + extra
        node_uid_list.append(all_uids[start:end])
        if verbose:
            print(f"Node {i}: {start} - {end-1} UIDs assigned.")
        start = end

    # Split UIDs among GPUs within each node
    gpu_uid_list_per_node = []
    for i, node_uids in enumerate(node_uid_list):
        gpu_uid_list = []
        chunk_size_gpu = len(node_uids) // GPUs_per_node
        remainder_gpu = len(node_uids) % GPUs_per_node

        start = 0
        for j in range(GPUs_per_node):
            extra_gpu = 1 if j < remainder_gpu else 0  # Distribute remainder across GPUs
            end = start + chunk_size_gpu + extra_gpu
            gpu_uid_list.append(node_uids[start:end])
            if verbose:
                print(f"Node {i} GPU {j}: {start} - {end-1} UIDs assigned.")
            start = end
        gpu_uid_list_per_node.append(gpu_uid_list)

    # Return the list for the specified node and GPU
    return gpu_uid_list_per_node