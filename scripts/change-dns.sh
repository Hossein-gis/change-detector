#!/usr/bin/env bash
#
# change-dns.sh — Set or clear DNS resolvers on Ubuntu (netplan + systemd-resolved)
#
# Usage:
#   sudo ./change-dns.sh <dns1> [dns2] [dns3...]   # Set DNS server(s)
#   sudo ./change-dns.sh                            # Clear override -> back to DHCP/default
#
# Example:
#   sudo ./change-dns.sh 8.8.8.8 8.8.4.4
#
set -euo pipefail

OVERRIDE_FILE="/etc/netplan/90-dns-override.yaml"
BACKUP_DIR="/etc/netplan/.dns-override-backups"

# ---------- output helpers ----------
c_green="\e[32m"; c_red="\e[31m"; c_yellow="\e[33m"; c_bold="\e[1m"; c_reset="\e[0m"

info()  { echo -e "${c_bold}==>${c_reset} $*"; }
ok()    { echo -e "${c_green}✔${c_reset} $*"; }
warn()  { echo -e "${c_yellow}⚠${c_reset} $*"; }
err()   { echo -e "${c_red}✘${c_reset} $*" >&2; }

require_root() {
    if [[ "${EUID}" -ne 0 ]]; then
        err "This script must be run as root. Try: sudo $0 $*"
        exit 1
    fi
}

is_valid_ip() {
    local ip="$1"
    if [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
        local IFS='.'
        read -r -a octets <<< "$ip"
        for o in "${octets[@]}"; do
            (( o >= 0 && o <= 255 )) || return 1
        done
        return 0
    fi
    if [[ "$ip" =~ ^[0-9a-fA-F:]+$ && "$ip" == *:* ]]; then
        return 0
    fi
    return 1
}

detect_interface() {
    local iface
    iface=$(ip -o -4 route show to default 2>/dev/null | awk '{print $5}' | head -n1)
    if [[ -z "$iface" ]]; then
        iface=$(ip -o -6 route show to default 2>/dev/null | awk '{print $5}' | head -n1)
    fi
    if [[ -z "$iface" ]]; then
        err "Could not auto-detect the primary network interface (no default route found)."
        exit 1
    fi
    echo "$iface"
}

backup_existing() {
    if [[ -f "$OVERRIDE_FILE" ]]; then
        mkdir -p "$BACKUP_DIR"
        local ts
        ts=$(date +%Y%m%d-%H%M%S)
        cp "$OVERRIDE_FILE" "${BACKUP_DIR}/90-dns-override.yaml.${ts}.bak"
    fi
}

netplan_apply_and_restart() {
    info "Applying netplan configuration..."
    netplan apply
    sleep 1

    if systemctl is-active --quiet systemd-resolved 2>/dev/null; then
        info "Restarting systemd-resolved and flushing DNS caches..."
        systemctl restart systemd-resolved
        command -v resolvectl &>/dev/null && resolvectl flush-caches || true
    fi
}

show_status() {
    local iface="$1"
    echo
    info "Current DNS configuration for ${c_bold}${iface}${c_reset}:"
    if command -v resolvectl &>/dev/null; then
        resolvectl status "$iface" 2>/dev/null | grep -E "DNS Servers|DNS Domain" | sed 's/^/    /' || true
    fi
}

# ---------- main ----------

require_root

if ! command -v netplan &>/dev/null; then
    err "netplan not found. This script expects a netplan-managed Ubuntu system."
    exit 1
fi

IFACE=$(detect_interface)

if [[ $# -eq 0 ]]; then
    # ---- CLEAR MODE ----
    if [[ -f "$OVERRIDE_FILE" ]]; then
        backup_existing
        rm -f "$OVERRIDE_FILE"
        info "Removed custom DNS override for interface ${c_bold}${IFACE}${c_reset}."
        netplan_apply_and_restart
        ok "DNS has been cleared. ${IFACE} will now use whatever DNS it gets from DHCP or its default config."
        show_status "$IFACE"
    else
        warn "No custom DNS override is currently set — nothing to clear."
        show_status "$IFACE"
    fi
    exit 0
fi

# ---- SET MODE ----
DNS_IPS=("$@")

for ip in "${DNS_IPS[@]}"; do
    if ! is_valid_ip "$ip"; then
        err "'$ip' is not a valid IPv4/IPv6 address."
        exit 1
    fi
done

info "Setting DNS for interface ${c_bold}${IFACE}${c_reset} to: ${DNS_IPS[*]}"

backup_existing

{
    echo "network:"
    echo "  version: 2"
    echo "  ethernets:"
    echo "    ${IFACE}:"
    echo "      nameservers:"
    echo "        addresses:"
    for ip in "${DNS_IPS[@]}"; do
        echo "          - ${ip}"
    done
} > "$OVERRIDE_FILE"

chmod 600 "$OVERRIDE_FILE"
ok "Wrote DNS override to ${OVERRIDE_FILE}"

netplan_apply_and_restart

ok "DNS successfully set on ${c_bold}${IFACE}${c_reset}: ${DNS_IPS[*]}"
show_status "$IFACE"

echo
info "To revert to the default/DHCP-provided DNS at any time, run:"
echo "    sudo $0"
