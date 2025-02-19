from replay_episodes import EpisodeReplayer


def experiment(episode_name, control_mode, alt_control_mode, threshold):
    episode_replayer = EpisodeReplayer({
        'episode_name': episode_name,
        'control_mode': control_mode,
    })
    episode_replayer.alt_control_mode = alt_control_mode

    end_pose_data = episode_replayer.end_pose_data.copy()
    episode_replayer.end_pose_data = process_data(end_pose_data)

    print(f'experiment {episode_name} {control_mode} {alt_control_mode} {threshold}')
    episode_replayer.replay()
    recorded_end_pose = episode_replayer.record_end_pose

    return recorded_end_pose


def process_data(data, threshold):
    pass


def main():
    experiment()


if __name__ == "__main__":
    main()