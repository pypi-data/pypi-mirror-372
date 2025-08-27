# Fully automated

    $ ./release.sh patch

## Making an alpha release

    $ ./release.sh patch --new-version 0.8.0a1

# semi automated

To make a new release

```
# update src/pycafe_server/__about__.py
$ git add -u && git commit -m 'Release v0.8.0' && git tag v0.8.0 && git push upstream master v0.8.0
```

If a problem happens, and you want to keep the history clean

```
# drop the automatically created commits
$ git rebase -i HEAD~3
$ git tag v0.8.0 -f &&  git push upstream master v0.8.0 -f
```
