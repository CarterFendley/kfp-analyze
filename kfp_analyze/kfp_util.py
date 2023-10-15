def transformer_disable_caching(op):
    op.execution_options.caching_strategy.max_cache_staleness = "P0D"