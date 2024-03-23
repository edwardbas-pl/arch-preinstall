#!bin/bash

echo "performing postinstall script"
sudo echo '
[chaotic-aur]
Include = /etc/pacman.d/chaotic-mirrorlist ' | sudo tee -a /etc/pacman.conf
sudo curl https://aur.chaotic.cx/mirrorlist.txt -o /etc/pacman.d/chaotic-mirrorlist
sudo pacman-key --init
sudo pacman-key --recv-key 3056513887B78AEB --keyserver keyserver.ubuntu.com
sudo pacman-key --lsign-key 3056513887B78AEB
sudo pacman -U 'https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-keyring.pkg.tar.zst' --noconfirm
sudo pacman -U 'https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-mirrorlist.pkg.tar.zst' --noconfirm
git clone https://aur.archlinux.org/yay-bin.git && cd yay-bin && makepkg -si --noconfirm && cd .. && rm yay-bin -rf
yay -Sy
INSTALL="yay -S --noconfirm "
TERMINAL="kitty"
FLAT_INSTALL="flatpak install --assumeyes"
$INSTALL $TERMINAL

git clone https://github.com/edwardbas-pl/backup && cd backup && git clone https://github.com/edwardbas-pl/Wallpapers backgrounds &&sh Restore && cd ..

$INSTALL gnome-shell gnome-tweaks gnome-control-center gdm gnome-shell-extension-installer gnome-calculatoreog file-roller qbittorrent gimp  code mpv nemo libreoffice-fresh gnome-calculator  #gui apps
$INSTALL xdg-desktop-portal-gnome 
$INSTALL xdg-desktop-portal
sudo systemctl enable gdm

ln -s /run/media/$USER/     ~/Media

# Unused packages
# playerctl

$INSTALL ttf-symbola ttf-dejavu ttf-liberation nerd-fonts #fonts
$INSTALL w3m nodejs git rar dialog ranger btop gtop htop vim udisks2 autofs numlockx pfetch flatpak neovim xorg-xkill xorg-xinit #terminal utilities
$INSTALL pavucontrol alsa-oss

gsettings set org.cinnamon.desktop.default-applications.terminal exec "$TERMINAL"
xdg-mime default nemo.desktop inode/directory

GNOME_VERSION=$(gnome-shell --version | awk '{print $3}' | cut -d'.' -f 1)
declare -a array=( 2890 615 1460 3193 5547 1160 1319 )
arraylength=${#array[@]}
for (( i=0; i<${arraylength}; i++ ));
do
  # echo "gnome-shell-extension-installer --yes" ${array[$i]} $GNOME_VERSION 
  string-"gnome-shell-extension-installer --yes ${array[$i]} $GNOME_VERSION"
  # gnome-shell-extension-installer --yes ${array[$i]} $GNOME_VERSION 
done


sudo curl https://raw.githubusercontent.com/chaotic-aur/chaotic-aur.github.io/master/mirrorlist.txt --output /etc/pacman.d/chaotic-mirrorlist

$INSTALL gnome-shell-extension-arc-menu-git 
$INSTALL gnome-shell-extension-dash-to-panel-git
$INSTALL gnome-shell-extension-dash-to-vitals
$INSTALL gnome-shell-extension-appindicator-git
$INSTALL gnome-shell-extension-blur-my-shell
$INSTALL gnome-shell-extension-custom-accent-colors-git

sudo mkdir -p /etc/pulse/default.pa.d/
### Enable Echo/Noise-Cancellation
sudo echo 'load-module module-echo-cancel use_master_format=1 aec_method=webrtc aec_args="analog_gain_control=0\ digital_gain_control=1" source_name=echoCancel_source sink_name=echoCancel_sink' > /etc/pulse/default.pa.d/noise-cancellation.pa
sudo echo 'set-default-source echoCancel_source' >> /etc/pulse/default.pa.d/noise-cancellation.pa
sudo echo 'set-default-sink echoCancel_sink' >> /etc/pulse/default.pa.d/noise-cancellation.pa
EOF
if [[ -f /sys/clsass/power_supply/BAT0 ]]
then
	$INSTALL networkmanager network-manager-applet  tlp tp_smapi acpi_call
fi


$FLAT_INSTALL flathub com.discordapp.Discord
gsettings set org.gnome.shell.keybindings show-screenshot-ui "['<Shift><Super>s']"
gsettings set org.gnome.shell.keybindings toogle-overview "['<Super><Tab>']"
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'

rm gnome.sh
clear

sudo reboot
