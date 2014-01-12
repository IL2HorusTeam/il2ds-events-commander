# Class: uwsgi
#
# uWSGI package, service and config files.
class uwsgi (
    $app_name           = undef,
    $config_name        = undef,
    $config_source      = undef,
    $django_config      = undef,
    $owner              = undef,
    $touch_reload_file  = undef,
    $virtualenv         = undef,
) {

    include supervisor

    $ensure_touch_reload_file = $touch_reload_file ? {
        undef   => absent,
        default => present,
    }

    file { $touch_reload_file:
        ensure => $ensure_touch_reload_file,
    } ->

    python::pip { "uwsgi":
        virtualenv => $virtualenv,
        owner      => $owner,
        ensure     => present,
    } ->

    file { ["/etc/uwsgi",
            "/etc/uwsgi/conf.d"]:
        ensure => directory,
    } ->

    file { "/etc/uwsgi/conf.d/${config_name}":
        ensure => file,
        notify => Supervisor::Service["uwsgi"],
        source => $config_source,
    } ->

    supervisor::service { "uwsgi":
        ensure      => present,
        environment => "DJANGO_SETTINGS_MODULE='${django_config}'",
        command     => "${virtualenv}/bin/uwsgi --ini /etc/uwsgi/conf.d/${config_name}",
        require     => Python::Pip["uwsgi"],
    }
}
