%{?filter_setup:
%filter_provides_in %{_datadir}/proton/examples/
%filter_requires_in %{_datadir}/proton/examples/
%filter_setup
}

%global proton_licensedir %{_licensedir}/proton
%{!?_licensedir:
%global license %doc
%global proton_licensedir %{_datadir}/proton}

Name:                qpid-proton
Version:             0.38.0
Release:             2
Summary:             A high performance and lightweight library for messaging applications
License:             ASL 2.0
URL:                 http://qpid.apache.org/proton/
Source0:             https://github.com/apache/qpid-proton/archive/%{version}.tar.gz
Patch0000:           proton.patch

BuildRequires:       gcc gcc-c++ cmake swig pkgconfig doxygen libuuid-devel openssl-devel
BuildRequires:       python3-devel python3-sphinx glibc-headers cyrus-sasl-devel jsoncpp-devel

%description
Proton is a high performance, lightweight messaging library. It can be used in
the widest range of messaging applications including brokers, client libraries,
routers, bridges, proxies, and more. Proton makes it trivial to integrate with
the AMQP 1.0 ecosystem from any platform, environment, or language.

%package   c-cpp
Summary:             C/C++ libs for qpid-proton
Requires:            cyrus-sasl-lib jsoncpp
Provides:            qpid-proton-c = %{version}-%{release} qpid-proton-cpp = %{version}-%{release}
Obsoletes:           qpid-proton perl-qpid-proton qpid-proton-c < %{version}-%{release}
Obsoletes:           qpid-proton-cpp < %{version}-%{release}

%description c-cpp
This package contains C/C++ libraries for qpid-proton.

%package c-cpp-devel
Summary:             Development C/C++ libs for qpid-proton
Requires:            qpid-proton-c-cpp = %{version}-%{release}
Provides:            qpid-proton-c-devel = %{version}-%{release} qpid-proton-cpp-devel = %{version}-%{release}
Obsoletes:           qpid-proton-devel qpid-proton-c-devel < %{version}-%{release}
Obsoletes:           qpid-proton-cpp-devel < %{version}-%{release}

%description c-cpp-devel
This package contains C/C++ development libraries for writing messaging apps with qpid-proton.


%package c-help
Summary:             Documentation for the C development libs
BuildArch:           noarch
Provides:            c-docs = %{version}-%{release}
Obsoletes:           qpid-proton-c-devel-doc qpid-proton-c-devel-docs c-docs < %{version}-%{release}

%description c-help
This package contains documentation for the C development libraries and examples for qpid-proton.

%package   cpp-help
Summary:             Documentation for the C++ development libs
BuildArch:           noarch
Provides:            cpp-docs = %{version}-%{release}
Obsoletes:           qpid-proton-cpp-devel-doc qpid-proton-cpp-devel-docs cpp-docs < %{version}-%{release}

%description cpp-help
This package contains documentation for the C++ development libraries and examples for qpid-proton.

%package -n python3-qpid-proton
Summary:             Python language bindings for the qpid-proton
%python_provide python3-qpid-proton
Requires:            qpid-proton-c = %{version}-%{release} python3

%description -n python3-qpid-proton
This package contains python language bindings for the qpid-proton messaging framework.

%package -n python-qpid-proton-help
Summary:             Documentation for the Python language bindings for qpid-proton
BuildArch:           noarch
Provides:            python-qpid-proton-docs = %{version}-%{release}
Obsoletes:           python-qpid-proton-doc python-qpid-proton-docs < %{version}-%{release}

%description -n python-qpid-proton-help
This package contains documentation for the Python language bindings for qpid-proton.

%package tests
Summary:             Tests for qpid-proton
BuildArch:           noarch

%description tests
This package contains some tests for qpid-proton.

%prep
%autosetup -n %{name}-%{version} -p1

%build
%if "%toolchain" == "clang"
	export CFLAGS="$CFLAGS -Wno-error=strict-prototypes -Wno-error=unused-but-set-variable"
	export CXXFLAGS="$CXXFLAGS -Wno-error=strict-prototypes -Wno-error=unused-but-set-variable"
	%ifarch riscv64
		sed -i '/LTO_Clang/d' %{_builddir}/%{name}-%{version}/CMakeLists.txt
	%endif
