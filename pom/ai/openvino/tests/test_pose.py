import sys
from unittest.mock import MagicMock

# Mock cv2 BEFORE importing modules.pose
sys.modules['cv2'] = MagicMock()

import pytest
import numpy as np
from modules.pose import Pose

class TestPose:
    def test_pose_initialization(self):
        # Create dummy keypoints: 18 keypoints, 2D (x, y)
        # The Pose class implementation suggests it expects (N, 2) because it assigns to a (N, 2) array
        keypoints = np.ones((18, 2), dtype=np.float32)
        confidence = 0.9
        
        pose = Pose(keypoints, confidence)
        
        assert pose.confidence == confidence
        assert np.array_equal(pose.keypoints, keypoints)
        assert pose.id is None
        assert len(pose.translation_filter) == 3

    def test_update_id(self):
        keypoints = np.ones((18, 2), dtype=np.float32)
        pose = Pose(keypoints, 0.8)
        
        # Test manual ID assignment
        pose.update_id(10)
        assert pose.id == 10
        
        # Test automatic ID assignment
        # Reset class variable for deterministic testing
        Pose.last_id = -1
        pose.update_id(None)
        assert pose.id == 0
        assert Pose.last_id == 0
        
        pose2 = Pose(keypoints, 0.8)
        pose2.update_id(None)
        assert pose2.id == 1
        assert Pose.last_id == 1

    def test_filter(self):
        keypoints = np.ones((18, 2), dtype=np.float32)
        pose = Pose(keypoints, 0.8)
        
        translation = [10.0, 20.0, 30.0]
        filtered = pose.filter(translation)
        
        # First filter call should return the value itself (initialized)
        assert len(filtered) == 3
        assert filtered == translation
        
        # Second call should be smoothed
        translation2 = [12.0, 22.0, 32.0]
        filtered2 = pose.filter(translation2)
        
        # Values should be between old and new (smoothing)
        assert 10.0 < filtered2[0] < 12.0
        assert 20.0 < filtered2[1] < 22.0
        assert 30.0 < filtered2[2] < 32.0
