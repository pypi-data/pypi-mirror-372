# Documentation technique fournit par `mkdocs`.
## Les tests
Dans votre virtual environement executer `python -m unittest discover` pour jouer la suite de test complete.

### Tests doctests

Certaines classes ou méthodes sont couvertes par des tests **doctes**, qui sont des tests inclus directement dans le docstring. Le fichier `test_doctests.py` sert de point d'entrée pour ces tests. +
Ces tests se lancent en faisant :

```sh
$ python tests tests/test_doctests.py
````

### Tests in Odoo
#### Lancer en local

```shell
# Avoir le virtualenv de la version d'activé
ODOO_VERSION=15.0 \ <1>
python -m unittest discover \ <2>
-s tests/tests_odoo \ <3>
-t ./ <4>
```
- 1 Set la variable `ODOO_VERSION` à la version voulu
- 2 Lance les tests
- 3 Precise où sont les tests, pour ne pas lancer les tests simple
- 4 Force le path au niveau de `./`, pour éviter que python oubli les top level package et avoir des soucis d'import

#### Lancer avec une image docker


```shell
docker run \ <1>
--mount type=bind,source="$(pwd)",target=/builds/oenv2config \ <2>
--entrypoint "/builds/oenv2config/in_docker_test.sh" \ <3>
--workdir=/builds/oenv2config \ <4>
--rm \ <5>
-t registry.ndp-systemes.fr/odoo-cloud/container:15.0 <6>
```
- 1 Run une image docker
- 2 Créer un volume du path local `pwd` vers `/builds/oenv2config` dans le container
- 3 Change l'entrypoint, pour ne pas lancer Odoo, mais lancer `in_docker_test.sh`
- 4 Set le `workdir` au point de montage, pour que lors de l'exécution de l'entrypoint, nous sommes dans le bon path
- 5 Supprime le container apres le run
- 6 l'image docker, ici la v15

.Sans commentaire
```shell
docker run \
--mount type=bind,source="$(pwd)",target=/builds/oenv2config \
--entrypoint "/builds/oenv2config/in_docker_test.sh" \
--workdir=/builds/oenv2config \
--rm \
-t registry.ndp-systemes.fr/odoo-cloud/container:15.0
```

Il existe des décorateurs particuliers pour ne jouer les tests que dans un environment Odoo.

Pour les Utiliser if faut les importer dans votre fichier de tests, et ensuite décorer votre fonction avec.

## `src` et `src/odoo_env_config`
Contient le code source du projet, voir la partie code

## Fichier de configuration
### `.gitlab-ci.yml`
Fichier de configuration pour lancer le ci de GitLab. Voir [sur GitLab](https://gitlab.ndp-systemes.fr/python-libs/odoo-libs/-/ci/editor?branch_name=main&tab=1)

### `pyproject.toml`
Cette lib est disponible sur le pypi interne de ndp.
Vous pouvez l'installer soit depuis le code source avec `pip install .` ou depuis le pypi de ndp avec la commande suivante.
`pip install --index-url https://gl-token:$GITLAB_TOKEN@gitlab.example.com/api/v4/projects/377/packages/pypi/simple --no-deps openv2config`

### `mkdocs.yml`
Fichier de configuration pour la documentation technique

### `.local-antora.playbook.yml`
Fichier de configuration pour lancer la documentation fonctionnel de ce projet via `antora`

### `.pre-commit-config.yml`
Lance les tests `lint` avec les commits

## Lancer la documentation `mkdocs` en locale
Pour lancer cette documentation sur votre poste local, vous devez

```shell
pip install -e .
pip install -r ./docs/mkdocs/requirements.txt
mkdocks server
```

## Lancer la documentation `antora` en locales
La documentation `antora` est une documentation plus fonctionnelle de ce projet.
Elle automatiquement inclut dans le projet la documentation generale de NDP [Atlas](https://atlas.docs.ndp-systemes.fr/general) ([Lien direct](https://atlas.docs.ndp-systemes.fr/general/ci-runbot/latest/index.html).

Il est possible de la builder modifier et de voir son rendu en locale.
Voir la section d'installation d'`antora` [ici](https://atlas.docs.ndp-systemes.fr/general/antora/main/readme.html)

```shell
antora .local-antora-playbook.yml --stacktrace &&  npx http-server build/site -c-1 -p 5000
```
