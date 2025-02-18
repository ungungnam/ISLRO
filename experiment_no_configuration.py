import replay_episodes

def experiment(episode_name, control_mode, alt_control_mode, movement_detection):
    replay_episodes.main()

def main(args):
    experiment('cup_six_50','JointCtrl', None, None)
    experiment('cup_six_50','EndPoseCtrl', None, None)
    experiment('cup_six_50','EndPoseCtrl', 'DetourEndPoseCtrl', 'equal')
    experiment('cup_six_50','EndPoseCtrl', 'JointCtrl', 'equal')
