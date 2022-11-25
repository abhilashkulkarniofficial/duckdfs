# DuckDFS

## Installation (MacOS)

1. Clone the repository

2. Setup DuckDFS using the following command:

```
source ./setup.sh
```

3. Check where DuckDFS is installed:

```
where duckdfs
```

4. All DuckDFS commands:

```
duckdfs --help
```

## Map Reduce

1. Download US_Accidents_Dataset.csv from [Kaggle](https://www.kaggle.com/code/prajwalkrish/us-accidents-exploratory-data-analysis/data)

2. Copy the dataset into /examples/datasets folder.

3. Create a new folder in duckdfs

```
duckdfs mkdir US_Accidents
```

4. Put the dataset into the folder

```
duckdfs put -i examples/datasets/US_Accidents_Dataset.csv -o US_Accidents
```

5. Describe the dataset.

```
duckdfs mapreduce -i /US_Accidents/US_Accidents_Dataset.csv -d 1 
```

5. Perform the followinig mapreduce exploratory analysis:

### Analysis 1

Top 10 counties with the highest number of Accidents.

```
duckdfs mapreduce -i /US_Accidents/US_Accidents_Dataset.csv -q examples/queries/q1.json -o output1.csv
```

### Analysis 2

Number of accidents by severity.

```
duckdfs mapreduce -i /US_Accidents/US_Accidents_Dataset.csv -q examples/queries/q2.json -o output2.csv
```

### Analysis 3

Number of accidents in Snow and Light Snow weather conditions.

```
duckdfs mapreduce -i /US_Accidents/US_Accidents_Dataset.csv -q examples/queries/q3.json -o output3.csv
```

### Analysis 4

Distinct weather conditions.

```
duckdfs mapreduce -i /US_Accidents/US_Accidents_Dataset.csv -q examples/queries/q4.json -o output4.csv
```

### Analysis 5

Average Temperature and Average Winds at each Airports when accidents occurred.

```
duckdfs mapreduce -i /US_Accidents/US_Accidents_Dataset.csv -q examples/queries/q5.json -o output5.csv
```


## Shutdown DuckDFS

```
source ./shutdown.sh
```

