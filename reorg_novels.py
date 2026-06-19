import os, shutil

ROOT = r"D:\DMM_Translation\dotabyss-translation\translations\novels"

# 1. loose json -> folder/zh_Hans.json
loose = [f for f in os.listdir(ROOT) if f.endswith(".json") and os.path.isfile(os.path.join(ROOT, f))]
print("loose json:", len(loose))
moved = 0
for fname in loose:
    base = fname[:-5]
    src = os.path.join(ROOT, fname)
    newdir = os.path.join(ROOT, base)
    dst = os.path.join(newdir, "zh_Hans.json")
    if os.path.exists(dst):
        print("  skip (exists):", base)
        continue
    if not os.path.exists(newdir):
        os.makedirs(newdir)
    shutil.move(src, dst)
    moved += 1
print("moved:", moved)

# 2. fill zh_Hant.json where missing
folders = [d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d))]
print("folders:", len(folders))
filled = 0
skipped = 0
for folder in folders:
    hans = os.path.join(ROOT, folder, "zh_Hans.json")
    hant = os.path.join(ROOT, folder, "zh_Hant.json")
    if not os.path.exists(hans):
        skipped += 1
        continue
    if os.path.exists(hant):
        continue
    shutil.copy2(hans, hant)
    filled += 1
print("filled zh_Hant:", filled, "skipped(no hans):", skipped)
print("done")
