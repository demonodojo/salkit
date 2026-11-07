---
name: salkit-test
description: Ejecuta los tests de salkit (tests/sal/test_*.sal) con el compilador sal. Úsalo tras modificar cualquier módulo .sal o al verificar un cambio.
---

# Tests de salkit

Cada módulo `X.sal` tiene `tests/sal/test_X.sal`. Un test es un programa Sal cuyo `main` devuelve el número de comprobaciones fallidas: **exit 0 = pasa**. Los fallos se imprimen en stderr como `FAIL #<código> got=[..] want=[..]`.

## Ejecutar

Desde la raíz del repo, con el compilador del repo hermano `../sal` (no el de `~/.cargo/bin`, que no tiene `test` y es anterior):

```bash
../sal/target/release/sal test
```

Si falta el binario: `cargo build --release` en `../sal`. Por defecto recorre `tests/sal`. Una sola suite: `../sal/target/release/sal run tests/sal/test_json.sal`.

- Cada línea es `sal test: ok <ruta>`, `sal test: FAIL <ruta> (exit Some(N))` o `sal test: compile FAIL`. El comando sale distinto de 0 si alguna suite falla. `N` es el número de comprobaciones fallidas de ese programa.
- Los tests de `fsx`/`proc` escriben bajo `target/` (ignorado por git). `test_http.sal` usa `tests/sal/support/mock_server.py` (necesita `python3`).

## Escribir tests

Usa los helpers de `tests/sal/support/assert.sal`: `ck_int(got, want, code)` y `ck_str(got, want, code)`. Numera los `code` correlativamente y acumula: `f = f + ck_int(...)`; el `main` termina devolviendo `f`.
