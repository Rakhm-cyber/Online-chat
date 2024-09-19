FROM redis
COPY ./redis_configs/redis.conf /usr/local/etc/redis/redis.conf
ENTRYPOINT ["redis-server", "/usr/local/etc/redis/redis.conf"]
