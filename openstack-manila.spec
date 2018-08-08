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
Version:          6.0.2
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

BuildArch:        noarch
BuildRequires:    intltool
BuildRequires:    openstack-macros
BuildRequires:    git
BuildRequires:    python-d2to1
BuildRequires:    python2-pbr
BuildRequires:    python2-setuptools
BuildRequires:    python2-devel
BuildRequires:    python2-mock
BuildRequires:    python2-oslotest
BuildRequires:    python-lxml
BuildRequires:    python2-ddt
BuildRequires:    python2-tooz
# Required to build manpages and html documents
BuildRequires:    python2-sphinx
BuildRequires:    python2-openstackdocstheme

Requires:         python-%{service} = %{epoch}:%{version}-%{release}

%{?systemd_requires}
Requires(pre):    shadow-utils

# We pull the posix_ipc with Oslo's common lockutils.
Requires:         python-posix_ipc

%description
%{common_desc}

%package -n       python-%{service}
Summary:          Python libraries for OpenStack Shared Filesystem Service
Group:            Applications/System

# Rootwrap in 2013.2 and later deprecates anything but sudo.
Requires:         sudo

Requires:         python2-paramiko

Requires:         python2-alembic
Requires:         python2-eventlet
Requires:         python2-greenlet
Requires:         python-ipaddress
Requires:         python2-netaddr
Requires:         python-lxml
Requires:         python-anyjson
Requires:         python2-requests >= 2.14.2
Requires:         python-retrying >= 1.2.3
Requires:         python2-stevedore >= 1.20.0
Requires:         python2-suds
Requires:         python2-tooz >= 1.58.0

Requires:         python2-sqlalchemy
Requires:         python-migrate

Requires:         python-paste-deploy
Requires:         python2-routes
Requires:         python-webob

Requires:         python2-cinderclient >= 3.3.0
Requires:         python2-keystoneauth1 >= 3.3.0
Requires:         python2-keystoneclient
Requires:         python2-keystonemiddleware >= 4.17.0
Requires:         python2-neutronclient >= 6.3.0
Requires:         python2-novaclient >= 9.1.0

Requires:         python2-oslo-concurrency >= 3.25.0
Requires:         python2-oslo-config >= 2:5.1.0
Requires:         python2-oslo-context >= 2.19.2
Requires:         python2-oslo-db >= 4.27.0
Requires:         python2-oslo-i18n >= 3.15.3
Requires:         python2-oslo-log >= 3.36.0
Requires:         python2-oslo-messaging >= 5.29.0
Requires:         python2-oslo-middleware >= 3.31.0
Requires:         python2-oslo-policy >= 1.30.0
Requires:         python2-oslo-reports >= 1.18.0
Requires:         python2-oslo-rootwrap >= 5.8.0
Requires:         python2-oslo-serialization >= 2.18.0
Requires:         python2-oslo-service >= 1.24.0
Requires:         python2-oslo-utils >= 3.33.0

# We need pbr at runtime because it deterimines the version seen in API.
Requires:         python2-pbr

Requires:         python2-six >= 1.10.0

Requires:         python2-babel
Requires:         python2-pyparsing >= 2.1.0

# Config file generation dependencies
BuildRequires:    python2-oslo-config >= 2:5.1.0
BuildRequires:    python2-oslo-concurrency >= 3.25.0
BuildRequires:    python2-oslo-db >= 4.27.0
BuildRequires:    python2-oslo-messaging >= 5.29.0
BuildRequires:    python2-oslo-middleware
BuildRequires:    python2-oslo-policy >= 1.30.0
BuildRequires:    python2-keystoneauth1
BuildRequires:    python2-keystonemiddleware
BuildRequires:    python2-cinderclient
BuildRequires:    python2-neutronclient
BuildRequires:    python2-novaclient >= 9.1.0
BuildRequires:    python2-paramiko

%description -n   python-%{service}
%{common_desc}

This package contains the associated Python library.

%package -n       %{name}-share
Summary:          An implementation of OpenStack Shared Filesystem Service
Group:            Applications/System

Requires:         python-%{service} = %{epoch}:%{version}-%{release}

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

%package -n python-%{service}-tests
Summary:        Manila tests
Requires:       openstack-%{service} = %{epoch}:%{version}-%{release}

# ddt is a runtime dependency of various tests
Requires:    python2-ddt

%description -n python-%{service}-tests
%{common_desc}

This package contains the Manila test files.


%if 0%{?with_doc}
%package doc
Summary:          Documentation for OpenStack Shared Filesystem Service
Group:            Documentation

Requires:         %{name} = %{epoch}:%{version}-%{release}

BuildRequires:    systemd
BuildRequires:    graphviz

# Required to build module documents
BuildRequires:    python2-eventlet
BuildRequires:    python2-routes
BuildRequires:    python2-sqlalchemy
BuildRequires:    python-webob
# while not strictly required, quiets the build down when building docs.
BuildRequires:    python-migrate, python2-iso8601

%description      doc
%{common_desc}

This package contains the associated documentation.
%endif

%prep
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

%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# docs generation requires everything to be installed first
%if 0%{?with_doc}
%{__python2} setup.py build_sphinx -b html
# Fix hidden-file-or-dir warnings
rm -fr doc/build/html/.doctrees doc/build/html/.buildinfo
%endif

%{__python2} setup.py build_sphinx -b man
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 doc/build/man/*.1 %{buildroot}%{_mandir}/man1/

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

%pre -n python-%{service}
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
%{_mandir}/man1/%{service}*.1.gz

%defattr(-, %{service}, %{service}, -)
%dir %{_sharedstatedir}/%{service}
%dir %{_sharedstatedir}/%{service}/tmp

%files -n python-%{service}
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

%{python2_sitelib}/%{service}
%{python2_sitelib}/%{service}-%{version}*.egg-info
%exclude %{python2_sitelib}/%{service}/tests

%{_bindir}/%{service}-manage
%{_bindir}/%{service}-rootwrap

%files -n python-%{service}-tests
%license LICENSE
%{python2_sitelib}/%{service}/tests

%files -n %{name}-share
%{_bindir}/%{service}-share
%{_unitdir}/%{name}-share.service

%if 0%{?with_doc}
%files doc
%doc doc/build/html
%endif

%changelog
* Wed Aug 08 2018 RDO <dev@lists.rdoproject.org> 1:6.0.2-1
- Update to 6.0.2

* Tue Apr 24 2018 RDO <dev@lists.rdoproject.org> 1:6.0.1-1
- Update to 6.0.1

* Wed Feb 28 2018 RDO <dev@lists.rdoproject.org> 1:6.0.0-1
- Update to 6.0.0

* Thu Feb 22 2018 RDO <dev@lists.rdoproject.org> 1:6.0.0-0.3.0rc2
- Update to 6.0.0.0rc3

* Tue Feb 20 2018 RDO <dev@lists.rdoproject.org> 1:6.0.0-0.2.0rc1
- Update to 6.0.0.0rc2

* Thu Feb 15 2018 RDO <dev@lists.rdoproject.org> 1:6.0.0-0.1.0rc1
- Update to 6.0.0.0rc1

