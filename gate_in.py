import datetime
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///parking.db")

def vehicle_enter(plate):

    with engine.begin() as conn:

        student = conn.execute(
            text("SELECT student_id FROM vehicle WHERE plate=:p"),
            {"p": plate}
        ).fetchone()

        if student:

            conn.execute(
                text("""
                INSERT INTO parking_log (plate, time_in, gate_in)
                VALUES (:p, :t, 'gate2')
                """),
                {
                    "p": plate,
                    "t": datetime.datetime.now().isoformat()
                }
            )

            print("OPEN BARRIER")
            print("Student:", student[0])

        else:
            print("DENY - UNKNOWN VEHICLE")


if __name__ == "__main__":
    plate = input("Enter detected plate: ")
    vehicle_enter(plate)