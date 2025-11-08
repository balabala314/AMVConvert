import ffmpeg
from sys import argv
from os import system
from math import floor


def get_video_resolution_ffmpeg(video_path: str):
    try:
        probe = ffmpeg.probe(video_path)
        video_info = next(
            stream for stream in probe["streams"] if stream["codec_type"] == "video"
        )
        width = int(video_info["width"])
        height = int(video_info["height"])
        return width, height
    except Exception as e:
        print(f"错误: {e}")
        return (0, 0)


def acquire_new_resolution(orig: tuple[int, int], target: tuple[int, int]):
    print(f"Target: {target}")
    rotate: bool = False
    mode: int = 0  # 1为对齐宽度，0为对齐高度
    if (orig[0] < orig[1] and target[0] > target[1]) or (
        orig[0] > orig[1] and target[0] < target[1]
    ):
        orig = (orig[1], orig[0])
        rotate = True
    if (orig[0] / target[0]) < (orig[1] / target[1]):
        mode = 1
    scaleFactor = orig[mode] / target[mode]
    ans: tuple[int, int] = (floor(orig[0] / scaleFactor), floor(orig[1] / scaleFactor))
    if rotate:
        return (ans[1], ans[0]), rotate
    return ans, rotate


def gen_command(filePath: str, res: tuple[int, int], rotate: bool, targetPath: str):
    if not targetPath.lower().endswith(".amv"):
        raise Exception(f"Unsupported output file extension: {targetPath}")
    if rotate:
        return f'ffmpeg -i {filePath} -ar 22050 -ac 1 -vf "scale={res[0]}:{res[1]},transpose=0" -r 25 -block_size 882 -strict -1 {targetPath}'
    else:
        return f'ffmpeg -i {filePath} -ar 22050 -ac 1 -vf "scale={res[0]}:{res[1]}" -r 25 -block_size 882 -strict -1 {targetPath}'


def main():
    if len(argv) < 2:
        print("A file please.")
        return
    res = get_video_resolution_ffmpeg(argv[1])
    print(f"Original resolution: {res}")
    new_res, rot = acquire_new_resolution(res, (160, 128))
    print(f"New resolution: {new_res} \nRotation: {rot}")
    command = gen_command(argv[1], new_res, rot, "output.amv")
    print(f"Command: {command}")
    if system(command) != 0:
        print("Failed!")


if __name__ == "__main__":
    main()
