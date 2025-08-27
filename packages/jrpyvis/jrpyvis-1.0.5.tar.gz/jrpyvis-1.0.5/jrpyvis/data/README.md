Seaborn datasets that are required in the Python-Vis course:

- diamonds
- exercise
- flights
- healthexp
- iris
- penguins
- planets

These were migrated into jrPyVis, because a client (NAT) had technical issues
using them from `sns.load_dataset()`.

This happened because:
- they couldn't use our course VMs (security)
- so they ran our course demo scripts / exercises on their Anaconda environment
- but `sns.load_dataset()` failed on their Anaconda env possibly because github
  (where the datasets are stored; or possibly some other restricted location) is
  inaccessible to them

The datasets can be loaded using

```
import jrpyvis

ds = jrpyvis.data.load("penguins") # or some other dataset name
```
