CREATE KEYSPACE demo_callcentre WITH replication = {'class': 'NetworkTopologyStrategy', 'caas-dc': '3'}  AND durable_writes = true;

CREATE TABLE demo_callcentre.job_status (
    job_id text PRIMARY KEY,
    last_update_time timestamp,
    status text
) WITH additional_write_policy = '99PERCENTILE'
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'chunk_length_in_kb': '64', 'class': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND crc_check_chance = 1.0
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND nodesync = {'enabled': 'true', 'incremental': 'true'}
    AND read_repair = 'BLOCKING'
    AND speculative_retry = '99PERCENTILE';
CREATE CUSTOM INDEX status_idx ON demo_callcentre.job_status (status) USING 'StorageAttachedIndex';

CREATE TABLE demo_callcentre.call_centre_voice_source (
    call_id uuid PRIMARY KEY,
    call_audio_filetype text,
    call_s3_link text,
    created_time timestamp,
    last_updated timestamp,
    process_status text,
    transcript text
) WITH additional_write_policy = '99PERCENTILE'
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'chunk_length_in_kb': '64', 'class': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND crc_check_chance = 1.0
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND nodesync = {'enabled': 'true', 'incremental': 'true'}
    AND read_repair = 'BLOCKING'
    AND speculative_retry = '99PERCENTILE';
CREATE CUSTOM INDEX process_status_idx ON demo_callcentre.call_centre_voice_source (process_status) USING 'StorageAttachedIndex';
CREATE CUSTOM INDEX call_audio_filetype_idx ON demo_callcentre.call_centre_voice_source (call_audio_filetype) USING 'StorageAttachedIndex';