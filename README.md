IL-2 DS Events Commander
========================

For developers
--------------

Install:

    vagrant (>=1.3)
    virtualbox (>=4.0)
    NFS server
    fabric
    wine (>=1.6) # for work on linux only

If you need to run project on guest FreeBSD or Windows then copy propper
vagrant boxes to `provision/boxes` (see Vagrantfile for names).

**Copy** IL-2 DS directory to `provision/files/il2ds` so that executable file
will be accessible as `provision/files/il2ds/il2server.exe`. This directory
will serve as a source of dedicated server. Do not mind if you have no local
copy of IL-2 DS: it will be obtained during provisioning and placed to the
directory as mentioned just above.

> **Note**: `confs.ini`, `gc.cmd` and `server.cmd` will be changed in
development mode. Their values will be taken from `provision/files/conf/l2dsd`.
Place all your custom server commands to `user.cmd` inside server root
directory.

Add `il2ds-host` with address of your network adapter to your `hosts`, e.g.:

    192.168.1.3     il2ds-host

To make thing work, first run:

    vagrant up [ubuntu|freebsd|windows]

Then you can start your dedicated server: on Windows run `il2server.exe` as
usual. On Linux you can run it as:

    wine PATH/TO/PROJECT/provision/files/il2ds/il2server.exe &

To make you work with dedicated server on Linux easier, you can install
[il2dsd](https://github.com/IL2HorusTeam/il2dsd). If so, set path to
`il2server.exe` in `/etc/il2dsd.conf` and start the service:

    sudo service il2dsd start
