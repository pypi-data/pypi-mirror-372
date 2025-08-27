from sklearn.neighbors import NearestNeighbors
import numpy as np
import heapq
import msgpack
from azure.storage.blob import ContainerClient
from erioon.functions import async_log


def handle_vector_similarity_search(
    user_id,
    db_id,
    coll_id,
    query_vector,
    similarity_metric="cosine",
    limit=10,
    container_url=None,
):
    """
    Perform a vector similarity search on stored vectors in Azure Blob Storage.

    This function supports multiple similarity/distance metrics including cosine similarity,
    Euclidean distance, Manhattan distance, dot product, and a K-Nearest Neighbors (KNN) mode
    leveraging scikit-learn's efficient nearest neighbor search.

    Parameters:
    -----------
    user_id : str
        Identifier of the user making the request, used for logging.
    db_id : str
        Database identifier where the vector collection is stored.
    coll_id : str
        Collection identifier within the database.
    query_vector : list or array-like
        The query vector to compare against stored vectors.
    similarity_metric : str, optional (default='cosine')
        The similarity or distance metric to use for search. Supported values:
        - 'cosine': Cosine similarity (higher is better)
        - 'euclidean': Euclidean distance (lower is better)
        - 'manhattan': Manhattan distance (lower is better)
        - 'dot': Dot product (higher is better)
        - 'knn': Use k-nearest neighbors algorithm (Euclidean metric by default)
    limit : int, optional (default=10)
        Maximum number of top results to return.
    container_url : str, optional
        Azure Blob Storage container URL where vector data blobs are stored.

    Returns:
    --------
    dict, int
        A tuple containing:
        - A dictionary with search status, count of results, and the results list.
          Each result includes the original record fields plus a 'score' or 'distance' key.
        - HTTP-like status code (200 for success, 400 for error).

    Behavior:
    ---------
    - Retrieves blobs from Azure Blob Storage under the path `{db_id}/{coll_id}/`.
    - Each blob is expected to be a msgpack file containing a list of records with at least:
      `_id` (unique record ID) and `vector` (list of floats).
    - Deduplicates records by `_id` and vector values.
    - For 'knn' metric, loads all vectors and uses scikit-learn's NearestNeighbors to find closest matches.
    - For other metrics, performs a linear scan calculating similarity/distance and keeps top results in a heap.
    - Logs success or error events asynchronously.
    - Returns results sorted by similarity score (descending) or distance (ascending), depending on metric.

    Raises:
    -------
    Logs errors internally and continues on blob read failures; does not raise exceptions outward.

    Example usage:
    --------------
    results, status = handle_vector_similarity_search(
        user_id="user123",
        db_id="db1",
        coll_id="col1",
        query_vector=[0.1, 0.2, 0.3],
        similarity_metric="cosine",
        limit=5,
        container_url="https://<storage-account>.blob.core.windows.net/container"
    )
    """

    def cosine_similarity(a, b):
        a = np.array(a)
        b = np.array(b)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        return (np.dot(a, b) / denom) if denom != 0 else 0

    def euclidean_distance(a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    def manhattan_distance(a, b):
        return np.sum(np.abs(np.array(a) - np.array(b)))

    def dot_product(a, b):
        return np.dot(np.array(a), np.array(b))

    metric_map = {
        "cosine": (cosine_similarity, True),
        "euclidean": (euclidean_distance, False),
        "manhattan": (manhattan_distance, False),
        "dot": (dot_product, True),
    }

    if similarity_metric == "knn":
        container_client = ContainerClient.from_container_url(container_url)
        directory_path = f"{db_id}/{coll_id}/"
        blob_list = container_client.list_blobs(name_starts_with=directory_path)
        blob_names = [blob.name for blob in blob_list if blob.name.endswith(".msgpack")]

        vectors = []
        records = []
        seen_ids = set()

        for blob_name in blob_names:
            try:
                blob_client = container_client.get_blob_client(blob_name)
                msgpack_data = blob_client.download_blob().readall()
                unpacked_data = msgpack.unpackb(msgpack_data, raw=False)
            except Exception as e:
                async_log(
                    user_id,
                    db_id,
                    coll_id,
                    "VECTOR_SEARCH",
                    "ERROR",
                    f"Error reading blob {blob_name}: {e}",
                    1,
                    container_url,
                )
                continue

            if not isinstance(unpacked_data, list):
                continue

            for record in unpacked_data:
                rec_id = record.get("_id")
                vector = record.get("vector")
                if not vector or not isinstance(vector, list):
                    continue
                if rec_id in seen_ids:
                    continue
                seen_ids.add(rec_id)

                vectors.append(vector)
                records.append(record)

        if not vectors:
            return {"status": "OK", "count": 0, "results": []}, 200

        nbrs = NearestNeighbors(
            n_neighbors=min(limit, len(vectors)), algorithm="auto", metric="euclidean"
        )
        nbrs.fit(vectors)
        distances, indices = nbrs.kneighbors([query_vector])

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            rec = records[idx].copy()
            rec["distance"] = float(dist)
            results.append(rec)

        async_log(
            user_id,
            db_id,
            coll_id,
            "VECTOR_SEARCH",
            "SUCCESS",
            "OK",
            len(results),
            container_url,
        )
        return {"status": "OK", "count": len(results), "results": results}, 200

    if similarity_metric not in metric_map:
        async_log(
            user_id,
            db_id,
            coll_id,
            "VECTOR_SEARCH",
            "ERROR",
            f"Unsupported similarity metric: {similarity_metric}",
            1,
            container_url,
        )
        return {
            "status": "KO",
            "count": 0,
            "error": f"Unsupported similarity metric: {similarity_metric}",
        }, 400

    metric_func, higher_is_better = metric_map[similarity_metric]

    container_client = ContainerClient.from_container_url(container_url)
    directory_path = f"{db_id}/{coll_id}/"
    blob_list = container_client.list_blobs(name_starts_with=directory_path)
    blob_names = [blob.name for blob in blob_list if blob.name.endswith(".msgpack")]

    heap = []
    seen_ids = set()
    seen_vectors = set()

    for blob_name in blob_names:
        try:
            blob_client = container_client.get_blob_client(blob_name)
            msgpack_data = blob_client.download_blob().readall()
            unpacked_data = msgpack.unpackb(msgpack_data, raw=False)
        except Exception as e:
            async_log(
                user_id,
                db_id,
                coll_id,
                "VECTOR_SEARCH",
                "ERROR",
                f"Error reading blob {blob_name}: {e}",
                1,
                container_url,
            )
            continue

        if not isinstance(unpacked_data, list):
            continue

        for record in unpacked_data:
            rec_id = record.get("_id")
            vector = record.get("vector")
            if not vector or not isinstance(vector, list):
                continue
            vector_key = tuple(round(x, 6) for x in vector)
            if rec_id in seen_ids or vector_key in seen_vectors:
                continue
            seen_ids.add(rec_id)
            seen_vectors.add(vector_key)

            score = metric_func(query_vector, vector)
            heap_score = score if higher_is_better else -score

            if len(heap) < limit:
                heapq.heappush(heap, (heap_score, record))
            else:
                if heap_score > heap[0][0]:
                    heapq.heapreplace(heap, (heap_score, record))

    if higher_is_better:
        results = sorted(
            [{"score": float(item[0]), **item[1]} for item in heap],
            key=lambda x: x["score"],
            reverse=True,
        )
    else:
        results = sorted(
            [{"distance": float(-item[0]), **item[1]} for item in heap],
            key=lambda x: x["distance"],
        )

    async_log(
        user_id,
        db_id,
        coll_id,
        "VECTOR_SEARCH",
        "SUCCESS",
        "OK",
        len(results),
        container_url,
    )
    return {"status": "OK", "count": len(results), "results": results}, 200
