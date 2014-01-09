class system::apt {
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
