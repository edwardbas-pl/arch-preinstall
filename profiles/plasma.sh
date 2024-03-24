#!/bin/bash

git clone https://aur.archlinux.org/yay-bin.git && cd yay-bin && makepkg -si --noconfirm && cd .. && rm yay-bin
INSTALL="yay -S --noconfirm "
TERMINAL="kitty"
flat_install="flatpak install --assumeyes"
$install $TERMINAL
# INSTALL="sudo pacman -Sy --neded --noconfirm"

KDE="spectacle plasma-desktop plasma-settinngs sddm-kcm archlinux-themes-sddm plasma-nm dolphin"

# shellcheck disable=SC2034
SOUND="pulseaudio pavucontrol spectacle apulse pulseaudio-alsa alsa-oss alsa-firmware playerctl"

# shellcheck disable=SC2034
FONTS="ttf-symbola ttf-dejavu ttf-liberation nerd-fonts-complete"

# shellcheck disable=SC2034
GUI_APPS="qbittorrent gimp  code mpv  libreoffice-fresh kcalc"

# shellcheck disable=SC2034
MISC="w3m git rar dialog ranger btop gtop htop vim udisks2 autofs numlockx pfetch  flatpak neovim   "

$INSTALL $KDE $TERMINAL $MISC $GUI_APPS $FONTS $SOUND

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

#configuring kde to my liking
#.config/kdeglobas
#.config/plasma-org.kde.plasma.desktop-appletsrc 
# echo $XDG_CURRENT_DESKTOP
git clone https://github.com/wsdfhjxc/kwin-scripts.git
sudo cp -r  kwin-scripts/virtual-desktops-only-on-primary /usr/share/kwin/scripts/
rm kwin-scripts -rf
git clone https://github.com/d86leader/dynamic_workspaces.git
sudo cp -r dynamic_workspaces /usr/share/kwin/scripts/ 
kwriteconfig5 --file kwinrc --group Plugins --key dynamic_workspacesEnabled true
kwriteconfig5 --file kwinrc --group Plugins --key virtual-desktops-only-on-primaryEnabled true

qdbus org.kde.KWin /KWin reconfigure
if [[ -f /sys/clsass/power_supply/BAT0 ]]
then
	$INSTALL networkmanager network-manager-applet  tlp tp_smapi acpi_call
fi
$flat_install flathub com.discordapp.Discord
cp /etc/skel/.bashrc $HOME
sudo systemctl enable sddm
reboot
