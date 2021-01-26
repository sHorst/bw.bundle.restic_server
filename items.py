

# restic Server consists basicaly of a rsync Server
if not node.has_bundle('openssh'):
    raise BundleException('SSH is needed')

# Fail if we do not have rssh and there is a user, which needs it
if not node.has_bundle('rssh'):
    for username, user_attrs in node.metadata.get('users', {}).items():
        if user_attrs.get('shell', None) == '/usr/bin/rssh':
            raise BundleException('rSSH is needed')

