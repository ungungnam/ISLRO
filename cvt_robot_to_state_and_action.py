import pickle

for i in range(1,10):
    with open(f'/home/islab/islab_ws/ISLRO/record/aligncups_episode{i}/aligncups_episode{i}.pickle', 'rb') as f:
        record_data = pickle.load(f)

    with open(f'/home/islab/islab_ws/ISLRO/replay/aligncups_episode{i}/aligncups_episode{i}.pickle', 'rb') as f:
        replay_data_to_read = pickle.load(f)

    replay_data_to_read['action'] = record_data['robot']
    replay_data_to_read['state'] = replay_data_to_read['robot']
    del replay_data_to_read['robot']

    print(replay_data_to_read.keys())
    print(replay_data_to_read['state'].keys())
    print(replay_data_to_read['action'].keys())

    with open(f'/home/islab/islab_ws/ISLRO/replay/aligncups_episode{i}/aligncups_episode{i}.pickle', 'wb') as f:
        pickle.dump(replay_data_to_read, f, pickle.HIGHEST_PROTOCOL)