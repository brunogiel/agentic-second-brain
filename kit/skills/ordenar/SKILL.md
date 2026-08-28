---
name: ordenar
description: >
  Pasada de limpieza sobre la carpeta de descargas. Clasifica cada archivo y lo mueve a carpetas
  de staging **dentro** de Downloads, para que vos hagas el movimiento final a tu sistema. Detecta
  duplicados por contenido, instaladores de apps que ya tenés puestas, ZIPs ya descomprimidos y
  archivos versionados. Nunca saca nada de Downloads y nunca borra. Usalo con "ordená las
  descargas", "limpiá Downloads", "qué basura tengo bajada", o como rutina semanal.
---

# ordenar — la pasada semanal sobre Downloads

## Qué es

Downloads es el inbox de todo lo que baja del navegador, del mail y de la mensajería, y se
convierte en un pozo: instaladores ya usados, ZIPs que ya descomprimiste, la misma factura tres
veces con `(1)` y `(2)`, y en el medio cosas que sí importan.

Esto hace la primera pasada, la mecánica, y te deja para decidir **solo lo dudoso**.

## Las cuatro reglas duras

1. **Nunca mover un archivo fuera de Downloads.** Solo se reordena adentro.
2. **Nunca borrar.** Lo que parece basura va a `_borrar/` y borrás vos.
3. **Nunca tocar una carpeta que ya estaba**, salvo que la muevas entera como bloque.
4. **Ante la duda, se conserva.** Si un archivo puede tener valor y no sabés dónde va, a
   `_para_inbox/`, no a `_borrar/`.

Y una que parece menor y evita el peor error del skill: **las reglas de contenido le ganan al
detector de duplicados.** Un resultado de laboratorio que además tiene una copia con `(1)` no se
borra por duplicado. Solo lo que no matchea ninguna regla puede caer en `_borrar/` por tener copia.

## De dónde salen las categorías

**No hay una tabla fija de destinos, y es a propósito.** Las carpetas de staging se derivan de **tu
propia estructura**: leé el `CLAUDE.md` de tu brain y sus carpetas, y armá un `_para_<carpeta>/`
por cada destino real que tengas. Si tenés un proyecto activo, va a existir su staging; si lo
archivás, deja de aparecer.

Una tabla hardcodeada envejece mal y, peor, tienta a poner adentro los datos que identifican tus
documentos. **No pongas identificadores personales en las reglas.** Un número de identificación
fiscal, un número de afiliado o una dirección convierten un script de ordenar archivos en un
archivo de datos personales. Y además envejecen mal: dejan de funcionar apenas cambia algo.
Clasificá por **tipo de documento**, no por quién sos.

## Parámetros

- `--plan` (default): analiza y muestra qué haría. **No toca nada.**
- `--aplicar`: ejecuta el plan ya revisado.
- `--reportar`: genera el reporte sin mover nada.

## Flujo

1. **[DET] Escanear y proponer.** Corré el script en modo plan. Escanea el primer nivel de
   Downloads, entra a las carpetas chicas para ver qué tienen, calcula hashes para detectar
   duplicados de contenido, y arma el plan.

   Lo que detecta solo:
   - **Duplicados por contenido** (mismo hash, distinto nombre).
   - **Versionados:** `archivo (1).pdf`, `archivo (2).pdf`.
   - **ZIP ya descomprimido:** existe la carpeta con el mismo nombre al lado.
   - **Instalador de una app que ya tenés instalada.**

2. **[LATENT] Revisar con quien manda.** Mostrá tres cosas y **esperá el OK**:
   - La tabla resumen: cuántos archivos por destino y cuánto pesa cada grupo.
   - El top 10 de candidatos a borrar **por tamaño**, que es donde están los gigas.
   - La lista completa de lo que no matcheó ninguna regla, **proponiendo destino para cada uno**.
     Esta es la parte donde hace falta criterio y no hay script que la resuelva.

3. **[DET] Aplicar.** Mueve según el plan aprobado. Si un archivo ya no está porque lo moviste a
   mano en el medio, lo saltea con un aviso: **no falla la corrida entera por eso.**

4. **[LATENT] Reportar.** Un reporte corto con qué se movió, cuántos gigas quedaron recuperables
   en `_borrar/`, y los accionables que salieron de la pasada.

## Output esperado

- Las carpetas `_para_*/`, `_borrar/` y `_revisar/` creadas dentro de Downloads, con los archivos
  adentro.
- El plan en JSON, como caché entre el análisis y la aplicación.
- Un reporte con fecha.
- Un cierre en el chat con los accionables de arriba, no el listado completo.

## Success metrics

- **Cero archivos movidos fuera de Downloads.** Es la métrica que importa: si esta falla, ninguna
  otra cuenta.
- Al menos 70% de los archivos sueltos quedaron clasificados.
- `_revisar/` con menos de 30 archivos. Si tiene más, las reglas se quedaron cortas y conviene
  ajustarlas antes de la próxima pasada.
- Cero identificadores personales en el archivo de reglas.

## Troubleshooting

- **Todo cae en `_revisar/`.** Las reglas todavía no conocen tus tipos de documento. Agregá de a
  poco, empezando por lo que más se repite.
- **Un archivo importante fue a `_borrar/`.** Casi siempre es el detector de duplicados ganándole a
  una regla que falta. Agregá la regla; el orden ya la pone por encima del detector.
- **La pasada tarda mucho.** El hash de archivos muy grandes es lo caro. Subí el umbral de tamaño
  a partir del cual no se hashea: para archivos de gigas, el nombre y la fecha alcanzan.
