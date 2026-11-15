# salkit

Librería de utilidades para [Sal](../sal): JSON, regex, glob, HTTP, procesos, ficheros, base64 y frontmatter. Está pensada para `supercoder-sal` y no depende de nada fuera de `std/io`.

## Uso

```toml
# Sal.toml del proyecto
[dependencies]
io = { std = "io" }
salkit = { git = "https://github.com/demonodojo/salkit", version = "0.2" }   # o { path = "../salkit" }
```

`version` es un requisito semver (`0.2` ≡ `^0.2`, es decir `>=0.2.0, <0.3.0`) que `sal fetch` resuelve contra los tags `vX.Y.Z` del repositorio y fija en `Sal.lock`.

## Versiones

Cada versión es un tag ligero `vX.Y.Z` cuyo número coincide con `version` de `Sal.toml`:

```bash
# subir version en Sal.toml, commit, y:
git tag v0.2.1
git push origin main v0.2.1
```

Mientras sea `0.x`, un cambio de minor (`0.2` → `0.3`) puede romper la API; los parches (`0.2.x`) solo corrigen.

```bash
sal install        # enlaza sal_modules/io y sal_modules/salkit
```

```sal
import "salkit/json.sal"

fn main() -> Int ! alloc
    d = json_parse(&"{\"a\":[1,2]}")
    json_int(&d, json_path(&d, json_root(&d), &"a.1"))   # 2
```

## Módulos

| Módulo | Prefijo | Contenido |
|---|---|---|
| `int.sal` | `sk_` | `sk_parse_int`, `sk_parse_hex`, `sk_is_int` |
| `strbuf.sal` | `sk_` | búsqueda (`sk_index_of`), `trim`, `replace_all`, `List[String]` (`sk_sl_*`), `split_lines`, `join`, ordenación, `sk_truncate_middle` |
| `json.sal` | `json_`, `jb_` | `JsonDoc` con dueño, `json_get/at/path/len/str/int`, `json_dump`, `json_quote`, constructores `jb_obj/jb_arr/jb_kv` |
| `regex.sal` | `regex_` | NFA tipo Pike (tiempo lineal): `. [] \d \w \s \b ^ $ \| () * + ? {n,m}` |
| `glob.sal` | `glob_` | `*`, `**`, `?`, `[a-z]`, `{a,b}` |
| `fsx.sal` | `fsx_` | leer/escribir/añadir, `list_dir`, `walk` con ignorados |
| `proc.sal` | `proc_` | ejecutar con stdout+stderr mezclados, timeout con SIGKILL, recorte cabeza+cola |
| `http.sal` | `http_` | HTTP/1.1 plano: `Authorization`, chunked, `Content-Length`, plazo total; flujo `HttpStream` |
| `base64.sal` | `b64_` | `b64_encode` |
| `frontmatter.sal` | `fm_` | cabecera `---` YAML sencilla → documento JSON |

Los resultados con dueño son structs (`ProcResult`, `HttpResult`, `Frontmatter`, `JsonDoc`, `HttpStream`, `Regex`): se mueven por valor y se liberan al salir de ámbito. Los lectores los reciben prestados (`&T` / `&mut T`). Los índices de nodo JSON y las listas de cadenas son `Int` o `List[String]`, no asas `vec`. Los descriptores de fichero y socket son `Fd` de std/io (`fsx_open_write`, `fsx_write_fd`, `http_connect`, `http_send_all`, `HttpStream.fd`); un `Fd` con valor negativo indica error.

## Desarrollo

Salkit se comprueba con Sal **v0.5.0**. Instala esa versión del compilador y asegúrate de que `sal --version` muestra `sal 0.5.0`; una instalación antigua puede no disponer de `install` o `test`. La integración continua compila esa versión desde el repositorio de Sal.

```bash
sal install && sal test      # tests/sal/test_*.sal; el de http lanza un servidor Python local
```

Trampas del compilador Sal que condicionan el estilo del código:

- Memoria al estilo Rust: un valor con dueño se mueve; se presta con `&T`/`&mut T`; la copia profunda es `.clone()`. No hay modos `borrow`/`take`/`keep`.
- Un accesor de campo `String` debe devolver `&String` o un `.clone()`; no devolver el campo por valor si el struct se sigue usando.
- Una función no puede devolver `&Struct` (solo `&String`): el puntero sale inválido. Presta el campo en el sitio (`&fm.doc`).
- `Path.new` toma `String` por valor: desde un `&String` hay que clonar (`Path.new(path.clone())`).
- **No reasignes una variable ya definida dentro de una rama que termina en `return`**: el valor se filtra y un `phi` posterior queda sin definir (`E_INTERNAL: use of undefined value`). Usa nombres temporales propios en esas ramas.
- Un brazo de `match` en la misma línea es una expresión; sobre `Int`, el `match` debe devolver un valor y la asignación va fuera.
- `on` y `from` son palabras reservadas. No hay `break`: usa una bandera en el `while`.
- `x = x + ...` añade en sitio (amortizado); `f(acc + x)` copia cada vez.
