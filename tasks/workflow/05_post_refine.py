import argparse
import sys
from pathlib import Path

FILE_PATH = Path(__file__).absolute()
BASE_DIR = FILE_PATH.parent.parent.parent
sys.path.insert(0, str(BASE_DIR))  # run code in any path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run post-refine pipeline")
    parser.add_argument("--task_id", required=True, help="Target task ID")
    parser.add_argument(
        "--start-stage",
        choices=["rag", "rewrite", "figure", "rule", "tables"],
        default="rag",
        help="從指定階段開始執行 post-refine 流程",
    )
    parser.add_argument(
        "--mainbody-path",
        help="自訂輸入主體的路徑（預設使用 pipeline 內建路徑）",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    from src.models.post_refine import PostRefiner

    post_refiner = PostRefiner(args.task_id)

    mainbody_path = Path(args.mainbody_path) if args.mainbody_path else None
    post_refiner.run(mainbody_path=mainbody_path, start_stage=args.start_stage)
