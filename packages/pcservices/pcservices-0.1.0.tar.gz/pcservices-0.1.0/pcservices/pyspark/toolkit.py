def write_to_bigquery(
    spark_df,
    table_name,
    project_id="pcb-prod-pds",
    dataset="PCMC_PORTFOLIO",
    mode="overwrite",
    use_temp_bucket=False,
    temp_bucket=None
):
    """
    Writes a Spark DataFrame to a BigQuery table.
    
    :param spark_df: The Spark DataFrame to write.
    :param table_name: The name of the BigQuery table.
    :param project_id: The Google Cloud project ID.
    :param dataset: The BigQuery dataset name.
    :param mode: Write mode ('overwrite' or 'append').
    :param use_temp_bucket: If True, use indirect write via GCS.
    :param temp_bucket: Temporary GCS bucket (required if use_temp_bucket=True).
    """
    
    full_table_id = f"{project_id}.{dataset}.{table_name}"
    
    writer = (spark_df.write
        .format("bigquery")
        .mode(mode)
        .option("table", full_table_id)
    )
    
    if use_temp_bucket:
        if not temp_bucket:
            raise ValueError("temp_bucket must be provided when use_temp_bucket=True")
        writer = (writer
            .option("temporaryGcsBucket", temp_bucket)
            .option("writeDisposition", "WRITE_TRUNCATE" if mode=="overwrite" else "WRITE_APPEND")
        )
    else:
        writer = writer.option("writeMethod", "direct")
    
    writer.save()
    print(f"{mode.capitalize()}d {table_name} in BigQuery table {full_table_id}")