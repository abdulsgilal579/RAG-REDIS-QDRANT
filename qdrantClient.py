from qdrant_client import QdrantClient

qdrant_client = QdrantClient(
    url="https://62689522-41c6-4029-b564-3592c4b09e75.sa-east-1-0.aws.cloud.qdrant.io:6333", 
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIiwic3ViamVjdCI6ImFwaS1rZXk6MDc5NTZjYjgtMjA0Yi00YTlhLWI0NzYtMjQ0MTRhMzE0NGU4In0.XAwWFvkGzjeFmgYuMZxHmbBXhHO5RlKbkmhLL8YNAVg",
)

print(qdrant_client.get_collections())