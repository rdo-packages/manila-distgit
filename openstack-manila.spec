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
Version:          XXX
Release:          XXX
Summary:          OpenStack Shared Filesystem Service

License:          ASL 2.0
URL:              https://wiki.openstack.org/wiki/Manila
Source0:          https://tarballs.openstack.org/%{service}/%{service}-%{version}%{?milestone}.tar.gz
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
BuildRequires:    python-pbr
BuildRequires:    python-setuptools
BuildRequires:    python2-devel
BuildRequires:    python-mock
BuildRequires:    python-oslotest
BuildRequires:    python-lxml
BuildRequires:    python-ddt
BuildRequires:    python-tooz

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

Requires:         python-paramiko

Requires:         python-alembic
Requires:         python-eventlet
Requires:         python-greenlet
Requires:         python-ipaddress
Requires:         python-iso8601
Requires:         python-netaddr
Requires:         python-lxml
Requires:         python-anyjson
Requires:         python-requests >= 2.10.0
Requires:         python-retrying >= 1.2.3
Requires:         python-stevedore >= 1.20.0
Requires:         python-suds
Requires:         python-tooz >= 1.47.0

Requires:         python-sqlalchemy
Requires:         python-migrate

Requires:         python-paste-deploy
Requires:         python-routes
Requires:         python-webob

Requires:         python-cinderclient >= 3.1.0
Requires:         python-keystoneauth1 >= 3.1.0
Requires:         python-keystoneclient
Requires:         python-keystonemiddleware >= 4.12.0
Requires:         python-neutronclient >= 6.3.0
Requires:         python-novaclient >= 1:9.0.0

Requires:         python-oslo-concurrency >= 3.8.0
Requires:         python-oslo-config >= 2:4.0.0
Requires:         python-oslo-context >= 2.14.0
Requires:         python-oslo-db >= 4.24.0
Requires:         python-oslo-i18n >= 2.1.0
Requires:         python-oslo-log >= 3.22.0
Requires:         python-oslo-messaging >= 5.24.2
Requires:         python-oslo-middleware >= 3.27.0
Requires:         python-oslo-policy >= 1.23.0
Requires:         python-oslo-reports >= 0.6.0
Requires:         python-oslo-rootwrap >= 5.0.0
Requires:         python-oslo-serialization >= 1.10.0
Requires:         python-oslo-service >= 1.10.0
Requires:         python-oslo-utils >= 3.20.0

# We need pbr at runtime because it deterimines the version seen in API.
Requires:         python-pbr

Requires:         python-six >= 1.9.0

Requires:         python-babel
Requires:         python-lockfile
Requires:         pyparsing >= 2.0.1

# Config file generation dependencies
BuildRequires:    python-oslo-config >= 4.0.0
BuildRequires:    python-oslo-concurrency >= 3.8.0
BuildRequires:    python-oslo-db >= 4.24.0
BuildRequires:    python-oslo-messaging >= 5.24.2
BuildRequires:    python-oslo-middleware
BuildRequires:    python-oslo-policy >= 1.23.0
BuildRequires:    python-keystoneauth1
BuildRequires:    python-keystonemiddleware
BuildRequires:    python-cinderclient
BuildRequires:    python-neutronclient
BuildRequires:    python-novaclient >= 1:9.0.0
BuildRequires:    python-paramiko

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

%description -n python-%{service}-tests
%{common_desc}

This package contains the Manila test files.


%if 0%{?with_doc}
%package doc
Summary:          Documentation for OpenStack Shared Filesystem Service
Group:            Documentation

Requires:         %{name} = %{epoch}:%{version}-%{release}

BuildRequires:    systemd-units
BuildRequires:    graphviz

# Required to build module documents
BuildRequires:    python-sphinx
BuildRequires:    python-openstackdocstheme
BuildRequires:    python-eventlet
BuildRequires:    python-routes
BuildRequires:    python-sqlalchemy
BuildRequires:    python-webob
# while not strictly required, quiets the build down when building docs.
BuildRequires:    python-migrate, python-iso8601

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

# Create fake egg-info for the tempest plugin
%py2_entrypoint %{service} %{service}

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
mv %{buildroot}%{_prefix}/etc/%{service}/policy.json %{buildroot}%{_sysconfdir}/%{service}/policy.json

# Install initscripts for services
install -p -D -m 644 %{SOURCE10} %{buildroot}%{_unitdir}/%{name}-api.service
install -p -D -m 644 %{SOURCE11} %{buildroot}%{_unitdir}/%{name}-scheduler.service
install -p -D -m 644 %{SOURCE12} %{buildroot}%{_unitdir}/%{name}-share.service
install -p -D -m 644 %{SOURCE12} %{buildroot}%{_unitdir}/%{name}-data.service

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
# Install tempest tests files
cp -r %{service}_tempest_tests %{buildroot}%{python2_sitelib}/%{service}_tempest_tests

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
%config(noreplace) %attr(-, root, %{service}) %{_sysconfdir}/%{service}/policy.json
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
%exclude %{python2_sitelib}/%{service}_tempest_tests
%exclude %{python2_sitelib}/%{service}/tests

%{_bindir}/%{service}-manage
%{_bindir}/%{service}-rootwrap

%files -n python-%{service}-tests
%license LICENSE
%{python2_sitelib}/%{service}_tempest_tests
%{python2_sitelib}/%{service}/tests
%{python2_sitelib}/%{service}_tests.egg-info

%files -n %{name}-share
%{_bindir}/%{service}-share
%{_unitdir}/%{name}-share.service

%if 0%{?with_doc}
%files doc
%doc doc/build/html
%endif

%changelog
