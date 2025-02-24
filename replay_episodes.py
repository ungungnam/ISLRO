import argparse
import pyrealsense2 as rs
from piper_sdk import *

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

        self.piper = C_PiperInterface("can0")
        self.piper.ConnectPort()
        self.piper.EnableArm(7)

        self.rs_config = rs.config()
        self.rs_config.enable_stream(rs.stream.color)
        self.rs_config.enable_stream(rs.stream.depth)

        self.pipeline = rs.pipeline()
        self.pipeline.start(self.rs_config)

        self.valid_ctrl_modes = ['JointCtrl','EndPoseCtrl','ForwardKinematicsCtrl', 'CurveCtrl']

        self.record_end_pose = []
        self.record_act_time = []
        self.fps = REPLAY_FPS
        self.index = 0

        self.episode_data = load_episode(self.episode_name)
        self.joint_data = self.episode_data['robot']['joint_data']
        self.gripper_data = self.episode_data['robot']['gripper_data']
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

        self.frames = None
        self.depth_image, self.color_image = None, None
        self.image_dataset, self.record_image_time = [],[]

    def replay(self):
        setZeroConfiguration(self.piper)

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

        print(f"average time on robot actuation : {np.mean(self.record_act_time)}")
        setZeroConfiguration(self.piper)
        save_episode_image(self.image_dataset, self.episode_name)

    def reverse_replay(self):
        self.replay_end_pose(reversed=True)

    def replay_joint(self):
        for i in range(len(self.joint_data)):
            self.index = i
            t_before_act = time.time()

            joint = self.joint_data[self.index]
            gripper = self.gripper_data[self.index]

            ctrlJoint(self.piper, joint, gripper)

            self.record_end_pose.append(readEndPoseMsg(self.piper))
            self.record_image_data()

            time.sleep(max(0, 1 / self.fps - time.time() - t_before_act))
            t_after_act = time.time()

            self.record_act_time.append(t_after_act - t_before_act)

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

            self.record_end_pose.append(readEndPoseMsg(self.piper))
            self.record_image_data()

            time.sleep(max(0, 1 / self.fps - time.time() - t_before_act))
            t_after_act = time.time()

            self.record_act_time.append(t_after_act - t_before_act)

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

            self.record_end_pose.append(readEndPoseMsg(self.piper))
            self.record_image_data()

            time.sleep(max(0, 1 / self.fps - time.time() - t_before_act))
            t_after_act = time.time()

            self.record_act_time.append(t_after_act - t_before_act)

    def replay_curve(self):
        for i in range(len(self.end_pose_data)-2):
            if i%2:
                continue

            self.index = i
            t_before_act = time.time()

            self.curve_points = self.end_pose_data[self.index:self.index+3]
            self.gripper = self.gripper_data[self.index]

            ctrlCurve(self.piper, self.curve_points, self.gripper)

            self.record_end_pose.append(readEndPoseMsg(self.piper))
            self.record_image_data()

            time.sleep(max(0, 1 / self.fps - time.time() - t_before_act))
            t_after_act = time.time()

            self.record_act_time.append(t_after_act - t_before_act)

    def record_image_data(self):
        self.frames = self.pipeline.wait_for_frames()
        self.depth_image = np.array(self.frames.get_depth_frame().get_data()).astype(np.uint8)
        self.color_image = np.array(self.frames.get_color_frame().get_data()).astype(np.uint8)

        self.color_image = cv2.resize(self.color_image, (self.depth_image.shape[1], self.depth_image.shape[0]))
        self.image_data = [self.color_image, self.depth_image]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode_name', type=str, required=True)
    parser.add_argument('--control_mode', type=str, required=True)
    parser.add_argument('--alt_control_mode', type=str, required=False)
    args = vars(parser.parse_args())

    episode_replayer = EpisodeReplayer(args)

    # episode_replayer = EpisodeReplayer({
    #     'episode_name': 'curve_ctrl_test',
    #     'control_mode': 'CurveCtrl',
    # })

    episode_replayer.replay()