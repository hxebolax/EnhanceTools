@cls
@echo off
echo Creando complemento...
scons --clean
scons
scons pot
EnhanceTools-1.1.nvda-addon