from yoyo import step

steps = [
    step(
        """
        CREATE SCHEMA IF NOT EXISTS roots_vision;
        """,
        """
        DROP SCHEMA IF EXISTS roots_vision;
        """
    )
]
