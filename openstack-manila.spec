%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0xf8675126e2411e7748dd46662fc2093e4682645f
%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%global service manila

%global common_desc \
OpenStack Shared Filesystem Service (code-name Manila) provides services \
to manage network filesystems for use by Virtual Machine instances.


%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order bashate os-api-ref psycopg2-binary
# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif

Name:             openstack-%{service}
# Liberty semver reset
# https://review.openstack.org/#/q/I6a35fa0dda798fad93b804d00a46af80f08d475c,n,z
Epoch:            1
Version:          18.1.0
Release:          1%{?dist}
Summary:          OpenStack Shared Filesystem Service

License:          Apache-2.0
URL:              https://wiki.openstack.org/wiki/Manila
Source0:          https://tarballs.openstack.org/%{service}/%{service}-%{version}%{?milestone}.tar.gz
#

Source2:          %{service}.logrotate
Source3:          %{service}-dist.conf

Source10:         openstack-%{service}-api.service
Source11:         openstack-%{service}-scheduler.service
Source12:         openstack-%{service}-share.service
Source13:         openstack-%{service}-data.service

Source20:         %{service}-sudoers
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/%{service}/%{service}-%{version}%{?milestone}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch:        noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif
BuildRequires:    intltool
BuildRequires:    openstack-macros
BuildRequires:    git-core
BuildRequires:    systemd
BuildRequires:    python3-devel
BuildRequires:    pyproject-rpm-macros
Requires:         python3-%{service} = %{epoch}:%{version}-%{release}

%{?systemd_ordering}

Requires(pre):    shadow-utils

%description
%{common_desc}

%package -n       python3-%{service}
Summary:          Python libraries for OpenStack Shared Filesystem Service
Group:            Applications/System

Requires:         sudo

%description -n   python3-%{service}
%{common_desc}

This package contains the associated Python library.

%package -n       %{name}-share
Summary:          An implementation of OpenStack Shared Filesystem Service
Group:            Applications/System

Requires:         python3-%{service} = %{epoch}:%{version}-%{release}

%{?systemd_requires}
Requires(pre):    shadow-utils

# The manila-share can create shares out of LVM slices.
Requires:         lvm2
# The manila-share runs testparm, smbd and aborts if it's missing.
Requires:         samba

%description -n   %{name}-share
%{common_desc}

This package contains a reference implementation of a service that
exports shares, similar to a filer.

%package -n python3-%{service}-tests
Summary:        Unit tests for the OpenStack Shared Filesystem Service
Requires:       openstack-%{service} = %{epoch}:%{version}-%{release}
# ddt is a runtime dependency of various tests
Requires:    python3-ddt

%description -n python3-%{service}-tests
%{common_desc}

This package contains the Manila test files.


%if 0%{?with_doc}
%package doc
Summary:          Documentation for OpenStack Shared Filesystem Service
Group:            Documentation

Requires:         %{name} = %{epoch}:%{version}-%{release}
BuildRequires:    graphviz

%description      doc
%{common_desc}

This package contains the associated documentation.
%endif

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{service}-%{upstream_version} -S git

find . \( -name .gitignore -o -name .placeholder \) -delete

find %{service} -name \*.py -exec sed -i '/\/usr\/bin\/env python/{d;q}' {} +

sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini
# Tox uses doc8 to check docs syntax which we do not ship
sed -i /.*doc8.*/d tox.ini
sed -i '/sphinx-build/ s/-W//' tox.ini
# We do not run linters on packaging
rm -f manila/tests/test_hacking.py

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel

%install
%pyproject_install
# Generate config file
PYTHONPATH=%{buildroot}/%{python3_sitelib} oslo-config-generator --config-file=etc/oslo-config-generator/%{service}.conf

# docs generation requires everything to be installed first
%if 0%{?with_doc}
%tox -e docs
# Fix hidden-file-or-dir warnings
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo

