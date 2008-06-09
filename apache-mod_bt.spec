%define mod_name mod_bt
%define mod_conf 69_%{mod_name}.conf

%define	major 0
%define libname %mklibname mod_bt %{major}

Summary:	BitTorrent tracker for the Apache2 web server
Name:		apache-%{mod_name}
Version:	0.0.19
Release:	%mkrel 9
Group:		System/Servers
License:	GPL
URL:		http://www.crackerjack.net/mod_bt/
Source0:	http://www.crackerjack.net/mod_bt/%{mod_name}-%{version}.tar.bz2
Source1:	%{mod_conf}
Patch0:		mod_bt-we_are_at_apr1.diff
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	apache-mod_perl-devel
#BuildRequires:	autoconf2.5
#BuildRequires:	automake1.7
BuildRequires:	libxml2-devel
BuildRequires:	db4-devel
BuildRequires:	perl
BuildRequires:	perl-devel
BuildRequires:	libtool
BuildRequires:	php-devel
BuildRequires:	php-cli
BuildRequires:	pkgconfig
BuildRequires:	file
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_bt is a BitTorrent tracker for the Apache Web server. It is written in C
and runs as an Apache 2.x module. It is possible for mod_perl or PHP to
directly access the tracker's information; no need to download and bdecode
scrape URLs. The tracker is fully configured from within Apache's own
configuration file. The goal of mod_bt is to seamlessly integrate Bram
Cohen's BitTorrent protocol with Apache so that any Webmaster who serves up
large files can shift the burden of bandwidth onto its clients with as little
hassle as possible.

%package -n	%{libname}
Summary:	Shared BitTorrent Tracker and Utility Library
Group:          System/Libraries

%description -n	%{libname}
libbtt provides logic to drive a BitTorrent tracker. No actual connection
handling is done by this module; instead, it accepts BitTorrent request
information as strings, processes the request, and returns strings suitable
to send back to the client.

libbtutil provides several functions that are useful to BitTorrent trackers,
peers, and tools, such as:

 o Parsing of bencoded and URL query data
 o SHA1-summing data
 o Loading of metainfo (.torrent) files
 o Pretty formatting commonly-used data types (SHA1 sums, file sizes, etc.)

%package	utils
Summary:	BitTorrent Tracker Library - Utility Programs
Group:          System/Servers

%description	utils
This package provides some utility programs that come with the mod_bt
distribution:

 o btt_db2xml - Dump your BitTorrent Tracker database as an XML file
 o btt_xml2db - Restore an XML dump into a BitTorrent database
 o bt_showmetainfo  - Display information about a metainfo (.torrent) file.


%package -n	perl-Net-BitTorrent-LibBT-Tracker
Summary:	Access a tracker running under libbttracker
Group:          Development/Perl

%description -n	perl-Net-BitTorrent-LibBT-Tracker
The Net::BitTorrent::LibBT::Tracker module provides an interface to the
"libbttracker" Hash and Peer databases and the statistics stored in shared
memory.

%package -n	php-mod_bt
Summary:	PHP bindings for mod_bt
Group:          Development/PHP
Requires:	%{name} = %{version}-%{release}

%description -n	php-mod_bt
This package provides access to a BitTorrent tracker running mod_bt from a
PHP environment.

%package -n	%{libname}-devel
Summary:	Development library and header files for the %{libname} library
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	libmod_bt-devel = %{version}-%{release}

%description -n	%{libname}-devel
This package contains the static %{libname} library and its header
files.

%prep

%setup -q -n %{mod_name}-%{version}
%patch0 -p0

cp %{SOURCE1} %{mod_conf}

# fix attribs
find . -type f -perm 0444 -exec chmod 644 {} \;

# temporary hack
perl -pi -e "s|-Wall -Werror||g" configure

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

# fix bug
find src examples -type f | xargs perl -pi -e "s|Net::BitTorrent::LibBTT|Net::BitTorrent::LibBT::Tracker|g"

%build
#export WANT_AUTOCONF_2_5=1
#rm -f configure
#libtoolize --copy --force; aclocal-1.7; autoconf; automake-1.7 --add-missing --gnu
#autoreconf

#%%configure2_5x --localstatedir=/var/lib \
#    --with-apxs=%{_sbindir}/apxs \
#    --with-xml-prefix=%{_prefix} \
#    --with-bdb=%{_prefix} \
#    --with-apr=%{_bindir}/apr-1-config \
#    --with-makefilepl-args="INSTALLDIRS=vendor" \
#    --with-modperl=%{_prefix} \
#    --with-php-config=%{_bindir}/php-config \
#    --with-docdir=%{_docdir}/%{name}-%{version}

if [ -x %{_bindir}/apr-config ]; then APR=%{_bindir}/apr-config; fi
if [ -x %{_bindir}/apr-1-config ]; then APR=%{_bindir}/apr-1-config; fi

