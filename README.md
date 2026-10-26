# Make It With Out SQL
## Description 
This is an ORM (Object Relational Mapping) library for Python that allows you to interact with a sql database using Python objects. 

## Installation
```python
pip install MIWOS
```
## Getting Started
### Prerequisites
- Python 3.13 or higher
- Python-venv (optional but recommended)

### Installation
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
pip install -r dev-requirements.txt

cp .env.example .env # fill in the .env file with your database credentials
```

## Batched reads

`whereIn` accepts iterables of column values and binds them as SQL parameters on
SQLite and MariaDB. Filters can be chained with `where`, `whereNot`, `orderBy`
and `limit`. An empty iterable matches no rows; `None` includes SQL `NULL`.

```python
users = User.whereIn(discord_id=["123", "456"])
layouts = ProfileLayout.whereIn(guild_id=[None, current_guild.id])
members = GuildUser.where(guild_id=current_guild.id).whereIn(user_id=[1, 2])
```

Use `withRelations` to load declared `BelongsTo` relations in batches instead of
issuing a query for every row:

```python
leaders = (GuildUser.where(guild_id=current_guild.id)
           .orderBy("monthly_point DESC").limit(10).withRelations("user"))
for leader in leaders:
    print(leader.user.discord_id, leader.monthly_point)
```

This performs two queries for ten leaders: one for the leaders and one for their
users. Collections remain lazy until read. Each relation uses batches of at most
500 distinct identifiers. Multiple relation names are supported, including after
a collection has been fetched; unknown names raise `ValueError`. Only direct
`BelongsTo` relations are supported. Related model modules must be imported first.

Prefetched relations are snapshots stored on the returned instances, with no
global data cache. Assigning a relation or its foreign key invalidates its
snapshot. Fetch a new collection to observe changes made elsewhere.

Every `HasMany` access creates an independent query, so pending collections can
be filtered or fetched without modifying another collection or the parent's
save query. Saving an unchanged persisted model still runs its hooks but does
not issue an empty SQL update.

SQLite connections are reused within each thread and reopened when the configured
database path changes. Create and use queries in the same thread. Failed commits
roll back, and `SQLiteQueryExecutor.close()` closes the current thread's connection.

## Tests

From this repository, using Python 3.13 or newer with the dependencies installed:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The query tests use temporary SQLite databases and check query counts, relation
isolation, SQL parameter binding, null filters, connection lifecycle and rollback.
