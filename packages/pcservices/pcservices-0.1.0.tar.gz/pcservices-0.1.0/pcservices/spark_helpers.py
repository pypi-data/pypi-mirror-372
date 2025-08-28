from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType

def create_spark_dataframe():
    # Initialize Spark Session
    spark = (
        SparkSession.builder.appName("BigQuery Integration Test")
        # .config(
        #     "spark.jars",
        #     "https://storage.googleapis.com/spark-lib/bigquery/spark-bigquery-latest_2.12.jar",
        # )
        .getOrCreate()
    )

    # Define schema for the DataFrame
    schema = StructType([
        StructField("Value", IntegerType(), True)
    ])

    # Create data for the DataFrame
    data = [(1,)]

    # Create DataFrame
    df = spark.createDataFrame(data, schema)

    return df

# Example usage:
df = create_spark_dataframe()
# df.show()
print("Hello World!")
print(type(df))
print(df.count())