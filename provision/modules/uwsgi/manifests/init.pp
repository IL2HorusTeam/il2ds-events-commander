# Class: uwsgi
#
# uWSGI package, service and config files.
class uwsgi (
    $app_name           = undef,
    $config_name        = undef,
    $config_source      = undef,
    $django_config      = undef,
    $touch_reload_file  = undef,
    $path               = "/usr/bin"
) {

    include supervisor

    $ensure_touch_reload_file = $touch_reload_file ? {
        undef   => absent,
        default => present,
    }

    file { $touch_reload_file:
        ensure => $ensure_touch_reload_file,
    } ->

    package { "uwsgi":
      ensure   => present,
      provider => pip,
      require  => [ Package["python-dev"], Package["python-pip"] ],
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
        command     => "${path}/uwsgi --ini /etc/uwsgi/conf.d/${config_name}",
    }
}
