# rpm-go-graphite
my rpm spec files for [go-graphite](https://github.com/go-graphite/)

# Description
These spec files are based on [packagecloud.io/go-graphite/stable](https://packagecloud.io/go-graphite/stable).
I created spec files with the goal to build rpms with only the spec file and sources from git repos.  
Build and tested for/with [Red Hat Enterprise Linux Server](https://www.redhat.com/en/technologies/linux-platforms/enterprise-linux/server) 9
or clones like [AlmaLinux](https://almalinux.org/), [Rocky Linux](https://rockylinux.org/).  

# Build rpms
You can build rpms from just the spec file with `spectool -gf -R <spec>` and `rpmbuild -bb <spec>`.
But you need to create the `vendor.tar.gz` as it is described in the spec file for `SOURCE2`.
