#!bin/bash
#

echo "performing postinstall script"
git clone https://aur.archlinux.org/yay-bin.git && cd yay-bin && makepkg -si --noconfirm && cd .. && rm yay-bin
install="yay -S --noconfirm "
TERMINAL="kitty"
flat_install="flatpak install --assumeyes"
$install $TERMINAL

git clone https://github.com/edwardbas-pl/backup && cd backup && sh Restore && cd ..

$install gnome-shell gnome-tweaks gnome-control-center gdm gnome-shell-extension-installer
sudo systemctl enable gdm

ln -s /run/media/$USER/     ~/Media

$install ttf-symbola ttf-dejavu ttf-liberation spectacle pulseaudio pavucontrol feh w3m alsa-firmware apulse pulseaudio-alsa alsa-oss nodejs git rar dialog ranger btop gtop htop vim udisks2 autofs numlockx python-pywal pfetch qbittorrent gimp playerctl code mpv nautilus nemo libreoffice-fresh galculator flatpak neovim nerd-fonts-complete

gsettings set org.cinnamon.desktop.default-applications.terminal exec $TERMINAL


GNOME_VERSION=$(gnome-shell --version | awk '{print $3}' | cut -d'.' -f 1)
declare -a array=( 2890 615 1460 3193 5547 1160 1319 )
arraylength=${#array[@]}
for (( i=0; i<${arraylength}; i++ ));
do
  # echo "gnome-shell-extension-installer --yes" ${array[$i]} $GNOME_VERSION 
  string-"gnome-shell-extension-installer --yes ${array[$i]} $GNOME_VERSION"
  # gnome-shell-extension-installer --yes ${array[$i]} $GNOME_VERSION 
done

$install gnome-shell-extension-arc-menu-git 
$install gnome-shell-extension-dash-to-panel-git
$install gnome-shell-extension-dash-to-vitals
$install gnome-shell-extension-appindicator-git
$install gnome-shell-extension-blur-my-shell
$install gnome-shell-extension-custom-accent-colors-git

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
clear
sudo reboot

