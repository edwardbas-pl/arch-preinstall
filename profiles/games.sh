#!/bin/bash
#
sudo echo '
[rumpowered]
Server = https://jc141x.github.io/rumpowered-packages/$arch' | sudo tee -a /etc/pacman.conf

sudo sed -i "/\[multilib\]/,/Include/"'s/^#//' /etc/pacman.conf
sudo pacman-key --recv-keys cc7a2968b28a04b3
sudo pacman-key --lsign-key cc7a2968b28a04b3

sudo pacman -S --needed {lib32-,}{alsa-lib,alsa-plugins,libpulse,pipewire,openal,libxcrypt-compat,gst-plugins-{good,base,base-libs},sdl2_ttf,sdl2_image} dwarfs fuse-overlayfs wine-staging bubblewrap libgphoto2 xdg-user-dirs && xdg-user-dirs-update


GPU=$(lspci | grep -i --color 'vga\|4d\|2d')

# echo $GPU
if [[ $GPU = *NVIDIA* ]];
then
    echo 'Found NVIDIA GPU!'
    sudo pacman -S --needed nvidia-dkms nvidia-utils lib32-nvidia-utils nvidia-settings vulkan-icd-loader lib32-vulkan-icd-loader --noconfirm
fi
if [[ $GPU = *Radeon* ]];
then
    echo 'Found AMD GPU!'
    sudo pacman -R amdvlk && sudo pacman -R vulkan-amdgpu-pro
    sudo pacman -S --needed lib32-mesa vulkan-radeon lib32-vulkan-radeon vulkan-icd-loader lib32-vulkan-icd-loader --noconfirm
fi
if [[ $GPU = *Intel* ]];
then
    echo 'Found intel GPU!'
    sudo pacman -S --needed lib32-mesa vulkan-intel lib32-vulkan-intel vulkan-icd-loader lib32-vulkan-icd-loader --noconfirm
fi

$INSTALL steam lutris
