#!/usr/bin/env bash
cd out
git status
git branch
ls -aslh
echo $GH_REF
echo $PWD
git push --force --quiet "https://${GH_TOKEN}@${GH_REF}" master:gh-pages
echo -e "Deploy completed\n";
