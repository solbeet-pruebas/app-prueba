"""Tests de aceptación: uno por criterio de la spec aprobada.

Los escribe el paso `construir` antes que el código y en otra sesión. Una vez
mergeados no se tocan: el check `solbeet / tests` frena cualquier PR que cambie un
archivo existente de esta carpeta sin el dale de una persona (label tests-con-dale).
Agregar archivos nuevos sí se puede.

Se escriben con la fixture `api` (ver conftest.py): corren en el CI dentro del proceso y,
con `ACEPTACION_BASE_URL`, contra staging y producción después de cada deploy (autoprueba
por cambio). Nombre `test_ca_<issue>_<n>_...`; sin secretos; inocuas contra producción.
"""
