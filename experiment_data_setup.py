import matplotlib.pyplot as plt
import numpy as np

from constants import *
from data_utils import *
from replay_episodes import EpisodeReplayer

def _experiment(episode_name, modified_end_pose_data, delay= False):
    episode_replayer = EpisodeReplayer({
        'episode_name': episode_name,
        'control_mode': 'EndPoseCtrl',
    })

    episode_replayer.end_pose_data = modified_end_pose_data
    episode_replayer.is_experiment = True

    if delay:
        delay_size = 5 // 2
        delayed_gripper = episode_replayer.gripper_data[:-delay_size]
        episode_replayer.gripper_data[delay_size:] = delayed_gripper

    episode_replayer.replay()

    robot_dataset = episode_replayer.robot_dataset
    recorded_end_pose = []
    for robot_data in robot_dataset:
        recorded_end_pose.append(robot_data['robot']['end_pose_data'])

    recorded_end_pose = np.array(recorded_end_pose)
    return recorded_end_pose


def get_indices(coor, threshold):
    x = coor[0]
    y = coor[1]
    z = coor[2]

    dx = np.diff(x)
    dy = np.diff(y)
    dz = np.diff(z)

    dist = np.sqrt(np.power(dx, 2) + np.power(dy, 2) + np.power(dz, 2))
    indices = np.where(dist > threshold)[0]

    return indices


def alt_threshold(data, indices):
    threshold_data = np.zeros_like(data)

    temp = data[0,:]
    for i in range(data.shape[0]):
        if i in indices:
            threshold_data[i,:] = data[i,:]
            temp = data[i,:]
        else:
            threshold_data[i,:] = temp

    return threshold_data


def threshold_data(end_pose_data, threshold):
    x,y,z = end_pose_data[:, 0], end_pose_data[:, 1], end_pose_data[:, 2]
    indices = get_indices([x,y,z], threshold)
    processed_end_pose_data = alt_threshold(end_pose_data, indices)

    return processed_end_pose_data, indices


def alternate_data(end_pose_data, joint_data, indices):
    fk_calc = FK_CALC

    def get_detoured_end_pose(joint):
        return 1000 * np.array(fk_calc.CalFK(joint)[-1]).astype(int)

    end_pose_data_alt_ctrl = np.zeros_like(end_pose_data)
    for i in range(end_pose_data.shape[0]):
        if i in indices:
            end_pose_data_alt_ctrl[i,:] = end_pose_data[i,:]
        else:
            joints = deg2rad(0.001 * joint_data[i])
            alt_end_pose_data = get_detoured_end_pose(joints)
            end_pose_data_alt_ctrl[i,:] = alt_end_pose_data

    return end_pose_data_alt_ctrl


def get_moving_average(end_pose_data, window_size):
    end_pose_data = np.array(end_pose_data)
    filtered_data = np.zeros_like(end_pose_data)

    r_data = end_pose_data[:, 3:]

    filtered_data[:window_size] = end_pose_data[:window_size]
    for i in range(window_size, end_pose_data.shape[0]):
        window = end_pose_data[i:i + window_size]
        filtered_data[i] = np.mean(window, axis=0)

    filtered_data = filtered_data.astype(np.int32)
    filtered_data[:, 3:] = r_data

    delay = window_size // 2
    delayed_r_data = r_data[:-delay]
    filtered_data[delay:,3:] = delayed_r_data
    return filtered_data


def plot_end_pose_data(list_of_end_pose_data, plot_legend):
    fig, ax = plt.subplots(3,2, figsize=[25, 15])

    for end_pose_data in list_of_end_pose_data:
        end_pose_data = np.array(end_pose_data).astype(np.int32)
        ax[0, 0].plot(end_pose_data[:, 0])
        ax[1, 0].plot(end_pose_data[:, 1])
        ax[2, 0].plot(end_pose_data[:, 2])
        ax[0, 1].plot(end_pose_data[:, 3])
        ax[1, 1].plot(end_pose_data[:, 4])
        ax[2, 1].plot(end_pose_data[:, 5])

    for row in range(ax.shape[0]):
        for col in range(ax.shape[1]):
            if col == 1:
                ax[row, col].set_ylim([-200000, 200000])
            else:
                if row == 1:
                    ax[row, col].set_ylim([-500000, 500000])
                else:
                    ax[row, col].set_ylim([0, 500000])
            ax[row,col].grid(True)
            ax[row,col].legend(plot_legend)

    plt.show()


