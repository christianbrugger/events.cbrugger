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
  git remote add originA https://$GH_TOKEN@github.com/christianbrugger/events.cbrugger.git
  git remote add originB https://$GH_TOKEN@github.com/christianbrugger/events.cbrugger.git > /dev/null 2>&1
  git remote add origin https://${GH_TOKEN}@github.com/christianbrugger/events.cbrugger.git > /dev/null 2>&1
  echo https://${GH_TOKEN}@github.com
  git remote -v
  git push --quiet --set-upstream origin master
}

setup_git
commit_website_files
upload_files
