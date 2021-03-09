Name:           bill-calculator
Version:        __VERSION__
Release:        __RELEASE__
Summary:        Calculate and alarms on costs and balance for AWS

Group:          Applications/System
License:        Fermitools Software Legal Information (Modified BSD License)
URL:            https://fermipoint.fnal.gov/project/fnalhcf/SitePages/Home.aspx
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-XXXXXX)

BuildArch:      noarch

%description
Calculate and alarms on costs and balance for AWS

%prep
%setup -q


%build


%install
# copy the files into place
mkdir -p $RPM_BUILD_ROOT/opt/bill-calculator
cp -r ./ $RPM_BUILD_ROOT/opt/bill-calculator


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc /opt/bill-calculator/doc/installation-instructions.txt 
/opt/bill-calculator/bin/AccountConstants.py
/opt/bill-calculator/bin/billAlarms.py
/opt/bill-calculator/bin/billAnalysis.py
/opt/bill-calculator/bin/billAlarmsGCE.py
/opt/bill-calculator/bin/billAnalysisGCE.py
/opt/bill-calculator/bin/billDataEgress.py
/opt/bill-calculator/bin/graphite.py
/opt/bill-calculator/bin/ServiceDeskProxy.py
/opt/bill-calculator/bin/ServiceNowConstants.py
/opt/bill-calculator/bin/ServiceNowHandler.py
//opt/bill-calculator/bin/submitAlarm.py
/opt/bill-calculator/clients/analyzeCMSRunAnalysis.py
/opt/bill-calculator/clients/analyzeCMSRunAnalysis.pyc
/opt/bill-calculator/clients/analyzeCMSRunAnalysis.pyo

%changelog
