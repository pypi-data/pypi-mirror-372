# UltraCompress Module

Ce module permet de compresser et décompresser des fichiers JSON en utilisant un format binaire `.uc`.

## Installation

```bash
pip install .
````

## Utilisation

```python
from ultracompress_module import compress, decompress

# Compresser un fichier JSON
compress("input.json", "output.uc")

# Décompresser un fichier .uc
decompress("output.uc", "input2.json")
```

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.