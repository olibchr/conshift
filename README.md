# Concept Drift

A model to detect changes in concept over time from an annotated collection of news paper articles

## Getting Started

This is a research project at CWI. To analyze concepts, a data set of annotated news paper article is necessary.
The model works in several steps. 
* Extract annotations
* Create vector representations for all concept
* Query based concept analysis

A data set can be found here: http://ion.project.cwi.nl/ under About. Please let us know if the server is down.


### Installing

You need python 2.7.x and pip. Get this repository and then you can run (virtual environment recommended):

```
pip install requirements.txt
```

## Process

There are several steps involved to get the concepts representations in a usable format. 

### Preprocessing

To extract all annotations from the jsonld files, run:
```
python 0_data_Prep/create_vectors.py GIVE_PATH_TO_DATA_SET
```

That gives you 2 files: 'all_annotation_vectors.csv' and 'annotation_to_index.csv'

Best store these files in some directory where you will also store all later created files. Lets calls this dir $PROJECT_FILES for now.

Next, we create the concept representations with the following command:

```
python 0_data_Prep/distr_vec_time.py $PROJECT_FILES ALL
```

There are new files being stored in $PROJECT_FILES which we'll need for our change detection.

We need some more numbers, so run:
```
python 0_data_Prep/index_counter.py $PROJECT_FILES
python 0_data_Prep/index_analysis.py $PROJECT_FILES
python 0_data_Prep/idf_weights.py $PROJECT_FILES
```

Now, youre set with all files to analyze concepts. All concepts are being refered to with some id, as given in the file 'annotation_to_index.csv'. Look up an id or just use a number between 0 and 71.000.
Run the command as follows, where N is the amount if bins you want to use to split up the concept representation and ID is some concept ID. 

```
python concept_time_analysis $PROJECT_FILES ALL N ID
```


## Authors

* **Oliver Becher** - [OliBchr](https://github.com/olibchr)


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* CWI
* Amsterdam Data Science
* Laura Hollink & Desmond Elliott
