import numpy as np
from replay_episodes import EpisodeReplayer


def _experiment(episode_name, control_mode, alt_control_mode, threshold):
    episode_replayer = EpisodeReplayer({
        'episode_name': episode_name,
        'control_mode': control_mode,
    })
    episode_replayer.alt_control_mode = alt_control_mode

    end_pose_data = episode_replayer.end_pose_data.copy()
    gripper_data = episode_replayer.gripper_data.copy()
    episode_replayer.end_pose_data, episode_replayer.gripper_data = process_data(end_pose_data, gripper_data, threshold)

    print(f'experiment {episode_name} {control_mode} {alt_control_mode} {threshold}')
    episode_replayer.replay()
    recorded_end_pose = episode_replayer.record_end_pose

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


def slice_and_stack(data, indices):
    data_re = []

    for i in range(data.shape[1]):
        datum = data[:, i]
        datum_re = np.hstack([datum[0], datum[indices]])
        data_re.append(datum_re)

    return np.column_stack(data_re)


def process_data(end_pose_data, gripper_data, threshold):
    x,y,z = end_pose_data[:, 0], end_pose_data[:, 1], end_pose_data[:, 2]
    indices = get_indices([x,y,z], threshold)

    processed_end_pose_data = slice_and_stack(end_pose_data, indices)
    processed_gripper_data = slice_and_stack(gripper_data, indices)

    return processed_end_pose_data, processed_gripper_data


def main():
    episode_name = 'arrange_cups_2_30'
    control_mode = 'EndPoseCtrl'

    data1=_experiment(episode_name, control_mode, None, 50)
    data2=_experiment(episode_name, control_mode, None, 100)
    data3=_experiment(episode_name, control_mode, None, 500)
    data4=_experiment(episode_name, control_mode, None, 1000)
    data5=_experiment(episode_name, control_mode, None, 5000)


if __name__ == "__main__":
    main()