class il2dsd (
) {
    $src_path = "/vagrant/provision/files/il2ds"
    $cfg_path = "puppet:///files/conf/il2ds"

    # Check DS exists ---------------------------------------------------------
    exec { "Check IL-2 DS host":
        command => "bash <( curl https://raw2.github.com/IL2HorusTeam/il2dsd/master/scripts/il2ds-install ) -d /tmp -o ${src_path}",
        onlyif  => "test ! -f ${src_path}/il2server.exe",
        timeout => 0,
    }

    # Set configuration -------------------------------------------------------
    file { "${src_path}/confs.ini":
        ensure => file,
        source => "${cfg_path}/confs.ini",
    }
    file { "${src_path}/gc.cmd":
        ensure => file,
        source => "${cfg_path}/gc.cmd",
    }
    file { "${src_path}/server.cmd":
        ensure => file,
        source => "${cfg_path}/server.cmd",
    }
    file { "${src_path}/user.cmd":
        ensure  => "present",
        replace => "no",
    }
}
