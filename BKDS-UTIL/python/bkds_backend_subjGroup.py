import os
import json
import argparse
from datetime import datetime
import time
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Custom functions
from bkds_Utilities import log_msg, fetch_data, subjGenOutputHandler, get_sqlTemplate

# Main Setup / Variables
program_name = os.path.basename(__file__)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a subject given a batch id")
    parser.add_argument("batch_id", help="Batch ID")
    parser.add_argument("subjType", help="Subject type ('wiki', 'flickr', 'youtube')")
    return parser.parse_args()

args = parse_arguments()
batch_id = args.batch_id
subjType = args.subjType

query_key = 'bkds_subGroupjGen_source'

def logMsg(msg):
    log_msg(program_name, batch_id, msg)
    print(msg)

def vectorize_text(data):
    logMsg("Starting text vectorization")
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(data)
    return X, vectorizer

def perform_clustering(X, n_clusters=5):
    logMsg(f"Performing clustering with {n_clusters} clusters")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)
    logMsg(f"Cluster labels: {labels}")
    return labels

def main():
    logMsg(f"starting main for {batch_id} for {subjType} from {program_name}")
    sql_query = get_sqlTemplate(query_key)


    if subjType:
        logMsg(f"Processing {subjType} with {sql_query}")

        # Fetch data for clustering
        data = fetch_data(sql_query)
        
        print(f'using: sql_query: {sql_query}')
        
        df = pd.DataFrame(data, columns=['record_id', 'raw_content'])
        # Assuming the other parts of the script setup are done and data is ready
        X, _ = vectorize_text(df['raw_content'])  # with improved text processing
        optimal_k = 1100  # Set this based on your analysis from the elbow method
        df['cluster_id'] = perform_clustering(X, optimal_k)

      

        # Generate output data
        output_data = []
        for _, row in df.iterrows():
            result_item = {
                "record_id": row['record_id'],
                "cluster_id": row['cluster_id'],
                "description": row['raw_content']
            }
            output_data.append(result_item)

        output_filepath = subjGenOutputHandler(output_data, subjType, 'bkds_', 'json', 'groupGen', batch_id)
        logMsg(f"Results from subjGenMedia output: {output_filepath}")

    else:
        logMsg(f"Unsupported subject type: {subjType}")

    logMsg(f"ending main for {batch_id} from {program_name}")
# Main clustering part
if __name__ == "__main__":

    main()
