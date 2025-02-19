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
    episode_name = 'arrange_cups_2_30'
    experiment_name = 'no_config_2'
    instance_name_list = ['ref_data','JointCtrl', 'EndPoseCtrl', 'EndPoseCtrl_DetourEndPoseCtrl', 'EndPoseCtrl_JointCtrl']

    # data1 = experiment(episode_name,'JointCtrl', None, None)
    # data2 = experiment(episode_name,'EndPoseCtrl', None, None)
    # data3 = experiment(episode_name,'EndPoseCtrl', 'DetourEndPoseCtrl', 'equal')
    # data4 = experiment(episode_name,'EndPoseCtrl', 'JointCtrl', 'equal')
    # data5 = experiment(episode_name, 'ForwardKinematicsCtrl', False, False)
    #
    # assert len(data1) == len(data2)
    # assert len(data1) == len(data3)
    # assert len(data1) == len(data4)
    #
    # save_exp_csv(data1, 'JointCtrl', experiment_name)
    # save_exp_csv(data2, 'EndPoseCtrl', experiment_name)
    # save_exp_csv(data3, 'EndPoseCtrl_DetourEndPoseCtrl', experiment_name)
    # save_exp_csv(data4, 'EndPoseCtrl_JointCtrl', experiment_name)
    # save_exp_csv(data5, 'ForwardKinematicsCtrl', experiment_name)

    _, _, end_pose_data = load_h5_data(file_name=f'dataset/episode_{episode_name}.h5')

    data1 = load_exp_csv(experiment_name, 'JointCtrl')
    data2 = load_exp_csv(experiment_name, 'EndPoseCtrl')
    data3 = load_exp_csv(experiment_name, 'EndPoseCtrl_DetourEndPoseCtrl')
    data4 = load_exp_csv(experiment_name, 'EndPoseCtrl_JointCtrl')
    # data5 = load_exp_csv(experiment_name, 'ForwardKinematicsCtrl')

    fig, ax = plt.subplots(3,2, figsize=[25, 15])

    plot_data(ax, end_pose_data)
    plot_data(ax,data1)
    plot_data(ax,data2)
    plot_data(ax,data3)
    plot_data(ax,data4)
    # plot_data(ax,data5)

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

    fig, ax = plt.subplots(4,1, figsize=[10, 10])
    mse = []
    for data in [data1, data2, data3, data4]:
        data_arr = np.array(data).astype(float)
        x1 = data_arr[:,0] - end_pose_data[:,0]
        y1 = data_arr[:,1] - end_pose_data[:,1]
        z1 = data_arr[:,2] - end_pose_data[:,2]
        dist1 = np.sqrt(np.power(x1,2) + np.power(y1,2) + np.power(z1,2))
        dist1 = 0.001 * dist1
        mse.append(np.mean(dist1))
        ax[0].plot(x1)
        ax[1].plot(y1)
        ax[2].plot(z1)
        ax[3].plot(dist1)
        for axes in ax:
            axes.grid(True)
            axes.legend(instance_name_list[1:])

    plt.show()
    print(f'MSE of Cartesian distance\nJointCtrl : {mse[0]}\nEndPoseCtrl : {mse[1]}\nEndPoseCtrl+Detour : {mse[2]}\nEdnPoseCtrl+Joint : {mse[3]}')


if __name__ == '__main__':
    main()