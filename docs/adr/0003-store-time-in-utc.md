# ADR 0003: Store All Timestamps in Universal Coordinated Time (UTC)

- **Status**: Approved
- **Date**: 2026-07-18
- **Context**: Financial markets operate across multiple timezones (New York, London, Tokyo, Broker GMT+2/3). Mixing local broker times causes DST (Daylight Saving Time) shifts and invalid candle alignments.
- **Decision**: All storage, pipelines, models, and API payloads MUST strictly use UTC ISO8601 timestamps. Timezone conversion occurs only in the frontend UI display layer.
- **Consequences**: Guarantees zero timezone offset bugs in quantitative backtesting and AI model training datasets.
