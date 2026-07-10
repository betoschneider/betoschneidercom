#!/bin/sh
set -e

# Ajusta permissões dos arquivos montados via volume
# (roda como root no entrypoint, depois desce para appuser)
if [ -f /app/projects.db ]; then
    chown appuser:appuser /app/projects.db
fi
if [ -f /app/projects.db.bak ]; then
    chown appuser:appuser /app/projects.db.bak
fi

# Desce para appuser e executa o CMD
# $* concatena todos os argumentos em uma string unica para o -c
exec su -s /bin/sh -c "exec $*" appuser
