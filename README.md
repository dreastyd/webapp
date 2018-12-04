# simple test web app
# Technology used:

```
Python 3.6
Flask
SQLAlchemy
SQLite
HTML
CSS
Bootstrap
jQUERY+AJAX
```

## Deployment on Ubuntu
##### Recommended system 18.04 on other versions may not work
```
git clone git@github.com:dreastyd/webapp.git
cd webapp
source venv/bin/activate
pip install -r requirements.txt
python3 webapp.py
```
## Deployment using docker
```
#docker setup
sudo snap install docker (sudo apt install docker.io)

#pull docker image
sudo docker pull dreasty/webapp:0.2

#run docker as daemon with port binding
sudo docker run -d -p 5000:5000 dreasty/webapp:0.2
```

## requirements.txt:
```
bcrypt==3.1.4
cffi==1.11.5
Click==7.0
Flask==1.0.2
Flask-Bcrypt==0.7.1
Flask-Login==0.4.1
Flask-SQLAlchemy==2.3.2
Flask-WTF==0.14.2
itsdangerous==1.1.0
Jinja2==2.10
MarkupSafe==1.1.0
Pillow==5.3.0
pycparser==2.19
six==1.11.0
SQLAlchemy==1.2.14
Werkzeug==0.14.1
WTForms==2.2.1
```
