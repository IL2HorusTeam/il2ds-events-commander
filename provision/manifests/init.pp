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

class { "system::apt": stage => "apt-update" }
class {"application":
    project_name  => "il2ec",
    src           => "/vagrant",
    virtualenvs   => "/var/virtualenvs",
    timezone      => "Europe/Kiev",
    user          => "vagrant",
    group         => "www-data",
    motd          => "
Welcome to IL-2 DS Events Commander virtual machine maintained by IL-2 Horus Team.

View home page for details: https://github.com/IL2HorusTeam/il2ds-events-commander

"
}
