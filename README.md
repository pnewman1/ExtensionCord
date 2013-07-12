# What is Extension Cord?

Extenion Cord is a web application for managing test cases and planning QA work. It is aimed at the software QA community.

# How is it implemented?

Python/Django/Javascript/jQuery/Mysql

# Installation
* `sudo apt-get install mysql-server mysql-common mysql-client git-core python-pip python-setuptools`
* For prod also run `sudo apt-get install apache2 libapache2-mod-wsgi`
* `mysql < make_initial_db.sql`
* `pip install -r requirements.txt`
* Update your extension_cord/settings.py to include your bug tracker URL, or
  add it to extension_cord/local_settings.py
* Create an extension_cord/ldap_groups/settings.py based on
  extension_cord/ldap_groups/local_settings.py.template
* To collect static data run `./manage.py collectstatic`
* Run `./manage.py runserver` to test locally
* To use in conjuction with apache, move apache_files/extension_cord into your
  sites-available, and symlink it into sites-enabled. Example:
   `sudo cp apache_files/extension_cord /etc/apache2/sites-available/ (you can alternatively symlink it here)
    sudo rm -f /etc/apache2/sites-enabled/000-default
    a2ensite extension_cord
    sudo /etc/init.d/apache2 restart`
* Restart apache: `sudo apache2 graceful`
* You're all set to go!

# Extension Cord is released under the Apache 2.0 license
