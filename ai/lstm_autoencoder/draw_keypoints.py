from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

BODY_EDGES = [
    (0, 1), (1, 16), (16, 18), (1, 15), (15, 17),
    (0, 3), (3, 4), (4, 5), (0, 9), (9, 10), (10, 11),
    (0, 6), (6, 7), (7, 8), (0, 12), (12, 13), (13, 14)
]
HEAD_KEYPOINTS = {1, 15, 16, 17, 18}


NUM_KEYPOINTS = 19
VALUES_PER_KPT_3D = 4  
VALUES_PER_KPT_2D = 3  


def _normalize_pose_array(poses_3d: np.ndarray) -> np.ndarray:
    """Ensure poses are shaped as (N, 19, 4)."""
    poses = np.asarray(poses_3d, dtype=np.float32)
    if poses.ndim == 2 and poses.shape[1] == NUM_KEYPOINTS * VALUES_PER_KPT_3D:
        poses = poses.reshape((-1, NUM_KEYPOINTS, VALUES_PER_KPT_3D))
    elif poses.ndim == 3 and poses.shape[1:] == (NUM_KEYPOINTS, VALUES_PER_KPT_3D):
        pass
    else:
        raise ValueError(
            "Expected poses shaped as (N, 19, 4) or (N, 76); "
            f"got array with shape {poses.shape}."
        )
    return poses

#ai/openvino/modules/parse_poses.py lines 111-176
def project_poses_3d_to_2d(
    poses_3d: np.ndarray,
    fx: float,
    input_scale: float,
    stride: int,
    feature_map_size: tuple[int, int],
) -> np.ndarray:

    poses = _normalize_pose_array(poses_3d)
    feature_h, feature_w = feature_map_size
    principal_x = feature_w / 2.0
    principal_y = feature_h / 2.0
    focal = fx * input_scale / stride
    scale_back = stride / input_scale

    projected = np.ones((poses.shape[0], NUM_KEYPOINTS * VALUES_PER_KPT_2D + 1), dtype=np.float32) * -1

    for pose_id, pose in enumerate(poses):
        pose_conf = pose[:, 3]
        valid_mask = (pose_conf > 0) & (pose[:, 2] > 0)
        if not np.any(valid_mask):
            continue

        z = pose[valid_mask, 2]
        x = pose[valid_mask, 0]
        y = pose[valid_mask, 1]

        with np.errstate(divide="ignore", invalid="ignore"):
            x_over_z = x / z
            y_over_z = y / z
            u_feature = x_over_z * focal + principal_x
            v_feature = y_over_z * focal + principal_y

        keypoint_ids = np.flatnonzero(valid_mask)
        for kpt_index, u_feat, v_feat in zip(keypoint_ids, u_feature, v_feature):
            if not np.isfinite(u_feat) or not np.isfinite(v_feat):
                continue
            base_idx = kpt_index * VALUES_PER_KPT_2D
            u_scaled = u_feat * scale_back
            v_scaled = v_feat * scale_back
            projected[pose_id, base_idx] = u_scaled
            projected[pose_id, base_idx + 1] = v_scaled
            projected[pose_id, base_idx + 2] = pose_conf[kpt_index]

        projected[pose_id, -1] = float(np.mean(pose_conf[valid_mask]))

    return projected

#ai/openvino/human_pose_estimation_3d_demo.py lines 193-200
def _inverse_axis_transform(poses_3d: np.ndarray) -> np.ndarray:
   
    poses = poses_3d.copy()
    if poses.ndim == 3:

        x_csv = poses[:, :, 0].copy()
        y_csv = poses[:, :, 1].copy()
        z_csv = poses[:, :, 2].copy()
        poses[:, :, 0] = y_csv
        poses[:, :, 1] = -z_csv
        poses[:, :, 2] = -x_csv
    elif poses.ndim == 2:
        x_csv = poses[:, 0].copy()
        y_csv = poses[:, 1].copy()
        z_csv = poses[:, 2].copy()
        poses[:, 0] = y_csv
        poses[:, 1] = -z_csv
        poses[:, 2] = -x_csv
    return poses

#ai/openvino/human_pose_estimation_3d_demo.py lines 193-200
def _inverse_rotation(poses_3d: np.ndarray, R: np.ndarray, t: np.ndarray) -> np.ndarray:
    """
    Reverse the rotation applied in rotate_poses.
    
    In human_pose_estimation_3d_demo.py rotate_poses:
    R_inv = np.linalg.inv(R)
    pose_3d[0:3] = np.dot(R_inv, pose_3d[0:3] - t)
    
    So if we have pose_rotated = R_inv * (pose_original - t), then:
    pose_original = R * pose_rotated + t
    
    Inverse: pose_3d[0:3] = np.dot(R, pose_3d[0:3]) + t
    """
    poses = poses_3d.copy()
    if poses.ndim == 3:
        for pose_id in range(poses.shape[0]):
            pose_xyz = poses[pose_id, :, 0:3].T
            pose_xyz = np.dot(R, pose_xyz) + t
            poses[pose_id, :, 0:3] = pose_xyz.T
    elif poses.ndim == 2:
        pose_xyz = poses[:, 0:3].T
        pose_xyz = np.dot(R, pose_xyz) + t
        poses[:, 0:3] = pose_xyz.T
    return poses

