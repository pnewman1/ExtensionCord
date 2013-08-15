# What is Extension Cord?

Extension Cord is a web application for managing test cases and planning QA work. It is aimed at the software QA community.

For more take a look at the Extension Cord wiki: https://github.com/DeemOpen/ExtensionCord/wiki

# How is it implemented?

Python/Django/Javascript/jQuery/Mysql

# Installation

The following steps are to run a development instance on Ubuntu:

* Install dependencies:

```bash
sudo apt-get install mysql-server mysql-common mysql-client git-core python-dev python-pip python-setuptools libmysqlclient-dev libldap2-dev libsasl2-dev
```

* If /var/www doesn't exist: `mkdir /var/www`
* `git clone https://github.com/DeemOpen/ExtensionCord.git /var/www/extension_cord`
* `cd /var/www/extension_cord`
* Create the extension_cord user and db using: `mysql -p < make_initial_db.sql`
* `sudo pip install -r requirements.txt` (Note if you're using a virtualenv don't use sudo)
* Populate the database. From the project's root directory, run `./manage.py syncdb` followed by `./manage.py migrate`
* Update your `extension_cord/settings.py` to include your bug tracker URL (currently only Jira is supported), or
  add it to `extension_cord/local_settings.py`
* Optional: If you want to use with LDAP create an `extension_cord/ldap_groups/settings.py` based on `extension_cord/ldap_groups/local_settings.py.template`
* To collect static data run `./manage.py collectstatic`
* Run `./manage.py runserver` to test locally

To run a live version on Apache (again these steps are for Ubuntu):

* Complete all the steps listed above in the development section
* Install wsgi: `sudo apt-get install apache2 libapache2-mod-wsgi`
* move apache_files/extension_cord into your sites-available, and symlink it into sites-enabled. Example: 

```bash
  sudo cp apache_files/extension_cord /etc/apache2/sites-available/ (you can alternatively symlink it here)
  sudo rm -f /etc/apache2/sites-enabled/000-default
  a2ensite extension_cord
  sudo /etc/init.d/apache2 reload
```

* Restart apache: `sudo apache2 graceful`
* You're all set to go!

# License & Contribution

Extension Cord is released under the Apache 2.0 license.

Comments, bugs, pull requests, and other contributions are all welcomed!

For questions please feel free to contact pnewman@deem.com
