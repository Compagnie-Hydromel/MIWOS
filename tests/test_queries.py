from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from MIWOS.config import DBConfig
from MIWOS.libs.sql.association import BelongsTo, HasMany
from MIWOS.libs.sql.queryexecutor.sqlite import SQLiteQueryExecutor
from MIWOS.libs.sql.querygenerator.mariadb import MariaDBQueryGenerator
from MIWOS.libs.sql.querygenerator.sqlite import SQLiteQueryGenerator
from MIWOS.model import Model


class QueryAuthor(Model):
    _table_name = "authors"
    _has_many = [
        HasMany("articles", class_name="QueryArticle", foreign_key="author_id")]


class QueryArticle(Model):
    _table_name = "articles"
    _belongs_to = [BelongsTo("author", class_name="QueryAuthor")]


class QueryByline(QueryArticle):
    _belongs_to = [
        BelongsTo("writer", class_name="QueryAuthor", foreign_key="author_id")]


class TestQueryGenerator(unittest.TestCase):
    def test_in_values_are_bound_for_both_backends(self):
        for generator, placeholder in ((MariaDBQueryGenerator, "%s"), (SQLiteQueryGenerator, "?")):
            with self.subTest(generator=generator):
                query = generator("articles")
                query.select("*")
                query.where(author_id=2)
                query.where_in(title=["a' OR 1=1 --", "b"])
                self.assertIn(
                    f"title IN ({placeholder}, {placeholder})", query.query)
                self.assertNotIn("OR 1=1", query.query)
                self.assertEqual(query.arguments, [2, "a' OR 1=1 --", "b"])

    def test_empty_and_null_filters(self):
        for generator in (MariaDBQueryGenerator, SQLiteQueryGenerator):
            with self.subTest(generator=generator):
                query = generator("articles")
                query.select()
                query.where()
                query.where(author_id=None)
                query.where_not(title=None)
                query.where_in(id=[])
                self.assertIn(
                    "WHERE author_id IS NULL AND title IS NOT NULL AND 1=0", query.query)
                self.assertEqual(query.arguments, [])


