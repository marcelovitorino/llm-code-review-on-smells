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
            WHERE table_name = 'llm_prompt_results'
              AND column_name IN ('dataset_id', 'mlcq_file_id')
            """
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                ALTER TABLE llm_prompt_results
                ADD COLUMN mlcq_file_id INTEGER
                """
            )
    else:
        cursor.execute(
            """
            CREATE TABLE llm_prompt_results (
                id SERIAL PRIMARY KEY,
                experiment_id INTEGER NOT NULL REFERENCES experiment_setup(id) ON DELETE CASCADE,
                prompt_id INTEGER NOT NULL REFERENCES prompt(id) ON DELETE CASCADE,
                mlcq_file_id INTEGER,
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
    cursor.execute(
        """
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'mlcq_samples'
        """
    )
    if cursor.fetchone():
        cursor.execute("ALTER TABLE mlcq_samples RENAME TO mlcq_smell_occurrences")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mlcq_smell_occurrences (
            id INTEGER PRIMARY KEY,
            repo_url TEXT NOT NULL,
            commit_hash TEXT NOT NULL,
            file_path TEXT NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            code_snippet TEXT,
            file_content TEXT,
            smell TEXT NOT NULL,
            severity TEXT NOT NULL,
            type TEXT,
            code_name TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mlcq_files (
            id SERIAL PRIMARY KEY,
            repo_url TEXT NOT NULL,
            commit_hash TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_content TEXT,
            annotated_smells TEXT[] NOT NULL,
            annotation_count INTEGER NOT NULL,
            smell_occurrence_ids INTEGER[] NOT NULL,
            UNIQUE (repo_url, commit_hash, file_path)
        )
        """
    )
    cursor.execute(
        """
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'llm_prompt_results' AND column_name = 'dataset_id'
        """
    )
    if cursor.fetchone():
        cursor.execute(
            """
            ALTER TABLE llm_prompt_results
            ALTER COLUMN dataset_id TYPE INTEGER
            USING NULLIF(dataset_id, '')::INTEGER
            """
        )
        cursor.execute(
            "ALTER TABLE llm_prompt_results RENAME COLUMN dataset_id TO mlcq_file_id"
        )
    cursor.execute(
        """
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'llm_prompt_results'
          AND constraint_name = 'llm_prompt_results_mlcq_file_id_fkey'
        """
    )
    if not cursor.fetchone():
        cursor.execute(
            """
            ALTER TABLE llm_prompt_results
            ADD CONSTRAINT llm_prompt_results_mlcq_file_id_fkey
                FOREIGN KEY (mlcq_file_id) REFERENCES mlcq_files(id) ON DELETE CASCADE
            """
        )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluation_labels (
            id SERIAL PRIMARY KEY,
            llm_result_id INTEGER NOT NULL REFERENCES llm_prompt_results(id) ON DELETE CASCADE,
            smell_occurrence_id INTEGER NOT NULL REFERENCES mlcq_smell_occurrences(id) ON DELETE CASCADE,
            label_config_version TEXT NOT NULL,
            ls_task_id INTEGER NOT NULL,
            ls_annotation_id INTEGER NOT NULL,
            annotator TEXT NOT NULL,
            label CHAR(1) NOT NULL CHECK (label IN ('I','H','M','U')),
            needs_review BOOLEAN NOT NULL DEFAULT FALSE,
            comment TEXT,
            lead_time_seconds DOUBLE PRECISION,
            created_at TIMESTAMPTZ NOT NULL,
            UNIQUE (llm_result_id, smell_occurrence_id, annotator)
        )
        """
    )
    connection.commit()
