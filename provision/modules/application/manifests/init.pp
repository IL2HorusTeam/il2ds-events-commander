class application (
    $project_name,
    $src,
    $virtualenvs,
    $timezone,
    $user,
    $group,
    $motd = undef,
){
    $virtualenv = "$virtualenvs/$project_name"
    $project_base = "$virtualenv/src/$project_name"

    # Ensure given user and group exist ---------------------------------------
    group { "$group":
        ensure => present,
    } ->
    user { "$user":
        home => "/home/$user",
        ensure => present,
        groups => "$group",
        membership => minimum,
    } ->

    # Update system -----------------------------------------------------------
    class { "system::software": } ->
    class { "system::timezone":
        tz => $timezone,
    } ->

    # Prepare Python virtual environment --------------------------------------
    file { "$virtualenvs":
        ensure => directory,
        mode => 755,
        owner => $user,
        group => $group,
    } ->
    class { "python":
        version    => "system",
        dev        => true,
        virtualenv => true,
    } ->
    python::virtualenv { "$virtualenv":
        ensure       => present,
        version      => "system",
        requirements => "$src/requirements.pip",
        systempkgs   => true,
        owner        => $user,
        group        => $group,
    } ->
    python::pip { "bpython":
        ensure       => present,
        virtualenv   => "$virtualenv",
        owner        => $user,
    } ->

    # Prepare project's structure ---------------------------------------------
    file { ["$virtualenv/var",
            "$virtualenv/var/static",
            "$virtualenv/var/uploads",
            "$virtualenv/var/log",
            "$virtualenv/src", ]:
        ensure => directory,
        mode => 770,
        owner => $user,
        group => $group,
    } ->
    file { "$virtualenv/src/$project_name":
        ensure => link,
        path => $project_base,
        target => $src,
        mode => 770,
        owner => $user,
        group => $group,
    } ->
    file { "$virtualenv/var/log/$project_name.log":
        ensure => file,
        mode => 660,
        owner => $user,
        group => $group,
    } ->

    # Install dedicated server ------------------------------------------------
    class { "il2dsd": } ->

    # Update user's .bashrc ---------------------------------------------------
    utils::file::line { "bashrc-workon-venv":
        file => "/home/$user/.bashrc",
        line => "source $virtualenv/bin/activate",
    } ->
    utils::file::line { "bashrc-cd-venv":
        file => "/home/$user/.bashrc",
        line => "cd $project_base",
    }

    # Update message of the day -----------------------------------------------
    if motd {
        file { "/etc/motd":
            content => $motd,
        }
    }
}
