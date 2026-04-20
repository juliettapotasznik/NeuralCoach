import sys
import pytest
from unittest.mock import MagicMock, patch, mock_open
import numpy as np
from pathlib import Path
import json

# Add module path
sys.path.append(str(Path(__file__).parent.parent))

# Mock tensorflow BEFORE any other imports or patches
mock_tf = MagicMock()
sys.modules['tensorflow'] = mock_tf
sys.modules['tensorflow.keras'] = MagicMock()
sys.modules['tensorflow.keras.models'] = MagicMock()

# Mock matplotlib and seaborn BEFORE importing metrics
sys.modules['matplotlib'] = MagicMock()
sys.modules['matplotlib.pyplot'] = MagicMock()
sys.modules['matplotlib.image'] = MagicMock()
sys.modules['matplotlib.backend_bases'] = MagicMock()
sys.modules['matplotlib.colors'] = MagicMock()
sys.modules['seaborn'] = MagicMock()

# Mock cv2
sys.modules['cv2'] = MagicMock()

# Configure model_from_json
mock_model = MagicMock()
sys.modules['tensorflow.keras.models'].model_from_json.return_value = mock_model

# JSON content that satisfies extrinsics.json
dummy_json = json.dumps({
    "R": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
    "t": [0.0, 0.0, 0.0]
})

# We also need to mock numpy.load because it's called at module level
# We can use patch for this one as numpy is likely installed
with patch('numpy.load') as mock_np_load, \
     patch('builtins.open', mock_open(read_data=dummy_json)) as mock_file:
    
    # Mock mean and std arrays
    mock_np_load.side_effect = [
        np.zeros((57,), dtype=np.float32), # mean
        np.ones((57,), dtype=np.float32)   # std
    ]
    
    # Now import the module
    import autoencoder_service

class TestAutoencoderService:
    def test_prepare_data_for_model(self):
        # Create a dummy CSV content
        # 30 frames, 57 columns (joint_0_x, joint_0_y, joint_0_z, ...)
        # We need enough frames for windowing (SEQ_LEN=30)
        
        # Create 60 frames of data
        frames = 60
        cols = []
        # Generate column names: joint_0_x, joint_0_y, joint_0_z, ...
        for i in range(19):
            cols.extend([f'joint_{i}_x', f'joint_{i}_y', f'joint_{i}_z'])
            
        import pandas as pd
        import base64
        
        df = pd.DataFrame(np.random.rand(frames, 57), columns=cols)
        csv_str = df.to_csv(index=False)
        csv_base64 = base64.b64encode(csv_str.encode('utf-8')).decode('utf-8')
        
        windows, window_starts, num_frames, original_frame_ids, values, joint_0 = \
            autoencoder_service.prepare_data_for_model(csv_base64)
            
        assert num_frames == frames
        # Step is 5, Seq len is 30.
        # Windows: 0..30, 5..35, ...
        # Last window start <= 60 - 30 = 30.
        # Starts: 0, 5, 10, 15, 20, 25, 30. (7 windows)
        assert len(windows) == 7
        assert windows.shape == (7, 30, 57)

    def test_build_prompt(self):
        joint_errors = {'left_shoulder': 2.5, 'right_knee': 0.1}
        exercise_name = "Squat"
        
        prompt = autoencoder_service.build_prompt(
            joint_errors=joint_errors,
            exercise_name=exercise_name,
            per_frame_mse=[0.1]*10,
            per_frame_joint_mse={'left_shoulder': [0.1]*10},
            frame_ids=[1,2,3],
            mse_threshold=2.0
        )
        
        assert "Squat" in prompt
        assert "left_shoulder" in prompt
        assert "right_knee" in prompt
        assert "Do NOT mention" in prompt

    def test_calculate_joint_errors(self):
        # Mock model prediction
        # Input shape: (batch, 30, 57)
        # Output shape: (batch, 30, 57)
        
        # Create dummy windows
        windows = np.zeros((2, 30, 57))
        window_starts = [0, 5]
        num_frames = 40
        
        # Mock reconstruction to be exactly the input (zero error)
        # We need to set the return value on the mocked model instance
        # autoencoder_service.model is the mock_model we configured earlier
        autoencoder_service.model.predict.return_value = windows
        
        joint_errors, joint_ratings, per_frame_joint_mse, per_frame_mse, reconstructed = \
            autoencoder_service.calculate_joint_errors_and_ratings(windows, window_starts, num_frames)
            
        # Errors should be 0
        assert joint_errors['left_shoulder'] == 0.0
        # Ratings should be 100
        assert joint_ratings['left_shoulder'] == 100.0
