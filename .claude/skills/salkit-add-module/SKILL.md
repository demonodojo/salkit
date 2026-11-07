---
name: salkit-add-module
description: Convenciones para añadir o modificar un módulo de salkit (prefijos, efectos, tests, README y trampas del compilador sal actual). Úsalo al crear o editar un .sal de la librería.
---

# Añadir un módulo a salkit

1. **Fichero** `nombre.sal` en la raíz, con cabecera de una línea: `# salkit/nombre.sal — qué hace`.
2. **Prefijo único** en todas las funciones públicas (`json_`, `fsx_`, `proc_`, `b64_`, `fm_`, `sk_`…). Comprueba que no choca: `grep -n "^fn prefijo_" *.sal`. Los ayudantes internos también llevan prefijo; Sal no tiene visibilidad privada.
3. **Efectos explícitos** en la firma (`! io`, `! alloc`, `! io, alloc`); sin efectos si la función es pura.
4. **Dependencias mínimas**: solo `std/io` (`import "io/io.sal"`) y otros módulos de salkit por ruta relativa. No añadas dependencias externas: la librería está pensada para no depender de nada más.
5. **Errores sin excepciones**: devolver `0`/`-1`/cadena vacía según el estilo del módulo vecino más parecido (mira `fsx.sal`, `proc.sal`) y documentarlo.
6. **Test** `tests/sal/test_nombre.sal` con `ck_int`/`ck_str` (ver skill `salkit-test`) cubriendo casos normales, vacíos y de error. Importa el módulo con `import "../../nombre.sal"`.
7. **README**: añade una fila a la tabla de módulos (módulo, prefijo, contenido).
8. Ejecuta todos los tests antes de dar el cambio por bueno (skill `salkit-test`).

Si el cambio rompe la API pública de un módulo existente, tenlo en cuenta al elegir la versión (skill `salkit-release`).

## Compilador

Este `sal` (el de `../sal/target/release/sal`) no es el de `~/.cargo/bin`. Al escribir `.sal`:

- `{` y `}` dentro de una cadena son literales. No las escribas `{{` ni `}}`.
- No llames a lo marcado `@deprecated` en `std/io`. Sustitutos: `Path.new(path).size()`, `.is_dir()`, `.mtime()`, `.open_read()`, `.parent()`, `.mkdir_p()`; `Fd.new(fd).read(ptr, len)`, `.write(ptr, len)`, `.write_str(s)`, `.close()`, `.read_timeout(ptr, len, ms)`; `Pipe.create()` y `.read_fd()` / `.write_fd()`; `Wait.from_raw(status).exit_code()`. Un aviso `W_DEPRECATED` no tumba el test, pero no se deja.
- Un brazo de `match` en la misma línea tiene que ser una expresión: `return` no lo es. Los brazos con bloque sobre un `Int` no aplican las asignaciones y un `return` en el comodín deja un phi sin definir (`E_INTERNAL: use of undefined value`). El `match` devuelve un valor (`step = match c ...`) y la asignación o el `return` van fuera.
- `&&` y `||` cortocircuitan (`&&` ata más que `||`). Sirven para juntar `if` anidados que comparten el mismo cuerpo. El operando derecho no se evalúa si el izquierdo ya decide.
- Devolver un campo `String` de un struct libera los demás. Un accesor que se puede llamar más de una vez sobre el mismo valor lo toma `borrow` y copia: `s.slice(0, s.len())`.
- No reasignes una variable ya definida en una rama que termina en `return`: el phi posterior queda sin definir. Usa un nombre nuevo en esa rama.
- `on` y `from` son palabras reservadas. No hay `break`: usa una bandera en el `while`.
