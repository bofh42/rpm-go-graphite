# spec file for package go-carbon

%define debug_package %{nil}

Name:           go-carbon
Version:        0.17.3
Release:        1%{?dist}
Summary:        Golang implementation of Graphite/Carbon server
License:        MIT
Group:          bofh42/addon/go-graphite
Url:            https://github.com/go-graphite/go-carbon

# spectool -fg -S -R go-carbon.spec to download source
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz
# this needs to be updated for every version change
%global src0sum d4e1b884524e96637e063af179df745e

# for create new vendor tar.gz unpack source and cd into it
# sudo rm -rf ~/.cache/go* ~/go ; go mod vendor && tar -cvzf ../go-carbon-$(pwd | awk -F- '{ print $NF}')-vendor.tar.gz vendor
Source2:        %{name}-%{version}-vendor.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-build


BuildRequires:  xxhash
BuildRequires:  golang >= 1.21.13, compiler(go-compiler)

%{?systemd_requires}
Requires(pre):  %{_sbindir}/useradd
Requires(pre):  %{_bindir}/id

%description
Golang implementation of Graphite/Carbon server
with classic architecture: Agent -> Cache -> Persister

%prep
echo "%{src0sum}  %{SOURCE0}" | xxh128sum -c

%setup -q -n %{name}-%{version}
%setup -q -T -D -a 2 -n %{name}-%{version}

%build
# use local vendor source
export GO111MODULE=on
export GOFLAGS=-mod=vendor

go build -v -o %{name}

# our tmpfiles
echo "D /run/%{name} 0775 carbon carbon -" >deploy/%{name}.tmpfiles
# change pid location
sed -i -e 's|pidfile /var/run/%{name}.pid|pidfile /run/%{name}/%{name}.pid|' deploy/%{name}.service

%check
# use local vendor source
export GO111MODULE=on
export GOFLAGS=-mod=vendor

go test -v

%install
%{__rm} -rf %{buildroot}
%{__install} -d -m0755 \
    %{buildroot}%{_sysconfdir}/%{name} \
    %{buildroot}%{_sysconfdir}/logrotate.d \
    %{buildroot}%{_bindir} \
    %{buildroot}%{_localstatedir}/log/%{name} \
    %{buildroot}%{_unitdir} \
    %{buildroot}%{_tmpfilesdir}

%{__install} -m0755 -p %{name} %{buildroot}%{_bindir}/%{name}
%{__install} -m0644 -p deploy/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
%{__install} -m0644 -p deploy/%{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -m0644 -p %{name}.conf.example %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf
%{__install} -m0644 -p deploy/storage-schemas.conf %{buildroot}%{_sysconfdir}/%{name}/
%{__install} -m0644 -p deploy/storage-aggregation.conf %{buildroot}%{_sysconfdir}/%{name}/
%{__install} -m0644 -p deploy/%{name}.tmpfiles %{buildroot}%{_tmpfilesdir}/%{name}.conf

%clean
%{__rm} -rf %{buildroot}

%preun
%systemd_preun %{name}.service

%post
%systemd_post %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%pre
%{_bindir}/id carbon >/dev/null 2>&1 || \
  %{_sbindir}/useradd \
    -r -U \
    -s %{_bindir}/false \
    -M -d /dev/null \
    -c "go-graphite daemon" carbon

%files
%license LICENSE.md
%defattr(-,root,root)
%doc README.md CHANGELOG.md %{name}.conf.example deploy/*.conf
%config(noreplace) %{_sysconfdir}/%{name}/*.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%{_tmpfilesdir}/%{name}.conf

%defattr(-, carbon, carbon, 0750)
%dir %{_localstatedir}/log/%{name}

%changelog
* Wed Mar 05 2025 Peter Tuschy <foss+rpm@bofh42.de> - 0.17.3-1
- initial rpm
