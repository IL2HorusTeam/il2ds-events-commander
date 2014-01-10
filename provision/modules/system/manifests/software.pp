class system::software {
    package {
        [
            "curl",
            "gcc",
            "gettext",
            "make",
            "vim",
            "unzip",
        ]:
        ensure => present,
    }
}
