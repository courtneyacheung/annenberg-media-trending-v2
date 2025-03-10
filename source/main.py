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
import requests
import json

def lambda_handler(event, context):
    # GA property id
    property_id = "385998900"

    # GA API credentials
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'API_test.json'
    client = BetaAnalyticsDataClient()

    # getting data from GA
    request = RunReportRequest(

        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pagePathPlusQueryString"), Dimension(name="nthday")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="6daysAgo", end_date="today")],

    )
    response = client.run_report(request)

    # creating a dataframe
    data = [
        (row.dimension_values[0].value,  # path
         row.metric_values[0].value,  # views
         row.dimension_values[1].value)  # number of days between start date and publication date
        for row in response.rows
    ]
    views_df = pd.DataFrame(data, columns=['path', 'views', 'days_since_start'])
    views_df = views_df.astype({'days_since_start': 'int64', 'views': 'int64'})
    # print(views_df)

    # filter for articles (no landing pages)
    views_df = views_df[views_df['path'].str.contains(r"^/\d{4}/\d{2}/\d{2}", regex=True)]
    # weight the view counts by recency
    views_df['weighted_score'] = views_df['views'] * (3 ** (views_df['days_since_start']))
    # total the weighted view counts for each article across days
    views_df = views_df.groupby('path')[['views', 'weighted_score']].sum().reset_index()
    # get paths to articles with the 10 highest total weighted view count
    top_pages = views_df.sort_values(by='weighted_score', ascending=False).head(10)
    top_pages = top_pages['path'].values
    # print(top_pages)

    # Arc XP API token
    token = "D600IPB7GATQC0GAAPF4AUFU8J5U65UViPSwC7eQ/6z++BjK7OG2L4Iz9Xervs1dRE/9e6e7"

    # getting data from Arc XP
    articles = ','.join([path for path in top_pages])
    headers = {"Authorization": f"Bearer {token}"}
    url = ('https://api.uscannenberg.arcpublishing.com/content/v4/urls?' +
           'website=uscannenberg&included_fields=' +
           'canonical_url,headlines.basic,subheadlines.basic,display_date,promo_items.basic' +
           '.additional_properties.resizeUrl,credits&website_urls=' +
           articles)
    response = requests.get(url, headers=headers)
    # print(response.content)

    outputs = []
    host = 'www.uscannenbergmedia.com'
    print(json.dumps(response.json(), indent=2))

    for article in response.json()['content_elements']:
        output_dict = {'url': 'www.uscannenbergmedia.com' + article['canonical_url'],
                       'image_url': 'www.uscannenbergmedia.com' + article['promo_items']['basic']['additional_properties'].get('resizeUrl'),
                       'headline': article['headlines']['basic'],
                       'subheadline': article['subheadlines']['basic'],
                       'date': article['display_date'],
                       'credits': [author['additional_properties']['original']['byline'] for author in article['credits']['by']]}
        outputs.append(output_dict)
    # print(json.dumps(outputs, indent=2))

    # writing the output to data.js
    with open('/tmp/data.js', 'w') as f:
        f.write('trending(' + json.dumps(outputs) + ');')


    # ! do not uncomment the lines below !

    # Create an S3 client
    # s3 = boto3.client('s3', region_name='us-east-1')

    # Upload a file
    # cache_control_header = 'no-store, no-cache, must-revalidate'
    # s3.upload_file('/tmp/data.js', 'annenberg-trending-data', 'data.js',
    #                ExtraArgs={'CacheControl': cache_control_header})

    return


if __name__ == "__main__":
    event = {
        'action': 'someaction'
    }
    print(lambda_handler(event, None))