"""Regression checks using an isolated SQLite database, without Telegram calls."""
import asyncio
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN="123456:test", ADMIN_IDS="", MYSQL_URL="", DATABASE_URL="")

import main
import db_backend


class QuizRewardTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        db_backend._sqlite_path = ""
        main.DB_PATH = str(Path(self.temp.name) / "test.db")
        await main.init_db()
        self.user = await main.create_user(123, None, "Test", "1234")

    async def asyncTearDown(self):
        db_backend._sqlite_path = ""
        self.temp.cleanup()

    async def reward(self):
        return await main.grant_activity_once(
            self.user["id"], main.ACTIVITY_QUIZ_REWARD, None, 0
        )

    async def counts(self):
        async with db_backend.db_session() as db:
            values = []
            for query in (
                "SELECT balance FROM users",
                "SELECT COUNT(*) FROM quiz_awards",
                "SELECT COUNT(*) FROM transactions",
            ):
                cursor = await db.execute(query)
                values.append((await cursor.fetchone())[0])
            return values

    async def test_concurrent_retries_award_only_once(self):
        results = await asyncio.gather(self.reward(), self.reward())
        self.assertEqual(sum(result[0] for result in results), 1)
        self.assertEqual(await self.counts(), [10, 1, 1])

    async def test_failed_balance_update_rolls_back_and_allows_retry(self):
        async with db_backend.db_session() as db:
            await db.execute("""CREATE TRIGGER fail_balance BEFORE UPDATE OF balance ON users
                BEGIN SELECT RAISE(ABORT, 'simulated failure'); END""")
            await db.commit()
        with self.assertRaisesRegex(Exception, "simulated failure"):
            await self.reward()
        self.assertEqual(await self.counts(), [0, 0, 0])
        async with db_backend.db_session() as db:
            await db.execute("DROP TRIGGER fail_balance")
            await db.commit()
        self.assertTrue((await self.reward())[0])
        self.assertEqual(await self.counts(), [10, 1, 1])

    async def test_limit_does_not_mark_question_awarded(self):
        async with db_backend.db_session() as db:
            await db.execute("UPDATE activities SET limit_per_user = 0 WHERE title = ?",
                             (main.ACTIVITY_QUIZ_REWARD,))
            await db.commit()
        self.assertFalse((await self.reward())[0])
        self.assertEqual(await self.counts(), [0, 0, 0])


if __name__ == "__main__":
    unittest.main()
