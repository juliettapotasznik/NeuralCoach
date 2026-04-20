# 3D Human Pose Estimation Demo
##Excersises dataset
https://drive.google.com/drive/folders/1gGygtjigrayj337UzF_3EdKW8zFlCD1E?usp=sharing

## Setup Steps


1. **Create and activate virtual environment**:
   ```bash
   python3.10 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install required packages**:
   PROSZE SIE UPEWNIC CZY MACIE DOBRA WERSJE TENSORFLOW ODKOMENTOWANA W REQUIREMENTS
   ```bash
   pip install -r requirements.txt
   ```

3. **Build the pose extractor module**:
   ```bash
   cd openvino/pose_extractor
   rm -rf build
   mkdir build
   cd build
   cmake ..
   make
   cp pose_extractor.so ..
   cd ..
   ```

4. **Download and prepare the model**:
   ```bash
   cd ..
   omz_downloader --name human-pose-estimation-3d-0001
   omz_converter --name human-pose-estimation-3d-0001
   ```

5. **Run the demo**:
   ```bash
   cd ..
   python human_pose_estimation_3d_demo.py -m public/human-pose-estimation-3d-0001/FP16/human-pose-estimation-3d-0001.xml -i "../dataset/excersises/barbell_biceps_curl/barbell biceps curl_1.mp4" --csv_output ../results --no_show
   ```
python human_pose_estimation_3d_demo.py -m public/human-pose-estimation-3d-0001/FP16/human-pose-estimation-3d-0001.xml -i "/Users/zosia/Documents/GitHub/RepRight/test/pies.mp4" --csv_output ../results


   stdout: python human_pose_estimation_3d_demo.py \
  -m public/human-pose-estimation-3d-0001/FP16/human-pose-estimation-3d-0001.xml \
  -i "/Users/zosia/Documents/GitHub/RepRight/users_videos/biceps_curl.mp4" \
  --csv_stdout --no_show > /Users/zosia/Documents/GitHub/RepRight/results/out.csv
  
   optional -o ../results/output.mp4 --output_3d ../results/output_3d.mp4

6. **Process all videos in dataset**:
   To process all videos in the dataset folder and save their corresponding CSV files:
   ```bash
   cd openvino
   python process_all_videos.py
   ```
   This will:
   - Process all video files in the dataset_videos/full_dataset directory
   - Save CSV files in the results directory

   - Handle errors gracefully



TESTING SERVICES:

### OpenVINO service (video → CSV)

Run the service:
```bash
cd openvino
uvicorn openvino_service:app --host 0.0.0.0 --port 8001
```

Open docs: `http://localhost:8001/docs`

Test endpoint:
```bash
response=$(curl -sS -X POST "http://localhost:8001/process_video" \
  -F "file=@/Users/zosia/Documents/GitHub/RepRight/test/biceps_curl.mp4" \
  -F "exercise_name=biceps")

echo "$response" | python3 -c 'import sys, json; data=json.load(sys.stdin); print(data.get("csv_base64", "ERROR: " + data.get("detail", data.get("error", "Unknown error"))))' > b64.txt

if grep -q "^ERROR:" b64.txt; then
  cat b64.txt
  echo "Failed - see error above"
else
  echo "Success - CSV base64 saved to b64.txt"
fi
```

Expected: 
- Success: CSV base64 encoded string saved to `b64.txt`
- Error: Error message in `b64.txt` (starts with "ERROR:")

### LSTM autoencoder service (CSV → feedback)
Run the service:
```bash
cd lstm_autoencoder
uvicorn autoencoder_service:app --host 0.0.0.0 --port 8000 --env-file ../../.env
```

Open docs: `http://localhost:8000/docs`

Test endpoint (use a CSV produced by the OpenVINO service):
```bash
curl -sS -X POST "http://localhost:8000/analyze_csv" \
  -F "exercise_name=biceps_curl" \
  --form-string "csv_base64=$(cat b64.txt)" \
  -F "video_path=/Users/zosia/Documents/GitHub/neural-coach/ai/users_videos/biceps_curl.mp4" \
  | jq '.'
```
Expected: JSON with `feedback` and `joint_ratings` (0-100 scale per joint).

To see only joint ratings:
```bash
curl -sS -X POST "http://localhost:8000/analyze_csv" \
  -F "exercise_name=biceps" \
  --form-string "csv_base64=$(cat b64.txt)" \
  | jq '.joint_ratings'
```

lsof -i :port
kill -9 pid

cd /Users/zosia/Documents/GitHub/RepRight/lstm_autoencoder
docker build -t repright-autoencoder:py310 .
docker run --rm -p 8000:8000 --env-file .env repright-autoencoder:py310

http://localhost:8000/docs

cd /Users/zosia/Documents/GitHub/RepRight/openvino
docker build -t repright-openvino:py310 .
docker run --rm -p 8001:8001 --env-file .env repright-openvino:py310

http://localhost:8001/health

