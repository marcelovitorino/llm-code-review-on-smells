import psycopg2

from start_here.experiments.constants import (
    RESULTS_DATABASE_NAME,
    RESULTS_DATABASE_HOST,
    RESULTS_DATABASE_PORT,
    RESULTS_DATABASE_USER,
    RESULTS_DATABASE_PASSWORD,
)


def ensure_schema(connection: psycopg2.extensions.connection) -> None:
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS experiment_setup (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            model_key TEXT NOT NULL,
            temperature DOUBLE PRECISION NOT NULL,
            top_p DOUBLE PRECISION NOT NULL,
            max_tokens INTEGER NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prompt (
            id SERIAL PRIMARY KEY,
            experiment_id INTEGER NOT NULL REFERENCES experiment_setup(id) ON DELETE CASCADE,
            prompt_text TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'prompt' AND column_name = 'order_index'
        """
    )
    if cursor.fetchone():
        cursor.execute("ALTER TABLE prompt DROP COLUMN order_index")
    cursor.execute(
        """
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'llm_prompt_results'
        """
    )
    if cursor.fetchone():
        cursor.execute(
            """
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'llm_prompt_results' AND column_name = 'experiment_id'
            """
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                ALTER TABLE llm_prompt_results
                ADD COLUMN experiment_id INTEGER REFERENCES experiment_setup(id) ON DELETE CASCADE
                """
            )
            cursor.execute(
                """
                ALTER TABLE llm_prompt_results
                ADD COLUMN prompt_id INTEGER REFERENCES prompt(id) ON DELETE CASCADE
                """
            )
        cursor.execute(
            """
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'llm_prompt_results' AND column_name = 'dataset_id'
            """
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                ALTER TABLE llm_prompt_results
                ADD COLUMN dataset_id TEXT
                """
            )
    else:
        cursor.execute(
            """
            CREATE TABLE llm_prompt_results (
                id SERIAL PRIMARY KEY,
                experiment_id INTEGER NOT NULL REFERENCES experiment_setup(id) ON DELETE CASCADE,
                prompt_id INTEGER NOT NULL REFERENCES prompt(id) ON DELETE CASCADE,
                dataset_id TEXT,
                model_key TEXT NOT NULL,
                model_name TEXT NOT NULL,
                prompt TEXT NOT NULL,
                response TEXT,
                timestamp TEXT NOT NULL,
                duration_seconds DOUBLE PRECISION NOT NULL,
                success BOOLEAN NOT NULL,
                error TEXT
            )
            """
        )
    connection.commit()
