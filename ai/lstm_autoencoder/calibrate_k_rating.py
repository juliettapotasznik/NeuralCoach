import argparse
import os
import sys
import base64
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from autoencoder_service import prepare_data_for_model, calculate_joint_errors_and_ratings 


def read_csv_as_b64(csv_path: str) -> str:
    with open(csv_path, 'rb') as f:
        csv_bytes = f.read()
    return base64.b64encode(csv_bytes).decode('utf-8')


def compute_per_frame_mse_for_csv(csv_path: str, seq_len: int, step: int) -> np.ndarray:
    csv_b64 = read_csv_as_b64(csv_path)
    (
        windows,
        window_starts,
        num_frames,
        _,
        _,
        _,
        _,
    ) = prepare_data_for_model(csv_b64, seq_len=seq_len, step=step)
    if windows.size == 0:
        return np.array([])
    _, _, _, per_frame_mse, _ = calculate_joint_errors_and_ratings(windows, window_starts, num_frames, seq_len=seq_len)
    return np.array(per_frame_mse)


def iter_csv_files(root_dir: str):
    for name in sorted(os.listdir(root_dir)):
        if name.lower().endswith('.csv'):
            yield os.path.join(root_dir, name)


def main():
    parser = argparse.ArgumentParser(description='Calibrate K_RATING using baseline (correct) CSVs.')
    parser.add_argument('--dir', required=True, help='Directory with correct exercise CSV files')
    parser.add_argument('--percentile', type=float, default=95.0, help='Percentile of MSE to target (default: 95)')
    parser.add_argument('--target-rating', type=float, default=75.0, help='Desired rating at that percentile (default: 75)')
    parser.add_argument('--seq-len', type=int, default=30, help='Sequence length used in the model (default: 30)')
    parser.add_argument('--step', type=int, default=5, help='Step between windows (default: 5)')
    args = parser.parse_args()

    csv_dir = args.dir
    if not os.path.isdir(csv_dir):
        print(f"Error: directory not found: {csv_dir}", file=sys.stderr)
        sys.exit(1)

    all_mse = []
    total_files = 0
    used_files = 0

    for csv_path in iter_csv_files(csv_dir):
        total_files += 1
        try:
            per_frame_mse = compute_per_frame_mse_for_csv(csv_path, seq_len=args.seq_len, step=args.step)
            if per_frame_mse.size > 0:
                all_mse.append(per_frame_mse)
                used_files += 1
        except Exception as e:
            print(f"Warning: failed on {csv_path}: {e}", file=sys.stderr)

    if not all_mse:
        print("Error: no usable MSE data collected. Check CSVs and model files.", file=sys.stderr)
        sys.exit(2)

    mse_concat = np.concatenate(all_mse)
    mse_p = float(np.percentile(mse_concat, args.percentile))

    # rating = 100 / (1 + K * mse)  =>  K = (100/R - 1) / mse
    K = (100.0 / args.target_rating - 1.0) / mse_p if mse_p > 0 else float('inf')

    print("Calibration summary:\n")
    print(f" - Input directory: {csv_dir}")
    print(f" - CSV files found: {total_files}, used: {used_files}")
    print(f" - Percentile: p{args.percentile}")
    print(f" - p{args.percentile} MSE: {mse_p:.6f}")
    print(f" - Target rating: {args.target_rating}")
    print(f" - Recommended K_RATING: {K:.6f}")


    print("\nK_RATING_VALUE_ONLY=", end="")
    print(f"{K:.6f}")


if __name__ == '__main__':
    main()

# python /Users/zosia/Documents/GitHub/RepRight/lstm_autoencoder/calibrate_k_rating.py \
#   --dir /Users/zosia/Documents/GitHub/RepRight/dataset_csv \
#   --percentile 95 \
#   --target-rating 75 \
#   --seq-len 30 \
#   --step 5