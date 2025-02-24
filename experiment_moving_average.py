import numpy as np
import matplotlib.pyplot as plt
from data_utils import *
from replay_episodes import EpisodeReplayer

def _experiment(episode_name, ma_end_pose_data, window_size):
    episode_replayer = EpisodeReplayer({
        'episode_name': episode_name,
        'control_mode': 'EndPoseCtrl',
    })

    episode_replayer.end_pose_data = ma_end_pose_data

    delay = window_size // 2
    if delay:
        delayed_gripper = episode_replayer.gripper_data[:-delay]
        episode_replayer.gripper_data[delay:] = delayed_gripper
    episode_replayer.replay()

    recorded_end_pose = episode_replayer.record_end_pose

    return recorded_end_pose


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
    episode_name = 'paper_cup_3'
    experiment_name = 'moving_average_3'
    end_pose_data = load_episode(episode_name)['robot']['end_pose_data']

    ref_data = np.array(end_pose_data)
    ma_2 = get_moving_average(end_pose_data, window_size=2)
    ma_5 = get_moving_average(end_pose_data, window_size=5)
    ma_10 = get_moving_average(end_pose_data, window_size=10)

    ref_data_re = _experiment(episode_name, ref_data, 0)
    ma_2_re=_experiment(episode_name, ma_2, 2)
    ma_5_re=_experiment(episode_name, ma_5, 5)
    ma_10_re=_experiment(episode_name, ma_10, 10)

    save_exp_csv(ref_data, 'ref_data', experiment_name)
    save_exp_csv(ma_2, 'ma_2', experiment_name)
    save_exp_csv(ma_5, 'ma_5', experiment_name)
    save_exp_csv(ma_10, 'ma_10', experiment_name)

    save_exp_csv(ref_data_re, 'ref_data_re', experiment_name)
    save_exp_csv(ma_2_re, 'ma_2_re', experiment_name)
    save_exp_csv(ma_5_re, 'ma_5_re', experiment_name)
    save_exp_csv(ma_10_re, 'ma_10_re', experiment_name)

    # ref_data = load_exp_csv(experiment_name, 'ref_data')
    # ma_2 = load_exp_csv(experiment_name, 'ma_2')
    # ma_5 = load_exp_csv(experiment_name, 'ma_5')
    # ma_10 = load_exp_csv(experiment_name, 'ma_10')
    #
    # ref_data_re = load_exp_csv(experiment_name, 'ref_data_re')
    # ma_2_re = load_exp_csv(experiment_name, 'ma_2_re')
    # ma_5_re = load_exp_csv(experiment_name, 'ma_5_re')
    # ma_10_re = load_exp_csv(experiment_name, 'ma_10_re')

    data_to_plot = [ref_data, ma_2, ma_5, ma_10, ref_data_re, ma_2_re, ma_5_re, ma_10_re]
    plot_legend = ['ref_data', 'ma_2', 'ma_5', 'ma_10', 'ref_data_re', 'ma_2_re', 'ma_5_re', 'ma_10_re']

    # data_to_plot = [ref_data, ref_data_re, ma_2_re, ma_5_re, ma_10_re]
    # plot_legend = ['ref_data', 'ref_data_re', 'ma_2_re', 'ma_5_re', 'ma_10_re']

    # data_to_plot = [ref_data, ma_2, ma_5, ma_10]
    # plot_legend = ['ref_data', 'ma_2', 'ma_5', 'ma_10']

    plot_end_pose_data(data_to_plot, plot_legend)


if __name__ == "__main__":
    main()