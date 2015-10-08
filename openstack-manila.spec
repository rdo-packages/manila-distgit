%global with_doc %{!?_without_doc:1}%{?_without_doc:0}

## N.B. For next release: in the past Manila's milestones didn't have a dot.
## If they gain a dot, put it into the milestone macro, like we do with dist.
#global milestone rc2
%global upstream_name manila
%global milestone .0rc2

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:             openstack-manila
# Liberty semver reset
# https://review.openstack.org/#/q/I6a35fa0dda798fad93b804d00a46af80f08d475c,n,z
Epoch:            1
Version:          1.0.0
Release:          0.1%{?milestone}%{?dist}
Summary:          OpenStack Shared Filesystem Service

License:          ASL 2.0
URL:              https://wiki.openstack.org/wiki/Manila
Source0:          http://tarballs.openstack.org/manila/%{upstream_name}-%{upstream_version}.tar.gz
Source1:          manila.conf
Source2:          manila.logrotate
Source3:          manila-dist.conf
Source4:          api-paste.ini

Source10:         openstack-manila-api.service
Source11:         openstack-manila-scheduler.service
Source12:         openstack-manila-share.service

Source20:         manila-sudoers


#
# patches_base=1.0.0.0rc2
#

BuildArch:        noarch
BuildRequires:    intltool
BuildRequires:    python-d2to1
BuildRequires:    python-oslo-sphinx
BuildRequires:    python-pbr
BuildRequires:    python-setuptools
BuildRequires:    python-sphinx
BuildRequires:    python2-devel

Requires:         openstack-utils
Requires:         python-manila = %{epoch}:%{version}-%{release}

Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
Requires(pre):    shadow-utils

# We pull the posix_ipc with Oslo's common lockutils.
Requires:         python-posix_ipc

%description
OpenStack Shared Filesystem Service (code-name Manila) provides services
to manage network filesystems for use by Virtual Machine instances.

%package -n       python-manila
Summary:          Python libraries for OpenStack Shared Filesystem Service
Group:            Applications/System

# Rootwrap in 2013.2 and later deprecates anything but sudo.
Requires:         sudo

Requires:         MySQL-python

Requires:         python-paramiko

Requires:         python-qpid
Requires:         python-kombu
Requires:         python-amqplib

Requires:         python-eventlet
Requires:         python-greenlet
Requires:         python-iso8601
Requires:         python-netaddr
Requires:         python-lxml
Requires:         python-anyjson
Requires:         python-cheetah
Requires:         python-suds

Requires:         python-sqlalchemy
Requires:         python-migrate

Requires:         python-paste-deploy
Requires:         python-routes
Requires:         python-webob

Requires:         python-cinderclient
Requires:         python-keystoneclient
Requires:         python-keystonemiddleware
Requires:         python-neutronclient
Requires:         python-novaclient >= 1:2.15

Requires:         python-oslo-concurrency >= 1.8.0
Requires:         python-oslo-config >= 1.7.0
Requires:         python-oslo-context >= 0.2.0
Requires:         python-oslo-db >= 1.7.1
Requires:         python-oslo-i18n >= 1.5.0
Requires:         python-oslo-log
Requires:         python-oslo-messaging >= 1.3.0-0.1.a9
Requires:         python-oslo-rootwrap
Requires:         python-oslo-serialization >= 1.4.0
Requires:         python-oslo-service
Requires:         python-oslo-utils >= 1.4.0

# We need pbr at runtime because it deterimines the version seen in API.
Requires:         python-pbr

Requires:         python-six >= 1.5.0

Requires:         python-babel
Requires:         python-lockfile

%description -n   python-manila
OpenStack Shared Filesystem Service (code-name Manila) provides services
to manage network filesystems for use by Virtual Machine instances.

This package contains the associated Python library.

%package -n       %{name}-share
Summary:          An implementation of OpenStack Shared Filesystem Service
Group:            Applications/System

Requires:         python-manila = %{epoch}:%{version}-%{release}

Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
Requires(pre):    shadow-utils

# The manila-share can create shares out of LVM slices.
Requires:         lvm2
# The manila-share runs testparm, smbd and aborts if it's missing.
Requires:         samba

%description -n   %{name}-share
OpenStack Shared Filesystem Service (code-name Manila) provides services
to manage network filesystems for use by Virtual Machine instances.

This package contains a reference implementation of a service that
exports shares, similar to a filer.

%if 0%{?with_doc}
%package doc
Summary:          Documentation for OpenStack Shared Filesystem Service
Group:            Documentation