#ai/openvino/human_pose_estimation_3d_demo.py lines 204-278
def load_poses_3d_from_csv(
    csv_path: str | Path,
    extrinsics_path: Optional[str | Path] = None,
    apply_inverse_transform: bool = True,
    skip_axis_transform: bool = False,
) -> dict[int, np.ndarray]:
    
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    R = None
    t = None
    if apply_inverse_transform:
        if extrinsics_path is None:
            default_extrinsics = Path(__file__).parent / "openvino" / "data" / "extrinsics.json"
            if default_extrinsics.exists():
                extrinsics_path = default_extrinsics
            else:
                raise ValueError(
                    "extrinsics_path required when apply_inverse_transform=True. "
                    "Provide path to extrinsics.json or set apply_inverse_transform=False"
                )
        else:
            extrinsics_path = Path(extrinsics_path)
            if not extrinsics_path.exists():
                raise FileNotFoundError(f"Extrinsics file not found: {extrinsics_path}")

        with open(extrinsics_path, 'r') as f:
            extrinsics = json.load(f)
        R = np.array(extrinsics['R'], dtype=np.float32)
        t = np.array(extrinsics['t'], dtype=np.float32).reshape(3, 1)

    poses_by_frame = {}
    with open(csv_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            frame_id = int(row['frame_id'])
            pose_3d = np.ones((NUM_KEYPOINTS, VALUES_PER_KPT_3D), dtype=np.float32) * -1

            for joint_id in range(NUM_KEYPOINTS):
                x_key = f'joint_{joint_id}_x'
                y_key = f'joint_{joint_id}_y'
                z_key = f'joint_{joint_id}_z'

                if x_key in row and y_key in row and z_key in row:
                    x = float(row[x_key]) if row[x_key] else -1.0
                    y = float(row[y_key]) if row[y_key] else -1.0
                    z = float(row[z_key]) if row[z_key] else -1.0

                    if x != -1.0 and y != -1.0 and z != -1.0:
                        pose_3d[joint_id, 0] = x
                        pose_3d[joint_id, 1] = y
                        pose_3d[joint_id, 2] = z
                        pose_3d[joint_id, 3] = 1.0
            if apply_inverse_transform and R is not None and t is not None:
                if frame_id == 0:
                    print(f"\n=== DEBUG Loading CSV ===", file=sys.stderr)
                    print(f"Frame {frame_id} - Before inverse transform:", file=sys.stderr)
                    valid_before = np.sum((pose_3d[:, 0] != -1) & (pose_3d[:, 1] != -1) & (pose_3d[:, 2] != -1))
                    print(f"  Valid points: {valid_before}/19", file=sys.stderr)
                    if valid_before > 0:
                        valid_idx = np.where((pose_3d[:, 0] != -1) & (pose_3d[:, 1] != -1) & (pose_3d[:, 2] != -1))[0][0]
                        print(f"  Sample point (joint {valid_idx}): x={pose_3d[valid_idx, 0]:.2f}, y={pose_3d[valid_idx, 1]:.2f}, z={pose_3d[valid_idx, 2]:.2f}", file=sys.stderr)
                
                pose_3d = _inverse_axis_transform(pose_3d)
                
                if frame_id == 0:
                    print(f"After inverse axis transform:", file=sys.stderr)
                    valid_after_axis = np.sum((pose_3d[:, 0] != -1) & (pose_3d[:, 1] != -1) & (pose_3d[:, 2] != -1))
                    print(f"  Valid points: {valid_after_axis}/19", file=sys.stderr)
                    if valid_after_axis > 0:
                        valid_idx = np.where((pose_3d[:, 0] != -1) & (pose_3d[:, 1] != -1) & (pose_3d[:, 2] != -1))[0][0]
                        print(f"  Sample point (joint {valid_idx}): x={pose_3d[valid_idx, 0]:.2f}, y={pose_3d[valid_idx, 1]:.2f}, z={pose_3d[valid_idx, 2]:.2f}", file=sys.stderr)
                
                pose_3d = _inverse_rotation(pose_3d, R, t)
                
                if frame_id == 0:
                    print(f"After inverse rotation:", file=sys.stderr)
                    valid_after_rot = np.sum((pose_3d[:, 0] != -1) & (pose_3d[:, 1] != -1) & (pose_3d[:, 2] != -1))
                    print(f"  Valid points: {valid_after_rot}/19", file=sys.stderr)
                    if valid_after_rot > 0:
                        valid_idx = np.where((pose_3d[:, 0] != -1) & (pose_3d[:, 1] != -1) & (pose_3d[:, 2] != -1))[0][0]
                        print(f"  Sample point (joint {valid_idx}): x={pose_3d[valid_idx, 0]:.2f}, y={pose_3d[valid_idx, 1]:.2f}, z={pose_3d[valid_idx, 2]:.2f}", file=sys.stderr)
                    print(f"Note: These 3D coords are in camera space after translation from parse_poses", file=sys.stderr)

            poses_by_frame[frame_id] = pose_3d

    print(f"\nLoaded {len(poses_by_frame)} frames from CSV", file=sys.stderr)
    return poses_by_frame

#ai/openvino/human_pose_estimation_3d_demo.py lines 182-278
def draw_skeleton_on_video(
    video_path: str | Path,
    csv_path: Optional[str | Path] = None,
    output_path: str | Path = Path("overlay.mp4"),
    fx: Optional[float] = None,
    input_scale: Optional[float] = None,
    stride: int = 8,
    base_height: int = 256,
    feature_map_size: Optional[tuple[int, int]] = None,
    extrinsics_path: Optional[str | Path] = None,
    primary_color: tuple[int, int, int] = (0, 0, 255),
    detected_poses: Optional[dict[int, np.ndarray]] = None,
    reference_poses_by_frame: Optional[dict[int, np.ndarray]] = None,
    reference_color: tuple[int, int, int] = (0, 255, 0),
    draw_actual_skeleton: bool = True,
    render_mode: str = "overlay",
) -> None:
    
    video_path = Path(video_path)
    output_path = Path(output_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    poses_3d_by_frame: dict[int, np.ndarray]
    if detected_poses is not None:
        poses_3d_by_frame = detected_poses
    else:
        if csv_path is None:
            raise ValueError("Either csv_path or detected_poses must be provided.")
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        poses_3d_by_frame = load_poses_3d_from_csv(
            csv_path, 
            extrinsics_path=extrinsics_path,
            apply_inverse_transform=True
        )
    if not poses_3d_by_frame:
        raise ValueError(f"No poses found in CSV file: {csv_path}")

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if fx is None:
        fx = np.float32(0.8 * width)
    if input_scale is None:
        input_scale = base_height / height
    if feature_map_size is None:
        scaled_h = height * input_scale
        scaled_w = width * input_scale
        feature_h = max(1, int(round(scaled_h / stride)))
        feature_w = max(1, int(round(scaled_w / stride)))
        feature_map_size = (feature_h, feature_w)

    render_mode = render_mode.lower()
    if render_mode not in ("overlay", "side_by_side"):
        raise ValueError("render_mode must be 'overlay' or 'side_by_side'")

    frame_multiplier = 2 if render_mode == "side_by_side" else 1
    # Use avc1 (H.264) for web compatibility
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width * frame_multiplier, height))
    if not out.isOpened():
        # Fallback to mp4v if avc1 fails
        print("Warning: avc1 codec failed, falling back to mp4v. Video may not play in browsers.")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width * frame_multiplier, height))
        
    if not out.isOpened():
        raise RuntimeError(f"Failed to create output video: {output_path}")

    frame_id = 0
    debug_printed = False
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        output_frame = frame.copy()
        left_frame = None
        right_frame = None

        has_detected = frame_id in poses_3d_by_frame
        has_reference = reference_poses_by_frame and frame_id in reference_poses_by_frame

        if has_detected:
            pose_3d = poses_3d_by_frame[frame_id]
            poses_3d_array = pose_3d.reshape(1, NUM_KEYPOINTS, VALUES_PER_KPT_3D)

            poses_2d = project_poses_3d_to_2d(
                poses_3d_array,
                fx=fx,
                input_scale=input_scale,
                stride=stride,
                feature_map_size=feature_map_size,
            )
            if not debug_printed:
                debug_printed = True

            if render_mode == "overlay":
                if draw_actual_skeleton:
                    _draw_pose(output_frame, poses_2d, primary_color)
            else:
                left_frame = frame.copy()
                if draw_actual_skeleton:
                    _draw_pose(left_frame, poses_2d, primary_color)

        if reference_poses_by_frame and has_reference:
            ref_pose = reference_poses_by_frame[frame_id]
            if ref_pose.shape[-1] == 3:
                confidence = np.ones((NUM_KEYPOINTS, 1), dtype=np.float32)
                ref_pose = np.concatenate([ref_pose, confidence], axis=1)
            ref_poses_2d = project_poses_3d_to_2d(
                ref_pose.reshape(1, NUM_KEYPOINTS, VALUES_PER_KPT_3D),
                fx=fx,
                input_scale=input_scale,
                stride=stride,
                feature_map_size=feature_map_size,
            )
            if render_mode == "overlay":
                _draw_pose(output_frame, ref_poses_2d, reference_color)
            else:
                right_frame = frame.copy()
                _draw_pose(right_frame, ref_poses_2d, reference_color)

        if render_mode == "side_by_side":
            if left_frame is None:
                left_frame = frame.copy()
            if right_frame is None:
                right_frame = frame.copy()
            combined = np.zeros((height, width * 2, 3), dtype=np.uint8)
            combined[:, :width] = left_frame
            combined[:, width:] = right_frame
            output_frame = combined

        out.write(output_frame)
        frame_id += 1

    cap.release()
    out.release()

    if output_path.exists():
        import subprocess
        import shutil
        
        temp_output = output_path.with_name(f"temp_{output_path.name}")
        try:
            cmd = [
                "ffmpeg", "-y",
                "-i", str(output_path),
                "-vcodec", "libx264",
                "-acodec", "aac",
                "-movflags", "+faststart",
                str(temp_output)
            ]
            
            print(f"Re-encoding video to H.264: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                shutil.move(str(temp_output), str(output_path))
                print("Video successfully re-encoded to H.264")
            else:
                print(f"FFmpeg re-encoding failed: {result.stderr}")
                if temp_output.exists():
                    temp_output.unlink()
        except Exception as e:
            print(f"Error during FFmpeg re-encoding: {e}")
            if temp_output.exists():
                temp_output.unlink()

#ai/openvino/modules/draw.py lines 104-115
def _draw_pose(frame: np.ndarray, poses_2d: np.ndarray, color: tuple[int, int, int]) -> None:
    pose = np.array(poses_2d[0][0:-1]).reshape((-1, 3)).transpose()
    visibility = pose[2] > 0
    connected = [False] * pose.shape[1]
    for start, end in BODY_EDGES:
        if start in HEAD_KEYPOINTS or end in HEAD_KEYPOINTS:
            continue
        if visibility[start] and visibility[end]:
            pt1 = tuple(pose[0:2, start].astype(np.int32))
            pt2 = tuple(pose[0:2, end].astype(np.int32))
            cv2.line(frame, pt1, pt2, color, 3, cv2.LINE_AA)
            connected[start] = True
            connected[end] = True
    for kpt_id in range(pose.shape[1]):
        if kpt_id in HEAD_KEYPOINTS:
            continue
        if pose[2, kpt_id] > 0 and connected[kpt_id]:
            center = tuple(pose[0:2, kpt_id].astype(np.int32))
            cv2.circle(frame, center, 3, color, -1, cv2.LINE_AA)

#ai/openvino/human_pose_estimation_3d_demo.py command section lines 52-124
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Draw 2D skeleton on video using 3D poses from CSV"
    )
    parser.add_argument("video", type=str, help="Path to input video file")
    parser.add_argument("csv", type=str, help="Path to CSV file with 3D poses")
    parser.add_argument("output", type=str, help="Path to save output video")
    parser.add_argument("--fx", type=float, default=None, help="Camera focal length (default: 0.8 * width)")
    parser.add_argument("--input-scale", type=float, default=None, help="Input scale factor (default: calculated)")
    parser.add_argument("--stride", type=int, default=8, help="Network stride (default: 8)")
    parser.add_argument("--base-height", type=int, default=256, help="Base height for inference (default: 256)")
    parser.add_argument("--feature-h", type=int, default=None, help="Feature map height (default: estimated)")
    parser.add_argument("--feature-w", type=int, default=None, help="Feature map width (default: estimated)")
    parser.add_argument("--extrinsics", type=str, default=None, help="Path to extrinsics.json (default: auto-detect)")

    args = parser.parse_args()

    feature_map_size = None
    if args.feature_h is not None and args.feature_w is not None:
        feature_map_size = (args.feature_h, args.feature_w)

    draw_skeleton_on_video(
        video_path=args.video,
        csv_path=args.csv,
        output_path=args.output,
        fx=args.fx,
        input_scale=args.input_scale,
        stride=args.stride,
        base_height=args.base_height,
        feature_map_size=feature_map_size,
        extrinsics_path=args.extrinsics,
    )


if __name__ == "__main__":
    main()

__all__ = ["project_poses_3d_to_2d", "load_poses_3d_from_csv", "draw_skeleton_on_video"]