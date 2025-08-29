import subprocess

def print_cuda_memory(tag=""):
    import torch
    allocated = torch.cuda.memory_allocated() / 1024**2
    reserved = torch.cuda.memory_reserved() / 1024**2
    print(f"[{tag}] Allocated: {allocated:.2f} MB, Reserved: {reserved:.2f} MB")
    
    
def get_gpu_memory_info():
    """
    Print total, used, and free memory for each GPU.
    """
    try:
        output = subprocess.check_output([
            'nvidia-smi',
            '--query-gpu=index,name,memory.total,memory.used,memory.free',
            '--format=csv,noheader,nounits'
        ], encoding='utf-8')
        
        print("Available GPU memory per device:")
        print("-------------------------------")
        for line in output.strip().split('\n'):
            index, name, total, used, free = [x.strip() for x in line.split(',')]
            print(f"GPU {index} ({name}):")
            print(f"  Total Memory: {total} MiB")
            print(f"  Used Memory : {used} MiB")
            print(f"  Free Memory : {free} MiB\n")
    except subprocess.CalledProcessError as e:
        print("Error running nvidia-smi:", e)

def show_gpu_with_free_memory(threshold):
    """
    Print indices of GPUs with free memory >= threshold.
    """
    try:
        output = subprocess.check_output([
            'nvidia-smi',
            '--query-gpu=index,memory.free',
            '--format=csv,noheader,nounits'
        ], encoding='utf-8')

        for line in output.strip().split('\n'):
            index, free = [x.strip() for x in line.split(',')]
            if int(free) >= threshold:
                print(f"GPU {index} has {free} MiB free")
    except subprocess.CalledProcessError as e:
        print("Error running nvidia-smi:", e)

def get_gpu_id_list_with_free_memory(threshold):
    """
    Return a list of GPU indices with free memory >= threshold.
    """
    gpu_ids = []
    try:
        output = subprocess.check_output([
            'nvidia-smi',
            '--query-gpu=index,memory.free',
            '--format=csv,noheader,nounits'
        ], encoding='utf-8')

        for line in output.strip().split('\n'):
            index, free = [x.strip() for x in line.split(',')]
            if int(free) >= threshold:
                gpu_ids.append(int(index))
    except subprocess.CalledProcessError as e:
        print("Error running nvidia-smi:", e)
    return gpu_ids