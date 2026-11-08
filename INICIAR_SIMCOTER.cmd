@echo off
setlocal
cd /d "%~dp0"
title SIMCOTER - Instalacao e execucao local
echo ===========================================================
echo              SIMCOTER - INICIO LOCAL
echo ===========================================================
echo.
echo Somente para o computador local. Nao exponha a LAN/internet.
echo Verificando os pre-requisitos...
where py >nul 2>nul
if errorlevel 1 (
  echo ERRO: Python com inicializador "py" nao foi encontrado.
  echo Instale Python 3.11 ou posterior e reinicie o terminal.
  goto :failed
)
where npm >nul 2>nul
if errorlevel 1 (
  echo ERRO: Node.js e npm nao foram encontrados.
  echo Instale Node.js LTS e reinicie o terminal.
  goto :failed
)
if not exist ".venv\Scripts\python.exe" (
  py -m venv .venv
  if errorlevel 1 goto :failed
)
".venv\Scripts\python.exe" -m pip install -e ".[test]"
if errorlevel 1 goto :failed
pushd frontend
call npm install
if errorlevel 1 (
  popd
  goto :failed
)
call npm run build
if errorlevel 1 (
  popd
  goto :failed
)
popd
echo.
echo A aplicacao sera disponibilizada em http://127.0.0.1:8000
echo Deixe esta janela aberta durante o uso do jogo.
echo.
".venv\Scripts\python.exe" scripts\start_local.py
if errorlevel 1 goto :failed
exit /b 0
:failed
echo.
echo A inicializacao falhou. Consulte docs\INSTALACAO_COMPUTADOR.md
pause
exit /b 1
