class system::software {
    package {
        [
            "curl",
            "gcc",
            "gettext",
            "git",
            "make",
            "vim",
            "unzip",
            "wget",
        ]:
        ensure => present,
    }
}
