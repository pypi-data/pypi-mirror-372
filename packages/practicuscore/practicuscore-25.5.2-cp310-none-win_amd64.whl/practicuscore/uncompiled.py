class SQLHelper:
    @staticmethod
    def run_sql(query, table__4__sql, sql: str):
        _ = table__4__sql
        return query(sql).to_df()
