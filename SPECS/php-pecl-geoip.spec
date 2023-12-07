%define _debugsource_template %{nil}
%define debug_package %{nil}

%define pecl_name geoip
%global ini_name  40-%{pecl_name}.ini

Name:           php-pecl-geoip
Version:        1.1.1
Release:        17%{?dist}
Summary:        Extension to map IP addresses to geographic places
License:        PHP-3.01
URL:            https://pecl.php.net/package/%{pecl_name}
Source0:        https://pecl.php.net/get/%{pecl_name}-%{version}.tgz

# Upstream patches
# https://svn.php.net/viewvc?view=revision&revision=351082
Patch0:         %{pecl_name}-php8.patch
Patch1:         %{pecl_name}-php81.patch

BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  GeoIP-devel
BuildRequires:  php-devel
BuildRequires:  php-pear

Requires(post): %{__pecl}
Requires(postun): %{__pecl}

Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}

Provides:       php-%{pecl_name}               = %{version}
Provides:       php-%{pecl_name}%{?_isa}       = %{version}
Provides:       php-pecl(%{pecl_name})         = %{version}
Provides:       php-pecl(%{pecl_name})%{?_isa} = %{version}

%description
This PHP extension allows you to find the location of an IP address
City, State, Country, Longitude, Latitude, and other information as
all, such as ISP and connection type. It makes use of Maxminds geoip
database


%prep
%setup -c -q

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    -e '/LICENSE/s/role="doc"/role="src"/' \
    -i package.xml

cat > %{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF

cd %{pecl_name}-%{version}
%patch -P0 -p1 -b .php8
%patch -P1 -p1 -b .php81

# Upstream often forget this
extver=$(sed -n '/#define PHP_GEOIP_VERSION/{s/.* "//;s/".*$//;p}' php_geoip.h)
if test "x${extver}" != "x%{version}"; then
   : Error: Upstream version is ${extver}, expecting %{version}.
   exit 1
fi

%build
cd %{pecl_name}-%{version}
phpize
%configure --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

%install
make -C %{pecl_name}-%{version} install INSTALL_ROOT=%{buildroot} INSTALL="install -p"

# Install XML package description
install -Dpm 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# install config file
install -Dpm644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Documentation
cd %{pecl_name}-%{version}
for i in $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done

%check
cd %{pecl_name}-%{version}
: Minimal load test for NTS extension
%{__php} -n \
    -d extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    -m | grep %{pecl_name}

# Missing IPv6 data
rm tests/019.phpt

TEST_PHP_EXECUTABLE=%{__php} \
REPORT_EXIT_STATUS=1 \
NO_INTERACTION=1 \
%{__php} run-tests.php \
    -n -q \
    -d extension_dir=modules \
    -d extension=%{pecl_name}.so \
    --show-diff

%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi

%files
%license %{pecl_name}-%{version}/LICENSE
%doc %{pecl_docdir}/%{pecl_name}
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{name}.xml


%changelog
* Thu Oct 28 2021 Remi Collet <remi@remirepo.net> - 1.1.1-17
- rebuild for https://fedoraproject.org/wiki/Changes/php81
- add upstream patch for PHP 8.1

* Sat Feb  6 2021 Alexander Ursu <alexander.ursu@gmail.com> - 1.1.1-4
- Build for CentOS 8.3
- add upstream patch for PHP 8

* Sun Jun 28 2020 Alexander Ursu <alexander.ursu@gmail.com> - 1.1.1-3
- Build for CentOS 8.2

* Tue Aug  7 2018 Alexander Ursu <alexander.ursu@gmail.com> - 1.1.1-2
- Build for CentOS 6 and PHP 5.6

* Mon Nov 14 2016 Remi Collet <remi@fedoraproject.org> - 1.1.1-1
- update to 1.1.1

* Wed Jul 27 2016 Remi Collet <remi@fedoraproject.org> - 1.1.0-1
- update to 1.1.0 (beta)
- https://fedoraproject.org/wiki/Changes/php70
- cleanup spec

* Thu Feb 25 2016 Remi Collet <remi@fedoraproject.org> - 1.0.8-12
- drop scriptlets (replaced by file triggers in php-pear #1310546)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.8-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.8-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.8-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 19 2014 Remi Collet <rcollet@redhat.com> - 1.0.8-8
- rebuild for https://fedoraproject.org/wiki/Changes/Php56
- add numerical prefix to extension configuration file

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.8-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.8-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Mar 22 2013 Remi Collet <rcollet@redhat.com> - 1.0.8-5
- rebuild for http://fedoraproject.org/wiki/Features/Php55

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.8-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Oct 28 2012 Andrew Colin Kissa <andrew@topdog.za.net> - 1.0.8-3
- Fix php spec file macros

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jan 19 2012 Remi Collet <remi@fedoraproject.org> - 1.0.8-1
- update to 1.0.8 for php 5.4

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.7-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sat Oct 15 2011 Remi Collet <remi@fedoraproject.org> - 1.0.7-7
- fix segfault when build with latest GeoIP (#746417)
- run test suite during build
- add patch for tests, https://bugs.php.net/bug.php?id=59804
- add filter to avoid private-shared-object-provides geoip.so

* Fri Jul 15 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.0.7-6
- Fix bugzilla #715693

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.7-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Jul 12 2009 Remi Collet <Fedora@FamilleCollet.com> 1.0.7-3
- rebuild for new PHP 5.3.0 ABI (20090626)

* Mon Jun 22 2009 Andrew Colin Kissa <andrew@topdog.za.net> - 1.0.7-2
- Fix timestamps on installed files

* Sun Jun 14 2009 Andrew Colin Kissa <andrew@topdog.za.net> - 1.0.7-1
- Initial RPM package
