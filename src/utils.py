def chunks(elems, chunk_size):
    chunk_size = max(1, chunk_size)
    return list(elems[i : i + chunk_size] for i in range(0, len(elems), chunk_size))
