"""Create a private .env with a random secret, without overwriting an existing one."""

from pathlib import Path
import secrets


def main():
    root = Path(__file__).resolve().parent.parent
    destination = root / ".env"
    contents = (root / ".env.example").read_text(encoding="utf-8")
    contents = contents.replace("replace-with-a-generated-secret-key", secrets.token_urlsafe(64))
    try:
        with destination.open("x", encoding="utf-8") as output:
            output.write(contents)
    except FileExistsError:
        print("Existing .env kept. Edit it directly if you need different settings.")
    else:
        destination.chmod(0o600)
        print("Created .env with a unique secret. Do not commit or share this file.")


if __name__ == "__main__":
    main()
