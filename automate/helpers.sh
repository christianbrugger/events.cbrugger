#!/bin/sh

# SOURCE: https://gist.github.com/willprice/e07efd73fb7f13f917ea

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
  git remote add origin-push https://${GH_TOKEN}@github.com/christianbrugger/events.cbrugger.git > /dev/null 2>&1
}

upload_files() {
  git push --quiet --set-upstream origin-push master > /dev/null 2>&1
}

