global node, BundleException, repo

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

    reset_piggy_files = []

    for user_name, user in node.metadata.get('restic', {}).get('server', {}).items():
        home = user.get('home', f'/home/{user_name}')
        monitor_home = node.metadata.get('restic/server/' + user.get('monitoring_user', user_name), {}).get('home')
        piggy_file = f'{monitor_home}/piggy_restic'

        if not user.get('clients', None):
            continue

        cron += [
            f'##### {user_name} #####',
        ]

        if piggy_file not in reset_piggy_files:
            cron += [
                f'echo "" > {piggy_file}_tmp',
            ]
            reset_piggy_files += [piggy_file, ]

        for restic_nodename in user.get('clients', []):
            restic_node = repo.get_node(restic_nodename)
            hostname = restic_node.hostname

            cron += [
                f'echo "<<<<{hostname}>>>>" >> {piggy_file}_tmp',
                f'echo "<<<local>>>" >> {piggy_file}_tmp',
                f'/opt/restic/restic_last_change.sh {home}/{restic_nodename} >> {piggy_file}_tmp',
            ]

        cron += [
            f'echo "<<<<>>>>" >> {piggy_file}_tmp',
            '',
            f'mv {piggy_file}_tmp {piggy_file}',
        ]
    files['/etc/cron.hourly/restic_last_backup'] = {
        'content': '\n'.join(cron) + '\n',
        'mode': '0755',
    }