def main():
    episode_name = 'test2'
    experiment_name = 'opt_data_setup'
    joint_data = load_episode(episode_name)['robot']['joint_data']
    end_pose_data = load_episode(episode_name)['robot']['end_pose_data']

    ref_data = np.array(end_pose_data)
    end_pose_data_threshold, indices = threshold_data(ref_data, 1000)
    end_pose_data_alt_ctrl = alternate_data(end_pose_data_threshold, joint_data, indices)
    end_pose_data_ma5 = get_moving_average(end_pose_data_alt_ctrl, 5)

    # ref_data_re = _experiment(episode_name, end_pose_data)
    # end_pose_data_threshold_re = _experiment(episode_name, end_pose_data_threshold)
    # end_pose_data_alt_ctrl_re = _experiment(episode_name, end_pose_data_alt_ctrl)
    # end_pose_data_ma5_re = _experiment(episode_name, end_pose_data_ma5, delay= True)
    #
    # save_exp_csv(ref_data, 'ref_data', experiment_name)
    # save_exp_csv(end_pose_data_threshold, 'threshold_data', experiment_name)
    # save_exp_csv(end_pose_data_alt_ctrl, 'altered_data', experiment_name)
    # save_exp_csv(end_pose_data_ma5, 'ma5_data', experiment_name)
    #
    # save_exp_csv(ref_data_re, 'ref_data_re', experiment_name)
    # save_exp_csv(end_pose_data_threshold_re, 'threshold_data_re', experiment_name)
    # save_exp_csv(end_pose_data_alt_ctrl_re, 'altered_data_re', experiment_name)
    # save_exp_csv(end_pose_data_ma5_re, 'ma_5_re', experiment_name)

    ref_data = load_exp_csv(experiment_name, 'ref_data')
    end_pose_data_threshold = load_exp_csv(experiment_name, 'threshold_data')
    end_pose_data_alt_ctrl = load_exp_csv(experiment_name, 'end_pose_data_alt_ctrl')
    end_pose_data_ma5 = load_exp_csv(experiment_name, 'ma_5')

    ref_data_re = load_exp_csv(experiment_name, 'ref_data')
    end_pose_data_threshold_re = load_exp_csv(experiment_name, 'threshold_data_re')
    end_pose_data_alt_ctrl_re = load_exp_csv(experiment_name, 'end_pose_data_alt_ctrl_re')
    end_pose_data_ma5_re = load_exp_csv(experiment_name, 'ma_5_re')

    data_to_plot = [ref_data, end_pose_data_threshold, end_pose_data_alt_ctrl, end_pose_data_ma5, ref_data_re, end_pose_data_threshold_re, end_pose_data_alt_ctrl_re, end_pose_data_ma5_re]
    plot_legend = ['ref_data', 'end_pose_data_threshold', 'end_pose_data_alt_ctrl', 'end_pose_data_ma_5', 'ref_data_re', 'end_pose_data_threshold_re', 'end_pose_data_alt_ctrl_re', 'end_pose_data_ma_5_re']

    # data_to_plot = [ref_data, ref_data_re, end_pose_data_threshold_re, end_pose_data_alt_ctrl_re, ma_5_re]
    # plot_legend = ['ref_data', 'ref_data_re', 'end_pose_data_threshold_re', 'end_pose_data_alt_ctrl_re', 'ma_5_re']

    # data_to_plot = [ref_data, end_pose_data_threshold, end_pose_data_alt_ctrl, end_pose_data_ma5]
    # plot_legend = ['ref_data', 'end_pose_data_threshold', 'end_pose_data_alt_ctrl', 'end_pose_data_ma_5']

    plot_end_pose_data(data_to_plot, plot_legend)


if __name__ == "__main__":
    main()