# Activate virtual environment
python3 -m venv venv
source venv/bin/activate  # สำหรับ Linux/MacOS
venv\Scripts\activate     # สำหรับ Windows

# Establish secure shell tunnel 
# Port forward 

ssh -i C:\Users\ASUS\.ssh\Jupiter.pem -N -L 27019:127.0.0.1:27017 ubuntu@188.166.188.153 


# ล้างค่า git ที่ server ที่ทำงานค้างไว้
cd /home/ubuntu/salepie-admin-api
git fetch --all
git reset --hard origin/main


# Merge dev to main branch
