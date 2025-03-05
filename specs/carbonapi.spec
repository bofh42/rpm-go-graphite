# spec file for package carbonapi

%define debug_package %{nil}

Name:           carbonapi
Version:        0.16.0
Release:        1%{?dist}
Summary:        carbonapi: replacement for graphite API server
License:        BSD-2
Group:          bofh42/addon/go-graphite
Url:            https://github.com/go-graphite/carbonapi

# spectool -fg -S -R go-carbon.spec to download source
Source0:        %{url}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz
# this needs to be updated for every version change
%global src0sum 43bcc540bd1b365fa4a56414bf0302df

# for create new vendor tar.gz unpack source and cd into it
# sudo rm -rf ~/.cache/go* ~/go ; go mod vendor && tar -cvzf ../carbonapi-$(pwd | awk -F- '{ print $NF}')-vendor.tar.gz vendor
Source2:        %{name}-%{version}-vendor.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-build


BuildRequires:  xxhash
BuildRequires:  cairo-devel >= 1.12.0
BuildRequires:  golang >= 1.21.13, compiler(go-compiler)

%{?systemd_requires}
Requires(pre):  %{_sbindir}/useradd
Requires(pre):  %{_bindir}/id

%description
carbonapi: replacement for graphite API server

%prep
echo "%{src0sum}  %{SOURCE0}" | xxh128sum -c

%setup -q -n %{name}-%{version}
%setup -q -T -D -a 2 -n %{name}-%{version}

%build
# use local vendor source
export GO111MODULE=on
export GOFLAGS=-mod=vendor

make

# our tmpfiles
echo "D /run/%{name} 0775 carbon carbon -" >%{name}.tmpfiles

%check
# use local vendor source
export GO111MODULE=on
export GOFLAGS=-mod=vendor

make test

%install
%{__rm} -rf %{buildroot}
%{__install} -d -m0755 \
    %{buildroot}%{_sysconfdir}/%{name} \
    %{buildroot}%{_sysconfdir}/logrotate.d \
    %{buildroot}%{_sysconfdir}/sysconfig \
    %{buildroot}%{_bindir} \
    %{buildroot}%{_localstatedir}/log/%{name} \
    %{buildroot}%{_unitdir} \
    %{buildroot}%{_tmpfilesdir}

%{__install} -m0755 -p %{name} %{buildroot}%{_bindir}/%{name}
%{__install} -m0644 -p contrib/%{name}/common/%{name}.env %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__install} -m0644 -p contrib/%{name}/rhel/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
%{__install} -m0644 -p contrib/%{name}/rhel/%{name}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -m0644 -p %{name}.tmpfiles %{buildroot}%{_tmpfilesdir}/%{name}.conf

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
%license LICENSE
%defattr(-,root,root)
%doc *.md cmd/carbonapi/carbonapi.example.yaml
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%{_tmpfilesdir}/%{name}.conf

%defattr(-, carbon, carbon, 0750)
%dir %{_localstatedir}/log/%{name}

%changelog
* Wed Mar 05 2025 Peter Tuschy <foss+rpm@bofh42.de> - 0.16.0-1
- initial rpm
