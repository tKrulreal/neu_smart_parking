import argparse


def build_parser():
    parser = argparse.ArgumentParser(description="NEU Smart Parking")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init-db", help="Khoi tao DB")

    enter_cmd = sub.add_parser("enter", help="Cong vao: quet anh bien so")
    enter_cmd.add_argument("--image", required=True, help="Anh bien so xe vao")
    enter_cmd.add_argument("--gate", default="gate2", help="Ten cong vao")

    exit_cmd = sub.add_parser("exit", help="Cong ra: quet bien so + QR")
    exit_cmd.add_argument("--plate-image", required=True, help="Anh bien so xe ra")
    exit_cmd.add_argument("--gate", default="gate1", help="Ten cong ra")
    exit_cmd.add_argument("--qr-mode", choices=["camera", "image"], default="camera")
    exit_cmd.add_argument("--qr-image", default=None, help="Anh QR neu mode=image")
    exit_cmd.add_argument("--camera", type=int, default=0, help="Camera index")
    exit_cmd.add_argument("--timeout", type=int, default=20, help="Timeout quet QR")
    exit_cmd.add_argument(
        "--qr-max-age-minutes",
        type=int,
        default=5,
        help="So phut QR con hieu luc",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "init-db":
        from db_init import init_db

        init_db()
        return

    if args.cmd == "enter":

        from gate_in import vehicle_enter_from_image


        vehicle_enter_from_image(args.image, args.gate)
        return

    if args.cmd == "exit":

        from gate_out import vehicle_exit


        vehicle_exit(
            plate_image_path=args.plate_image,
            gate_name=args.gate,
            use_camera_qr=(args.qr_mode == "camera"),
            qr_image_path=args.qr_image,
            camera_index=args.camera,
            qr_timeout_sec=args.timeout,
            qr_max_age_minutes=args.qr_max_age_minutes,
        )
        return


if __name__ == "__main__":
    main()
