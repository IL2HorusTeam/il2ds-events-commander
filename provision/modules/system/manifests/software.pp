class system::software {
    package {
        [
            "curl",
            "gcc",
            "gettext",
            "make",
            "vim",
            "unzip",
            "wget",
        ]:
        ensure => present,
    }
}
