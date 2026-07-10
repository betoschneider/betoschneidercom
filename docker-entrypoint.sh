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
if [ -d /app/data ]; then
    chown -R appuser:appuser /app/data
fi

# Desce para appuser e executa o CMD
exec su appuser -s /bin/sh -c "exec $@"
