from replay_episodes import EpisodeReplayer


def experiment(episode_name, control_mode, alt_control_mode, movement_detection):
    episode_replayer = EpisodeReplayer({
        'episode_name': episode_name,
        'control_mode': control_mode,
    })
    episode_replayer.alt_control_mode = alt_control_mode
    episode_replayer.movement_detection = movement_detection

    episode_replayer.replay()
    recorded_end_pose = episode_replayer.record_end_pose

    wi


def main(args):
    experiment('cup_six_50','JointCtrl', None, None)
    experiment('cup_six_50','EndPoseCtrl', None, None)
    experiment('cup_six_50','EndPoseCtrl', 'DetourEndPoseCtrl', 'equal')
    experiment('cup_six_50','EndPoseCtrl', 'JointCtrl', 'equal')

if __name__ == '__main__':
    main()