from fastapi import FastAPI, Form, HTTPException
import pandas as pd
import numpy as np
import requests
import time
from tensorflow.keras.models import model_from_json
import base64, io
import os
import json
from pathlib import Path
import tensorflow as tf
import binascii
from metrics import (
        correlation_matrix, mae, cosine_similarity, dtw,
        skewness_and_kurtosis, anomaly_heatmap
    )
from datetime import datetime
from draw_keypoints import draw_skeleton_on_video

try:
    tf.config.set_visible_devices([], 'GPU')
    print("Using CPU for TensorFlow operations")
except:
    print("Could not configure TensorFlow devices")

app = FastAPI()

SEQ_LEN = 30
FEATURES = 57 
K_RATING = 0.748382  #calibrated on dataset: percentile=95 MSE=0.445405 -> rating=75
NUM_KEYPOINTS = 19
SKEL_VIDEO_DIR = Path("/app/user_videos_skel").resolve()
SKEL_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
EXTRINSICS_PATH = (Path(__file__).resolve().parent / "extrinsics.json").resolve()
with open(EXTRINSICS_PATH, "r") as extr_file:
    extrinsics = json.load(extr_file)
EXTR_R = np.array(extrinsics["R"], dtype=np.float32)
EXTR_T = np.array(extrinsics["t"], dtype=np.float32).reshape(3, 1)

BASE_DIR = Path(__file__).resolve().parent

try:
    with open(BASE_DIR / "lstm_architecture.json", "r") as f:
        model = model_from_json(f.read())

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.load_weights(BASE_DIR / "lstm_weights.weights.h5")
    print("Model loaded successfully")

    mean = np.load(BASE_DIR / "mean.npy")
    std = np.load(BASE_DIR / "std.npy")

except FileNotFoundError as e:
    raise RuntimeError(f"Required model artifact not found: {e.filename}") from e
except (OSError, ValueError) as e:
    raise RuntimeError(f"Failed to load LSTM model or weights: {e}") from e

joint_indices = {
    "left_shoulder": slice(15, 18), 
    "right_shoulder": slice(18, 21),
    "left_elbow": slice(21, 24),
    "right_elbow": slice(24, 27),
    "left_wrist": slice(27, 30),
    "right_wrist": slice(30, 33),
    "left_hip": slice(33, 36),
    "right_hip": slice(36, 39),
    "left_knee": slice(39, 42),
    "right_knee": slice(42, 45),
    "left_ankle": slice(45, 48),
    "right_ankle": slice(48, 51),
    "left_heel": slice(51, 54),
    "right_heel": slice(54, 57)
}

def build_prompt(joint_errors, exercise_name, per_frame_mse=None, per_frame_joint_mse=None, frame_ids=None, mse_threshold=0.445):
    high_deviation_joints = [name for name, val in joint_errors.items() if val >= mse_threshold]
    low_deviation_joints = [name for name, val in joint_errors.items() if val < mse_threshold]

    prompt = f"""You are a professional personal trainer analyzing the following exercise: {exercise_name}.

Rules you must follow strictly:
- Do NOT use greetings or sign-offs (e.g., no "Dear", no "Best regards").
- Do NOT reference past progress or history; speak only about the current recording/session.
- Use present tense, concise, practical coaching. Avoid filler and generic praise.
- Do NOT mention the words "MSE", "mean squared error", or "frame".
- Do NOT include any numbers or numeric scores.
- Focus ONLY on the joints listed as having significant deviation.
- Use qualitative wording like "noticeable issue", "seems off", "an anomaly is detected".
- Keep a supportive but objective tone.
- Do not use "Best regards,[Your name]" or any kind of greetings.
Joints with significant deviation (address these with actionable coaching):
"""
    if high_deviation_joints:
        for joint in high_deviation_joints:
            prompt += f"- {joint}\n"
    else:
        prompt += "- none\n"

    prompt += """

Joints with minor or no deviation (do NOT focus feedback on these, but you can mention them if you want to):
"""
    if low_deviation_joints:
        for joint in low_deviation_joints:
            prompt += f"- {joint}\n"
    else:
        prompt += "- none\n"

    prompt += """

Time-series context (do NOT quote numbers back; reason qualitatively over trends):
- Overall per-frame deviations are provided in a list (length equals number of frames).
- Per-joint per-frame deviations are also provided as lists per joint.
- Frame identifiers may be provided to help localize segments.

Use this time-series context only to identify rough segments where issues are likely occurring (e.g., "at the start", "midway", "towards the end"), and describe them without numbers.

Per-frame overall deviations (array):
{per_frame_mse}

Per-frame deviations by joint (dictionary of arrays):
{per_frame_joint_mse}

Frame identifiers (optional):
{frame_ids}

Now write a brief, personalized coaching note about the current session only. Do not use any numbers or the terms MSE/mean squared error. Focus on improving the listed high-deviation joints only, and reference segments qualitatively (e.g., early/middle/late) instead of giving numeric positions. No greeting, no sign-off, no comments about past progress.
"""
    return prompt

