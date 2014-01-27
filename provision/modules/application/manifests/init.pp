class application (
    $project_name,
    $src,
    $virtualenvs,
    $timezone,
    $user,
    $group,
    $motd = undef,
){
    $virtualenv    = "${virtualenvs}/${project_name}"
    $project_base  = "${virtualenv}/src/${project_name}"
    $django_config = "${project_name}.settings.local"
    $uwsgi_config  = "${project_name}-local.ini"
    $nginx_config  = "${project_name}-local.conf"
    $nginx_certs   = "certificate-local"

    # Ensure given user and group exist ---------------------------------------
    group { $group:
        ensure => present,
    } ->
    user { $user:
        home       => "/home/${user}",
        ensure     => present,
        groups     => $group,
        membership => minimum,
    } ->

    # Update system -----------------------------------------------------------
    class { "system::software": } ->
    class { "system::timezone":
        tz => $timezone,
    } ->

    # Prepare Python virtual environment --------------------------------------
    file { $virtualenvs:
        ensure => directory,
        mode   => 755,
        owner  => $user,
        group  => $group,
    } ->
    class { "python":
        version    => "system",
        pip        => true,
        dev        => true,
        virtualenv => true,
    } ->
    python::virtualenv { $virtualenv:
        ensure     => present,
        version    => "system",
        systempkgs => true,
        owner      => $user,
        group      => $group,
    } ->

    # Set Django settings variable --------------------------------------------
    utils::env::setenv { "DJANGO_SETTINGS_MODULE":
        variable  => "DJANGO_SETTINGS_MODULE",
        value     => $django_config,
        permanent => true,
    } ->

    # Prepare project's structure ---------------------------------------------
    file { ["${virtualenv}/var",
            "${virtualenv}/var/static",
            "${virtualenv}/var/uploads",
            "${virtualenv}/var/log",
            "${virtualenv}/src", ]:
        ensure => directory,
        mode   => 770,
        owner  => $user,
        group  => $group,
    } ->
    file { "${virtualenv}/src/${project_name}":
        ensure => link,
        path   => $project_base,
        target => $src,
        mode   => 770,
        owner  => $user,
        group  => $group,
    } ->
    file { ["${virtualenv}/var/log/${project_name}-web.log",
            "${virtualenv}/var/log/${project_name}-daemon.log"]:
        ensure => file,
        mode   => 660,
        owner  => $user,
        group  => $group,
    } ->

    # Install IL-2 DS ---------------------------------------------------------
    class { "il2ds": } ->

    # Install databases -------------------------------------------------------
    class { "redis": } ->

    class { "postgresql::server":
        postgres_password => "qwerty",
        version           => "9.1",
        encoding          => "UTF8",
        locale            => "en_US.UTF-8",
    } ->
    package { "postgresql-server-dev-9.1": } ->
    class { "postgis":
        version => "9.1",
    } ->
    postgresql::server::role { $user:
        password_hash => postgresql_password($user, "qwerty"),
        createdb      => true,
    } ->
    postgresql::server::db { $project_name:
        user     => $user,
        owner    => $user,
        password => "qwerty",
        encoding => "UTF8",
        locale   => "en_US.UTF-8",
        template => "template_postgis",
    } ->

    # Prepare web server ------------------------------------------------------
    class { "uwsgi":
        app_name          => $project_name,
        config_name       => "${project_name}.ini",
        config_source     => "puppet:///files/conf/uwsgi/${uwsgi_config}",
        django_config     => $django_config,
        virtualenv        => $virtualenv,
        owner             => $user,
        touch_reload_file => "/tmp/uwsgi-touch-reload-${project_name}",
    } ->
    class { "nginx":
        app_name      => $project_name,
        config_name   => "${project_name}.conf",
        config_source => "puppet:///files/conf/nginx/${nginx_config}",
        credentials   => "puppet:///files/conf/nginx/${nginx_certs}",
        user          => $user,
    } ->

    # Update project's dependencies -------------------------------------------
    python::requirements { "${src}/requirements.pip":
        virtualenv => $virtualenv,
        owner      => $user,
        group      => $group,
    } ->

    # Celery ------------------------------------------------------------------
    class { "celery":
        django_config  => $django_config,
        dj_manage_path => $project_base,
        virtualenv     => $virtualenv,
        owner          => $user,
        group          => $group,
    } ->

    # Update user's .bashrc ---------------------------------------------------
    utils::file::line { "bashrc-workon-venv":
        file => "/home/${user}/.bashrc",
        line => "source ${virtualenv}/bin/activate",
    }
    utils::file::line { "bashrc-cd-venv":
        file => "/home/${user}/.bashrc",
        line => "cd ${project_base}",
    }

    # Update .bash_profile ----------------------------------------------------
    file { "/home/${user}/.bash_profile":
        ensure => file,
        mode   => 644,
        owner  => $user,
        group  => $group,
    } ->
    utils::file::line { "bash-profile-source-bashrc":
        file => "/home/${user}/.bash_profile",
        line => "source /home/${user}/.bashrc",
    }

    # Update message of the day -----------------------------------------------
    if motd {
        file { "/etc/motd":
            content => $motd,
        }
    }
}
