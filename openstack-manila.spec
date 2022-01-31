%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x01527a34f0d0080f8a5db8d6eb6c5df21b4b6363
%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%global service manila

## N.B. For next release: in the past Manila's milestones didn't have a dot.
## If they gain a dot, put it into the milestone macro, like we do with dist.
#global milestone rc2

%global common_desc \
OpenStack Shared Filesystem Service (code-name Manila) provides services \
to manage network filesystems for use by Virtual Machine instances.


%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:             openstack-%{service}
# Liberty semver reset
# https://review.openstack.org/#/q/I6a35fa0dda798fad93b804d00a46af80f08d475c,n,z
Epoch:            1
Version:          12.1.1
Release:          1%{?dist}
Summary:          OpenStack Shared Filesystem Service

License:          ASL 2.0
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
BuildRequires:    python3-pbr
BuildRequires:    python3-setuptools
BuildRequires:    python3-devel
BuildRequires:    python3-mock
BuildRequires:    python3-oslotest
BuildRequires:    python3-ddt
BuildRequires:    python3-tooz


BuildRequires:    python3-lxml
BuildRequires:    python3-retrying >= 1.2.3

Requires:         python3-%{service} = %{epoch}:%{version}-%{release}

%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif
Requires(pre):    shadow-utils

%description
%{common_desc}

%package -n       python3-%{service}
Summary:          Python libraries for OpenStack Shared Filesystem Service
%{?python_provide:%python_provide python3-%{service}}
Group:            Applications/System

# Rootwrap in 2013.2 and later deprecates anything but sudo.
Requires:         sudo

Requires:         python3-paramiko >= 2.7.2

Requires:         python3-alembic >= 1.4.2
Requires:         python3-eventlet >= 0.26.1
Requires:         python3-greenlet >= 0.4.13
Requires:         python3-netaddr >= 0.7.19
Requires:         python3-requests >= 2.23.0
Requires:         python3-stevedore >= 3.2.2
Requires:         python3-tooz >= 2.7.1

Requires:         python3-sqlalchemy >= 1.3.1

Requires:         python3-routes >= 2.4.1
Requires:         python3-webob >= 1.8.6

Requires:         python3-cinderclient >= 3.3.0
Requires:         python3-glanceclient >= 3.2.2
Requires:         python3-keystoneauth1 >= 4.2.1
Requires:         python3-keystonemiddleware >= 9.1.0
Requires:         python3-neutronclient >= 6.7.0
Requires:         python3-novaclient >= 17.2.1

Requires:         python3-oslo-concurrency >= 4.3.0
Requires:         python3-oslo-config >= 2:8.3.2
Requires:         python3-oslo-context >= 3.1.1
Requires:         python3-oslo-db >= 8.4.0
Requires:         python3-oslo-i18n >= 5.0.1
Requires:         python3-oslo-log >= 4.4.0
Requires:         python3-oslo-messaging >= 12.5.0
Requires:         python3-oslo-middleware >= 4.1.1
Requires:         python3-oslo-policy >= 3.6.2
Requires:         python3-oslo-reports >= 2.2.0
Requires:         python3-oslo-rootwrap >= 6.2.0
Requires:         python3-oslo-serialization >= 4.0.1
Requires:         python3-oslo-service >= 2.4.0
Requires:         python3-oslo-upgradecheck >= 1.3.0
Requires:         python3-oslo-utils >= 4.7.0
# We need pbr at runtime because it deterimines the version seen in API.
Requires:         python3-pbr >= 5.5.0

Requires:         python3-six >= 1.15.0

Requires:         python3-pyparsing >= 2.4.6

Requires:         python3-lxml >= 4.2.3
Requires:         python3-retrying >= 1.2.3
Requires:         python3-paste-deploy >= 2.1.0
Requires:         python3-paste >= 3.4.3
Requires:         python3-osprofiler >= 3.4.0

# Config file generation dependencies
BuildRequires:    python3-oslo-config >= 2:8.3.2
BuildRequires:    python3-oslo-concurrency >= 3.25.0
BuildRequires:    python3-oslo-db >= 4.27.0
BuildRequires:    python3-oslo-messaging >= 5.29.0
BuildRequires:    python3-oslo-middleware
BuildRequires:    python3-oslo-policy >= 1.30.0
BuildRequires:    python3-keystoneauth1
BuildRequires:    python3-keystonemiddleware
BuildRequires:    python3-cinderclient
BuildRequires:    python3-glanceclient
BuildRequires:    python3-neutronclient
BuildRequires:    python3-novaclient >= 9.1.0
BuildRequires:    python3-paramiko

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
%{?python_provide:%python_provide python3-%{service}-tests}
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

# Required to build module documents
BuildRequires:    python3-eventlet
BuildRequires:    python3-routes
BuildRequires:    python3-sqlalchemy
BuildRequires:    python3-webob
# while not strictly required, quiets the build down when building docs.
BuildRequires:    python3-iso8601
# Required to build manpages and html documents
BuildRequires:    python3-sphinx
BuildRequires:    python3-openstackdocstheme

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

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
%py_req_cleanup

# FIXME avoid LXD dependency - real fix is to make drivers fully pluggable upstream
sed -i '/lxd/ s/^/#/' %{service}/opts.py

# disable warning-is-error, image install/common/figures/hwreqs.png is not included
# in the tarball so it generates a warning when trying to create the doc. Until this
# is fixed upstream, we need to disable warning-is-error
sed -i 's/^warning-is-error.*/warning-is-error = 0/g' setup.cfg

%build
# Generate config file
PYTHONPATH=. oslo-config-generator --config-file=etc/oslo-config-generator/%{service}.conf

%{py3_build}

%install
%{py3_install}

# docs generation requires everything to be installed first
%if 0%{?with_doc}
sphinx-build -b html doc/source doc/build/html
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
%{python3_sitelib}/%{service}-%{version}*.egg-info
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
* Mon Jan 31 2022 RDO <dev@lists.rdoproject.org> 1:12.1.1-1
- Update to 12.1.1

* Tue Nov 09 2021 RDO <dev@lists.rdoproject.org> 1:12.1.0-1
- Update to 12.1.0

* Wed Apr 14 2021 RDO <dev@lists.rdoproject.org> 1:12.0.0-1
- Update to 12.0.0

* Fri Mar 26 2021 RDO <dev@lists.rdoproject.org> 1:12.0.0-0.1.0rc1
- Update to 12.0.0.0rc1

