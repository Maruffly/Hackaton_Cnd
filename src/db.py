from sqlalchemy import create_engine

def get_engine(db_url):
    if not db_url:
        return None
    return create_engine(db_url, pool_pre_ping=True)


def write_chunk_to_db(chunk, engine, table_name):
    if engine is None:
        return
    chunk.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )
