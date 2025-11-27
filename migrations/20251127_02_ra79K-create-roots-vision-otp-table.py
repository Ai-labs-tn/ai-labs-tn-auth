"""
create_roots_vision_otp_table
"""

from yoyo import step

__depends__ = {'20251127_01_vlNY9-create-roots-vision-schema'}

steps = [
    step(
        # --- UP ---
        """
        CREATE TABLE IF NOT EXISTS roots_vision.otp (
          id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
          user_id text NOT NULL,
          email text,
          phone text,
          otp_hash text NOT NULL,
          purpose text NOT NULL,
          created_at timestamptz NOT NULL DEFAULT now(),
          expires_at timestamptz NOT NULL,
          consumed_at timestamptz,
          retry_count int NOT NULL DEFAULT 0,
          CHECK (email IS NOT NULL OR phone IS NOT NULL)
        );

        CREATE INDEX IF NOT EXISTS idx_otp_purpose
          ON roots_vision.otp (user_id, purpose, created_at);
        """,
        
        """
        DROP INDEX IF EXISTS roots_vision.idx_otp_purpose;
        DROP TABLE IF EXISTS roots_vision.otp;
        """
    )
]
