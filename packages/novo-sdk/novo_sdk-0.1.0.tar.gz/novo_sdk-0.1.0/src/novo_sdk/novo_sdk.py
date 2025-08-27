import argparse
import os, shutil
import subprocess
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KeilProject:

    def __init__(self, args):
        self.uv4_path = args.uv4
        self.project_path = Path(args.project_path).resolve()

        # 构建目录结构: <project_path>/build/<test_name>
        self.build_dir = self.project_path / "build"

        # 初始化项目文件信息（将在get_project_uvprojx中动态查找）
        self.project_files = {
            'uvprojx': None,
            'uvoptx': None,
            'jlink': None
        }

        self.get_project_uvprojx()

    def get_project_uvprojx(self) -> str:
        """Get project file path (search all subdirectories for first .uvprojx file)"""
        # First check if project file has already been found
        if self.project_files['uvprojx'] and self.project_files['uvprojx'].exists():
            logger.info(f"Using found project file: {self.project_files['uvprojx']}")
            return str(self.project_files['uvprojx'])

        # Search all subdirectories for .uvprojx files
        logger.info(f"Searching for .uvprojx files in project directory {self.project_path}...")

        # Use rglob to recursively search all subdirectories
        uvprojx_files = list(self.project_path.rglob("*.uvprojx"))

        if not uvprojx_files:
            logger.error(f"No *.uvprojx files found in project directory {self.project_path} and its subdirectories")
            return ""

        # Use the first .uvprojx file found
        uvprojx_path = uvprojx_files[0]
        logger.info(f"Found project file: {uvprojx_path}")

        # Update project file information
        project_name = uvprojx_path.stem
        self.project_files = {
            'uvprojx': uvprojx_path,
            'uvoptx': uvprojx_path.parent / f"{project_name}.uvoptx",
            'jlink': uvprojx_path.parent / "JLinkSettings.ini"
        }

        # Check if related files exist
        if self.project_files['uvoptx'].exists():
            logger.info(f"Found options file: {self.project_files['uvoptx']}")
        if self.project_files['jlink'].exists():
            logger.info(f"Found JLink settings file: {self.project_files['jlink']}")

        return str(uvprojx_path)

def build(args, keilProject: KeilProject):
    """Compile firmware"""
    cmd = [
        keilProject.uv4_path,
        "-b",
        keilProject.project_files['uvprojx'],
        "-j0",
        "-o",
        f"{keilProject.build_dir}/build.log"
    ]

    cmd_str = ' '.join(str(item) for item in cmd)
    logger.info(f"Building device with command: {cmd_str}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            logger.error(f"Build failed: {result.stderr}")
            exit(1)

        logger.info("Build completed successfully")

    except subprocess.TimeoutExpired:
        logger.error("Timeout while building device")
        exit(1)
    except Exception as e:
        logger.error(f"Error building device: {e}")
        exit(1)

def flash(args, keilProject: KeilProject):
    """Flash device"""
    cmd = [
        keilProject.uv4_path,
        "-f",
        keilProject.project_files['uvprojx'],
        # Not open the Keil GUI
        "-j0",
        "-o",
        f"{keilProject.build_dir}/build.log"
    ]
    cmd_str = ' '.join(str(item) for item in cmd)
    logger.info(f"Building device with command: {cmd_str}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            logger.error(f"Flash failed: {result.stderr}")
            exit(1)

        logger.info("Flash completed successfully")

    except subprocess.TimeoutExpired:
        logger.error("Timeout while flashing device")
        exit(1)
    except Exception as e:
        logger.error(f"Error flashing device: {e}")
        exit(1)

def main():
    parser = argparse.ArgumentParser(description="Novo SDK Tool. e.g. `python project.py build`", prog="novo_sdk.py")
    parser.add_argument("--project_path",  help="Project path (default: current directory)")
    parser.add_argument("--uv4", help="Path to UV4.exe (if not specified, will use UV4_PATH environment variable)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.required = True

    # Build command
    build_parser = subparsers.add_parser("build", add_help=False)

    # Flash command
    flash_parser = subparsers.add_parser("flash", add_help=False)

    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", add_help=False)
    monitor_parser.add_argument("-p", "--port", help="monitor device port", default="")
    monitor_parser.add_argument("-b", "--baudrate", type=int, help="monitor baudrate", default=115200)

    # Clean command
    clean_parser = subparsers.add_parser("clean", add_help=False)

    args = parser.parse_args()

    if not args.uv4:
        args.uv4 = os.getenv("UV4_PATH")
        if not args.uv4:
            logger.error("UV4 path not specified. Use --uv4 or set UV4_PATH environment variable.")
            exit(1)

    if not Path(args.uv4).exists():
        logger.error(f"UV4.exe not found at specified path: {args.uv4}")
        exit(1)

    if not args.command:
        parser.print_help()
        exit(1)

    if not args.project_path:
        args.project_path = os.getcwd()

    # Check project path
    project_path = Path(args.project_path)
    if not project_path.exists():
        parser.error(f"Project path does not exist: {project_path}")

    if not project_path.is_dir():
        parser.error(f"Project path must be a directory: {project_path}")

    keilProject = KeilProject(args)

    if args.command == "build":
        return build(args, keilProject)
    elif args.command == "flash":
        return flash(args, keilProject)
    elif args.command == "clean":
        if keilProject.build_dir.exists():
            shutil.rmtree(keilProject.build_dir)
            logger.info(f"Cleaned build directory: {keilProject.build_dir}")
        else:
            logger.info(f"No build directory to clean: {keilProject.build_dir}")
    elif args.command == "monitor":
        logger.info("Monitor command not implemented yet")

    exit(0)

if __name__ == "__main__":
    main()
