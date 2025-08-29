"""Prometheus metrics for the tokenizer service."""
# TODO: disable use in development environments to avoid log spam.

from __future__ import annotations

from typing import ClassVar

from prometheus_client import CollectorRegistry, Counter, Histogram


class Metrics:
    """Prometheus metrics for the tokenizer service."""

    _instance: ClassVar[Metrics | None] = None
    _registry: ClassVar[CollectorRegistry] = CollectorRegistry()

    FUNCTION_LATENCY: Histogram
    HERMES_FAILURE_COUNT: Counter
    TOKEN_METRICS: Histogram
    MESSAGE_METRICS: Histogram
    CONTINUATION_ATTEMPTS: Counter
    UNSAFE_CHUNK_COUNTER: Counter

    def __new__(cls):
        """Singleton pattern that allows arbitrary arguments."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialize_metrics(cls._instance)
        return cls._instance

    @classmethod
    def _initialize_metrics(cls, instance):
        """Initialize metrics."""
        instance.FUNCTION_LATENCY = Histogram(
            "tokenizer_function_latency_seconds",
            "Function latency (seconds)",
            buckets=[
                0.001,
                0.003,
                0.005,
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
                15.0,
                20.0,
                25.0,
                30.0,
                float("inf"),
            ],
            labelnames=["function"],
            registry=cls._registry,
        )

        instance.HERMES_FAILURE_COUNT = Counter(
            "tokenizer_hermes_failure_count",
            "Number of failures when calling Hermes",
            labelnames=["reason"],
            registry=cls._registry,
        )

        instance.UNSAFE_CHUNK_COUNTER = Counter(
            "tokenizer_unsafe_chunk_counter",
            "The number of chunks at which safety filter was triggered.",
            labelnames=["initial_or_continuation", "chunk_counter", "model_server_url"],
            registry=cls._registry,
        )

        instance.CONTINUATION_ATTEMPTS = Counter(
            "tokenizer_continuation_attempts",
            "Number of continuation attempts",
            labelnames=["reason", "continuations", "model_server_url"],
            registry=cls._registry,
        )

        instance.HERMES_TEMPLATE_NAME = Counter(
            "tokenizer_hermes_template_name",
            "Count the number of times a specific template name is used.",
            labelnames=["template_name", "template_dir", "source"],
            registry=cls._registry,
        )

        instance.TOKEN_METRICS = Histogram(
            "tokenizer_token_metrics",
            "Metrics reflecting how tokens are handled in tokenizer.",
            buckets=[
                1000,
                1500,
                2000,
                2500,
                3000,
                3500,
                4000,
                5000,
                6000,
                7000,
                8000,
                9000,
                10000,
                15000,
                20000,
                25000,
                30000,
                35000,
                40000,
                45000,
                50000,
                60000,
                70000,
                80000,
                90000,
                100000,
                250000,
                500000,
                750000,
                1000000,
                float("inf"),
            ],
            labelnames=["metric_type"],
            registry=cls._registry,
        )

        instance.MESSAGE_METRICS = Histogram(
            "tokenizer_message_metrics",
            "Metrics reflecting how messages are handled in tokenizer.",
            buckets=[
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                15,
                20,
                25,
                30,
                35,
                40,
                45,
                50,
                60,
                70,
                80,
                90,
                100,
                150,
                200,
                250,
                300,
                350,
                400,
                450,
                500,
                600,
                700,
                800,
                900,
                1000,
                1250,
                1500,
                1750,
                2000,
                2500,
                3000,
                3500,
                4000,
                4500,
                5000,
                10000,
                20000,
                50000,
                float("inf"),
            ],
            labelnames=["metric_type"],
            registry=cls._registry,
        )