def prepare_data_for_model(csv_base64: str, seq_len: int = 30, step: int = 5):
    
    try:
        csv_bytes = base64.b64decode(csv_base64)
    except (binascii.Error, ValueError) as decode_error:
        raise HTTPException(status_code=400, detail="Invalid base64-encoded CSV payload.") from decode_error

    try:
        df = pd.read_csv(io.BytesIO(csv_bytes))
    except pd.errors.EmptyDataError as empty_error:
        raise HTTPException(status_code=400, detail="CSV file is empty.") from empty_error
    except pd.errors.ParserError as parser_error:
        raise HTTPException(status_code=400, detail=f"Malformed CSV data: {parser_error}") from parser_error

    original_frame_ids = None
    if 'frame_id' in df.columns:  
        original_frame_ids = df['frame_id'].to_list() 
        df = df.drop(columns=['frame_id']) 

    joint_0_cols = [col for col in df.columns if 'joint_0' in col]  
    joint_0 = df[joint_0_cols].values  
    joint_0_repeated = np.repeat(joint_0, repeats=57//3, axis=1)  
    centered = df.values - joint_0_repeated  
    centered = (centered - mean) / std

    windows = []
    window_starts = [] 
    for i in range(0, len(centered) - seq_len + 1, step):  
        window = centered[i:i+seq_len]  
        windows.append(window)
        window_starts.append(i)  
    windows = np.array(windows)

    num_frames = len(centered)

    return windows, window_starts, num_frames, original_frame_ids, df.values, joint_0


def calculate_joint_errors_and_ratings(windows, window_starts, num_frames, seq_len: int = 30):
    
    try:
        reconstructed = model.predict(windows, batch_size=32)
    except (ValueError, tf.errors.OpError) as predict_error:
        raise HTTPException(status_code=500, detail=f"Autoencoder inference failed: {predict_error}") from predict_error

    joint_errors = {}  
    per_frame_joint_mse = {} 
    joint_ratings = {}
    
    for name, joint_slice in joint_indices.items():  
        real_joint = windows[:, :, joint_slice] 
        recon_joint = reconstructed[:, :, joint_slice]  
        joint_sq_err = (real_joint - recon_joint) ** 2 

        joint_per_window_timestep_mse = np.mean(joint_sq_err, axis=2)  

        joint_sum = np.zeros(num_frames, dtype=np.float64)  
        joint_cnt = np.zeros(num_frames, dtype=np.int32) 
        for w_idx, start_idx in enumerate(window_starts):  
            per_frame_indices = np.arange(start_idx, start_idx + seq_len) 
            joint_sum[per_frame_indices] += joint_per_window_timestep_mse[w_idx]  
            joint_cnt[per_frame_indices] += 1  
        with np.errstate(divide='ignore', invalid='ignore'):
            joint_per_frame = np.divide(joint_sum, joint_cnt, out=np.zeros_like(joint_sum), where=joint_cnt>0)
            joint_per_frame_rating = 100 * (1 / (1 + K_RATING * joint_per_frame))  

        per_frame_joint_mse[name] = joint_per_frame.tolist()

        joint_errors[name] = float(np.mean(joint_per_frame[joint_cnt>0])) if np.any(joint_cnt>0) else 0.0  
        joint_ratings[name] = float(np.mean(joint_per_frame_rating[joint_cnt>0])) if np.any(joint_cnt>0) else 100.0  

    per_frame_mse = np.mean([np.array(per_frame_joint_mse[name]) for name in joint_indices.keys()], axis=0)

    return joint_errors, joint_ratings, per_frame_joint_mse, per_frame_mse, reconstructed


def reconstruct_reference_sequence(
    reconstructed_windows: np.ndarray,
    window_starts,
    num_frames: int,
    joint_0: np.ndarray,
    seq_len: int = 30,
) -> np.ndarray:
    feature_dim = reconstructed_windows.shape[2]
    sums = np.zeros((num_frames, feature_dim), dtype=np.float32)
    counts = np.zeros((num_frames, feature_dim), dtype=np.int32)
    for idx, start_idx in enumerate(window_starts):
        window = reconstructed_windows[idx]
        window_denorm = window * std + mean
        end_idx = start_idx + seq_len
        sums[start_idx:end_idx] += window_denorm
        counts[start_idx:end_idx] += 1
    with np.errstate(divide='ignore', invalid='ignore'):
        averaged = np.divide(sums, counts, out=np.zeros_like(sums), where=counts > 0)
    mask = counts.sum(axis=1) == 0
    for idx in range(1, num_frames):
        if mask[idx]:
            averaged[idx] = averaged[idx - 1]
    joint_0_repeated = np.repeat(joint_0, repeats=NUM_KEYPOINTS, axis=1)
    reference = averaged + joint_0_repeated
    return reference


def build_reference_pose_dict(reference_array: np.ndarray, frame_ids) -> dict[int, np.ndarray]:
    poses_by_frame = {}
    last_pose = None
    for idx, frame_id in enumerate(frame_ids):
        pose_flat = reference_array[idx]
        pose_matrix = pose_flat.reshape(NUM_KEYPOINTS, 3)
        pose_matrix = inverse_axes_and_rotation(pose_matrix)
        if not np.all(np.isfinite(pose_matrix)):
            if last_pose is None:
                continue
            pose_matrix = last_pose
        last_pose = pose_matrix
        poses_by_frame[int(frame_id)] = pose_matrix
    return poses_by_frame


def build_detected_pose_dict(original_values: np.ndarray, frame_ids) -> dict[int, np.ndarray]:
    poses_by_frame = {}
    last_pose = None
    for idx, frame_id in enumerate(frame_ids):
        pose_flat = original_values[idx]
        pose_matrix = pose_flat.reshape(NUM_KEYPOINTS, 3)
        pose_matrix = inverse_axes_and_rotation(pose_matrix)
        if not np.all(np.isfinite(pose_matrix)):
            if last_pose is None:
                continue
            pose_matrix = last_pose
        confidence = np.ones((NUM_KEYPOINTS, 1), dtype=np.float32)
        pose_with_conf = np.concatenate([pose_matrix, confidence], axis=1)
        poses_by_frame[int(frame_id)] = pose_with_conf
        last_pose = pose_matrix
    return poses_by_frame


def inverse_axes_and_rotation(pose_matrix: np.ndarray) -> np.ndarray:
    transformed = pose_matrix.copy()
    x_vals = transformed[:, 0].copy()
    y_vals = transformed[:, 1].copy()
    z_vals = transformed[:, 2].copy()
    transformed[:, 0] = y_vals
    transformed[:, 1] = -z_vals
    transformed[:, 2] = -x_vals
    pose_xyz = transformed.T
    pose_xyz = np.dot(EXTR_R, pose_xyz) + EXTR_T
    return pose_xyz.T


def ask_groq(prompt: str):

    start_time = time.perf_counter()

    api_url = "https://api.groq.com/openai/v1/chat/completions"
    api_key = os.getenv("GROQ_API_KEY")  

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "llama-3.1-8b-instant", 
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful AI personal trainer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 400,
        "temperature": 0.7,
        "top_p": 0.9,
        "stream": False
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            text = data["choices"][0]["message"]["content"]
        else:
            text = "No response generated."

        elapsed = time.perf_counter() - start_time
        print(f"\nGrok response time: {elapsed:.2f}s")
        return text.strip(), elapsed

    except requests.exceptions.Timeout as timeout_error:
        elapsed = time.perf_counter() - start_time
        print(f"Groq API timeout after {elapsed:.2f}s: {timeout_error}")
        raise HTTPException(status_code=504, detail="LLM service timeout.") from timeout_error
    except requests.exceptions.HTTPError as http_error:
        status_code = http_error.response.status_code if http_error.response else 502
        elapsed = time.perf_counter() - start_time
        print(f"Groq API HTTP error after {elapsed:.2f}s: {http_error}")
        if status_code in (401, 403):
            detail = "LLM service authentication failed."
        else:
            detail = f"LLM service returned an error (status {status_code})."
        raise HTTPException(status_code=status_code, detail=detail) from http_error
    except requests.exceptions.ConnectionError as connection_error:
        elapsed = time.perf_counter() - start_time
        print(f"Groq API connection error after {elapsed:.2f}s: {connection_error}")
        raise HTTPException(status_code=503, detail="LLM service unavailable.") from connection_error
    except requests.exceptions.RequestException as request_error:
        elapsed = time.perf_counter() - start_time
        print(f"Groq API request error after {elapsed:.2f}s: {request_error}")
        raise HTTPException(status_code=502, detail="Failed to contact LLM service.") from request_error

def compute_all_metrics(windows, reconstructed, per_frame_joint_mse, per_frame_mse, output_dir="../user_metrics"):

    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_file = os.path.join(output_dir, f"metrics_report_{timestamp}.txt")
    
    report_lines = []
    
    report_lines.append("=" * 80)
    report_lines.append("MODEL METRICS - REPORT")
    report_lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 80)
    
    report_lines.append("\n📊 MAE (Mean Absolute Error):")
    mae_value = mae(windows, reconstructed)
    report_lines.append(f"  Overall MAE: {mae_value:.6f}")
    
    report_lines.append("\n📈 Cosine Similarity:")
    try:
        cos_sim = cosine_similarity(windows, reconstructed)
        report_lines.append(f"  Overall: {cos_sim:.6f}")
    except Exception as e:
        report_lines.append(f"  Error: {e}")
    
    report_lines.append("\n⏱️  DTW (Dynamic Time Warping):")
    try:
        dtw_value = dtw(windows, reconstructed)
        report_lines.append(f"  Mean DTW distance: {dtw_value:.6f}")
    except Exception as e:
        report_lines.append(f"  Error: {e}")
    
    report_lines.append("\n🔗 MSE Error Correlation Matrix:")
    try:
        corr_matrix = correlation_matrix(per_frame_joint_mse)
        mean_corr = float(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean())
        report_lines.append(f"  Shape: {corr_matrix.shape}")
        report_lines.append(f"  Mean correlation: {mean_corr:.6f}")
        
        triu_indices = np.triu_indices_from(corr_matrix.values, k=1)
        max_corr_idx = np.argmax(corr_matrix.values[triu_indices])
        max_i, max_j = triu_indices[0][max_corr_idx], triu_indices[1][max_corr_idx]
        joint_names = list(per_frame_joint_mse.keys())
        max_corr = float(corr_matrix.values[max_i, max_j])
        report_lines.append(f"  Highest correlation: {joint_names[max_i]} <-> {joint_names[max_j]}: {max_corr:.6f}")
    except Exception as e:
        report_lines.append(f"  Error: {e}")
    
    report_lines.append("\n📉 Skewness and Kurtosis:")
    try:
        stats = skewness_and_kurtosis(per_frame_mse)
        skew_val = stats['skewness']
        kurt_val = stats['kurtosis']
        
        report_lines.append(f"  Skewness: {skew_val:.6f}")
        if skew_val > 0:
            report_lines.append("    → Distribution skewed to the right (more small errors, a few large ones)")
        elif skew_val < 0:
            report_lines.append("    → Distribution skewed to the left (more large errors)")
        else:
            report_lines.append("    → Symmetrical distribution")
        
        report_lines.append(f"  Kurtosis: {kurt_val:.6f}")
        if kurt_val > 3:
            report_lines.append("    → High kurtosis (more extremes than a normal distribution)")
        elif kurt_val < 3:
            report_lines.append("    → Low kurtosis (fewer extremes, flatter distribution)")
        else:
            report_lines.append("    → Normal kurtosis (similar to a normal distribution)")
    except Exception as e:
        report_lines.append(f"  Error: {e}")
    
    report_lines.append("\n🎯 Joint statistics:")
    try:
        for joint_name, errors in per_frame_joint_mse.items():
            joint_stats = skewness_and_kurtosis(errors)
            mean_error = float(np.mean(errors))
            
            report_lines.append(f"  {joint_name}:")
            report_lines.append(f"    Mean MSE: {mean_error:.6f}")
            report_lines.append(f"    Skewness: {joint_stats['skewness']:.6f}, Kurtosis: {joint_stats['kurtosis']:.6f}")
    except Exception as e:
        report_lines.append(f"  Error: {e}")
    
    heatmap_path = os.path.join(output_dir, f"anomaly_heatmap_{timestamp}.png")
    heatmap_success = False
    try:
        anomaly_heatmap(per_frame_joint_mse, save_path=heatmap_path)
        report_lines.append(f"\nAnomaly heatmap saved to: {heatmap_path}")
        heatmap_success = True
    except Exception as e:
        report_lines.append(f"\nFailed to create heatmap: {e}")
    
    report_lines.append("\n" + "=" * 80)
    
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Metrics saved to: {txt_file}")
    if heatmap_success:
        print(f"Heatmap saved to: {heatmap_path}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/analyze_csv")
