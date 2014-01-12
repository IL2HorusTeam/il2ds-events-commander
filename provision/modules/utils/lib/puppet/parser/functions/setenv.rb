module Puppet::Parser::Functions
  newfunction(:setenv) do |args|
    variable = args[0]
    value = args[1]
    ENV[variable] = value
  end
end