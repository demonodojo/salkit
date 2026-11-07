# salkit

Librería de utilidades para [Sal](../sal): JSON, regex, glob, HTTP, procesos, ficheros, base64 y frontmatter. Está pensada para `supercoder-sal` y no depende de nada fuera de `std/io`.

## Uso

```toml
# Sal.toml del proyecto
[dependencies]
io = { std = "io" }
salkit = { git = "https://github.com/demonodojo/salkit", version = "0.1" }   # o { path = "../salkit" }
```

`version` es un requisito semver (`0.1` ≡ `^0.1`, es decir `>=0.1.0, <0.2.0`) que `sal fetch` resuelve contra los tags `vX.Y.Z` del repositorio y fija en `Sal.lock`.

## Versiones

Cada versión es un tag ligero `vX.Y.Z` cuyo número coincide con `version` de `Sal.toml`:

```bash
# subir version en Sal.toml, commit, y:
git tag v0.1.0
git push origin main v0.1.0
```

Mientras sea `0.x`, un cambio de minor (`0.1` → `0.2`) puede romper la API; los parches (`0.1.x`) solo corrigen.

```bash
sal install        # enlaza sal_modules/io y sal_modules/salkit
```

```sal
import "salkit/json.sal"

fn main() -> Int ! alloc
    d = json_parse("{\"a\":[1,2]}")
    json_int(d, json_path(d, json_root(d), "a.1"))   # 2
```

## Módulos

| Módulo | Prefijo | Contenido |
|---|---|---|
| `int.sal` | `sk_` | `sk_parse_int`, `sk_parse_hex`, `sk_is_int` |
| `strbuf.sal` | `sk_` | búsqueda sin reservas (`sk_index_of`), `trim`, `replace_all`, listas de cadenas (`sk_sl_*`), `split_lines`, `join`, ordenación, `sk_truncate_middle` |
| `json.sal` | `json_`, `jb_` | parser a arena, `json_get/at/path/len/str/int`, `json_dump`, `json_quote`, constructores `jb_obj/jb_arr/jb_kv` |
| `regex.sal` | `regex_` | NFA tipo Pike (tiempo lineal): `. [] \d \w \s \b ^ $ \| () * + ? {n,m}` |
| `glob.sal` | `glob_` | `*`, `**`, `?`, `[a-z]`, `{a,b}` |
| `fsx.sal` | `fsx_` | leer/escribir/añadir, `list_dir`, `walk` con ignorados |
| `proc.sal` | `proc_` | ejecutar con stdout+stderr mezclados, timeout con SIGKILL, recorte cabeza+cola |
| `http.sal` | `http_` | HTTP/1.1 plano: `Authorization`, chunked, `Content-Length`, plazo total |
| `base64.sal` | `b64_` | `b64_encode` |
| `frontmatter.sal` | `fm_` | cabecera `---` YAML sencilla → documento JSON |

Los resultados son structs por valor (`ProcResult`, `HttpResult`, `Frontmatter`): se pasan y se devuelven en registros, sin reservar memoria. Los nodos JSON, las listas de cadenas y el estado de un flujo HTTP (`hs_*`) siguen siendo asas `Int` (vec) a propósito: son contenedores de tamaño variable o estado mutable compartido, no valores.

## Desarrollo

```bash
sal install && sal test      # tests/sal/test_*.sal; el de http lanza un servidor Python local
```

Trampas del compilador Sal que condicionan el estilo del código:

- **No reasignes una variable ya definida dentro de una rama que termina en `return`**: el valor se filtra y un `phi` posterior queda sin definir (`E_INTERNAL: use of undefined value`). Usa nombres temporales propios en esas ramas.
- `on` y `from` son palabras reservadas. Un parámetro o local no puede llamarse así.
- Las cadenas se mueven al asignarlas (`a = b` consume `b`); copia con `str_slice(b, 0, str_len(b))`.
- No hay `break`: usa una bandera en el `while`. Evita la recursión en cadenas largas.
- `x = x + ...` añade en sitio (amortizado); `f(acc + x)` copia cada vez.
- La memoria no se libera nunca: evita `str_slice` por posición en bucles.
