"""
Local database management for Clyrdia CLI - handles SQLite storage.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from ..models.results import BenchmarkResult
from ..core.console import console

class LocalDatabase:
    """Local SQLite database for zero-knowledge storage"""
    
    def __init__(self):
        self.db_path = Path.home() / ".clyrdia" / "clyrdia.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            # Create the main benchmark_results table that the dashboard expects
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    benchmark_id TEXT NOT NULL,
                    benchmark_name TEXT,
                    model TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    prompt TEXT,
                    response TEXT,
                    latency_ms INTEGER,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    cost REAL,
                    success BOOLEAN,
                    error TEXT,
                    quality_score REAL,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmarks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    config TEXT,
                    tags TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    benchmark_id TEXT,
                    model TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    prompt TEXT,
                    response TEXT,
                    latency_ms INTEGER,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    cost REAL,
                    success BOOLEAN,
                    error TEXT,
                    quality_scores TEXT,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (benchmark_id) REFERENCES benchmarks(id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    model TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS drift_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model TEXT NOT NULL,
                    test_hash TEXT NOT NULL,
                    drift_score REAL,
                    details TEXT,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_results_benchmark ON benchmark_results(benchmark_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_results_model ON benchmark_results(model)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_results_timestamp ON benchmark_results(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_benchmark ON results(benchmark_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_model ON results(model)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_results_timestamp ON results(timestamp)")
    
    def save_benchmark(self, benchmark_id: str, name: str, description: str, config: Dict, tags: List[str]) -> str:
        """Save benchmark configuration"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO benchmarks (id, name, description, config, tags) VALUES (?, ?, ?, ?, ?)",
                (benchmark_id, name, description, json.dumps(config), json.dumps(tags))
            )
        return benchmark_id
    
    def save_result(self, result: BenchmarkResult, benchmark_id: Optional[str] = None) -> int:
        """Save benchmark result to both tables for compatibility"""
        with sqlite3.connect(self.db_path) as conn:
            # Save to the original results table
            cursor = conn.execute(
                """INSERT INTO results 
                   (benchmark_id, model, provider, test_name, prompt, response, 
                    latency_ms, input_tokens, output_tokens, cost, success, error, 
                    quality_scores, metadata, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    benchmark_id,
                    result.model,
                    result.provider,
                    result.test_name,
                    result.prompt,
                    result.response,
                    result.latency_ms,
                    result.input_tokens,
                    result.output_tokens,
                    result.cost,
                    result.success,
                    result.error,
                    json.dumps(result.quality_scores),
                    json.dumps(result.metadata),
                    result.timestamp
                )
            )
            
            # Also save to the benchmark_results table that the dashboard expects
            # Extract quality score (use first score if multiple, or 0.0 if none)
            quality_score = 0.0
            if result.quality_scores and len(result.quality_scores) > 0:
                if isinstance(result.quality_scores, dict):
                    quality_score = list(result.quality_scores.values())[0]
                elif isinstance(result.quality_scores, list):
                    quality_score = result.quality_scores[0]
                else:
                    quality_score = float(result.quality_scores)
            
            # Get benchmark name if available
            benchmark_name = None
            if benchmark_id:
                try:
                    name_cursor = conn.execute(
                        "SELECT name FROM benchmarks WHERE id = ?",
                        (benchmark_id,)
                    )
                    name_row = name_cursor.fetchone()
                    if name_row:
                        benchmark_name = name_row[0]
                except:
                    pass
            
            conn.execute(
                """INSERT INTO benchmark_results 
                   (benchmark_id, benchmark_name, model, provider, test_name, prompt, response, 
                    latency_ms, input_tokens, output_tokens, cost, success, error, 
                    quality_score, metadata, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    benchmark_id,
                    benchmark_name,
                    result.model,
                    result.provider,
                    result.test_name,
                    result.prompt,
                    result.response,
                    result.latency_ms,
                    result.input_tokens,
                    result.output_tokens,
                    result.cost,
                    result.success,
                    result.error,
                    quality_score,
                    json.dumps(result.metadata),
                    result.timestamp
                )
            )
            
            return cursor.lastrowid
    
    def get_recent_benchmarks(self, limit: int = 10) -> List[Dict]:
        """Get recent benchmark runs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM benchmarks ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_model_performance(self, model: str, days: int = 30) -> pd.DataFrame:
        """Get model performance over time"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT timestamp, latency_ms, cost, success, quality_scores
                FROM results
                WHERE model = ? AND timestamp > datetime('now', '-{} days')
                ORDER BY timestamp
            """.format(days)
            return pd.read_sql_query(query, conn, params=(model,))
    
    def migrate_existing_data(self) -> int:
        """Migrate existing data from results table to benchmark_results table"""
        migrated_count = 0
        with sqlite3.connect(self.db_path) as conn:
            # Check if there's data to migrate
            cursor = conn.execute("SELECT COUNT(*) FROM results")
            total_results = cursor.fetchone()[0]
            
            if total_results == 0:
                return 0
            
            # Check if benchmark_results already has data
            cursor = conn.execute("SELECT COUNT(*) FROM benchmark_results")
            existing_benchmark_results = cursor.fetchone()[0]
            
            if existing_benchmark_results > 0:
                return 0  # Already migrated
            
            console.print(f"[yellow]🔄 Migrating {total_results} existing results to dashboard format...[/yellow]")
            
            # Get all results and migrate them
            cursor = conn.execute("""
                SELECT r.*, b.name as benchmark_name
                FROM results r
                LEFT JOIN benchmarks b ON r.benchmark_id = b.id
                ORDER BY r.timestamp
            """)
            
            for row in cursor.fetchall():
                # Extract quality score
                quality_score = 0.0
                if row['quality_scores']:
                    try:
                        scores = json.loads(row['quality_scores'])
                        if isinstance(scores, dict) and scores:
                            quality_score = list(scores.values())[0]
                        elif isinstance(scores, list) and scores:
                            quality_score = scores[0]
                        else:
                            quality_score = float(scores)
                    except:
                        quality_score = 0.0
                
                # Insert into benchmark_results
                conn.execute("""
                    INSERT INTO benchmark_results 
                    (benchmark_id, benchmark_name, model, provider, test_name, prompt, response, 
                     latency_ms, input_tokens, output_tokens, cost, success, error, 
                     quality_score, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['benchmark_id'],
                    row['benchmark_name'],
                    row['model'],
                    row['provider'],
                    row['test_name'],
                    row['prompt'],
                    row['response'],
                    row['latency_ms'],
                    row['input_tokens'],
                    row['output_tokens'],
                    row['cost'],
                    row['success'],
                    row['error'],
                    quality_score,
                    row['metadata'],
                    row['timestamp']
                ))
                migrated_count += 1
            
            conn.commit()
            console.print(f"[green]✅ Successfully migrated {migrated_count} results[/green]")
        
        return migrated_count
