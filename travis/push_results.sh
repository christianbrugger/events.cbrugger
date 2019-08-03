#!/bin/sh

# SOURCE: https://gist.github.com/willprice/e07efd73fb7f13f917ea

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

commit_website_files() {
  git add test.txt
  git commit --message "Travis build: $TRAVIS_BUILD_NUMBER"
}

upload_files() {
  git remote add origin-push https://${GH_TOKEN}@github.com/christianbrugger/events.cbrugger.git > /dev/null 2>&1
  git push --quiet --set-upstream origin-push master
}

setup_git
commit_website_files
upload_files
