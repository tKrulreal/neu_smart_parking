from sqlalchemy import create_engine, text

# engine = create_engine("sqlite:///parking.db", future=True)
#
# with engine.begin() as conn:
#     conn.execute(text("""
#     CREATE TABLE IF NOT EXISTS vehicle (
#         plate TEXT PRIMARY KEY,
#         student_id TEXT NOT NULL
#     );
#     """))
#     conn.execute(text("""
#     CREATE TABLE IF NOT EXISTS parking_log (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         plate TEXT NOT NULL,
#         time_in TEXT NOT NULL,
#         time_out TEXT,
#         gate_in TEXT,
#         gate_out TEXT
#     );
#     """))
#
#     # dữ liệu mẫu
#     conn.execute(text("INSERT OR IGNORE INTO vehicle(plate, student_id) VALUES (:p,:s)"),
#                  [{"p":"29X-12345","s":"20211234"}])
#
# print("OK: parking.db created")
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///parking.db")

with engine.begin() as conn:
    conn.execute(text("""
    INSERT OR IGNORE INTO vehicle(plate, student_id)
    VALUES ('29-G1 333.33', '20211234')
    """))