# Make a release

Panoramax API uses [semantic versioning](https://semver.org/) for its release numbers.

Run these commands in order to issue a new release:

```bash
git checkout develop

vim ./geovisio/__init__.py	# Change __version__

vim CHANGELOG.md	# Replace unreleased to version number

git add *
git commit -m "Release x.x.x"
git tag -a x.x.x -m "Release x.x.x"
git push origin develop
git checkout main
git merge develop
git push origin main --tags
```
