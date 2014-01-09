class system::timezone (
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
