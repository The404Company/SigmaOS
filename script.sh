sudo apt update
sudo apt install -y live-build git python3 python3-venv curl xorriso

mkdir ~/sigmaos-build
cd ~/sigmaos-build

git clone https://github.com/Lominub44/SigmaOS.git

lb config --mode debian --architecture amd64 \
  --bootappend-live "boot=live components quiet" \
  --binary-images iso-hybrid

mkdir -p config/hooks/live
cat << 'EOF' > config/hooks/live/99-sigmaos-autostart.chroot
#!/bin/bash
set -e

apt update
apt install -y python3 python3-venv

cp -r /root/SigmaOS /opt/SigmaOS
cd /opt/SigmaOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt || true

cat << EOM > /opt/SigmaOS/start.sh
#!/bin/bash
cd /opt/SigmaOS
source venv/bin/activate
python3 SigmaOS.py
poweroff
EOM

chmod +x /opt/SigmaOS/start.sh

echo "/opt/SigmaOS/start.sh" >> /root/.bash_profile
EOF
chmod +x config/hooks/live/99-sigmaos-autostart.chroot

cp -r SigmaOS config/includes.chroot/root/SigmaOS

sudo lb build
