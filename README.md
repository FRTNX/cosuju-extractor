# ml-data-scraper

![](image.gif)

To run the extractor:

 $``` python main.py```


 ## datasets Integrations
 ---

To use the data with the ```datasets``` library you may either load the dataset from its repository on huggingface.co:

 ```
 from datasets import load_dataset

 dataset = load_dataset('FRTNX/cosuju', split='train')
 ```

 or read the files locally after cloning this repository:

```
from datasets import load_dataset

dataset = load_dataset('dataset/cosuju.py', data_files='dataset/train-v1.0.json', split='train')
```