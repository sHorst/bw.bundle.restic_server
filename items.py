

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
    }

    cron = [
        '# !/usr/bin/env bash',
    ]

    for user_name, user in node.metadata.get('restic', {}).get('server', {}).items():
        for restic_nodename in user.get('clients', []):
            restic_node = repo.get_node(restic_nodename)
            hostname = restic_node.hostname

            home = user.get('home', f'/home/{user_name}')

            cron += [
                f'echo "<<<<{hostname}>>>>" > /var/lib/check_mk_agent/spool/piggy_{hostname}',
                f'echo "<<<local>>>" >> /var/lib/check_mk_agent/spool/piggy_{hostname}',
                f'/opt/restic/restic_last_change.sh {home}/{restic_nodename} >> /var/lib/check_mk_agent/spool/piggy_{hostname}',
                f'echo "<<<<>>>>" >> /var/lib/check_mk_agent/spool/piggy_{hostname}',
            ]

    files['/etc/cron.hourly/restic_last_backup'] = {
        'content': '\n'.join(cron) + '\n',
        'mode': '0755',
    }
