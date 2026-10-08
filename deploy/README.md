# Contrato de deploy

`deploy/contract.yaml` es la única fuente de verdad sobre cómo se despliega este proyecto.
Las herramientas de la fábrica (chart de Helm, bootstrap de VPS) lo leen; no deberían
necesitar mirar el código ni los Dockerfiles para saber qué hacer.

Si cambiás un puerto, una ruta de salud, una variable de entorno o el comando de
migración, actualizá el contrato **en el mismo PR**.

## Esquema (`schema_version: 1`)

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `schema_version` | entero | sí | Versión del esquema. Cambia solo si se rompe la compatibilidad. |
| `project` | string | sí | Slug del proyecto (minúsculas, números, guiones). Prefijo de recursos. |
| `services` | mapa | sí | Un servicio por clave (`api`, `web`). La clave es el nombre del servicio. |
| `services.<s>.image` | string | sí | Repositorio de la imagen sin tag. El tag lo decide el pipeline (sha o versión). |
| `services.<s>.build.context` | string | sí | Directorio de build, relativo a la raíz del repo. |
| `services.<s>.build.dockerfile` | string | sí | Dockerfile, relativo al contexto. |
| `services.<s>.port` | entero | sí | Puerto HTTP en el que escucha el contenedor. |
| `services.<s>.health.liveness` | string | sí | Ruta HTTP de liveness: 200 mientras el proceso viva. |
| `services.<s>.health.readiness` | string | sí | Ruta HTTP de readiness: 200 si puede recibir tráfico, 503 si no. |
| `services.<s>.route.path_prefix` | string | sí | Prefijo de ruta pública. Todos los servicios comparten host; el ingress enruta por prefijo, el más largo primero. |
| `services.<s>.migrate.command` | lista de strings | no | Comando a correr con la imagen del servicio **antes** de desplegar la versión nueva (Job o paso previo). Si falla, no se despliega. Debe ser idempotente. |
| `services.<s>.env` | lista | sí (puede ser `[]`) | Variables de entorno que lee el servicio. |
| `services.<s>.env[].name` | string | sí | Nombre de la variable. |
| `services.<s>.env[].required` | bool | sí | Si es `true` y falta, el deploy debe fallar antes de arrancar. |
| `services.<s>.env[].secret` | bool | sí | Si es `true`, va en un Secret / gestor de secretos, nunca en texto plano. |
| `database` | mapa | no | Base de datos que necesita el proyecto. Ausente = sin base. |
| `database.engine` | string | sí | Hoy solo `postgres`. |
| `database.version` | string | sí | Versión mayor de Postgres. |
| `database.url_env` | string | sí | Variable donde se inyecta la URL de conexión. |
| `database.url_scheme` | string | sí | Esquema de la URL que espera la app (`postgresql+psycopg`). |
| `database.backup` | bool | sí | Si es `true`, la plataforma debe programar backups y probar restauraciones. |

## Reglas para quien consume el contrato

- Orden de deploy: migración (si existe) → servicios. La app **no** migra al arrancar.
- `readiness` decide si entra tráfico; `liveness` decide si se reinicia el contenedor.
  No usar `readiness` como liveness: una caída de la base reiniciaría todo en bucle.
- Las rutas de salud no se exponen por el ingress público (no están bajo `path_prefix`
  salvo el `/` del frontend); se consultan dentro del cluster o del host.
- Los contenedores corren como usuario no root (api uid 10001, web uid 101).

## Cambios de esquema

Agregar campos opcionales no cambia `schema_version`. Renombrar, quitar o cambiar el
significado de un campo sí, y requiere actualizar en paralelo los consumidores.
