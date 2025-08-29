ARG IMG_REGISTRY="registry.ndp-systemes.fr"
ARG IMG_VERSION="12.0"
FROM $IMG_REGISTRY/odoo-cloud/container:$IMG_VERSION
WORKDIR $ADDONS_LOCAL_PROJECT
RUN ls -alh ./ && touch EXCLUDE

#RUN export ADDONS_GIT_CLOUD_MODULES="False" \
#    && python3 --version \
#    && pip3 --version \
#    && pip3 install -U pip \
#    && pip3 install --no-input --disable-pip-version-check --no-python-version-warning --verbose  $ADDONS_LOCAL_PROJECT
#
#RUN python3 -m unittest discover -s tests/tests_odoo -t $ADDONS_LOCAL_PROJECT
