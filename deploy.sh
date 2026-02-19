#!/bin/bash

echo "Starting Deployment..."

# 1. เข้าไปที่โฟลเดอร์โปรเจกต์
cd /home/ubuntu/salepie-admin-api

# 2. ดึงโค้ดล่าสุดจาก Git
git pull origin main

# 3. ติดตั้ง Dependencies ใหม่ (เผื่อมีการเพิ่ม library ใน requirements.txt)
/home/ubuntu/salepie-admin-api/venv/bin/pip install -r requirements.txt

# 4. Restart Systemd Service
sudo systemctl restart salepie.service

echo "Deployment Completed!"