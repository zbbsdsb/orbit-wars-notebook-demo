"""
Kaggle submission preparation script.

Creates a submission package for the Orbit Wars competition.

Contributors: CeaserZhao, PrismScope
"""

import os
import shutil
import tempfile
from pathlib import Path


def prepare_submission(
    output_dir: str = "submissions",
    version: str = "v1.0"
):
    """
    Prepare submission package for Kaggle.
    
    Args:
        output_dir: Directory to save submission
        version: Version string for the submission
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = version
    submission_name = f"orbit-wars-agent-{timestamp}"
    
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)
    
    print(f"Preparing submission: {submission_name}")
    
    try:
        print("  Copying main.py...")
        shutil.copy("main.py", temp_path / "main.py")
        
        print("  Copying src directory...")
        shutil.copytree("src", temp_path / "src")
        
        print("  Creating README...")
        with open(temp_path / "README.md", "w") as f:
            f.write(f"""# Orbit Wars Agent - {timestamp}

Kaggle competition submission.

## Usage

```python
from main import agent
```
""")
        
        zip_path = output_path / f"{submission_name}.zip"
        print(f"  Creating zip file: {zip_path}")
        shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", temp_dir)
        
        print("\n✅ Submission prepared successfully!")
        print(f"   File: {zip_path}")
        print("\nNext steps:")
        print(f"1. Submit using Kaggle CLI:")
        print(f"   kaggle competitions submit -c orbit-wars -f {zip_path} -m \"Heuristic Agent {timestamp}\"")
        print("\n2. Or upload directly via Kaggle website")
        
        return zip_path
        
    finally:
        shutil.rmtree(temp_dir)


def validate_agent():
    """
    Validate agent function before submission.
    
    Returns:
        True if valid, False otherwise
    """
    print("Validating agent...")
    
    try:
        from main import agent
        
        test_obs = {
            "player": 0,
            "planets": [
                [0, 0, 20.0, 20.0, 2.0, 50, 3],
                [1, 1, 80.0, 80.0, 2.0, 30, 2],
                [2, -1, 50.0, 20.0, 1.5, 20, 1],
            ],
            "fleets": [],
            "angular_velocity": 0.03,
        }
        
        test_config = {}
        result = agent(test_obs, test_config)
        
        if not isinstance(result, list):
            print(f"❌ Agent returned non-list: {type(result)}")
            return False
        
        for move in result:
            if not isinstance(move, list) or len(move) != 3:
                print(f"❌ Invalid move format: {move}")
                return False
            
            planet_id, angle, ships = move
            if not isinstance(planet_id, (int, float)):
                print(f"❌ Invalid planet_id: {planet_id}")
                return False
            if not isinstance(angle, (int, float)):
                print(f"❌ Invalid angle: {angle}")
                return False
            if not isinstance(ships, (int, float)):
                print(f"❌ Invalid ships: {ships}")
                return False
        
        print(f"✅ Agent validation passed!")
        print(f"   Test result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Agent validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ORBIT WARS SUBMISSION PREPARATION")
    print("=" * 60)
    
    if validate_agent():
        print()
        prepare_submission(version="1.0-heuristic")
    else:
        print("\n❌ Submission preparation aborted due to validation errors")
        import sys
        sys.exit(1)
