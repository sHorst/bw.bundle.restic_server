

# restic Server consists basicaly of a rsync Server
if not node.has_bundle('openssh'):
    raise BundleException('SSH is needed')

# Fail if we do not have rssh and there is a user, which needs it
if not node.has_bundle('rssh'):
    for username, user_attrs in node.metadata.get('users', {}).items():
        if user_attrs.get('shell', None) == '/usr/bin/rssh':
            raise BundleException('rSSH is needed')

files = {}

if node.has_bundle('check_mk_agent'):
    files['/opt/restic/restic_last_change.sh'] = {
        'mode': '0755',
        'content_type': 'jinja2',
        'context': {
            'server_name': node.hostname,
        }
    }

    cron = [
        '#!/usr/bin/env bash',
    ]

    for user_name, user in node.metadata.get('restic', {}).get('server', {}).items():
        home = user.get('home', f'/home/{user_name}')
        piggy_file = f'{home}/piggy_restic'

        cron += [
            f'echo "" > {piggy_file}'
        ]
        for restic_nodename in user.get('clients', []):
            restic_node = repo.get_node(restic_nodename)
            hostname = restic_node.hostname

            cron += [
                f'echo "<<<<{hostname}>>>>" >> {piggy_file}',
                f'echo "<<<local>>>" >> {piggy_file}',
                f'/opt/restic/restic_last_change.sh {home}/{restic_nodename} >> {piggy_file}',
            ]

        cron += [
            f'echo "<<<<>>>>" >> {piggy_file}',
        ]
    files['/etc/cron.hourly/restic_last_backup'] = {
        'content': '\n'.join(cron) + '\n',
        'mode': '0755',
    }