sphinx-build -b man doc/source doc/build/man
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 doc/build/man/*.1 %{buildroot}%{_mandir}/man1/
%endif

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{service}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{service}/tmp
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{service}

# Install config files
install -d -m 755 %{buildroot}%{_sysconfdir}/%{service}
install -p -D -m 640 etc/%{service}/%{service}.conf.sample %{buildroot}%{_sysconfdir}/%{service}/%{service}.conf
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_datadir}/%{service}/%{service}-dist.conf
mv %{buildroot}%{_prefix}/etc/%{service}/rootwrap.conf %{buildroot}%{_sysconfdir}/%{service}/rootwrap.conf
# XXX We want to set signing_dir to /var/lib/manila/keystone-signing,
# but there's apparently no way to override the value in api-paste.ini
# from manila.conf. So we keep a forked api-paste.ini around for now.
#install -p -D -m 640 etc/manila/api-paste.ini %{buildroot}%{_sysconfdir}/manila/api-paste.ini
mv %{buildroot}%{_prefix}/etc/%{service}/api-paste.ini %{buildroot}%{_sysconfdir}/%{service}/api-paste.ini

# Install initscripts for services
install -p -D -m 644 %{SOURCE10} %{buildroot}%{_unitdir}/%{name}-api.service
install -p -D -m 644 %{SOURCE11} %{buildroot}%{_unitdir}/%{name}-scheduler.service
install -p -D -m 644 %{SOURCE12} %{buildroot}%{_unitdir}/%{name}-share.service
install -p -D -m 644 %{SOURCE13} %{buildroot}%{_unitdir}/%{name}-data.service

# Install sudoers
install -p -D -m 440 %{SOURCE20} %{buildroot}%{_sysconfdir}/sudoers.d/%{service}

# Install logrotate
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-%{service}

# Install pid directory
install -d -m 755 %{buildroot}%{_localstatedir}/run/%{service}

# Install rootwrap files in /usr/share/manila/rootwrap
mkdir -p %{buildroot}%{_datadir}/%{service}/rootwrap/
mv %{buildroot}%{_prefix}/etc/%{service}/rootwrap.d/* %{buildroot}%{_datadir}/%{service}/rootwrap/

# Remove duplicate config directory /usr/etc/manila, /usr/etc/manila/rootwrap.d,
# we are keeping config files at /etc/manila and rootwrap files at /usr/share/manila/rootwrap
rmdir %{buildroot}%{_prefix}/etc/%{service}/rootwrap.d %{buildroot}%{_prefix}/etc/%{service}

# Remove files unneeded in production
rm -f %{buildroot}%{_bindir}/%{service}-all

%pre -n python3-%{service}
getent group %{service} >/dev/null || groupadd -r %{service}
getent passwd %{service} >/dev/null || \
   useradd -r -g %{service} -G %{service},nobody -d %{_sharedstatedir}/%{service} \
      -s /sbin/nologin -c "OpenStack Manila Daemons" %{service}

%post
%systemd_post %{name}-api.service
%systemd_post %{name}-scheduler.service
%systemd_post %{name}-data.service

%preun
%systemd_preun %{name}-api.service
%systemd_preun %{name}-scheduler.service
%systemd_preun %{name}-data.service

%postun
%systemd_postun_with_restart %{name}-api.service
%systemd_postun_with_restart %{name}-scheduler.service
%systemd_postun_with_restart %{name}-data.service

%post -n %{name}-share
%systemd_post %{name}-share.service

%preun -n %{name}-share
%systemd_preun %{name}-share.service

%postun -n %{name}-share
%systemd_postun_with_restart %{name}-share.service

%check
%tox -e %{default_toxenv}

%files
%{_bindir}/%{service}-wsgi
%{_bindir}/%{service}-api
%{_bindir}/%{service}-scheduler
%{_bindir}/%{service}-data
%{_unitdir}/%{name}-api.service
%{_unitdir}/%{name}-scheduler.service
%{_unitdir}/%{name}-data.service
%if 0%{?with_doc}
%{_mandir}/man1/%{service}*.1.gz
%endif

%defattr(-, %{service}, %{service}, -)
%dir %{_sharedstatedir}/%{service}
%dir %{_sharedstatedir}/%{service}/tmp

%files -n python3-%{service}
%license LICENSE

# Aww, this is awkward. The python-manila itself does not need or provide
# any configurations, but since it's the bracket package, there's no choice.
%dir %{_sysconfdir}/%{service}
%config(noreplace) %attr(-, root, %{service}) %{_sysconfdir}/%{service}/%{service}.conf
%config(noreplace) %attr(-, root, %{service}) %{_sysconfdir}/%{service}/api-paste.ini
%config(noreplace) %attr(-, root, %{service}) %{_sysconfdir}/%{service}/rootwrap.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-%{service}
%config(noreplace) %{_sysconfdir}/sudoers.d/%{service}

%dir %{_datadir}/%{service}
%dir %{_datadir}/%{service}/rootwrap
%{_datadir}/%{service}/rootwrap/*
%attr(-, root, %{service}) %{_datadir}/%{service}/%{service}-dist.conf

# XXX On Fedora 19 and later, /var/run is a symlink to /run, which is mounted.
# If one specifies directories in /run, they disappear on reboot. Fix?
%dir %attr(0750, %{service}, root) %{_localstatedir}/log/%{service}
%dir %attr(0755, %{service}, root) %{_localstatedir}/run/%{service}

%{python3_sitelib}/%{service}
%{python3_sitelib}/%{service}-%{version}*.dist-info
%exclude %{python3_sitelib}/%{service}/tests

%{_bindir}/%{service}-manage
%{_bindir}/%{service}-rootwrap
%{_bindir}/%{service}-status

%files -n python3-%{service}-tests
%license LICENSE
%{python3_sitelib}/%{service}/tests

%files -n %{name}-share
%{_bindir}/%{service}-share
%{_unitdir}/%{name}-share.service

%if 0%{?with_doc}
%files doc
%doc doc/build/html
%endif

%changelog
* Thu Apr 18 2024 RDO <dev@lists.rdoproject.org> 1:18.1.0-1
- Update to 18.1.0

* Wed Apr 03 2024 RDO <dev@lists.rdoproject.org> 1:18.0.1-1
- Update to 18.0.1

* Mon Mar 18 2024 RDO <dev@lists.rdoproject.org> 1:18.0.0-0.1.0rc1
- Update to 18.0.0.0rc1

