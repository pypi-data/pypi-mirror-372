from __future__ import annotations

import datetime
import os

from ..connection import SystemSSHConnection as Connection
from ..util import build_exclude_flags_s3, build_exclude_flags_zip  # Re-use for rsync --exclude flags and zip excludes


def transfer_via_rsync(*,
                       source_instance: str,
                       dest_instance: str,
                       source_path: str,
                       dest_path: str,
                       exclude: str = "",
                       rsync_opts: str = "-avz --progress",
                       archive: bool = False,
                       operation_id: int | None = None,
                       config: dict | None = None,
                       personal_config: dict | None = None) -> None:
    """Copy *source_path* on *source_instance* directly to *dest_path* on *dest_instance*.  (Full implementation)"""

    config = config or {}
    tid = operation_id or int(datetime.datetime.utcnow().timestamp())

    exclude_flags = build_exclude_flags_s3(exclude)

    print("──────────── Transfer Context ────────────")
    print(f"🚚 Transfer ID : {tid}")
    print(f"📦 Archive mode: {archive}")
    print(f"🗂️  Exclude     : {exclude}")

    with Connection(source_instance, config, personal_config=personal_config) as src, Connection(dest_instance, config, personal_config=personal_config) as dest:

        if src.is_local and dest.is_local:
            raise ValueError("Both endpoints cannot be local. One side must be remote.")

        # Build SSH option snippets once for each endpoint
        ssh_opts_src = "-o StrictHostKeyChecking=no"
        if src.port is not None:
            ssh_opts_src += f" -p {src.port}"

        ssh_opts_dest = "-o StrictHostKeyChecking=no"
        if dest.port is not None:
            ssh_opts_dest += f" -p {dest.port}"

        if archive:
            remote_zip_path = f"/tmp/xfer_{tid}.zip"
            zip_exclude_flags = build_exclude_flags_zip(exclude)

            src_dir = os.path.dirname(source_path.rstrip("/")) or "."
            item_name = os.path.basename(source_path.rstrip("/"))
            src.run(
                f'cd "{src_dir}" && zip -r -0 "{remote_zip_path}" "{item_name}" {zip_exclude_flags}'
            )

            if dest.is_local:
                dest.run(
                    f'rsync {rsync_opts} -e "ssh {ssh_opts_src}" {src.user}@{src.host}:"{remote_zip_path}" "{remote_zip_path}"'
                )
            else:
                src.run(
                    f'rsync {rsync_opts} -e "ssh {ssh_opts_dest}" "{remote_zip_path}" {dest.user}@{dest.host}:"{remote_zip_path}"'
                )

            src.run(f'rm -f "{remote_zip_path}"')

            dest_parent = os.path.dirname(dest_path.rstrip("/")) or "."
            dest.run(
                f'mkdir -p "{dest_parent}" && unzip -o "{remote_zip_path}" -d "{dest_parent}" && rm -f "{remote_zip_path}"'
            )

        else:
            if dest.is_local:
                dest.run(
                    f'rsync {rsync_opts} {exclude_flags} -e "ssh {ssh_opts_src}" {src.user}@{src.host}:"{source_path}" "{dest_path}"'
                )
            else:
                src.run(
                    f'rsync {rsync_opts} {exclude_flags} -e "ssh {ssh_opts_dest}" "{source_path}" {dest.user}@{dest.host}:"{dest_path}"'
                )

        print("✅ Transfer completed!") 