%endif
rm -rf buildpython3 && mkdir buildpython3
pushd buildpython3
python_includes=$(ls -d /usr/include/python3*)
%cmake \
    -DSYSINSTALL_BINDINGS=ON \
    -DCMAKE_SKIP_RPATH:BOOL=OFF \
    -DENABLE_FUZZ_TESTING=NO \
    "-DCMAKE_C_FLAGS=$CMAKE_C_FLAGS $CFLAGS -Wno-error=format-security" \
    "-DCMAKE_CXX_FLAGS=$CMAKE_CXX_FLAGS $CXXFLAGS -Wno-error=format-security" \
    ..
make all docs -j1
(pushd python/dist; %py3_build)

%install
pushd buildpython3
%make_install
(pushd python/dist; %py3_install)

find %{buildroot}%{_datadir}/proton/examples/python -name "*.py" -exec sed -i 's/!\/usr\/bin\/env python/!\/usr\/bin\/python3/' {} \;
echo '#!/usr/bin/python3' > %{buildroot}%{_datadir}/proton/examples/python/proton_server.py.original
cat %{buildroot}%{_datadir}/proton/examples/python/proton_server.py >> %{buildroot}%{_datadir}/proton/examples/python/proton_server.py.original
mv %{buildroot}%{_datadir}/proton/examples/python/proton_server.py.original %{buildroot}%{_datadir}/proton/examples/python/proton_server.py
chmod +x %{buildroot}%{python3_sitearch}/_cproton.so

rm -fr %{buildroot}%{_datadir}/proton/examples/**/*.cmake
rm -f  %{buildroot}%{_datadir}/proton/CMakeLists.txt
rm -fr %{buildroot}%{_datadir}/proton/examples/go
for fpath in %{buildroot}%{_libdir} %{buildroot}%{_datarootdir} \
        %{buildroot}%{_datadir}/proton/examples
do
    rm -rf ${fpath}/ruby
done

%check

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

%files c-cpp
%dir %{_datadir}/proton
%license %{_datadir}/proton/LICENSE.txt
%doc %{_datadir}/proton/README*
%{_libdir}/libqpid-proton*

%files c-cpp-devel
%{_includedir}/proton
%{_libdir}/cmake/Proton
%{_libdir}/pkgconfig/*
%{_libdir}/cmake/ProtonCpp

%files c-help
%defattr(-,root,root,-)
%license %{_datadir}/proton/LICENSE.txt
%doc %{_datadir}/proton/examples/README.md
%doc %{_datadir}/proton/docs/api-c
%doc %{_datadir}/proton/examples/c/*

%files cpp-help
%defattr(-,root,root,-)
%license %{_datadir}/proton/LICENSE.txt
%{_datadir}/proton/docs/api-cpp
%doc %{_datadir}/proton/examples/cpp/*

%files -n python3-qpid-proton
%{python3_sitearch}/*

%files -n python-qpid-proton-help
%defattr(-,root,root,-)
%license %{_datadir}/proton/LICENSE.txt
%doc %{_datadir}/proton/docs/api-py
%doc %{_datadir}/proton/examples/python

%files tests
%license %{_datadir}/proton/LICENSE.txt
%doc %{_datadir}/proton/tests

%changelog
* Thu May 18 2023 yoo <sunyuechi@iscas.ac.cn> - 0.38.0-2
- fix clang build error

* Tue Feb 07 2023 xu_ping <xuping33@h-partners.com> - 0.38.0-1
- Update to 0.38.0

* Tue Jul 13 2021 huangtianhua <huangtianhua@huawei.com> - 0.33.0-1
- Update to 0.33.0

* Tue Aug 10 2021 wangyue <wangyue92@huawei.com> - 0.31.0-2
- Patch for non-constant SIGSTKSZ

* Tue Jun 2 2020 leiju <leiju4@huawei.com> - 0.31.0-1
- Update to 0.31.0

* Wed Jan 8 2020 Senlin Xia<xiasenlin1@huawei.com> - 0.24.0-5
- Package init
