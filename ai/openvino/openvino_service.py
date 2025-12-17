from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pathlib import Path
import shutil
import subprocess
import base64
import time
import uuid
from openvino.runtime import Core
import cv2  
import numpy as np
from ultralytics import YOLO


app = FastAPI()

ESTIMATION_MODEL_PATH = Path(__file__).parent / 'public/human-pose-estimation-3d-0001/FP16/human-pose-estimation-3d-0001.xml'

# Use the mounted volume path from docker-compose
TEMP_DIR = Path('/usr/src/app/users_videos').resolve()
TEMP_DIR.mkdir(exist_ok=True, parents=True)

core = Core()
try:
    yolo_model = YOLO("yolov8n.pt")
except Exception as yolo_error:
    print(f"Failed to initialize YOLO model: {yolo_error}")
    yolo_model = None

def video_contains_person(video_path: Path, confidence_threshold=0.45, frame_step=5, min_frames_with_detection=1):

    cap = cv2.VideoCapture(str(video_path))
    if yolo_model is None:
        cap.release()
        raise RuntimeError("YOLO model is unavailable.")

    frame_count = 0
    frames_with_person = 0
    total_frames_checked = 0

    if not cap.isOpened():
        cap.release()
        raise ValueError(f"Cannot open video file: {video_path}")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1

            if frame_count % frame_step != 0:
                continue

            total_frames_checked += 1

            try:
                results = yolo_model(frame[..., ::-1], verbose=False)
            except Exception as inference_error:
                raise RuntimeError(f"YOLO inference failed: {inference_error}") from inference_error

            if len(results) > 0 and len(results[0].boxes) > 0:
                boxes = results[0].boxes

                for box in boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])

                    if cls_id == 0 and conf >= confidence_threshold:
                        frames_with_person += 1
                        break
        
    finally:
        cap.release()

    if total_frames_checked == 0:
        raise ValueError("No frames were processed from the provided video.")

    detection_ratio = frames_with_person / total_frames_checked
    print(f"\nAnalysis complete: {frames_with_person}/{total_frames_checked} frames with a person "
          f"({detection_ratio*100:.1f}%)\n")

    return frames_with_person >= min_frames_with_detection

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/process_video")
async def process_video(file: UploadFile = File(...), exercise_name: str = Form(...)):
    temp_video_path = TEMP_DIR / file.filename

    try:
        TEMP_DIR.mkdir(exist_ok=True)

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file must include a filename."
            )

        with open(temp_video_path, "wb") as f:
            try:
                shutil.copyfileobj(file.file, f)
            except shutil.Error as copy_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error while saving the uploaded video: {copy_error}"
                )
            except OSError as os_error:
                raise HTTPException(
                    status_code=500,
                    detail=f"File system error while saving the video: {os_error}"
                )

        print("Starting YOLO person validation...")
        yolo_start = time.perf_counter()
        try:
            has_person = video_contains_person(temp_video_path, confidence_threshold=0.7, frame_step=5, min_frames_with_detection=2)
        except ValueError as value_error:
            yolo_elapsed = time.perf_counter() - yolo_start
            print(f"YOLO person validation failed in {yolo_elapsed:.2f}s: {value_error}")
            raise HTTPException(status_code=400, detail=str(value_error))
        except RuntimeError as runtime_error:
            yolo_elapsed = time.perf_counter() - yolo_start
            print(f"YOLO person validation failed in {yolo_elapsed:.2f}s: {runtime_error}")
            raise HTTPException(status_code=500, detail=str(runtime_error))
        except Exception as unexpected_yolo_error:
            yolo_elapsed = time.perf_counter() - yolo_start
            print(f"YOLO person validation failed in {yolo_elapsed:.2f}s: {unexpected_yolo_error}")
            raise HTTPException(status_code=500, detail="Unexpected error during YOLO validation.") from unexpected_yolo_error
        yolo_elapsed = time.perf_counter() - yolo_start
        if not has_person:
            print(f"YOLO person validation finished in {yolo_elapsed:.2f}s: no person detected.")
            raise HTTPException(
                status_code=422,
                detail="No person detected in the uploaded video. Make sure the person is clearly visible."
            )
        print(f"YOLO person validation finished in {yolo_elapsed:.2f}s: person detected.")

        output_filename = f"{uuid.uuid4()}.mp4"
        output_path = TEMP_DIR / output_filename

        print("Starting OpenVINO pose detection...")
        ov_start = time.perf_counter()
        cmd = [
            "python",
            "human_pose_estimation_3d_demo.py",
            "-m", str(ESTIMATION_MODEL_PATH),
            "-i", str(temp_video_path),
            "-o", str(output_path),
            "--csv_stdout",
            "--no_show"
        ]
        try:
            result = subprocess.run(
                cmd,
                check=True,
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=300
            )
        except FileNotFoundError as fnf_error:
            raise HTTPException(
                status_code=500,
                detail="Pose estimation script or Python executable not found."
            ) from fnf_error
        except subprocess.TimeoutExpired as timeout_error:
            raise HTTPException(
                status_code=504,
                detail="Pose estimation process timed out."
            ) from timeout_error
        csv_stdout = result.stdout
        ov_elapsed = time.perf_counter() - ov_start
        print(f"OpenVINO pose detection finished in {ov_elapsed:.2f}s.")

        if not csv_stdout or not csv_stdout.strip():
            raise HTTPException(
                status_code=422,
                detail="CSV data was not generated. The video may not include a detectable person."
            )

        csv_lines = csv_stdout.strip().split('\n')
        if len(csv_lines) <= 1:
            raise HTTPException(
                status_code=422,
                detail="No pose data detected in the video. The video may not include a detectable person."
            )

        video_base64 = None
        if output_path.exists():
            try:
                with open(output_path, "rb") as f:
                    video_bytes = f.read()
                    video_base64 = base64.b64encode(video_bytes).decode("utf-8")
                output_path.unlink()
            except Exception as e:
                print(f"Error reading processed video: {e}")

        return {
            "exercise_name": exercise_name,
            "csv_base64": base64.b64encode(csv_stdout.encode('utf-8')).decode("utf-8"),
            "video_base64": video_base64,
            "video_path": str(temp_video_path)
        }

    except HTTPException:
        raise

    except subprocess.CalledProcessError as e:
        if 'ov_start' in locals():
            elapsed = time.perf_counter() - ov_start
            print(f"OpenVINO pose detection failed in {elapsed:.2f}s: {e}")
        error_msg = (e.stderr or e.stdout or 'Unknown error').strip()
        print(f"OpenVINO stderr: {e.stderr}")
        print(f"OpenVINO stdout: {e.stdout}")
        print(f"OpenVINO returncode: {e.returncode}")
        raise HTTPException(
            status_code=500,
            detail=f"Pose estimation process failed: {error_msg[:200]}"
        ) from e

    except (RuntimeError, ValueError) as proc_error:
        print(f"Video processing error: {proc_error}")
        raise HTTPException(status_code=500, detail=str(proc_error)) from proc_error

    except Exception as e:
        print(f"Unexpected error during video processing: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unexpected error during video processing."
        ) from e

    finally:
        pass



