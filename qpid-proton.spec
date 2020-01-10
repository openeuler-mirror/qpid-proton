%{?filter_setup:
%filter_provides_in %{_datadir}/proton-%{version}/examples/
%filter_requires_in %{_datadir}/proton-%{version}/examples/
%filter_setup
}

%global pythonx python2
%{!?__python2:
%global __python2 %{__python}
%global python2_sitearch %{python_sitearch}
%global pythonx python
}

%global proton_licensedir %{_licensedir}/proton-%{version}
%{!?_licensedir:
%global license %doc
%global proton_licensedir %{_datadir}/proton-%{version}
}

Name:           qpid-proton
Version:        0.24.0
Release:        5
Summary:        A high-performance and lightweight library for messaging applications
License:        ASL 2.0
URL:            http://qpid.apache.org/proton/
Source0:        https://github.com/apache/qpid-proton/archive/0.24.0.tar.gz
BuildRequires:  gcc-c++ cmake swig pkgconfig doxygen libuuid-devel
BuildRequires:  openssl-devel %{pythonx}-devel python3-devel epydoc
BuildRequires:  glibc-headers cyrus-sasl-devel

%description
qpid-proton is a high-performance, lightweight messaging library. It can be used
in the widest range of messaging applications, including brokers, client libraries,
routers, bridges, proxies, and more. Proton makes it trivial to integrate with the
AMQP 1.0 ecosystem from any platform, environment, or language.

%package c-cpp
Summary:        C/C++ libs for qpid-proton
Requires:       cyrus-sasl-lib
Provides:       qpid-proton-c = %{version}-%{release} qpid-proton-cpp = %{version}-%{release}
Obsoletes:      qpid-proton perl-qpid-proton qpid-proton-c < %{version}-%{release}
Obsoletes:      qpid-proton-cpp < %{version}-%{release}

%description c-cpp
This package contains C/C++ libraries for qpid-proton.



%package c-cpp-devel
Requires:       qpid-proton-c-cpp = %{version}-%{release}
Summary:        Development C/C++ libs for qpid-proton
Provides:       qpid-proton-c-devel = %{version}-%{release} qpid-proton-cpp-devel = %{version}-%{release}
Obsoletes:      qpid-proton-devel qpid-proton-c-devel < %{version}-%{release}
Obsoletes:      qpid-proton-cpp-devel < %{version}-%{release}

%description c-cpp-devel
This package contains development C/C++ libraries for writing messaging apps with qpid-proton.



%package c-help
Summary:        Documentation for the C development libs
BuildArch:      noarch
Provides:       c-docs = %{version}-%{release}
Obsoletes:      qpid-proton-c-devel-doc qpid-proton-c-devel-docs c-docs < %{version}-%{release}

%description c-help
This package contains documentation for the C development libraries and examples for qpid-proton.


%package   cpp-help
Summary:        Documentation for the C++ development libs
BuildArch:      noarch
Provides:       cpp-docs = %{version}-%{release}
Obsoletes:      qpid-proton-cpp-devel-doc qpid-proton-cpp-devel-docs cpp-docs < %{version}-%{release}

%description cpp-help
This package contains documentation for the C++ development libraries for qpid-proton.

%package -n %{pythonx}-qpid-proton
Summary:  Python language bindings for qpid-proton
%python_provide python2-qpid-proton
Requires: qpid-proton-c = %{version}-%{release} %{pythonx}

%description -n %{pythonx}-qpid-proton
This package contains python language bindings for the qpid-proton messaging framework.



%package -n python3-qpid-proton
Summary:  Python language bindings for qpid-proton
%python_provide python3-qpid-proton
Requires: qpid-proton-c = %{version}-%{release} python3

%description -n python3-qpid-proton
This package contains python language bindings for the qpid-proton messaging framework.


%package -n python-qpid-proton-help
Summary:        Documentation for the Python language bindings for qpid-proton
BuildArch:      noarch
Provides:       python-qpid-proton-docs = %{version}-%{release}
Obsoletes:      python-qpid-proton-doc python-qpid-proton-docs < %{version}-%{release}


%description -n python-qpid-proton-help
This package constains documentation for the Python language bindings for qpid-proton.


%prep
%autosetup -n %{name}-%{version} -p1


%build
rm -rf buildpython2 && mkdir buildpython2
rm -rf buildpython3 && mkdir buildpython3

