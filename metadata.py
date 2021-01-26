
@metadata_reactor
def add_users(metadata):
    if not node.has_bundle('users'):
        raise DoNotRunAgain

    users = {}
    for username, user_attrs in metadata.get('restic/server', {}).items():
        users[username] = {
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
            users[username]['ssh_pubkeys'] = user_attrs['ssh_pubkeys']

    return {
        'users': users,
    }


@metadata_reactor
def find_clients(metadata):
    server = {}
    for restic_node in sorted(repo.nodes, key=lambda x: x.name):
        if not restic_node.has_bundle('restic'):
            continue

        if restic_node.name == node.name:
            continue

        username = restic_node.metadata.get(f'restic/backup_hosts/{node.name}/username', None)
        if username is None:
            continue

        server.setdefault(username, {}).setdefault('ssh_pubkeys', [])
        pk = restic_node.metadata.get(f'restic/backup_hosts/{node.name}/public_key', None)
        if pk is not None:
            server[username]['ssh_pubkeys'] += [pk, ]

    return {
        'restic': {
            'server': server,
        },
    }
