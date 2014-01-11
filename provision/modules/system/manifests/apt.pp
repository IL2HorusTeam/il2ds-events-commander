class system::apt {
    # exec { "apt-get update":
    #     timeout => 0,
    # }
    #->
    # package { "python-software-properties":
    #     ensure => present,
    # } ->
    # # Add repo for python-pip 1.4.1-2 and python-virtualenv 1.10.1-1
    # exec { "apt-add-repository 'deb http://archive.ubuntu.com/ubuntu saucy universe'": } ->
    # exec { "apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32": } ->
    # exec { "apt-get update again":
    #     command => "apt-get update",
    #     timeout => 0,
    # }
}
