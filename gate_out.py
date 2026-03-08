import datetime
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///parking.db")

def vehicle_exit(plate, student_id):

    with engine.begin() as conn:

        row = conn.execute(
            text("""
            SELECT id FROM parking_log
            WHERE plate=:p AND time_out IS NULL
            ORDER BY id DESC LIMIT 1
            """),
            {"p": plate}
        ).fetchone()

        if row:

            conn.execute(
                text("""
                UPDATE parking_log
                SET time_out=:t, gate_out='gate1'
                WHERE id=:id
                """),
                {
                    "t": datetime.datetime.now().isoformat(),
                    "id": row[0]
                }
            )

            print("OPEN EXIT BARRIER")

        else:
            print("NO VEHICLE FOUND")


if __name__ == "__main__":

    plate = input("Plate: ")
    student = input("Student ID from QR: ")

    vehicle_exit(plate, student)