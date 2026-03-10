
## In ssh.py, what does "defaults vary" mean?

On line 70, "not set (defaults vary)" is the message shown when PasswordAuthentication is not explicitly 
configured in the SSH config (`sshd_config`).
 
It means: if the directive is absent, the actual default behavior depends on the OpenSSH version and 
OS/distro. For example:
 
- Older OpenSSH (before ~9.0): defaults to yes (password auth enabled) 
- Newer OpenSSH (9.0+): some builds default to no, or prefer keyboard-interactive instead
- Distro patches: Ubuntu, RHEL, etc. may ship with their own default overrides in packaged configs

Since the audit can't know which default applies without deeper inspection, it reports a WARN (line 69)
rather than a definitive PASS or FAIL, and surfaces "defaults vary" to tell the user they should
explicitly set the value rather than relying on an ambiguous default.
