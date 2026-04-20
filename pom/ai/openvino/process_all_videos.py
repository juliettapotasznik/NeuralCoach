import os
import subprocess
from pathlib import Path

def process_all_videos():
    dataset_dir = (Path(__file__).parent.parent / 'dataset_videos' / 'full_dataset').resolve()
    results_dir = (Path(__file__).parent.parent / 'dataset_csv').resolve()
    
    results_dir.mkdir(exist_ok=True)
    
    model_path = Path(__file__).parent / 'public/human-pose-estimation-3d-0001/FP16/human-pose-estimation-3d-0001.xml'
    
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    
    total_files = 0
    for root, dirs, files in os.walk(dataset_dir):
        for file in files:
            if file.lower().endswith(video_extensions):
                total_files += 1
                print(f"Found video file: {file}")
    
    print(f"\nTotal video files found: {total_files}")
    processed_files = 0
    skipped_files = 0
    
    for root, dirs, files in os.walk(dataset_dir):
        for file in files:
            if file.lower().endswith(video_extensions):
                video_path = os.path.join(root, file)
                csv_path = results_dir / f"{Path(file).stem}.csv"
                
                if csv_path.exists():
                    print(f"\nSkipping already processed video: {file}")
                    skipped_files += 1
                    continue
                
                print(f"\nProcessing video: {video_path}")
                
                cmd = [
                    'python',
                    'human_pose_estimation_3d_demo.py',
                    '-m', str(model_path),
                    '-i', video_path,
                    '--csv_output', str(results_dir),
                    '--no_show'
                ]
                
                try:
                    subprocess.run(cmd, check=True)
                    processed_files += 1
                    print(f"Successfully processed: {file} ({processed_files}/{total_files})")
                except subprocess.CalledProcessError as e:
                    print(f"Error processing {file}: {e}")
                except Exception as e:
                    print(f"Unexpected error processing {file}: {e}")
    
    print(f"\nProcessing complete!")
    print(f"Total videos found: {total_files}")
    print(f"Videos processed: {processed_files}")
    print(f"Videos skipped (already processed): {skipped_files}")
    print(f"Remaining videos: {total_files - processed_files - skipped_files}")

if __name__ == '__main__':
    process_all_videos() 