# Comandos para crear repos en GitHub y hacer push
# Ejecutar en tu terminal (donde tienes acceso al GNOME Keyring)
# Reemplaza TU_PAT por tu Personal Access Token de GitHub

export GITHUB_PAT="TU_PAT_AQUI"
export GITHUB_USER="Pueblac"

# ─── 1. Crear repo BitacoraExpress en GitHub ────────────────────────────────
curl -s -X POST \
  -H "Authorization: token $GITHUB_PAT" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "BitacoraExpress",
    "description": "Tracker de actividades y tiempo por proyecto — ecosistema Express",
    "private": false,
    "auto_init": false
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('Repo URL:', d.get('html_url', d.get('message','ERROR')))"

# ─── 2. Cambiar el remote origin de BitacoraExpress ──────────────────────────
cd /home/pueblac/AndroidStudioProjects/BitacoraExpress
git remote set-url origin https://$GITHUB_USER:$GITHUB_PAT@github.com/$GITHUB_USER/BitacoraExpress.git
git push -u origin desarrollo

# ─── 3. Crear repo NexoExpress en GitHub ────────────────────────────────────
curl -s -X POST \
  -H "Authorization: token $GITHUB_PAT" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "NexoExpress",
    "description": "Coordinador del ecosistema Express — schemas, skills y documentación",
    "private": false,
    "auto_init": false
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('Repo URL:', d.get('html_url', d.get('message','ERROR')))"

# ─── 4. Conectar NexoExpress al repo y hacer push ───────────────────────────
cd /home/pueblac/AndroidStudioProjects/NexoExpress
git remote add origin https://$GITHUB_USER:$GITHUB_PAT@github.com/$GITHUB_USER/NexoExpress.git
git branch -m master main
git push -u origin main
