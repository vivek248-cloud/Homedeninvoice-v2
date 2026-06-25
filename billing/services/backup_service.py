import os
import zipfile
import subprocess
from datetime import datetime

from django.conf import settings


def cleanup_old_backups(days=30):

    backup_dir = os.path.join(settings.BASE_DIR, "backups")

    if not os.path.exists(backup_dir):
        return

    now = datetime.now().timestamp()

    for filename in os.listdir(backup_dir):

        if not filename.endswith(".zip"):
            continue

        file_path = os.path.join(backup_dir, filename)

        age = (now - os.path.getctime(file_path)) / 86400

        if age > days:
            os.remove(file_path)


def create_backup():

    cleanup_old_backups()

    db = settings.DATABASES["default"]

    DB_NAME = db["NAME"]
    DB_USER = db["USER"]
    DB_PASSWORD = db["PASSWORD"]
    DB_HOST = db.get("HOST") or "localhost"
    DB_PORT = db.get("PORT") or "3306"

    backup_dir = os.path.join(settings.BASE_DIR, "backups")

    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    sql_filename = f"backup_{timestamp}.sql"
    zip_filename = f"backup_{timestamp}.zip"

    sql_path = os.path.join(backup_dir, sql_filename)
    zip_path = os.path.join(backup_dir, zip_filename)

    with open(sql_path, "w") as outfile:

        result = subprocess.run(
            [
                "mysqldump",
                f"-h{DB_HOST}",
                f"-P{DB_PORT}",
                f"-u{DB_USER}",
                f"-p{DB_PASSWORD}",
                DB_NAME,
            ],
            stdout=outfile,
            stderr=subprocess.PIPE,
            text=True,
        )

    if result.returncode != 0:
        raise Exception(result.stderr)

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as zipf:

        zipf.write(sql_path, sql_filename)

    os.remove(sql_path)

    return zip_path