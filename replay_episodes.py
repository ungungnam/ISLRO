import argparse

from piper_sdk import *

from robot_utils import *
from constants import *

fk_calc = FK_CALC

class EpisodeReplayer:
    def __init__(self, args):
        self.args = args
        self.episode_name = self.args['episode_name']
        self.control_mode = self.args['control_mode']

        self.piper = C_PiperInterface("can0")
        self.piper.ConnectPort()
        self.piper.EnableArm(7)
        setZeroConfiguration(self.piper)

        self.record_act_time = []
        self.fps = FPS

        self.joint_data, self.gripper_data, self.end_pose_data = load_h5_data(file_name=f'dataset/episode_{self.episode_name}.h5')
        self.prev_end_pose = self.end_pose_data[0]
        self.prev_gripper = self.gripper_data[0]

        self.detoured_end_pose = np.zeros(6)

    def replay(self):

        if self.control_mode == 'JointCtrl':
            self.replay_joint()
        elif self.control_mode == 'EndPoseCtrl':
            self.replay_end_pose()
        else:
            print("Invalid control mode\n Try either 'JointCtrl' or 'EndPoseCtrl'")
            exit()
        setZeroConfiguration(self.piper)

    def replay_joint(self):
        for i in range(len(self.joint_data)):
            t_before_act = time.time()

            joint = self.joint_data[i]
            gripper = self.gripper_data[i]

            ctrlJoint(self.piper, joint, gripper)

            time.sleep(1 / self.fps)
            t_after_act = time.time()
            self.record_act_time.append(t_after_act - t_before_act)

        print(f"average time on robot actuation : {np.mean(self.record_act_time)}")

    def replay_end_pose(self):
        for i in range(len(self.end_pose_data)):
            t_before_act = time.time()

            end_pose = self.end_pose_data[i]
            gripper = self.gripper_data[i]

            ctrlEndPose(self.piper, end_pose, gripper)

            if not isMoved(self.piper, prev_data={
                'end_pose': self.prev_end_pose,
                'gripper': self.prev_gripper
            }):
                joint = deg2rad(0.001 * self.joint_data[i])
                self.detoured_end_pose = np.array(fk_calc.CalFK(joint)[-1])
                self.detoured_end_pose = (1000 * self.detoured_end_pose).astype(int)
                ctrlEndPose(self.piper, self.detoured_end_pose, gripper)

                # ctrlJoint(piper, joint_data[i], gripper)

            time.sleep(1 / self.fps)

            self.prev_end_pose = readEndPoseMsg(self.piper)
            self.prev_gripper = readGripperMsg(self.piper)

            t_after_act = time.time()
            self.record_act_time.append(t_after_act - t_before_act)

        print(f"average time on robot actuation : {np.mean(self.record_act_time)}")


def main(args):
    episode_name = args['episode_name']
    control_mode = args['control_mode']

    piper = C_PiperInterface("can0")
    piper.ConnectPort()
    piper.EnableArm(7)
    setZeroConfiguration(piper)

    # recording actuation time
    record_act_time = []
    fps = FPS

    # Load the h5 file using episode_name
    joint_data, gripper_data, end_pose_data = load_h5_data(file_name=f'dataset/episode_{episode_name}.h5')
    prev_end_pose = end_pose_data[0]
    prev_gripper = gripper_data[0]

    if control_mode == 'JointCtrl':
        for i in range(len(joint_data)):
            t_before_act = time.time()

            joint = joint_data[i]
            gripper = gripper_data[i]

            ctrlJoint(piper, joint, gripper)

            time.sleep(1/fps)
            t_after_act = time.time()
            record_act_time.append(t_after_act - t_before_act)

        print(f"average time on robot actuation : {np.mean(record_act_time)}")

    elif control_mode == 'EndPoseCtrl':
        for i in range(len(end_pose_data)):
            t_before_act = time.time()

            end_pose = end_pose_data[i]
            gripper = gripper_data[i]

            ctrlEndPose(piper, end_pose, gripper)

            if not isMoved(piper, prev_data={
                'end_pose': prev_end_pose,
                'gripper': prev_gripper
            }):
                joint = deg2rad(0.001 * joint_data[i])
                detoured_end_pose = np.array(fk_calc.CalFK(joint)[-1])
                detoured_end_pose = (1000 * detoured_end_pose).astype(int)
                ctrlEndPose(piper, detoured_end_pose, gripper)

                # ctrlJoint(piper, joint_data[i], gripper)

            time.sleep(1 / fps)

            prev_end_pose = readEndPoseMsg(piper)
            prev_gripper = readGripperMsg(piper)

            t_after_act = time.time()
            record_act_time.append(t_after_act - t_before_act)

        print(f"average time on robot actuation : {np.mean(record_act_time)}")

    else:
        print("Invalid control mode\n Try either 'JointCtrl' or 'EndPoseCtrl'")
        exit()

    setZeroConfiguration(piper)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode_name', type=str, required=True)
    parser.add_argument('--control_mode', type=str, required=True)
    args = vars(parser.parse_args())

    episodeReplayer = EpisodeReplayer(args)
    episodeReplayer.replay()