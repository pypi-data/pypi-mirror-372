docker pull registry.ndp-systemes.fr/odoo-cloud/container:$1
docker build . -t local/oenv2config:$1 --build-arg=IMG_VERSION=$1 --progress=plain --no-cache
