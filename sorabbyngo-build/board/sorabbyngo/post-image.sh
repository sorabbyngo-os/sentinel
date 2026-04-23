#!/bin/bash
set -e

echo "[sorabbyngo] Post-image starting..."
echo "[sorabbyngo] Build artifacts:"
ls -lh ${BINARIES_DIR}/

# Rename rootfs for clarity
[ -f "${BINARIES_DIR}/rootfs.ext4" ] && \
    cp "${BINARIES_DIR}/rootfs.ext4" "${BINARIES_DIR}/sorabbyngo-rootfs.ext4" || true

[ -f "${BINARIES_DIR}/rootfs.iso9660" ] && \
    cp "${BINARIES_DIR}/rootfs.iso9660" "${BINARIES_DIR}/sorabbyngo.iso" && \
    echo "[sorabbyngo] ISO ready: ${BINARIES_DIR}/sorabbyngo.iso" || true

echo "[sorabbyngo] Post-image complete."
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║       Sorabbyngo OS — Build Complete                     ║"
echo "║       Rhythm of Digital Life                             ║"
echo "╚══════════════════════════════════════════════════════════╝"