async def analyze_csv(
    csv_base64: str = Form(...),
    exercise_name: str = Form(...),
    video_path: str | None = Form(None),
):

    print("Starting autoencoder analysis...")
    print(f"Exercise: {exercise_name}, CSV length: {len(csv_base64)}, video_path: {video_path}")
    ae_start = time.perf_counter()
    video_file: Path | None = None
    if video_path:
        video_file = Path(video_path)
        if not video_file.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Referenced video not found: {video_file}"
            )
    try:
        (
            windows,
            window_starts,
            num_frames,
            original_frame_ids,
            original_values,
            joint_0,
        ) = prepare_data_for_model(csv_base64, seq_len=SEQ_LEN, step=5)
    except Exception as e:
        print(f"Error in prepare_data_for_model: {e}")
        raise

    joint_errors, joint_ratings, per_frame_joint_mse, per_frame_mse, reconstructed = calculate_joint_errors_and_ratings(
        windows, window_starts, num_frames, seq_len=SEQ_LEN
    )
    
    # compute_all_metrics(windows, reconstructed, per_frame_joint_mse, per_frame_mse)
    ae_elapsed = time.perf_counter() - ae_start
    print(f"Autoencoder analysis finished in {ae_elapsed:.2f}s.")
 
    target_rating = 75
    threshold = (100/target_rating - 1) / K_RATING

    print("Starting LLM response generation...")
    prompt = build_prompt(
        joint_errors,
        exercise_name,
        per_frame_mse=per_frame_mse.tolist() if isinstance(per_frame_mse, np.ndarray) else per_frame_mse, 
        per_frame_joint_mse=per_frame_joint_mse,
        frame_ids=original_frame_ids,
        mse_threshold=threshold,
    )
    feedback_text, llm_elapsed = ask_groq(prompt)
    print(f"LLM response finished in {llm_elapsed:.2f}s.")

    joint_ratings_serializable = {name: f"{int(round(float(rating)))}/100" for name, rating in joint_ratings.items()}
    
    avg_rating_value = int(round(sum(int(round(float(rating))) for rating in joint_ratings.values()) / len(joint_ratings)))
    avg_rating = f"{avg_rating_value}/100"

    response = {
        "feedback": feedback_text,
        "joint_ratings": joint_ratings_serializable,
        "avg_rating": avg_rating
    }

    if video_file is not None:
        frame_ids = original_frame_ids or list(range(num_frames))
        if len(frame_ids) != len(original_values):
            print("Skipping overlay rendering: pose count mismatch with video frames.")
            return response
        try:
            reference_sequence = reconstruct_reference_sequence(
                reconstructed,
                window_starts,
                num_frames,
                joint_0,
                seq_len=SEQ_LEN,
            )
            reference_pose_dict = build_reference_pose_dict(reference_sequence, frame_ids)
            detected_pose_dict = build_detected_pose_dict(original_values, frame_ids)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            overlay_output_path = SKEL_VIDEO_DIR / f"{video_file.stem}_{timestamp}_overlay.mp4"
            draw_skeleton_on_video(
                video_path=video_file,
                detected_poses=detected_pose_dict,
                reference_poses_by_frame=reference_pose_dict,
                output_path=overlay_output_path,
                primary_color=(0, 0, 255),
                reference_color=(0, 255, 0),
                render_mode="side_by_side", #overlay or side_by_side
            )
            response["overlay_video_path"] = str(overlay_output_path)
        except Exception as draw_error:
            print(f"Failed to draw overlay video: {draw_error}")

    return response


