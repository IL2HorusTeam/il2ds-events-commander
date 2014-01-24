class celery (
    $django_config  = undef,
    $dj_manage_path = undef,
    $virtualenv     = undef,
    $owner          = undef,
    $group          = undef,
) {
    $python_path = "${virtualenv}/bin"

    file { ["/var/log/celery",
            "/var/run/celery"]:
        ensure => "directory",
        owner  => $owner,
        group  => $group,
    }

    file { "/etc/default/celeryd":
        ensure  => "present",
        content => template("celery/celeryd-defaults"),
        mode    => 0644,
    }

    file { "/etc/init.d/celeryd":
        ensure  => "present",
        content => template("celery/celeryd"),
        mode    => 0755,
    }

    file { "/etc/init.d/celerybeat":
        ensure  => "present",
        content => template("celery/celerybeat"),
        mode    => 0755,
    }

    python::pip { "celery":
        virtualenv => $virtualenv,
        owner      => $owner,
        ensure     => present,
    } ->
    service { ["celeryd",
               "celerybeat"]:
        ensure => running,
        require => [
            File["/etc/default/celeryd"],
            File["/etc/init.d/celeryd"],
            File["/etc/init.d/celerybeat"],
            File["/var/log/celery"],
            File["/var/run/celery"],
        ],
    }
}
