import inspect
from pathlib import Path
import yaml


class Fixer:

    def __init__(self, model):
        self.model = model
        self.fixes = self.get_fixer_conf(self.model)

    def get_fixer_conf(self, model):
        """
        Update Docstrings
        """
        recipe = Path(
            inspect.getfile(Fixer)
            ).parent / f"conf/{model.lower()}_fixer.yaml"
        try:
            with open(recipe, 'r') as f:
                fixes = yaml.safe_load(f)

        except FileNotFoundError:
            print(f"No fixes available for model {model}")
            return None

        else:
            return fixes

    def multiply(self, da, factor):
        """
        Update Docstrings
        """
        return da * factor

    def apply(self, ds):
        """
        Update docstrings
        """
        if self.fixes is None:
            return ds

        for variable in ds:
            da = ds[variable]

            if variable in self.fixes:

                for fix in self.fixes[variable]:
                    fix_fn = getattr(self, fix["action"])

                    ds[variable] = fix_fn(
                        da, **{k: v for k,v in fix.items() if k != "action"}
                        )

        return ds
