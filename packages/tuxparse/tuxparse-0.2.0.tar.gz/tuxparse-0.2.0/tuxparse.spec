Name:      tuxparse
Version:   0.2.0
Release:   0%{?dist}
Summary:   FIXME
License:   FIXME
URL:       FIXME
Source0:   %{pypi_source}


BuildRequires: git
BuildRequires: make
BuildRequires: python3-devel
BuildRequires: python3-flit
BuildRequires: python3-pip
BuildRequires: python3-pytest
BuildRequires: python3-pytest-cov
BuildRequires: python3-pytest-mock
BuildRequires: python3-yaml

BuildArch: noarch

Requires: python3 >= 3.6
Requires: python3-yaml

%global debug_package %{nil}

%description
FIXME

%prep
%setup -q

%build
export FLIT_NO_NETWORK=1
make run
#make man
#make bash_completion

%check
python3 -m pytest test/

%install
mkdir -p %{buildroot}/usr/share/%{name}/
cp -r run %{dist} %{buildroot}/usr/share/%{name}/
mkdir -p %{buildroot}/usr/bin
ln -sf ../share/%{name}/run %{buildroot}/usr/bin/%{name}
#mkdir -p %{buildroot}%{_mandir}/man1
#install -m 644 %{name}.1 %{buildroot}%{_mandir}/man1/
#mkdir -p %{buildroot}/usr/share/bash-completion/completions/
#install -m 644 bash_completion/%{name} %{buildroot}/usr/share/bash-completion/completions/

%files
/usr/share/%{name}
%{_bindir}/%{name}
#%{_mandir}/man1/%{name}.1*
#/usr/share/bash-completion/completions/%{name}

%doc README.md
%license LICENSE

%changelog

* Wed Jun 22 2025 Your Name <your.name@domain.com> - 0.0.2-1
- Release 0.0.2
* Wed Mar 19 2025 Your Name <your.name@domain.com> - 0.0.0-1
- Initial version of the package
