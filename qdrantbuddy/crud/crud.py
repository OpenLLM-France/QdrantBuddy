from filecatcher.components import Indexer
from qdrantbuddy.config import load_config
from qdrant_client import QdrantClient, models

# Load the configuration
config = load_config()

class QdrantCRUD :
    def __init__(self):
        self.indexer = Indexer(config=config)
        self.collection_name = config.vectordb.collection_name
        self.logger = self.indexer.logger

    
    def get_file_points(self, file_name: str):
        """
        Get the points associated with a file from Qdrant
        """
        try:
            # Scroll through all vectors
            has_more = True
            offset = None
            results = []

            while has_more:
                response = self.indexer.vectordb.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=models.Filter(must=[]),  # No initial filter for substring
                    limit=100,
                    offset=offset,
                )
                
                # Add points that contain the filename in metadata.source
                results.extend(
                    point
                    for point in response[0]
                    if file_name in point.payload.get("metadata", {}).get("source", "")
                )
                has_more = response[1]  # Check if there are more results
                offset = response[1] if has_more else None

            # Return list of result ids
            return [res.id for res in results]
        
        except Exception as e:
            raise Exception(f"An exception as occured: {e}")


    def delete_points(self, points: list):
        """
        Delete points from Qdrant
        """
        try:
            self.indexer.vectordb.client.delete_points(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=points)
            )
        except Exception as e:
            raise Exception(f"An exception as occured: {e}")
    
    
    def delete_file_chunks(self, file_name: str):
        """
        Delete the chunks associated with a file from Qdrant
        """
        try:
            self.indexer.vectordb.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="metadata.source",
                                match=models.MatchValue(value="file_name"),
                            ),
                        ],
                    )
                ),
            )
        except Exception as e:
            raise Exception(f"An exception as occured: {e}")
