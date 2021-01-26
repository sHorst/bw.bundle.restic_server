
@metadata_reactor
def add_users(metadata):
    if not node.has_bundle('users'):
        raise DoNotRunAgain

    users = {}
    for username, user_attrs in metadata.get('restic/server', {}).items():
        users[f'{username}backup'] = {
            'sudo': False,
            'rssh': {
                'umask': '011',
                'accessbits': '100110',
                'path': '',
            },  # add only RSYNC, SFTP and SCP here
            'home': user_attrs.get('home', "/home/{}".format(username)),
            'full_name': f'Backup user for {username}',
            'password_hash': user_attrs.get('password_hash', '*'),
            'shell': user_attrs.get('shell', '/usr/bin/rssh'),
        }

        if 'ssh_pubkeys' in user_attrs:
            users[f'{username}backup']['ssh_pubkeys'] = user_attrs['ssh_pubkeys']

    return {
        'users': users,
    }
