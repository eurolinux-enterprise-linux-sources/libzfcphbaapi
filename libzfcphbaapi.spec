%global srcname lib-zfcp-hbaapi

Name:           libzfcphbaapi
Summary:        HBA API for the zFCP device driver
Group:          System Environment/Libraries
Version:        2.1
Release:        2%{?dist}
License:        CPL
URL:            http://www.ibm.com/developerworks/linux/linux390/zfcp-hbaapi.html
# http://www.ibm.com/developerworks/linux/linux390/zfcp-hbaapi-%%{hbaapiver}.html
Source0:        http://download.boulder.ibm.com/ibmdl/pub/software/dw/linux390/ht_src/%{srcname}-%{version}.tar.gz
ExclusiveArch:  s390 s390x

BuildRequires:  automake
BuildRequires:  doxygen
BuildRequires:  libsysfs-devel
BuildRequires:  sg3_utils-devel
BuildRequires:  libhbaapi-devel
Requires:       libhbaapi
Requires(post): grep
Requires(postun): grep sed
Provides:       s390utils-libzfcphbaapi = 2:1.20.0-4
Obsoletes:      s390utils-libzfcphbaapi <= 2:1.20.0-3

# exclude plugin soname from Provides
%global __provides_exclude ^(libzfcphbaapi-%{version}[.]so.*)$

# build the library as a module
Patch1:         %{srcname}-2.1-module.patch
# fix linking of the tools when using vendor library mode
Patch2:         %{srcname}-2.1-vendorlib.patch
# fix crash on HBA_FreeLibrary call (#713817)
Patch3:         %{srcname}-2.1-HBA_FreeLibrary.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=951586
Patch4:         %{srcname}-2.1-parse-u64-as-ull.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=949099
Patch5:         %{srcname}-2.1-find-sg-without-sysfs-deprecated.patch

%description
zFCP HBA API Library is an implementation of FC-HBA (see www.t11.org) for
the zFCP device driver.


%package docs
License:  CPL
Summary:  zFCP HBA API Library -- Documentation
Group:    Development/Libraries
URL:      http://www.ibm.com/developerworks/linux/linux390/zfcp-hbaapi.html
Requires: %{name} = %{version}-%{release}
Provides:       s390utils-libzfcphbaapi-docs = 2:1.20.0-4
Obsoletes:      s390utils-libzfcphbaapi-docs <= 2:1.20.0-3

%description docs
Documentation for the zFCP HBA API Library.


%prep
%setup -q -n %{srcname}-%{version}

%patch1 -p1 -b .module
%patch2 -p1 -b .vendorlib
%patch3 -p2 -b .HBA_FreeLibrary
%patch4 -p2 -b .parse-as-ull
%patch5 -p2 -b .find-sg

# lib-zfcp-hbaapi: fix perms
chmod a-x *.h AUTHORS README ChangeLog LICENSE


%build
%configure --disable-static --enable-vendor-lib
make EXTRA_CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"


%install
%makeinstall docdir=$RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
# keep only html docs
rm -rf $RPM_BUILD_ROOT%{_docdir}/%{srcname}-%{version}/latex
# remove unwanted files
rm -f $RPM_BUILD_ROOT%{_libdir}/%{name}.*


%post
grep -q -e "^libzfcphbaapi" /etc/hba.conf ||
    echo "libzfcphbaapi %{_libdir}/libzfcphbaapi-%{version}.so" >> /etc/hba.conf
:

%preun
grep -q -e "^libzfcphbaapi" /etc/hba.conf &&
    sed -i.orig -e "/^libzfcphbaapi/d" /etc/hba.conf
:


%files
%doc README COPYING ChangeLog AUTHORS LICENSE
%{_bindir}/zfcp_ping
%{_bindir}/zfcp_show
%{_libdir}/%{name}-%{version}.so
%{_mandir}/man3/libzfcphbaapi.3*
%{_mandir}/man3/SupportedHBAAPIs.3*
%{_mandir}/man3/UnSupportedHBAAPIs.3*
%{_mandir}/man8/zfcp_ping.8*
%{_mandir}/man8/zfcp_show.8*
%exclude %{_mandir}/man3/hbaapi.h.3*

%files docs
%docdir %{_docdir}/%{name}-%{version}
%{_docdir}/%{name}-%{version}/


%changelog
* Wed May 29 2013 Dan Horák <dan[at]danny.cz> - 2.1-2
- add missing compatibility Provides
- exclude plugin soname from Provides

* Thu May 16 2013 Dan Horák <dan[at]danny.cz> - 2.1-1
- move libzfcphbaapi to own package from s390utils
