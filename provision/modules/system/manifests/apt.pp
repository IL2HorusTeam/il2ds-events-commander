class system::apt {
    exec { "apt-get update":
        timeout => 0,
    }
}
