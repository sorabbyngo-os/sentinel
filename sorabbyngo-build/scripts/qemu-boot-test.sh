#!/bin/bash
# =============================================================================
# Sorabbyngo OS — QEMU Boot Test
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/../output/images"
ISO="${BUILD_DIR}/sorabbyngo.iso"
HEADLESS=false
TIMEOUT=120

while [[ $# -gt 0 ]]; do
    case $1 in
        --headless) HEADLESS=true ;;
        --iso) ISO="$2"; shift ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
    shift
done

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║       Sorabbyngo OS — QEMU Boot Test                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

if ! command -v qemu-system-x86_64 &>/dev/null; then
    echo "[ERROR] qemu-system-x86_64 not found."
    echo "  Install: sudo apt-get install qemu-system-x86"
    exit 1
fi

if [ ! -f "${ISO}" ]; then
    echo "[ERROR] ISO not found: ${ISO}"
    echo "  Build first: make sorabbyngo_x86_64_defconfig && make -j\$(nproc)"
    exit 1
fi

echo "[INFO] ISO: ${ISO} ($(du -sh "${ISO}" | cut -f1))"
echo ""

QEMU_COMMON=(
    qemu-system-x86_64
    -m 2G
    -smp 2
    -cdrom "${ISO}"
    -boot d
    -drive "file=${BUILD_DIR}/sorabbyngo-test-disk.qcow2,if=virtio,format=qcow2"
    -netdev "user,id=net0,hostfwd=tcp::2222-:22,hostfwd=tcp::4222-:4222,hostfwd=tcp::8000-:8000"
    -device "virtio-net-pci,netdev=net0"
    -serial stdio
    -no-reboot
)

if $HEADLESS; then
    echo "[INFO] Headless mode — monitoring serial output..."
    echo ""

    [ ! -f "${BUILD_DIR}/sorabbyngo-test-disk.qcow2" ] && \
        qemu-img create -f qcow2 "${BUILD_DIR}/sorabbyngo-test-disk.qcow2" 8G

    MARKERS=(
        "SORABBYNGO.*Boot sequence starting"
        "SORABBYNGO.*NodeID"
        "SORABBYNGO.*NATS running"
        "SORABBYNGO.*Byngox running"
        "SORABBYNGO.*System ready"
        "Chameha"
    )

    LOG="${BUILD_DIR}/qemu-boot-$(date +%Y%m%d-%H%M%S).log"
    echo "[INFO] Boot log: ${LOG}"

    timeout ${TIMEOUT} "${QEMU_COMMON[@]}" -display none 2>&1 | tee "${LOG}" &
    QEMU_PID=$!

    PASSED=0
    for marker in "${MARKERS[@]}"; do
        if timeout 30 grep -m1 -P "${marker}" <(tail -f "${LOG}" 2>/dev/null) 2>/dev/null; then
            echo "  ✅ ${marker}"
            ((PASSED++))
        else
            echo "  ⏳ ${marker} — not detected"
        fi
    done

    kill ${QEMU_PID} 2>/dev/null || true
    wait ${QEMU_PID} 2>/dev/null || true

    echo ""
    [ ${PASSED} -ge 3 ] && echo "✅ Boot test PASSED" && exit 0
    echo "⚠️  Boot test INCOMPLETE — check ${LOG}"
    exit 1

else
    echo "[INFO] Interactive — Ctrl+A X to exit QEMU"
    echo ""

    [ ! -f "${BUILD_DIR}/sorabbyngo-test-disk.qcow2" ] && \
        qemu-img create -f qcow2 "${BUILD_DIR}/sorabbyngo-test-disk.qcow2" 8G

    "${QEMU_COMMON[@]}" -enable-kvm 2>/dev/null || "${QEMU_COMMON[@]}"
fi
