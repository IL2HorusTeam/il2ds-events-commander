IL-2 DS Events Commander
========================

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/IL2HorusTeam/il2ds-events-commander/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

For developers
--------------

Install:

    git
    vagrant (>=1.3)
    virtualbox (>=4.0)
    NFS server
    fabric
    wine (>=1.6) # to develop work on Linux only

If you need to run project on guest FreeBSD or Windows then copy propper
vagrant boxes to `provision/boxes` (see Vagrantfile for names).

Clone the whole project:

    git clone --recursive git@github.com:IL2HorusTeam/il2ds-events-commander.git

**Copy** IL-2 DS directory to `provision/files/il2ds` so that executable file
will be accessible as `provision/files/il2ds/il2server.exe`. You need to do
this to provide access to config and log files from virtual machine directly. Do
not mind if you have no local copy of IL-2 DS: it will be obtained during
provisioning and placed to the directory as mentioned just above.

> **Note**: `confs.ini`, `gc.cmd` and `server.cmd` will be changed during
development. Their content will be taken from `provision/files/conf/l2dsd`.
Place all your custom server commands to `user.cmd` inside server root
directory.

Firstly, start a development virtual machine:

    vagrant up [ubuntu|freebsd|windows]

This will bring for you a clean virtual machine, install all of the necessary
soft and configure it.

If database creation error will appear due to incompatible encoding, run:

    vagrant ssh
    sudo su - postgres
    pg_dropcluster 9.1 main --stop
    pg_createcluster --locale=en_US.UTF-8 --start 9.1 main
    exit
    exit
    vagrant provision

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

Then you can start your dedicated server: on Windows run `il2server.exe` as
usual. On Linux you can run it as:

    wine PATH/TO/PROJECT/provision/files/il2ds/il2server.exe &

To make your work with dedicated server on Linux easier, you can install
[il2dsd](https://github.com/IL2HorusTeam/il2dsd). If so, set path to your
`il2server.exe` in `/etc/il2dsd.conf` and start the service:

    sudo service il2dsd start
