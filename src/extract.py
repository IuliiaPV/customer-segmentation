import psycopg2
import boto3
import pandas as pd
from io import StringIO


def connect_to_redshift(dbname, host, port, user, password):
    """Method that connects to redshift. This gives a warning so will look for another solution"""

    connect = psycopg2.connect(
        dbname=dbname, host=host, port=port, user=user, password=password
    )

    print("connection to redshift made")

    return connect


def connect_to_s3(aws_access_key_id, aws_secret_access_key):
    """Methods that connects to s3"""

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    return s3_client


def df_to_s3(df, key, s3_bucket, aws_access_key_id, aws_secret_access_key):
    """Function that writes a data frame as a .csv file to an s3 bucket"""

    csv_buffer = StringIO()  # create buffer to temporarily store the Data Frame

    df.to_csv(csv_buffer, index=False)  # code to write the data frame as csv file

    s3_client = connect_to_s3(aws_access_key_id, aws_secret_access_key)

    s3_client.put_object(
        Bucket=s3_bucket, Key=key, Body=csv_buffer.getvalue()
    )  # this code writes the temp stored csv file and writes to s3

    print(f"The transformed data is saved as CSV in the following location s3://{s3_bucket}/{key}")


def extract_transactional_data(dbname, host, port, user, password):
    # connect to redshift
    connect = connect_to_redshift(dbname, host, port, user, password)

    # write the sql query
    query = """
        select  ot.invoice,
                ot.stock_code,
                ot.quantity, 
                ot.price, 
                ot.quantity * ot.price as total_order_value,
                ot.customer_id,
                ot.country,
               /*this code to replace the missing values in description with unknown*/
               case when sd.description is null then 'Unknown'
                   else sd.description end as description,
               /*this code to fix the invoice date's date type*/
               cast(ot.invoice_date as datetime) as invoice_date
        from bootcamp.online_transactions ot 
        left join (select *
                   from bootcamp.stock_description 
                   where description <> '?') sd on ot.stock_code = sd.stock_code 
        where customer_id != ''
            and ot.stock_code not in ('BANK CHARGES', 'POST', 'D', 'M', 'CRUK')
        """

    online_trans_cleaned = pd.read_sql(query, connect)

    print("the shape of my data is:", online_trans_cleaned.shape)

    connect.close()

    return online_trans_cleaned