Requires:         %{name} = %{epoch}:%{version}-%{release}

BuildRequires:    systemd-units
#BuildRequires:    graphviz

# Required to build module documents
BuildRequires:    python-eventlet
BuildRequires:    python-routes
BuildRequires:    python-sqlalchemy
BuildRequires:    python-webob
# while not strictly required, quiets the build down when building docs.
BuildRequires:    python-migrate, python-iso8601

%description      doc
OpenStack Shared Filesystem Service (code-name Manila) provides services
to manage network filesystems for use by Virtual Machine instances.

This package contains the associated documentation.
%endif

%prep
%autosetup -n %{upstream_name}-%{upstream_version} -S git

find . \( -name .gitignore -o -name .placeholder \) -delete

find manila -name \*.py -exec sed -i '/\/usr\/bin\/env python/{d;q}' {} +

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt tools/{pip,test}-requires

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# docs generation requires everything to be installed first
export PYTHONPATH="$( pwd ):$PYTHONPATH"

pushd doc

%if 0%{?with_doc}
SPHINX_DEBUG=1 sphinx-build -b html source build/html
# Fix hidden-file-or-dir warnings
rm -fr build/html/.doctrees build/html/.buildinfo
%endif

# Create dir link to avoid a sphinx-build exception
mkdir -p build/man/.doctrees/
ln -s .  build/man/.doctrees/man
SPHINX_DEBUG=1 sphinx-build -b man -c source source/man build/man
mkdir -p %{buildroot}%{_mandir}/man1
install -p -D -m 644 build/man/*.1 %{buildroot}%{_mandir}/man1/

popd

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/manila
install -d -m 755 %{buildroot}%{_sharedstatedir}/manila/tmp
install -d -m 755 %{buildroot}%{_localstatedir}/log/manila

# Install config files
install -d -m 755 %{buildroot}%{_sysconfdir}/manila
install -p -D -m 640 %{SOURCE1} %{buildroot}%{_sysconfdir}/manila/manila.conf
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_datadir}/manila/manila-dist.conf
install -p -D -m 640 etc/manila/rootwrap.conf %{buildroot}%{_sysconfdir}/manila/rootwrap.conf
# XXX We want to set signing_dir to /var/lib/manila/keystone-signing,
# but there's apparently no way to override the value in api-paste.ini
# from manila.conf. So we keep a forked api-paste.ini around for now.
#install -p -D -m 640 etc/manila/api-paste.ini %{buildroot}%{_sysconfdir}/manila/api-paste.ini
install -p -D -m 640 %{SOURCE4} %{buildroot}%{_sysconfdir}/manila/api-paste.ini
install -p -D -m 640 etc/manila/policy.json %{buildroot}%{_sysconfdir}/manila/policy.json

# Install initscripts for services
install -p -D -m 644 %{SOURCE10} %{buildroot}%{_unitdir}/%{name}-api.service
install -p -D -m 644 %{SOURCE11} %{buildroot}%{_unitdir}/%{name}-scheduler.service
install -p -D -m 644 %{SOURCE12} %{buildroot}%{_unitdir}/%{name}-share.service

# Install sudoers
install -p -D -m 440 %{SOURCE20} %{buildroot}%{_sysconfdir}/sudoers.d/manila

# Install logrotate
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-manila

# Install pid directory
install -d -m 755 %{buildroot}%{_localstatedir}/run/manila

# Install rootwrap files in /usr/share/manila/rootwrap
mkdir -p %{buildroot}%{_datadir}/manila/rootwrap/
install -p -D -m 644 etc/manila/rootwrap.d/* %{buildroot}%{_datadir}/manila/rootwrap/

# Install tempest tests files
cp -r manila_tempest_tests %{buildroot}%{python2_sitelib}/manila_tempest_tests

%pre -n python-manila
getent group manila >/dev/null || groupadd -r manila
getent passwd manila >/dev/null || \
   useradd -r -g manila -G manila,nobody -d %{_sharedstatedir}/manila \
      -s /sbin/nologin -c "OpenStack Manila Daemons" manila

%post
%systemd_post %{name}-api.service
%systemd_post %{name}-scheduler.service

%preun
%systemd_preun %{name}-api.service
%systemd_preun %{name}-scheduler.service

%postun
%systemd_postun_with_restart %{name}-api.service
%systemd_postun_with_restart %{name}-scheduler.service

%post -n %{name}-share
%systemd_post %{name}-share.service

%preun -n %{name}-share
%systemd_preun %{name}-share.service

%postun -n %{name}-share
%systemd_postun_with_restart %{name}-share.service

%files
%{_bindir}/manila-api
%{_bindir}/manila-scheduler
%{_unitdir}/%{name}-api.service
%{_unitdir}/%{name}-scheduler.service
%{_mandir}/man1/manila*.1.gz

%defattr(-, manila, manila, -)
%dir %{_sharedstatedir}/manila
%dir %{_sharedstatedir}/manila/tmp

%files -n python-manila
%doc LICENSE

# Aww, this is awkward. The python-manila itself does not need or provide
# any configurations, but since it's the bracket package, there's no choice.
%dir %{_sysconfdir}/manila
%config(noreplace) %attr(-, root, manila) %{_sysconfdir}/manila/manila.conf
%config(noreplace) %attr(-, root, manila) %{_sysconfdir}/manila/api-paste.ini
%config(noreplace) %attr(-, root, manila) %{_sysconfdir}/manila/rootwrap.conf
%config(noreplace) %attr(-, root, manila) %{_sysconfdir}/manila/policy.json
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-manila
%config(noreplace) %{_sysconfdir}/sudoers.d/manila

%dir %{_datadir}/manila
%dir %{_datadir}/manila/rootwrap
%{_datadir}/manila/rootwrap/*
%attr(-, root, manila) %{_datadir}/manila/manila-dist.conf

# XXX On Fedora 19 and later, /var/run is a symlink to /run, which is mounted.
# If one specifies directories in /run, they disappear on reboot. Fix?
%dir %attr(0750, manila, root) %{_localstatedir}/log/manila
%dir %attr(0755, manila, root) %{_localstatedir}/run/manila

%{python2_sitelib}/manila
%{python2_sitelib}/manila-%{version}*.egg-info
# Tempest tests
%{python2_sitelib}/manila_tempest_tests

%{_bindir}/manila-all
%{_bindir}/manila-manage
%{_bindir}/manila-rootwrap

%files -n %{name}-share
%{_bindir}/manila-share
%{_unitdir}/%{name}-share.service

%if 0%{?with_doc}
%files doc
%doc doc/build/html
%endif

%changelog
* Thu Oct 08 2015 Haikel Guemar <hguemar@fedoraproject.org> 1:1.0.0-0.1.0rc2
- Update to upstream 1.0.0.0rc2

* Mon Jul 27 2015 Haïkel Guémar <hguemar@fedoraproject.org> - 2015.1.0-4
- Update to latest stable/kilo

* Mon Jun 29 2015 Pete Zaitcev <zaitcev@redhat.com> - 2015.1.0-3
- Drop the direct dependencies on python-qpid et.al.

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2015.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Apr 30 2015 Pete Zaitcev <zaitcev@redhat.com> - 2015.1.0-1
- Final Kilo release (2015.1.0)

* Wed Apr 29 2015 Pete Zaitcev <zaitcev@redhat.com> - 2015.1-0.3.rc1
- Set better dependencies from the results of testing, mostly python-oslo-*

* Fri Apr 24 2015 Martin Mágr <mmagr@redhat.com> - 2015.1-0.2.rc1
- Modified logrotate file so that log files won't grow too big (bz#1212485)

* Wed Apr 22 2015 Pete Zaitcev <zaitcev@redhat.com> - 2015.1-0.1.rc1
- Update to upstream 2015.1.0rc1
- Use the OpenStack tarballs repository instead of raw Github

* Tue Oct 14 2014 Haïkel Guémar <hguemar@fedoraproject.org> - 2014.2-0.3
- Upstream 2014.2.rc2

* Wed Sep 10 2014 Pete Zaitcev <zaitcev@redhat.com>
- 2014.2-0.2
- Address review comments bz#1125033 comment#2
- Upstream removed jQuery

* Sun Aug 10 2014 Pete Zaitcev <zaitcev@redhat.com>
- 2013.2-0.9
- Add dependency on python-neutronclient, else traceback
- Split away the openstack-manila-share and its dependencies on lvm2 and samba

* Wed Jul 30 2014 Pete Zaitcev <zaitcev@redhat.com>
- 2013.2-0.8
- Switch to dynamic UID/GID allocation per Packaging:UsersAndGroups

* Tue Jul 29 2014 Pete Zaitcev <zaitcev@redhat.com>
- 2013.2-0.7
- Require python-pbr after all

* Thu Jun 26 2014 Pete Zaitcev <zaitcev@redhat.com>
- 2013.2-0.3
- Initial testing RPM
