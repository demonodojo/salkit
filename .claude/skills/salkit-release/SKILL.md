---
name: salkit-release
description: Publica una nueva versión de salkit (sube version en Sal.toml, crea el tag vX.Y.Z y lo empuja para que el CI genere la release). Úsalo cuando se pida sacar/etiquetar una versión.
---

# Release de salkit

`sal fetch` resuelve `version` contra los tags `vX.Y.Z` del repo, y `.github/workflows/release.yml` crea la release de GitHub al empujar un tag `v*.*.*`. Verifica que el tag coincide con `version` de `Sal.toml`.

## Elegir versión (semver, 0.x)

- Parche `0.1.x`: correcciones sin cambio de API.
- Minor `0.x.0`: funciones nuevas **o** cambios incompatibles (en 0.x un minor puede romper; los consumidores con `version = "0.1"` no lo reciben solos).
- Sufijo (`0.2.0-rc1`): se publica como prerelease.

## Pasos

1. Árbol limpio y tests pasando (skill `salkit-test`): `git status --short` vacío.
2. Editar `version` en `Sal.toml`; commit (`git commit -am "release vX.Y.Z"`).
3. Tag **ligero** (no `-a`/`-s`: `sal fetch` guardaría el hash del objeto tag en vez del commit):
   ```bash
   git tag vX.Y.Z
   ```
4. **Confirmar con el usuario** y empujar: `git push origin main vX.Y.Z`.
5. Comprobar en la pestaña Actions del repo que corrió "Release" y que existe la release.

## Si el workflow no se lanza

Con el workflow ya en el remoto, vuelve a subir el tag: `git push origin :refs/tags/vX.Y.Z && git push origin vX.Y.Z` (solo si aún no hay release asociada). Comprueba también que Actions está habilitado en Settings.
