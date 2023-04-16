from fastapi import APIRouter
import os

router = APIRouter(
    prefix="/env",
    tags=["Environment"]
)

def compare_env_files(file1, file2):
    """
    Compare two environment variable files.
    """
    env1 = {}
    env2 = {}

    # Load the first file
    with open(file1, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env1[key] = value

    # Load the second file
    with open(file2, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env2[key] = value

    # Compare the two environments
    diff1 = {}
    diff2 = {}

    # Find keys in env1 that are not in env2
    for key in env1.keys() - env2.keys():
        diff1[key] = env1[key]

    # Find keys in env2 that are not in env1
    for key in env2.keys() - env1.keys():
        diff2[key] = env2[key]

    # Find keys that are in both environments but have different values
    for key in env1.keys() & env2.keys():
        if env1[key] != env2[key]:
            diff1[key] = env1[key]
            diff2[key] = env2[key]

    return diff1, diff2

@router.get("/diff")
def compare():
    # Example usage
    diff1, diff2 = compare_env_files('.env1', '.env2')
    return {'env1':diff1, 'env2':diff2}
    # print('Variables only in file 1:', diff1)
    # print('Variables only in file 2:', diff2)
    # return True
