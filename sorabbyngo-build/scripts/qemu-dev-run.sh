#!/bin/bash
# Sorabbyngo OS — QEMU Dev Run (direct kernel boot, no ISO)
set -e

BUILD_DIR="$(dirname "$0")/../output/images"
KERNEL="${BUILD_DIR}/bzImage"
INITRD="${BUILD_DIR}/rootfs.cpio.gz"

[ ! -f "${KERNEL}" ] && echo "[ERROR] Kernel not found: ${KERNEL}" && exit 1

echo "[INFO] Booting Sorabbyngo OS (dev mode)"
echo "[INFO] Kernel: $(du -sh ${KERNEL} | cut -f1)"
echo ""

qemu-system-x86_64 \
    -m 2G -smp 2 \
    -kernel "${KERNEL}" \
    -initrd "${INITRD}" \
    -append "root=/dev/ram rw console=ttyS0,115200 nokaslr" \
    -netdev "user,id=net0,hostfwd=tcp::2222-:22,hostfwd=tcp::4222-:4222" \
    -device "virtio-net-pci,netdev=net0" \
    -serial stdio \
    -display none \
    -no-reboot \
    ${KVM:+-enable-kvm}
