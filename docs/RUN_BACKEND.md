# Comandos para correr el backend

Documento rapido de referencia para levantar la API.
El puerto local por defecto es **8001** (el 8000 esta reservado para otro programa).

---

## 1. Despliegue en Render (produccion)

**URL publica:** `https://back-despliegue-cp05.onrender.com`

El deploy se dispara automaticamente al hacer `git push` a `main`.
`despliegue/start.sh` corre, en orden:

1. `alembic upgrade head` — aplica todas las migraciones pendientes.
2. `python -m SETT.run_all` — siembra datos si `SEED_ON_STARTUP=true`.
3. `gunicorn` con worker `uvicorn` en `0.0.0.0:$PORT` (Render inyecta el puerto).

**Variables de entorno requeridas en Render** (Dashboard -> Environment):

| Variable | Valor |
| --- | --- |
| `DATABASE_URL` | URL postgres de Render |
| `SECRET_KEY` | string aleatorio largo |
| `SEED_ON_STARTUP` | `true` (devel) o `false` (produccion congelada) |
| `CLOUDINARY_*` | credenciales Cloudinary |
| `GEMINI_API_KEY` | clave de Google Gemini |
| `STRIPE_SECRET_KEY` | `sk_test_...` (modo test) |
| `DEBUG` | `false` |
| `AUTO_CREATE_TABLES` | `false` |

Para verificar healthcheck:

```powershell
curl https://back-despliegue-cp05.onrender.com/health
```

---

## 2. Backend local (puerto 8001)

### 2.1 Prerequisitos (una sola vez)

```powershell
cd "C:/Users/Isael Ortiz/Documents/yary/Backend"
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2.2 Variables de entorno locales

Crear `.env` (ya existe). Asegurate de que `DATABASE_URL` apunte a tu
PostgreSQL local:

```
DATABASE_URL=postgresql://postgres:12345678@localhost:5432/emergencias_vehiculares
```

### 2.3 Aplicar migraciones

```powershell
cd "C:/Users/Isael Ortiz/Documents/yary/Backend"
venv\Scripts\Activate.ps1
python -m alembic upgrade head
```

### 2.4 Sembrar datos (opcional)

```powershell
python -m SETT.run_all
```

### 2.5 Arrancar la API en el puerto 8001

**Opcion A — directo con uvicorn (recomendado para desarrollo, recarga al guardar):**

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Opcion B — via main.py (usa el puerto del env var `PORT`, default 8001):**

```powershell
python -m app.main
```

**Opcion C — gunicorn (similar a produccion):**

```powershell
gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8001 --workers 1 --timeout 120
```

### 2.6 Verificar

```powershell
curl http://localhost:8001/health
# Esperado: {"status":"healthy","database":"connected"}
```

Documentacion interactiva: <http://localhost:8001/docs>

---

## 3. Cambiar el puerto

Si necesitas otro puerto distinto a 8001 (ej. 9000):

```powershell
$env:PORT = "9000"
python -m app.main
```

O directo:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

---

## 4. Tests

```powershell
cd "C:/Users/Isael Ortiz/Documents/yary/Backend"
venv\Scripts\Activate.ps1
python -m pytest -q
```

Suite actual: **126 tests**.

---

## 5. Frontends

**Ambos frontends consumen el deploy de Render** (no requieren backend local):

| Frontend | Archivo de configuracion | URL configurada |
| --- | --- | --- |
| Flutter | `lib/config/api_config.dart` | `https://back-despliegue-cp05.onrender.com` |
| Angular (web) | `src/environments/environment.ts` | `https://back-despliegue-cp05.onrender.com` |

Para apuntar temporalmente a local:

**Flutter** — editar `lib/config/api_config.dart`:
```dart
static const String baseUrl = 'http://10.0.2.2:8001';  // Android emulator
// o 'http://localhost:8001' para iOS simulator / web
static const String wsUrl  = 'ws://10.0.2.2:8001';
```

**Angular** — editar `src/environments/environment.ts`:
```ts
apiUrl: 'http://localhost:8001',
wsBase: 'ws://localhost:8001',
```

---

## 6. Despliegue manual

Para forzar un redeploy en Render despues de cambios:

```powershell
git add .
git commit -m "deploy: descripcion del cambio"
git push origin main
```

Render detecta el push y corre automaticamente:
1. `pip install -r requirements.txt`
2. `bash despliegue/start.sh` (migraciones + seed + gunicorn)

Logs en vivo: <https://dashboard.render.com>
