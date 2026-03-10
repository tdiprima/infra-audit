### ⚠️ SSH password authentication: not set

```sh
sudo vim /etc/ssh/sshd_config
```

### ⚠️ ufw found but could not query status (try running as root)

```sh
# Query status
sudo ufw status
sudo systemctl status ufw
```

### ⚠️ 5 listening TCP port(s) detected

```sh
# List them
sudo lsof -iTCP -sTCP:LISTEN -nP
```

### ❌ 2 failed services

```sh
# List them
sudo systemctl --failed --no-pager --no-legend
```

### ⚠️ 3 package(s) outdated (apt)

```sh
sudo apt update
sudo apt upgrade
sudo apt autoremove
```

<br>
