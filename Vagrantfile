# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    #---------------------------------------------------------------------------
    # Ubuntu Precise 32 bit VM
    #---------------------------------------------------------------------------

    config.vm.define "ubuntu" do |ubuntu|
        ubuntu.vm.hostname = "il2ec-precise"
        ubuntu.vm.box = "precise32"
        ubuntu.vm.box_url = "http://files.vagrantup.com/precise32.box"

        ubuntu.vm.network :private_network, ip: "10.11.12.13"
        ubuntu.vm.network :forwarded_port,
            guest: 22,
            host: 2210,
            id: "ssh",
            auto_correct: true
        ubuntu.vm.network :forwarded_port,
            guest: 80,
            host: 8010,
            id: "web"

        ubuntu.vm.synced_folder "provision/files", "/etc/provision/files",
            :nfs => true
        ubuntu.vm.synced_folder ".", "/vagrant",
            id: "vagrant-root",
            :nfs => true

        ubuntu.vm.provision :puppet do |puppet|
            puppet.manifests_path = "provision/manifests"
            puppet.module_path = "provision/modules"
            puppet.manifest_file = "init.pp"
            puppet.options = "-l console --verbose --trace --fileserverconfig=/vagrant/provision/fileserver.conf"
            puppet.nfs = false
        end
    end

    # #---------------------------------------------------------------------------
    # # FreeBSD 9.2 64 bit VM
    # #---------------------------------------------------------------------------

    # config.vm.define "freebsd" do |freebsd|
    #     freebsd.vm.guest = :freebsd
    #     freebsd.vm.hostname = "il2ec-freebsd"
    #     freebsd.vm.box = "freebsd64"
    #     freebsd.vm.box_url = "https://dl.dropboxusercontent.com/u/76022516/vagrant/freebsd92-64.box"

    #     freebsd.vm.network :private_network, ip: "10.11.12.23"
    #     freebsd.vm.network :forwarded_port,
    #         guest: 22,
    #         host: 2220,
    #         id: "ssh",
    #         auto_correct: true
    #     freebsd.vm.network :forwarded_port,
    #         guest: 80,
    #         host: 8020,
    #         id: "web"

    #     freebsd.vm.synced_folder "provision/files", "/etc/provision/files",
    #         :nfs => true
    #     freebsd.vm.synced_folder ".", "/vagrant",
    #         id: "vagrant-root",
    #         :nfs => true

    #     freebsd.vm.provision :puppet do |puppet|
    #         puppet.manifests_path = "provision/manifests"
    #         puppet.module_path = "provision/modules"
    #         puppet.manifest_file = "init.pp"
    #         puppet.options = "-l console --verbose --trace --fileserverconfig=/vagrant/provision/fileserver.conf"
    #         puppet.nfs = true
    #     end
    # end

    # #---------------------------------------------------------------------------
    # # Windows Server 2008 64 bit VM
    # #---------------------------------------------------------------------------

    # config.vm.define "windows" do |windows|
    #     windows.vm.hostname = "il2ec-win2008"
    #     windows.vm.box = "win2008r2x64"
    #     windows.vm.box_url = "provision/boxes/win2008r2x64.box"

    #     windows.winrm.username = "vagrant"
    #     windows.winrm.password = "vagrant"

    #     windows.vm.guest = :windows
    #     windows.vm.boot_timeout = 500
    #     windows.windows.halt_timeout = 25

    #     windows.vm.network :private_network, ip: "10.11.12.33"
    #     windows.vm.network :forwarded_port,
    #         guest: 22,
    #         host: 2230,
    #         id: "ssh",
    #         auto_correct: true
    #     windows.vm.network :forwarded_port,
    #         guest: 80,
    #         host: 8030,
    #         id: "web"
    #     windows.vm.network :forwarded_port,
    #         guest: 5985,
    #         host: 5985,
    #         id: "WinRM"

    #     windows.vm.synced_folder "provision/files", "/etc/provision/files",
    #         :nfs => false
    #     windows.vm.synced_folder ".", "/vagrant",
    #         id: "vagrant-root",
    #         :nfs => false

    #     windows.vm.provider :virtualbox do |vb|
    #         vb.gui = true
    #     end

    #     windows.vm.provision :puppet do |puppet|
    #         puppet.manifests_path = "provision/manifests"
    #         puppet.module_path = "provision/modules"
    #         puppet.manifest_file = "init.pp"
    #         puppet.options = "-l console --verbose --trace --fileserverconfig=/vagrant/provision/fileserver.conf"
    #         puppet.nfs = false
    #     end
    # end

    config.vm.provider "virtualbox" do |vb|
        vb.customize ["modifyvm", :id, "--memory", 700]
    end

end
