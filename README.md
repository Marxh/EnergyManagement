# 1. Start a project

`django-admin startproject mysite`

1. The outer mysite/ root directory is just a container for your project. Its name doesn’t matter to Django; you can rename it to anything you like.
manage.py: A command-line utility that lets you interact with this Django project in various ways. You can read all the details about manage.py in django-admin and manage.py.
2. The inner mysite/ directory is the actual Python package for your project. Its name is the Python package name you’ll need to use to import anything inside it (e.g. mysite.urls).
3. mysite/__init__.py: An empty file that tells Python that this directory should be considered a Python package. If you’re a Python beginner, read more about packages in the official Python docs.
4. mysite/settings.py: Settings/configuration for this Django project. Django settings will tell you all about how settings work.
mysite/urls.py: The URL declarations for this Django project; a “table of contents” of your Django-powered site. You can read more about URLs in URL dispatcher.
5. mysite/wsgi.py: An entry-point for WSGI-compatible web servers to serve your project. See How to deploy with WSGI for more details.

# 2. Start an app

`python manage.py startapp polls`

# 3. Database
##3.1 Database Connection
修改`settings.py`配置数据库

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'EnergyManufacture',   #数据库名字
        'HOST':'127.0.0.1',  #空的默认为localhost
        'USER':'root',    #mysql用户名
        'PASSWORD':'Pa22word',    #mysql密码
        'PORT':'3306',
    }
}
```

在`init.py`添加

```
import pymysql

pymysql.install_as_MySQLdb()
```

从而使得连接mysql数据库

`python manage.py migrate`

创建原始数据库

##3.2 Model

1. 在app中定义模型；
2. 修改settings.py

	eg:
	
	```
	INSTALLED_APPS = [
	    'LineDetection.apps.LinedetectionConfig',
	    'django.contrib.admin',
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.messages',
	    'django.contrib.staticfiles',
	]
	```
3. 数据库迁移：

	`python manage.py makemigrations LineDetection`
	
	By running makemigrations, you’re telling Django that you’ve made some changes to your models (in this case, you’ve made new ones) and that you’d like the changes to be stored as a migration.
	
	看0001_init.py文件对应的sql：
	
	`python manage.py sqlmigrate LineDetection 0001`
	
	There’s a command that will run the migrations for you and manage your database schema automatically - that’s called migrate.
	
	
	`python manage.py migrate`