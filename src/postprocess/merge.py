import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import lit
from pyspark.sql.functions import concat,col
from pyspark.sql.functions import when
import datetime

args = getResolvedOptions(sys.argv, ["JOB_NAME", "Bucket", "Partition", "Key"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

path0 = "s3a://"+ args['Bucket'] + "/runs/" + args['Partition'] + "/data_clusters.csv"
path1 = "s3a://"+ args['Bucket'] + "/" + args['Key']

df1 = spark.read.options(header=True).csv(path0).withColumnRenamed("CustomerID", "ID")
df2 = spark.read.options(header=True).csv(path1)

merged_df = df1.join(df2, df1.ID == df2.CustomerID, "inner").cache()
merged_df = merged_df.withColumn("UniqueEndpoints", concat(merged_df.ChannelType, merged_df.Address)).cache()
merged_df = merged_df.dropDuplicates(["UniqueEndpoints"])
merged_df = merged_df.select("ID", "ChannelType", "Address", "r_score", "f_score", "m_score", "Cluster_Labels")

# Format as per Pinpoint schema requirements

## Rename columns
merged_df = merged_df.withColumnRenamed("ID", "User.UserId")
merged_df = merged_df.withColumnRenamed("r_score", "Metrics.RScore")
merged_df = merged_df.withColumnRenamed("f_score", "Metrics.FScore")
merged_df = merged_df.withColumnRenamed("m_score", "Metrics.MScore")
merged_df = merged_df.withColumnRenamed("Cluster_Labels", "Metrics.ClusterLabel")

## Add last updated date/time
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
merged_df = merged_df.withColumn("EffectiveDate", lit(now))

## Write to CSV files
merged_df.write.options(header=True).csv("s3a://"+ args['Bucket'] + "/runs/" + args['Partition'] + "/endpoints/")

job.commit()
