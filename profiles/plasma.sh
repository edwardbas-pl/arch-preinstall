#!/bin/bash

git clone https://aur.archlinux.org/yay-bin.git && cd yay-bin && makepkg -si --noconfirm && cd .. && rm yay-bin
INSTALL="yay -S --noconfirm "
TERMINAL="kitty"
flat_install="flatpak install --assumeyes"
$install $TERMINAL
# INSTALL="sudo pacman -Sy --neded --noconfirm"
$INSTALL ttf-symbola ttf-dejavu ttf-liberation spectacle pulseaudio pavucontrol eog w3m alsa-firmware apulse pulseaudio-alsa alsa-oss git rar dialog ranger btop gtop htop vim udisks2 autofs numlockx pfetch qbittorrent gimp playerctl code mpv dolphin libreoffice-fresh kcalc flatpak neovim nerd-fonts-complete archlinux-themes-sddm
$INSTALL plasma-desktop plasma-settinngs sddm-kcm kitty
git clonee https://github.com/wsdfhjxc/kwin-scripts.git
cd kwin-scripts
ln -s /run/media/$USER/     ~/Media
sh helper.sh install workspaces-only-on-primary
sh helper.sh install temporary-virtual-desktops
sudo mkdir -p /etc/pulse/default.pa.d/
sudo echo > /etc/pulse/default.pa.d/noise-cancellation.pa << EOF
### Enable Echo/Noise-Cancellation
load-module module-echo-cancel use_master_format=1 aec_method=webrtc aec_args="analog_gain_control=0\ digital_gain_control=1" source_name=echoCancel_source sink_name=echoCancel_sink
set-default-source echoCancel_source
set-default-sink echoCancel_sink
EOF

if [[ -f /sys/clsass/power_supply/BAT0 ]]
then
	$install networkmanager network-manager-applet  tlp tp_smapi acpi_call
fi
$flat_install flathub com.discordapp.Discord
cp /etc/skel/.bashrc $HOME
sudo systemctl enable sddm
