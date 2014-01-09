class il2dsd (
    $dst_path  = "/opt/il2ds",
) {
    $src_path = "/vagrant/provision/files/il2ds"
    $cfg_path = "puppet:///files/conf/il2ds"

    # Install packages --------------------------------------------------------
    package { ["wine1.7-i386",
               "il2dsd"]:
        ensure => present,
    } ->

    # Check DS exists ---------------------------------------------------------
    exec { "Check IL-2 DS host":
        command => "il2ds-install -d /tmp -o ${src_path}",
        onlyif  => "test ! -f ${src_path}/il2server.exe",
        timeout => 0,
    } ->
    exec { "Check IL-2 DS guest":
        command => "cp -r ${src_path} ${dst_path}",
        onlyif  => "test ! -f ${dst_path}/il2server.exe",
        timeout => 0,
    } ->

    # Set configuration -------------------------------------------------------
    file { "/etc/il2dsd.conf":
        ensure  => file,
        content => template("il2dsd/il2dsd.conf.erb"),
        notify  => Service["il2dsd"],
    } ->
    file { "${dst_path}/confs.ini":
        ensure => file,
        source => "${cfg_path}/confs.ini",
        notify => Service["il2dsd"],
    } ->
    file { "${dst_path}/gc.cmd":
        ensure => file,
        source => "${cfg_path}/gc.cmd",
        notify => Service["il2dsd"],
    } ->
    file { "${dst_path}/server.cmd":
        ensure => file,
        source => "${cfg_path}/server.cmd",
        notify => Service["il2dsd"],
    } ->

    # Run service -------------------------------------------------------------
    service { "il2dsd":
        ensure => running,
        enable => false,
    }
}
