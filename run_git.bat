@cls
@echo off
scons --clean
git init
git add --all
git commit -m "carpeta vacía"
git push -u origin master
pause