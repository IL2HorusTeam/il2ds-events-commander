IL-2 DS Events Commander
========================

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/IL2HorusTeam/il2ds-events-commander/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

For developers
--------------

### Development process overview

Development of this project is a fully isolated process. All services and
servers (except game server) are running on a VirtualBox guest machine. It is
managed by [Vagrant](http://www.vagrantup.com/) and provisioned by
[Puppet](http://puppetlabs.com/puppet/what-is-puppet). You do not need to dive
into the abyss of knowledge about how these things are working. If you are not
familiar with DevOps, just let the magic happen to you: run few commands and
look how the entire system borns and gets configured automatically. You can
access the guest machine via SSH or use [Fabric](http://docs.fabfile.org/en/1.8/)
to run some commands.

During provisioning you will get installed and configured Postgres 9.1, PostGIS 1.5,
Redis, Nginx+uWSGI, isolated Python environment (by [virtualenv](http://www.virtualenv.org/en/latest/)),
configured project and other stuff. Due to certain problems with running
IL-2 Dedicated Server on VirtualBox under Wine, IL-2 DS must be located on the
host machine.

The approach, described above, provides identical development environment for
every developer. This environment is close to the real production server
environment, so minimal amount of deployment issues is expected.

To start development on this project, you will need:

1. Install needed software.
2. Clone git repository.
3. Setup security settings.
4. Get IL-2 DS somewhere and place it to project's directory. In case
you've got no one, maybe this [full and clean 4.12.2](https://drive.google.com/file/d/0B4hbTGD5PQqQOUtBVTJqWEFhaU0/edit?usp=sharing) will help you (Its size is ~2 GB, so take some patience).
Or you can leave this task up to automatic provisioning stage.
5. Start VM and automatically provision all needed stuff. This will start
the web application.
6. Update 'hosts' file.
7. Start IL-2 DS.
8. Run commander.

### Install tools

1. git
2. vagrant (>=1.3)
3. virtualbox (>=4.0)
4. NFS server
5. fabric
6. wine (>=1.6) # to develop work on Linux only

If you need to run project on guest FreeBSD or Windows then copy propper
vagrant boxes to `provision/boxes` (see Vagrantfile for names).

### Get sourses

Clone the whole project:

    git clone --recursive git@github.com:IL2HorusTeam/il2ds-events-commander.git

### Setup security settings

You will need to use an existsing development email for different purposes:
sending email confirmation requests, password resetting requests, etc. To make
this possible, you need to copy `il2ec/settings/local/security.py.example`
into `il2ec/settings/local/security.py` and set valid value for
`EMAIL_HOST_PASSWORD`. Contact developers to get the real passsword value.

### Get IL-2 DS

**Copy** IL-2 DS directory to `provision/files/il2ds` so that executable file
will be accessible as `provision/files/il2ds/il2server.exe`. You need to do
this to provide access to config and log files from virtual machine directly. Do
not mind if you have no local copy of IL-2 DS: it will be obtained during
provisioning and placed to the directory as mentioned just above.

> **Note**: `confs.ini`, `gc.cmd` and `server.cmd` will be changed during
development. Their content will be taken from `provision/files/conf/l2dsd`.
Place all your custom server commands to `user.cmd` inside server root
directory.

### Start VM and let some magic happen

Firstly, start a development virtual machine:

    vagrant up [ubuntu|freebsd|windows]

This will bring for you a clean virtual machine, install all of the necessary
software and configure it.

If database creation error will appear due to incompatible encoding, run:

    vagrant ssh
    sudo su - postgres
    pg_dropcluster 9.1 main --stop
    pg_createcluster --locale=en_US.UTF-8 --start 9.1 main
    exit
    exit
    vagrant provision

Now you can prepare and run the web application:

    fab incarnate

This will create database and run several services, so the web application will
be accessible at

    http://localhost:8010

### Update 'hosts'

To make your IL-2 server accessible from the outer world, you need to set
a `localHost` parameter in server's config file. This parameter specifies an IP
address of the network interface the server will be running on. Due to bugs
occurring on Wine running on VirtualBox, it was decided to place IL-2 server
outside the virtual machine. Hence, the value of `localHost` may vary for every
developer while it must be stored in repository and remain the same. To resolve
this problem it was decided to store the name of server's interface as
`il2ds-host`. It's value must be specified on developer's machine and on the
virtual machine. To do that you need to edit `hosts` file on both of them.
To define `il2ds-host` on Windows host machine, add the next string to your
`C:\Windows\System32\Drivers\etc\hosts`:

    XXX.XXX.XXX.XXX    il2ds-host

where `XXX.XXX.XXX.XXX` is the IP address of target network interface.
For the Linux host machine run:

    sudo bash -c 'echo "XXX.XXX.XXX.XXX    il2ds-host" >> /etc/hosts'

Run this command on the guest machine also (for any host machine):

    vagrant ssh
    sudo bash -c 'echo "XXX.XXX.XXX.XXX    il2ds-host" >> /etc/hosts'
    exit

### Run game server

Then you can start your dedicated server: on Windows run `il2server.exe` as
usual. On Linux you can run it as:

    wine PATH/TO/PROJECT/provision/files/il2ds/il2server.exe &

To make your work with dedicated server on Linux easier, you can install
[il2dsd](https://github.com/IL2HorusTeam/il2dsd). If so, set path to your
`il2server.exe` in `/etc/il2dsd.conf` and start the service:

    sudo service il2dsd start

### Run commander

Execute next command to run commander as daemon:

    fab commander:run
