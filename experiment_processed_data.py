import numpy as np
from replay_episodes import EpisodeReplayer


def experiment(episode_name, control_mode, alt_control_mode, threshold):
    episode_replayer = EpisodeReplayer({
        'episode_name': episode_name,
        'control_mode': control_mode,
    })
    episode_replayer.alt_control_mode = alt_control_mode

    end_pose_data = episode_replayer.end_pose_data.copy()
    episode_replayer.end_pose_data = process_data(end_pose_data, threshold)

    print(f'experiment {episode_name} {control_mode} {alt_control_mode} {threshold}')
    episode_replayer.replay()
    recorded_end_pose = episode_replayer.record_end_pose

    return recorded_end_pose


def process_data(data, threshold):
    x,y,z = data[:,0], data[:,1], data[:,2]
    rx, ry, rz = data[:,3], data[:,4], data[:,5]

    dx = np.diff(x)
    dy = np.diff(y)
    dz = np.diff(z)

    dist = np.sqrt(np.power(dx,2) + np.power(dy,2) + np.power(dz,2))
    indices = np.where(dist < threshold)[0]

    x_re = np.hstack([x[0], x[indices]])
    y_re = np.hstack([y[0], y[indices]])
    z_re = np.hstack([z[0], z[indices]])

    rx_re = np.stack([rx[0], rx[indices]])
    ry_re = np.stack([ry[0], ry[indices]])
    rz_re = np.stack([rz[0], rz[indices]])

    processed_data = np.column_stack([x_re, y_re, z_re, rx_re, ry_re, rz_re])
    return processed_data


def main():
    episode_name = 'arrange_cups_2_30'
    control_mode = 'EndPoseCtrl'

    data1=experiment(episode_name, control_mode, None, 50)
    data2=experiment(episode_name, control_mode, None, 100)
    data3=experiment(episode_name, control_mode, None, 500)
    data4=experiment(episode_name, control_mode, None, 1000)
    data5=experiment(episode_name, control_mode, None, 5000)


if __name__ == "__main__":
    main()