pushd buildpython2
%cmake \
       -DCMAKE_EXE_LINKER_FLAGS="-Wl,-z,relro,-z,now" \
       -DCMAKE_SHARED_LINKER_FLAGS="-Wl,-z,relro" \
       -DCMAKE_MODULE_LINKER_FLAGS="-Wl,-z,relro" -DSYSINSTALL_BINDINGS=ON \
       -DCMAKE_SKIP_RPATH:BOOL=OFF -DENABLE_FUZZ_TESTING=NO \
       ..

export ADDCFLAGS=" -Wno-error=return-type"
%cmake \
    -DSYSINSTALL_BINDINGS=ON -DCMAKE_SKIP_RPATH:BOOL=OFF \
    -DENABLE_FUZZ_TESTING=NO "-DCMAKE_C_FLAGS=$CMAKE_C_FLAGS $CFLAGS $ADDCFLAGS" \
     -DCYRUS_SASL_INCLUDE_DIR=/usr/include -DPYTHON_EXECUTABLE=/usr/bin/python2.7 \
     -DPYTHON_INCLUDE_DIR=/usr/include/python2.7/ "-DPYTHON_LIBRARY=%{_libdir}/libpython2.7.so" \
    ..

make all docs -j1
(pushd python/dist; %py2_build)
pushd ..

pushd buildpython3
python_includes=$(ls -d /usr/include/python3*)
%cmake \
    -DSYSINSTALL_BINDINGS=ON -DCMAKE_SKIP_RPATH:BOOL=OFF \
    -DENABLE_FUZZ_TESTING=NO "-DCMAKE_C_FLAGS=$CMAKE_C_FLAGS $CFLAGS $ADDCFLAGS" \
     -DCYRUS_SASL_INCLUDE_DIR=/usr/include -DPYTHON_EXECUTABLE=/usr/bin/python3 \
    "-DPYTHON_INCLUDE_DIR=$python_includes" "-DPYTHON_LIBRARY=%{_libdir}/libpython3.so" \
    ..

make all docs -j1
(pushd python/dist; %py3_build)


%install
pushd buildpython2
%make_install
(pushd python/dist; %py2_install)

pushd ../buildpython3
%make_install
(pushd python/dist; %py3_install)

chmod +x %{buildroot}%{python2_sitearch}/_cproton.so
chmod +x %{buildroot}%{python3_sitearch}/_cproton.so

rm -fr %{buildroot}%{proton_datadir}/examples/**/*.cmake
rm -fr %{buildroot}%{proton_datadir}/examples/go
for fpath in %{buildroot}%{_libdir} %{buildroot}%{_datarootdir} \
        %{buildroot}%{proton_datadir}/examples
do
    rm -rf ${fpath}/ruby
done



%check


%post
/sbin/ldconfig

%postun
/sbin/ldconfig


%files c-cpp
%dir %{_datadir}/proton-%{version}
%license %{_datadir}/proton-%{version}/LICENSE.txt
%doc %{_datadir}/proton-%{version}/README.md
%{_libdir}/libqpid-proton*

%files c-cpp-devel
%{_includedir}/proton
%{_libdir}/cmake/Proton
%{_libdir}/cmake/ProtonCpp
%{_libdir}/pkgconfig/*


%files c-help
%defattr(-,root,root,-)
%license %{_datadir}/proton-%{version}/LICENSE.txt
%doc %{_datadir}/proton-%{version}/docs/api-c
%doc %{_datadir}/proton-%{version}/examples/c/*


%files cpp-help
%defattr(-,root,root,-)
%license %{_datadir}/proton-%{version}/LICENSE.txt
%{_datadir}/proton-%{version}/docs/api-cpp
%doc %{_datadir}/proton-%{version}/examples/cpp/*

%files -n %{pythonx}-qpid-proton
%defattr(-,root,root,-)
%license %{_datadir}/proton-%{version}/LICENSE.txt
%{python2_sitearch}/*

%files -n python3-qpid-proton
%{python3_sitearch}/*

%files -n python-qpid-proton-help
%defattr(-,root,root,-)
%license %{_datadir}/proton-%{version}/LICENSE.txt
%doc %{_datadir}/proton-%{version}/docs/api-py
%doc %{_datadir}/proton-%{version}/examples/python


%changelog
* Wed Jan 8 2020 Senlin Xia<xiasenlin1@huawei.com> - 0.24.0-5
- Package init
