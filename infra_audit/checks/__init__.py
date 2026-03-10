from infra_audit.checks.devsecops import (check_exposed_env_files,
                                          check_open_ports)
from infra_audit.checks.docker import check_docker_configs, check_docker_socket
from infra_audit.checks.firewall import check_firewall_status
from infra_audit.checks.packages import check_outdated_packages
from infra_audit.checks.ssh import (check_ssh_password_auth,
                                    check_ssh_root_login)
from infra_audit.checks.system import (check_disk_usage, check_memory_usage,
                                       check_service_failures,
                                       check_zombie_processes)

ALL_CHECKS = [
    check_ssh_root_login,
    check_ssh_password_auth,
    check_firewall_status,
    check_open_ports,
    check_disk_usage,
    check_memory_usage,
    check_zombie_processes,
    check_service_failures,
    check_docker_socket,
    check_docker_configs,
    check_exposed_env_files,
    check_outdated_packages,
]
