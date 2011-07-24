%define archivever 1_2_1

Name:          axis
Version:       1.2.1
Release:       7.2%{?dist}
Epoch:         0
Summary:       A SOAP implementation in Java
License:       ASL 2.0
Group:         Development/Libraries
URL:           http://ws.apache.org/%{name}/
Source0:       http://archive.apache.org/dist/ws/axis/1_2_1/axis-src-1_2_1.tar.gz
Patch1:        %{name}-bz152255.patch
Patch2:        %{name}-imageio.patch
Patch3:        %{name}-objectweb.patch
Patch4:        %{name}-%{version}-DH.patch
Patch5:        %{name}-build_xml.patch
Patch6:        %{name}-java16.patch
BuildRequires: jpackage-utils >= 0:1.5
BuildRequires: java-devel
BuildRequires: ant >= 0:1.6, ant-nodeps
# Mandatory requires
BuildRequires: jaf
BuildRequires: jakarta-commons-discovery
BuildRequires: jakarta-commons-httpclient
BuildRequires: jakarta-commons-logging
BuildRequires: javamail
BuildRequires: jaxp_parser_impl
BuildRequires: log4j
BuildRequires: apache-tomcat-apis
BuildRequires: wsdl4j
# optional requires
BuildRequires: jsse
BuildRequires: junit
BuildRequires: oro
BuildRequires: jms
BuildRequires: castor
#BuildRequires: xml-security

Requires:      java
Requires:      jpackage-utils >= 0:1.5
Requires:      jaf
Requires:      jakarta-commons-discovery
Requires:      jakarta-commons-logging
Requires:      jakarta-commons-httpclient
Requires:      javamail
Requires:      jaxp_parser_impl
Requires:      log4j
Requires:      wsdl4j

BuildArch:     noarch
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Apache AXIS is an implementation of the SOAP ("Simple Object Access Protocol")
submission to W3C.

From the draft W3C specification:

SOAP is a lightweight protocol for exchange of information in a decentralized,
distributed environment. It is an XML based protocol that consists of three
parts: an envelope that defines a framework for describing what is in a message
and how to process it, a set of encoding rules for expressing instances of
application-defined datatypes, and a convention for representing remote
procedure calls and responses.

This project is a follow-on to the Apache SOAP project.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Documentation

%description javadoc
Javadoc for %{name}.

%package manual
Summary:        Manual for %{name}
Group:          Documentation

%description manual
Documentation for %{name}.

%prep
%setup -q -n %{name}-%{archivever}
%patch1 -p1 -b .orig
%patch2 -p1 -b .orig
%patch3 -p1 -b .orig
%patch4
%patch5
%patch6 -b .orig

# Remove provided binaries
find . -name "*.jar" -exec rm -f {} \;
find . -name "*.zip" -exec rm -f {} \;
find . -name "*.class" -exec rm -f {} \;

# Fix for wrong-file-end-of-line-encoding problem
for i in `find docs -iname "*.html"`; do %{__sed} -i 's/\r//' $i; done
for i in `find docs -iname "*.css"`; do %{__sed} -i 's/\r//' $i; done
for i in `find docs -iname "*.bib"`; do %{__sed} -i 's/\r//' $i; done
%{__sed} -i 's/\r//' README
%{__sed} -i 's/\r//' LICENSE
%{__sed} -i 's/\r//' docs/docbook/testing-again.dbk
%{__sed} -i 's/\r//' release-notes.html
%{__sed} -i 's/\r//' changelog.html

%build

[ -z "$JAVA_HOME" ] && export JAVA_HOME=%{_jvmdir}/java

CLASSPATH=$(build-classpath wsdl4j jakarta-commons-discovery jakarta-commons-httpclient jakarta-commons-logging log4j jaf javamail/mailapi apache-tomcat-apis/tomcat-servlet2.4-api)
export CLASSPATH=$CLASSPATH:$(build-classpath oro junit jimi xml-security jsse httpunit jms castor 2>/dev/null)

export OPT_JAR_LIST="ant/ant-nodeps"
ant -Dcompile.ime=true \
    -Dwsdl4j.jar=$(build-classpath wsdl4j) \
    -Dcommons-discovery.jar=$(build-classpath jakarta-commons-discovery) \
    -Dcommons-logging.jar=$(build-classpath jakarta-commons-logging) \
    -Dcommons-httpclient.jar=$(build-classpath jakarta-commons-httpclient) \
    -Dlog4j-core.jar=$(build-classpath log4j) \
    -Dactivation.jar=$(build-classpath jaf) \
    -Dmailapi.jar=$(build-classpath javamail/mailapi) \
    -Dxerces.jar=$(build-classpath jaxp_parser_impl) \
    -Dservlet.jar=$(build-classpath apache-tomcat-apis/tomcat-servlet2.4-api) \
    -Dregexp.jar=$(build-classpath oro 2>/dev/null) \
    -Djunit.jar=$(build-classpath junit 2>/dev/null) \
    -Djimi.jar=$(build-classpath jimi 2>/dev/null) \
    -Djsse.jar=$(build-classpath jsse/jsse 2>/dev/null) \
    -Dsource=1.4 \
    clean compile javadocs

%install
rm -rf $RPM_BUILD_ROOT

### Jar files

install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/%{name}

pushd build/lib
   install -m 644 axis.jar axis-ant.jar saaj.jar jaxrpc.jar \
           $RPM_BUILD_ROOT%{_javadir}/%{name}
popd

