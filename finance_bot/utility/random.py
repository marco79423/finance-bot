from snowflake import SnowflakeGenerator

gen = SnowflakeGenerator(42)


def generate_id():
    return next(gen)