export CPPFLAGS=`$APR --cppflags`

./configure \
 	--prefix=%{_prefix} \
	--exec-prefix=%{_exec_prefix} \
	--bindir=%{_bindir} \
	--sbindir=%{_sbindir} \
	--sysconfdir=%{_sysconfdir} \
	--datadir=%{_datadir} \
	--includedir=%{_includedir} \
	--libdir=%{_libdir} \
	--libexecdir=%{_libexecdir} \
	--localstatedir=/var/lib \
	--sharedstatedir=%{_sharedstatedir} \
	--mandir=%{_mandir} \
	--infodir=%{_infodir} \
	--with-apxs=%{_sbindir}/apxs \
	--with-xml-prefix=%{_prefix} \
        --with-bdb=%{_prefix} \
        --with-apr=$APR \
        --with-makefilepl-args="INSTALLDIRS=vendor" \
        --with-modperl=%{_prefix} \
        --with-php-config=%{_bindir}/php-config

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_sysconfdir}/php.d

%makeinstall_std

install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

cat > %{buildroot}%{_sysconfdir}/php.d/A52_mod_bt.ini << EOF
extension = mod_bt.so
EOF

# fix docs
rm -rf html-docs
cp -rp htdocs html-docs
find html-docs -name "Makefile*"|xargs rm -f
find html-docs -name "MANIFEST"|xargs rm -f
find html-docs -name "*.in"|xargs rm -f
rm -f examples/MANIFEST

cp src/apache2/Apache2-ModBT/Changes Changes.Apache2-ModBT
cp src/apache2/Apache2-ModBT/README README.Apache2-ModBT
cp src/libbttracker/Net-BitTorrent-LibBT-Tracker/Changes Changes.Net-BitTorrent-LibBT-Tracker
cp src/libbttracker/Net-BitTorrent-LibBT-Tracker/README README.Net-BitTorrent-LibBT-Tracker

# fixup
mv %{buildroot}%{_includedir}/apache2 %{buildroot}%{_includedir}/apache
mv %{buildroot}%{_libdir}/apache %{buildroot}%{_libdir}/apache-extramodules
mv %{buildroot}%{_libdir}/php/extensions/php_mod_bt.so %{buildroot}%{_libdir}/php/extensions/mod_bt.so

# @PERL@
perl -pi -e "s|\@PERL\@|%{_bindir}/perl|g" examples/*

# cleanup
rm -f %{buildroot}%{_libdir}/php/extensions/*.a
rm -rf %{buildroot}%{_docdir}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog NEWS README examples etc/httpd.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/*mod_bt.conf
%attr(0755,root,root) %{_libdir}/apache-extramodules/mod_bt.so

%files -n %{libname}
%defattr(-,root,root)
%attr(0755,root,root) %{_libdir}/lib*.so.*

%files utils
%defattr(-,root,root)
%attr(0755,root,root) %{_bindir}/bt_showmetainfo
%attr(0755,root,root) %{_bindir}/btt_db2xml
%attr(0755,root,root) %{_bindir}/btt_xml2db
%attr(0755,root,root) %{_bindir}/btt_infohash
%attr(0644,root,root) %{_mandir}/man1/*
%attr(0644,root,root) %{_mandir}/man8/*

%files -n perl-Net-BitTorrent-LibBT-Tracker
%defattr(-,root,root)
%doc Changes.* README.*
%{perl_vendorarch}/Net/BitTorrent/LibBT/*.pm
%{perl_vendorarch}/Apache2/*.pm
%{perl_vendorarch}/Apache2/ModBT/*.pm
%{perl_vendorarch}/auto/Net/BitTorrent/LibBT/Tracker/*.so
%{perl_vendorarch}/auto/Net/BitTorrent/LibBT/Tracker/*.ix
%{perl_vendorarch}/auto/Apache2/ModBT/*.so
%attr(0644,root,root) %{_mandir}/man3/*

%files -n php-mod_bt
%defattr(-,root,root)
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/php.d/*.ini
%attr(0755,root,root) %{_libdir}/php/extensions/mod_bt.so

%files -n %{libname}-devel
%defattr(-,root,root)
%attr(0755,root,root) %{_libdir}/*.a
%attr(0644,root,root) %{_libdir}/*.la
%attr(0755,root,root) %{_libdir}/*.so
%dir %{_includedir}/libbttracker
%dir %{_includedir}/libbttracker/types
%{_includedir}/libbttracker/*.h
%{_includedir}/libbttracker/types/*.h
%{_includedir}/libbttracker.h
%dir %{_includedir}/libbtutil
%dir %{_includedir}/libbtutil/util
%dir %{_includedir}/libbtutil/types
%{_includedir}/libbtutil/*.h
%{_includedir}/libbtutil/util/*.h
%{_includedir}/libbtutil/types/*.h
%{_includedir}/libbtutil.h
%{_includedir}/apache/*.h
