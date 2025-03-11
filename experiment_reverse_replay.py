import matplotlib.pyplot as plt
import numpy as np

from constants import *
from data_utils import *
from replay_episodes import EpisodeReplayer

def _experiment(episode_name, is_reversed):
    episode_replayer = EpisodeReplayer({
        'episode_name': episode_name,
        'control_mode': 'EndPoseCtrl',
    })

    if not is_reversed:
        episode_replayer.replay()
    else:
        episode_replayer.reverse_replay()

    robot_dataset = episode_replayer.robot_dataset
    recorded_end_pose = []
    for robot_data in robot_dataset:
        recorded_end_pose.append(robot_data['robot']['end_pose'])

    recorded_end_pose = np.array(recorded_end_pose)
    return recorded_end_pose


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
    episode_name = 'paper_cup_5'
    experiment_name = 'reverse_replay'
    end_pose_data = load_episode(episode_name)['robot']['end_pose_data']

    ref_data = np.array(end_pose_data)

    end_pose_data_re = _experiment(episode_name, is_reversed=False)
    end_pose_data_reversed = _experiment(episode_name, is_reversed=True)

    save_exp_csv(ref_data, 'ref_data', experiment_name)
    save_exp_csv(end_pose_data_re, 'ref_data_re', experiment_name)
    save_exp_csv(end_pose_data_reversed, 'rev_data_re', experiment_name)

    # ref_data = load_exp_csv(experiment_name, 'ref_data')
    # end_pose_data_threshold = load_exp_csv(experiment_name, 'threshold_data')
    # end_pose_data_alt_ctrl = load_exp_csv(experiment_name, 'end_pose_data_alt_ctrl')
    # end_pose_data_ma5 = load_exp_csv(experiment_name, 'ma_5')
    #
    # ref_data_re = load_exp_csv(experiment_name, 'ref_data')
    # end_pose_data_threshold_re = load_exp_csv(experiment_name, 'threshold_data_re')
    # end_pose_data_alt_ctrl_re = load_exp_csv(experiment_name, 'end_pose_data_alt_ctrl_re')
    # end_pose_data_ma5_re = load_exp_csv(experiment_name, 'ma_5_re')

    data_to_plot = [ref_data, end_pose_data_re, end_pose_data_reversed]
    plot_legend = ['ref_data', 'ref_data_re', 'end_pose_data_reversed']

    plot_end_pose_data(data_to_plot, plot_legend)


if __name__ == "__main__":
    main()