class system::software {
    package { "gcc":
        ensure => present,
    }
    package { "gettext":
        ensure => present,
    }
    package { "make":
        ensure => present,
    }
    package { "curl":
        ensure => present,
    }
    package { "vim":
        ensure => present,
    }
}
