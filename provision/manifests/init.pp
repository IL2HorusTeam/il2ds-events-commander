# Update system PATH and turn on console output for failures only -------------
Exec {
    path => ["/usr/local/sbin",
             "/usr/local/bin",
             "/usr/sbin",
             "/usr/bin",
             "/sbin",
             "/bin"],
    logoutput => on_failure,
}

# Describe node and stages ----------------------------------------------------

stage { "apt-update": before => Stage["main"] }

class { "aptupdate": stage => "apt-update" }
class {"application":
    project_name => "il2-ds-ec",
    src          => "/vagrant",
    virtualenvs  => "/var/virtualenvs",
    timezone     => "Europe/Kiev",
    user         => "vagrant",
    group        => "www-data",
}

file { "/etc/motd":
    content => "
Welcome to IL-2 DS Events Commander virtual machine maintained by IL-2 Horus Team.

View home page for details: https://github.com/IL2HorusTeam/il2ds-events-commander

"
}

#------------------------------------------------------------------------------

class aptupdate {
    exec { "apt-get update":
        timeout => 0
    } ->
    package { "python-software-properties":
        ensure => latest,
    } ->
    exec { "add-apt-repository ppa:ubuntu-wine/ppa": } ->
    exec { "add-apt-repository ppa:il2horus/ppa": } ->
    exec { "apt-get update again":
        command => "apt-get update",
        timeout => 0,
    }
}

class application (
    $project_name,
    $src,
    $virtualenvs,
    $timezone,
    $user,
    $group,
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
    class { "software": } ->
    class { "timezone":
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

    # Update user's .bashrc ---------------------------------------------------
    utils::file::line { "bashrc-workon-venv":
        file => "/home/$user/.bashrc",
        line => "source $virtualenv/bin/activate",
    } ->
    utils::file::line { "bashrc-cd-venv":
        file => "/home/$user/.bashrc",
        line => "cd $project_base",
    }
}

class software {
    package { "gcc":
        ensure => present,
    }
    package { "gettext":
        ensure => present,
    }
    package { "make":
        ensure => present,
    }
    package { "wget":
        ensure => present,
    }
    package { "curl":
        ensure => present,
    }
    package { "vim":
        ensure => present,
    }
}

class timezone (
    $tz,
){
    package { "tzdata":
        ensure => latest,
    }
    file { "/etc/localtime":
        require => Package["tzdata"],
        source  => "file:///usr/share/zoneinfo/${tz}",
    }
}
