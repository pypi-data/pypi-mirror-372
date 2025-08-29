import torch

def check_gpus():
    if torch.cuda.is_available():
        num_gpus = torch.cuda.device_count()
        print(f"GPUs are active. {num_gpus} GPU(s) detected.")
        for i in range(num_gpus):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    else:
        print("No GPUs detected. Running on CPU.")

if __name__ == "__main__":
    check_gpus()