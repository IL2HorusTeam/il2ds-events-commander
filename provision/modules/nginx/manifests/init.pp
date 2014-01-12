# Class: nginx
#
# Nginx package, service and config files
class nginx(
    $app_name,
    $config_name,
    $config_source,
    $credentials = undef,
    $user        = "nginx",
    $login       = undef,
    $password    = undef
    ) {

    if $login != undef and $password != undef {
        file { "/etc/nginx/htpasswd":
            ensure  => file,
            content => "$login:$password",
            notify  => Service['nginx'],
            require => Package['nginx'],
        }
    }

    package { "nginx":
        ensure => installed,
    } ->

    file { "/etc/nginx/certificate.pem":
        ensure => file,
        source => "${credentials}.pem",
    } ->

    file { "/etc/nginx/certificate.crt":
        ensure => file,
        source => "${credentials}.crt",
    } ->

    file { "/etc/nginx/nginx.conf":
        ensure  => present,
        content => template("nginx/nginx.conf.erb"),
    } ->

    file { "/etc/nginx/conf.d/default.conf":
        ensure => absent,
        notify => Service["nginx"],
    } ->

    file { "/etc/nginx/conf.d/$config_name":
        ensure => file,
        source => $config_source,
        notify => Service["nginx"],
    } ->

    service { "nginx":
        enable => true,
        ensure => running,
        hasstatus => true,
    }

}
