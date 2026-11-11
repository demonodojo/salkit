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

## Compilador y memoria

Este `sal` (el de `../sal/target/release/sal`) no es el de `~/.cargo/bin`. Al escribir `.sal`:

- Memoria (SPEC «Memoria»): un valor con dueño se **mueve**; se presta con `&T` / `&mut T`; la copia profunda es **`.clone()`**. No escribas modos `borrow`/`take`/`keep` (son `E_PARSE`). No uses asas `vec_*` / `str_as_int` / `str_from_int` para cadenas o listas: usa `String`, `List[T]` y structs.
- Un accesor que solo lee un campo `String` del struct debe devolver `&String` (p. ej. `&r.body`). Si el llamador necesita una segunda dueña, `.clone()`. Devolver el campo por valor mueve ese campo fuera del struct.
- No escribas funciones que devuelvan `&Struct` (p. ej. `-> &JsonDoc`): el compilador devuelve un puntero inválido y el llamador se cae (SEGV). `-> &String` sí funciona. Presta el campo en el sitio: `d = &fm.doc`.
- `List.push` / `sk_sl_push` **mueven** el elemento: clona antes si lo vas a seguir usando. `list.get` / `sk_sl_get` prestan (`&T`).
- `{` y `}` dentro de una cadena son literales. No las escribas `{{` ni `}}`.
- No llames a lo marcado `@deprecated` en `std/io`. Sustitutos: `Path.new(path.clone()).size()` (y `.is_dir()`, `.mtime()`, `.open_read()`, `.parent()`, `.mkdir_p()`; `Path.new` toma `String` por valor); `Fd.new(fd).read/write/write_str/close/read_timeout`; `Pipe.create()` / `.read_fd()` / `.write_fd()`; `Wait.from_raw(status).exit_code()`. Un aviso `W_DEPRECATED` no tumba el test, pero no se deja.
- Un brazo de `match` en la misma línea tiene que ser una expresión: `return` no lo es. Los brazos con bloque sobre un `Int` no aplican las asignaciones y un `return` en el comodín deja un phi sin definir (`E_INTERNAL: use of undefined value`). El `match` devuelve un valor (`step = match c ...`) y la asignación o el `return` van fuera.
- `&&` y `||` cortocircuitan (`&&` ata más que `||`). Sirven para juntar `if` anidados que comparten el mismo cuerpo. El operando derecho no se evalúa si el izquierdo ya decide.
- No reasignes una variable ya definida en una rama que termina en `return`: el phi posterior queda sin definir. Usa un nombre nuevo en esa rama.
- `on` y `from` son palabras reservadas. No hay `break`: usa una bandera en el `while`.
