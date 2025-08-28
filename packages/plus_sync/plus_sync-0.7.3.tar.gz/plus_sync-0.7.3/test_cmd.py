import plus_sync.cmd

if __name__ == '__main__':
    plus_sync.cmd.app(['sync', 'audiograms', '--limit', 3])
    # plus_sync.cmd.app(['ls', 'thht_cocktaileye'])
    # plus_sync.cmd.main.app(['add', 'gitlab-config', 'thht_cocktaileye2', 'thht_experiments/do-not-track-my-cocktail-eye', 'eye_data/eye_data'])  # noqa
    # plus_sync.cmd.app(['list-subjects', 'meg_donottrack'])
