import argparse
import threading

import pyrealsense2 as rs
from piper_sdk import *
from torch.distributed.pipeline.sync import pipe

from robot_utils import *
from data_utils import *
from constants import *

class EpisodeReplayer:
    def __init__(self, args):
        self.args = args
        self.episode_name = self.args['episode_name']
        self.control_mode = self.args['control_mode']
        self.alt_control_mode = self.args['alt_control_mode'] if 'alt_control_mode' in self.args else None

        self.fk_calc = FK_CALC
        self.is_experiment = False

        self.piper = C_PiperInterface("can0")
        self.piper.ConnectPort()
        self.piper.EnableArm(7)

        self.wrist_rs_config = rs.config()
        self.exo_rs_config = rs.config()

        self.wrist_cam_sn = WRIST_CAM_SN
        self.exo_cam_sn = EXO_CAM_SN

        self.wrist_rs_config.enable_device(self.wrist_cam_sn)
        self.exo_rs_config.enable_device(self.exo_cam_sn)

        self.wrist_rs_config.enable_stream(rs.stream.color)
        self.wrist_rs_config.enable_stream(rs.stream.depth)

        self.exo_rs_config.enable_stream(rs.stream.color)
        self.exo_rs_config.enable_stream(rs.stream.depth)

        self.wrist_rs_pipeline = rs.pipeline()
        self.exo_rs_pipeline = rs.pipeline()

        self.wrist_rs_pipeline.start(self.wrist_rs_config)
        self.exo_rs_pipeline.start(self.exo_rs_config)

        self.valid_ctrl_modes = ['JointCtrl','EndPoseCtrl','ForwardKinematicsCtrl', 'CurveCtrl']

        self.record_end_pose = []
        self.record_act_time = []
        self.fps = REPLAY_FPS
        self.index = 0

        self.dataset_dir = REPLAY_DATASET_DIR
        self.create_dir()

        self.episode_data = load_episode(self.episode_name)
        self.joint_data = self.episode_data['robot']['joint_data']
        self.gripper_data = np.abs(self.episode_data['robot']['gripper_data'])
        # self.gripper_data = self.episode_data['robot']['gripper_data']
        self.end_pose_data = self.episode_data['robot']['end_pose_data']
        # self.joint_data, self.gripper_data, self.end_pose_data = load_h5_data(file_name=f'dataset/episode_{self.episode_name}.h5')
        # self.joint_data, self.gripper_data, self.end_pose_data = load_h5_data(file_name=f'data_re.h5')

        self.rev_end_pose_data = self.end_pose_data[::-1]
        self.rev_gripper_data = self.gripper_data[::-1]

        self.prev_end_pose = self.end_pose_data[0].copy()
        self.prev_gripper = self.gripper_data[0].copy()

        self.end_pose = self.end_pose_data[0].copy()
        self.gripper = self.gripper_data[0].copy()
        self.curve_points = self.end_pose_data[0:3].copy()

        self.rev_end_pose = self.end_pose_data[-1].copy()
        self.rev_gripper = self.gripper_data[-1].copy()

        self.detoured_end_pose = self.end_pose_data[0].copy()
        self.movement_detection = None

        self.robot_dataset, self.record_robot_time = [],[]
        self.robot_data, self.robot_time_data = None, None

        self.image_dataset = None
        self.wrist_image_data, self.exo_image_data = None, None
        self.wrist_frames, self.exo_frames = None, None
        self.wrist_depth_image, self.wrist_color_image = None, None
        self.exo_depth_image, self.exo_color_image = None, None
        self.wrist_image_dataset, self.exo_image_dataset, self.record_image_time = [],[], []

        self.is_replay_finished = False
        self.lock = threading.Lock()

        self.wrist_image_thread = threading.Thread(target=self.fetch_image_data, args=(self.wrist_rs_pipeline,True))
        self.exo_image_thread = threading.Thread(target=self.fetch_image_data, args=(self.exo_rs_pipeline,False))


    def replay(self):
        setZeroConfiguration(self.piper)

        self.wrist_image_thread.start()
        self.exo_image_thread.start()

        t0 = time.time()
        if self.control_mode in self.valid_ctrl_modes:
            if self.control_mode == 'JointCtrl':
                self.replay_joint()
            elif self.control_mode == 'EndPoseCtrl':
                self.replay_end_pose()
            elif self.control_mode == 'ForwardKinematicsCtrl':
                self.replay_fk()
            elif  self.control_mode == 'CurveCtrl':
                self.replay_curve()
        else:
            print(f"Invalid control mode\n Try {self.valid_ctrl_modes}")
            exit()

        self.is_replay_finished = True
        t1 = time.time()

        print(f"average time on image record : {np.mean(self.record_image_time)}")
        print(f"average time on robot record : {np.mean(self.record_robot_time)}")
        print(f"average time on robot actuation : {np.mean(self.record_act_time)}")
        print(f"average Hz : {len(self.end_pose_data)/(t1 - t0)}")

        setZeroConfiguration(self.piper)

        self.image_dataset={
            'wrist_image_dataset': self.wrist_image_dataset,
            'exo_image_dataset': self.exo_image_dataset,
        }

        if not self.is_experiment:
            save_episode(self.episode_name, self.robot_dataset, image_dataset=self.image_dataset,is_record=False)
        else:
            pass

    def reverse_replay(self):
        self.replay_end_pose(reversed=True)

    def record_robot_data(self):
        self.robot_data = {
            "joint_data": readJointMsg(self.piper),
            "gripper_data": readGripperMsg(self.piper),
            "end_pose_data": readEndPoseMsg(self.piper),
        }

    def record_data(self):
        t0=time.time()
        self.record_robot_data()
        t1=time.time()
        self.record_image_data()
        t2=time.time()

        t_robot = t1-t0
        t_image = t2-t1

        self.robot_time_data = {
            "index": self.index,
            "timestamp": t_robot,
            "robot": self.robot_data,
        }

        self.robot_dataset.append(self.robot_time_data)

        while self.wrist_image_data is None or self.exo_image_data is None:
            pass
        self.wrist_image_dataset.append(self.wrist_image_data)
        self.exo_image_dataset.append(self.exo_image_data)

        self.record_robot_time.append(t_robot)
        self.record_image_time.append(t_image)

    def replay_joint(self):
        for i in range(len(self.joint_data)):
            self.index = i
            t_before_act = time.time()

            joint = self.joint_data[self.index]
            gripper = self.gripper_data[self.index]

            ctrlJoint(self.piper, joint, gripper)

            self.record_data()

            t_after_act = time.time()
            t_act = t_after_act - t_before_act
            time.sleep(max(0, 1 / self.fps - t_act))

            self.record_act_time.append(t_act)

    def replay_end_pose(self, reversed=False):
        for i in range(len(self.end_pose_data)):
            self.index = i
            t_before_act = time.time()

            if not reversed:
                self.end_pose = self.end_pose_data[self.index]
                self.gripper = self.gripper_data[self.index]

                ctrlEndPose(self.piper, self.end_pose, self.gripper)
            else:
                self.rev_end_pose = self.rev_end_pose_data[self.index]
                self.rev_gripper = self.rev_gripper_data[self.index]

                ctrlEndPose(self.piper, self.rev_end_pose, self.rev_gripper)

            if self.alt_control_mode:
                if not isMoved(self.piper, prev_data={
                    'end_pose': self.prev_end_pose,
                    'gripper': self.prev_gripper
                }):
                    self.replay_alt_ctrl()

                self.prev_end_pose = readEndPoseMsg(self.piper)
                self.prev_gripper = readGripperMsg(self.piper)

            self.record_data()

            t_after_act = time.time()
            t_act = t_after_act - t_before_act
            time.sleep(max(0, 1 / self.fps - t_act))

            self.record_act_time.append(t_act)

    def replay_alt_ctrl(self):
        if self.alt_control_mode == 'DetourEndPoseCtrl':
            joint = deg2rad(0.001 * self.joint_data[self.index])
            self.detoured_end_pose = self.get_detoured_end_pose(joint)

            ctrlEndPose(self.piper, self.detoured_end_pose, self.gripper)

        elif self.alt_control_mode == 'JointCtrl':
            ctrlJoint(self.piper, self.joint_data[self.index], self.gripper)

    def get_detoured_end_pose(self, joint):
        return 1000 * np.array(self.fk_calc.CalFK(joint)[-1]).astype(int)

    def replay_fk(self):
        end_pose_fk = []
        for i in range(len(self.joint_data)):
            joint = deg2rad(0.001 * self.joint_data[i])
            fk = self.get_detoured_end_pose(joint)
            end_pose_fk.append(fk)

        for i in range(len(end_pose_fk)):
            self.index = i
            t_before_act = time.time()

            self.end_pose = end_pose_fk[self.index]
            self.gripper = self.gripper_data[self.index]

            ctrlEndPose(self.piper, self.end_pose, self.gripper)

            self.record_data()

            t_after_act = time.time()
            t_act = t_after_act - t_before_act
            time.sleep(max(0, 1 / self.fps - t_act))

            self.record_act_time.append(t_act)

    def replay_curve(self):
        for i in range(len(self.end_pose_data)-2):
            if i%2:
                continue

            self.index = i
            t_before_act = time.time()

            self.curve_points = self.end_pose_data[self.index:self.index+3]
            self.gripper = self.gripper_data[self.index]

            ctrlCurve(self.piper, self.curve_points, self.gripper)

            self.record_data()

            t_after_act = time.time()
            t_act = t_after_act - t_before_act
            time.sleep(max(0, 1 / self.fps - t_act))

            self.record_act_time.append(t_act)

    def record_image_data(self):
        # self.wrist_image_thread = threading.Thread(target=self.fetch_image_data(self.wrist_rs_pipeline,True))
        # self.exo_image_thread = threading.Thread(target=self.fetch_image_data(self.exo_rs_pipeline,False))
        #
        # self.wrist_image_thread.start()
        # self.exo_image_thread.start()
        #
        # self.wrist_image_thread.join()
        # self.exo_image_thread.join()
        # print('image fetched')
        pass

    def fetch_image_data(self, pipeline, is_wrist):
        while True:
            t0 = time.time()
            frames = pipeline.wait_for_frames()
            depth_image = np.array(frames.get_depth_frame().get_data()).astype(np.uint8)
            color_image = np.array(frames.get_color_frame().get_data()).astype(np.uint8)

            image_data = [color_image, depth_image]

            self.lock.acquire()
            if is_wrist:
                self.wrist_image_data = image_data
            else:
                self.exo_image_data = image_data
            self.lock.release()

            t1 = time.time()
            time.sleep(max(0,1/REPLAY_FPS-(t1-t0)))

            if self.is_replay_finished:
                break

    def create_dir(self):
        if not os.path.isdir(self.dataset_dir):
            os.makedirs(self.dataset_dir)
        try:
            if not os.path.exists(f"{self.dataset_dir}/{self.episode_name}"):
                os.makedirs(f"{self.dataset_dir}/{self.episode_name}")
        except OSError:
            print(f"Error: Creating directory. {self.episode_name}")
            exit()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--episode_name', type=str, required=True)
    # parser.add_argument('--control_mode', type=str, required=True)
    # parser.add_argument('--alt_control_mode', type=str, required=False)
    # args = vars(parser.parse_args())
    #
    # episode_replayer = EpisodeReplayer(args)

    episode_replayer = EpisodeReplayer({
        'episode_name': 'wrist_cam_test',
        'control_mode': 'EndPoseCtrl',
    })

    episode_replayer.replay()