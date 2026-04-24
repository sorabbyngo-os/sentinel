# Sorabbyngo OS — Build Guide

## Prerequisites

```bash
sudo apt-get install -y \
    build-essential gcc g++ make git \
    libncurses-dev bison flex \
    libssl-dev libelf-dev \
    python3 python3-pip \
    wget cpio rsync bc \
    qemu-system-x86 qemu-utils \
    golang-go
```

## Build Steps

```bash
# 1 — Configure
make sorabbyngo_x86_64_defconfig

# 2 — Build (30–90 min first time)
make -j$(nproc)

# 3 — Output
ls output/images/
# bzImage                ← Linux kernel
# rootfs.ext4            ← Root filesystem
# rootfs.cpio.gz         ← Initramfs
# sorabbyngo.iso         ← Bootable hybrid ISO
```

## Boot in QEMU

```bash
# Interactive
./scripts/qemu-boot-test.sh

# Headless automated test
./scripts/qemu-boot-test.sh --headless

# Dev mode — direct kernel boot (fastest)
./scripts/qemu-dev-run.sh
```

## Port Forwarding (QEMU)

| Host port | Guest port | Service |
|---|---|---|
| 2222 | 22 | SSH |
| 4222 | 4222 | NATS |
| 8000 | 8000 | Novela API |

Connect: `ssh root@localhost -p 2222` (password: sorabbyngo)

## Production Kernel

For production builds with sorabbyngo patches:
BR2_LINUX_KERNEL_CUSTOM_TARBALL=y
BR2_LINUX_KERNEL_CUSTOM_TARBALL_LOCATION="file:///path/to/linux-6.19.10-sorabbyngo.tar.gz"
BR2_LINUX_KERNEL_USE_CUSTOM_CONFIG=y
BR2_LINUX_KERNEL_CUSTOM_CONFIG_FILE="/path/to/sorabbyngo.config"

## OS Variants

| Variant | Target |
|---|---|
| sorabbyngo_x86_64_defconfig | QEMU, x86 hardware |
| sorabbyngo_arm64_defconfig (planned) | ARM servers |
| sorabbyngo_novela_defconfig (planned) | Hospital deployment |