class TestSQLiteQueries(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.database = str(Path(directory.name) / "test.sqlite3")
        config = patch.dict(DBConfig._config, db_connector="sqlite",
                            db_database=self.database, sql_log_file="")
        config.start()
        self.addCleanup(config.stop)
        self.executor = SQLiteQueryExecutor(self.database)
        self.addCleanup(self.executor.close)
        self.executor.commit(
            "CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT)")
        self.executor.commit(
            "CREATE TABLE articles (id INTEGER PRIMARY KEY, author_id INTEGER, title TEXT)")
        QueryAuthor.createOrFail(id=1, name="Alice")
        QueryAuthor.createOrFail(id=2, name="Bob")
        for id, author in ((1, 1), (2, 2), (3, 1), (4, None)):
            QueryArticle.createOrFail(
                id=id, author_id=author, title=f"Article {id}")

    def test_eager_loading_fetches_all_authors_in_two_queries(self):
        with patch.object(self.executor, "execute", wraps=self.executor.execute) as execute:
            articles = list(QueryArticle.orderBy("id").withRelations("author"))
            self.assertEqual([article.author.name if article.author else None for article in articles],
                             ["Alice", "Bob", "Alice", None])
            self.assertIs(articles[0].author, articles[2].author)
            self.assertEqual(execute.call_count, 2)

    def test_prefetch_chunks_large_collections(self):
        for id in range(3, 506):
            QueryAuthor.createOrFail(id=id, name=f"Author {id}")
            QueryArticle.createOrFail(id=id + 10, author_id=id, title="Other")
        with patch.object(self.executor, "execute", wraps=self.executor.execute) as execute:
            articles = list(QueryArticle.withRelations("author"))
            self.assertEqual(len(articles), 507)
            self.assertTrue(
                all(article.author is not None for article in articles if article.author_id))
            self.assertEqual(execute.call_count, 3)

    def test_eager_null_or_missing_relations_do_not_fall_back_to_extra_queries(self):
        QueryArticle.createOrFail(id=5, author_id=999, title="Orphan")
        with patch.object(self.executor, "execute", wraps=self.executor.execute) as execute:
            articles = list(QueryArticle.whereIn(
                id=[4, 5]).withRelations("author"))
            self.assertEqual(
                [article.author for article in articles], [None, None])
            self.assertEqual(execute.call_count, 2)
        with patch.object(self.executor, "execute", wraps=self.executor.execute) as execute:
            self.assertEqual(list(QueryArticle.whereIn(
                id=[]).withRelations("author")), [])
            self.assertEqual(execute.call_count, 1)

    def test_prefetch_is_invalidated_when_foreign_key_or_relation_changes(self):
        article = QueryArticle.whereIn(id=[1]).withRelations("author")[0]
        self.assertEqual(article.author.name, "Alice")
        article.author_id = 2
        self.assertEqual(article.author.name, "Bob")
        article.saveOrFail()
        self.assertEqual(article.author.name, "Bob")
        article.author = QueryAuthor.find(1)
        article.saveOrFail()
        self.assertEqual(article.author.name, "Alice")

    def test_where_in_includes_null_and_preserves_other_filters(self):
        articles = QueryArticle.whereNot(id=2).whereIn(
            author_id=[None, 1]).orderBy("id")
        self.assertEqual([article.id for article in articles], [1, 3, 4])
        self.assertEqual(
            [article.id for article in QueryArticle.where(author_id=None)], [4])
        self.assertEqual(len(QueryArticle.whereNot(author_id=None)), 3)

    def test_prefetch_uses_explicit_class_and_foreign_key(self):
        article = QueryByline.whereIn(id=[1]).withRelations("writer")[0]
        self.assertEqual(article.writer.name, "Alice")
        article.writer = QueryAuthor.find(2)
        article.saveOrFail()
        self.assertEqual(article.writer.name, "Bob")
        self.assertEqual(QueryArticle.find(1).author_id, 2)

    def test_prefetch_during_pending_relation_changes_does_not_leave_a_stale_snapshot(self):
        articles = QueryArticle.whereIn(id=[1])
        article = articles[0]
        article.author = QueryAuthor.find(2)
        articles.withRelations("author")
        article.saveOrFail()
        self.assertEqual(article.author.name, "Bob")

    def test_chained_relation_filters_convert_models_to_foreign_keys(self):
        author = QueryAuthor.find(1)
        self.assertEqual(
            [article.id for article in QueryArticle.all().where(author=author)], [1, 3])

    def test_relation_queries_and_writes_remain_independent(self):
        author = QueryAuthor.find(1)
        first = author.articles.where(id=1)
        second = author.articles.where(id=3)
        author.name = "Updated"
        author.saveOrFail()
        self.assertEqual([article.id for article in second], [3])
        self.assertEqual([article.id for article in first], [1])
        self.assertEqual(QueryAuthor.find(1).name, "Updated")

    def test_unchanged_save_does_not_execute_empty_sql(self):
        article = QueryArticle.find(1)
        with patch.object(self.executor, "execute", wraps=self.executor.execute) as execute:
            article.saveOrFail()
            execute.assert_not_called()

    def test_prefetch_can_be_added_to_a_fetched_collection(self):
        articles = QueryArticle.all()
        self.assertEqual(len(articles), 4)
        with patch.object(self.executor, "execute", wraps=self.executor.execute) as execute:
            articles.withRelations("author")
            self.assertEqual(articles[0].author.name, "Alice")
            self.assertEqual(execute.call_count, 1)
        with self.assertRaises(ValueError):
            QueryArticle.withRelations("not_a_relation")

    def test_sqlite_reconnects_when_the_database_changes(self):
        other = str(Path(self.database).with_name("other.sqlite3"))
        SQLiteQueryExecutor(other).commit(
            "CREATE TABLE only_in_other (id INTEGER)")
        original = SQLiteQueryExecutor(self.database)
        self.assertEqual(len(original.execute(
            "SELECT * FROM authors", many=True)), 2)
        self.assertIsNone(original.execute(
            "SELECT name FROM sqlite_master WHERE name='only_in_other'"))

    def test_sqlite_uses_a_connection_per_thread(self):
        def read_from_thread():
            executor = SQLiteQueryExecutor(self.database)
            try:
                return executor.execute("SELECT COUNT(*) AS total FROM authors")["total"]
            finally:
                executor.close()
        with ThreadPoolExecutor(max_workers=1) as pool:
            self.assertEqual(pool.submit(read_from_thread).result(), 2)
        self.assertEqual(QueryAuthor.find(1).name, "Alice")

    def test_failed_write_rolls_back_and_allows_following_writes(self):
        with self.assertRaises(sqlite3.IntegrityError):
            QueryAuthor.createOrFail(id=1, name="Duplicate")
        QueryAuthor.createOrFail(id=3, name="Charlie")
        self.assertEqual(QueryAuthor.find(3).name, "Charlie")


if __name__ == "__main__":
    unittest.main()
