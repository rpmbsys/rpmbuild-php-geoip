ARG centos=7
ARG image=php-7.1

FROM aursu/pearbuild:${centos}-${image}

# PHP 7.3 build image based on pcre2-devel
RUN yum -y install \
        GeoIP-devel \
    && yum clean all && rm -rf /var/cache/yum /var/cache/dnf

COPY SOURCES ${BUILD_TOPDIR}/SOURCES
COPY SPECS ${BUILD_TOPDIR}/SPECS

RUN chown -R $BUILD_USER ${BUILD_TOPDIR}/{SOURCES,SPECS}

USER $BUILD_USER

ENTRYPOINT ["/usr/bin/rpmbuild", "php-pecl-geoip.spec"]
CMD ["-ba"]
