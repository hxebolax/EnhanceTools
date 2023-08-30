@cls
@echo off
scons --clean
git init
git add --all
git commit -m "1.2"
git push -u origin master
pause