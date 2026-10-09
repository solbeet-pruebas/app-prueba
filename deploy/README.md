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
| `smoke` | mapa | no | Verificación post-deploy (ver abajo). Ausente = solo se verifica la readiness. |
| `smoke.timeout_seconds` | entero | no | Tiempo máximo de cada chequeo, en segundos. Default `10`. |
| `smoke.checks` | lista | sí (si hay `smoke`) | Chequeos, en orden. Cada uno tiene `name` y **exactamente uno** de `http` o `command`. |
| `smoke.checks[].name` | string | sí | Identificador único (minúsculas, números, guiones). Aparece en el resultado de la verificación. |
| `smoke.checks[].http.method` | string | no | `GET` (default) o `HEAD`. Los chequeos no deben cambiar datos. |
| `smoke.checks[].http.path` | string | sí | Ruta que empieza con `/`, relativa a la URL pública del ambiente. |
| `smoke.checks[].http.expect.status` | entero | no | Código HTTP esperado. Default `200`. No se siguen redirecciones. |
| `smoke.checks[].http.expect.body_contains` | string | no | Texto que tiene que aparecer en el cuerpo de la respuesta. |
| `smoke.checks[].command` | lista de strings | sí (si no hay `http`) | Comando que se corre con la imagen de `service` de la versión recién desplegada. Recibe `SMOKE_BASE_URL` (URL pública del ambiente, sin barra final). Pasa si sale con código 0. |
| `smoke.checks[].service` | string | no | Servicio cuya imagen corre el `command`. Default `api`. |

## Reglas para quien consume el contrato

- Orden de deploy: migración (si existe) → servicios. La app **no** migra al arrancar.
- `readiness` decide si entra tráfico; `liveness` decide si se reinicia el contenedor.
  No usar `readiness` como liveness: una caída de la base reiniciaría todo en bucle.
- Las rutas de salud no están bajo `path_prefix`. La única que se publica por el ingress
  es la `readiness` del api, como ruta exacta (en el chart: `ingress.apiExactPaths: [/readyz]`),
  para que la verificación post-deploy la consulte por la URL pública. `liveness` no se publica.
- Los contenedores corren como usuario no root (api uid 10001, web uid 101).

## Verificación post-deploy (`smoke`)

Después de cada deploy a un ambiente, Run (solbeet-run, loop `post-deploy`) corre los
chequeos de `smoke` del contrato **de la revisión desplegada** contra la URL pública de ese
ambiente (la del Deployment de GitHub, p. ej. `https://<proyecto>-staging.<dominio>`), además
de mirar la readiness y los errores durante una ventana. El deploy queda verificado solo si
pasan todos.

- Un chequeo `http` arma `<URL del ambiente><path>`, hace el pedido sin seguir redirecciones,
  con `timeout_seconds`, y compara `expect.status` y, si está, `expect.body_contains`.
- Un chequeo `command` corre una sola vez, con la imagen de `service` y el tag desplegado,
  sin secretos de la app; solo recibe `SMOKE_BASE_URL`. Sirve para pruebas que un pedido HTTP
  no alcanza a expresar.
- Los chequeos tienen que ser de solo lectura y rápidos: corren en producción en cada deploy.
- Quien consume decide reintentos y ventana; el contrato solo dice qué tiene que dar bien.

La plantilla trae un smoke mínimo: readiness del api (`/readyz` con `"status":"ok"`), el
listado de `items` (`/api/items`, pasa por el ingress y la base) y, con frontend, que `/`
devuelva el HTML de la SPA. Al reemplazar `items` por el recurso real, cambiar ese chequeo.

## Cambios de esquema

Agregar campos opcionales no cambia `schema_version`. Renombrar, quitar o cambiar el
significado de un campo sí, y requiere actualizar en paralelo los consumidores.
