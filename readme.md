## install mysql client

Có 2 cách

1. Nếu cách pip install mysqlclient ko dc thì dùng cách 2

2. Dùng cái này pip install mysql-connector-python

nếu dùng cái này thì cần phải chỉnh trong setting như sau để kết nối db
DATABASES = {
'default': {
'ENGINE': 'mysql.connector.django',
'NAME': 'auto-video',
'USER': 'root',
'PASSWORD': 'root',
'HOST': 'localhost',
'PORT': '3306',
}
}

## Start project

Trước tiên là phải start cái môi trường ảo cho python trước

source ../auto-video-env/bin/activate

Sau khi start xong môi trường thì start server

python manage.py runserver

Sau khi run migrate
python manage.py migrate

sort start server: ./start.sh

### Tạo admin user

python manage.py createsuperuser

Sau khi run lệnh trên và thực hiện theo các bước xong thì sẽ có dc user admin
