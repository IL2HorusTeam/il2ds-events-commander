define utils::env::setenv($variable, $value, $permanent=false) {
    case $permanent {
        default: {
            setenv($variable, $value)
        }
        true: {
            setenv($variable, $value)

            utils::file::propval_line { "/etc/environment:$variable":
                file => "/etc/environment",
                prop => $variable,
                val  => $value,
            }
        }
    }
}
