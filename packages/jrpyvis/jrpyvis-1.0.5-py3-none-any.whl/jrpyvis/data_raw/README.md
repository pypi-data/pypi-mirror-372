The seaborn-derived datasets
(diamonds, exercise, flights, healthexp, iris, penguins, planets)
were added using the following code:

```py
import pathlib
import seaborn as sns

data_path = pathlib.Path("... path to jrpyvis/jrpyvis/data/ ....")

seaborn_datasets = ["diamonds", "exercise", "flights", "healthexp", "iris", "penguins", "planets"]

for ds_name in seaborn_datasets:
    dataset = sns.load_dataset(ds_name) # imported as pandas DataFrame
    base_name = f"{ds_name}.zip"
    dataset.to_csv(data_path / basename, index=False)
```