pushd $RPM_BUILD_ROOT%{_javadir}/%{name}
   for jar in *.jar ; do
      vjar=$(echo $jar | sed s+.jar+-%{version}.jar+g)
      mv $jar $vjar
      ln -fs $vjar $jar
   done
popd

### Javadoc

install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr build/javadocs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

pushd docs
   rm -fr apiDocs
   ln -fs %{_javadocdir}/%{name}-%{version} apiDocs
popd

ln -sf %{_javadocdir}/%{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644,root,root,0755)
%doc LICENSE README release-notes.html changelog.html
%dir %{_javadir}/%{name}
%{_javadir}/%{name}/*.jar

%files javadoc
%defattr(0644,root,root,0755)
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*
%{_javadocdir}/%{name}

%files manual
%defattr(0644,root,root,0755)
%doc docs/*

%changelog
* Tue Feb 9 2010 Alexander Kurtakov <akurtako@redhat.com> 0:1.2.1-7.2
- Use apache-tomcat-apis instead of tomcat5-*.

* Sat Jan 9 2010 Alexander Kurtakov <akurtako@redhat.com> 0:1.2.1-7.1
- Drop gcj support.

* Fri Sep 25 2009 Dan Horak <dan[at]danny.cz> 0:1.2.1-7
- Backport fix for building with java 1.6, synced from F-11 branch (#511480, #523203)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2.1-6.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.2.1-5.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Oct 01 2008 Permaine Cheung <pcheung@redhat.com> 0:1.2.1-4.1
- Specify source=1.4 for javac

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> 0:1.2.1-4
- drop repotag
- fix license tag

* Thu Jun 05 2008 Permaine Cheung <pcheung@redhat.com> 0:1.2.1-3jpp.9
- Add javac.source=1.4 to the ant command for the build

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:1.2.1-3jpp.8
- Autorebuild for GCC 4.3

* Thu Apr 19 2007 Permaine Cheung <pcheung@redhat.com> 0:1.2.1-2jpp.8
- Rebuild

* Wed Apr 04 2007 Permaine Cheung <pcheung@redhat.com> 0:1.2.1-2jpp.7
- Fix building javadoc
- rpmlint cleanup

* Thu Aug 03 2006 Deepak Bhole <dbhole@redhat.com> 0:1.2.1-2jpp.6
- Added missing requirements

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 0:1.2.1-2jpp_5fc
- Rebuilt

* Wed Jul 19 2006 Deepak Bhole <dbhole@redhat.com> - 0:1.2.1-2jpp_4fc
- Added conditional native compilation.

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0:1.2.1-2jpp_3fc
- rebuild

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 0:1.2.1-2jpp_2fc
- stop scriptlet spew

* Wed Mar  1 2006 Archit Shah <ashah@redhat.com> 0:1.2.1-2jpp_1fc
- remove unnecessary build dependencies on jacorb and jonathan-rmi
- include fix to Axis bug 2142
- merge from upstream 2jpp

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Tue Jun 21 2005 Gary Benson <gbenson@redhat.com> 0:1.2.1-1jpp_1fc
- Upgrade to 1.2.1-1jpp.

* Fri Jun 17 2005 Fernando Nasser <fnasser@redhat.com> 0:1.2.1-1jpp
- Upgrade to 1.2.1 maintenance release

* Fri Jun 17 2005 Gary Benson <gbenson@redhat.com> 0:1.2-1jpp_1fc
- Work around file descripter leak (#160802).
- Build into Fedora.

* Mon Jun 13 2005 Gary Benson <gbenson@redhat.com>
- Add ObjectWeb's patch.

* Fri Jun 10 2005 Gary Benson <gbenson@redhat.com>
- Remove jarfiles from the tarball.

* Tue Jun  7 2005 Gary Benson <gbenson@redhat.com>
- Add DOM3 stubs to classes that need them (#152255).
- Avoid some API holes in libgcj's ImageIO implementation.
- Pick up CORBA and javax.rmi classes from jacorb and jonathan-rmi.

* Wed May 04 2005 Fernando Nasser <fnasser@redhat.com> 0:1.2-1jpp_1rh
- Merge with upstream for upgrade

* Wed May 04 2005 Fernando Nasser <fnasser@redhat.com> 0:1.2-1jpp
- Finaly 1.2 final release

* Sat Mar 12 2005 Ralph Apel <r.apel at r-apel.de>  0:1.2-0.rc2.3jpp
- Also Buildrequire ant-nodeps

* Fri Mar 11 2005 Ralph Apel <r.apel at r-apel.de>  0:1.2-0.rc2.2jpp
- Set OPT_JAR_LIST to "ant/ant-nodeps"
- Buildrequire ant >= 1.6

* Mon Feb 28 2005 Fernando Nasser <fnasser@redhat.com> 0:1.2-0.rc2.1jpp
- Upgrade to 1.2.rc2

* Fri Aug 20 2004 Ralph Apel <r.apel at r-apel.de>  0:1.1-3jpp
- Build with ant-1.6.2

* Thu Jun 26 2003 Nicolas Mailhot <Nicolas.Mailhot at laPoste.net>  0:1.1-2jpp
- fix javadoc versionning

* Thu Jun 26 2003 Nicolas Mailhot <Nicolas.Mailhot at laPoste.net>  0:1.1-1jpp
- Initial packaging
- no xml security for now since xml-security is not packaged yet
- functional tests not executed yet - seems they need some setup and do not
  run out of the box
- no webapp right now - file layout is too messy if hidden into a war file
  since jpp installs webapps expanded, this matters
