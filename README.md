IL-2 DS Events Commander
========================

For developers
--------------

Install:

    vagrant (>=1.3)
    virtualbox (>=4.0)
    NFS server
    fabric

Copy propper vagrant boxes to `provision/boxes` to run project on FreeBSD or
Windows virtual machine.

Copy or link IL-2 DS directory to `provision/files/il2ds` so that executable
file will be accessible as `provision/files/il2ds/il2server.exe`. This
directory will serve as a source of dedicated server and no changes will be
done inside it. Do not mind if you have no local copy of IL-2 DS: it will be
obtained during provisioning and placed to the directory as mentioned just
above.

Run:

    vagrant up [ubuntu|freebsd|windows]
