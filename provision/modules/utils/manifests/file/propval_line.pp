define utils::file::propval_line($file, $prop, $val, $ensure=present) {
    $line = "$prop=$val"
    case $ensure {
        default: { err ( "unknown ensure value ${ensure}" ) }
        present: {
            exec { "/bin/sed -i 's/${prop}=.*/${prop}=${val}/g' ${file}":
                onlyif => "/bin/grep -qFvx '${line}' '${file}' && /bin/grep -qF '${prop}=' '${file}'"
            } ->
            exec { "/bin/echo '${line}' >> '${file}'":
                unless => "/bin/grep -qFx '${line}' '${file}'"
            }
        }
        absent: {
            exec { "/bin/grep -vFx '${line}' '${file}' | /usr/bin/tee '${file}' > /dev/null 2>&1":
              onlyif => "/bin/grep -qFx '${line}' '${file}'"
            }
        }
    }
}
