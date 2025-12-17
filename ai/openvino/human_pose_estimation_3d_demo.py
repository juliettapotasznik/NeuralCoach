#!/usr/bin/env python3
"""
 Copyright (c) 2019-2024 Intel Corporation
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import collections
import json
import sys
import logging as log
from argparse import ArgumentParser, SUPPRESS
from pathlib import Path
from time import perf_counter
import csv
import os

import cv2
import numpy as np

from modules.inference_engine import InferenceEngine
from modules.draw import Plotter3d, draw_poses
from modules.parse_poses import parse_poses

sys.path.append(str(Path(__file__).resolve().parents[2] / 'common/python'))
sys.path.append(str(Path(__file__).resolve().parents[2] / 'common/python/model_zoo'))

import monitors
from images_capture import open_images_capture
from model_api.performance_metrics import PerformanceMetrics

log.basicConfig(format='[ %(levelname)s ] %(message)s', level=log.DEBUG, stream=sys.stderr)


def rotate_poses(poses_3d, R, t):
    R_inv = np.linalg.inv(R)
    for pose_id in range(poses_3d.shape[0]):
        pose_3d = poses_3d[pose_id].reshape((-1, 4)).transpose()
        pose_3d[0:3] = np.dot(R_inv, pose_3d[0:3] - t)
        poses_3d[pose_id] = pose_3d.transpose().reshape(-1)

    return poses_3d


if __name__ == '__main__':
    parser = ArgumentParser(description='Lightweight 3D human pose estimation demo. '
                                        'Press esc to exit, "p" to (un)pause video or process next image.',
                            add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS,
                      help='Show this help message and exit.')
    args.add_argument('-m', '--model',
                      help='Required. Path to an .xml file with a trained model.',
                      type=Path, required=True)
    args.add_argument('-i', '--input', required=True,
                      help='Required. An input to process. The input must be a single image, '
                           'a folder of images, video file or camera id.')
    args.add_argument('--loop', default=False, action='store_true',
                      help='Optional. Enable reading the input in a loop.')
    args.add_argument('-o', '--output', required=False,
                      help='Optional. Name of the output file(s) to save. Frames of odd width or height can be truncated. See https://github.com/opencv/opencv/pull/24086')
    args.add_argument('-limit', '--output_limit', required=False, default=1000, type=int,
                      help='Optional. Number of frames to store in output. '
                           'If 0 is set, all frames are stored.')
    args.add_argument('-d', '--device',
                      help='Optional. Specify the target device to infer on: CPU or GPU. '
                           'The demo will look for a suitable plugin for device specified '
                           '(by default, it is CPU).',
                      type=str, default='CPU')
    args.add_argument('--height_size', help='Optional. Network input layer height size.', type=int, default=256)
    args.add_argument('--extrinsics_path',
                      help='Optional. Path to file with camera extrinsics.',
                      type=Path, default=None)
    args.add_argument('--fx', type=np.float32, default=-1, help='Optional. Camera focal length.')
    args.add_argument('--no_show', help='Optional. Do not display output.', action='store_true')
    args.add_argument("-u", "--utilization_monitors", default='', type=str,
                      help="Optional. List of monitors to show initially.")
    args.add_argument('--csv_output', required=False,
                      help='Optional. Path to save the CSV file with pose landmarks.')
    args.add_argument('--output_3d', required=False, help='Optional. Name of the output file for 3D map video.')
    args.add_argument('--csv_stdout', required=False, action='store_true', help='Optional. Print CSV data to stdout.')
    args = parser.parse_args()


    results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
    results_dir = os.path.abspath(results_dir)
    os.makedirs(results_dir, exist_ok=True)

    cap = open_images_capture(args.input, args.loop)

    stride = 8
    if not getattr(args, "csv_stdout", False):
        print("Before model load")

    inference_engine = InferenceEngine(args.model, args.device, stride)

    if not getattr(args, "csv_stdout", False):
        print("After model load")

    canvas_3d = np.zeros((720, 1280, 3), dtype=np.uint8)
    plotter = Plotter3d(canvas_3d.shape[:2])
    canvas_3d_window_name = 'Canvas 3D'
    out_3d = None
    
    output_3d_path = None
    if args.output_3d:
        if os.path.isdir(args.output_3d):
            input_name = os.path.splitext(os.path.basename(args.input))[0]
            output_3d_path = os.path.join(results_dir, f'{input_name}_output_3d.mp4')
        else:
            base = os.path.basename(args.output_3d)
            if not base.endswith('.mp4'):
                base = os.path.splitext(base)[0] + '.mp4'
            output_3d_path = os.path.join(results_dir, base)
        fourcc_3d = cv2.VideoWriter_fourcc(*'mp4v')
        out_3d = cv2.VideoWriter(output_3d_path, fourcc_3d, 30, (canvas_3d.shape[1], canvas_3d.shape[0]))
        if not out_3d.isOpened():
            raise RuntimeError(f"Can't open 3D video writer for {output_3d_path}")
    if not args.no_show:
        cv2.namedWindow(canvas_3d_window_name)
        cv2.setMouseCallback(canvas_3d_window_name, Plotter3d.mouse_callback)

    file_path = args.extrinsics_path
    if file_path is None:
        file_path = Path(__file__).parent / 'data/extrinsics.json'
    with open(file_path, 'r') as f:
        extrinsics = json.load(f)
    R = np.array(extrinsics['R'], dtype=np.float32)
    t = np.array(extrinsics['t'], dtype=np.float32)

    is_video = cap.get_type() in ('VIDEO', 'CAMERA')

    base_height = args.height_size
    fx = args.fx

    frames_processed = 0
    delay = 1
    esc_code = 27
    p_code = 112
    space_code = 32
    mean_time = 0
    presenter = monitors.Presenter(args.utilization_monitors, 0)
    metrics = PerformanceMetrics()
    video_writer = cv2.VideoWriter()

    all_rows = []
    person_counter = collections.Counter()
    csv_path = None
    if args.csv_output:
        input_name = os.path.splitext(os.path.basename(args.input))[0]
        if os.path.isdir(args.csv_output):
            csv_path = os.path.join(args.csv_output, f'{input_name}.csv')
        else:
            csv_path = args.csv_output

    start_time = perf_counter()
    frame = cap.read()
    if frame is None:
        raise RuntimeError("Can't read an image from the input")

    if args.output:
        if os.path.isdir(args.output):
            input_name = os.path.splitext(os.path.basename(args.input))[0]
            video_path = os.path.join(results_dir, f'{input_name}_output.mp4')
        else:
            base = os.path.basename(args.output)
            if not base.endswith('.mp4'):
                base = os.path.splitext(base)[0] + '.mp4'
            video_path = os.path.join(results_dir, base)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        if not video_writer.open(video_path, fourcc, cap.fps(), (frame.shape[1], frame.shape[0])):
            raise RuntimeError("Can't open video writer")
        log.info(f'Saving video to: {video_path}')

    while frame is not None:
        current_time = cv2.getTickCount()
        input_scale = base_height / frame.shape[0]
        scaled_img = cv2.resize(frame, dsize=None, fx=input_scale, fy=input_scale)
        if fx < 0:  
            fx = np.float32(0.8 * frame.shape[1])

        inference_result = inference_engine.infer(scaled_img)
        poses_3d, poses_2d, pose_ids = parse_poses(inference_result, input_scale, stride, fx, is_video)
        edges = []
        if len(poses_3d) > 0:
            poses_3d = rotate_poses(poses_3d, R, t)
            poses_3d_copy = poses_3d.copy()
            x = poses_3d_copy[:, 0::4]
            y = poses_3d_copy[:, 1::4]
            z = poses_3d_copy[:, 2::4]
            poses_3d[:, 0::4], poses_3d[:, 1::4], poses_3d[:, 2::4] = -z, x, -y

            poses_3d = poses_3d.reshape(poses_3d.shape[0], 19, -1)[:, :, 0:3]
            edges = (Plotter3d.SKELETON_EDGES + 19 * np.arange(poses_3d.shape[0]).reshape((-1, 1, 1))).reshape((-1, 2))


            if (args.csv_output or args.csv_stdout) and poses_3d is not None and len(poses_3d) > 0:
                for person_idx, pose in enumerate(poses_3d):
                    person_id = int(pose_ids[person_idx]) if pose_ids is not None and len(pose_ids) > person_idx else person_idx
                    row = [frames_processed, person_id]
                    for joint in pose:
                        row.extend(joint)
                    all_rows.append(row)
                    person_counter[person_id] += 1
        plotter.plot(canvas_3d, poses_3d, edges)
        if out_3d is not None:
            out_3d.write(canvas_3d)

        presenter.drawGraphs(frame)
        draw_poses(frame, poses_2d)
        metrics.update(start_time, frame)

        frames_processed += 1
        if video_writer.isOpened() and (args.output_limit <= 0 or frames_processed <= args.output_limit):
            video_writer.write(frame)

        if not args.no_show:
            cv2.imshow(canvas_3d_window_name, canvas_3d)
            cv2.imshow('3D Human Pose Estimation', frame)

            key = cv2.waitKey(delay)
            if key == esc_code:
                break
            if key == p_code:
                if delay == 1:
                    delay = 0
                else:
                    delay = 1
            else:
                presenter.handleKey(key)
            if delay == 0 or not is_video:  
                key = 0
                while (key != p_code
                       and key != esc_code
                       and key != space_code):
                    plotter.plot(canvas_3d, poses_3d, edges)
                    cv2.imshow(canvas_3d_window_name, canvas_3d)
                    key = cv2.waitKey(33)
                if key == esc_code:
                    break
                else:
                    delay = 1
        start_time = perf_counter()
        frame = cap.read()

    metrics.log_total()
    for rep in presenter.reportMeans():
        log.info(rep)

    if (args.csv_output or args.csv_stdout) and all_rows:
        most_common_person_id = person_counter.most_common(1)[0][0]
        header = ['frame_id'] + [f'joint_{j}_{axis}' for j in range(19) for axis in ('x','y','z')]

        if args.csv_stdout:
            writer = csv.writer(sys.stdout)
            writer.writerow(header)
            for row in all_rows:
                if row[1] == most_common_person_id:
                    writer.writerow([row[0]] + row[2:])
            sys.stdout.flush()
            
        elif args.csv_output:
            with open(csv_path, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                header = ['frame_id']
                for joint in range(19):
                    header.extend([f'joint_{joint}_x', f'joint_{joint}_y', f'joint_{joint}_z'])
                csv_writer.writerow(header)
                for row in all_rows:
                    if row[1] == most_common_person_id:
                        csv_writer.writerow([row[0]] + row[2:])
            log.info(f'Saving pose data to: {csv_path} (only person_id={most_common_person_id})')
    sys.exit()
