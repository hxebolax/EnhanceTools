@cls
@echo off
echo Creando complemento...
scons --clean
scons
scons pot
EnhanceTools-1.2.nvda-addon