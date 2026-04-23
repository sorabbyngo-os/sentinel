#!/bin/bash
set -e

echo "[sorabbyngo] Post-build starting..."

# Hostname and issue
echo "sorabbyngo" > ${TARGET_DIR}/etc/hostname
echo "Sorabbyngo OS — Rhythm of Digital Life" > ${TARGET_DIR}/etc/issue

# Runtime directories
mkdir -p ${TARGET_DIR}/var/lib/sorabbyngo/nats
mkdir -p ${TARGET_DIR}/var/log/sorabbyngo
mkdir -p ${TARGET_DIR}/var/lib/cyberwall/quarantine
mkdir -p ${TARGET_DIR}/etc/sorabbyngo/nats
mkdir -p ${TARGET_DIR}/opt/sorabbyngo/chameha/audit
mkdir -p ${TARGET_DIR}/run/sorabbyngo

# Install NATS config
cp ${BUILD_DIR}/../board/sorabbyngo/overlay/opt/sorabbyngo/sorabbyngo-os/os/core-services/nats/nats-server.conf \
   ${TARGET_DIR}/etc/sorabbyngo/nats/nats-server.conf 2>/dev/null || true

# Install systemd units
SYSTEMD_DIR="${TARGET_DIR}/usr/lib/systemd/system"
mkdir -p "${SYSTEMD_DIR}"

cp board/sorabbyngo/overlay/opt/sorabbyngo/sorabbyngo-os/os/core-services/systemd/sorabbyngo-nats.service \
   "${SYSTEMD_DIR}/" 2>/dev/null || true
cp board/sorabbyngo/overlay/opt/sorabbyngo/sorabbyngo-os/os/core-services/systemd/sorabbyngo.target \
   "${SYSTEMD_DIR}/" 2>/dev/null || true

# Install kernel modules
KV=$(cat ${BUILD_DIR}/linux-custom/include/config/kernel.release 2>/dev/null || echo "6.19.10-sorabbyngo")
MDIR="${TARGET_DIR}/lib/modules/${KV}/kernel/drivers/sorabbyngo"
mkdir -p "${MDIR}/byngonet"

for ko in sorabbyngo_nodeid.ko; do
    src="${BUILD_DIR}/linux-custom/drivers/sorabbyngo/${ko}"
    [ -f "${src}" ] && cp "${src}" "${MDIR}/" && echo "[sorabbyngo] ${ko} installed" || \
        echo "[sorabbyngo] WARN: ${ko} not found"
done

for ko in byngonet_identity.ko; do
    src="${BUILD_DIR}/linux-custom/drivers/sorabbyngo/byngonet/${ko}"
    [ -f "${src}" ] && cp "${src}" "${MDIR}/byngonet/" && echo "[sorabbyngo] ${ko} installed" || \
        echo "[sorabbyngo] WARN: ${ko} not found"
done

# Set sorabbyngo-init as PID 1
if [ -f "${TARGET_DIR}/opt/sorabbyngo/sorabbyngo-os/os/init/sorabbyngo-init" ]; then
    cp "${TARGET_DIR}/opt/sorabbyngo/sorabbyngo-os/os/init/sorabbyngo-init" \
       "${TARGET_DIR}/sbin/sorabbyngo-init"
    chmod +x "${TARGET_DIR}/sbin/sorabbyngo-init"
    echo "[sorabbyngo] sorabbyngo-init installed as PID 1"
fi

# Install HAL daemon
if [ -f "${BUILD_DIR}/sorabbyngo-hal/hald" ]; then
    cp "${BUILD_DIR}/sorabbyngo-hal/hald" "${TARGET_DIR}/usr/sbin/sorabbyngo-hald"
    chmod +x "${TARGET_DIR}/usr/sbin/sorabbyngo-hald"
    echo "[sorabbyngo] HAL daemon installed"
fi

echo "[sorabbyngo] Post-build complete."
