import argparse
import subprocess


def run_django_command(command):
    full_command = f"python manage.py {command}"
    subprocess.call(full_command, shell=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["up", "makemigrations", "migrate"])
    parser.add_argument("extra", nargs='*', default=[])  # Captura argumentos adicionales

    args = parser.parse_args()

    if args.action == "up":
        run_django_command("runserver 0.0.0.0:8085")
    elif args.action in ["makemigrations", "migrate"]:
        extra_args = ' '.join(args.extra)
        run_django_command(f"{args.action} {extra_args}")

if __name__ == "__main__":
    main()
