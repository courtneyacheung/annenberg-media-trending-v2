from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
import boto3
import os
import pandas as pd

def lambda_handler(event, context):
    # GA property id
    property_id = "385998900"

    # Using a default constructor instructs the client to use the credentials
    # specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'API_test.json'
    client = BetaAnalyticsDataClient()

    request = RunReportRequest(

        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pagePathPlusQueryString"), Dimension(name="pageTitle"),
                    Dimension(name="fullPageUrl"), Dimension(name="nthday")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="6daysAgo", end_date="today")],

    )
    response = client.run_report(request)

    # creating a dataframe
    print("Top Articles:")
    data = [
        (row.dimension_values[0].value,  # path
         row.dimension_values[2].value,  # url
         row.metric_values[0].value,  # views
         row.dimension_values[3].value,  # date
         row.dimension_values[1].value.replace(' – Annenberg Media', ''))  # title
        for row in response.rows
    ]
    views_df = pd.DataFrame(data, columns=['path', 'url', 'views', 'days_since_start', 'title'])
    views_df = views_df.astype({'days_since_start': 'int64', 'views': 'int64'})

    # filter for articles
    views_df = views_df[views_df['path'].str.contains(r"^/\d{4}/\d{2}/\d{2}", regex=True)]
    # weight the view counts by recency
    views_df = views_df.groupby(['url', 'title', 'days_since_start']).sum().reset_index()
    views_df['weighted_score'] = views_df['views'] * (3 ** (views_df['days_since_start']))
    # total the weighted view counts
    views_df = views_df.groupby(['url', 'title'])[['views', 'weighted_score']].sum().reset_index()
    # display articles with the 5 highest total weighted view count
    top_pages = views_df.sort_values(by='weighted_score', ascending=False).head(10)
    top_pages['image_placeholder'] = 'placeholder'
    print(top_pages)

    # writing the top_pages to data.js
    json_data = top_pages.to_json(orient='records')
    with open('/tmp/data.js', 'w') as f:
        print('start')
        f.write('trending(' + json_data + ');')
        print('end')

    # Create an S3 client
    s3 = boto3.client('s3', region_name='us-east-1')

    # Upload a file
    cache_control_header = 'no-store, no-cache, must-revalidate'
    s3.upload_file('/tmp/data.js', 'annenberg-trending-data', 'data.js',
                   ExtraArgs={'CacheControl': cache_control_header})


    return


if __name__ == "__main__":
    event = {
        'action': 'someaction'
    }
    print(lambda_handler(event, None))