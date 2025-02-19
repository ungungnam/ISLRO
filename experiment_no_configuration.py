import matplotlib.pyplot as plt

from replay_episodes import EpisodeReplayer
from robot_utils import *
from data_utils import *

def experiment(episode_name, control_mode, alt_control_mode, movement_detection):
    episode_replayer = EpisodeReplayer({
        'episode_name': episode_name,
        'control_mode': control_mode,
    })
    episode_replayer.alt_control_mode = alt_control_mode
    episode_replayer.movement_detection = movement_detection

    print(f'experiment {episode_name} {control_mode} {alt_control_mode} {movement_detection}')
    episode_replayer.replay()
    recorded_end_pose = episode_replayer.record_end_pose

    return recorded_end_pose


def plot_data(ax, data):
    data = np.array(data).astype(float)

    x = data[:,0]
    y = data[:,1]
    z = data[:,2]
    rx = data[:,3]
    ry = data[:,4]
    rz = data[:,5]

    ax[0,0].plot(x)
    ax[1,0].plot(y)
    ax[2,0].plot(z)
    ax[0,1].plot(rx)
    ax[1,1].plot(ry)
    ax[2,1].plot(rz)


def main():
    episode_name = 'arrange_cups_50'
    experiment_name = 'no_config'
    instance_name_list = ['ref_data','JointCtrl', 'EndPoseCtrl', 'EndPoseCtrl_DetourEndPoseCtrl', 'EndPoseCtrl_JointCtrl']

    data1 = experiment(episode_name,'JointCtrl', None, None)
    data2 = experiment(episode_name,'EndPoseCtrl', None, None)
    data3 = experiment(episode_name,'EndPoseCtrl', 'DetourEndPoseCtrl', 'equal')
    data4 = experiment(episode_name,'EndPoseCtrl', 'JointCtrl', 'equal')

    assert len(data1) == len(data2)
    assert len(data1) == len(data3)
    assert len(data1) == len(data4)

    save_exp_csv(data1, 'JointCtrl', experiment_name)
    save_exp_csv(data2, 'EndPoseCtrl', experiment_name)
    save_exp_csv(data3, 'EndPoseCtrl_DetourEndPoseCtrl', experiment_name)
    save_exp_csv(data4, 'EndPoseCtrl_JointCtrl', experiment_name)

    _, _, end_pose_data = load_h5_data(file_name=f'dataset/episode_{episode_name}.h5')

    # data1 = load_exp_csv(experiment_name, 'JointCtrl')
    # data2 = load_exp_csv(experiment_name, 'EndPoseCtrl')
    # data3 = load_exp_csv(experiment_name, 'EndPoseCtrl_DetourEndPoseCtrl')
    # data4 = load_exp_csv(experiment_name, 'EndPoseCtrl_JointCtrl')

    fig, ax = plt.subplots(3,2, figsize=[25, 15])

    plot_data(ax, end_pose_data)
    plot_data(ax,data1)
    plot_data(ax,data2)
    plot_data(ax,data3)
    plot_data(ax,data4)

    for row in range(ax.shape[0]):
        for col in range(ax.shape[1]):
            if col == 1:
                ax[row, col].set_ylim([-200000, 200000])
            else:
                if row == 1:
                    ax[row, col].set_ylim([-300000, 300000])
                else:
                    ax[row, col].set_ylim([0, 500000])
            ax[row,col].grid(True)
            ax[row,col].legend(instance_name_list)

    plt.show()


if __name__ == '__main__':
    main()